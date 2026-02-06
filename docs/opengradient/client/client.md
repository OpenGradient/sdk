---
outline: [2,3]
---

  

# Package opengradient.client.client

Main Client class that unifies all OpenGradient service namespaces.

## Classes
    

### Client

```python
class Client
```

  

  
Main OpenGradient SDK client.

Provides unified access to all OpenGradient services including LLM inference,
on-chain model inference, and the Model Hub. Handles authentication via
blockchain private key and optional Model Hub credentials.
  

**Arguments**

* **`private_key`**: Private key for OpenGradient transactions.
* **`email`**: Email for Model Hub authentication. Optional.
* **`password`**: Password for Model Hub authentication. Optional.
* **`rpc_url`**: RPC URL for the blockchain network.
* **`api_url`**: API URL for the OpenGradient API.
* **`contract_address`**: Inference contract address.
* **`og_llm_server_url`**: OpenGradient LLM server URL.
* **`og_llm_streaming_server_url`**: OpenGradient LLM streaming server URL.
  

#### Constructor

```python
def __init__(private_key: str, email: Optional[str] = None, password: Optional[str] = None, rpc_url: str = 'https://ogevmdevnet.opengradient.ai', api_url: str = 'https://sdk-devnet.opengradient.ai', contract_address: str = '0x8383C9bD7462F12Eb996DD02F78234C0421A6FaE', og_llm_server_url: Optional[str] = 'https://llmogevm.opengradient.ai', og_llm_streaming_server_url: Optional[str] = 'https://llmogevm.opengradient.ai')
```

#### Variables

  
    
* static `inference  : opengradient.client.onchain_inference.Inference`
    
* static `llm  : opengradient.client.llm.LLM`
    
* static `model_hub  : opengradient.client.model_hub.ModelHub`

  
    
* `alpha` - Access Alpha Testnet features.

  Returns:
    Alpha: Alpha namespace with workflow and ML model execution methods.

  Example:
    client = og.Client(...)
    result = client.alpha.new_workflow(model_cid, input_query, input_tensor_name)