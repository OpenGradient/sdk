import logging
from web3 import Web3
from web3.exceptions import ContractLogicError

# Example hard-coded Solidity code. You can adapt to load from an external file.
MODEL_EXECUTOR_VOLATILITY_SOL = r"""
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

/**
 * @title ModelExecutorVolatility
 * @dev Implementation of IModelExecutor to predict ETH/USDT volatility using OpenGradient's model.
 */
contract ModelExecutorVolatility  {
    event InferenceResultEmitted(address indexed caller, uint256 inferenceResult);
    uint256 private inferenceResult;

    function run() public {
        inferenceResult = inferenceResult + 1;
        emit InferenceResultEmitted(msg.sender, inferenceResult);
    }
}
"""

class WorkflowManager:
    def __init__(self, web3: Web3, private_key: str):
        """
        Manages deployment and interaction with user-defined workflow contracts.
        """
        self._web3 = web3
        self._private_key = private_key
        self._account = self._web3.eth.account.from_key(private_key)
        self._wallet_address = self._web3.toChecksumAddress(self._account.address)

    def new_workflow(self, solidity_source: str = MODEL_EXECUTOR_VOLATILITY_SOL) -> str:
        """
        Deploy a new contract from the provided Solidity source code.
        """
        logging.info("Compiling and deploying new workflow contract...")

        compiled_bytecode, contract_abi = self._mock_compile(solidity_source)
        contract = self._web3.eth.contract(abi=contract_abi, bytecode=compiled_bytecode)
        nonce = self._web3.eth.get_transaction_count(self._wallet_address, 'pending')
        
        transaction = contract.constructor().buildTransaction({
            'from': self._wallet_address,
            'nonce': nonce,
            'gasPrice': self._web3.eth.gas_price,
        })

        signed_tx = self._web3.eth.account.sign_transaction(transaction, self._private_key)
        tx_hash = self._web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = self._web3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 0:
            raise ContractLogicError(f"Deployment failed. Receipt: {receipt}")

        contract_address = receipt.contractAddress
        logging.info(f"New workflow contract deployed at: {contract_address}")
        return contract_address

    def read_workflow(self, contract_address: str) -> str:
        """
        Call the 'run()' function on a previously deployed workflow contract.
        """
        logging.info(f"Calling 'run()' on contract at {contract_address} ...")

        mock_abi = self._mock_abi()
        checksum_address = self._web3.toChecksumAddress(contract_address)
        contract = self._web3.eth.contract(address=checksum_address, abi=mock_abi)

        nonce = self._web3.eth.get_transaction_count(self._wallet_address, 'pending')
        run_function = contract.functions.run()
        estimated_gas = run_function.estimateGas({'from': self._wallet_address})
        
        transaction = run_function.buildTransaction({
            'from': self._wallet_address,
            'nonce': nonce,
            'gas': int(estimated_gas * 2),
            'gasPrice': self._web3.eth.gas_price
        })

        signed_tx = self._web3.eth.account.sign_transaction(transaction, self._private_key)
        tx_hash = self._web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = self._web3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 0:
            raise ContractLogicError(f"'run' transaction failed. Receipt: {receipt}")

        logging.info(f"'run()' called successfully. TX Hash: {tx_hash.hex()}")
        return tx_hash.hex()

    def _mock_compile(self, solidity_code: str):
        """Mock compilation - replace with real compiler integration"""
        mock_abi = self._mock_abi()
        mock_bytecode = "0x608060405234801561001057600080fd5b5060..."  # shortened
        return mock_bytecode, mock_abi

    def _mock_abi(self):
        """Minimal ABI with run() function"""
        return [
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "internalType": "address", "name": "caller", "type": "address"},
                    {"indexed": False, "internalType": "uint256", "name": "inferenceResult", "type": "uint256"}
                ],
                "name": "InferenceResultEmitted",
                "type": "event"
            },
            {
                "inputs": [],
                "name": "run",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ] 