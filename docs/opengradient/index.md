---
outline: [2,3]
---

  

# Package opengradient

OpenGradient Python SDK for interacting with AI models and infrastructure.

## Submodules

* [**alphasense**](./alphasense): OpenGradient AlphaSense Tools
* [**llm**](./llm): OpenGradient LLM Adapters
* [**workflow_models**](./workflow_models): OpenGradient Hardcoded Models

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
def init(email: str, password: str, private_key: str, rpc_url='http://18.188.176.119:8545', contract_address='0x8383C9bD7462F12Eb996DD02F78234C0421A6FaE')
```

  

  
Initialize the OpenGradient SDK with authentication and network settings.
  

**Arguments**

* **`email`**: User's email address for authentication
* **`password`**: User's password for authentication
* **`private_key`**: Ethereum private key for blockchain transactions
* **`rpc_url`**: Optional RPC URL for the blockchain network, defaults to mainnet
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
def llm_chat(model_cid: opengradient.types.LLM, messages: List[Dict], inference_mode: opengradient.types.LlmInferenceMode = LlmInferenceMode.VANILLA, max_tokens: int = 100, stop_sequence: Optional[List[str]] = None, temperature: float = 0.0, tools: Optional[List[Dict]] = None, tool_choice: Optional[str] = None, max_retries: Optional[int] = None) ‑> opengradient.types.TextGenerationOutput
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

TextGenerationOutput

**Raises**

* **`RuntimeError`**: If SDK is not initialized
  

  

### Llm completion 

```python
def llm_completion(model_cid: opengradient.types.LLM, prompt: str, inference_mode: opengradient.types.LlmInferenceMode = LlmInferenceMode.VANILLA, max_tokens: int = 100, stop_sequence: Optional[List[str]] = None, temperature: float = 0.0, max_retries: Optional[int] = None) ‑> opengradient.types.TextGenerationOutput
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
  

  

### New workflow 

```python
def new_workflow(model_cid: str, input_query: opengradient.types.HistoricalInputQuery, input_tensor_name: str, scheduler_params: Optional[opengradient.types.SchedulerParams] = None) ‑> str
```

  

  
Deploy a new workflow contract with the specified parameters.

This function deploys a new workflow contract and optionally registers it with
the scheduler for automated execution. If scheduler_params is not provided,
the workflow will be deployed without automated execution scheduling.
  

**Arguments**

* **`model_cid`**: IPFS CID of the model
* **`input_query`**: HistoricalInputQuery containing query parameters
* **`input_tensor_name`**: Name of the input tensor
* **`scheduler_params`**: Optional scheduler configuration as SchedulerParams instance
        If not provided, the workflow will be deployed without scheduling.

  
**Returns**

str: Deployed contract address. If scheduler_params was provided, the workflow
     will be automatically executed according to the specified schedule.

  

### Read workflow history 

```python
def read_workflow_history(contract_address: str, num_results: int) ‑> List[opengradient.types.ModelOutput]
```

  

  
Gets historical inference results from a workflow contract.
  

**Returns**

List[Dict]: List of historical inference results

  

### Read workflow result 

```python
def read_workflow_result(contract_address: str) ‑> opengradient.types.ModelOutput
```

  

  
Reads the latest inference result from a deployed workflow contract.

This function retrieves the most recent output from a deployed model executor contract.
It includes built-in retry logic to handle blockchain state delays.
  

**Returns**

Dict[str, Union[str, Dict]]: A dictionary containing:
    - status: "success" or "error"
    - result: The model output data if successful
    - error: Error message if status is "error"

**Raises**

* **`RuntimeError`**: If OpenGradient client is not initialized
  

  

### Run workflow 

```python
def run_workflow(contract_address: str) ‑> opengradient.types.ModelOutput
```

  

  
Executes the workflow by calling run() on the contract to pull latest data and perform inference.
  

**Returns**

Dict[str, Union[str, Dict]]: Status of the run operation

  

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

  
    
* static `ASCENDING`
    
* static `DESCENDING`

      
    

###  CandleType

<code>class <b>CandleType</b>(*args, **kwds)</code>

  

  
Enum where members are also (and must be) ints
  

#### Variables

  
    
* static `CLOSE`
    
* static `HIGH`
    
* static `LOW`
    
* static `OPEN`
    
* static `VOLUME`

      
    

###  HistoricalInputQuery

<code>class <b>HistoricalInputQuery</b>(base: str, quote: str, total_candles: int, candle_duration_in_mins: int, order: [CandleOrder](docs/types.md#CandleOrder), candle_types: List[[CandleType](docs/types.md#CandleType)])</code>

  

  
HistoricalInputQuery(base: str, quote: str, total_candles: int, candle_duration_in_mins: int, order: opengradient.types.CandleOrder, candle_types: List[opengradient.types.CandleType])
  

  

### To abi format 

```python
def to_abi_format(self) ‑> tuple
```

  

  
Convert to format expected by contract ABI
  

#### Variables

  
    
* static `base  : str`
    
* static `candle_duration_in_mins  : int`
    
* static `candle_types  : List[opengradient.types.CandleType]`
    
* static `order  : opengradient.types.CandleOrder`
    
* static `quote  : str`
    
* static `total_candles  : int`

      
    

###  InferenceMode

<code>class <b>InferenceMode</b>(*args, **kwds)</code>

  

  
Enum for the different inference modes available for inference (VANILLA, ZKML, TEE)
  

#### Variables

  
    
* static `TEE`
    
* static `VANILLA`
    
* static `ZKML`

      
    

###  LLM

<code>class <b>LLM</b>(*args, **kwds)</code>

  

  
Enum for available LLM models
  

#### Variables

  
    
* static `DOBBY_LEASHED_3_1_8B`
    
* static `DOBBY_UNHINGED_3_1_8B`
    
* static `LLAMA_3_2_3B_INSTRUCT`
    
* static `META_LLAMA_3_1_70B_INSTRUCT`
    
* static `META_LLAMA_3_8B_INSTRUCT`
    
* static `QWEN_2_5_72B_INSTRUCT`

      
    

###  LlmInferenceMode

<code>class <b>LlmInferenceMode</b>(*args, **kwds)</code>

  

  
Enum for differetn inference modes available for LLM inferences (VANILLA, TEE)
  

#### Variables

  
    
* static `TEE`
    
* static `VANILLA`

      
    

###  SchedulerParams

<code>class <b>SchedulerParams</b>(frequency: int, duration_hours: int)</code>

  

  
SchedulerParams(frequency: int, duration_hours: int)
  

  

### From dict 

```python
def from_dict(data: Optional[Dict[str, int]]) ‑> Optional[opengradient.types.SchedulerParams]
```

  

  

  

#### Variables

  
    
* static `duration_hours  : int`
    
* static `frequency  : int`

  
    
* `end_time  : int`

      
    

###  TEE_LLM

<code>class <b>TEE_LLM</b>(*args, **kwds)</code>

  

  
Enum for LLM models available for TEE execution
  

#### Variables

  
    
* static `META_LLAMA_3_1_70B_INSTRUCT`