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
import secrets

logging.basicConfig(level=logging.DEBUG)

class Client:
    def __init__(self, wallet_address, private_key):
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.rpc_url = "http://18.218.115.248:8545"
        self._w3 = None
        self.contract_address = "0x2EFf2e5e706f895B1d86E4C5d24DF29A976070A4"
        self.storage_url = "http://18.222.64.142:5000"

        with open('abi/inference.abi', 'r') as abi_file:
            inference_abi = json.load(abi_file)
        self.abi = inference_abi

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
                    headers={"Content-Type": f"multipart/form-data"}
                )
                response.raise_for_status()
                return {"model_cid": response.json()["cid"]}
        except requests.RequestException as e:
            raise UploadError(f"Upload failed: {str(e)}")

    def infer(self, model_id: str, inference_mode: InferenceMode, model_input: ModelInput) -> ModelOutput:
        logging.debug("Entering infer method")
        self._initialize_web3()
        logging.debug(f"Web3 initialized. Connected: {self.w3.is_connected()}")

        try:
            logging.debug(f"Creating contract instance. Address: {self.contract_address}")
            contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)
            logging.debug("Contract instance created successfully")

            logging.debug(f"Model ID: {model_id}")
            logging.debug(f"Inference Mode: {inference_mode}")
            logging.debug(f"Model Input: {model_input.__dict__}")

            # Convert InferenceMode to uint8
            inference_mode_uint8 = int(inference_mode)

            # Prepare ModelInput struct
            number_tensors = [("", [(int(v), 0) for v in model_input.numbers])]
            string_tensors = []  # Assuming no string inputs are required

            model_input_struct = (number_tensors, string_tensors)

            logging.debug("Preparing run function")
            run_function = contract.functions.run(
                model_id,
                inference_mode_uint8,
                model_input_struct
            )
            logging.debug("Run function prepared successfully")

            logging.debug("Calling run function")
            try:
                output = run_function.call({'from': self.wallet_address})
                logging.debug(f"Run function call successful. Raw output: {output}")
                
                # Parse the output
                parsed_output = self._parse_output(output)
                logging.debug(f"Parsed output: {parsed_output}")
                
                return ModelOutput(**parsed_output)
            except Exception as call_error:
                logging.error(f"Error calling run function: {str(call_error)}")
                logging.debug(f"Function arguments: model_id={model_id}, inference_mode={inference_mode_uint8}, model_input={model_input_struct}")
                raise

        except Exception as e:
            logging.error(f"Error in infer method: {str(e)}", exc_info=True)
            raise InferenceError(f"Inference failed: {str(e)}")

    def _parse_output(self, raw_output):
        logging.debug(f"Parsing raw output: {raw_output}")
        parsed_output = {
            'numbers': [],
            'strings': [],
            'is_simulation_result': False
        }
        
        if isinstance(raw_output, tuple) and len(raw_output) >= 2:
            number_tensors, string_tensors = raw_output[:2]
            
            logging.debug(f"Number tensors: {number_tensors}")
            logging.debug(f"String tensors: {string_tensors}")
            
            for name, values in number_tensors:
                parsed_output['numbers'].append({'name': name, 'values': values})
            
            for name, values in string_tensors:
                parsed_output['strings'].append({'name': name, 'values': values})
        else:
            logging.warning(f"Unexpected raw output format: {raw_output}")
        
        logging.debug(f"Parsed output: {parsed_output}")
        return parsed_output

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

    def generate_ethereum_account():
        # Generate a random private key
        private_key = secrets.token_hex(32)
        
        # Create an account from the private key
        account = Account.from_key(private_key)
        
        return {
            'private_key': private_key,
            'address': account.address
        }

    # Generate a new account
    new_account = generate_ethereum_account()

    print(f"Private Key: {new_account['private_key']}")
    print(f"Ethereum Address: {new_account['address']}")
