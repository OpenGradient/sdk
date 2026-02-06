"""
OpenGradient LLM Adapters

This module provides adapter interfaces to use OpenGradient LLMs with popular AI frameworks
like LangChain and OpenAI. These adapters allow seamless integration of OpenGradient models
into existing applications and agent frameworks.
"""

from .og_langchain import *
from .og_openai import *


def langchain_adapter(private_key: str, model_cid: LLM, max_tokens: int = 300) -> OpenGradientChatModel:
    """
    Returns an OpenGradient LLM that implements LangChain's LLM interface
    and can be plugged into LangChain agents.
    """
    return OpenGradientChatModel(private_key=private_key, model_cid=model_cid, max_tokens=max_tokens)


def openai_adapter(private_key: str) -> OpenGradientOpenAIClient:
    """
    Returns an generic OpenAI LLM client that can be plugged into Swarm and can
    be used with any LLM model on OpenGradient. The LLM is usually defined in the
    agent.
    """
    return OpenGradientOpenAIClient(private_key=private_key)


__all__ = [
    "langchain_adapter",
    "openai_adapter",
]

__pdoc__ = {"og_langchain": False, "og_openai": False}
