import requests
import os
import time
import json
from .exceptions import UploadError, InferenceError, InvalidInputError
import web3
from web3 import Web3

class Client:
    def __init__(self, api_key, storage_url="http://localhost:5000", rpc_url=None):
        self.api_key = api_key
        self.storage_url = storage_url
        self.rpc_url = rpc_url
        self.w3 = None  # We'll initialize this when needed
        with open(os.path.join(os.path.dirname(__file__), '..', 'abi', 'inference.abi'), 'r') as file:
            self.abi = json.load(file)

    def _initialize_web3(self):
        if self.w3 is None:
            if self.rpc_url is None:
                raise ValueError("RPC URL is required for blockchain operations")
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))

    def upload(self, model_path):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"File not found: {model_path}")

        try:
            with open(model_path, "rb") as file:
                files = {"file": (os.path.basename(model_path), file)}
                response = requests.post(
                    f"{self.storage_url}/upload",
                    files=files,
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                return {"model_cid": response.json()["cid"]}
        except requests.RequestException as e:
            raise UploadError(f"Upload failed: {str(e)}")

    def infer(self, model_cid, model_inputs):
        self._initialize_web3()

        try:
            contract_address = "0x1234567890123456789012345678901234567890"  # Hardcoded contract address
            contract = self.w3.eth.contract(address=contract_address, abi=self.abi)

            # Prepare the transaction
            tx = contract.functions.infer(model_cid, model_inputs).build_transaction({
                'from': self.w3.eth.account.from_key(self.api_key).address,
                'gas': 2000000,  # You might want to estimate this
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.w3.eth.account.from_key(self.api_key).address),
            })

            # Sign and send the transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.api_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # Wait for the transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            # Return the transaction hash as the inference ID
            return {'inference_id': tx_hash.hex()}

        except Exception as e:
            raise InferenceError(f"Inference failed: {str(e)}")

    def download(self, model_cid):
        try:
            response = requests.get(
                f"{self.storage_url}/download/{model_cid}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            raise DownloadError(f"Download failed: {str(e)}")
