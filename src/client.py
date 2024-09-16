import requests
import os
import time
import json
from src.exceptions import UploadError, InferenceError, InvalidInputError
import web3
from web3 import Web3
from web3.auto import w3
from eth_account import Account
from src.types import ModelInput, InferenceMode, Abi, ModelOutput, Number, NumberTensor, StringTensor
import pickle
import onnx
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import numpy as np
import logging
import secrets
from typing import Dict, Tuple
from web3.exceptions import ContractLogicError
from web3.datastructures import AttributeDict
import src.utils

logging.basicConfig(level=logging.DEBUG)

class Client:
    def __init__(self, wallet_address, private_key):
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.rpc_url = "http://18.218.115.248:8545"
        self._w3 = None
        self.contract_address = "0x8383C9bD7462F12Eb996DD02F78234C0421A6FaE"
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

    def upload(self, model_path: str) -> dict:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        try:
            with open(model_path, 'rb') as file:
                filename = os.path.basename(model_path)
                files = {'file': (filename, file, 'application/octet-stream')}
                headers = {
                    # Remove Content-Type header, let requests set it automatically
                }
                params = {
                    # Add any query parameters required by the server
                }

                logging.info(f"Uploading file: {model_path}")
                logging.debug(f"Upload URL: {self.storage_url}/upload")
                logging.debug(f"Headers: {headers}")
                logging.debug(f"Params: {params}")

                response = requests.post(
                    f"{self.storage_url}/upload",
                    files=files,
                    headers=headers,
                    params=params
                )

                logging.debug(f"Response status code: {response.status_code}")
                logging.debug(f"Response headers: {response.headers}")
                logging.debug(f"Response content: {response.text}")

                response.raise_for_status()

                json_response = response.json()
                logging.info(f"Upload successful. CID: {json_response.get('cid', 'N/A')}")
                return {"model_cid": json_response["cid"]}

        except requests.RequestException as e:
            logging.error(f"Upload failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Response status code: {e.response.status_code}")
                logging.error(f"Response headers: {e.response.headers}")
                logging.error(f"Response content: {e.response.text}")
            raise UploadError(f"Upload failed: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error during upload: {str(e)}")
            raise UploadError(f"Upload failed due to unexpected error: {str(e)}")
    
    def infer(self, model_id: str, inference_mode: InferenceMode, model_input: Dict[str, np.ndarray]) -> Tuple[str, ModelOutput]:
        try:
            logging.debug("Entering infer method")
            self._initialize_web3()
            logging.debug(f"Web3 initialized. Connected: {self.w3.is_connected()}")

            logging.debug(f"Creating contract instance. Address: {self.contract_address}")
            contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)
            logging.debug("Contract instance created successfully")

            logging.debug(f"Model ID: {model_id}")
            logging.debug(f"Inference Mode: {inference_mode}")
            logging.debug(f"Model Input: {model_input}")

            # Convert InferenceMode to uint8
            inference_mode_uint8 = int(inference_mode)

            # Prepare ModelInput tuple
            converted_model_input = src.utils.convert_to_model_input(model_input)
            logging.debug(f"Prepared model input tuple: {converted_model_input}")

            logging.debug("Preparing run function")
            run_function = contract.functions.run(
                model_id,
                inference_mode_uint8,
                converted_model_input
            )
            logging.debug("Run function prepared successfully")

            # Build transaction
            nonce = self.w3.eth.get_transaction_count(self.wallet_address)
            logging.debug(f"Nonce: {nonce}")

            # Estimate gas
            estimated_gas = run_function.estimate_gas({'from': self.wallet_address})
            logging.debug(f"Estimated gas: {estimated_gas}")

            # Increase gas limit by 20%
            gas_limit = int(estimated_gas * 3)
            logging.debug(f"Gas limit set to: {gas_limit}")

            transaction = run_function.build_transaction({
                'from': self.wallet_address,
                'nonce': nonce,
                'gas': gas_limit,
                'gasPrice': self.w3.eth.gas_price,
            })

            logging.debug(f"Transaction built: {transaction}")

            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            logging.debug("Transaction signed successfully")

            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            logging.debug(f"Transaction sent. Hash: {tx_hash.hex()}")

            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            logging.debug(f"Transaction receipt received: {tx_receipt}")

            # Check if the transaction was successful
            if tx_receipt['status'] == 0:
                raise ContractLogicError(f"Transaction failed. Receipt: {tx_receipt}")

            # Process the InferenceResult event
            inference_result = None
            for log in tx_receipt['logs']:
                try:
                    decoded_log = contract.events.InferenceResult().process_log(log)
                    inference_result = decoded_log
                    break
                except:
                    continue

            if inference_result is None:
                logging.error("InferenceResult event not found in transaction logs")
                logging.debug(f"Transaction receipt logs: {tx_receipt['logs']}")
                raise InferenceError("InferenceResult event not found in transaction logs")

            # Extract the ModelOutput from the event
            event_data = inference_result['args']
            logging.debug(f"Raw event data: {event_data}")

            try:
                model_output = self._parse_event_data(event_data)
                logging.debug(f"Parsed ModelOutput: {model_output}")
            except Exception as e:
                logging.error(f"Error parsing event data: {str(e)}", exc_info=True)
                raise InferenceError(f"Failed to parse event data: {str(e)}")

            return tx_hash.hex(), model_output

        except ContractLogicError as e:
            logging.error(f"Contract logic error: {str(e)}", exc_info=True)
            raise InferenceError(f"Inference failed due to contract logic error: {str(e)}")
        except Exception as e:
            logging.error(f"Error in infer method: {str(e)}", exc_info=True)
            raise InferenceError(f"Inference failed: {str(e)}")

    def _parse_event_data(self, event_data) -> ModelOutput:
        logging.debug(f"Parsing event data: {event_data}")
        
        numbers = []
        strings = []
        is_simulation_result = False

        if isinstance(event_data, AttributeDict):
            output = event_data.get('output', {})
            logging.debug(f"Output data: {output}")

            if isinstance(output, AttributeDict):
                # Parse numbers
                for tensor in output.get('numbers', []):
                    logging.debug(f"Processing number tensor: {tensor}")
                    if isinstance(tensor, AttributeDict):
                        name = tensor.get('name')
                        values = []
                        for v in tensor.get('values', []):
                            if isinstance(v, AttributeDict):
                                values.append(Number(value=v.get('value'), decimals=v.get('decimals')))
                        numbers.append(NumberTensor(name=name, values=values))

                # Parse strings
                for tensor in output.get('strings', []):
                    logging.debug(f"Processing string tensor: {tensor}")
                    if isinstance(tensor, AttributeDict):
                        name = tensor.get('name')
                        values = tensor.get('values', [])
                        strings.append(StringTensor(name=name, values=values))

                is_simulation_result = output.get('is_simulation_result', False)
            else:
                logging.warning(f"Unexpected output type: {type(output)}")
        else:
            logging.warning(f"Unexpected event_data type: {type(event_data)}")

        logging.debug(f"Parsed numbers: {numbers}")
        logging.debug(f"Parsed strings: {strings}")
        logging.debug(f"Is simulation result: {is_simulation_result}")

        return ModelOutput(numbers=numbers, strings=strings, is_simulation_result=is_simulation_result)

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
