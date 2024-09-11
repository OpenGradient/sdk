import requests
import os
import time
import json
from src.exceptions import UploadError, InferenceError, InvalidInputError
import web3
from web3 import Web3
from web3.auto import w3
from eth_account import Account
from src.types import ModelInput, InferenceMode, Abi, ModelOutput
import pickle
import onnx
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG)

class InferenceMode:
    VANILLA = 0
    PRIVATE = 1
    VERIFIED = 2

class Client:
    def __init__(self, wallet_address, private_key):
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.rpc_url = "http://18.218.115.248:8545"
        self._w3 = None
        self.contract_address = "0x2EFf2e5e706f895B1d86E4C5d24DF29A976070A4"

    @property
    def w3(self):
        if self._w3 is None:
            self._w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        return self._w3

    @w3.setter
    def w3(self, value):
        self._w3 = value

    def _initialize_web3(self):
        if self._w3 is None:
            self._w3 = Web3(Web3.HTTPProvider(self.rpc_url))

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

    def infer(self, model_id: str, inference_mode: InferenceMode, model_input: ModelInput) -> ModelOutput:
        self._initialize_web3()

        try:
            contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)

            # Prepare the transaction
            tx = contract.functions.run(
                model_id,
                inference_mode,
                model_input.__dict__
            ).build_transaction({
                'from': self.wallet_address,
                'gas': 0,  # You might want to estimate this
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
            })

            # Sign and send the transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # Wait for the transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            # Decode the output
            output = contract.functions.run().call(
                model_id,
                inference_mode,
                model_input.__dict__
            )

            return ModelOutput(**output)

        except Exception as e:
            raise InferenceError(f"Inference failed: {str(e)}")

    # def download(self, model_cid):
    #     try:
    #         response = requests.get(
    #             f"{self.storage_url}/download/{model_cid}",
    #             headers={"Authorization": f"Bearer {self.api_key}"}
    #         )
    #         response.raise_for_status()
    #         return response.content
    #     except requests.RequestException as e:
    #         raise DownloadError(f"Download failed: {str(e)}")

    def convert_pickle_to_onnx(self, pickle_path):
        logging.debug(f"Attempting to load pickle file from {pickle_path}")
        try:
            with open(pickle_path, 'rb') as f:
                data = pickle.load(f)
            logging.debug(f"Pickle file loaded successfully. Type: {type(data)}")
        except Exception as e:
            logging.error(f"Failed to load pickle file: {str(e)}")
            raise

        if isinstance(data, dict):
            logging.debug("Loaded data is a dictionary. Searching for model...")
            model = self._find_model_in_dict(data)
        else:
            model = data

        logging.debug(f"Model type: {type(model)}")

        try:
            if hasattr(model, 'predict'):
                return self._convert_sklearn_model(model)
            elif hasattr(model, 'forward'):
                return self._convert_pytorch_model(model)
            elif hasattr(model, '__call__'):
                return self._convert_general_model(model)
            else:
                raise ValueError(f"Unsupported model type: {type(model)}")
        except Exception as e:
            logging.error(f"Error during model conversion: {str(e)}")
            raise

    def _find_model_in_dict(self, data):
        for key, value in data.items():
            if hasattr(value, 'predict') or hasattr(value, 'forward') or hasattr(value, '__call__'):
                logging.debug(f"Found potential model in key: {key}")
                return value
        raise ValueError("No suitable model found in the dictionary")

    def _convert_sklearn_model(self, model):
        logging.debug("Converting scikit-learn model to ONNX")
        if hasattr(model, 'n_features_in_'):
            n_features = model.n_features_in_
        else:
            n_features = 10
            logging.warning(f"n_features_in_ not found. Using default value: {n_features}")

        initial_type = [('float_input', FloatTensorType([None, n_features]))]
        onnx_model = convert_sklearn(model, initial_types=initial_type)
        onnx_path = 'model.onnx'
        onnx.save_model(onnx_model, onnx_path)
        logging.debug(f"ONNX model saved at: {onnx_path}")
        return onnx_path

    def _convert_pytorch_model(self, model):
        logging.error("PyTorch conversion not yet implemented")
        raise NotImplementedError("PyTorch conversion not yet implemented")

    def _convert_general_model(self, model):
        logging.error("General model conversion not yet implemented")
        raise NotImplementedError("General model conversion not yet implemented")
