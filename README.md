# OpenGradient Python SDK

A Python SDK for decentralized model management and inference services on the OpenGradient platform. The SDK enables programmatic access to our model repository and decentralized AI infrastructure.

## Key Features

- Model management and versioning
- Decentralized model inference
- Support for LLM inference with various models
- End-to-end verified AI execution
- Command-line interface (CLI) for direct access

## Model Hub

Browse and discover AI models on our [Model Hub](https://hub.opengradient.ai/). The Hub provides:
- Registry of models and LLMs
- Easy model discovery and deployment
- Direct integration with the SDK

## Installation

```bash
pip install opengradient
```

Note: Windows users should temporarily enable WSL when installing `opengradient` (fix in progress).

## Getting Started

### 1. Account Setup

You'll need two accounts to use the SDK:
- **Model Hub account**: Create one at [Hub Sign Up](https://hub.opengradient.ai/signup)
- **OpenGradient account**: Use an existing Ethereum-compatible wallet or create a new one via SDK

The easiest way to set up your accounts is through our configuration wizard:

```bash
opengradient config init
```

This wizard will:
- Guide you through account creation
- Help you set up credentials
- Direct you to our Test Faucet for devnet tokens

### 2. Initialize the SDK

```python
import opengradient as og
og.init(private_key="<private_key>", email="<email>", password="<password>")
```

### 3. Basic Usage

Browse available models on our [Model Hub](https://hub.opengradient.ai/) or create and upload your own:


```python
# Create and upload a model
og.create_model(
    model_name="my-model",
    model_desc="Model description",
    model_path="/path/to/model"
)

# Run inference
inference_mode = og.InferenceMode.VANILLA
result = og.infer(
    model_cid="your-model-cid",
    model_inputs={"input": "value"},
    inference_mode=inference_mode
)
```

### 4. Examples

See code examples under [examples](./examples).

## CLI Usage

The SDK includes a command-line interface for quick operations. First, verify your configuration:

```bash
opengradient config show
```

Run a test inference:

```bash
opengradient infer -m QmbUqS93oc4JTLMHwpVxsE39mhNxy6hpf6Py3r9oANr8aZ \
    --input '{"num_input1":[1.0, 2.0, 3.0], "num_input2":10}'
```

## Use Cases

1. **Off-chain Applications**: Use OpenGradient as a decentralized alternative to centralized AI providers like HuggingFace and OpenAI.

2. **Model Development**: Manage models on the Model Hub and integrate directly into your development workflow.

## Documentation

For comprehensive documentation, API reference, and examples, visit:
- [OpenGradient Documentation](https://docs.opengradient.ai/)
- [API Reference](https://docs.opengradient.ai/api_reference/python_sdk/)

## Support

- Run `opengradient --help` for CLI command reference
- Visit our [documentation](https://docs.opengradient.ai/) for detailed guides
- Join our [community](https://.opengradient.ai/) for support
