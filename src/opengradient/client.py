import requests
import os
import json
from web3 import Web3
from opengradient.exceptions import OpenGradientError
from opengradient.types import InferenceMode
from opengradient import utils
import numpy as np
import logging
from typing import Dict, Tuple, Union, List
from web3.exceptions import ContractLogicError
import firebase

logging.basicConfig(level=logging.INFO)

class Client:
    FIREBASE_CONFIG = {
        "apiKey": "AIzaSyDUVckVtfl-hiteBzPopy1pDD8Uvfncs7w",
        "authDomain": "vanna-portal-418018.firebaseapp.com",
        "projectId": "vanna-portal-418018",
        "storageBucket": "vanna-portal-418018.appspot.com",
        "appId": "1:487761246229:web:259af6423a504d2316361c",
        "databaseURL": ""
    }
    
    def __init__(self, private_key: str, rpc_url: str, contract_address: str, email: str = "test@test.com", password: str = "Test-123"):
        """
        Initialize the Client with private key, RPC URL, and contract address.

        Args:
            private_key (str): The private key for the wallet.
            rpc_url (str): The RPC URL for the Ethereum node.
            contract_address (str): The contract address for the smart contract.
            email (str, optional): Email for authentication. Defaults to "test@test.com".
            password (str, optional): Password for authentication. Defaults to "Test-123".
        """
        self.private_key = private_key
        self.rpc_url = rpc_url
        self.contract_address = contract_address
        self._w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.wallet_account = self._w3.eth.account.from_key(private_key)
        self.wallet_address = self._w3.to_checksum_address(self.wallet_account.address)
        self.firebase_app = firebase.initialize_app(self.FIREBASE_CONFIG)
        self.auth = self.firebase_app.auth()
        self.user = None

        abi_path = os.path.join(os.path.dirname(__file__), 'abi', 'inference.abi')
        with open(abi_path, 'r') as abi_file:
            inference_abi = json.load(abi_file)
        self.abi = inference_abi

        self.login(email, password)

    def _initialize_web3(self):
        """
        Initialize the Web3 instance if it is not already initialized.
        """
        if self._w3 is None:
            self._w3 = Web3(Web3.HTTPProvider(self.rpc_url))

    def refresh_token(self) -> None:
        """
        Refresh the authentication token for the current user.
        """
        if self.user:
            self.user = self.auth.refresh(self.user['refreshToken'])
        else:
            logging.error("No user is currently signed in")

    def create_model(self, model_name: str, model_desc: str, version: str = "1.00") -> dict:
        """
        Create a new model with the given model_name and model_desc, and a specified version.

        Args:
            model_name (str): The name of the model.
            model_desc (str): The description of the model.
            version (str): The version identifier (default is "1.00").

        Returns:
            dict: The server response containing model details.

        Raises:
            CreateModelError: If the model creation fails.
        """
        if not self.user:
            raise ValueError("User not authenticated")

        url = f"https://api.opengradient.ai/api/v0/models/"
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
            model_name = json_response.get('name')
            if not model_name:
                raise Exception(f"Model creation response missing 'name'. Full response: {json_response}")
            logging.info(f"Model creation successful. Model name: {model_name}")

            # Create the specified version for the newly created model
            try:
                version_response = self.create_version(model_name, version)
                logging.info(f"Version creation successful. Version string: {version_response['versionString']}")
            except Exception as ve:
                logging.error(f"Version creation failed, but model was created. Error: {str(ve)}")
                return {"name": model_name, "versionString": None, "version_error": str(ve)}

            return {"name": model_name, "versionString": version_response["versionString"]}

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

    def create_version(self, model_name: str, notes: str = None, is_major: bool = False) -> dict:
        """
        Create a new version for the specified model.

        Args:
            model_name (str): The unique identifier for the model.
            notes (str, optional): Notes for the new version.
            is_major (bool, optional): Whether this is a major version update. Defaults to False.

        Returns:
            dict: The server response containing version details.

        Raises:
            Exception: If the version creation fails.
        """
        if not self.user:
            raise ValueError("User not authenticated")

        url = f"https://api.opengradient.ai/api/v0/models/{model_name}/versions"
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
                return {"versionString": "Unknown", "note": "Created based on empty response"}
            elif isinstance(json_response, dict):
                versionString = json_response.get('versionString')
                if not versionString:
                    logging.warning(f"'versionString' not found in response. Response: {json_response}")
                    return {"versionString": "Unknown", "note": "Version ID not provided in response"}
                logging.info(f"Version creation successful. Version ID: {versionString}")
                return {"versionString": versionString}
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

    def upload(self, model_path: str, model_name: str, version: str) -> dict:
        """
        Upload a model file to the server.

        Args:
            model_path (str): The path to the model file.
            model_name (str): The unique identifier for the model.
            version (str): The version identifier for the model.

        Returns:
            dict: The processed result.

        Raises:
            OpenGradientError: If the upload fails.
        """
        from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

        if not self.user:
            raise ValueError("User not authenticated")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        url = f"https://api.opengradient.ai/api/v0/models/{model_name}/versions/{version}/files"
        headers = {
            'Authorization': f'Bearer {self.user["idToken"]}'
        }

        logging.info(f"Starting upload for file: {model_path}")
        logging.info(f"File size: {os.path.getsize(model_path)} bytes")
        logging.debug(f"Upload URL: {url}")
        logging.debug(f"Headers: {headers}")

        def create_callback(encoder):
            encoder_len = encoder.len
            def callback(monitor):
                progress = (monitor.bytes_read / encoder_len) * 100
                logging.info(f"Upload progress: {progress:.2f}%")
            return callback

        try:
            with open(model_path, 'rb') as file:
                encoder = MultipartEncoder(
                    fields={'file': (os.path.basename(model_path), file, 'application/octet-stream')}
                )
                monitor = MultipartEncoderMonitor(encoder, create_callback(encoder))
                headers['Content-Type'] = monitor.content_type

                logging.info("Sending POST request...")
                response = requests.post(url, data=monitor, headers=headers, timeout=3600)  # 1 hour timeout
                
                logging.info(f"Response received. Status code: {response.status_code}")
                logging.info(f"Full response content: {response.text}")  # Log the full response content

                if response.status_code == 201:
                    if response.content and response.content != b'null':
                        json_response = response.json()
                        logging.info(f"JSON response: {json_response}")  # Log the parsed JSON response
                        logging.info(f"Upload successful. CID: {json_response.get('ipfsCid', 'N/A')}")
                        result = {"model_cid": json_response.get("ipfsCid"), "size": json_response.get("size")}
                    else:
                        logging.warning("Empty or null response content received. Assuming upload was successful.")
                        result = {"model_cid": None, "size": None}
                elif response.status_code == 500:
                    error_message = "Internal server error occurred. Please try again later or contact support."
                    logging.error(error_message)
                    raise OpenGradientError(error_message, status_code=500)
                else:
                    error_message = response.json().get('detail', 'Unknown error occurred')
                    logging.error(f"Upload failed with status code {response.status_code}: {error_message}")
                    raise OpenGradientError(f"Upload failed: {error_message}", status_code=response.status_code)

                return result

        except requests.RequestException as e:
            logging.error(f"Request exception during upload: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Response status code: {e.response.status_code}")
                logging.error(f"Response headers: {e.response.headers}")
                logging.error(f"Response content: {e.response.text[:1000]}...")  # Log first 1000 characters
            raise OpenGradientError(f"Upload failed due to request exception: {str(e)}", 
                                    status_code=e.response.status_code if hasattr(e, 'response') else None)
        except Exception as e:
            logging.error(f"Unexpected error during upload: {str(e)}", exc_info=True)
            raise OpenGradientError(f"Unexpected error during upload: {str(e)}")
    
    def infer(self, model_cid: str, inference_mode: InferenceMode, model_input: Dict[str, Union[str, int, float, List, np.ndarray]]) -> Tuple[str, Dict[str, np.ndarray]]:
        """
        Perform inference on a model.

        Args:
            model_cid (str): The unique content identifier for the model from IPFS.
            inference_mode (InferenceMode): The inference mode.
            model_input (Dict[str, Union[str, int, float, List, np.ndarray]]): The input data for the model.

        Returns:
            Tuple[str, Dict[str, np.ndarray]]: The transaction hash and the model output.

        Raises:
            OpenGradientError: If the inference fails.
        """
        try:
            logging.debug("Entering infer method")
            self._initialize_web3()
            logging.debug(f"Web3 initialized. Connected: {self._w3.is_connected()}")

            logging.debug(f"Creating contract instance. Address: {self.contract_address}")
            contract = self._w3.eth.contract(address=self.contract_address, abi=self.abi)
            logging.debug("Contract instance created successfully")

            logging.debug(f"Model ID: {model_cid}")
            logging.debug(f"Inference Mode: {inference_mode}")
            logging.debug(f"Model Input: {model_input}")

            # Convert InferenceMode to uint8
            inference_mode_uint8 = int(inference_mode)

            # Prepare ModelInput tuple
            converted_model_input = utils.convert_to_model_input(model_input)
            logging.debug(f"Prepared model input tuple: {converted_model_input}")

            logging.debug("Preparing run function")
            run_function = contract.functions.run(
                model_cid,
                inference_mode_uint8,
                converted_model_input
            )
            logging.debug("Run function prepared successfully")

            # Build transaction
            nonce = self._w3.eth.get_transaction_count(self.wallet_address)
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
                'gasPrice': self._w3.eth.gas_price,
            })

            logging.debug(f"Transaction built: {transaction}")

            # Sign transaction
            signed_tx = self._w3.eth.account.sign_transaction(transaction, self.private_key)
            logging.debug("Transaction signed successfully")

            # Send transaction
            tx_hash = self._w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            logging.debug(f"Transaction sent. Hash: {tx_hash.hex()}")

            # Wait for transaction receipt
            tx_receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash)
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
                raise OpenGradientError("InferenceResult event not found in transaction logs")

            # Extract the ModelOutput from the event
            event_data = inference_result['args']
            logging.debug(f"Raw event data: {event_data}")

            try:
                model_output = utils.convert_to_model_output(event_data)
                logging.debug(f"Parsed ModelOutput: {model_output}")
            except Exception as e:
                logging.error(f"Error parsing event data: {str(e)}", exc_info=True)
                raise OpenGradientError(f"Failed to parse event data: {str(e)}")

            return tx_hash.hex(), model_output

        except ContractLogicError as e:
            logging.error(f"Contract logic error: {str(e)}", exc_info=True)
            raise OpenGradientError(f"Inference failed due to contract logic error: {str(e)}")
        except Exception as e:
            logging.error(f"Error in infer method: {str(e)}", exc_info=True)
            raise OpenGradientError(f"Inference failed: {str(e)}")
        
    def login(self, email, password):
        try:
            self.user = self.auth.sign_in_with_email_and_password(email, password)
            return self.user
        except Exception as e:
            logging.error(f"Authentication failed: {str(e)}")
            raise