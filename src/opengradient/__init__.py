from typing import Dict, List, Optional, Tuple

from .client import Client
from .defaults import DEFAULT_INFERENCE_CONTRACT_ADDRESS, DEFAULT_RPC_URL
from .types import InferenceMode, LlmInferenceMode, LLM, TEE_LLM
from . import llm

__version__ = "0.3.17"

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

def infer(model_cid, inference_mode, model_input, max_retries: Optional[int] = None):
    """
    Perform inference on a model.

    Args:
        model_cid: Model CID to use for inference
        inference_mode: Mode of inference (e.g. VANILLA)
        model_input: Input data for the model
        max_retries: Optional maximum number of retry attempts for transaction errors

    Returns:
        Tuple of (transaction hash, model output)
    """
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.infer(model_cid, inference_mode, model_input, max_retries=max_retries)

def llm_completion(model_cid: LLM, 
                  prompt: str, 
                  inference_mode: str = LlmInferenceMode.VANILLA,
                  max_tokens: int = 100, 
                  stop_sequence: Optional[List[str]] = None, 
                  temperature: float = 0.0,
                  max_retries: Optional[int] = None) -> Tuple[str, str]:
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.llm_completion(model_cid=model_cid, 
                                inference_mode=inference_mode, 
                                prompt=prompt,
                                max_tokens=max_tokens, 
                                stop_sequence=stop_sequence, 
                                temperature=temperature,
                                max_retries=max_retries)

def llm_chat(model_cid: LLM,
             messages: List[Dict],
             inference_mode: str = LlmInferenceMode.VANILLA,
             max_tokens: int = 100,
             stop_sequence: Optional[List[str]] = None,
             temperature: float = 0.0,
             tools: Optional[List[Dict]] = None,
             tool_choice: Optional[str] = None,
             max_retries: Optional[int] = None) -> Tuple[str, str, Dict]:
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.llm_chat(model_cid=model_cid, 
                          inference_mode=inference_mode, 
                          messages=messages, 
                          max_tokens=max_tokens, 
                          stop_sequence=stop_sequence, 
                          temperature=temperature, 
                          tools=tools, 
                          tool_choice=tool_choice,
                          max_retries=max_retries)

def login(email: str, password: str):
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.login(email, password)

def list_files(model_name: str, version: str) -> List[Dict]:
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.list_files(model_name, version)

def generate_image(model: str, prompt: str, height: Optional[int] = None, width: Optional[int] = None) -> bytes:
    """
    Generate an image using the specified model and prompt.

    Args:
        model (str): The model identifier (e.g. "stabilityai/stable-diffusion-xl-base-1.0")
        prompt (str): The text prompt to generate the image from
        height (Optional[int]): Height of the generated image. Default is None.
        width (Optional[int]): Width of the generated image. Default is None.

    Returns:
        bytes: The raw image data bytes

    Raises:
        RuntimeError: If the client is not initialized
        OpenGradientError: If the image generation fails
    """
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.generate_image(model, prompt, height=height, width=width)
