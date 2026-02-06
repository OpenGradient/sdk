import os

import opengradient as og

client = og.new_client(
    email=None,
    password=None,
    private_key=os.environ.get("OG_PRIVATE_KEY"),
)

messages = [
    {"role": "user", "content": "Describe to me the 7 network layers?"},
]

stream = client.llm_chat(
    model=og.TEE_LLM.GPT_4_1_2025_04_14,
    messages=messages,
    x402_settlement_mode=og.x402SettlementMode.SETTLE_METADATA,
    stream=True,
    max_tokens=1000,
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
