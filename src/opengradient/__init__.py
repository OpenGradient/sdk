import os
from .client import Client
from .defaults import *
from .types import InferenceMode
from typing import List, Dict, Optional, Tuple
from huggingface_hub import snapshot_download, HfApi
import tempfile
import io
import shutil
from .exceptions import OpenGradientError
import time
from requests.exceptions import RequestException, SSLError

__version__ = "0.4.0"
__all__ = ['init', 'upload', 'create_model', 'create_version', 'infer', 'infer_llm', 'login', 'list_files', 'InferenceMode', 'create_model_from_huggingface']

_client = None

def init(email: str,
         password: str,
         private_key: str,
         rpc_url=DEFAULT_RPC_URL,
         contract_address=DEFAULT_INFERENCE_CONTRACT_ADDRESS):
    global _client
    _client = Client(private_key=private_key, rpc_url=rpc_url, contract_address=contract_address, email=email, password=password)

def upload(model_path, model_name, version):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.upload(model_path, model_name, version)

def create_model(model_name: str, model_desc: str, model_path: str = None):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    
    result = _client.create_model(model_name, model_desc)
    
    if model_path:
        version = "0.01"
        upload_result = _client.upload(model_path, model_name, version)
        result["upload"] = upload_result
    
    return result

def create_version(model_name, notes=None, is_major=False):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.create_version(model_name, notes, is_major)

def infer(model_cid, inference_mode, model_input):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.infer(model_cid, inference_mode, model_input)

def infer_llm(model_cid: str, 
              prompt: str, 
              max_tokens: int = 100, 
              stop_sequence: Optional[List[str]] = None, 
              temperature: float = 0.0) -> Tuple[str, str]:
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.infer_llm(model_cid, prompt, max_tokens, stop_sequence, temperature)

def login(email: str, password: str):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.login(email, password)

def list_files(model_name: str, version: str) -> List[Dict]:
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.list_files(model_name, version)

def create_model_from_huggingface(repo_id: str, model_name: str, model_desc: str, max_retries=3, retry_delay=5):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")

    temp_dir = os.path.join(os.getcwd(), "opengradient_temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    try:
        try:
            model_result = _client.create_model(model_name, model_desc)
        except OpenGradientError as e:
            if e.status_code == 409:
                print(f"Model '{model_name}' already exists. Using existing model.")
                model_result = {"name": model_name, "versionString": "1.00"}
            else:
                raise

        version = model_result['versionString']
        download_dir = os.path.join(temp_dir, f"{model_name}_{version}")
        os.makedirs(download_dir, exist_ok=True)

        try:
            snapshot_download(repo_id, local_dir=download_dir)

            for root, _, files in os.walk(download_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, download_dir)
                    
                    for attempt in range(max_retries):
                        try:
                            upload_result = _client.upload(file_path, model_name, version)
                            print(f"Uploaded {relative_path}: {upload_result}")
                            break
                        except (OpenGradientError, RequestException, SSLError) as e:
                            if attempt < max_retries - 1:
                                print(f"Attempt {attempt + 1} failed to upload {relative_path}: {str(e)}")
                                time.sleep(retry_delay)
                            else:
                                print(f"Failed to upload {relative_path} after {max_retries} attempts: {str(e)}")

        finally:
            shutil.rmtree(download_dir, ignore_errors=True)

        return model_result
    except Exception as e:
        print(f"Error in create_model_from_huggingface: {str(e)}")
        raise
    finally:
        try:
            os.rmdir(temp_dir)
        except OSError:
            pass
