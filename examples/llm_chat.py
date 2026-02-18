import os

import opengradient as og

client = og.Client(
    private_key=os.environ.get("OG_PRIVATE_KEY"),
)

approval = client.llm.ensure_opg_approval(opg_amount=5)
print(f"$OPG Approval Status: {approval}")

messages = [
    {"role": "user", "content": "What is the capital of France?"},
]

result = client.llm.chat(
    model=og.TEE_LLM.CLAUDE_4_0_SONNET,
    messages=messages,
    max_tokens=300,
    x402_settlement_mode=og.x402SettlementMode.SETTLE_METADATA,
)
print(f"Response: {result.chat_output['content']}")
