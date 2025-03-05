import os
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import BaseTool
import opengradient as og
from typing import List

og_key = os.environ.get("OG_PRIVATE_KEY")

llm = og.llm.langchain_adapter(private_key=og_key, model_cid=og.LLM.QWEN_2_5_72B_INSTRUCT)
og.init(private_key=og_key, email=None, password=None)

# Create ad-hoc model inference tool
def model_input_provider():
    # This function can be used to retrieve live data, process data, etc. 
    return {
            "open_high_low_close": [
                [2535.79, 2535.79, 2505.37, 2515.36],
                [2515.37, 2516.37, 2497.27, 2506.94],
                [2506.94, 2515, 2506.35, 2508.77],
                [2508.77, 2519, 2507.55, 2518.79],
                [2518.79, 2522.1, 2513.79, 2517.92],
                [2517.92, 2521.4, 2514.65, 2518.13],
                [2518.13, 2525.4, 2517.2, 2522.6],
                [2522.59, 2528.81, 2519.49, 2526.12],
                [2526.12, 2530, 2524.11, 2529.99],
                [2529.99, 2530.66, 2525.29, 2526],
            ]
        }

def output_formatter(inference_result: og.InferenceResult):
    # Format output of the inference to 3 decimal places.
    return format(float(inference_result.model_output["Y"].item()), ".3%")

run_model_tool = og.alphasense.create_run_model_tool(
    tool_type=og.alphasense.ToolType.LANGCHAIN,
    model_cid="QmRhcpDXfYCKsimTmJYrAVM4Bbvck59Zb2onj3MHv9Kw5N",
    tool_name="OneHourEthUsdtVolatilityForecaster",
    model_input_provider=model_input_provider,
    model_output_formatter=output_formatter,
    tool_input_schema=None,  # If the model_input_provider does not require any input arguments, then tool_input_schema is not required
    tool_description="Returns the predicted price volatility for the trading pair ETH/USDT over the next hour",
    inference_mode=og.InferenceMode.VANILLA
)

tools: List[BaseTool] = [run_model_tool]
agent = create_react_agent(model=llm, tools=tools, prompt="Answer the users questions using the tools provided")


# Helper to print agent steps
def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


inputs = {"messages": [("user", "what is the future volatility of the trading pair ETH/USDT?")]}
print_stream(agent.stream(inputs, stream_mode="values"))
