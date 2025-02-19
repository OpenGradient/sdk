---
outline: [2,3]
---

  

# Package opengradient.alphasense

OpenGradient AlphaSense Tools

## Functions

  

### Create read workflow tool 

```python
def create_read_workflow_tool(tool_type: opengradient.alphasense.types.ToolType, workflow_contract_address: str, tool_name: str, tool_description: str, output_formatter: Callable[..., str] = <function <lambda>>) ‑> langchain_core.tools.base.BaseTool
```

  

  
Creates a tool that reads results from a workflow contract on OpenGradient.

This function generates a tool that can be integrated into either a LangChain pipeline
or a Swarm system, allowing the workflow results to be retrieved and formatted as part
of a chain of operations.
  

**Returns**

BaseTool: For ToolType.LANGCHAIN, returns a LangChain StructuredTool.
Callable: For ToolType.SWARM, returns a decorated function with appropriate metadata.

**Raises**

* **`ValueError`**: If an invalid tool_type is provided.

  

  

### Create run model tool 

```python
def create_run_model_tool(tool_type: opengradient.alphasense.types.ToolType, model_cid: str, tool_name: str, input_getter: Callable, output_formatter: Callable[..., str] = <function <lambda>>, input_schema: Type[pydantic.main.BaseModel] = None, tool_description: str = 'Executes the given ML model', inference_mode: opengradient.types.InferenceMode = 0) ‑> langchain_core.tools.base.BaseTool
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

  

  
Indicates the framework the tool is compatible with.
  

#### Variables

  
    
* static `LANGCHAIN` - The type of the None singleton.
    
* static `SWARM` - The type of the None singleton.