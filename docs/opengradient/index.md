---
outline: [2,3]
---

  

# Package opengradient

OpenGradient Python SDK for interacting with AI models and infrastructure.

## Submodules

* [**agents**](./agents): OpenGradient LLM Adapters
* [**alphasense**](./alphasense): OpenGradient AlphaSense Tools
* [**client**](./client): 
* [**types**](./types): 
* [**workflow_models**](./workflow_models): OpenGradient Hardcoded Models

## Functions

  

### Init 

```python
def init(private_key: str, email: Optional[str] = None, password: Optional[str] = None, **kwargs) ‑> opengradient.client.client.Client
```

  

  
Initialize the global OpenGradient client.
  

**Arguments**

* **`private_key`**: Private key for OpenGradient transactions.
* **`email`**: Email for Model Hub authentication. Optional.
* **`password`**: Password for Model Hub authentication. Optional.
* **`**kwargs`**: Additional arguments forwarded to :class:`Client`.

  
**Returns**

The newly created :class:`Client` instance.

## Global variables

  
    
* `global_client  : Optional[opengradient.client.client.Client]` - Global client instance. Set by calling :func:`init`.

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

      
    

###  Client

<code>class <b>Client</b>(private_key: str, email: Optional[str] = None, password: Optional[str] = None, rpc_url: str = 'https://ogevmdevnet.opengradient.ai', api_url: str = 'https://sdk-devnet.opengradient.ai', contract_address: str = '0x8383C9bD7462F12Eb996DD02F78234C0421A6FaE', og_llm_server_url: Optional[str] = 'https://llmogevm.opengradient.ai', og_llm_streaming_server_url: Optional[str] = 'https://llmogevm.opengradient.ai')</code>

  

  
Initialize the OpenGradient client.
  

**Arguments**

* **`private_key`**: Private key for OpenGradient transactions.
* **`email`**: Email for Model Hub authentication. Optional.
* **`password`**: Password for Model Hub authentication. Optional.
* **`rpc_url`**: RPC URL for the blockchain network.
* **`api_url`**: API URL for the OpenGradient API.
* **`contract_address`**: Inference contract address.
* **`og_llm_server_url`**: OpenGradient LLM server URL.
* **`og_llm_streaming_server_url`**: OpenGradient LLM streaming server URL.
  

#### Variables

  
    
* static `inference  : opengradient.client.onchain_inference.Inference` - The type of the None singleton.
    
* static `llm  : opengradient.client.llm.LLM` - The type of the None singleton.
    
* static `model_hub  : opengradient.client.model_hub.ModelHub` - The type of the None singleton.

  
    
* `alpha` - Access Alpha Testnet features.

  Returns:
    Alpha: Alpha namespace with workflow and ML model execution methods.

  Example:
    client = og.Client(...)
    result = client.alpha.new_workflow(model_cid, input_query, input_tensor_name)

      
    

###  HistoricalInputQuery

<code>class <b>HistoricalInputQuery</b>(base: str, quote: str, total_candles: int, candle_duration_in_mins: int, order: `CandleOrder`, candle_types: List[`CandleType`])</code>

  

  
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

  

  
Enum for available LLM models in OpenGradient.

These models can be used with llm_chat() and llm_completion() methods.
You can use either the enum value or the string identifier directly.
  

**Note**

TEE_LLM enum contains the same models but is specifically for
Trusted Execution Environment (TEE) verified inference.

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

  

  
Enum for LLM models available for TEE (Trusted Execution Environment) execution.

TEE mode provides cryptographic verification that inference was performed
correctly in a secure enclave. Use this for applications requiring
auditability and tamper-proof AI inference.
  

**Note**

The models in TEE_LLM are the same as LLM, but this enum explicitly
indicates support for TEE execution.

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