# OpenGradient SDK Examples

This directory contains example scripts demonstrating how to use the OpenGradient Python SDK for various use cases, from basic model operations to advanced agent integrations.

## Prerequisites

Before running any examples, ensure you have:

1. **Installed the SDK**: `pip install opengradient`
2. **Set up your credentials**: Configure your OpenGradient account using environment variables:
   - `OG_PRIVATE_KEY`: Your Ethereum private key for OpenGradient
   - `OG_MODEL_HUB_EMAIL`: (Optional) Your Model Hub email for model uploads
   - `OG_MODEL_HUB_PASSWORD`: (Optional) Your Model Hub password for model uploads
   - `GOOGLE_API_KEY`: (Optional) Required for third-party LLM examples

You can also use the configuration wizard:
```bash
opengradient config init
```

## Basic Usage Examples

### Model Management

#### `create_model.py`
Creates a new model repository on the Model Hub.

```bash
python examples/create_model.py
```

**What it does:**
- Creates a new model repository with a name and description
- Returns a model repository object with version information

#### `upload_model.py`
Uploads a model file to an existing model repository.

```bash
python examples/upload_model.py
```

**What it does:**
- Creates a model repository (or uses an existing one)
- Uploads an ONNX model file to the repository
- Returns the model CID (Content Identifier) for use in inference

**Note:** Requires Model Hub credentials (`OG_MODEL_HUB_EMAIL` and `OG_MODEL_HUB_PASSWORD`).

### Inference Examples

#### `run_inference.py`
Runs inference on a custom model using the OpenGradient network.

```bash
python examples/run_inference.py
```

**What it does:**
- Executes inference on a model using its CID
- Demonstrates passing structured input data (e.g., OHLC price data)
- Returns model predictions along with the transaction hash

**Example use case:** Running predictions on financial models, forecasting models, etc.

#### `run_llm.py`
Runs inference on a hosted LLM model.

```bash
python examples/run_llm.py
```

**What it does:**
- Sends a chat message to a hosted LLM (e.g., Dobby Unhinged)
- Demonstrates the chat completion interface
- Returns the LLM response and transaction hash

**Example use case:** Chatbots, text generation, conversational AI.

#### `run_embeddings_model.py`
Runs inference on an embeddings model for semantic search.

```bash
python examples/run_embeddings_model.py
```

**What it does:**
- Generates embeddings for queries and passages
- Demonstrates multilingual embeddings models
- Useful for semantic search, retrieval-augmented generation (RAG), etc.

**Example use case:** Building search systems, RAG applications, similarity matching.

## Workflow Examples

Workflows enable scheduled, automated model inference with historical data integration.

#### `create_workflow.py`
Creates a new scheduled workflow for automated model inference.

```bash
python examples/create_workflow.py
```

**What it does:**
- Defines a workflow that runs a model on a schedule
- Configures historical data queries (e.g., cryptocurrency price data)
- Deploys the workflow as a smart contract
- Returns the contract address for the workflow

**Example use case:** Automated trading signals, scheduled forecasting, monitoring systems.

#### `use_workflow.py`
Reads results from a deployed workflow.

```bash
python examples/use_workflow.py
```

**What it does:**
- Retrieves the latest prediction from a workflow contract
- Fetches historical predictions from the workflow
- Demonstrates how to consume workflow outputs

**Example use case:** Reading automated predictions, monitoring workflow performance.

## Third-Party LLM Examples

These examples show how to use OpenGradient as a router for third-party LLM providers.

#### `run_third_party_llm.py`
Runs inference through OpenGradient routers for third-party LLMs (Gemini, Anthropic, OpenAI).

```bash
python examples/run_third_party_llm.py
```

**What it does:**
- Demonstrates completion and chat interfaces for third-party models
- Uses OpenGradient routers to access models like Gemini
- Requires `GOOGLE_API_KEY` environment variable

**Note:** Requires `opengradient==0.5.0a2` or compatible version.

#### `run_x402_llm.py`
Runs LLM inference with x402 transaction processing.

```bash
python examples/run_x402_llm.py
```

**What it does:**
- Uses x402 protocol for payment processing
- Currently supports `gpt-4.1-2025-04-14` model
- Returns payment hash instead of transaction hash

**Note:** Requires `opengradient==0.5.0a3` or compatible version.

## LangChain Agent Examples

These examples demonstrate integrating OpenGradient models and workflows into LangChain agents for building AI applications.

#### `agents/langchain_llm.py`
Creates a basic LangChain agent using an OpenGradient LLM.

```bash
python examples/agents/langchain_llm.py
```

**What it does:**
- Sets up a LangGraph ReAct agent with an OpenGradient LLM
- Demonstrates basic agent functionality
- Shows how to stream agent responses

**Example use case:** Building conversational agents, task automation.

#### `agents/langchain_run_model.py`
Creates a LangChain agent with a custom model inference tool.

```bash
python examples/agents/langchain_run_model.py
```

**What it does:**
- Integrates a custom model (e.g., volatility forecaster) as a LangChain tool
- Agent can call the model tool to answer questions
- Demonstrates model input providers and output formatters

**Example use case:** Agents that need to run predictions, financial analysis agents.

#### `agents/langchain_run_model_with_schema.py`
Creates a LangChain agent with a model tool that accepts structured input.

```bash
python examples/agents/langchain_run_model_with_schema.py
```

**What it does:**
- Defines a Pydantic schema for tool inputs
- Agent can pass structured parameters to the model tool
- Demonstrates dynamic model input based on agent decisions

**Example use case:** Multi-parameter models, conditional inference, complex agent workflows.

#### `agents/langchain_use_workflow.py`
Creates a LangChain agent that reads from deployed workflows.

```bash
python examples/agents/langchain_use_workflow.py
```

**What it does:**
- Integrates workflow results as a LangChain tool
- Agent can query workflow predictions
- Demonstrates reading from on-chain workflows

**Example use case:** Agents that monitor automated systems, reporting agents.

## Common Patterns

### Initializing the Client

All examples use a similar pattern to initialize the OpenGradient client:

```python
import os
import opengradient as og

og_client = og.new_client(
    email=os.environ.get("OG_MODEL_HUB_EMAIL"),
    password=os.environ.get("OG_MODEL_HUB_PASSWORD"),
    private_key=os.environ.get("OG_PRIVATE_KEY")
)
```

### Running Inference

Basic inference pattern:

```python
result = og_client.infer(
    model_cid="your-model-cid",
    model_input={"input_key": "input_value"},
    inference_mode=og.InferenceMode.VANILLA
)
print(f"Output: {result.model_output}")
print(f"Tx hash: {result.transaction_hash}")
```

### LLM Chat

LLM chat pattern:

```python
completion = og_client.llm_chat(
    model_cid=og.LLM.DOBBY_UNHINGED_3_1_8B,
    messages=[{"role": "user", "content": "Your message"}],
    inference_mode=og.LlmInferenceMode.VANILLA
)
print(f"Response: {completion.chat_output['content']}")
```

## Finding Model CIDs

Browse available models on the [OpenGradient Model Hub](https://hub.opengradient.ai/). Each model has a CID that you can use in your code.

## Additional Resources

- [OpenGradient Documentation](https://docs.opengradient.ai/)
- [API Reference](https://docs.opengradient.ai/api_reference/python_sdk/)
- [Model Hub](https://hub.opengradient.ai/)

## Getting Help

- Run `opengradient --help` for CLI command reference
- Visit our [documentation](https://docs.opengradient.ai/) for detailed guides
- Check the main [README](../README.md) for SDK overview

