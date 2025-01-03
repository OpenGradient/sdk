from typing import List, Dict, Optional, Any, Sequence, Union
import json

from langchain.chat_models.base import BaseChatModel
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    BaseMessage,
    ChatResult,
    ChatGeneration,
)
from langchain_core.messages.tool import (
    ToolMessage
)
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.tools import BaseTool
from langchain_core.messages import ToolCall

from opengradient import Client, LlmInferenceMode
from opengradient.defaults import DEFAULT_RPC_URL, DEFAULT_INFERENCE_CONTRACT_ADDRESS


class OpenGradientChatModel(BaseChatModel):
    """OpenGradient adapter class for LangChain chat model"""

    client: Client = None
    model_cid: str = None
    max_tokens: int = None
    tools: List[Dict] = []

    def __init__(self, private_key: str, model_cid: str, max_tokens: int = 300):
        super().__init__()
        self.client = Client(
            private_key=private_key,
            rpc_url=DEFAULT_RPC_URL,
            contract_address=DEFAULT_INFERENCE_CONTRACT_ADDRESS,
            email=None,
            password=None)
        self.model_cid = model_cid
        self.max_tokens = max_tokens

    @property
    def _llm_type(self) -> str:
        return "opengradient"
    
    def bind_tools(
        self,
        tools: Sequence[Union[BaseTool, Dict]],
    ) -> "OpenGradientChatModel":
        """Bind tools to the model."""
        tool_dicts = []
        for tool in tools:
            if isinstance(tool, BaseTool):
                tool_dicts.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.args_schema.schema() if hasattr(tool, "args_schema") else {}
                    }
                })
            else:
                tool_dicts.append(tool)
        
        self.tools = tool_dicts
        return self

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
                sdk_messages.append({
                    "role": "assistant", 
                    "content": message.content, 
                    "tool_calls": [{
                        "id": call["id"],
                        "name": call["name"],
                        "arguments": json.dumps(call["args"])
                    } for call in message.tool_calls]})
            elif isinstance(message, ToolMessage):
                sdk_messages.append({"role": "tool", "content": message.content, "tool_call_id": message.tool_call_id})
            else:
                raise ValueError(f"Unexpected message type: {message}")

        _, finish_reason, chat_response = self.client.llm_chat(
            model_cid=self.model_cid,
            messages=sdk_messages,
            stop_sequence=stop,
            max_tokens=self.max_tokens,
            tools=self.tools,
            inference_mode=LlmInferenceMode.VANILLA
        )

        if "tool_calls" in chat_response and chat_response["tool_calls"]:
            tool_calls = []
            for tool_call in chat_response["tool_calls"]:
                tool_calls.append(
                    ToolCall(
                        id=tool_call.get("id", ""),
                        name=tool_call["name"],
                        args=json.loads(tool_call["arguments"])
                    )
                )
            
            message = AIMessage(
                content='',
                tool_calls=tool_calls
            )
        else:
            message = AIMessage(content=chat_response["content"])

        return ChatResult(
            generations=[ChatGeneration(
                message=message,
                generation_info={"finish_reason": finish_reason}
            )]
        )

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_cid,
        }
