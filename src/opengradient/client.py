import asyncio
import base64
import json
import logging
import os
import time
import urllib.parse
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

import firebase
import httpx
import numpy as np
import requests
from eth_account.account import LocalAccount
from web3 import Web3
from web3.exceptions import ContractLogicError
from web3.logs import DISCARD
from x402.clients.base import x402Client
from x402.clients.httpx import x402HttpxClient

from .defaults import (
    DEFAULT_NETWORK_FILTER,
    DEFAULT_OPENGRADIENT_LLM_SERVER_URL,
    DEFAULT_OPENGRADIENT_LLM_STREAMING_SERVER_URL,
)
from .exceptions import OpenGradientError
from .types import (
    LLM,
    TEE_LLM,
    FileUploadResult,
    InferenceMode,
    InferenceResult,
    ModelRepository,
    StreamChunk,
    TextGenerationOutput,
    TextGenerationStream,
    x402SettlementMode,
)
from .utils import convert_to_model_input, convert_to_model_output
from .x402_auth import X402Auth

# Security Update: Credentials moved to environment variables
_FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL", ""),
}

# How much time we wait for txn to be included in chain
LLM_TX_TIMEOUT = 60
INFERENCE_TX_TIMEOUT = 120
REGULAR_TX_TIMEOUT = 30

# How many times we retry a transaction because of nonce conflict
DEFAULT_MAX_RETRY = 5
DEFAULT_RETRY_DELAY_SEC = 1

PRECOMPILE_CONTRACT_ADDRESS = "0x00000000000000000000000000000000000000F4"

X402_PROCESSING_HASH_HEADER = "x-processing-hash"
X402_PLACEHOLDER_API_KEY = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"

TIMEOUT = httpx.Timeout(
    timeout=90.0,
    connect=15.0,
    read=15.0,
    write=30.0,
    pool=10.0,
)
LIMITS = httpx.Limits(
    max_keepalive_connections=100,
    max_connections=500,
    keepalive_expiry=60 * 20,  # 20 minutes
)


class Client:
    _inference_hub_contract_address: str
    _blockchain: Web3
    _wallet_account: LocalAccount

    _hub_user: Optional[Dict]
    _api_url: str
    _inference_abi: Dict
    _precompile_abi: Dict

    def __init__(
        self,
        private_key: str,
        rpc_url: str,
        api_url: str,
        contract_address: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        og_llm_server_url: Optional[str] = DEFAULT_OPENGRADIENT_LLM_SERVER_URL,
        og_llm_streaming_server_url: Optional[str] = DEFAULT_OPENGRADIENT_LLM_STREAMING_SERVER_URL,
    ):
        """
        Initialize the Client with private key, RPC URL, and contract address.

        Args:
            private_key (str): The private key for the wallet.
            rpc_url (str): The RPC URL for the Ethereum node.
            contract_address (str): The contract address for the smart contract.
            email (str, optional): Email for authentication. Defaults to "test@test.com".
            password (str, optional): Password for authentication. Defaults to "Test-123".
        """
        self._inference_hub_contract_address = contract_address
        self._blockchain = Web3(Web3.HTTPProvider(rpc_url))
        self._api_url = api_url
        self._wallet_account = self._blockchain.eth.account.from_key(private_key)

        abi_path = Path(__file__).parent / "abi" / "inference.abi"
        with open(abi_path, "r") as abi_file:
            self._inference_abi = json.load(abi_file)

        abi_path = Path(__file__).parent / "abi" / "InferencePrecompile.abi"
        with open(abi_path, "r") as abi_file:
            self._precompile_abi = json.load(abi_file)

        if email is not None:
            self._hub_user = self._login_to_hub(email, password)
        else:
            self._hub_user = None

        self._og_llm_server_url = og_llm_server_url
        self._og_llm_streaming_server_url = og_llm_streaming_server_url

        self._alpha = None  # Lazy initialization for alpha namespace

    @property
    def alpha(self):
        """
        Access Alpha Testnet features.

        Returns:
            Alpha: Alpha namespace with workflow and ML model execution methods.

        Example:
            client = og.new_client(...)
            result = client.alpha.new_workflow(model_cid, input_query, input_tensor_name)
        """
        if self._alpha is None:
            from .alpha import Alpha

            self._alpha = Alpha(self)
        return self._alpha

    def _login_to_hub(self, email, password):
        try:
            # Check if API Key is present in environment
            if not _FIREBASE_CONFIG.get("apiKey"):
                logging.warning("Firebase API Key is missing in environment variables. Authentication may fail.")

            firebase_app = firebase.initialize_app(_FIREBASE_CONFIG)
            return firebase_app.auth().sign_in_with_email_and_password(email, password)
        except Exception as e:
            logging.error(f"Authentication failed: {str(e)}")
            raise

    def create_model(self, model_name: str, model_desc: str, version: str = "1.00") -> ModelRepository:
        """
        Create a new model with the given model_name and model_desc, and a specified version.

        Args:
            model_name (str): The name of the model.
            model_desc (str): The description of the model.
            version (str): The version identifier (default is "1.00").

        Returns:
            dict: The server response containing model details.

        Raises:
            CreateModelError: If the model creation fails.
        """
        if not self._hub_user:
            raise ValueError("User not authenticated")

        url = "https://api.opengradient.ai/api/v0/models/"
        headers = {"Authorization": f"Bearer {self._hub_user['idToken']}", "Content-Type": "application/json"}
        payload = {"name": model_name, "description": model_desc}

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
        except requests.HTTPError as e:
            error_details = f"HTTP {e.response.status_code}: {e.response.text}"
            raise OpenGradientError(f"Model creation failed: {error_details}") from e

        json_response = response.json()
        model_name = json_response.get("name")
        if not model_name:
            raise Exception(f"Model creation response missing 'name'. Full response: {json_response}")

        # Create the specified version for the newly created model
        version_response = self.create_version(model_name, version)

        return ModelRepository(model_name, version_response["versionString"])

    def create_version(self, model_name: str, notes: str = "", is_major: bool = False) -> dict:
        """
        Create a new version for the specified model.

        Args:
            model_name (str): The unique identifier for the model.
            notes (str, optional): Notes for the new version.
            is_major (bool, optional): Whether this is a major version update. Defaults to False.

        Returns:
            dict: The server response containing version details.

        Raises:
            Exception: If the version creation fails.
        """
        if not self._hub_user:
            raise ValueError("User not authenticated")

        url = f"https://api.opengradient.ai/api/v0/models/{model_name}/versions"
        headers = {"Authorization": f"Bearer {self._hub_user['idToken']}", "Content-Type": "application/json"}
        payload = {"notes": notes, "is_major": is_major}

        try:
            logging.debug(f"Create Version URL: {url}")
            logging.debug(f"Headers: {headers}")
            logging.debug(f"Payload: {payload}")

            response = requests.post(url, json=payload, headers=headers, allow_redirects=False)
            response.raise_for_status()

            json_response = response.json()

            logging.debug(f"Full server response: {json_response}")

            if isinstance(json_response, list) and not json_response:
                logging.info("Server returned an empty list. Assuming version was created successfully.")
                return {"versionString": "Unknown", "note": "Created based on empty response"}
            elif isinstance(json_response, dict):
                version_string = json_response.get("versionString")
                if not version_string:
                    logging.warning(f"'versionString' not found in response. Response: {json_response}")
                    return {"versionString": "Unknown", "note": "Version ID not provided in response"}
                logging.info(f"Version creation successful. Version ID: {version_string}")
                return {"versionString": version_string}
            else:
                logging.error(f"Unexpected response type: {type(json_response)}. Content: {json_response}")
                raise Exception(f"Unexpected response type: {type(json_response)}")

        except requests.RequestException as e:
            logging.error(f"Version creation failed: {str(e)}")
            if hasattr(e, "response") and e.response is not None:
                logging.error(f"Response status code: {e.response.status_code}")
                logging.error(f"Response headers: {e.response.headers}")
                logging.error(f"Response content: {e.response.text}")
            raise Exception(f"Version creation failed: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error during version creation: {str(e)}")
            raise

    def upload(self, model_path: str, model_name: str, version: str) -> FileUploadResult:
        """
        Upload a model file to the server.

        Args:
            model_path (str): The path to the model file.
            model_name (str): The unique identifier for the model.
            version (str): The version identifier for the model.

        Returns:
            dict: The processed result.

        Raises:
            OpenGradientError: If the upload fails.
        """
        from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

        if not self._hub_user:
            raise ValueError("User not authenticated")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        url = f"https://api.opengradient.ai/api/v0/models/{model_name}/versions/{version}/files"
        headers = {"Authorization": f"Bearer {self._hub_user['idToken']}"}

        logging.info(f"Starting upload for file: {model_path}")
        logging.info(f"File size: {os.path.getsize(model_path)} bytes")
        logging.debug(f"Upload URL: {url}")
        logging.debug(f"Headers: {headers}")

        def create_callback(encoder):
            encoder_len = encoder.len

            def callback(monitor):
                progress = (monitor.bytes_read / encoder_len) * 100
                logging.info(f"Upload progress: {progress:.2f}%")

            return callback

        try:
            with open(model_path, "rb") as file:
                encoder = MultipartEncoder(fields={"file": (os.path.basename(model_path), file, "application/octet-stream")})
                monitor = MultipartEncoderMonitor(encoder, create_callback(encoder))
                headers["Content-Type"] = monitor.content_type

                logging.info("Sending POST request...")
                response = requests.post(url, data=monitor, headers=headers, timeout=3600)  # 1 hour timeout

                logging.info(f"Response received. Status code: {response.status_code}")
                logging.info(f"Full response content: {response.text}")  # Log the full response content

                if response.status_code == 201:
                    if response.content and response.content != b"null":
                        json_response = response.json()
                        return FileUploadResult(json_response.get("ipfsCid"), json_response.get("size"))
                    else:
                        raise RuntimeError("Empty or null response content received. Assuming upload was successful.")
                elif response.status_code == 500:
                    error_message = "Internal server error occurred. Please try again later or contact support."
                    logging.error(error_message)
                    raise OpenGradientError(error_message, status_code=500)
                else:
                    error_message = response.json().get("detail", "Unknown error occurred")
                    logging.error(f"Upload failed with status code {response.status_code}: {error_message}")
                    raise OpenGradientError(f"Upload failed: {error_message}", status_code=response.status_code)

        except requests.RequestException as e:
            logging.error(f"Request exception during upload: {str(e)}")
            if hasattr(e, "response") and e.response is not None:
                logging.error(f"Response status code: {e.response.status_code}")
                logging.error(f"Response content: {e.response.text[:1000]}...")  # Log first 1000 characters
            raise OpenGradientError(f"Upload failed due to request exception: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error during upload: {str(e)}", exc_info=True)
            raise OpenGradientError(f"Unexpected error during upload: {str(e)}")

    def infer(
        self,
        model_cid: str,
        inference_mode: InferenceMode,
        model_input: Dict[str, Union[str, int, float, List, np.ndarray]],
        max_retries: Optional[int] = None,
    ) -> InferenceResult:
        """
        Perform inference on a model.

        Args:
            model_cid (str): The unique content identifier for the model from IPFS.
            inference_mode (InferenceMode): The inference mode.
            model_input (Dict[str, Union[str, int, float, List, np.ndarray]]): The input data for the model.
            max_retries (int, optional): Maximum number of retry attempts. Defaults to 5.

        Returns:
            InferenceResult (InferenceResult): A dataclass object containing the transaction hash and model output.
                transaction_hash (str): Blockchain hash for the transaction
                model_output (Dict[str, np.ndarray]): Output of the ONNX model

        Raises:
            OpenGradientError: If the inference fails.
        """

        def execute_transaction():
            contract = self._blockchain.eth.contract(address=self._inference_hub_contract_address, abi=self._inference_abi)
            precompile_contract = self._blockchain.eth.contract(address=PRECOMPILE_CONTRACT_ADDRESS, abi=self._precompile_abi)

            inference_mode_uint8 = inference_mode.value
            converted_model_input = convert_to_model_input(model_input)

            run_function = contract.functions.run(model_cid, inference_mode_uint8, converted_model_input)

            tx_hash, tx_receipt = self._send_tx_with_revert_handling(run_function)
            parsed_logs = contract.events.InferenceResult().process_receipt(tx_receipt, errors=DISCARD)
            if len(parsed_logs) < 1:
                raise OpenGradientError("InferenceResult event not found in transaction logs")

            # TODO: This should return a ModelOutput class object
            model_output = convert_to_model_output(parsed_logs[0]["args"])
            if len(model_output) == 0:
                # check inference directly from node
                parsed_logs = precompile_contract.events.ModelInferenceEvent().process_receipt(tx_receipt, errors=DISCARD)
                inference_id = parsed_logs[0]["args"]["inferenceID"]
                inference_result = self._get_inference_result_from_node(inference_id, inference_mode)
                model_output = convert_to_model_output(inference_result)

            return InferenceResult(tx_hash.hex(), model_output)

        return run_with_retry(execute_transaction, max_retries)

    def _og_payment_selector(self, accepts, network_filter=DEFAULT_NETWORK_FILTER, scheme_filter=None, max_value=None):
        """Custom payment selector for OpenGradient network."""
        return x402Client.default_payment_requirements_selector(
            accepts,
            network_filter=network_filter,
            scheme_filter=scheme_filter,
            max_value=max_value,
        )

    def llm_completion(
        self,
        model_cid: str,
        prompt: str,
        max_tokens: int = 100,
        stop_sequence: Optional[List[str]] = None,
        temperature: float = 0.0,
        x402_settlement_mode: Optional[x402SettlementMode] = x402SettlementMode.SETTLE_BATCH,
    ) -> TextGenerationOutput:
        """
        Perform inference on an LLM model using completions via TEE.

        Args:
            model_cid (str): The unique content identifier for the model (e.g., 'anthropic/claude-3.5-haiku').
            prompt (str): The input prompt for the LLM.
            max_tokens (int): Maximum number of tokens for LLM output. Default is 100.
            stop_sequence (List[str], optional): List of stop sequences for LLM. Default is None.
            temperature (float): Temperature for LLM inference, between 0 and 1. Default is 0.0.
            x402_settlement_mode (x402SettlementMode, optional): Settlement mode for x402 payments.
                - SETTLE: Records input/output hashes only (most privacy-preserving).
                - SETTLE_BATCH: Aggregates multiple inferences into batch hashes (most cost-efficient).
                - SETTLE_METADATA: Records full model info, complete input/output data, and all metadata.
                Defaults to SETTLE_BATCH.

        Returns:
            TextGenerationOutput: Generated text results including:
                - Transaction hash ("external" for TEE providers)
                - String of completion output
                - Payment hash for x402 transactions

        Raises:
            OpenGradientError: If the inference fails.
        """
        if model_cid not in TEE_LLM:
            raise OpenGradientError("That model CID is not supported yet for TEE inference")

        return self._tee_llm_completion(
            model=model_cid.split("/")[1],
            prompt=prompt,
            max_tokens=max_tokens,
            stop_sequence=stop_sequence,
            temperature=temperature,
            x402_settlement_mode=x402_settlement_mode,
        )

    def _tee_llm_completion(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 100,
        stop_sequence: Optional[List[str]] = None,
        temperature: float = 0.0,
        x402_settlement_mode: Optional[x402SettlementMode] = x402SettlementMode.SETTLE_BATCH,
    ) -> TextGenerationOutput:
        """
        Route completion request to OpenGradient TEE LLM server with x402 payments.

        Args:
            model: Model identifier
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            stop_sequence: Stop sequences
            temperature: Sampling temperature
            x402_settlement_mode: Settlement mode for x402 payments

        Returns:
            TextGenerationOutput with completion

        Raises:
            OpenGradientError: If request fails
        """

        async def make_request():
            # Security Fix: verify=True enabled
            async with x402HttpxClient(
                account=self._wallet_account,
                base_url=self._og_llm_server_url,
                payment_requirements_selector=self._og_payment_selector,
                verify=True,
            ) as client:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {X402_PLACEHOLDER_API_KEY}",
                    "X-SETTLEMENT-TYPE": x402_settlement_mode,
                }

                payload = {
                    "model": model,
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                }

                if stop_sequence:
                    payload["stop"] = stop_sequence

                try:
                    response = await client.post("/v1/completions", json=payload, headers=headers, timeout=60)

                    # Read the response content
                    content = await response.aread()
                    result = json.loads(content.decode())
                    payment_hash = ""

                    if X402_PROCESSING_HASH_HEADER in response.headers:
                        payment_hash = response.headers[X402_PROCESSING_HASH_HEADER]

                    return TextGenerationOutput(
                        transaction_hash="external", completion_output=result.get("completion"), payment_hash=payment_hash
                    )

                except Exception as e:
                    error_msg = f"TEE LLM completion request failed: {str(e)}"
                    logging.error(error_msg)
                    raise OpenGradientError(error_msg)

        try:
            # Run the async function in a sync context
            return asyncio.run(make_request())
        except Exception as e:
            error_msg = f"TEE LLM completion failed: {str(e)}"
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {e.response.text}"
            logging.error(error_msg)
            raise OpenGradientError(error_msg)

    def llm_chat(
        self,
        model_cid: str,
        messages: List[Dict],
        max_tokens: int = 100,
        stop_sequence: Optional[List[str]] = None,
        temperature: float = 0.0,
        tools: Optional[List[Dict]] = [],
        tool_choice: Optional[str] = None,
        x402_settlement_mode: Optional[x402SettlementMode] = x402SettlementMode.SETTLE_BATCH,
        stream: bool = False,
    ) -> Union[TextGenerationOutput, TextGenerationStream]:
        """
        Perform inference on an LLM model using chat via TEE.

        Args:
            model_cid (str): The unique content identifier for the model (e.g., 'anthropic/claude-3.5-haiku').
            messages (List[Dict]): The messages that will be passed into the chat.
            max_tokens (int): Maximum number of tokens for LLM output. Default is 100.
            stop_sequence (List[str], optional): List of stop sequences for LLM.
            temperature (float): Temperature for LLM inference, between 0 and 1.
            tools (List[dict], optional): Set of tools for function calling.
            tool_choice (str, optional): Sets a specific tool to choose.
            x402_settlement_mode (x402SettlementMode, optional): Settlement mode for x402 payments.
                - SETTLE: Records input/output hashes only (most privacy-preserving).
                - SETTLE_BATCH: Aggregates multiple inferences into batch hashes (most cost-efficient).
                - SETTLE_METADATA: Records full model info, complete input/output data, and all metadata.
                Defaults to SETTLE_BATCH.
            stream (bool, optional): Whether to stream the response. Default is False.

        Returns:
            Union[TextGenerationOutput, TextGenerationStream]:
                - If stream=False: TextGenerationOutput with chat_output, transaction_hash, finish_reason, and payment_hash
                - If stream=True: TextGenerationStream yielding StreamChunk objects with typed deltas (true streaming via threading)

        Raises:
            OpenGradientError: If the inference fails.
        """
        if model_cid not in TEE_LLM:
            raise OpenGradientError("That model CID is not supported yet for TEE inference")

        if stream:
            # Use threading bridge for true sync streaming
            return self._tee_llm_chat_stream_sync(
                model=model_cid.split("/")[1],
                messages=messages,
                max_tokens=max_tokens,
                stop_sequence=stop_sequence,
                temperature=temperature,
                tools=tools,
                tool_choice=tool_choice,
                x402_settlement_mode=x402_settlement_mode,
            )
        else:
            # Non-streaming
            return self._tee_llm_chat(
                model=model_cid.split("/")[1],
                messages=messages,
                max_tokens=max_tokens,
                stop_sequence=stop_sequence,
                temperature=temperature,
                tools=tools,
                tool_choice=tool_choice,
                x402_settlement_mode=x402_settlement_mode,
            )

    def _tee_llm_chat(
        self,
        model: str,
        messages: List[Dict],
        max_tokens: int = 100,
        stop_sequence: Optional[List[str]] = None,
        temperature: float = 0.0,
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[str] = None,
        x402_settlement_mode: x402SettlementMode = x402SettlementMode.SETTLE_BATCH,
    ) -> TextGenerationOutput:
        """
        Route chat request to OpenGradient TEE LLM server with x402 payments.

        Args:
            model: Model identifier
            messages: List of chat messages
            max_tokens: Maximum tokens to generate
            stop_sequence: Stop sequences
            temperature: Sampling temperature
            tools: Function calling tools
            tool_choice: Tool selection strategy
            x402_settlement_mode: Settlement mode for x402 payments

        Returns:
            TextGenerationOutput: Chat completion

        Raises:
            OpenGradientError: If request fails
        """

        async def make_request():
            # Security Fix: verify=True enabled
            async with x402HttpxClient(
                account=self._wallet_account,
                base_url=self._og_llm_server_url,
                payment_requirements_selector=self._og_payment_selector,
                verify=True,
            ) as client:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {X402_PLACEHOLDER_API_KEY}",
                    "X-SETTLEMENT-TYPE": x402_settlement_mode,
                }

                payload = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                }

                if stop_sequence:
                    payload["stop"] = stop_sequence

                if tools:
                    payload["tools"] = tools
                    payload["tool_choice"] = tool_choice or "auto"

                try:
                    # Non-streaming with x402
                    endpoint = "/v1/chat/completions"
                    response = await client.post(endpoint, json=payload, headers=headers, timeout=60)

                    # Read the response content
                    content = await response.aread()
                    result = json.loads(content.decode())

                    payment_hash = ""
                    if X402_PROCESSING_HASH_HEADER in response.headers:
                        payment_hash = response.headers[X402_PROCESSING_HASH_HEADER]

                    choices = result.get("choices")
                    if not choices:
                        raise OpenGradientError(f"Invalid response: 'choices' missing or empty in {result}")

                    return TextGenerationOutput(
                        transaction_hash="external",
                        finish_reason=choices[0].get("finish_reason"),
                        chat_output=choices[0].get("message"),
                        payment_hash=payment_hash,
                    )

                except Exception as e:
                    error_msg = f"TEE LLM chat request failed: {str(e)}"
                    logging.error(error_msg)
                    raise OpenGradientError(error_msg)

        try:
            # Run the async function in a sync context
            return asyncio.run(make_request())
        except Exception as e:
            error_msg = f"TEE LLM chat failed: {str(e)}"
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {e.response.text}"
            logging.error(error_msg)
            raise OpenGradientError(error_msg)

    def _tee_llm_chat_stream_sync(
        self,
        model: str,
        messages: List[Dict],
        max_tokens: int = 100,
        stop_sequence: Optional[List[str]] = None,
        temperature: float = 0.0,
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[str] = None,
        x402_settlement_mode: x402SettlementMode = x402SettlementMode.SETTLE_BATCH,
    ):
        """
        Sync streaming using threading bridge - TRUE real-time streaming.

        Yields StreamChunk objects as they arrive from the background thread.
        NO buffering, NO conversion, just direct pass-through.
        """
        import threading
        from queue import Queue

        queue = Queue()
        exception_holder = []

        def _run_async():
            """Run async streaming in background thread"""
            loop = None
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                async def _stream():
                    try:
                        async for chunk in self._tee_llm_chat_stream_async(
                            model=model,
                            messages=messages,
                            max_tokens=max_tokens,
                            stop_sequence=stop_sequence,
                            temperature=temperature,
                            tools=tools,
                            tool_choice=tool_choice,
                            x402_settlement_mode=x402_settlement_mode,
                        ):
                            queue.put(chunk)  # Put chunk immediately
                    except Exception as e:
                        exception_holder.append(e)
                    finally:
                        queue.put(None)  # Signal completion

                loop.run_until_complete(_stream())
            except Exception as e:
                exception_holder.append(e)
                queue.put(None)
            finally:
                if loop:
                    try:
                        pending = asyncio.all_tasks(loop)
                        for task in pending:
                            task.cancel()
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                        # Properly close async generators to avoid RuntimeWarning
                        loop.run_until_complete(loop.shutdown_asyncgens())
                    finally:
                        loop.close()

        # Start background thread
        thread = threading.Thread(target=_run_async, daemon=True)
        thread.start()

        # Yield chunks DIRECTLY as they arrive - NO buffering
        try:
            while True:
                chunk = queue.get()  # Blocks until chunk available
                if chunk is None:
                    break
                yield chunk  # Yield immediately!

            thread.join(timeout=5)

            if exception_holder:
                raise exception_holder[0]
        except Exception:
            thread.join(timeout=1)
            raise

    async def _tee_llm_chat_stream_async(
        self,
        model: str,
        messages: List[Dict],
        max_tokens: int = 100,
        stop_sequence: Optional[List[str]] = None,
        temperature: float = 0.0,
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[str] = None,
        x402_settlement_mode: x402SettlementMode = x402SettlementMode.SETTLE_BATCH,
    ):
        """
        Internal async streaming implementation for TEE LLM with x402 payments.

        Yields StreamChunk objects as they arrive from the server.
        """
        async with httpx.AsyncClient(
            base_url=self._og_llm_streaming_server_url,
            headers={"Authorization": f"Bearer {X402_PLACEHOLDER_API_KEY}"},
            timeout=TIMEOUT,
            limits=LIMITS,
            http2=False,
            follow_redirects=False,
            auth=X402Auth(account=self._wallet_account, network_filter=DEFAULT_NETWORK_FILTER),  # type: ignore
            verify=True,
        ) as client:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {X402_PLACEHOLDER_API_KEY}",
                "X-SETTLEMENT-TYPE": x402_settlement_mode,
            }

            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True,
            }

            if stop_sequence:
                payload["stop"] = stop_sequence
            if tools:
                payload["tools"] = tools
                payload["tool_choice"] = tool_choice or "auto"

            async with client.stream(
                "POST",
                "/v1/chat/completions",
                json=payload,
                headers=headers,
            ) as response:
                buffer = b""
                async for chunk in response.aiter_raw():
                    if not chunk:
                        continue

                    buffer += chunk

                    # Process complete lines from buffer
                    while b"\n" in buffer:
                        line_bytes, buffer = buffer.split(b"\n", 1)

                        if not line_bytes.strip():
                            continue

                        try:
                            line = line_bytes.decode("utf-8").strip()
                        except UnicodeDecodeError:
                            continue

                        if not line.startswith("data: "):
                            continue

                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            return

                        try:
                            data = json.loads(data_str)
                            yield StreamChunk.from_sse_data(data)
                        except json.JSONDecodeError:
                            continue

    def list_files(self, model_name: str, version: str) -> List[Dict]:
        """
        List files for a specific version of a model.

        Args:
            model_name (str): The unique identifier for the model.
            version (str): The version identifier for the model.

        Returns:
            List[Dict]: A list of dictionaries containing file information.

        Raises:
            OpenGradientError: If the file listing fails.
        """
        if not self._hub_user:
            raise ValueError("User not authenticated")

        url = f"https://api.opengradient.ai/api/v0/models/{model_name}/versions/{version}/files"
        headers = {"Authorization": f"Bearer {self._hub_user['idToken']}"}

        logging.debug(f"List Files URL: {url}")
        logging.debug(f"Headers: {headers}")

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            json_response = response.json()
            logging.info(f"File listing successful. Number of files: {len(json_response)}")

            return json_response

        except requests.RequestException as e:
            logging.error(f"File listing failed: {str(e)}")
            if hasattr(e, "response") and e.response is not None:
                logging.error(f"Response status code: {e.response.status_code}")
                logging.error(f"Response content: {e.response.text[:1000]}...")  # Log first 1000 characters
            raise OpenGradientError(f"File listing failed: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error during file listing: {str(e)}", exc_info=True)
            raise OpenGradientError(f"Unexpected error during file listing: {str(e)}")

    def _get_abi(self, abi_name) -> str:
        """
        Returns the ABI for the requested contract.
        """
        abi_path = Path(__file__).parent / "abi" / abi_name
        with open(abi_path, "r") as f:
            return json.load(f)

    def _get_bin(self, bin_name) -> str:
        """
        Returns the bin for the requested contract.
        """
        bin_path = Path(__file__).parent / "bin" / bin_name
        # Read bytecode with explicit encoding
        with open(bin_path, "r", encoding="utf-8") as f:
            bytecode = f.read().strip()
            if not bytecode.startswith("0x"):
                bytecode = "0x" + bytecode
            return bytecode

    def _send_tx_with_revert_handling(self, run_function):
        """
        Execute a blockchain transaction with revert error.

        Args:
            run_function: Function that executes the transaction

        Returns:
            tx_hash: Transaction hash
            tx_receipt: Transaction receipt

        Raises:
            Exception: If transaction fails or gas estimation fails
        """
        nonce = self._blockchain.eth.get_transaction_count(self._wallet_account.address, "pending")
        try:
            estimated_gas = run_function.estimate_gas({"from": self._wallet_account.address})
        except ContractLogicError as e:
            try:
                run_function.call({"from": self._wallet_account.address})

            except ContractLogicError as call_err:
                raise ContractLogicError(f"simulation failed with revert reason: {call_err.args[0]}")

            raise ContractLogicError(f"simulation failed with no revert reason. Reason: {e}")

        gas_limit = int(estimated_gas * 3)

        transaction = run_function.build_transaction(
            {
                "from": self._wallet_account.address,
                "nonce": nonce,
                "gas": gas_limit,
                "gasPrice": self._blockchain.eth.gas_price,
            }
        )

        signed_tx = self._wallet_account.sign_transaction(transaction)
        tx_hash = self._blockchain.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_receipt = self._blockchain.eth.wait_for_transaction_receipt(tx_hash, timeout=INFERENCE_TX_TIMEOUT)

        if tx_receipt["status"] == 0:
            try:
                run_function.call({"from": self._wallet_account.address})

            except ContractLogicError as call_err:
                raise ContractLogicError(f"Transaction failed with revert reason: {call_err.args[0]}")

            raise ContractLogicError(f"Transaction failed with no revert reason. Receipt: {tx_receipt}")

        return tx_hash, tx_receipt

    def _get_inference_result_from_node(self, inference_id: str, inference_mode: InferenceMode) -> Dict:
        """
        Get the inference result from node.

        Args:
            inference_id (str): Inference id for a inference request

        Returns:
            Dict: The inference result as returned by the node

        Raises:
            OpenGradientError: If the request fails or returns an error
        """
        try:
            encoded_id = urllib.parse.quote(inference_id, safe="")
            url = f"{self._api_url}/artela-network/artela-rollkit/inference/tx/{encoded_id}"

            response = requests.get(url)
            if response.status_code == 200:
                resp = response.json()
                inference_result = resp.get("inference_results", {})
                if inference_result:
                    decoded_bytes = base64.b64decode(inference_result[0])
                    decoded_string = decoded_bytes.decode("utf-8")
                    output = json.loads(decoded_string).get("InferenceResult", {})
                    if output is None:
                        raise OpenGradientError("Missing InferenceResult in inference output")

                    match inference_mode:
                        case InferenceMode.VANILLA:
                            if "VanillaResult" not in output:
                                raise OpenGradientError("Missing VanillaResult in inference output")
                            if "model_output" not in output["VanillaResult"]:
                                raise OpenGradientError("Missing model_output in VanillaResult")
                            return {"output": output["VanillaResult"]["model_output"]}

                        case InferenceMode.TEE:
                            if "TeeNodeResult" not in output:
                                raise OpenGradientError("Missing TeeNodeResult in inference output")
                            if "Response" not in output["TeeNodeResult"]:
                                raise OpenGradientError("Missing Response in TeeNodeResult")
                            if "VanillaResponse" in output["TeeNodeResult"]["Response"]:
                                if "model_output" not in output["TeeNodeResult"]["Response"]["VanillaResponse"]:
                                    raise OpenGradientError("Missing model_output in VanillaResponse")
                                return {"output": output["TeeNodeResult"]["Response"]["VanillaResponse"]["model_output"]}

                            else:
                                raise OpenGradientError("Missing VanillaResponse in TeeNodeResult Response")

                        case InferenceMode.ZKML:
                            if "ZkmlResult" not in output:
                                raise OpenGradientError("Missing ZkmlResult in inference output")
                            if "model_output" not in output["ZkmlResult"]:
                                raise OpenGradientError("Missing model_output in ZkmlResult")
                            return {"output": output["ZkmlResult"]["model_output"]}

                        case _:
                            raise OpenGradientError(f"Invalid inference mode: {inference_mode}")
                else:
                    return None

            else:
                error_message = f"Failed to get inference result: HTTP {response.status_code}"
                if response.text:
                    error_message += f" - {response.text}"
                logging.error(error_message)
                raise OpenGradientError(error_message)

        except requests.RequestException as e:
            logging.error(f"Request exception when getting inference result: {str(e)}")
            raise OpenGradientError(f"Failed to get inference result: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error when getting inference result: {str(e)}", exc_info=True)
            raise OpenGradientError(f"Failed to get inference result: {str(e)}")


def run_with_retry(txn_function: Callable, max_retries=DEFAULT_MAX_RETRY, retry_delay=DEFAULT_RETRY_DELAY_SEC):
    """
    Execute a blockchain transaction with retry logic.

    Args:
        txn_function: Function that executes the transaction
        max_retries (int): Maximum number of retry attempts
        retry_delay (float): Delay in seconds between retries for nonce issues
    """
    NONCE_TOO_LOW = "nonce too low"
    NONCE_TOO_HIGH = "nonce too high"
    INVALID_NONCE = "invalid nonce"

    effective_retries = max_retries if max_retries is not None else DEFAULT_MAX_RETRY

    for attempt in range(effective_retries):
        try:
            return txn_function()
        except Exception as e:
            error_msg = str(e).lower()

            nonce_errors = [INVALID_NONCE, NONCE_TOO_LOW, NONCE_TOO_HIGH]
            if any(error in error_msg for error in nonce_errors):
                if attempt == effective_retries - 1:
                    raise OpenGradientError(f"Transaction failed after {effective_retries} attempts: {e}")
                time.sleep(retry_delay)
                continue

            raise
