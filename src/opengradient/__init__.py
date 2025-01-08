from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
from .client import Client
from .defaults import DEFAULT_RPC_URL
from .types import LlmInferenceMode, LLM

__version__ = "0.3.18"

_client = None

def init(
    email: str,
    password: str, 
    private_key: str,
    rpc_url: str = DEFAULT_RPC_URL
) -> None:
    """Initialize the OpenGradient SDK with authentication and network settings.

    Args:
        email: User's email address for authentication
        password: User's password for authentication
        private_key: Ethereum private key for blockchain transactions
        rpc_url: Optional RPC URL for the blockchain network, defaults to mainnet
    """
    global _client
    
    # Just use abi directory relative to current file
    abi_path = Path(__file__).parent / 'abi' / 'inference.abi'
    
    if not abi_path.exists():
        raise FileNotFoundError(f"Inference ABI not found at {abi_path}")
    
    _client = Client(
        private_key=private_key,
        rpc_url=rpc_url,
        email=email,
        password=password
    )
    return _client

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

def new_workflow(
    model_cid: str,
    input_query: Dict[str, Any],
    input_tensor_name: str
) -> str:
    """
    Deploy a new workflow contract with the specified parameters.
    
    Args:
        model_cid: IPFS CID of the model
        input_query: Dictionary containing query parameters
        input_tensor_name: Name of the input tensor
    
    Returns:
        str: Deployed contract address
    """
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init(...) first.")
    return _client.new_workflow(model_cid, input_query, input_tensor_name)

def read_workflow_result(contract_address: str) -> Dict[str, Union[str, Dict]]:
    """
    Reads the latest inference result from a deployed workflow contract.
    
    This function retrieves the most recent output from a deployed model executor contract.
    It includes built-in retry logic to handle blockchain state delays.
    
    Args:
        contract_address (str): Address of the deployed workflow contract
            
    Returns:
        Dict[str, Union[str, Dict]]: A dictionary containing:
            - status: "success" or "error"
            - result: The model output data if successful
            - error: Error message if status is "error"
            
    Raises:
        RuntimeError: If OpenGradient client is not initialized
    """
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.read_workflow(contract_address)

def run_workflow(contract_address: str) -> Dict[str, Union[str, Dict]]:
    """
    Executes the workflow by calling run() on the contract to pull latest data and perform inference.
    
    Args:
        contract_address (str): Address of the deployed workflow contract
        
    Returns:
        Dict[str, Union[str, Dict]]: Status of the run operation
    """
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.run_workflow(contract_address)
