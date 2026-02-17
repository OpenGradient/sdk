import os

import opengradient as og
from x402_permit2 import check_permit2_approval

client = og.Client(
    private_key=os.environ.get("OG_PRIVATE_KEY"),
)

check_permit2_approval(client.wallet_address)

messages = [
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a high-level programming language."},
    {"role": "user", "content": "What makes it good for beginners?"},
]

stream = client.llm.chat(
    model=og.TEE_LLM.GPT_4_1_2025_04_14,
    messages=messages,
    x402_settlement_mode=og.x402SettlementMode.SETTLE_METADATA,
    stream=True,
    max_tokens=300,
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
