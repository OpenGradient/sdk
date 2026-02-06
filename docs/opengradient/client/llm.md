---
outline: [2,3]
---

  

# Package opengradient.client.llm

LLM chat and completion via TEE-verified execution with x402 payments.

## Classes
    

###  LLM

<code>class <b>LLM</b>(wallet_account: `LocalAccount`, og_llm_server_url: str, og_llm_streaming_server_url: str)</code>

  

  
LLM inference namespace.

Provides access to large language model completions and chat via TEE
(Trusted Execution Environment) with x402 payment protocol support.
Supports both streaming and non-streaming responses.
  

  

### Chat 

```python
def chat(self, model: opengradient.types.TEE_LLM, messages: List[Dict], max_tokens: int = 100, stop_sequence: Optional[List[str]] = None, temperature: float = 0.0, tools: Optional[List[Dict]] = [], tool_choice: Optional[str] = None, x402_settlement_mode: Optional[opengradient.types.x402SettlementMode] = x402SettlementMode.SETTLE_BATCH, stream: bool = False) ‑> Union[opengradient.types.TextGenerationOutput, opengradient.types.TextGenerationStream]
```

  

  
Perform inference on an LLM model using chat via TEE.
  

**Returns**

Union[TextGenerationOutput, TextGenerationStream]:
    - If stream=False: TextGenerationOutput with chat_output, transaction_hash, finish_reason, and payment_hash
    - If stream=True: TextGenerationStream yielding StreamChunk objects with typed deltas (true streaming via threading)

**Raises**

* **`OpenGradientError`**: If the inference fails.
  

  

### Completion 

```python
def completion(self, model: opengradient.types.TEE_LLM, prompt: str, max_tokens: int = 100, stop_sequence: Optional[List[str]] = None, temperature: float = 0.0, x402_settlement_mode: Optional[opengradient.types.x402SettlementMode] = x402SettlementMode.SETTLE_BATCH) ‑> opengradient.types.TextGenerationOutput
```

  

  
Perform inference on an LLM model using completions via TEE.
  

**Returns**

TextGenerationOutput: Generated text results including:
    - Transaction hash ("external" for TEE providers)
    - String of completion output
    - Payment hash for x402 transactions

**Raises**

* **`OpenGradientError`**: If the inference fails.