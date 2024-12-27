Module opengradient.llm
=======================
OpenGradient LLM Adapters
=========================

This module provides adapter interfaces to use OpenGradient LLMs with popular AI frameworks
like LangChain and OpenAI. These adapters allow seamless integration of OpenGradient models
into existing applications and agent frameworks.

Functions
---------

`langchain_adapter(private_key: str, model_cid: str, max_tokens: int = 300) ‑> opengradient.llm.og_langchain.OpenGradientChatModel`
:   Returns an OpenGradient LLM that implements LangChain's LLM interface
    and can be plugged into LangChain agents.

`openai_adapter(private_key: str) ‑> opengradient.llm.og_openai.OpenGradientOpenAIClient`
:   Returns an OpenAI LLM client that can be plugged into Swarm.