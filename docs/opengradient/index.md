Module opengradient
===================

Sub-modules
-----------
* opengradient.llm

Functions
---------

`create_model(model_name: str, model_desc: str, model_path: str = None)`
:   

`create_version(model_name, notes=None, is_major=False)`
:   

`generate_image(model: str, prompt: str, height: int | None = None, width: int | None = None) ‑> bytes`
:   Generate an image using the specified model and prompt.
    
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

`infer(model_cid, inference_mode, model_input, max_retries: int | None = None)`
:   Perform inference on a model.
    
    Args:
        model_cid: Model CID to use for inference
        inference_mode: Mode of inference (e.g. VANILLA)
        model_input: Input data for the model
        max_retries: Optional maximum number of retry attempts for transaction errors
    
    Returns:
        Tuple of (transaction hash, model output)

`init(email: str, password: str, private_key: str, rpc_url='http://18.218.115.248:8545', contract_address='0x3fDCb0394CF4919ff4361f4EbA0750cEc2e3bBc7')`
:   

`llm_chat(model_cid: opengradient.types.LLM, messages: List[Dict], inference_mode: str = 0, max_tokens: int = 100, stop_sequence: List[str] | None = None, temperature: float = 0.0, tools: List[Dict] | None = None, tool_choice: str | None = None, max_retries: int | None = None) ‑> Tuple[str, str, Dict]`
:   

`llm_completion(model_cid: opengradient.types.LLM, prompt: str, inference_mode: str = 0, max_tokens: int = 100, stop_sequence: List[str] | None = None, temperature: float = 0.0, max_retries: int | None = None) ‑> Tuple[str, str]`
:   

`upload(model_path, model_name, version)`
: