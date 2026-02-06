---
outline: [2,3]
---

  

# Package opengradient.types

## Classes
    

###  Abi

<code>class <b>Abi</b>(functions: List[`AbiFunction`])</code>

  

  
Abi(functions: List[opengradient.types.AbiFunction])
  

  

### From json 

```python
def from_json(abi_json)
```

  

  

  

#### Variables

  
    
* static `functions  : List[opengradient.types.AbiFunction]` - The type of the None singleton.

      
    

###  AbiFunction

<code>class <b>AbiFunction</b>(name: str, inputs: List[Union[str, ForwardRef('`AbiFunction`')]], outputs: List[Union[str, ForwardRef('`AbiFunction`')]], state_mutability: str)</code>

  

  
AbiFunction(name: str, inputs: List[Union[str, ForwardRef('AbiFunction')]], outputs: List[Union[str, ForwardRef('AbiFunction')]], state_mutability: str)
  

#### Variables

  
    
* static `inputs  : List[Union[str, opengradient.types.AbiFunction]]` - The type of the None singleton.
    
* static `name  : str` - The type of the None singleton.
    
* static `outputs  : List[Union[str, opengradient.types.AbiFunction]]` - The type of the None singleton.
    
* static `state_mutability  : str` - The type of the None singleton.

      
    

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

      
    

###  FileUploadResult

<code>class <b>FileUploadResult</b>(modelCid: str, size: int)</code>

  

  
FileUploadResult(modelCid: str, size: int)
  

#### Variables

  
    
* static `modelCid  : str` - The type of the None singleton.
    
* static `size  : int` - The type of the None singleton.

      
    

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

      
    

###  InferenceResult

<code>class <b>InferenceResult</b>(transaction_hash: str, model_output: Dict[str, `ndarray`])</code>

  

  
Output for ML inference requests.
This class has two fields
    transaction_hash (str): Blockchain hash for the transaction
    model_output (Dict[str, np.ndarray]): Output of the ONNX model
  

#### Variables

  
    
* static `model_output  : Dict[str, numpy.ndarray]` - The type of the None singleton.
    
* static `transaction_hash  : str` - The type of the None singleton.

      
    

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

      
    

###  ModelInput

<code>class <b>ModelInput</b>(numbers: List[`NumberTensor`], strings: List[`StringTensor`])</code>

  

  
A collection of tensor inputs required for ONNX model inference.
  

**Attributes**

* **`numbers`**: Collection of numeric tensors for the model.
* **`strings`**: Collection of string tensors for the model.
  

#### Variables

  
    
* static `numbers  : List[opengradient.types.NumberTensor]` - The type of the None singleton.
    
* static `strings  : List[opengradient.types.StringTensor]` - The type of the None singleton.

      
    

###  ModelOutput

<code>class <b>ModelOutput</b>(numbers: Dict[str, `ndarray`], strings: Dict[str, `ndarray`], jsons: Dict[str, `ndarray`], is_simulation_result: bool)</code>

  

  
Model output struct based on translations from smart contract.
  

#### Variables

  
    
* static `is_simulation_result  : bool` - The type of the None singleton.
    
* static `jsons  : Dict[str, numpy.ndarray]` - The type of the None singleton.
    
* static `numbers  : Dict[str, numpy.ndarray]` - The type of the None singleton.
    
* static `strings  : Dict[str, numpy.ndarray]` - The type of the None singleton.

      
    

###  ModelRepository

<code>class <b>ModelRepository</b>(name: str, initialVersion: str)</code>

  

  
ModelRepository(name: str, initialVersion: str)
  

#### Variables

  
    
* static `initialVersion  : str` - The type of the None singleton.
    
* static `name  : str` - The type of the None singleton.

      
    

###  Number

<code>class <b>Number</b>(value: int, decimals: int)</code>

  

  
Number(value: int, decimals: int)
  

#### Variables

  
    
* static `decimals  : int` - The type of the None singleton.
    
* static `value  : int` - The type of the None singleton.

      
    

###  NumberTensor

<code>class <b>NumberTensor</b>(name: str, values: List[Tuple[int, int]])</code>

  

  
A container for numeric tensor data used as input for ONNX models.
  

**Attributes**

* **`name`**: Identifier for this tensor in the model.
* **`values`**: List of integer tuples representing the tensor data.
  

#### Variables

  
    
* static `name  : str` - The type of the None singleton.
    
* static `values  : List[Tuple[int, int]]` - The type of the None singleton.

      
    

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

      
    

###  StreamChoice

<code>class <b>StreamChoice</b>(delta: `StreamDelta`, index: int = 0, finish_reason: Optional[str] = None)</code>

  

  
Represents a choice in a streaming response.
  

**Attributes**

* **`delta`**: The incremental changes in this chunk
* **`index`**: Choice index (usually 0)
* **`finish_reason`**: Reason for completion (appears in final chunk)
  

#### Variables

  
    
* static `delta  : opengradient.types.StreamDelta` - The type of the None singleton.
    
* static `finish_reason  : Optional[str]` - The type of the None singleton.
    
* static `index  : int` - The type of the None singleton.

      
    

###  StreamChunk

<code>class <b>StreamChunk</b>(choices: List[`StreamChoice`], model: str, usage: Optional[`StreamUsage`] = None, is_final: bool = False)</code>

  

  
Represents a single chunk in a streaming LLM response.

This follows the OpenAI streaming format but is provider-agnostic.
Each chunk contains incremental data, with the final chunk including
usage information.
  

**Attributes**

* **`choices`**: List of streaming choices (usually contains one choice)
* **`model`**: Model identifier
* **`usage`**: Token usage information (only in final chunk)
* **`is_final`**: Whether this is the final chunk (before [DONE])
  

  

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

  
    
* static `choices  : List[opengradient.types.StreamChoice]` - The type of the None singleton.
    
* static `is_final  : bool` - The type of the None singleton.
    
* static `model  : str` - The type of the None singleton.
    
* static `usage  : Optional[opengradient.types.StreamUsage]` - The type of the None singleton.

      
    

###  StreamDelta

<code>class <b>StreamDelta</b>(content: Optional[str] = None, role: Optional[str] = None, tool_calls: Optional[List[Dict]] = None)</code>

  

  
Represents a delta (incremental change) in a streaming response.
  

**Attributes**

* **`content`**: Incremental text content (if any)
* **`role`**: Message role (appears in first chunk)
* **`tool_calls`**: Tool call information (if function calling is used)
  

#### Variables

  
    
* static `content  : Optional[str]` - The type of the None singleton.
    
* static `role  : Optional[str]` - The type of the None singleton.
    
* static `tool_calls  : Optional[List[Dict]]` - The type of the None singleton.

      
    

###  StreamUsage

<code>class <b>StreamUsage</b>(prompt_tokens: int, completion_tokens: int, total_tokens: int)</code>

  

  
Token usage information for a streaming response.
  

**Attributes**

* **`prompt_tokens`**: Number of tokens in the prompt
* **`completion_tokens`**: Number of tokens in the completion
* **`total_tokens`**: Total tokens used
  

#### Variables

  
    
* static `completion_tokens  : int` - The type of the None singleton.
    
* static `prompt_tokens  : int` - The type of the None singleton.
    
* static `total_tokens  : int` - The type of the None singleton.

      
    

###  StringTensor

<code>class <b>StringTensor</b>(name: str, values: List[str])</code>

  

  
A container for string tensor data used as input for ONNX models.
  

**Attributes**

* **`name`**: Identifier for this tensor in the model.
* **`values`**: List of strings representing the tensor data.
  

#### Variables

  
    
* static `name  : str` - The type of the None singleton.
    
* static `values  : List[str]` - The type of the None singleton.

      
    

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

      
    

###  TextGenerationOutput

<code>class <b>TextGenerationOutput</b>(transaction_hash: str, finish_reason: Optional[str] = None, chat_output: Optional[Dict] = None, completion_output: Optional[str] = None, payment_hash: Optional[str] = None)</code>

  

  
Output structure for text generation requests.
  

#### Variables

  
    
* static `chat_output  : Optional[Dict]` - Dictionary of chat response containing role, message content, tool call parameters, etc.. Empty dict if not applicable.
    
* static `completion_output  : Optional[str]` - Raw text output from completion-style generation. Empty string if not applicable.
    
* static `finish_reason  : Optional[str]` - Reason for completion (e.g., 'tool_call', 'stop', 'error'). Empty string if not applicable.
    
* static `payment_hash  : Optional[str]` - Payment hash for x402 transaction
    
* static `transaction_hash  : str` - Blockchain hash for the transaction.

      
    

###  TextGenerationStream

<code>class <b>TextGenerationStream</b>(_iterator: Union[Iterator[str], AsyncIterator[str]])</code>

  

  
Iterator wrapper for streaming text generation responses.

Provides a clean interface for iterating over stream chunks with
automatic parsing of SSE format.
  

      
    

###  x402SettlementMode

<code>class <b>x402SettlementMode</b>(*args, **kwds)</code>

  

  
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

  
    
* static `SETTLE` - The type of the None singleton.
    
* static `SETTLE_BATCH` - The type of the None singleton.
    
* static `SETTLE_INDIVIDUAL` - The type of the None singleton.
    
* static `SETTLE_INDIVIDUAL_WITH_METADATA` - The type of the None singleton.
    
* static `SETTLE_METADATA` - The type of the None singleton.