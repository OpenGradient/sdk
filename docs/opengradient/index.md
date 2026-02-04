---
outline: [2,3]
---

  

# Package opengradient

OpenGradient Python SDK for interacting with AI models and infrastructure.

## Submodules

* [**alpha**](./alpha): Alpha Testnet features for OpenGradient SDK.
* [**alphasense**](./alphasense): OpenGradient AlphaSense Tools
* [**llm**](./llm): OpenGradient LLM Adapters
* [**workflow_models**](./workflow_models): OpenGradient Hardcoded Models
* [**x402_auth**](./x402_auth): X402 Authentication handler for httpx streaming requests.

## Functions

  

### Create model 

```python
def create_model(model_name: str, model_desc: str, model_path: Optional[str] = None) ‑> opengradient.types.ModelRepository
```

  

  
Create a new model repository.
  

**Arguments**

* **`model_name`**: Name for the new model repository
* **`model_desc`**: Description of the model
* **`model_path`**: Optional path to model file to upload immediately

  
**Returns**

ModelRepository: Creation response with model metadata and optional upload results

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
  

  

### Infer 

```python
def infer(model_cid, inference_mode, model_input, max_retries: Optional[int] = None) ‑> opengradient.types.InferenceResult
```

  

  
Run inference on a model.
  

**Arguments**

* **`model_cid`**: CID of the model to use
* **`inference_mode`**: Mode of inference (e.g. VANILLA)
* **`model_input`**: Input data for the model
* **`max_retries`**: Maximum number of retries for failed transactions

  
**Returns**

InferenceResult (InferenceResult): A dataclass object containing the transaction hash and model output.
    * transaction_hash (str): Blockchain hash for the transaction
    * model_output (Dict[str, np.ndarray]): Output of the ONNX model

**Raises**

* **`RuntimeError`**: If SDK is not initialized
  

  

### Init 

```python
def init(email: str, password: str, private_key: str, rpc_url='https://ogevmdevnet.opengradient.ai', api_url='https://sdk-devnet.opengradient.ai', contract_address='0x8383C9bD7462F12Eb996DD02F78234C0421A6FaE')
```

  

  
Initialize the OpenGradient SDK with authentication and network settings.
  

**Arguments**

* **`email`**: User's email address for authentication
* **`password`**: User's password for authentication
* **`private_key`**: Ethereum private key for blockchain transactions
* **`rpc_url`**: Optional RPC URL for the blockchain network, defaults to devnet
* **`api_url`**: Optional API URL for the OpenGradient API, defaults to devnet
* **`contract_address`**: Optional inference contract address
  

  

### List files 

```python
def list_files(model_name: str, version: str) ‑> List[Dict]
```

  

  
List files in a model repository version.
  

**Arguments**

* **`model_name`**: Name of the model repository
* **`version`**: Version string to list files from

  
**Returns**

List[Dict]: List of file metadata dictionaries

**Raises**

* **`RuntimeError`**: If SDK is not initialized
  

  

### Llm chat 

```python
def llm_chat(model_cid: opengradient.types.LLM, messages: List[Dict], inference_mode: opengradient.types.LlmInferenceMode = LlmInferenceMode.VANILLA, max_tokens: int = 100, stop_sequence: Optional[List[str]] = None, temperature: float = 0.0, tools: Optional[List[Dict]] = None, tool_choice: Optional[str] = None, max_retries: Optional[int] = None, x402_settlement_mode: Optional[opengradient.types.x402SettlementMode] = settle-batch, stream: Optional[bool] = False) ‑> Union[opengradient.types.TextGenerationOutput, opengradient.types.TextGenerationStream]
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
* **`x402_settlement_mode`**: Settlement modes for x402 payment protocol transactions (enum x402SettlementMode)
* **`stream`**: Optional boolean to enable streaming

  
**Returns**

TextGenerationOutput or TextGenerationStream

**Raises**

* **`RuntimeError`**: If SDK is not initialized
  

  

### Llm completion 

```python
def llm_completion(model_cid: opengradient.types.LLM, prompt: str, inference_mode: opengradient.types.LlmInferenceMode = LlmInferenceMode.VANILLA, max_tokens: int = 100, stop_sequence: Optional[List[str]] = None, temperature: float = 0.0, max_retries: Optional[int] = None, x402_settlement_mode: Optional[opengradient.types.x402SettlementMode] = settle-batch) ‑> opengradient.types.TextGenerationOutput
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
* **`x402_settlement_mode`**: Settlement modes for x402 payment protocol transactions (enum x402SettlementMode)

  
**Returns**

TextGenerationOutput: Transaction hash and generated text

**Raises**

* **`RuntimeError`**: If SDK is not initialized
  

  

### Login 

```python
def login(model_name: str, version: str) ‑> List[Dict]
```

  

  
List files in a model repository version.
  

**Arguments**

* **`model_name`**: Name of the model repository
* **`version`**: Version string to list files from

  
**Returns**

List[Dict]: List of file metadata dictionaries

**Raises**

* **`RuntimeError`**: If SDK is not initialized
  

  

### Upload 

```python
def upload(model_path, model_name, version) ‑> opengradient.types.FileUploadResult
```

  

  
Upload a model file to OpenGradient.
  

**Arguments**

* **`model_path`**: Path to the model file on local filesystem
* **`model_name`**: Name of the model repository
* **`version`**: Version string for this model upload

  
**Returns**

FileUploadResult: Upload response containing file metadata

**Raises**

* **`RuntimeError`**: If SDK is not initialized
  

## Classes
    

###  CandleOrder

<code>class <b>CandleOrder</b>(*args, **kwds)</code>

  

  
Enum where members are also (and must be) ints
  

#### Variables

  
    
* static `ASCENDING` - The type of the None singleton.
    
* static `DESCENDING` - The type of the None singleton.

      
    

###  CandleType

<code>class <b>CandleType</b>(*args, **kwds)</code>

  

  
Enum where members are also (and must be) ints
  

#### Variables

  
    
* static `CLOSE` - The type of the None singleton.
    
* static `HIGH` - The type of the None singleton.
    
* static `LOW` - The type of the None singleton.
    
* static `OPEN` - The type of the None singleton.
    
* static `VOLUME` - The type of the None singleton.

      
    

###  HistoricalInputQuery

<code>class <b>HistoricalInputQuery</b>(base: str, quote: str, total_candles: int, candle_duration_in_mins: int, order: [CandleOrder](docs/types.md#CandleOrder), candle_types: List[[CandleType](docs/types.md#CandleType)])</code>

  

  
HistoricalInputQuery(base: str, quote: str, total_candles: int, candle_duration_in_mins: int, order: opengradient.types.CandleOrder, candle_types: List[opengradient.types.CandleType])
  

  

### To abi format 

```python
def to_abi_format(self) ‑> tuple
```

  

  
Convert to format expected by contract ABI
  

#### Variables

  
    
* static `base  : str` - The type of the None singleton.
    
* static `candle_duration_in_mins  : int` - The type of the None singleton.
    
* static `candle_types  : List[opengradient.types.CandleType]` - The type of the None singleton.
    
* static `order  : opengradient.types.CandleOrder` - The type of the None singleton.
    
* static `quote  : str` - The type of the None singleton.
    
* static `total_candles  : int` - The type of the None singleton.

      
    

###  InferenceMode

<code>class <b>InferenceMode</b>(*args, **kwds)</code>

  

  
Enum for the different inference modes available for inference (VANILLA, ZKML, TEE)
  

#### Variables

  
    
* static `TEE` - The type of the None singleton.
    
* static `VANILLA` - The type of the None singleton.
    
* static `ZKML` - The type of the None singleton.

      
    

###  LLM

<code>class <b>LLM</b>(*args, **kwds)</code>

  

  
Enum for available LLM models
  

#### Variables

  
    
* static `CLAUDE_3_5_HAIKU` - The type of the None singleton.
    
* static `CLAUDE_3_7_SONNET` - The type of the None singleton.
    
* static `CLAUDE_4_0_SONNET` - The type of the None singleton.
    
* static `GEMINI_2_0_FLASH` - The type of the None singleton.
    
* static `GEMINI_2_5_FLASH` - The type of the None singleton.
    
* static `GEMINI_2_5_FLASH_LITE` - The type of the None singleton.
    
* static `GEMINI_2_5_PRO` - The type of the None singleton.
    
* static `GPT_4O` - The type of the None singleton.
    
* static `GPT_4_1_2025_04_14` - The type of the None singleton.
    
* static `GROK_2_1212` - The type of the None singleton.
    
* static `GROK_2_VISION_LATEST` - The type of the None singleton.
    
* static `GROK_3_BETA` - The type of the None singleton.
    
* static `GROK_3_MINI_BETA` - The type of the None singleton.
    
* static `GROK_4_1_FAST` - The type of the None singleton.
    
* static `GROK_4_1_FAST_NON_REASONING` - The type of the None singleton.
    
* static `O4_MINI` - The type of the None singleton.

      
    

###  LlmInferenceMode

<code>class <b>LlmInferenceMode</b>(*args, **kwds)</code>

  

  
Enum for different inference modes available for LLM inference (VANILLA, TEE)
  

#### Variables

  
    
* static `TEE` - The type of the None singleton.
    
* static `VANILLA` - The type of the None singleton.

      
    

###  SchedulerParams

<code>class <b>SchedulerParams</b>(frequency: int, duration_hours: int)</code>

  

  
SchedulerParams(frequency: int, duration_hours: int)
  

  

### From dict 

```python
def from_dict(data: Optional[Dict[str, int]]) ‑> Optional[opengradient.types.SchedulerParams]
```

  

  

  

#### Variables

  
    
* static `duration_hours  : int` - The type of the None singleton.
    
* static `frequency  : int` - The type of the None singleton.

  
    
* `end_time  : int`

      
    

###  TEE_LLM

<code>class <b>TEE_LLM</b>(*args, **kwds)</code>

  

  
Enum for LLM models available for TEE execution
  

#### Variables

  
    
* static `CLAUDE_3_5_HAIKU` - The type of the None singleton.
    
* static `CLAUDE_3_7_SONNET` - The type of the None singleton.
    
* static `CLAUDE_4_0_SONNET` - The type of the None singleton.
    
* static `GEMINI_2_0_FLASH` - The type of the None singleton.
    
* static `GEMINI_2_5_FLASH` - The type of the None singleton.
    
* static `GEMINI_2_5_FLASH_LITE` - The type of the None singleton.
    
* static `GEMINI_2_5_PRO` - The type of the None singleton.
    
* static `GPT_4O` - The type of the None singleton.
    
* static `GPT_4_1_2025_04_14` - The type of the None singleton.
    
* static `GROK_2_1212` - The type of the None singleton.
    
* static `GROK_2_VISION_LATEST` - The type of the None singleton.
    
* static `GROK_3_BETA` - The type of the None singleton.
    
* static `GROK_3_MINI_BETA` - The type of the None singleton.
    
* static `GROK_4_1_FAST` - The type of the None singleton.
    
* static `GROK_4_1_FAST_NON_REASONING` - The type of the None singleton.
    
* static `O4_MINI` - The type of the None singleton.