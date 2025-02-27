import os
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import BaseTool
import opengradient as og
from typing import List

og_key = os.environ.get("OG_PRIVATE_KEY")

llm = og.llm.langchain_adapter(private_key=og_key, model_cid=og.LLM.QWEN_2_5_72B_INSTRUCT)
og.init(private_key=og_key, email=None, password=None)

# Create ad-hoc model inference tool
run_model_tool = og.alphasense.create_run_model_tool(
    tool_type=og.alphasense.ToolType.LANGCHAIN,
    model_cid="0x5DbC2b798501d08cF2957f005e25a5C34FAC2b1c",
    tool_name="BtcSpotForecast",
    tool_description="Returns the expected change of bitcoin price over the next 30 mins",
    input_getter=lambda: [],
    input_schema=None,
    output_formatter=lambda x: f"Expected return: {x.numbers['regression_output'][0] * 100}%",
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


inputs = {"messages": [("user", "what is the price of BTC going to be?")]}
print_stream(agent.stream(inputs, stream_mode="values"))
