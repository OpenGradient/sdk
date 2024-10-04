from .client import Client
from .exceptions import OpenGradientError, FileNotFoundError, UploadError, InferenceError, ResultRetrievalError
from .types import ModelInput, InferenceMode, Number, NumberTensor, StringTensor, ModelOutput

__version__ = "0.2.7"

_client = None

def init(private_key="cd09980ef6e280afc3900d2d6801f9e9c5d858a5deaeeab74a65643f5ff1a4c1",
         rpc_url="http://18.218.115.248:8545",
         contract_address="0x350E0A430b2B1563481833a99523Cfd17a530e4e",
         email="test@test.com",
         password="Test-123"):
    global _client
    _client = Client(private_key=private_key, rpc_url=rpc_url, contract_address=contract_address, email=email, password=password)

def upload(model_path, model_name, version):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.upload(model_path, model_name, version)

def create_model(model_name, model_desc):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.create_model(model_name, model_desc)

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