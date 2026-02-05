import base64
import json
import time
import urllib.parse
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

import numpy as np
import requests
from eth_account.account import LocalAccount
from web3 import Web3
from web3.exceptions import ContractLogicError
from web3.logs import DISCARD

from ..exceptions import OpenGradientError
from ..types import InferenceMode, InferenceResult
from ..utils import convert_to_model_input, convert_to_model_output

# How much time we wait for inference txn to be included in chain
INFERENCE_TX_TIMEOUT = 120

PRECOMPILE_CONTRACT_ADDRESS = "0x00000000000000000000000000000000000000F4"

# How many times we retry a transaction because of nonce conflict
DEFAULT_MAX_RETRY = 5
DEFAULT_RETRY_DELAY_SEC = 1


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


class Inference:
    def __init__(
        self,
        blockchain: Web3,
        wallet_account: LocalAccount,
        inference_hub_contract_address: str,
        inference_abi: Dict,
        precompile_abi: Dict,
        api_url: str,
    ):
        self._blockchain = blockchain
        self._wallet_account = wallet_account
        self._inference_hub_contract_address = inference_hub_contract_address
        self._inference_abi = inference_abi
        self._precompile_abi = precompile_abi
        self._api_url = api_url

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
                raise OpenGradientError(f"Failed to get inference result: HTTP {response.status_code}")

        except requests.RequestException as e:
            raise OpenGradientError(f"Failed to get inference result: {str(e)}")
        except OpenGradientError:
            raise
        except Exception as e:
            raise OpenGradientError(f"Failed to get inference result: {str(e)}")

    def _get_abi(self, abi_name) -> str:
        """
        Returns the ABI for the requested contract.
        """
        abi_path = Path(__file__).parent.parent / "abi" / abi_name
        with open(abi_path, "r") as f:
            return json.load(f)

    def _get_bin(self, bin_name) -> str:
        """
        Returns the bin for the requested contract.
        """
        bin_path = Path(__file__).parent.parent / "bin" / bin_name
        # Read bytecode with explicit encoding
        with open(bin_path, "r", encoding="utf-8") as f:
            bytecode = f.read().strip()
            if not bytecode.startswith("0x"):
                bytecode = "0x" + bytecode
            return bytecode
