from typing import Callable

from langchain_core.tools import BaseTool, StructuredTool

import opengradient as og

def create_og_model_tool(
    model_cid: str, 
    input_fetcher: Callable,
    tool_description: str, 
    input_description: str,
    inference_mode: og.InferenceMode) -> BaseTool:
    # define runnable
    def model_executor():
        tx_hash, output = og.infer(
            model_cid=model_cid,
            inference_mode=inference_mode,
            model_input=input_fetcher()
        )

        return output

    return StructuredTool(
        func=model_executor,
        description=tool_description
    )
