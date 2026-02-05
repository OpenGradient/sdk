# OpenGradient Python SDK

A Python SDK for decentralized model management and inference services on the OpenGradient platform. The SDK enables programmatic access to our model repository and decentralized AI infrastructure.

## Key Features

- Model management and versioning
- Decentralized model inference
- Support for LLM inference with various models
- **Trusted Execution Environment (TEE) inference** with cryptographic attestation
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

## Network Configuration

OpenGradient runs on two networks:
- **Testnet**: The main public testnet for general use
- **Alpha Testnet**: For alpha features like workflow execution (see [Alpha Testnet Features](#alpha-testnet-features))

For the latest network RPCs, contract addresses, and deployment information, see the [Network Deployment Documentation](https://docs.opengradient.ai/learn/network/deployment.html).

## Getting Started

### 1. Account Setup

You'll need:
- **Private key**: An Ethereum-compatible wallet private key for OpenGradient transactions
- **Model Hub account** (optional): Only needed for uploading models. Create one at [Hub Sign Up](https://hub.opengradient.ai/signup)

The easiest way to set up your configuration is through our wizard:
```bash
opengradient config init
```

### 2. Initialize the Client
```python
import os
import opengradient as og

og_client = og.new_client(
    email=None,  # Optional: only needed for model uploads
    password=None,
    private_key=os.environ.get("OG_PRIVATE_KEY"),
)
```

### 3. Basic Usage

#### LLM Chat
```python
completion = og_client.llm_chat(
    model_cid=og.TEE_LLM.GPT_4O,
    messages=[{"role": "user", "content": "Hello!"}],
    inference_mode=og.LlmInferenceMode.TEE,
)
print(f"Response: {completion.chat_output['content']}")
print(f"Tx hash: {completion.transaction_hash}")
```

#### Custom Model Inference
Browse models on our [Model Hub](https://hub.opengradient.ai/) or upload your own:
```python
result = og_client.infer(
    model_cid="your-model-cid",
    model_input={"input": [1.0, 2.0, 3.0]},
    inference_mode=og.InferenceMode.VANILLA,
)
print(f"Output: {result.model_output}")
```

### 4. TEE (Trusted Execution Environment) Inference

OpenGradient supports secure, verifiable inference through TEE for leading LLM providers. Access models from OpenAI, Anthropic, Google, and xAI with cryptographic attestation:
```python
# Use TEE mode for verifiable AI execution
completion = og_client.llm_chat(
    model_cid=og.TEE_LLM.CLAUDE_3_7_SONNET,
    messages=[{"role": "user", "content": "Your message here"}],
    inference_mode=og.LlmInferenceMode.TEE,
)
print(f"Response: {completion.chat_output['content']}")
```

**Available TEE Models:**
The SDK includes models from multiple providers accessible via the `og.TEE_LLM` enum:
- **OpenAI**: GPT-4.1, GPT-4o, o4-mini
- **Anthropic**: Claude 3.7 Sonnet, Claude 3.5 Haiku, Claude 4.0 Sonnet
- **Google**: Gemini 2.5 Flash, Gemini 2.5 Pro, Gemini 2.0 Flash
- **xAI**: Grok 3 Beta, Grok 3 Mini Beta, Grok 4.1 Fast

For the complete list, check the `og.TEE_LLM` enum in your IDE or see the [API documentation](https://docs.opengradient.ai/).

### 5. Alpha Testnet Features

The Alpha Testnet provides access to experimental features, including **workflow deployment and execution**. Workflows allow you to deploy on-chain AI pipelines that connect models with data sources and can be scheduled for automated execution.

**Note:** Alpha features require connecting to the Alpha Testnet. See [Network Configuration](#network-configuration) for details.

#### Deploy a Workflow
```python
import opengradient as og

og.init(
    email="your-email",
    password="your-password",
    private_key="your-private-key",
)

# Define input query for historical price data
input_query = og.HistoricalInputQuery(
    base="ETH",
    quote="USD",
    total_candles=10,
    candle_duration_in_mins=60,
    order=og.CandleOrder.DESCENDING,
    candle_types=[og.CandleType.CLOSE],
)

# Deploy a workflow (optionally with scheduling)
contract_address = og.alpha.new_workflow(
    model_cid="your-model-cid",
    input_query=input_query,
    input_tensor_name="input",
    scheduler_params=og.SchedulerParams(frequency=3600, duration_hours=24),  # Optional
)
print(f"Workflow deployed at: {contract_address}")
```

#### Execute and Read Results
```python
# Manually trigger workflow execution
result = og.alpha.run_workflow(contract_address)
print(f"Inference output: {result}")

# Read the latest result
latest = og.alpha.read_workflow_result(contract_address)

# Get historical results
history = og.alpha.read_workflow_history(contract_address, num_results=5)
```

### 6. Examples

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

2. **Verifiable AI Execution**: Leverage TEE inference for cryptographically attested AI outputs, enabling trustless AI applications.

3. **Model Development**: Manage models on the Model Hub and integrate directly into your development workflow.

## Documentation

For comprehensive documentation, API reference, and examples, visit:
- [OpenGradient Documentation](https://docs.opengradient.ai/)
- [API Reference](https://docs.opengradient.ai/api_reference/python_sdk/)

### Claude Code Users

If you use [Claude Code](https://claude.ai/code), copy [docs/CLAUDE_SDK_USERS.md](docs/CLAUDE_SDK_USERS.md) to your project's `CLAUDE.md` to help Claude assist you with OpenGradient SDK development.

## Support

- Run `opengradient --help` for CLI command reference
- Visit our [documentation](https://docs.opengradient.ai/) for detailed guides
- Join our [community](https://opengradient.ai/) for support
