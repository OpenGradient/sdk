from src.client import Client
from src.exceptions import OpenGradientError, FileNotFoundError, UploadError, InferenceError, ResultRetrievalError
from src.types import ModelInput, InferenceMode, Number, NumberTensor, ModelOutput, StringTensor

__version__ = "0.1.0"

_client = None

def init(wallet_address, private_key):
    global _client
    _client = Client(wallet_address=wallet_address, private_key=private_key)

def upload(model_path):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.upload(model_path)

def infer(model_id, inference_mode, model_input):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.infer(model_id, inference_mode, model_input)

def sign_in_with_email_and_password(email: str, password: str):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.sign_in_with_email_and_password(email, password)