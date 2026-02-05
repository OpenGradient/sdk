"""
Alpha Testnet features for OpenGradient SDK.

This module contains features that are only available on the Alpha Testnet,
including workflow management and ML model execution.
"""

import json
from pathlib import Path
from typing import List, Optional

from eth_account.account import LocalAccount
from web3 import Web3
from web3.exceptions import ContractLogicError

from ..defaults import DEFAULT_SCHEDULER_ADDRESS
from ..types import HistoricalInputQuery, ModelOutput, SchedulerParams
from ..utils import convert_array_to_model_output

# How much time we wait for txn to be included in chain
INFERENCE_TX_TIMEOUT = 120
REGULAR_TX_TIMEOUT = 30


class Alpha:
    """
    Alpha Testnet features namespace.

    This class provides access to features that are only available on the Alpha Testnet,
    including workflow deployment and execution.

    Usage:
        client = og.Client(...)
        result = client.alpha.new_workflow(model_cid, input_query, input_tensor_name)
    """

    def __init__(self, blockchain: Web3, wallet_account: LocalAccount):
        self._blockchain = blockchain
        self._wallet_account = wallet_account

    def _get_abi(self, abi_name: str) -> dict:
        """Returns the ABI for the requested contract."""
        abi_path = Path(__file__).parent / "abi" / abi_name
        with open(abi_path, "r") as f:
            return json.load(f)

    def _get_bin(self, bin_name: str) -> str:
        """Returns the bin for the requested contract."""
        bin_path = Path(__file__).parent / "bin" / bin_name
        with open(bin_path, "r", encoding="utf-8") as f:
            bytecode = f.read().strip()
            if not bytecode.startswith("0x"):
                bytecode = "0x" + bytecode
            return bytecode

    def new_workflow(
        self,
        model_cid: str,
        input_query: HistoricalInputQuery,
        input_tensor_name: str,
        scheduler_params: Optional[SchedulerParams] = None,
    ) -> str:
        """
        Deploy a new workflow contract with the specified parameters.

        This function deploys a new workflow contract on OpenGradient that connects
        an AI model with its required input data. When executed, the workflow will fetch
        the specified model, evaluate the input query to get data, and perform inference.

        The workflow can be set to execute manually or automatically via a scheduler.

        Args:
            model_cid (str): CID of the model to be executed from the Model Hub
            input_query (HistoricalInputQuery): Input definition for the model inference,
                will be evaluated at runtime for each inference
            input_tensor_name (str): Name of the input tensor expected by the model
            scheduler_params (Optional[SchedulerParams]): Scheduler configuration for automated execution:
                - frequency: Execution frequency in seconds
                - duration_hours: How long the schedule should live for

        Returns:
            str: Deployed contract address. If scheduler_params was provided, the workflow
                 will be automatically executed according to the specified schedule.

        Raises:
            Exception: If transaction fails or gas estimation fails
        """
        from .model_hub_inference import run_with_retry

        # Get contract ABI and bytecode
        abi = self._get_abi("PriceHistoryInference.abi")
        bytecode = self._get_bin("PriceHistoryInference.bin")

        def deploy_transaction():
            contract = self._blockchain.eth.contract(abi=abi, bytecode=bytecode)
            query_tuple = input_query.to_abi_format()
            constructor_args = [model_cid, input_tensor_name, query_tuple]

            try:
                # Estimate gas needed
                estimated_gas = contract.constructor(*constructor_args).estimate_gas({"from": self._wallet_account.address})
                gas_limit = int(estimated_gas * 1.2)
            except Exception as e:
                print(f"Gas estimation failed: {str(e)}")
                gas_limit = 5000000  # Conservative fallback
                print(f"Using fallback gas limit: {gas_limit}")

            transaction = contract.constructor(*constructor_args).build_transaction(
                {
                    "from": self._wallet_account.address,
                    "nonce": self._blockchain.eth.get_transaction_count(self._wallet_account.address, "pending"),
                    "gas": gas_limit,
                    "gasPrice": self._blockchain.eth.gas_price,
                    "chainId": self._blockchain.eth.chain_id,
                }
            )

            signed_txn = self._wallet_account.sign_transaction(transaction)
            tx_hash = self._blockchain.eth.send_raw_transaction(signed_txn.raw_transaction)

            tx_receipt = self._blockchain.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

            if tx_receipt["status"] == 0:
                raise Exception(f"Contract deployment failed, transaction hash: {tx_hash.hex()}")

            return tx_receipt.contractAddress

        contract_address = run_with_retry(deploy_transaction)

        if scheduler_params:
            self._register_with_scheduler(contract_address, scheduler_params)

        return contract_address

    def _register_with_scheduler(self, contract_address: str, scheduler_params: SchedulerParams) -> None:
        """
        Register the deployed workflow contract with the scheduler for automated execution.

        Args:
            contract_address (str): Address of the deployed workflow contract
            scheduler_params (SchedulerParams): Scheduler configuration containing:
                - frequency: Execution frequency in seconds
                - duration_hours: How long to run in hours
                - end_time: Unix timestamp when scheduling should end

        Raises:
            Exception: If registration with scheduler fails. The workflow contract will
                      still be deployed and can be executed manually.
        """
        scheduler_abi = self._get_abi("WorkflowScheduler.abi")

        # Scheduler contract address
        scheduler_address = DEFAULT_SCHEDULER_ADDRESS
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
            self._blockchain.eth.wait_for_transaction_receipt(scheduler_tx_hash, timeout=REGULAR_TX_TIMEOUT)
        except Exception as e:
            print(f"Error registering contract with scheduler: {str(e)}")
            print("  The workflow contract is still deployed and can be executed manually.")

    def read_workflow_result(self, contract_address: str) -> ModelOutput:
        """
        Reads the latest inference result from a deployed workflow contract.

        Args:
            contract_address (str): Address of the deployed workflow contract

        Returns:
            ModelOutput: The inference result from the contract

        Raises:
            ContractLogicError: If the transaction fails
            Web3Error: If there are issues with the web3 connection or contract interaction
        """
        # Get the contract interface
        contract = self._blockchain.eth.contract(
            address=Web3.to_checksum_address(contract_address), abi=self._get_abi("PriceHistoryInference.abi")
        )

        # Get the result
        result = contract.functions.getInferenceResult().call()

        return convert_array_to_model_output(result)

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
        contract = self._blockchain.eth.contract(
            address=Web3.to_checksum_address(contract_address), abi=self._get_abi("PriceHistoryInference.abi")
        )

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
        tx_receipt = self._blockchain.eth.wait_for_transaction_receipt(tx_hash, timeout=INFERENCE_TX_TIMEOUT)

        if tx_receipt.status == 0:
            raise ContractLogicError(f"Run transaction failed. Receipt: {tx_receipt}")

        # Get the inference result from the contract
        result = contract.functions.getInferenceResult().call()

        return convert_array_to_model_output(result)

    def read_workflow_history(self, contract_address: str, num_results: int) -> List[ModelOutput]:
        """
        Gets historical inference results from a workflow contract.

        Retrieves the specified number of most recent inference results from the contract's
        storage, with the most recent result first.

        Args:
            contract_address (str): Address of the deployed workflow contract
            num_results (int): Number of historical results to retrieve

        Returns:
            List[ModelOutput]: List of historical inference results
        """
        contract = self._blockchain.eth.contract(
            address=Web3.to_checksum_address(contract_address), abi=self._get_abi("PriceHistoryInference.abi")
        )

        results = contract.functions.getLastInferenceResults(num_results).call()
        return [convert_array_to_model_output(result) for result in results]
