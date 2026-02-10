---
outline: [2,3]
---

[opengradient](../index) / [client](./index) / twins

# Package opengradient.client.twins

Digital twins chat via OpenGradient verifiable inference.

## Classes

### `Twins`

Digital twins chat namespace.

Provides access to digital twin conversations from twin.fun,
backed by OpenGradient verifiable inference.

#### Constructor

```python
def __init__(api_key: str)
```

#### Methods

---

#### `chat()`

```python
def chat(self, twin_id: str, model: `TEE_LLM`, messages: List[Dict], temperature: Optional[float] = None, max_tokens: Optional[int] = None) ‑> `TextGenerationOutput`
```
Chat with a digital twin.

**Arguments**

* **`twin_id`**: The unique identifier of the digital twin.
* **`model`**: The model to use for inference (e.g., TEE_LLM.GROK_4_1_FAST_NON_REASONING).
* **`messages`**: The conversation messages to send.
* **`temperature`**: Sampling temperature. Optional.
* **`max_tokens`**: Maximum number of tokens for the response. Optional.

**Returns**

TextGenerationOutput: Generated text results including chat_output and finish_reason.

**Raises**

* **`OpenGradientError`**: If the request fails.