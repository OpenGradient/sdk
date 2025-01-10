"""
OpenGradient Python SDK for interacting with AI models and infrastructure.
"""
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
from .client import Client
from .defaults import DEFAULT_INFERENCE_CONTRACT_ADDRESS, DEFAULT_RPC_URL
from .types import InferenceMode, LlmInferenceMode, LLM, TEE_LLM
from . import llm
from . import mltools

_client = None

def init(email: str,
         password: str,
         private_key: str,
         rpc_url=DEFAULT_RPC_URL,
         contract_address=DEFAULT_INFERENCE_CONTRACT_ADDRESS):
    """Initialize the OpenGradient SDK with authentication and network settings.

    Args:
        email: User's email address for authentication
        password: User's password for authentication
        private_key: Ethereum private key for blockchain transactions
        rpc_url: Optional RPC URL for the blockchain network, defaults to mainnet
        contract_address: Optional inference contract address
    """
    global _client
    
    _client = Client(
        private_key=private_key,
        rpc_url=rpc_url,
        email=email,
        password=password,
        contract_address=contract_address
    )
    return _client

def upload(model_path, model_name, version):
    """Upload a model file to OpenGradient.

    Args:
        model_path: Path to the model file on local filesystem
        model_name: Name of the model repository
        version: Version string for this model upload

    Returns:
        dict: Upload response containing file metadata

    Raises:
        RuntimeError: If SDK is not initialized
    """
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.upload(model_path, model_name, version)

def create_model(model_name: str, model_desc: str, model_path: str = None):
    """Create a new model repository.

    Args:
        model_name: Name for the new model repository
        model_desc: Description of the model
        model_path: Optional path to model file to upload immediately

    Returns:
        dict: Creation response with model metadata and optional upload results

    Raises:
        RuntimeError: If SDK is not initialized
    """
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    
    result = _client.create_model(model_name, model_desc)
    
    if model_path:
        version = "0.01"
        upload_result = _client.upload(model_path, model_name, version)
        result["upload"] = upload_result
    
    return result

def create_version(model_name, notes=None, is_major=False):
    """Create a new version for an existing model.

    Args:
        model_name: Name of the model repository
        notes: Optional release notes for this version
        is_major: If True, creates a major version bump instead of minor

    Returns:
        dict: Version creation response with version metadata

    Raises:
        RuntimeError: If SDK is not initialized
    """
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.create_version(model_name, notes, is_major)

def infer(model_cid, inference_mode, model_input, max_retries: Optional[int] = None):
    """Run inference on a model.

    Args:
        model_cid: CID of the model to use
        inference_mode: Mode of inference (e.g. VANILLA)
        model_input: Input data for the model
        max_retries: Maximum number of retries for failed transactions

    Returns:
        Tuple[str, Any]: Transaction hash and model output

    Raises:
        RuntimeError: If SDK is not initialized
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
    """Generate text completion using an LLM.

    Args:
        model_cid: CID of the LLM model to use
        prompt: Text prompt for completion
        inference_mode: Mode of inference, defaults to VANILLA
        max_tokens: Maximum tokens to generate
        stop_sequence: Optional list of sequences where generation should stop
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
        max_retries: Maximum number of retries for failed transactions

    Returns:
        Tuple[str, str]: Transaction hash and generated text

    Raises:
        RuntimeError: If SDK is not initialized
    """
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
    """Have a chat conversation with an LLM.

    Args:
        model_cid: CID of the LLM model to use
        messages: List of chat messages, each with 'role' and 'content'
        inference_mode: Mode of inference, defaults to VANILLA
        max_tokens: Maximum tokens to generate
        stop_sequence: Optional list of sequences where generation should stop
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
        tools: Optional list of tools the model can use
        tool_choice: Optional specific tool to use
        max_retries: Maximum number of retries for failed transactions

    Returns:
        Tuple[str, str, Dict]: Transaction hash, model response, and metadata

    Raises:
        RuntimeError: If SDK is not initialized
    """
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
    """Login to OpenGradient.

    Args:
        email: User's email address
        password: User's password

    Returns:
        dict: Login response with authentication tokens

    Raises:
        RuntimeError: If SDK is not initialized
    """
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.login(email, password)

def list_files(model_name: str, version: str) -> List[Dict]:
    """List files in a model repository version.

    Args:
        model_name: Name of the model repository
        version: Version string to list files from

    Returns:
        List[Dict]: List of file metadata dictionaries

    Raises:
        RuntimeError: If SDK is not initialized
    """
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.list_files(model_name, version)

def generate_image(model: str, prompt: str, height: Optional[int] = None, width: Optional[int] = None) -> bytes:
    """Generate an image from a text prompt.

    Args:
        model: Model identifier (e.g. "stabilityai/stable-diffusion-xl-base-1.0")
        prompt: Text description of the desired image
        height: Optional height of the generated image in pixels
        width: Optional width of the generated image in pixels

    Returns:
        bytes: Raw image data as bytes

    Raises:
        RuntimeError: If SDK is not initialized
        OpenGradientError: If image generation fails
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
    return _client.read_workflow_result(contract_address)

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

__all__ = [
    'generate_image',
    'list_files',
    'login',
    'llm_chat',
    'llm_completion',
    'infer',
    'create_version',
    'create_model',
    'upload',
    'init',
    'LLM',
    'TEE_LLM'
    'new_workflow',
    'read_workflow_result',
    'run_workflow'
]

__pdoc__ = {
    'account': False,
    'cli': False,
    'client': False,
    'defaults': False,
    'exceptions': False,
    'llm': True,
    'mltools': True,
    'proto': False,
    'types': False,
    'utils': False
}