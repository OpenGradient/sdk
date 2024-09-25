from .client import Client
from .exceptions import OpenGradientError, FileNotFoundError, UploadError, InferenceError, ResultRetrievalError
from .types import ModelInput, InferenceMode, Number, NumberTensor, StringTensor, ModelOutput

__version__ = "0.1.9"

_client = None

def init(private_key, rpc_url, contract_address, email="test@test.com", password="Test123"):
    global _client
    _client = Client(private_key=private_key, rpc_url=rpc_url, contract_address=contract_address, email=email, password=password)

def upload(model_path, model_id, version_id):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.upload(model_path, model_id, version_id)

def create_model(model_name, model_desc):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.create_model(model_name,model_desc)

def create_version(model_id, notes=None, is_major=False):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.create_version(model_id, notes, is_major)

def infer(model_id, inference_mode, model_input):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.infer(model_id, inference_mode, model_input)

def sign_in_with_email_and_password(email: str, password: str):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.sign_in_with_email_and_password(email, password)