## Run non-hosted LLMs with x402 transaction processing through OpenGradient routers
# Use opengradient version pip install opengradient==0.5.0a3

# This currently only works with model: gpt-4.1-2025-04-14 but we are quickly working on adding
# more models.

# x402 Settlement Modes:
# - SETTLE: Individual settlement with input/output hashes only (most privacy-preserving)
# - SETTLE_BATCH: Batch settlement for multiple inferences (most cost-efficient, default)
# - SETTLE_METADATA: Full model info, complete input/output data, and all inference metadata

import os

import opengradient as og
from x402_permit2 import check_permit2_approval

network = "base-testnet"

client = og.Client(
    private_key=os.environ.get("OG_PRIVATE_KEY"),
)

check_permit2_approval(client.alpha._wallet_account.address, network)

messages = [
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a high-level programming language."},
    {"role": "user", "content": "What makes it good for beginners?"},
]

result = client.llm.chat(
    model=og.TEE_LLM.GPT_4_1_2025_04_14,
    messages=messages,
    x402_settlement_mode=og.x402SettlementMode.SETTLE_METADATA,
    network=network
)
print(f"Response: {result.chat_output['content']}")
print(f"Payment hash: {result.payment_hash}")
