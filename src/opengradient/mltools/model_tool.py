from enum import Enum
from typing import Callable, Dict, Any, Type

from pydantic import BaseModel
from langchain_core.tools import BaseTool, StructuredTool
import opengradient as og

class ToolType(str, Enum):
    """Indicates the framework the tool is compatible with."""

    LANGCHAIN = "langchain"
    SWARM = "swarm"
    
    def __str__(self) -> str:
        return self.value

def create_og_model_tool(
    tool_type: ToolType,
    model_cid: str, 
    tool_name: str,
    input_getter: Callable,
    output_formatter: Callable[..., str],
    input_schema: Type[BaseModel] = None,
    tool_description: str = "Executes the given ML model", 
    inference_mode: og.InferenceMode= og.InferenceMode.VANILLA) -> BaseTool:
    """
    Creates a tool that wraps an OpenGradient model for inference.

    This function generates a tool that can be integrated into either a LangChain pipeline
    or a Swarm system, allowing the model to be executed as part of a chain of operations.
    The tool uses the provided input_getter function to obtain the necessary input data and
    runs inference using the specified OpenGradient model.

    Args:
        tool_type (ToolType): Specifies the framework to create the tool for. Use 
            ToolType.LANGCHAIN for LangChain integration or ToolType.SWARM for Swarm
            integration. 
        model_cid (str): The CID of the OpenGradient model to be executed.
        tool_name (str): The name to assign to the created tool. This will be used to identify
            and invoke the tool within the agent.
        input_getter (Callable): A function that returns the input data required by the model.
            The function should return data in a format compatible with the model's expectations.
        output_formatter (Callable[..., str]): A function that takes the model output and 
            formats it into a string. This is required to ensure the output is compatible
            with the tool framework.
        input_schema (Type[BaseModel], optional): A Pydantic BaseModel class defining the
            input schema. This will be used directly for LangChain tools and converted
            to appropriate annotations for Swarm tools. Default is None.
        tool_description (str, optional): A description of what the tool does. Defaults to
            "Executes the given ML model".
        inference_mode (og.InferenceMode, optional): The inference mode to use when running
            the model. Defaults to VANILLA.

    Returns:
        BaseTool: For ToolType.LANGCHAIN, returns a LangChain StructuredTool.
        Callable: For ToolType.SWARM, returns a decorated function with appropriate metadata.

    Raises:
        ValueError: If an invalid tool_type is provided.

    Examples:
        >>> from pydantic import BaseModel, Field
        >>> class ClassifierInput(BaseModel):
        ...     query: str = Field(description="User query to analyze")
        ...     parameters: dict = Field(description="Additional parameters")
        >>> def get_input():
        ...     return {"text": "Sample input text"}
        >>> def format_output(output):
        ...     return str(output.get("class", "Unknown"))
        >>> # Create a LangChain tool
        >>> langchain_tool = create_og_model_tool(
        ...     tool_type=ToolType.LANGCHAIN,
        ...     model_cid="Qm...",
        ...     tool_name="text_classifier",
        ...     input_getter=get_input,
        ...     output_formatter=format_output,
        ...     input_schema=ClassifierInput
        ...     tool_description="Classifies text into categories"
        ... )
    """
    # define runnable
    def model_executor(**llm_input):
        # Combine LLM input with input provided by code
        combined_input = {
            **llm_input,
            **input_getter()
        }

        _, output = og.infer(
            model_cid=model_cid,
            inference_mode=inference_mode,
            model_input=combined_input
        )

        return output_formatter(output)

    if tool_type == ToolType.LANGCHAIN:
        return StructuredTool.from_function(
            func=model_executor,
            name=tool_name,
            description=tool_description,
            args_schema=input_schema
        )
    elif tool_type == ToolType.SWARM:
        model_executor.__name__ = tool_name
        model_executor.__doc__ = tool_description
        # Convert Pydantic model to Swarm annotations if provided
        if input_schema:
            model_executor.__annotations__ = _convert_pydantic_to_annotations(input_schema)
        return model_executor
    else:
        raise ValueError(f"Invalid tooltype: {tool_type}")

def _convert_pydantic_to_annotations(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Convert a Pydantic model to function annotations format used by Swarm.
    
    Args:
        model: A Pydantic BaseModel class
        
    Returns:
        Dict mapping field names to (type, description) tuples
    """
    annotations = {}
    for field_name, field in model.model_fields.items():
        field_type = field.annotation
        description = field.description or ""
        annotations[field_name] = (field_type, description)
    return annotations
