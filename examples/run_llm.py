import os
import opengradient as og

og_client = og.new_client(email=None, password=None, private_key=os.environ.get("OG_PRIVATE_KEY"))

completion = og_client.llm_chat(
    model_cid=og.LLM.DOBBY_UNHINGED_3_1_8B,
    messages=[{"role": "user", "content": "say something funny"}],
    inference_mode=og.InferenceMode.VANILLA,
)

print(f"Response: {completion.chat_output['content']}")
print(f"Tx hash: {completion.transaction_hash}")

## Run non-hosted LLMs through OpenGradient routers
# Use opengradient version `pip install opengradient==0.5.0a2`
# This works for Gemini, Anthropic, and OpenAI models in langchain
# https://docs.langchain.com/oss/python/integrations/chat
from opengradient import DEFAULT_INFERENCE_CONTRACT_ADDRESS, DEFAULT_RPC_URL, DEFAULT_API_URL
og_gemini_client = og.new_client(
    email=None, 
    password=None, 
    private_key=os.environ.get("OG_PRIVATE_KEY"),
    google_api_key=os.environ.get("GOOGLE_API_KEY")
)

result = og_gemini_client.llm_completion(
    model_cid="gemini-2.5-flash-lite", 
    inference_mode=og.LlmInferenceMode.VANILLA, 
    prompt="Write a haiku about coding"
)

print(f"Response: {result.completion_output}")
print(f"Tx hash: {completion.transaction_hash}")

messages = [
    {"role": "user", "content": "What is Python?"}, 
    {"role": "assistant", "content": "Python is a high-level programming language."},
    {"role": "user", "content": "What makes it good for beginners?"}
]

result = client.llm_chat(
    model_cid="gemini-2.5-flash-lite", 
    inference_mode=og.LlmInferenceMode.VANILLA, 
    messages=messages
)

print(f"Response: {completion.chat_output['content']}")
print(f"Tx hash: {completion.transaction_hash}")
