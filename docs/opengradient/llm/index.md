# Package opengradient.llm

OpenGradient LLM Adapters

This module provides adapter interfaces to use OpenGradient LLMs with popular AI frameworks
like LangChain and OpenAI. These adapters allow seamless integration of OpenGradient models
into existing applications and agent frameworks.

## Functions

  

### Langchain adapter 

```python
def langchain_adapter(private_key: str, model_cid: str, max_tokens: int = 300) ‑> [og_langchain](docs/llm.md#og_langchain)
```

  

  
Returns an OpenGradient LLM that implements LangChain's LLM interface
and can be plugged into LangChain agents.
  

  

### Openai adapter 

```python
def openai_adapter(private_key: str) ‑> [og_openai](docs/llm.md#og_openai)
```

  

  
Returns an OpenAI LLM client that can be plugged into Swarm.
  

## Classes
    

###  OpenGradientChatModel

<code>class <b>OpenGradientChatModel</b>(private_key: str, model_cid: str, max_tokens: int = 300)</code>

  

  
OpenGradient adapter class for LangChain chat model
  

  

### Bind tools 

```python
def bind_tools(self, tools: Sequence[langchain_core.tools.base.BaseTool | Dict]) ‑> [og_langchain](docs/llm.md#og_langchain)
```

  

  
Bind tools to the model.
  

#### Variables

  
    
* static `client  : [Client](docs/client.md#Client)`
    
* static `max_tokens  : int`
    
* static `model_cid  : str`
    
* static `model_computed_fields`
    
* static `model_config`
    
* static `model_fields`
    
* static `tools  : List[Dict]`

      
    

###  OpenGradientOpenAIClient

<code>class <b>OpenGradientOpenAIClient</b>(private_key: str)</code>

  

  
OpenAI client implementation
  

#### Variables

  
    
* static `chat  : [og_openai](docs/llm.md#og_openai)`
    
* static `client  : [Client](docs/client.md#Client)`