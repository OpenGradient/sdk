import os
import opengradient as og

og_client = og.new_client(email=None, password=None, private_key=os.environ.get("OG_PRIVATE_KEY"))

completion = og_client.llm_chat(
    model_cid=og.LLM.GPT_4O,
    messages=[{"role": "user", "content": "say something funny"}],
    inference_mode=og.InferenceMode.VANILLA,
)

print(f"Response: {completion.chat_output['content']}")
print(f"Tx hash: {completion.transaction_hash}")
