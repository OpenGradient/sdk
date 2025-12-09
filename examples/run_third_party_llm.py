## Run non-hosted LLMs through OpenGradient routers
# Use opengradient version pip install opengradient==0.5.0a2
# This works for Gemini, Anthropic, and OpenAI models in langchain
# https://docs.langchain.com/oss/python/integrations/chat
import opengradient as og
og_gemini_client = og.new_client(
    email=None,
    password=None,
    private_key=os.environ.get("OG_PRIVATE_KEY"),
    google_api_key=os.environ.get("GOOGLE_API_KEY")
)

result = og_gemini_client.llm_completion(
    model_cid="gemini-2.5-flash-lite", 
    inference_mode=og.LlmInferenceMode.VANILLA, 
    prompt="Write a haiku about coding")

print(f"Response: {result.completion_output}")
print(f"Tx hash: {result.transaction_hash}")

messages = [
    {"role": "user", "content": "What is Python?"}, 
    {"role": "assistant", "content": "Python is a high-level programming language."},
    {"role": "user", "content": "What makes it good for beginners?"}
]

result = og_gemini_client.llm_chat(model_cid="gemini-2.5-flash-lite", inference_mode=og.LlmInferenceMode.VANILLA, messages=messages)
print(f"Response: {result.chat_output['content']}")
print(f"Tx hash: {result.transaction_hash}")
