## Chat with digital twins from twin.fun via OpenGradient verifiable inference

import os

import opengradient as og

client = og.init(
    private_key=os.environ.get("OG_PRIVATE_KEY"),
    twins_api_key=os.environ.get("TWINS_API_KEY"),
)

# Chat with Elon Musk
elon = client.twins.chat(
    twin_id="0x1abd463fd6244be4a1dc0f69e0b70cd5",
    model=og.TEE_LLM.GROK_4_1_FAST_NON_REASONING,
    messages=[{"role": "user", "content": "What do you think about AI?"}],
    max_tokens=1000,
)
print(f"Elon: {elon.chat_output['content']}")

# Chat with Donald Trump
trump = client.twins.chat(
    twin_id="0x66ae99aae4324ed580b2787ac5e811f6",
    model=og.TEE_LLM.GROK_4_1_FAST_NON_REASONING,
    messages=[{"role": "user", "content": "What's your plan for America?"}],
    max_tokens=1000,
)
print(f"Trump: {trump.chat_output['content']}")
