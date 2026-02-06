"""On-chain ONNX model inference via blockchain smart contracts."""

import base64
import json
import urllib.parse
from typing import Dict, List, Optional, Union

import numpy as np
import requests
from eth_account.account import LocalAccount
from web3 import Web3
from web3.exceptions import ContractLogicError
from web3.logs import DISCARD

from ..types import InferenceMode, InferenceResult
from ._conversions import convert_to_model_input, convert_to_model_output
from ._utils import get_abi, run_with_retry
from .exceptions import OpenGradientError

# How much time we wait for inference txn to be included in chain
INFERENCE_TX_TIMEOUT = 120

PRECOMPILE_CONTRACT_ADDRESS = "0x00000000000000000000000000000000000000F4"


class Inference:
    """
    On-chain model inference namespace.

    Provides access to decentralized ONNX model inference via blockchain smart contracts.
    Supports multiple inference modes including VANILLA, TEE, and ZKML.

    Usage:
        client = og.Client(...)
        result = client.inference.infer(model_cid, InferenceMode.VANILLA, model_input)
    """

    def __init__(
        self,
        blockchain: Web3,
        wallet_account: LocalAccount,
        inference_hub_contract_address: str,
        api_url: str,
    ):
        self._blockchain = blockchain
        self._wallet_account = wallet_account
        self._inference_hub_contract_address = inference_hub_contract_address
        self._api_url = api_url
        self._inference_abi = None
        self._precompile_abi = None

    @property
    def inference_abi(self) -> dict:
        if self._inference_abi is None:
            self._inference_abi = get_abi("inference.abi")
        return self._inference_abi

    @property
    def precompile_abi(self) -> dict:
        if self._precompile_abi is None:
            self._precompile_abi = get_abi("InferencePrecompile.abi")
        return self._precompile_abi

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
            contract = self._blockchain.eth.contract(address=self._inference_hub_contract_address, abi=self.inference_abi)
            precompile_contract = self._blockchain.eth.contract(address=PRECOMPILE_CONTRACT_ADDRESS, abi=self.precompile_abi)

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
