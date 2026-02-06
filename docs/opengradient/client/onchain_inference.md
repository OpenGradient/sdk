---
outline: [2,3]
---

  

# Package opengradient.client.onchain_inference

## Classes
    

###  Inference

<code>class <b>Inference</b>(blockchain: [Web3](docs/main.md#Web3), wallet_account: [local](docs/signers.md#local), inference_hub_contract_address: str, api_url: str)</code>

  

  
On-chain model inference namespace.

Provides access to decentralized ONNX model inference via blockchain smart contracts.
Supports multiple inference modes including VANILLA, TEE, and ZKML.
  

  

### Infer 

```python
def infer(self, model_cid: str, inference_mode: opengradient.types.InferenceMode, model_input: Dict[str, Union[str, int, float, List, numpy.ndarray]], max_retries: Optional[int] = None) ‑> opengradient.types.InferenceResult
```

  

  
Perform inference on a model.
  

**Returns**

InferenceResult (InferenceResult): A dataclass object containing the transaction hash and model output.
    transaction_hash (str): Blockchain hash for the transaction
    model_output (Dict[str, np.ndarray]): Output of the ONNX model

**Raises**

* **`OpenGradientError`**: If the inference fails.
  

#### Variables

  
    
* `inference_abi  : dict`
    
* `precompile_abi  : dict`