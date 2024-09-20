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
og.sign_in_with_email_and_password(email="test@test.com", password="Test-123")
```

### Create a Model
```
og.create_model("test-network-model-5", "testing sdk")
```

### Create a Version of a Model
```
og.create_version(model_id=11, notes="test notes")
```

### Upload Files to a Model
```
og.upload(model_path, model_id, version=2)
```

### Run Inference
```
inference_mode = og.InferenceMode.VANILLA
inference_cid = og.infer(model_cid, model_inputs, inference_mode)
```

```
og.infer(model_id, inference_mode, model_input)
```