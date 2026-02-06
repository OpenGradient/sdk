"""
OpenGradient Agent Framework Adapters

This module provides adapter interfaces to use OpenGradient LLMs with popular AI frameworks
like LangChain. These adapters allow seamless integration of OpenGradient models
into existing applications and agent frameworks.
"""

from .og_langchain import *


def langchain_adapter(private_key: str, model_cid: LLM, max_tokens: int = 300) -> OpenGradientChatModel:
    """
    Returns an OpenGradient LLM that implements LangChain's LLM interface
    and can be plugged into LangChain agents.
    """
    return OpenGradientChatModel(private_key=private_key, model_cid=model_cid, max_tokens=max_tokens)


__all__ = [
    "langchain_adapter",
]

__pdoc__ = {"og_langchain": False}
