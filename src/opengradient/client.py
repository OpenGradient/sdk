import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import firebase
import grpc
import numpy as np
import requests
from eth_account.account import LocalAccount
from web3 import Web3
from web3.exceptions import ContractLogicError
from web3.logs import DISCARD

from . import utils
from .exceptions import OpenGradientError
from .proto import infer_pb2, infer_pb2_grpc
from .types import LLM, TEE_LLM, HistoricalInputQuery, InferenceMode, LlmInferenceMode, ModelOutput, SchedulerParams
from .defaults import DEFAULT_IMAGE_GEN_HOST, DEFAULT_IMAGE_GEN_PORT

_FIREBASE_CONFIG = {
    "apiKey": "AIzaSyDUVckVtfl-hiteBzPopy1pDD8Uvfncs7w",
    "authDomain": "vanna-portal-418018.firebaseapp.com",
    "projectId": "vanna-portal-418018",
    "storageBucket": "vanna-portal-418018.appspot.com",
    "appId": "1:487761246229:web:259af6423a504d2316361c",
    "databaseURL": "",
}


class Client:
    _inference_hub_contract_address: str
    _blockchain: Web3
    _wallet_account: LocalAccount

    _hub_user: Dict
    _inference_abi: Dict

    def __init__(self, private_key: str, rpc_url: str, contract_address: str, email: str, password: str):
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
        self._wallet_account = self._blockchain.eth.account.from_key(private_key)

        abi_path = Path(__file__).parent / "abi" / "inference.abi"
        with open(abi_path, "r") as abi_file:
            self._inference_abi = json.load(abi_file)

        if email is not None:
            self._hub_user = self._login_to_hub(email, password)
        else:
            self._hub_user = None

    def _login_to_hub(self, email, password):
        try:
            firebase_app = firebase.initialize_app(_FIREBASE_CONFIG)
            return firebase_app.auth().sign_in_with_email_and_password(email, password)
        except Exception as e:
            logging.error(f"Authentication failed: {str(e)}")
            raise

    def create_model(self, model_name: str, model_desc: str, version: str = "1.00") -> dict:
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
        headers = {"Authorization": f'Bearer {self._hub_user["idToken"]}', "Content-Type": "application/json"}
        payload = {"name": model_name, "description": model_desc}

        try:
            logging.debug(f"Create Model URL: {url}")
            logging.debug(f"Headers: {headers}")
            logging.debug(f"Payload: {payload}")

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            json_response = response.json()
            model_name = json_response.get("name")
            if not model_name:
                raise Exception(f"Model creation response missing 'name'. Full response: {json_response}")
            logging.info(f"Model creation successful. Model name: {model_name}")

            # Create the specified version for the newly created model
            try:
                version_response = self.create_version(model_name, version)
                logging.info(f"Version creation successful. Version string: {version_response['versionString']}")
            except Exception as ve:
                logging.error(f"Version creation failed, but model was created. Error: {str(ve)}")
                return {"name": model_name, "versionString": None, "version_error": str(ve)}

            return {"name": model_name, "versionString": version_response["versionString"]}

        except requests.RequestException as e:
            logging.error(f"Model creation failed: {str(e)}")
            if hasattr(e, "response") and e.response is not None:
                logging.error(f"Response status code: {e.response.status_code}")
                logging.error(f"Response headers: {e.response.headers}")
                logging.error(f"Response content: {e.response.text}")
            raise Exception(f"Model creation failed: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error during model creation: {str(e)}")
            raise

    def create_version(self, model_name: str, notes: str = None, is_major: bool = False) -> dict:
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
        headers = {"Authorization": f'Bearer {self._hub_user["idToken"]}', "Content-Type": "application/json"}
        payload = {"notes": notes, "is_major": is_major}

        try:
            logging.debug(f"Create Version URL: {url}")
            logging.debug(f"Headers: {headers}")
            logging.debug(f"Payload: {payload}")

            response = requests.post(url, json=payload, headers=headers, allow_redirects=True)
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

    def upload(self, model_path: str, model_name: str, version: str) -> dict:
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
        headers = {"Authorization": f'Bearer {self._hub_user["idToken"]}'}

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
                        logging.info(f"JSON response: {json_response}")  # Log the parsed JSON response
                        logging.info(f"Upload successful. CID: {json_response.get('ipfsCid', 'N/A')}")
                        result = {"model_cid": json_response.get("ipfsCid"), "size": json_response.get("size")}
                    else:
                        logging.warning("Empty or null response content received. Assuming upload was successful.")
                        result = {"model_cid": None, "size": None}
                elif response.status_code == 500:
                    error_message = "Internal server error occurred. Please try again later or contact support."
                    logging.error(error_message)
                    raise OpenGradientError(error_message, status_code=500)
                else:
                    error_message = response.json().get("detail", "Unknown error occurred")
                    logging.error(f"Upload failed with status code {response.status_code}: {error_message}")
                    raise OpenGradientError(f"Upload failed: {error_message}", status_code=response.status_code)

                return result

        except requests.RequestException as e:
            logging.error(f"Request exception during upload: {str(e)}")
            if hasattr(e, "response") and e.response is not None:
                logging.error(f"Response status code: {e.response.status_code}")
                logging.error(f"Response content: {e.response.text[:1000]}...")  # Log first 1000 characters
            raise OpenGradientError(
                f"Upload failed due to request exception: {str(e)}", status_code=e.response.status_code if hasattr(e, "response") else None
            )
        except Exception as e:
            logging.error(f"Unexpected error during upload: {str(e)}", exc_info=True)
            raise OpenGradientError(f"Unexpected error during upload: {str(e)}")

    def infer(
        self,
        model_cid: str,
        inference_mode: InferenceMode,
        model_input: Dict[str, Union[str, int, float, List, np.ndarray]],
        max_retries: Optional[int] = None,
    ) -> Tuple[str, Dict[str, np.ndarray]]:
        """
        Perform inference on a model.

        Args:
            model_cid (str): The unique content identifier for the model from IPFS.
            inference_mode (InferenceMode): The inference mode.
            model_input (Dict[str, Union[str, int, float, List, np.ndarray]]): The input data for the model.
            max_retries (int, optional): Maximum number of retry attempts. Defaults to 5.

        Returns:
            Tuple[str, Dict[str, np.ndarray]]: The transaction hash and the model output.

        Raises:
            OpenGradientError: If the inference fails.
        """

        def execute_transaction():
            contract = self._blockchain.eth.contract(address=self._inference_hub_contract_address, abi=self._inference_abi)

            inference_mode_uint8 = int(inference_mode)
            converted_model_input = utils.convert_to_model_input(model_input)

            run_function = contract.functions.run(model_cid, inference_mode_uint8, converted_model_input)

            nonce = self._blockchain.eth.get_transaction_count(self._wallet_account.address, "pending")
            estimated_gas = run_function.estimate_gas({"from": self._wallet_account.address})
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
            tx_receipt = self._blockchain.eth.wait_for_transaction_receipt(tx_hash)

            if tx_receipt["status"] == 0:
                raise ContractLogicError(f"Transaction failed. Receipt: {tx_receipt}")

            parsed_logs = contract.events.InferenceResult().process_receipt(tx_receipt, errors=DISCARD)
            if len(parsed_logs) < 1:
                raise OpenGradientError("InferenceResult event not found in transaction logs")

            model_output = utils.convert_to_model_output(parsed_logs[0]["args"])
            return tx_hash.hex(), model_output

        return run_with_retry(execute_transaction, max_retries or 5)

    def llm_completion(
        self,
        model_cid: LLM,
        inference_mode: InferenceMode,
        prompt: str,
        max_tokens: int = 100,
        stop_sequence: Optional[List[str]] = None,
        temperature: float = 0.0,
        max_retries: Optional[int] = None,
    ) -> Tuple[str, str]:
        """
        Perform inference on an LLM model using completions.

        Args:
            model_cid (LLM): The unique content identifier for the model.
            inference_mode (InferenceMode): The inference mode.
            prompt (str): The input prompt for the LLM.
            max_tokens (int): Maximum number of tokens for LLM output. Default is 100.
            stop_sequence (List[str], optional): List of stop sequences for LLM. Default is None.
            temperature (float): Temperature for LLM inference, between 0 and 1. Default is 0.0.

        Returns:
            Tuple[str, str]: The transaction hash and the LLM completion output.

        Raises:
            OpenGradientError: If the inference fails.
        """

        def execute_transaction():
            # Check inference mode and supported model
            if inference_mode != LlmInferenceMode.VANILLA and inference_mode != LlmInferenceMode.TEE:
                raise OpenGradientError("Invalid inference mode %s: Inference mode must be VANILLA or TEE" % inference_mode)

            if inference_mode == LlmInferenceMode.TEE and model_cid not in TEE_LLM:
                raise OpenGradientError("That model CID is not supported yet supported for TEE inference")

            contract = self._blockchain.eth.contract(address=self._inference_hub_contract_address, abi=self._inference_abi)

            # Prepare LLM input
            llm_request = {
                "mode": inference_mode,
                "modelCID": model_cid,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "stop_sequence": stop_sequence or [],
                "temperature": int(temperature * 100),  # Scale to 0-100 range
            }
            logging.debug(f"Prepared LLM request: {llm_request}")

            run_function = contract.functions.runLLMCompletion(llm_request)

            nonce = self._blockchain.eth.get_transaction_count(self._wallet_account.address, "pending")
            estimated_gas = run_function.estimate_gas({"from": self._wallet_account.address})
            gas_limit = int(estimated_gas * 1.2)

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
            tx_receipt = self._blockchain.eth.wait_for_transaction_receipt(tx_hash)

            if tx_receipt["status"] == 0:
                raise ContractLogicError(f"Transaction failed. Receipt: {tx_receipt}")

            parsed_logs = contract.events.LLMCompletionResult().process_receipt(tx_receipt, errors=DISCARD)
            if len(parsed_logs) < 1:
                raise OpenGradientError("LLM completion result event not found in transaction logs")

            llm_answer = parsed_logs[0]["args"]["response"]["answer"]
            return tx_hash.hex(), llm_answer

        return run_with_retry(execute_transaction, max_retries or 5)

    def llm_chat(
        self,
        model_cid: LLM,
        inference_mode: InferenceMode,
        messages: List[Dict],
        max_tokens: int = 100,
        stop_sequence: Optional[List[str]] = None,
        temperature: float = 0.0,
        tools: Optional[List[Dict]] = [],
        tool_choice: Optional[str] = None,
        max_retries: Optional[int] = None,
    ) -> Tuple[str, str]:
        """
        Perform inference on an LLM model using chat.

        Args:
            model_cid (LLM): The unique content identifier for the model.
            inference_mode (InferenceMode): The inference mode.
            messages (dict): The messages that will be passed into the chat.
                This should be in OpenAI API format (https://platform.openai.com/docs/api-reference/chat/create)
                Example:
                [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant."
                    },
                    {
                        "role": "user",
                        "content": "Hello!"
                    }
                ]
            max_tokens (int): Maximum number of tokens for LLM output. Default is 100.
            stop_sequence (List[str], optional): List of stop sequences for LLM. Default is None.
            temperature (float): Temperature for LLM inference, between 0 and 1. Default is 0.0.
            tools (List[dict], optional): Set of tools
                This should be in OpenAI API format (https://platform.openai.com/docs/api-reference/chat/create#chat-create-tools)
                Example:
                [
                    {
                        "type": "function",
                        "function": {
                            "name": "get_current_weather",
                            "description": "Get the current weather in a given location",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "The city and state, e.g. San Francisco, CA"
                                    },
                                    "unit": {
                                        "type": "string",
                                        "enum": ["celsius", "fahrenheit"]
                                    }
                                },
                                "required": ["location"]
                            }
                        }
                    }
                ]
            tool_choice (str, optional): Sets a specific tool to choose. Default value is "auto".

        Returns:
            Tuple[str, str, dict]: The transaction hash, finish reason, and a dictionary struct of LLM chat messages.

        Raises:
            OpenGradientError: If the inference fails.
        """

        def execute_transaction():
            # Check inference mode and supported model
            if inference_mode != LlmInferenceMode.VANILLA and inference_mode != LlmInferenceMode.TEE:
                raise OpenGradientError("Invalid inference mode %s: Inference mode must be VANILLA or TEE" % inference_mode)

            if inference_mode == LlmInferenceMode.TEE and model_cid not in TEE_LLM:
                raise OpenGradientError("That model CID is not supported yet supported for TEE inference")

            contract = self._blockchain.eth.contract(address=self._inference_hub_contract_address, abi=self._inference_abi)

            # For incoming chat messages, tool_calls can be empty. Add an empty array so that it will fit the ABI.
            for message in messages:
                if "tool_calls" not in message:
                    message["tool_calls"] = []
                if "tool_call_id" not in message:
                    message["tool_call_id"] = ""
                if "name" not in message:
                    message["name"] = ""

            # Create simplified tool structure for smart contract
            converted_tools = []
            if tools is not None:
                for tool in tools:
                    function = tool["function"]
                    converted_tool = {}
                    converted_tool["name"] = function["name"]
                    converted_tool["description"] = function["description"]
                    if (parameters := function.get("parameters")) is not None:
                        try:
                            converted_tool["parameters"] = json.dumps(parameters)
                        except Exception as e:
                            raise OpenGradientError("Chat LLM failed to convert parameters into JSON: %s", e)
                    converted_tools.append(converted_tool)

            # Prepare LLM input
            llm_request = {
                "mode": inference_mode,
                "modelCID": model_cid,
                "messages": messages,
                "max_tokens": max_tokens,
                "stop_sequence": stop_sequence or [],
                "temperature": int(temperature * 100),  # Scale to 0-100 range
                "tools": converted_tools or [],
                "tool_choice": tool_choice if tool_choice else ("" if tools is None else "auto"),
            }
            logging.debug(f"Prepared LLM request: {llm_request}")

            run_function = contract.functions.runLLMChat(llm_request)

            nonce = self._blockchain.eth.get_transaction_count(self._wallet_account.address, "pending")
            estimated_gas = run_function.estimate_gas({"from": self._wallet_account.address})
            gas_limit = int(estimated_gas * 1.2)

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
            tx_receipt = self._blockchain.eth.wait_for_transaction_receipt(tx_hash)

            if tx_receipt["status"] == 0:
                raise ContractLogicError(f"Transaction failed. Receipt: {tx_receipt}")

            parsed_logs = contract.events.LLMChatResult().process_receipt(tx_receipt, errors=DISCARD)
            if len(parsed_logs) < 1:
                raise OpenGradientError("LLM chat result event not found in transaction logs")

            llm_result = parsed_logs[0]["args"]["response"]
            message = dict(llm_result["message"])
            if (tool_calls := message.get("tool_calls")) is not None:
                message["tool_calls"] = [dict(tool_call) for tool_call in tool_calls]

            return tx_hash.hex(), llm_result["finish_reason"], message

        return run_with_retry(execute_transaction, max_retries or 5)

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
        headers = {"Authorization": f'Bearer {self._hub_user["idToken"]}'}

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
            raise OpenGradientError(
                f"File listing failed: {str(e)}", status_code=e.response.status_code if hasattr(e, "response") else None
            )
        except Exception as e:
            logging.error(f"Unexpected error during file listing: {str(e)}", exc_info=True)
            raise OpenGradientError(f"Unexpected error during file listing: {str(e)}")

    def generate_image(
        self,
        model_cid: str,
        prompt: str,
        host: str = DEFAULT_IMAGE_GEN_HOST,
        port: int = DEFAULT_IMAGE_GEN_PORT,
        width: int = 1024,
        height: int = 1024,
        timeout: int = 300,  # 5 minute timeout
        max_retries: int = 3,
    ) -> bytes:
        """
        Generate an image using a diffusion model through gRPC.

        Args:
            model_cid (str): The model identifier (e.g. "stabilityai/stable-diffusion-xl-base-1.0")
            prompt (str): The text prompt to generate the image from
            host (str, optional): gRPC host address. Defaults to DEFAULT_IMAGE_GEN_HOST.
            port (int, optional): gRPC port number. Defaults to DEFAULT_IMAGE_GEN_PORT.
            width (int, optional): Output image width. Defaults to 1024.
            height (int, optional): Output image height. Defaults to 1024.
            timeout (int, optional): Maximum time to wait for generation in seconds. Defaults to 300.
            max_retries (int, optional): Maximum number of retry attempts. Defaults to 3.

        Returns:
            bytes: The raw image data bytes

        Raises:
            OpenGradientError: If the image generation fails
            TimeoutError: If the generation exceeds the timeout period
        """

        def exponential_backoff(attempt: int, max_delay: float = 30.0) -> None:
            """Calculate and sleep for exponential backoff duration"""
            delay = min(0.1 * (2**attempt), max_delay)
            time.sleep(delay)

        channel = None
        start_time = time.time()
        retry_count = 0

        try:
            while retry_count < max_retries:
                try:
                    # Initialize gRPC channel and stub
                    channel = grpc.insecure_channel(f"{host}:{port}")
                    stub = infer_pb2_grpc.InferenceServiceStub(channel)

                    # Create image generation request
                    image_request = infer_pb2.ImageGenerationRequest(model=model_cid, prompt=prompt, height=height, width=width)

                    # Create inference request with random transaction ID
                    tx_id = str(uuid.uuid4())
                    request = infer_pb2.InferenceRequest(tx=tx_id, image_generation=image_request)

                    # Send request with timeout
                    response_id = stub.RunInferenceAsync(
                        request,
                        timeout=min(30, timeout),  # Initial request timeout
                    )

                    # Poll for completion
                    attempt = 0
                    while True:
                        # Check timeout
                        if time.time() - start_time > timeout:
                            raise TimeoutError(f"Image generation timed out after {timeout} seconds")

                        status_request = infer_pb2.InferenceTxId(id=response_id.id)
                        try:
                            status = stub.GetInferenceStatus(
                                status_request,
                                timeout=min(5, timeout),  # Status check timeout
                            ).status
                        except grpc.RpcError as e:
                            logging.warning(f"Status check failed (attempt {attempt}): {str(e)}")
                            exponential_backoff(attempt)
                            attempt += 1
                            continue

                        if status == infer_pb2.InferenceStatus.STATUS_COMPLETED:
                            break
                        elif status == infer_pb2.InferenceStatus.STATUS_ERROR:
                            raise OpenGradientError("Image generation failed on server")
                        elif status != infer_pb2.InferenceStatus.STATUS_IN_PROGRESS:
                            raise OpenGradientError(f"Unexpected status: {status}")

                        exponential_backoff(attempt)
                        attempt += 1

                    # Get result
                    result = stub.GetInferenceResult(
                        response_id,
                        timeout=min(30, timeout),  # Result fetch timeout
                    )
                    return result.image_generation_result.image_data

                except (grpc.RpcError, TimeoutError) as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise OpenGradientError(f"Image generation failed after {max_retries} retries: {str(e)}")

                    logging.warning(f"Attempt {retry_count} failed: {str(e)}. Retrying...")
                    exponential_backoff(retry_count)

        except grpc.RpcError as e:
            logging.error(f"gRPC error: {str(e)}")
            raise OpenGradientError(f"Image generation failed: {str(e)}")
        except TimeoutError as e:
            logging.error(f"Timeout error: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Error in generate image method: {str(e)}", exc_info=True)
            raise OpenGradientError(f"Image generation failed: {str(e)}")
        finally:
            if channel:
                channel.close()

    def _get_model_executor_abi(self) -> List[Dict]:
        """
        Returns the ABI for the ModelExecutorHistorical contract.
        """
        abi_path = Path(__file__).parent / "abi" / "ModelExecutorHistorical.abi"
        with open(abi_path, "r") as f:
            return json.load(f)

    def new_workflow(
        self,
        model_cid: str,
        input_query: Union[Dict[str, Any], HistoricalInputQuery],
        input_tensor_name: str,
        scheduler_params: Optional[SchedulerParams] = None,
    ) -> str:
        """
        Deploy a new workflow contract with the specified parameters.
        """
        if isinstance(input_query, dict):
            input_query = HistoricalInputQuery.from_dict(input_query)

        # Get contract ABI and bytecode
        abi = self._get_model_executor_abi()
        bin_path = Path(__file__).parent / "contracts" / "templates" / "ModelExecutorHistorical.bin"

        with open(bin_path, "r") as f:
            bytecode = f.read().strip()

        print("📦 Deploying workflow contract...")

        # Create contract instance
        contract = self._blockchain.eth.contract(abi=abi, bytecode=bytecode)

        # Deploy contract with constructor arguments
        transaction = contract.constructor(
            model_cid,
            input_query.to_abi_format(),
            "0x00000000000000000000000000000000000000F5",  # Historical contract address
            input_tensor_name,
        ).build_transaction(
            {
                "from": self._wallet_account.address,
                "nonce": self._blockchain.eth.get_transaction_count(self._wallet_account.address, "pending"),
                "gas": 15000000,
                "gasPrice": self._blockchain.eth.gas_price,
                "chainId": self._blockchain.eth.chain_id,
            }
        )

        signed_txn = self._wallet_account.sign_transaction(transaction)
        tx_hash = self._blockchain.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_receipt = self._blockchain.eth.wait_for_transaction_receipt(tx_hash)
        contract_address = tx_receipt.contractAddress

        print(f"✅ Workflow contract deployed at: {contract_address}")

        # Register with scheduler if params provided
        if scheduler_params:
            print("\n⏰ Setting up automated execution schedule...")
            print(f"   • Frequency: Every {scheduler_params.frequency} seconds")
            print(f"   • Duration: {scheduler_params.duration_hours} hours")
            print(f"   • End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(scheduler_params.end_time))}")

            scheduler_abi = [
                {
                    "inputs": [
                        {"internalType": "address", "name": "contractAddress", "type": "address"},
                        {"internalType": "uint256", "name": "endTime", "type": "uint256"},
                        {"internalType": "uint256", "name": "frequency", "type": "uint256"},
                    ],
                    "name": "registerTask",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function",
                }
            ]

            scheduler_address = "0xE81a54399CFDf551bB917d0427464fE54537D245"
            scheduler_contract = self._blockchain.eth.contract(address=scheduler_address, abi=scheduler_abi)

            try:
                # Register the workflow with the scheduler
                scheduler_tx = scheduler_contract.functions.registerTask(
                    contract_address, scheduler_params.end_time, scheduler_params.frequency
                ).build_transaction(
                    {
                        "from": self._wallet_account.address,
                        "gas": 300000,
                        "gasPrice": self._blockchain.eth.gas_price,
                        "nonce": self._blockchain.eth.get_transaction_count(self._wallet_account.address, "pending"),
                        "chainId": self._blockchain.eth.chain_id,
                    }
                )

                signed_scheduler_tx = self._wallet_account.sign_transaction(scheduler_tx)
                scheduler_tx_hash = self._blockchain.eth.send_raw_transaction(signed_scheduler_tx.raw_transaction)
                self._blockchain.eth.wait_for_transaction_receipt(scheduler_tx_hash)

                print("✅ Automated execution schedule set successfully!")
                print(f"   Transaction hash: {scheduler_tx_hash.hex()}")

            except Exception as e:
                print("❌ Failed to set up automated execution schedule")
                print(f"   Error: {str(e)}")
                print("   The workflow contract is still deployed and can be executed manually.")

        return contract_address

    def read_workflow_result(self, contract_address: str) -> Any:
        """
        Reads the latest inference result from a deployed workflow contract.

        Args:
            contract_address (str): Address of the deployed workflow contract

        Returns:
            Any: The inference result from the contract

        Raises:
            ContractLogicError: If the transaction fails
            Web3Error: If there are issues with the web3 connection or contract interaction
        """
        # Get the contract interface
        contract = self._blockchain.eth.contract(address=Web3.to_checksum_address(contract_address), abi=self._get_model_executor_abi())

        # Get the result
        result = contract.functions.getInferenceResult().call()
        return result

    def run_workflow(self, contract_address: str) -> ModelOutput:
        """
        Triggers the run() function on a deployed workflow contract and returns the result.

        Args:
            contract_address (str): Address of the deployed workflow contract

        Returns:
            ModelOutput: The inference result from the contract

        Raises:
            ContractLogicError: If the transaction fails
            Web3Error: If there are issues with the web3 connection or contract interaction
        """
        # Get the contract interface
        contract = self._blockchain.eth.contract(address=Web3.to_checksum_address(contract_address), abi=self._get_model_executor_abi())

        # Call run() function
        nonce = self._blockchain.eth.get_transaction_count(self._wallet_account.address, "pending")

        run_function = contract.functions.run()
        transaction = run_function.build_transaction(
            {
                "from": self._wallet_account.address,
                "nonce": nonce,
                "gas": 30000000,
                "gasPrice": self._blockchain.eth.gas_price,
                "chainId": self._blockchain.eth.chain_id,
            }
        )

        signed_txn = self._wallet_account.sign_transaction(transaction)
        tx_hash = self._blockchain.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_receipt = self._blockchain.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt.status == 0:
            raise ContractLogicError(f"Run transaction failed. Receipt: {tx_receipt}")

        # Get the inference result from the contract
        result = contract.functions.getInferenceResult().call()
        return result


def run_with_retry(txn_function, max_retries=5):
    """
    Execute a blockchain transaction with retry logic.

    Args:
        txn_function: Function that executes the transaction
        max_retries (int): Maximum number of retry attempts
    """
    last_error = None
    for attempt in range(max_retries):
        try:
            return txn_function()
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                if "nonce too low" in str(e) or "nonce too high" in str(e):
                    time.sleep(1)  # Wait before retry
                    continue
                # If it's not a nonce error, raise immediately
                raise
    # If we've exhausted all retries, raise the last error
    raise OpenGradientError(f"Transaction failed after {max_retries} attempts: {str(last_error)}")
