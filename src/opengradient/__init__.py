from .client import Client
from .defaults import *
from .types import InferenceMode

__version__ = "0.2.9"

_client = None

def init(private_key=DEFAULT_PRIVATE_KEY,
         rpc_url=DEFAULT_RPC_URL,
         contract_address=DEFAULT_INFERENCE_CONTRACT_ADDRESS,
         email=DEFAULT_HUB_EMAIL,
         password=DEFAULT_HUB_PASSWORD):
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

def login(email: str, password: str):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.login(email, password)