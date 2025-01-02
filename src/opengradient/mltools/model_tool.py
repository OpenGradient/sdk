from enum import Enum
from typing import Callable

from langchain_core.tools import BaseTool, StructuredTool

import opengradient as og

class ToolType(Enum):
    LANGCHAIN = "langchain"
    SWARM = "swarm"
    
    def __str__(self) -> str:
        return self.value

def create_og_model_tool(
    tool_type: ToolType,
    model_cid: str, 
    tool_name: str,
    input_getter: Callable,
    tool_description: str = "Executes the given ML model", 
    inference_mode: og.InferenceMode= og.InferenceMode.VANILLA) -> BaseTool:
    """
        Creates a LangChain-compatible tool that wraps an OpenGradient model for inference.

    This function generates a tool that can be integrated into a LangChain pipeline,
    allowing the model to be executed as part of a chain of operations. The tool uses
    the provided input_getter function to obtain the necessary input data and runs
    inference using the specified OpenGradient model.

    Args:
        tool_type (ToolType): Specifies the framework to create the tool for. Use 
            ToolType.LANGCHAIN for LangChain integration or ToolType.SWARM for Swarm
            integration. 
        model_cid (str): The CID of the OpenGradient model to be executed.
        tool_name (str): The name to assign to the created tool. This will be used to identify
            and invoke the tool within the agent.
        input_getter (Callable): A function that returns the input data required by the model.
            The function should return data in a format compatible with the model's expectations.
        tool_description (str, optional): A description of what the tool does. Defaults to
            "Executes the given ML model".
        inference_mode (og.InferenceMode, optional): The inference mode to use when running
            the model. Defaults to VANILLA.

    Returns:
        BaseTool: A LangChain tool that can be used to execute the OpenGradient model
            within a LangChain pipeline.

    Examples:
        >>> def get_input():
        ...     return {"text": "Sample input text"}
        >>> tool = create_og_model_tool(
        ...     tool_type=ToolType.LANGCHAIN,
        ...     model_cid="Qm...",
        ...     tool_name="text_classifier",
        ...     input_getter=get_input,
        ...     tool_description="Classifies text into categories"
        ... )
        >>> # Use in LangChain
        >>> agent = Agent(tools=[tool])
    """
    # define runnable
    def model_executor():
        _, output = og.infer(
            model_cid=model_cid,
            inference_mode=inference_mode,
            model_input=input_getter()
        )

        return output

    return StructuredTool.from_function(
        func=model_executor,
        name=tool_name,
        description=tool_description
    )
