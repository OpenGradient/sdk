import requests
import os
import time
import json
from src.exceptions import OpenGradientError
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
from typing import Tuple
from web3.exceptions import ContractLogicError
from web3.datastructures import AttributeDict
import firebase

logging.basicConfig(level=logging.DEBUG)

class Client:
    FIREBASE_CONFIG = {
        "apiKey": "AIzaSyDUVckVtfl-hiteBzPopy1pDD8Uvfncs7w",
        "authDomain": "vanna-portal-418018.firebaseapp.com",
        "projectId": "vanna-portal-418018",
        "storageBucket": "vanna-portal-418018.appspot.com",
        "appId": "1:487761246229:web:259af6423a504d2316361c",
        "databaseURL": ""
    }

    def __init__(self, wallet_address, private_key):
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.rpc_url = "http://18.218.115.248:8545"
        self._w3 = None
        self.contract_address = "0x8383C9bD7462F12Eb996DD02F78234C0421A6FaE"
        self.storage_url = "http://18.222.64.142:5000"
        self.firebase_app = firebase.initialize_app(self.FIREBASE_CONFIG)
        self.auth = self.firebase_app.auth()
        self.user = None

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

    def sign_in_with_email_and_password(self, email, password):
        try:
            self.user = self.auth.sign_in_with_email_and_password(email, password)
            return self.user
        except Exception as e:
            logging.error(f"Authentication failed: {str(e)}")
            raise

    def refresh_token(self):
        if self.user:
            self.user = self.auth.refresh(self.user['refreshToken'])
        else:
            logging.error("No user is currently signed in")
    
    def create_model(self, model_name: str, model_desc: str, version_id: str = "1.00") -> dict:
        """
        Create a new model with the given model_name and model_desc, and a specified version ID.

        Args:
            model_name (str): The name of the model.
            model_desc (str): The description of the model.
            version_id (str): The version identifier (default is "1.00").

        Returns:
            dict: The server response containing model details.

        Raises:
            CreateModelError: If the model creation fails.
        """
        if not self.user:
            raise ValueError("User not authenticated")

        url = f"https://api.opengradient.ai/api/v1/models/"
        headers = {
            'Authorization': f'Bearer {self.user["idToken"]}',
            'Content-Type': 'application/json'
        }
        payload = {
            'name': model_name,
            'description': model_desc
        }

        try:
            logging.debug(f"Create Model URL: {url}")
            logging.debug(f"Headers: {headers}")
            logging.debug(f"Payload: {payload}")

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            json_response = response.json()
            model_id = json_response.get('id')
            if not model_id:
                raise Exception(f"Model creation response missing 'id'. Full response: {json_response}")
            logging.info(f"Model creation successful. Model ID: {model_id}")

            # Create the specified version for the newly created model
            try:
                version_response = self.create_version(model_id, version_id)
                logging.info(f"Version creation successful. Version ID: {version_response['version_id']}")
            except Exception as ve:
                logging.error(f"Version creation failed, but model was created. Error: {str(ve)}")
                return {"id": model_id, "version_id": None, "version_error": str(ve)}

            return {"id": model_id, "version_id": version_response["version_id"]}

        except requests.RequestException as e:
            logging.error(f"Model creation failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Response status code: {e.response.status_code}")
                logging.error(f"Response headers: {e.response.headers}")
                logging.error(f"Response content: {e.response.text}")
            raise Exception(f"Model creation failed: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error during model creation: {str(e)}")
            raise

    def create_version(self, model_id: str, notes: str = None, is_major: bool = False) -> dict:
        """
        Create a new version for the specified model.

        Args:
            model_id (str): The unique identifier for the model.
            notes (str, optional): Notes for the new version.
            is_major (bool, optional): Whether this is a major version update. Defaults to False.

        Returns:
            dict: The server response containing version details.

        Raises:
            Exception: If the version creation fails.
        """
        if not self.user:
            raise ValueError("User not authenticated")

        url = f"https://api.opengradient.ai/api/v1/models/{model_id}/versions"
        headers = {
            'Authorization': f'Bearer {self.user["idToken"]}',
            'Content-Type': 'application/json'
        }
        payload = {
            "notes": notes,
            "is_major": is_major
        }

        try:
            logging.debug(f"Create Version URL: {url}")
            logging.debug(f"Headers: {headers}")
            logging.debug(f"Payload: {payload}")

            response = requests.post(url, json=payload, headers=headers, allow_redirects=True)
            response.raise_for_status()

            json_response = response.json()

            logging.debug(f"Full server response: {json_response}")

            if isinstance(json_response, list) and not json_response:
                logging.info(f"Server returned an empty list. Assuming version was created successfully.")
                return {"version_id": "Unknown", "note": "Created based on empty response"}
            elif isinstance(json_response, dict):
                version_id = json_response.get('version_id') or json_response.get('id')
                if not version_id:
                    logging.warning(f"'version_id' not found in response. Response: {json_response}")
                    return {"version_id": "Unknown", "note": "Version ID not provided in response"}
                logging.info(f"Version creation successful. Version ID: {version_id}")
                return {"version_id": version_id}
            else:
                logging.error(f"Unexpected response type: {type(json_response)}. Content: {json_response}")
                raise Exception(f"Unexpected response type: {type(json_response)}")

        except requests.RequestException as e:
            logging.error(f"Version creation failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Response status code: {e.response.status_code}")
                logging.error(f"Response headers: {e.response.headers}")
                logging.error(f"Response content: {e.response.text}")
            raise Exception(f"Version creation failed: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error during version creation: {str(e)}")
            raise

    def upload(self, model_path: str, model_id: str, version_id: str) -> dict:
        if not self.user:
            raise ValueError("User not authenticated")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        url = f"https://api.opengradient.ai/api/v1/models/{model_id}/versions/{version_id}/files"
        headers = {
            'Authorization': f'Bearer {self.user["idToken"]}'
        }

        try:
            with open(model_path, 'rb') as file:
                files = {'file': (os.path.basename(model_path), file)}
                logging.info(f"Uploading file: {model_path}")
                logging.debug(f"Upload URL: {url}")
                logging.debug(f"Headers: {headers}")

                response = requests.post(url, files=files, headers=headers)
                
                logging.debug(f"Response status code: {response.status_code}")
                logging.debug(f"Response headers: {response.headers}")
                logging.debug(f"Response content: {response.text}")

                if response.status_code == 201:
                    if response.content and response.content != b'null':
                        json_response = response.json()
                        logging.info(f"Upload successful. CID: {json_response.get('cid', 'N/A')}")
                        return {"model_cid": json_response.get("ipfs_cid"), "size": json_response.get("size")}
                    else:
                        logging.warning("Empty or null response content received. Assuming upload was successful.")
                        return {"model_cid": None, "size": None}
                elif response.status_code == 500:
                    error_message = "Internal server error occurred. Please try again later or contact support."
                    logging.error(error_message)
                    raise OpenGradientError(error_message, status_code=500)
                else:
                    error_message = response.json().get('detail', 'Unknown error occurred')
                    raise OpenGradientError(f"Upload failed: {error_message}", status_code=response.status_code)

        except requests.RequestException as e:
            logging.error(f"Upload failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Response status code: {e.response.status_code}")
                logging.error(f"Response headers: {e.response.headers}")
                logging.error(f"Response content: {e.response.text}")
            raise OpenGradientError(f"Upload failed: {str(e)}", status_code=e.response.status_code if hasattr(e, 'response') else None)
        except Exception as e:
            logging.error(f"Unexpected error during upload: {str(e)}")
            raise OpenGradientError(f"Unexpected error during upload: {str(e)}")
    
    def infer(self, model_id: str, inference_mode: InferenceMode, model_input: ModelInput) -> Tuple[str, ModelOutput]:
        if not self.user:
            raise ValueError("User not authenticated")

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

            # Prepare ModelInput struct
            number_tensors = [(tensor.name, [(number.value, number.decimals) for number in tensor.values]) for tensor in model_input.numbers]
            string_tensors = [(tensor.name, tensor.values) for tensor in model_input.strings]

            model_input_struct = (number_tensors, string_tensors)

            logging.debug(f"Prepared model input struct: {model_input_struct}")

            logging.debug("Preparing run function")
            run_function = contract.functions.run(
                model_id,
                inference_mode_uint8,
                model_input_struct
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