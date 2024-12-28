---
outline: [2,3]
---

  

# Package opengradient

OpenGradient Python SDK for interacting with AI models and infrastructure.

## Submodules

* [**llm**](./llm): OpenGradient LLM Adapters

## Functions

  

### Create model 

```python
def create_model(model_name: str, model_desc: str, model_path: str = None)
```

  

  
Create a new model repository.
  

**Arguments**

* **`model_name`**: Name for the new model repository
* **`model_desc`**: Description of the model
* **`model_path`**: Optional path to model file to upload immediately

  
**Returns**

dict: Creation response with model metadata and optional upload results

**Raises**

* **`RuntimeError`**: If SDK is not initialized
  

  

### Create version 

```python
def create_version(model_name, notes=None, is_major=False)
```

  

  
Create a new version for an existing model.
  

**Arguments**

* **`model_name`**: Name of the model repository
* **`notes`**: Optional release notes for this version
* **`is_major`**: If True, creates a major version bump instead of minor

  
**Returns**

dict: Version creation response with version metadata

**Raises**

* **`RuntimeError`**: If SDK is not initialized
  

  

### Generate image 

```python
def generate_image(model: str, prompt: str, height: int | None = None, width: int | None = None) ‑> bytes
```

  

  
Generate an image from a text prompt.
  

**Arguments**

* **`model`**: Model identifier (e.g. "stabilityai/stable-diffusion-xl-base-1.0")
* **`prompt`**: Text description of the desired image
* **`height`**: Optional height of the generated image in pixels
* **`width`**: Optional width of the generated image in pixels

  
**Returns**

bytes: Raw image data as bytes

**Raises**

* **`RuntimeError`**: If SDK is not initialized
* **`OpenGradientError`**: If image generation fails
  

  

### Infer 

```python
def infer(model_cid, inference_mode, model_input, max_retries: int | None = None)
```

  

  
Run inference on a model.
  

**Arguments**

* **`model_cid`**: CID of the model to use
* **`inference_mode`**: Mode of inference (e.g. VANILLA)
* **`model_input`**: Input data for the model
* **`max_retries`**: Maximum number of retries for failed transactions

  
**Returns**

Tuple[str, Any]: Transaction hash and model output

**Raises**

* **`RuntimeError`**: If SDK is not initialized
  

  

### Init 

```python
def init(email: str, password: str, private_key: str, rpc_url='http://18.218.115.248:8545', contract_address='0x3fDCb0394CF4919ff4361f4EbA0750cEc2e3bBc7')
```

  

  
Initialize the OpenGradient SDK with authentication and network settings.
  

**Arguments**

* **`email`**: User's email address for authentication
* **`password`**: User's password for authentication
* **`private_key`**: Ethereum private key for blockchain transactions
* **`rpc_url`**: Optional RPC URL for the blockchain network, defaults to mainnet
* **`contract_address`**: Optional inference contract address
  

  

### Llm chat 

```python
def llm_chat(model_cid: opengradient.types.LLM, messages: List[Dict], inference_mode: str = 0, max_tokens: int = 100, stop_sequence: List[str] | None = None, temperature: float = 0.0, tools: List[Dict] | None = None, tool_choice: str | None = None, max_retries: int | None = None) ‑> Tuple[str, str, Dict]
```

  

  
Have a chat conversation with an LLM.
  

**Arguments**

* **`model_cid`**: CID of the LLM model to use
* **`messages`**: List of chat messages, each with 'role' and 'content'
* **`inference_mode`**: Mode of inference, defaults to VANILLA
* **`max_tokens`**: Maximum tokens to generate
* **`stop_sequence`**: Optional list of sequences where generation should stop
* **`temperature`**: Sampling temperature (0.0 = deterministic, 1.0 = creative)
* **`tools`**: Optional list of tools the model can use
* **`tool_choice`**: Optional specific tool to use
* **`max_retries`**: Maximum number of retries for failed transactions

  
**Returns**

Tuple[str, str, Dict]: Transaction hash, model response, and metadata

**Raises**

* **`RuntimeError`**: If SDK is not initialized
  

  

### Llm completion 

```python
def llm_completion(model_cid: opengradient.types.LLM, prompt: str, inference_mode: str = 0, max_tokens: int = 100, stop_sequence: List[str] | None = None, temperature: float = 0.0, max_retries: int | None = None) ‑> Tuple[str, str]
```

  

  
Generate text completion using an LLM.
  

**Arguments**

* **`model_cid`**: CID of the LLM model to use
* **`prompt`**: Text prompt for completion
* **`inference_mode`**: Mode of inference, defaults to VANILLA
* **`max_tokens`**: Maximum tokens to generate
* **`stop_sequence`**: Optional list of sequences where generation should stop
* **`temperature`**: Sampling temperature (0.0 = deterministic, 1.0 = creative)
* **`max_retries`**: Maximum number of retries for failed transactions

  
**Returns**

Tuple[str, str]: Transaction hash and generated text

**Raises**

* **`RuntimeError`**: If SDK is not initialized
  

  

### Upload 

```python
def upload(model_path, model_name, version)
```

  

  
Upload a model file to OpenGradient.
  

**Arguments**

* **`model_path`**: Path to the model file on local filesystem
* **`model_name`**: Name of the model repository
* **`version`**: Version string for this model upload

  
**Returns**

dict: Upload response containing file metadata

**Raises**

* **`RuntimeError`**: If SDK is not initialized
  

## Classes
    

###  LLM

<code>class <b>LLM</b>(*args, **kwds)</code>

  

  
Enum for available LLM models
  

#### Variables

  
    
* static `HERMES_3_LLAMA_3_1_70B`
    
* static `LLAMA_3_2_3B_INSTRUCT`
    
* static `META_LLAMA_3_1_70B_INSTRUCT`
    
* static `META_LLAMA_3_8B_INSTRUCT`
    
* static `MISTRAL_7B_INSTRUCT_V3`

      
    

###  TEE_LLM

<code>class <b>TEE_LLM</b>(*args, **kwds)</code>

  

  
Enum for LLM models available for TEE execution
  

#### Variables

  
    
* static `META_LLAMA_3_1_70B_INSTRUCT`