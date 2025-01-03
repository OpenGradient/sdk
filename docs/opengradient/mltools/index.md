---
outline: [2,3]
---

  

# Package opengradient.mltools

OpenGradient AlphaSense Tools

## Functions

  

### Create og model tool 

```python
def create_og_model_tool(tool_type: opengradient.mltools.model_tool.ToolType, model_cid: str, tool_name: str, input_getter: Callable, output_formatter: Callable[..., str], input_schema: Type[pydantic.main.BaseModel] = None, tool_description: str = 'Executes the given ML model', inference_mode: opengradient.types.InferenceMode = 0) ‑> langchain_core.tools.base.BaseTool
```

  

  
Creates a tool that wraps an OpenGradient model for inference.

This function generates a tool that can be integrated into either a LangChain pipeline
or a Swarm system, allowing the model to be executed as part of a chain of operations.
The tool uses the provided input_getter function to obtain the necessary input data and
runs inference using the specified OpenGradient model.
  

**Returns**

BaseTool: For ToolType.LANGCHAIN, returns a LangChain StructuredTool.
Callable: For ToolType.SWARM, returns a decorated function with appropriate metadata.

**Raises**

* **`ValueError`**: If an invalid tool_type is provided.

  

## Classes
    

###  ToolType

<code>class <b>ToolType</b>(*args, **kwds)</code>

  

  
Create a collection of name/value pairs.

Example enumeration:

>>> class Color(Enum):
...     RED = 1
...     BLUE = 2
...     GREEN = 3

Access them by:

- attribute access:

  >>> Color.RED
  <Color.RED: 1>

- value lookup:

  >>> Color(1)
  <Color.RED: 1>

- name lookup:

  >>> Color['RED']
  <Color.RED: 1>

Enumerations can be iterated over, and know how many members they have:

>>> len(Color)
3

>>> list(Color)
[<Color.RED: 1>, <Color.BLUE: 2>, <Color.GREEN: 3>]

Methods can be added to enumerations, and members can have their own
attributes -- see the documentation for details.
  

#### Variables

  
    
* static `LANGCHAIN`
    
* static `SWARM`