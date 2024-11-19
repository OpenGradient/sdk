import json
import logging
import os
from typing import Dict, List, Optional, Tuple, Union

import firebase
import numpy as np
import requests
from web3 import Web3
from web3.exceptions import ContractLogicError
from web3.logs import DISCARD

from opengradient import utils
from opengradient.exceptions import OpenGradientError
from opengradient.types import InferenceMode, LLM


class Client:
    FIREBASE_CONFIG = {
        "apiKey": "AIzaSyDUVckVtfl-hiteBzPopy1pDD8Uvfncs7w",
        "authDomain": "vanna-portal-418018.firebaseapp.com",
        "projectId": "vanna-portal-418018",
        "storageBucket": "vanna-portal-418018.appspot.com",
        "appId": "1:487761246229:web:259af6423a504d2316361c",
        "databaseURL": ""
    }
    
    def __init__(self, private_key: str, rpc_url: str, contract_address: str, email: str, password: str):
        """
        Initialize the Client with private key, RPC URL, and contract address.

        Args:
            private_key (str): The private key for the wallet.
            rpc_url (str): The RPC URL for the Ethereum node.
            contract_address (str): The contract address for the smart contract.
            email (str, optional): Email for authentication. Defaults to "test@test.com".
            password (str, optional): Password for authentication. Defaults to "Test-123".
        """
        self.email = email
        self.password = password
        self.private_key = private_key
        self.rpc_url = rpc_url
        self.contract_address = contract_address
        self._w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.wallet_account = self._w3.eth.account.from_key(private_key)
        self.wallet_address = self._w3.to_checksum_address(self.wallet_account.address)
        self.firebase_app = firebase.initialize_app(self.FIREBASE_CONFIG)
        self.auth = self.firebase_app.auth()
        self.user = None
        
        logging.debug("Initialized client with parameters:\n"
                      "private key: %s\n"
                      "RPC URL: %s\n"
                      "Contract Address: %s\n",
                      private_key, rpc_url, contract_address)

        abi_path = os.path.join(os.path.dirname(__file__), 'abi', 'inference.abi')
        with open(abi_path, 'r') as abi_file:
            inference_abi = json.load(abi_file)
        self.abi = inference_abi

        if email is not None:
            self.login(email, password)

    def login(self, email, password):
        try:
            self.user = self.auth.sign_in_with_email_and_password(email, password)
            return self.user
        except Exception as e:
            logging.error(f"Authentication failed: {str(e)}")
            raise

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

        url = "https://api.opengradient.ai/api/v0/models/"
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
                logging.info("Server returned an empty list. Assuming version was created successfully.")
                return {"versionString": "Unknown", "note": "Created based on empty response"}
            elif isinstance(json_response, dict):
                version_string = json_response.get('versionString')
                if not version_string:
                    logging.warning(f"'versionString' not found in response. Response: {json_response}")
                    return {"versionString": "Unknown", "note": "Version ID not provided in response"}
                logging.info(f"Version creation successful. Version ID: {version_string}")
                return {"versionString": version_string}
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
                logging.error(f"Response content: {e.response.text[:1000]}...")  # Log first 1000 characters
            raise OpenGradientError(f"Upload failed due to request exception: {str(e)}", 
                                    status_code=e.response.status_code if hasattr(e, 'response') else None)
        except Exception as e:
            logging.error(f"Unexpected error during upload: {str(e)}", exc_info=True)
            raise OpenGradientError(f"Unexpected error during upload: {str(e)}")
    
    def infer(
            self, 
            model_cid: str, 
            inference_mode: InferenceMode, 
            model_input: Dict[str, Union[str, int, float, List, np.ndarray]]
            ) -> Tuple[str, Dict[str, np.ndarray]]:
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
            parsed_logs = contract.events.InferenceResult().process_receipt(tx_receipt, errors=DISCARD)

            if len(parsed_logs) < 1:
                raise OpenGradientError("InferenceResult event not found in transaction logs")
            inference_result = parsed_logs[0]

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
        
    def llm_completion(self, 
                       model_cid: LLM, 
                       prompt: str, 
                       max_tokens: int = 100, 
                       stop_sequence: Optional[List[str]] = None, 
                       temperature: float = 0.0) -> Tuple[str, str]:
        """
        Perform inference on an LLM model using completions.

        Args:
            model_cid (LLM): The unique content identifier for the model.
            prompt (str): The input prompt for the LLM.
            max_tokens (int): Maximum number of tokens for LLM output. Default is 100.
            stop_sequence (List[str], optional): List of stop sequences for LLM. Default is None.
            temperature (float): Temperature for LLM inference, between 0 and 1. Default is 0.0.

        Returns:
            Tuple[str, str]: The transaction hash and the LLM completion output.

        Raises:
            OpenGradientError: If the inference fails.
        """
        try:
            self._initialize_web3()
            
            abi_path = os.path.join(os.path.dirname(__file__), 'abi', 'inference.abi')
            with open(abi_path, 'r') as abi_file:
                llm_abi = json.load(abi_file)
            contract = self._w3.eth.contract(address=self.contract_address, abi=llm_abi)

            # Prepare LLM input
            llm_request = {
                "mode": InferenceMode.VANILLA,
                "modelCID": model_cid,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "stop_sequence": stop_sequence or [],
                "temperature": int(temperature * 100)  # Scale to 0-100 range
            }
            logging.debug(f"Prepared LLM request: {llm_request}")

            # Prepare run function
            run_function = contract.functions.runLLMCompletion(llm_request)

            # Build transaction
            nonce = self._w3.eth.get_transaction_count(self.wallet_address)
            estimated_gas = run_function.estimate_gas({'from': self.wallet_address})
            gas_limit = int(estimated_gas * 1.2)

            transaction = run_function.build_transaction({
                'from': self.wallet_address,
                'nonce': nonce,
                'gas': gas_limit,
                'gasPrice': self._w3.eth.gas_price,
            })

            # Sign and send transaction
            signed_tx = self._w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self._w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            logging.debug(f"Transaction sent. Hash: {tx_hash.hex()}")

            # Wait for transaction receipt
            tx_receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash)

            if tx_receipt['status'] == 0:
                raise ContractLogicError(f"Transaction failed. Receipt: {tx_receipt}")

            # Process the LLMResult event
            parsed_logs = contract.events.LLMCompletionResult().process_receipt(tx_receipt, errors=DISCARD)

            if len(parsed_logs) < 1:
                raise OpenGradientError("LLM completion result event not found in transaction logs")
            llm_result = parsed_logs[0]

            llm_answer = llm_result['args']['response']['answer']
            return tx_hash.hex(), llm_answer

        except ContractLogicError as e:
            logging.error(f"Contract logic error: {str(e)}", exc_info=True)
            raise OpenGradientError(f"LLM inference failed due to contract logic error: {str(e)}")
        except Exception as e:
            logging.error(f"Error in infer completion method: {str(e)}", exc_info=True)
            raise OpenGradientError(f"LLM inference failed: {str(e)}")
        
    def llm_chat(self,
                 model_cid: str,
                 messages: List[Dict],
                 max_tokens: int = 100,
                 stop_sequence: Optional[List[str]] = None,
                 temperature: float = 0.0,
                 tools: Optional[List[Dict]] = [],
                 tool_choice: Optional[str] = None) -> Tuple[str, str]:
        """
        Perform inference on an LLM model using chat.

        Args:
            model_cid (LLM): The unique content identifier for the model.
            messages (dict): The messages that will be passed into the chat. 
                This should be in OpenAI API format (https://platform.openai.com/docs/api-reference/chat/create)
                Example:
                [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant."
                    },
                    {
                        "role": "user",
                        "content": "Hello!"
                    }
                ]
            max_tokens (int): Maximum number of tokens for LLM output. Default is 100.
            stop_sequence (List[str], optional): List of stop sequences for LLM. Default is None.
            temperature (float): Temperature for LLM inference, between 0 and 1. Default is 0.0.
            tools (List[dict], optional): Set of tools
                This should be in OpenAI API format (https://platform.openai.com/docs/api-reference/chat/create#chat-create-tools)
                Example:
                [
                    {
                        "type": "function",
                        "function": {
                            "name": "get_current_weather",
                            "description": "Get the current weather in a given location",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "The city and state, e.g. San Francisco, CA"
                                    },
                                    "unit": {
                                        "type": "string",
                                        "enum": ["celsius", "fahrenheit"]
                                    }
                                },
                                "required": ["location"]
                            }
                        }
                    }
                ]
            tool_choice (str, optional): Sets a specific tool to choose. Default value is "auto". 

        Returns:
            Tuple[str, str, dict]: The transaction hash, finish reason, and a dictionary struct of LLM chat messages.

        Raises:
            OpenGradientError: If the inference fails.
        """
        try:
            self._initialize_web3()
            
            abi_path = os.path.join(os.path.dirname(__file__), 'abi', 'inference.abi')
            with open(abi_path, 'r') as abi_file:
                llm_abi = json.load(abi_file)
            contract = self._w3.eth.contract(address=self.contract_address, abi=llm_abi)

            # For incoming chat messages, tool_calls can be empty. Add an empty array so that it will fit the ABI.
            for message in messages:
                if 'tool_calls' not in message:
                    message['tool_calls'] = []
                if 'tool_call_id' not in message:
                    message['tool_call_id'] = ""
                if 'name' not in message:
                    message['name'] = ""

            # Create simplified tool structure for smart contract
            #
            #   struct ToolDefinition {
            #       string description;
            #       string name;
            #       string parameters; // This must be a JSON 
            #   }
            converted_tools = []
            if tools is not None:
                for tool in tools:
                    function = tool['function']

                    converted_tool = {}
                    converted_tool['name'] = function['name']
                    converted_tool['description'] = function['description']
                    if (parameters := function.get('parameters')) is not None:
                        try:
                            converted_tool['parameters'] = json.dumps(parameters)
                        except Exception as e:
                            raise OpenGradientError("Chat LLM failed to convert parameters into JSON: %s", e)
                    
                    converted_tools.append(converted_tool)

            # Prepare LLM input
            llm_request = {
                "mode": InferenceMode.VANILLA,
                "modelCID": model_cid,
                "messages": messages,
                "max_tokens": max_tokens,
                "stop_sequence": stop_sequence or [],
                "temperature": int(temperature * 100),  # Scale to 0-100 range
                "tools": converted_tools or [],
                "tool_choice": tool_choice if tool_choice else ("" if tools is None else "auto")
            }
            logging.debug(f"Prepared LLM request: {llm_request}")

            # Prepare run function
            run_function = contract.functions.runLLMChat(llm_request)

            # Build transaction
            nonce = self._w3.eth.get_transaction_count(self.wallet_address)
            estimated_gas = run_function.estimate_gas({'from': self.wallet_address})
            gas_limit = int(estimated_gas * 1.2)

            transaction = run_function.build_transaction({
                'from': self.wallet_address,
                'nonce': nonce,
                'gas': gas_limit,
                'gasPrice': self._w3.eth.gas_price,
            })

            # Sign and send transaction
            signed_tx = self._w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self._w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            logging.debug(f"Transaction sent. Hash: {tx_hash.hex()}")

            # Wait for transaction receipt
            tx_receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash)

            if tx_receipt['status'] == 0:
                raise ContractLogicError(f"Transaction failed. Receipt: {tx_receipt}")

            # Process the LLMResult event
            parsed_logs = contract.events.LLMChatResult().process_receipt(tx_receipt, errors=DISCARD)

            if len(parsed_logs) < 1:
                raise OpenGradientError("LLM chat result event not found in transaction logs")
            llm_result = parsed_logs[0]['args']['response']

            # Turn tool calls into normal dicts
            message = dict(llm_result['message'])
            if (tool_calls := message.get('tool_calls')) != None:
                new_tool_calls = []
                for tool_call in tool_calls:
                    new_tool_calls.append(dict(tool_call))
                message['tool_calls'] = new_tool_calls

            return (tx_hash.hex(), llm_result['finish_reason'], message)

        except ContractLogicError as e:
            logging.error(f"Contract logic error: {str(e)}", exc_info=True)
            raise OpenGradientError(f"LLM inference failed due to contract logic error: {str(e)}")
        except Exception as e:
            logging.error(f"Error in infer chat method: {str(e)}", exc_info=True)
            raise OpenGradientError(f"LLM inference failed: {str(e)}")


    def list_files(self, model_name: str, version: str) -> List[Dict]:
        """
        List files for a specific version of a model.

        Args:
            model_name (str): The unique identifier for the model.
            version (str): The version identifier for the model.

        Returns:
            List[Dict]: A list of dictionaries containing file information.

        Raises:
            OpenGradientError: If the file listing fails.
        """
        if not self.user:
            raise ValueError("User not authenticated")

        url = f"https://api.opengradient.ai/api/v0/models/{model_name}/versions/{version}/files"
        headers = {
            'Authorization': f'Bearer {self.user["idToken"]}'
        }

        logging.debug(f"List Files URL: {url}")
        logging.debug(f"Headers: {headers}")

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            json_response = response.json()
            logging.info(f"File listing successful. Number of files: {len(json_response)}")
            
            return json_response

        except requests.RequestException as e:
            logging.error(f"File listing failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Response status code: {e.response.status_code}")
                logging.error(f"Response content: {e.response.text[:1000]}...")  # Log first 1000 characters
            raise OpenGradientError(f"File listing failed: {str(e)}", 
                                    status_code=e.response.status_code if hasattr(e, 'response') else None)
        except Exception as e:
            logging.error(f"Unexpected error during file listing: {str(e)}", exc_info=True)
            raise OpenGradientError(f"Unexpected error during file listing: {str(e)}")

    def generate_image(
            self,
            model_cid: str,
            prompt: str,
            num_inference_steps: int = 50,
            guidance_scale: float = 7.5,
            negative_prompt: Optional[str] = None,
            width: int = 1024,
            height: int = 1024,
            seed: Optional[int] = None
        ) -> bytes:
        """
        Generate an image using a diffusion model.

        Args:
            model_cid (str): The model identifier (e.g. "stabilityai/stable-diffusion-xl-base-1.0")
            prompt (str): The text prompt to generate the image from
            num_inference_steps (int, optional): Number of denoising steps. Defaults to 50.
            guidance_scale (float, optional): Scale for classifier-free guidance. Defaults to 7.5.
            negative_prompt (str, optional): The prompt to not generate. Defaults to None.
            width (int, optional): Output image width. Defaults to 1024.
            height (int, optional): Output image height. Defaults to 1024.
            seed (int, optional): Random seed for reproducibility. Defaults to None.

        Returns:
            bytes: The raw image data bytes

        Raises:
            OpenGradientError: If the image generation fails
        """
        try:
            url = "https://api.opengradient.ai/api/v0/inference/image"
            
            headers = {
                'Content-Type': 'application/json'
            }
            if self.user:
                headers['Authorization'] = f'Bearer {self.user["idToken"]}'

            # Prepare request payload
            payload = {
                "model": model_cid,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "width": width,
                "height": height,
                "seed": seed or random.randint(0, 2**32 - 1)
            }

            logging.debug(f"Sending image generation request to {url}")
            logging.debug(f"Request payload: {payload}")

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            if response.headers.get('content-type') == 'application/json':
                # Handle error response
                error_data = response.json()
                raise OpenGradientError(f"Image generation failed: {error_data.get('detail', 'Unknown error')}")

            # Expect raw image bytes
            return response.content

        except requests.RequestException as e:
            logging.error(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Response status code: {e.response.status_code}")
                logging.error(f"Response content: {e.response.text[:1000]}...")
            raise OpenGradientError(f"Image generation failed: {str(e)}")
        except Exception as e:
            logging.error(f"Error in generate image method: {str(e)}", exc_info=True)
            raise OpenGradientError(f"Image generation failed: {str(e)}")