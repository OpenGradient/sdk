import os
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import BaseTool
import opengradient as og
from typing import List

og_key = os.environ.get("OG_PRIVATE_KEY")

llm = og.llm.langchain_adapter(private_key=og_key, model_cid=og.LLM.CLAUDE_3_7_SONNET)
og.init(private_key=og_key, email=None, password=None)

# Create workflow read tool
workflow_read_tool = og.alphasense.create_read_workflow_tool(
    tool_type=og.alphasense.ToolType.LANGCHAIN,
    workflow_contract_address="0x5DbC2b798501d08cF2957f005e25a5C34FAC2b1c",
    tool_name="BtcSpotForecast",
    tool_description="Returns the expected change of bitcoin price over the next 30 mins",
    output_formatter=lambda x: f"Expected return: {x.numbers['regression_output'][0] * 100}%",
)

tools: List[BaseTool] = [workflow_read_tool]
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
