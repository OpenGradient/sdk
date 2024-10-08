# OpenGradient SDK

Python SDK for OpenGradient decentralized model management & inference services.

## Installation
```python
pip install opengradient
```

## Quick Start
```python
import opengradient as og
og.init(email="<email>", password="<password>")
```

### Create a Model
```python
og.create_model(model_name="<model_name>", model_desc="<model_description>")
```

### Create a Model (with file upload)
```python
og.create_model(model_name="<model_name>", model_desc="<model_description>", model_path="<model_path>")
```

### Create a Version of a Model
```python
og.create_version(model_name="<model_name>", notes="<model_notes>")
```

### Upload Files to a Model
```python
og.upload(model_path="<model_path>", model_name="<model_name>", version="<version>")
```

### List Files of a Model Version
```python
og.list_files(model_name="<model_name>", version="<version>")
```

### Run Inference
```python
inference_mode = og.InferenceMode.VANILLA
og.infer(model_cid, model_inputs, inference_mode)
```

## Using the CLI

```bash
export OPENGRADIENT_EMAIL="<email>"
export OPENGRADIENT_PASSWORD="<password>"
```

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
opengradient upload "<model_path>" "<model_name>" "<version>" 
```

#### List Files of a Model Version
```bash
opengradient list_files "<model_name>" "<version>"
```

####  CLI infer using string 
```bash
opengradient infer QmbUqS93oc4JTLMHwpVxsE39mhNxy6hpf6Py3r9oANr8aZ VANILLA '{"num_input1":[1.0, 2.0, 3.0], "num_input2":10, "str_input1":["hello", "ONNX"], "str_input2":" world"}'
```

#### CLI infer using file path input
```bash
opengradient infer QmbUqS93oc4JTLMHwpVxsE39mhNxy6hpf6Py3r9oANr8aZ VANILLA --input_file input.json
```