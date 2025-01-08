from web3 import Web3
from web3.exceptions import ContractLogicError
import logging
from typing import Optional

class WorkflowManager:
    def __init__(self, w3: Web3, private_key: str):
        """
        Initialize the WorkflowManager.
        
        Args:
            w3 (Web3): Web3 instance
            private_key (str): Private key for signing transactions
        """
        self._w3 = w3
        self.private_key = private_key
        self.wallet_address = self._w3.eth.account.from_key(private_key).address

    def deploy_contract(self, abi: list, bytecode: str, constructor_args: Optional[list] = None) -> str:
        """
        Deploy a contract with the given ABI and bytecode.
        
        Args:
            abi (list): Contract ABI
            bytecode (str): Contract bytecode
            constructor_args (list, optional): Arguments for the constructor
            
        Returns:
            str: Deployed contract address
        """
        contract = self._w3.eth.contract(abi=abi, bytecode=bytecode)
        
        # Prepare constructor transaction
        constructor = contract.constructor(*constructor_args if constructor_args else [])
        
        # Get transaction parameters
        nonce = self._w3.eth.get_transaction_count(self.wallet_address, 'pending')
        
        transaction = constructor.build_transaction({
            'from': self.wallet_address,
            'nonce': nonce,
            'gasPrice': self._w3.eth.gas_price,
        })

        # Sign and send transaction
        signed_tx = self._w3.eth.account.sign_transaction(transaction, self.private_key)
        tx_hash = self._w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 0:
            raise ContractLogicError(f"Deployment failed. Receipt: {receipt}")

        return receipt.contractAddress 