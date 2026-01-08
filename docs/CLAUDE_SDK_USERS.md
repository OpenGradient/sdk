# OpenGradient SDK - Claude Code Guide

> **For SDK Users**: Copy this file to your project's `CLAUDE.md` to help Claude Code assist you with OpenGradient SDK development.

## Overview

OpenGradient SDK provides decentralized AI inference with optional cryptographic verification (TEE mode). It supports LLM chat/completions, ONNX model inference, and scheduled workflows.

## Installation

```bash
pip install opengradient
```

## Quick Start

```python
import opengradient as og
import os

# Initialize client
client = og.new_client(
    private_key=os.environ["OG_PRIVATE_KEY"],  # Required: Ethereum private key
    openai_api_key=os.environ.get("OPENAI_API_KEY"),  # Optional: for OpenAI models
    anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),  # Optional: for Claude
)

# LLM Chat
result = client.llm_chat(
    model_cid="gpt-4o",  # or og.LLM.CLAUDE_3_5_HAIKU
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=100,
)
print(result.chat_output["content"])
```

## Core API Reference

### Client Initialization

```python
# Option 1: Create client instance (recommended)
client = og.new_client(
    private_key="0x...",           # Required: Ethereum private key
    email=None,                    # Optional: Model Hub auth
    password=None,                 # Optional: Model Hub auth
    openai_api_key=None,           # Optional: OpenAI access
    anthropic_api_key=None,        # Optional: Anthropic access
    google_api_key=None,           # Optional: Google access
)

# Option 2: Global initialization
og.init(private_key="0x...", email="...", password="...")
```

### LLM Chat

```python
result = client.llm_chat(
    model_cid: str,                    # Model ID or og.LLM enum
    messages: List[Dict],              # [{"role": "user", "content": "..."}]
    max_tokens: int = 100,
    temperature: float = 0.0,
    tools: List[Dict] = [],            # Optional: function calling
    tool_choice: str = None,           # "auto", "none", or specific tool
    inference_mode: og.LlmInferenceMode = og.LlmInferenceMode.VANILLA,
)
# Returns: TextGenerationOutput
#   - chat_output: Dict with role, content, tool_calls
#   - transaction_hash: str
#   - finish_reason: str ("stop", "tool_call")
```

### LLM Completion

```python
result = client.llm_completion(
    model_cid: str,
    prompt: str,
    max_tokens: int = 100,
    temperature: float = 0.0,
    stop_sequence: List[str] = None,
    inference_mode: og.LlmInferenceMode = og.LlmInferenceMode.VANILLA,
)
# Returns: TextGenerationOutput
#   - completion_output: str (raw text)
#   - transaction_hash: str
```

### ONNX Model Inference

```python
result = client.infer(
    model_cid: str,                    # IPFS CID of model
    model_input: Dict[str, Any],       # Input tensors
    inference_mode: og.InferenceMode = og.InferenceMode.VANILLA,
)
# Returns: InferenceResult
#   - model_output: Dict[str, np.ndarray]
#   - transaction_hash: str
```

## Available Models

### TEE-Verified Models (og.LLM and og.TEE_LLM)

All models are now TEE-verified. The following models are available:

```python
# OpenAI
og.TEE_LLM.GPT_4_1_2025_04_14
og.TEE_LLM.GPT_4O
og.TEE_LLM.O4_MINI

# Anthropic
og.TEE_LLM.CLAUDE_3_7_SONNET
og.TEE_LLM.CLAUDE_3_5_HAIKU
og.TEE_LLM.CLAUDE_4_0_SONNET

# Google
og.TEE_LLM.GEMINI_2_5_FLASH
og.TEE_LLM.GEMINI_2_5_PRO

# xAI
og.TEE_LLM.GROK_3_BETA
og.TEE_LLM.GROK_3_MINI_BETA
```

### External Providers (by string)

```python
"gpt-4o", "gpt-4-turbo"        # OpenAI
"claude-3-sonnet"              # Anthropic
"gemini-2-5-pro"               # Google
```

## Common Patterns

### Tool/Function Calling

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
        }
    }
}]

result = client.llm_chat(
    model_cid=og.LLM.CLAUDE_3_7_SONNET,
    messages=[{"role": "user", "content": "What's the weather in NYC?"}],
    tools=tools,
    tool_choice="auto",
)

if result.chat_output.get("tool_calls"):
    for call in result.chat_output["tool_calls"]:
        print(f"Call {call['name']} with {call['arguments']}")
```

### TEE Verified Inference

```python
# Use TEE mode for cryptographic proof of execution
result = client.llm_chat(
    model_cid=og.TEE_LLM.GPT_4O,
    messages=[{"role": "user", "content": "Hello"}],
    inference_mode=og.LlmInferenceMode.TEE,
)
```

### LangChain Integration

```python
from langgraph.prebuilt import create_react_agent

# Create LangChain-compatible LLM
llm = og.llm.langchain_adapter(
    private_key=os.environ["OG_PRIVATE_KEY"],
    model_cid=og.LLM.CLAUDE_3_7_SONNET,
    max_tokens=300,
)

# Use with LangChain agents
agent = create_react_agent(model=llm, tools=[...])
for chunk in agent.stream({"messages": [("user", "Your question")]}):
    print(chunk)
```

### Scheduled Workflows

```python
# Define data input
input_query = og.HistoricalInputQuery(
    base="ETH",
    quote="USD",
    total_candles=10,
    candle_duration_in_mins=30,
    order=og.CandleOrder.ASCENDING,
    candle_types=[og.CandleType.OPEN, og.CandleType.HIGH,
                  og.CandleType.LOW, og.CandleType.CLOSE],
)

# Schedule execution
scheduler = og.SchedulerParams(frequency=60, duration_hours=2)

# Deploy
contract = client.new_workflow(
    model_cid="your-model-cid",
    input_query=input_query,
    input_tensor_name="price_data",
    scheduler_params=scheduler,
)

# Read results
result = client.read_workflow_result(contract)
history = client.read_workflow_history(contract, num_results=5)
```

### AlphaSense Tool Creation

```python
from pydantic import BaseModel, Field

class ToolInput(BaseModel):
    token: str = Field(description="Token symbol")

tool = og.alphasense.create_run_model_tool(
    tool_type=og.alphasense.ToolType.LANGCHAIN,
    model_cid="your-model-cid",
    tool_name="PricePrediction",
    tool_description="Predicts token price movement",
    tool_input_schema=ToolInput,
    model_input_provider=lambda token: {"input": get_price_data(token)},
    model_output_formatter=lambda r: f"Prediction: {r.model_output['pred']}",
    inference_mode=og.InferenceMode.VANILLA,
)
```

## Key Types

```python
# Inference modes
og.InferenceMode.VANILLA    # Standard execution
og.InferenceMode.TEE        # Trusted Execution Environment
og.InferenceMode.ZKML       # Zero-knowledge proof

og.LlmInferenceMode.VANILLA
og.LlmInferenceMode.TEE

# x402 Payment Settlement Modes
og.x402SettlementMode.SETTLE           # Input/output hashes only (most private)
og.x402SettlementMode.SETTLE_BATCH     # Batch hashes for multiple inferences (most cost-efficient)
og.x402SettlementMode.SETTLE_METADATA  # Full model info, input/output data, and metadata

# Workflow data types
og.CandleType.OPEN, .HIGH, .LOW, .CLOSE, .VOLUME
og.CandleOrder.ASCENDING, .DESCENDING
```

## Error Handling

```python
from opengradient.exceptions import (
    OpenGradientError,      # Base exception
    AuthenticationError,
    InferenceError,
    InvalidInputError,
    NetworkError,
    RateLimitError,
    TimeoutError,
)

try:
    result = client.llm_chat(...)
except RateLimitError:
    # Retry with backoff
except InferenceError as e:
    print(f"Inference failed: {e.message}")
except OpenGradientError as e:
    print(f"Error {e.status_code}: {e.message}")
```

## Environment Variables

```bash
OG_PRIVATE_KEY=0x...          # Required: Ethereum private key
OPENAI_API_KEY=sk-...         # Optional: for OpenAI models
ANTHROPIC_API_KEY=sk-ant-...  # Optional: for Anthropic models
GOOGLE_API_KEY=AIza...        # Optional: for Google models
```

## Resources

- [OpenGradient Documentation](https://docs.opengradient.ai)
- [GitHub Repository](https://github.com/OpenGradient/sdk)
- [Model Hub](https://hub.opengradient.ai)
