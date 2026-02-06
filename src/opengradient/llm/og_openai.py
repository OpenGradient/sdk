import time
import uuid
from typing import List

from openai.types.chat import ChatCompletion

from opengradient.client import Client
from opengradient.defaults import DEFAULT_INFERENCE_CONTRACT_ADDRESS, DEFAULT_RPC_URL
from opengradient.types import LLM


class OGCompletions(object):
    client: Client

    def __init__(self, client: Client):
        self.client = client

    def create(
        self,
        model: LLM,
        messages: List[object],
        tools: List[object],
        tool_choice: str,
        stream: bool = False,
        parallel_tool_calls: bool = False,
    ) -> ChatCompletion:
        # convert OpenAI message format so it's compatible with the SDK
        sdk_messages = OGCompletions.convert_to_abi_compatible(messages)

        chat_output = self.client.llm_chat(
            model_cid=model,
            messages=sdk_messages,
            max_tokens=200,
            tools=tools,
            tool_choice=tool_choice,
            temperature=0.25,
        )
        finish_reason = chat_output.finish_reason
        chat_completion = chat_output.chat_output

        choice = {
            "index": 0,  # Add missing index field
            "finish_reason": finish_reason,
            "message": {
                "role": chat_completion["role"],
                "content": chat_completion["content"],
                "tool_calls": [
                    {
                        "id": tool_call["id"],
                        "type": "function",  # Add missing type field
                        "function": {  # Add missing function field
                            "name": tool_call["name"],
                            "arguments": tool_call["arguments"],
                        },
                    }
                    for tool_call in chat_completion.get("tool_calls", [])
                ],
            },
        }

        return ChatCompletion(id=str(uuid.uuid4()), created=int(time.time()), model=model, object="chat.completion", choices=[choice])

    @staticmethod
    @staticmethod
    def convert_to_abi_compatible(messages):
        sdk_messages = []

        for message in messages:
            role = message["role"]
            sdk_message = {"role": role}

            if role == "system":
                sdk_message["content"] = message["content"]
            elif role == "user":
                sdk_message["content"] = message["content"]
            elif role == "tool":
                sdk_message["content"] = message["content"]
                sdk_message["tool_call_id"] = message["tool_call_id"]
            elif role == "assistant":
                flattened_calls = []
                for tool_call in message["tool_calls"]:
                    # OpenAI format
                    flattened_call = {
                        "id": tool_call["id"],
                        "name": tool_call["function"]["name"],
                        "arguments": tool_call["function"]["arguments"],
                    }
                    flattened_calls.append(flattened_call)

                sdk_message["tool_calls"] = flattened_calls
                sdk_message["content"] = message["content"]

            sdk_messages.append(sdk_message)

        return sdk_messages


class OGChat(object):
    completions: OGCompletions

    def __init__(self, client: Client):
        self.completions = OGCompletions(client)


class OpenGradientOpenAIClient(object):
    """OpenAI client implementation"""

    client: Client
    chat: OGChat

    def __init__(self, private_key: str):
        self.client = Client(
            private_key=private_key, rpc_url=DEFAULT_RPC_URL, contract_address=DEFAULT_INFERENCE_CONTRACT_ADDRESS, email=None, password=None
        )
        self.chat = OGChat(self.client)
