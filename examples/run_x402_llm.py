## Run non-hosted LLMs with x402 transaction processing through OpenGradient routers
# Use opengradient version pip install opengradient==0.5.0a3

# This currently only works with model: gpt-4.1-2025-04-14 but we are quickly working on adding
# more models.

# x402 Settlement Modes:
# - SETTLE: Individual settlement with input/output hashes only (most privacy-preserving)
# - SETTLE_BATCH: Batch settlement for multiple inferences (most cost-efficient, default)
# - SETTLE_METADATA: Full model info, complete input/output data, and all inference metadata

import opengradient as og
import os

client = og.new_client(
    email=None,
    password=None,
    private_key=os.environ.get("OG_PRIVATE_KEY"),
)

messages = [
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a high-level programming language."},
    {"role": "user", "content": "What makes it good for beginners?"},
]

result = client.llm_chat(
    model_cid=og.LLM.GPT_4_1_2025_04_14,
    inference_mode=og.LlmInferenceMode.TEE,
    messages=messages,
    x402_settlement_mode=og.x402SettlementMode.SETTLE_BATCH,
)
print(f"Response: {result.chat_output['content']}")
print(f"Payment hash: {result.payment_hash}")
