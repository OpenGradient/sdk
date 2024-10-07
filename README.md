# OpenGradient Python SDK

Python SDK for OpenGradient inference services.

## Installation
```python
pip install opengradient
```

## Quick Start
```python
import opengradient as og
og.init(private_key="x", rpc_url="y", contract_address="z")
```

### Sign in with Email
```python
og.login(email="you@opengradient.ai", password="xyz")
```

### Create a Model
```python
og.create_model(model_name="test-network-model", model_desc="testing upload to sdk")
```

### Create a Version of a Model
```python
og.create_version(model_name="test-network-model", notes="test notes")
```

### Upload Files to a Model
```python
og.upload(model_path="local_path_to_your_model.onnx", model_name="test-network-model", version="0.01")
```

### Run Inference
```python
inference_mode = og.InferenceMode.VANILLA
inference_cid = og.infer(model_cid, model_inputs, inference_mode)
```

```python
og.infer(model_id, inference_mode, model_input)
```

## Using the CLI

#### Creating a Model
```bash
opengradient create_model "<model_name>" "<description>" 
```
- creating a model automatically initializes version `v0.01`

#### Creating a Version
```bash
opengradient create_model "<model_name>" "<description>" 
```

#### Upload a File
```bash
opengradient upload "path/to/model.onnx" "<model_name>" "<version>" 
```

####  CLI infer using string 
```bash
opengradient infer QmbUqS93oc4JTLMHwpVxsE39mhNxy6hpf6Py3r9oANr8aZ VANILLA '{"num_input1":[1.0, 2.0, 3.0], "num_input2":10, "str_input1":["hello", "ONNX"], "str_input2":" world"}'
```

#### CLI infer using file path input
```bash
opengradient infer QmbUqS93oc4JTLMHwpVxsE39mhNxy6hpf6Py3r9oANr8aZ VANILLA --input_file input.json
```