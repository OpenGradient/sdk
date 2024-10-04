# OpenGradient Python SDK

Python SDK for OpenGradient inference services.

## Installation
```
pip install opengradient
```

## Quick Start
```
import opengradient as og
og.init(private_key="x", rpc_url="y", contract_address="z")
```

### Sign in with Email
```
og.login(email="you@opengradient.ai", password="xyz")
```

### Create a Model
```
og.create_model(model_name="test-network-model", model_desc="testing upload to sdk")
```

### Create a Version of a Model
```
og.create_version(model_name="test-network-model", notes="test notes")
```

### Upload Files to a Model
```
og.upload(model_path="local_path_to_your_model.onnx", model_name="test-network-model", version="0.01")
```

### Run Inference
```
inference_mode = og.InferenceMode.VANILLA
inference_cid = og.infer(model_cid, model_inputs, inference_mode)
```

```
og.infer(model_id, inference_mode, model_input)
```