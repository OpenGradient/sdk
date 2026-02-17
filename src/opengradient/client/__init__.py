"""
OpenGradient Client -- the central entry point to all SDK services.

## Overview

The `opengradient.client.client.Client` class provides unified access to four service namespaces:

- **`opengradient.client.llm`** -- LLM chat and text completion with TEE-verified execution and x402 payment settlement
- **`opengradient.client.model_hub`** -- Model repository management: create, version, and upload ML models
- **`opengradient.client.alpha`** -- Alpha Testnet features: on-chain ONNX model inference (VANILLA, TEE, ZKML modes), workflow deployment, and scheduled ML model execution
- **`opengradient.client.twins`** -- Digital twins chat via OpenGradient verifiable inference

## Usage

```python
import opengradient as og

client = og.init(private_key="0x...")

# Use separate keys for LLM (Base Sepolia) and Alpha Testnet
client = og.init(private_key="0xLLM_KEY...", alpha_private_key="0xALPHA_KEY...")

# LLM chat (TEE-verified, streamed)
for chunk in client.llm.chat(
    model=og.TEE_LLM.CLAUDE_3_5_HAIKU,
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=200,
    stream=True,
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")

# On-chain model inference
result = client.alpha.infer(
    model_cid="your_model_cid",
    inference_mode=og.InferenceMode.VANILLA,
    model_input={"input": [1.0, 2.0, 3.0]},
)

# Model Hub (requires email auth)
client = og.init(private_key="0x...", email="you@example.com", password="...")
repo = client.model_hub.create_model("my-model", "A price prediction model")
```
"""

from .client import Client

__all__ = ["Client"]

__pdoc__ = {
    "x402_auth": False,
}
