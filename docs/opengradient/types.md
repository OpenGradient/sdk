---
outline: [2,3]
---

  

# Package opengradient.types

OpenGradient Specific Types

## Classes
    

###  Abi

```python
class Abi(functions: List[`AbiFunction`])
```

  

  
Abi(functions: List[opengradient.types.AbiFunction])
  

#### Static methods

  

### From json 

```python
def from_json(abi_json)
```

  

  

  

#### Variables

  
    
* static `functions  : List[opengradient.types.AbiFunction]`

      
    

###  AbiFunction

```python
class AbiFunction(name: str, inputs: List[Union[str, ForwardRef('`AbiFunction`')]], outputs: List[Union[str, ForwardRef('`AbiFunction`')]], state_mutability: str)
```

  

  
AbiFunction(name: str, inputs: List[Union[str, ForwardRef('AbiFunction')]], outputs: List[Union[str, ForwardRef('AbiFunction')]], state_mutability: str)
  

#### Variables

  
    
* static `inputs  : List[Union[str, opengradient.types.AbiFunction]]`
    
* static `name  : str`
    
* static `outputs  : List[Union[str, opengradient.types.AbiFunction]]`
    
* static `state_mutability  : str`

      
    

###  CandleOrder

```python
class CandleOrder(*args, **kwds)
```

  

  
Enum where members are also (and must be) ints
  

#### Variables

  
    
* static `ASCENDING`
    
* static `DESCENDING`

      
    

###  CandleType

```python
class CandleType(*args, **kwds)
```

  

  
Enum where members are also (and must be) ints
  

#### Variables

  
    
* static `CLOSE`
    
* static `HIGH`
    
* static `LOW`
    
* static `OPEN`
    
* static `VOLUME`

      
    

###  FileUploadResult

```python
class FileUploadResult(modelCid: str, size: int)
```

  

  
FileUploadResult(modelCid: str, size: int)
  

#### Variables

  
    
* static `modelCid  : str`
    
* static `size  : int`

      
    

###  HistoricalInputQuery

```python
class HistoricalInputQuery(base: str, quote: str, total_candles: int, candle_duration_in_mins: int, order: `CandleOrder`, candle_types: List[`CandleType`])
```

  

  
HistoricalInputQuery(base: str, quote: str, total_candles: int, candle_duration_in_mins: int, order: opengradient.types.CandleOrder, candle_types: List[opengradient.types.CandleType])
  

#### Methods

  

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

```python
class InferenceMode(*args, **kwds)
```

  

  
Enum for the different inference modes available for inference (VANILLA, ZKML, TEE)
  

#### Variables

  
    
* static `TEE`
    
* static `VANILLA`
    
* static `ZKML`

      
    

###  InferenceResult

```python
class InferenceResult(transaction_hash: str, model_output: Dict[str, `ndarray`])
```

  

  
Output for ML inference requests.
This class has two fields
    transaction_hash (str): Blockchain hash for the transaction
    model_output (Dict[str, np.ndarray]): Output of the ONNX model
  

#### Variables

  
    
* static `model_output  : Dict[str, numpy.ndarray]`
    
* static `transaction_hash  : str`

      
    

###  LLM

```python
class LLM(*args, **kwds)
```

  

  
Enum for available LLM models in OpenGradient.

These models can be used with llm_chat() and llm_completion() methods.
You can use either the enum value or the string identifier directly.
  

**Note**

TEE_LLM enum contains the same models but is specifically for
Trusted Execution Environment (TEE) verified inference.

#### Variables

  
    
* static `CLAUDE_3_5_HAIKU`
    
* static `CLAUDE_3_7_SONNET`
    
* static `CLAUDE_4_0_SONNET`
    
* static `GEMINI_2_0_FLASH`
    
* static `GEMINI_2_5_FLASH`
    
* static `GEMINI_2_5_FLASH_LITE`
    
* static `GEMINI_2_5_PRO`
    
* static `GPT_4O`
    
* static `GPT_4_1_2025_04_14`
    
* static `GROK_2_1212`
    
* static `GROK_2_VISION_LATEST`
    
* static `GROK_3_BETA`
    
* static `GROK_3_MINI_BETA`
    
* static `GROK_4_1_FAST`
    
* static `GROK_4_1_FAST_NON_REASONING`
    
* static `O4_MINI`

      
    

###  ModelInput

```python
class ModelInput(numbers: List[`NumberTensor`], strings: List[`StringTensor`])
```

  

  
A collection of tensor inputs required for ONNX model inference.
  

**Attributes**

* **`numbers`**: Collection of numeric tensors for the model.
* **`strings`**: Collection of string tensors for the model.
  

#### Variables

  
    
* static `numbers  : List[opengradient.types.NumberTensor]`
    
* static `strings  : List[opengradient.types.StringTensor]`

      
    

###  ModelOutput

```python
class ModelOutput(numbers: Dict[str, `ndarray`], strings: Dict[str, `ndarray`], jsons: Dict[str, `ndarray`], is_simulation_result: bool)
```

  

  
Model output struct based on translations from smart contract.
  

#### Variables

  
    
* static `is_simulation_result  : bool`
    
* static `jsons  : Dict[str, numpy.ndarray]`
    
* static `numbers  : Dict[str, numpy.ndarray]`
    
* static `strings  : Dict[str, numpy.ndarray]`

      
    

###  ModelRepository

```python
class ModelRepository(name: str, initialVersion: str)
```

  

  
ModelRepository(name: str, initialVersion: str)
  

#### Variables

  
    
* static `initialVersion  : str`
    
* static `name  : str`

      
    

###  Number

```python
class Number(value: int, decimals: int)
```

  

  
Number(value: int, decimals: int)
  

#### Variables

  
    
* static `decimals  : int`
    
* static `value  : int`

      
    

###  NumberTensor

```python
class NumberTensor(name: str, values: List[Tuple[int, int]])
```

  

  
A container for numeric tensor data used as input for ONNX models.
  

**Attributes**

* **`name`**: Identifier for this tensor in the model.
* **`values`**: List of integer tuples representing the tensor data.
  

#### Variables

  
    
* static `name  : str`
    
* static `values  : List[Tuple[int, int]]`

      
    

###  SchedulerParams

```python
class SchedulerParams(frequency: int, duration_hours: int)
```

  

  
SchedulerParams(frequency: int, duration_hours: int)
  

#### Static methods

  

### From dict 

```python
def from_dict(data: Optional[Dict[str, int]]) ‑> Optional[opengradient.types.SchedulerParams]
```

  

  

  

#### Variables

  
    
* static `duration_hours  : int`
    
* static `frequency  : int`

  
    
* `end_time  : int`

      
    

###  StreamChoice

```python
class StreamChoice(delta: `StreamDelta`, index: int = 0, finish_reason: Optional[str] = None)
```

  

  
Represents a choice in a streaming response.
  

**Attributes**

* **`delta`**: The incremental changes in this chunk
* **`index`**: Choice index (usually 0)
* **`finish_reason`**: Reason for completion (appears in final chunk)
  

#### Variables

  
    
* static `delta  : opengradient.types.StreamDelta`
    
* static `finish_reason  : Optional[str]`
    
* static `index  : int`

      
    

###  StreamChunk

```python
class StreamChunk(choices: List[`StreamChoice`], model: str, usage: Optional[`StreamUsage`] = None, is_final: bool = False)
```

  

  
Represents a single chunk in a streaming LLM response.

This follows the OpenAI streaming format but is provider-agnostic.
Each chunk contains incremental data, with the final chunk including
usage information.
  

**Attributes**

* **`choices`**: List of streaming choices (usually contains one choice)
* **`model`**: Model identifier
* **`usage`**: Token usage information (only in final chunk)
* **`is_final`**: Whether this is the final chunk (before [DONE])
  

#### Static methods

  

### From sse data 

```python
def from_sse_data(data: Dict) ‑> opengradient.types.StreamChunk
```

  

  
Parse a StreamChunk from SSE data dictionary.
  

**Arguments**

* **`data`**: Dictionary parsed from SSE data line

  
**Returns**

StreamChunk instance

#### Variables

  
    
* static `choices  : List[opengradient.types.StreamChoice]`
    
* static `is_final  : bool`
    
* static `model  : str`
    
* static `usage  : Optional[opengradient.types.StreamUsage]`

      
    

###  StreamDelta

```python
class StreamDelta(content: Optional[str] = None, role: Optional[str] = None, tool_calls: Optional[List[Dict]] = None)
```

  

  
Represents a delta (incremental change) in a streaming response.
  

**Attributes**

* **`content`**: Incremental text content (if any)
* **`role`**: Message role (appears in first chunk)
* **`tool_calls`**: Tool call information (if function calling is used)
  

#### Variables

  
    
* static `content  : Optional[str]`
    
* static `role  : Optional[str]`
    
* static `tool_calls  : Optional[List[Dict]]`

      
    

###  StreamUsage

```python
class StreamUsage(prompt_tokens: int, completion_tokens: int, total_tokens: int)
```

  

  
Token usage information for a streaming response.
  

**Attributes**

* **`prompt_tokens`**: Number of tokens in the prompt
* **`completion_tokens`**: Number of tokens in the completion
* **`total_tokens`**: Total tokens used
  

#### Variables

  
    
* static `completion_tokens  : int`
    
* static `prompt_tokens  : int`
    
* static `total_tokens  : int`

      
    

###  StringTensor

```python
class StringTensor(name: str, values: List[str])
```

  

  
A container for string tensor data used as input for ONNX models.
  

**Attributes**

* **`name`**: Identifier for this tensor in the model.
* **`values`**: List of strings representing the tensor data.
  

#### Variables

  
    
* static `name  : str`
    
* static `values  : List[str]`

      
    

###  TEE_LLM

```python
class TEE_LLM(*args, **kwds)
```

  

  
Enum for LLM models available for TEE (Trusted Execution Environment) execution.

TEE mode provides cryptographic verification that inference was performed
correctly in a secure enclave. Use this for applications requiring
auditability and tamper-proof AI inference.
  

**Note**

The models in TEE_LLM are the same as LLM, but this enum explicitly
indicates support for TEE execution.

#### Variables

  
    
* static `CLAUDE_3_5_HAIKU`
    
* static `CLAUDE_3_7_SONNET`
    
* static `CLAUDE_4_0_SONNET`
    
* static `GEMINI_2_0_FLASH`
    
* static `GEMINI_2_5_FLASH`
    
* static `GEMINI_2_5_FLASH_LITE`
    
* static `GEMINI_2_5_PRO`
    
* static `GPT_4O`
    
* static `GPT_4_1_2025_04_14`
    
* static `GROK_2_1212`
    
* static `GROK_2_VISION_LATEST`
    
* static `GROK_3_BETA`
    
* static `GROK_3_MINI_BETA`
    
* static `GROK_4_1_FAST`
    
* static `GROK_4_1_FAST_NON_REASONING`
    
* static `O4_MINI`

      
    

###  TextGenerationOutput

```python
class TextGenerationOutput(transaction_hash: str, finish_reason: Optional[str] = None, chat_output: Optional[Dict] = None, completion_output: Optional[str] = None, payment_hash: Optional[str] = None)
```

  

  
Output structure for text generation requests.
  

#### Variables

  
    
* static `chat_output  : Optional[Dict]` - Dictionary of chat response containing role, message content, tool call parameters, etc.. Empty dict if not applicable.
    
* static `completion_output  : Optional[str]` - Raw text output from completion-style generation. Empty string if not applicable.
    
* static `finish_reason  : Optional[str]` - Reason for completion (e.g., 'tool_call', 'stop', 'error'). Empty string if not applicable.
    
* static `payment_hash  : Optional[str]` - Payment hash for x402 transaction
    
* static `transaction_hash  : str` - Blockchain hash for the transaction.

      
    

###  TextGenerationStream

```python
class TextGenerationStream(_iterator: Union[Iterator[str], AsyncIterator[str]])
```

  

  
Iterator wrapper for streaming text generation responses.

Provides a clean interface for iterating over stream chunks with
automatic parsing of SSE format.
  

      
    

###  x402SettlementMode

```python
class x402SettlementMode(*args, **kwds)
```

  

  
Settlement modes for x402 payment protocol transactions.

These modes control how inference data is recorded on-chain for payment settlement
and auditability. Each mode offers different trade-offs between data completeness,
privacy, and transaction costs.
  

**Attributes**

* **`SETTLE`**: Individual settlement with input/output hashes only.
        Also known as SETTLE_INDIVIDUAL in some documentation.
        Records cryptographic hashes of the inference input and output.
        Most privacy-preserving option - actual data is not stored on-chain.
        Suitable for applications where only proof of execution is needed.
        CLI usage: --settlement-mode settle
* **`SETTLE_METADATA`**: Individual settlement with full metadata.
        Also known as SETTLE_INDIVIDUAL_WITH_METADATA in some documentation.
        Records complete model information, full input and output data,
        and all inference metadata on-chain.
        Provides maximum transparency and auditability.
        Higher gas costs due to larger data storage.
        CLI usage: --settlement-mode settle-metadata
* **`SETTLE_BATCH`**: Batch settlement for multiple inferences.
        Aggregates multiple inference requests into a single settlement transaction
        using batch hashes.
        Most cost-efficient for high-volume applications.
        Reduced per-inference transaction overhead.
        CLI usage: --settlement-mode settle-batch

  

#### Variables

  
    
* static `SETTLE`
    
* static `SETTLE_BATCH`
    
* static `SETTLE_INDIVIDUAL`
    
* static `SETTLE_INDIVIDUAL_WITH_METADATA`
    
* static `SETTLE_METADATA`