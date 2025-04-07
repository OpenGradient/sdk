"""
OpenGradient Python SDK for interacting with AI models and infrastructure.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

from .client import Client
from .defaults import DEFAULT_INFERENCE_CONTRACT_ADDRESS, DEFAULT_RPC_URL, DEFAULT_API_URL
from .types import (
    LLM,
    TEE_LLM,
    HistoricalInputQuery,
    SchedulerParams,
    CandleType,
    CandleOrder,
    InferenceMode,
    InferenceResult,
    LlmInferenceMode,
    TextGenerationOutput,
    ModelOutput,
    ModelRepository,
    FileUploadResult,
)

from . import llm, alphasense

_client = None


def new_client(
    email: Optional[str],
    password: Optional[str],
    private_key: str,
    rpc_url=DEFAULT_RPC_URL,
    api_url=DEFAULT_API_URL,
    contract_address=DEFAULT_INFERENCE_CONTRACT_ADDRESS,
) -> Client:
    """
    Creates a unique OpenGradient client instance with the given authentication and network settings.

    Args:
        email: User's email address for authentication with Model Hub
        password: User's password for authentication with Model Hub
        private_key: Private key for OpenGradient transactions
        rpc_url: Optional RPC URL for the blockchain network, defaults to mainnet
        contract_address: Optional inference contract address
    """

    return Client(email=email, password=password, private_key=private_key, rpc_url=rpc_url, api_url=api_url, contract_address=contract_address)


def init(email: str, password: str, private_key: str, rpc_url=DEFAULT_RPC_URL, api_url=DEFAULT_API_URL, contract_address=DEFAULT_INFERENCE_CONTRACT_ADDRESS):
    """Initialize the OpenGradient SDK with authentication and network settings.

    Args:
        email: User's email address for authentication
        password: User's password for authentication
        private_key: Ethereum private key for blockchain transactions
        rpc_url: Optional RPC URL for the blockchain network, defaults to mainnet
        api_url: Optional API URL for the OpenGradient API, defaults to mainnet
        contract_address: Optional inference contract address
    """
    global _client
    
    _client = Client(private_key=private_key, rpc_url=rpc_url, api_url=api_url, email=email, password=password, contract_address=contract_address)
    return _client


def upload(model_path, model_name, version) -> FileUploadResult:
    """Upload a model file to OpenGradient.

    Args:
        model_path: Path to the model file on local filesystem
        model_name: Name of the model repository
        version: Version string for this model upload

    Returns:
        FileUploadResult: Upload response containing file metadata

    Raises:
        RuntimeError: If SDK is not initialized
    """
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.upload(model_path, model_name, version)


def create_model(model_name: str, model_desc: str, model_path: Optional[str] = None) -> ModelRepository:
    """Create a new model repository.

    Args:
        model_name: Name for the new model repository
        model_desc: Description of the model
        model_path: Optional path to model file to upload immediately

    Returns:
        ModelRepository: Creation response with model metadata and optional upload results

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


def infer(model_cid, inference_mode, model_input, max_retries: Optional[int] = None) -> InferenceResult:
    """Run inference on a model.

    Args:
        model_cid: CID of the model to use
        inference_mode: Mode of inference (e.g. VANILLA)
        model_input: Input data for the model
        max_retries: Maximum number of retries for failed transactions

    Returns:
        InferenceResult (InferenceResult): A dataclass object containing the transaction hash and model output.
            * transaction_hash (str): Blockchain hash for the transaction
            * model_output (Dict[str, np.ndarray]): Output of the ONNX model

    Raises:
        RuntimeError: If SDK is not initialized
    """
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.infer(model_cid, inference_mode, model_input, max_retries=max_retries)


def llm_completion(
    model_cid: LLM,
    prompt: str,
    inference_mode: LlmInferenceMode = LlmInferenceMode.VANILLA,
    max_tokens: int = 100,
    stop_sequence: Optional[List[str]] = None,
    temperature: float = 0.0,
    max_retries: Optional[int] = None,
) -> TextGenerationOutput:
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
        TextGenerationOutput: Transaction hash and generated text

    Raises:
        RuntimeError: If SDK is not initialized
    """
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.llm_completion(
        model_cid=model_cid,
        inference_mode=inference_mode,
        prompt=prompt,
        max_tokens=max_tokens,
        stop_sequence=stop_sequence,
        temperature=temperature,
        max_retries=max_retries,
    )


def llm_chat(
    model_cid: LLM,
    messages: List[Dict],
    inference_mode: LlmInferenceMode = LlmInferenceMode.VANILLA,
    max_tokens: int = 100,
    stop_sequence: Optional[List[str]] = None,
    temperature: float = 0.0,
    tools: Optional[List[Dict]] = None,
    tool_choice: Optional[str] = None,
    max_retries: Optional[int] = None,
) -> TextGenerationOutput:
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
        TextGenerationOutput

    Raises:
        RuntimeError: If SDK is not initialized
    """
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.llm_chat(
        model_cid=model_cid,
        inference_mode=inference_mode,
        messages=messages,
        max_tokens=max_tokens,
        stop_sequence=stop_sequence,
        temperature=temperature,
        tools=tools,
        tool_choice=tool_choice,
        max_retries=max_retries,
    )


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


def new_workflow(
    model_cid: str,
    input_query: HistoricalInputQuery,
    input_tensor_name: str,
    scheduler_params: Optional[SchedulerParams] = None,
) -> str:
    """
    Deploy a new workflow contract with the specified parameters.

    This function deploys a new workflow contract and optionally registers it with
    the scheduler for automated execution. If scheduler_params is not provided,
    the workflow will be deployed without automated execution scheduling.

    Args:
        model_cid: IPFS CID of the model
        input_query: HistoricalInputQuery containing query parameters
        input_tensor_name: Name of the input tensor
        scheduler_params: Optional scheduler configuration as SchedulerParams instance
            If not provided, the workflow will be deployed without scheduling.

    Returns:
        str: Deployed contract address. If scheduler_params was provided, the workflow
             will be automatically executed according to the specified schedule.
    """
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init(...) first.")

    return _client.new_workflow(
        model_cid=model_cid, input_query=input_query, input_tensor_name=input_tensor_name, scheduler_params=scheduler_params
    )


def read_workflow_result(contract_address: str) -> ModelOutput:
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


def run_workflow(contract_address: str) -> ModelOutput:
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


def read_workflow_history(contract_address: str, num_results: int) -> List[ModelOutput]:
    """
    Gets historical inference results from a workflow contract.

    Args:
        contract_address (str): Address of the deployed workflow contract
        num_results (int): Number of historical results to retrieve

    Returns:
        List[Dict]: List of historical inference results
    """
    if _client is None:
        raise RuntimeError("OpenGradient client not initialized. Call og.init() first.")
    return _client.read_workflow_history(contract_address, num_results)


__all__ = [
    "list_files",
    "login",
    "llm_chat",
    "llm_completion",
    "infer",
    "create_version",
    "create_model",
    "upload",
    "init",
    "LLM",
    "TEE_LLM",
    "new_workflow",
    "read_workflow_result",
    "run_workflow",
    "read_workflow_history",
    "InferenceMode",
    "LlmInferenceMode",
    "HistoricalInputQuery",
    "SchedulerParams",
    "CandleType",
    "CandleOrder",
    "InferenceMode",
    "llm",
    "alphasense",
]

__pdoc__ = {
    "account": False,
    "cli": False,
    "client": False,
    "defaults": False,
    "exceptions": False,
    "llm": True,
    "alphasense": True,
    "proto": False,
    "types": False,
    "utils": False,
}
