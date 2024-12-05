# OpenGradient Python SDK
Python SDK for the OpenGradient platform provides decentralized model management & inference services. Python SDK allows programmatic access to our model repository and decentralized AI infrastructure. 

## Installation

To install Python SDK and CLI, run the following command:
```python
pip install opengradient
```

## Quick Start

To get started, run:

```python
import opengradient as og
og.init(private_key="<private_key>", email="<email>", password="<password>")
```

The following commands show how to use Python SDK.

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
 - inference mode can be `VANILLA`, `ZKML`, or `TEE`

### LLM Inference
#### LLM Completion
```python
tx_hash, response = og.llm_completion(
    model_cid='meta-llama/Meta-Llama-3-8B-Instruct',
    prompt="Translate the following English text to French: 'Hello, how are you?'",
    max_tokens=50,
    temperature=0.0
)
``` 

#### LLM Chat
```python
# create messages history
messages = [
    {
        "role": "system",
        "content": "You are a helpful AI assistant.",
        "name": "HAL"
    },
    {
        "role": "user",
        "content": "Hello! How are you doing? Can you repeat my name?",
    }]

# run LLM inference
tx_hash, finish_reason, message = og.llm_chat(
  model_cid=og.LLM.MISTRAL_7B_INSTRUCT_V3,
  messages=messages
)
```



## Using the CLI

```bash
export OPENGRADIENT_EMAIL="<email>"
export OPENGRADIENT_PASSWORD="<password>"
```

#### Creating a Model Repo
```bash
opengradient create_model_repo "<model_name>" "<description>" 
```
- creating a model automatically initializes version `v0.01`

#### Creating a Version
```bash
opengradient create_model_repo "<model_name>" "<description>" 
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

#### Run LLM Inference
We also have explicit support for using LLMs through the completion and chat commands in the CLI.

For example, you can run a competion inference with Llama-3 using the following command:

``` bash
opengradient completion --model "meta-llama/Meta-Llama-3-8B-Instruct" --prompt "hello who are you?" --max-tokens 50
```

Or you can use files instead of text input in order to simplify your command:

```bash
opengradient chat --model "mistralai/Mistral-7B-Instruct-v0.3" --messages-file messages.json --tools-file tools.json --max-tokens 200
```

For more information read the OpenGradient [documentation](https://docs.opengradient.ai/).