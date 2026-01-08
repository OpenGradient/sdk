import os
import opengradient as og

# Initialize client with API keys for external providers
og_client = og.new_client(
    email=None,
    password=None,
    private_key=os.environ.get("OG_PRIVATE_KEY"),
    openai_api_key=os.environ.get("OPENAI_API_KEY"),  # Optional: for OpenAI models
    anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),  # Optional: for Anthropic models
    google_api_key=os.environ.get("GOOGLE_API_KEY"),  # Optional: for Google models
)

# Example 1: Using OpenAI GPT-4
completion = og_client.llm_chat(
    model_cid="gpt-4o",
    messages=[{"role": "user", "content": "Write a haiku about Python programming"}],
    inference_mode=og.LlmInferenceMode.VANILLA,
)

print("OpenAI GPT-4 Response:")
print(f"Response: {completion.chat_output['content']}")
print(f"Source: {completion.transaction_hash}")
print()

# Example 2: Using a hosted OpenGradient model
completion = og_client.llm_chat(
    model_cid=og.LLM.DOBBY_UNHINGED_3_1_8B,
    messages=[{"role": "user", "content": "say something funny"}],
    inference_mode=og.LlmInferenceMode.VANILLA,
)

print("OpenGradient Hosted Model Response:")
print(f"Response: {completion.chat_output['content']}")
print(f"Tx hash: {completion.transaction_hash}")
