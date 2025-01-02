from typing import Callable

from langchain_core.tools import BaseTool, StructuredTool

import opengradient as og

def create_og_model_tool(
    model_cid: str, 
    tool_name: str,
    tool_description: str, 
    input_getter: Callable,
    inference_mode: og.InferenceMode= og.InferenceMode.VANILLA) -> BaseTool:
    """
    Returns a LangChain-compatible tool that invokes the given OpenGradient 
    model and returns the result as output.
    """
    # define runnable
    def model_executor():
        tx_hash, output = og.infer(
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
