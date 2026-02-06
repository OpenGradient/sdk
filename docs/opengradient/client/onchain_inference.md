---
outline: [2,3]
---

[opengradient](../index) / [client](./index) / onchain_inference

# Package opengradient.client.onchain_inference

On-chain ONNX model inference via blockchain smart contracts.

## Classes

### `Inference`

On-chain model inference namespace.

Provides access to decentralized ONNX model inference via blockchain smart contracts.
Supports multiple inference modes including VANILLA, TEE, and ZKML.

#### Constructor

```python
def __init__(blockchain: `Web3`, wallet_account: `LocalAccount`, inference_hub_contract_address: str, api_url: str)
```

#### Methods

---

#### `infer()`

```python
def infer(self, model_cid: str, inference_mode: `InferenceMode`, model_input: Dict[str, Union[str, int, float, List, `ndarray`]], max_retries: Optional[int] = None) ‑> `InferenceResult`
```
Perform inference on a model.

**Arguments**

* **`model_cid (str)`**: The unique content identifier for the model from IPFS.
* **`inference_mode (InferenceMode)`**: The inference mode.
* **`model_input (Dict[str, Union[str, int, float, List, np.ndarray]])`**: The input data for the model.
* **`max_retries (int, optional)`**: Maximum number of retry attempts. Defaults to 5.

**Returns**

InferenceResult (InferenceResult): A dataclass object containing the transaction hash and model output.
    transaction_hash (str): Blockchain hash for the transaction
    model_output (Dict[str, np.ndarray]): Output of the ONNX model

**Raises**

* **`OpenGradientError`**: If the inference fails.

#### Variables

* `inference_abi` : dict
* `precompile_abi` : dict