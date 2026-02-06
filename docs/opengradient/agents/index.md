---
outline: [2,3]
---

  

# Package opengradient.agents

OpenGradient Agent Framework Adapters

This module provides adapter interfaces to use OpenGradient LLMs with popular AI frameworks
like LangChain and OpenAI. These adapters allow seamless integration of OpenGradient models
into existing applications and agent frameworks.

## Functions

  

### Langchain adapter 

```python
def langchain_adapter(private_key: str, model_cid: opengradient.types.LLM, max_tokens: int = 300) ‑> opengradient.agents.og_langchain.OpenGradientChatModel
```

  

  
Returns an OpenGradient LLM that implements LangChain's LLM interface
and can be plugged into LangChain agents.
  

  

### Openai adapter 

```python
def openai_adapter(private_key: str) ‑> opengradient.agents.og_openai.OpenGradientOpenAIClient
```

  

  
Returns an generic OpenAI LLM client that can be plugged into Swarm and can
be used with any LLM model on OpenGradient. The LLM is usually defined in the
agent.