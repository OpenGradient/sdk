import json
from typing import Any, Dict, List, Optional, Sequence, Union, Callable
from typing_extensions import override

from langchain.chat_models.base import BaseChatModel
from langchain.schema import (
    AIMessage,
    BaseMessage,
    ChatGeneration,
    ChatResult,
    HumanMessage,
    SystemMessage,
)
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.messages import ToolCall
from langchain_core.messages.tool import ToolMessage
from langchain_core.tools import BaseTool
from langchain_core.runnables import Runnable
from langchain_core.language_models.base import LanguageModelInput

from opengradient import Client, LlmInferenceMode, LLM
from opengradient.defaults import DEFAULT_INFERENCE_CONTRACT_ADDRESS, DEFAULT_RPC_URL, DEFAULT_API_URL


class OpenGradientChatModel(BaseChatModel):
    """OpenGradient adapter class for LangChain chat model"""

    _client: Client
    _model_cid: LLM
    _max_tokens: int
    _tools: List[Dict] = []

    def __init__(self, private_key: str, model_cid: LLM, max_tokens: int = 300):
        super().__init__()

        self._client = Client(
            private_key=private_key, rpc_url=DEFAULT_RPC_URL, api_url=DEFAULT_API_URL, contract_address=DEFAULT_INFERENCE_CONTRACT_ADDRESS, email=None, password=None
        )
        self._model_cid = model_cid
        self._max_tokens = max_tokens

    @property
    def _llm_type(self) -> str:
        return "opengradient"

    @override
    def bind_tools(
        self,
        tools: Sequence[
            Union[Dict[str, Any], type, Callable, BaseTool]  # noqa: UP006
        ],
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, BaseMessage]:
        """Bind tools to the model."""
        tool_dicts: List[Dict] = []

        for tool in tools:
            if isinstance(tool, BaseTool):
                tool_dicts.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": (
                                tool.args_schema.schema() if hasattr(tool, "args_schema") and tool.args_schema is not None else {}
                            ),
                        },
                    }
                )
            else:
                tool_dicts.append(tool)

        self._tools = tool_dicts

        return self

    @override
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        sdk_messages = []
        for message in messages:
            if isinstance(message, SystemMessage):
                sdk_messages.append({"role": "system", "content": message.content})
            elif isinstance(message, HumanMessage):
                sdk_messages.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                sdk_messages.append(
                    {
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": [
                            {"id": call["id"], "name": call["name"], "arguments": json.dumps(call["args"])} for call in message.tool_calls
                        ],
                    }
                )
            elif isinstance(message, ToolMessage):
                sdk_messages.append({"role": "tool", "content": message.content, "tool_call_id": message.tool_call_id})
            else:
                raise ValueError(f"Unexpected message type: {message}")

        chat_output = self._client.llm_chat(
            model_cid=self._model_cid,
            messages=sdk_messages,
            stop_sequence=stop,
            max_tokens=self._max_tokens,
            tools=self._tools,
            inference_mode=LlmInferenceMode.VANILLA,
        )

        finish_reason = chat_output.finish_reason or ""
        chat_response = chat_output.chat_output or {}

        if "tool_calls" in chat_response and chat_response["tool_calls"]:
            tool_calls = []
            for tool_call in chat_response["tool_calls"]:
                tool_calls.append(ToolCall(id=tool_call.get("id", ""), name=tool_call["name"], args=json.loads(tool_call["arguments"])))

            message = AIMessage(content="", tool_calls=tool_calls)
        else:
            message = AIMessage(content=chat_response["content"])

        return ChatResult(generations=[ChatGeneration(message=message, generation_info={"finish_reason": finish_reason})])

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model_name": self._model_cid,
        }
