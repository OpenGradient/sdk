---
outline: [2,3]
---

  

# Package opengradient.client

## Submodules

* [alpha](docs/client.md#alpha): Alpha Testnet features for OpenGradient SDK.
* [client](docs/client.md#client): 
* [exceptions](docs/client.md#exceptions): 
* [llm](docs/client.md#llm): 
* [model_hub](docs/client.md#model_hub): 
* [onchain_inference](docs/client.md#onchain_inference): 
* [x402_auth](docs/client.md#x402_auth): X402 Authentication handler for httpx streaming requests.

## Classes
    

###  Client

<code>class <b>Client</b>(private_key: str, email: Optional[str] = None, password: Optional[str] = None, rpc_url: str = 'https://ogevmdevnet.opengradient.ai', api_url: str = 'https://sdk-devnet.opengradient.ai', contract_address: str = '0x8383C9bD7462F12Eb996DD02F78234C0421A6FaE', og_llm_server_url: Optional[str] = 'https://llmogevm.opengradient.ai', og_llm_streaming_server_url: Optional[str] = 'https://llmogevm.opengradient.ai')</code>

  

  
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