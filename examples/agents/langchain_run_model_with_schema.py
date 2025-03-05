import os
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import BaseTool
import opengradient as og
from typing import List
from pydantic import Field, BaseModel
from enum import Enum

og_key = os.environ.get("OG_PRIVATE_KEY")

llm = og.llm.langchain_adapter(private_key=og_key, model_cid=og.LLM.QWEN_2_5_72B_INSTRUCT)
og.init(private_key=og_key, email=None, password=None)

# Create ad-hoc model inference tool
class Token(str, Enum):
    ETH = "ethereum"
    BTC = "bitcoin"

class InputSchema(BaseModel):
    token: Token = Field(default=Token.ETH, description="Token name specified by user.")

def model_input_provider(**llm_input):
    token = llm_input.get("token")
    if token == Token.BTC:
        # This live-price data would normally come from an exchange
        return {"price_series": [100001.1, 100013.2, 100149.2, 99998.1]}
    elif token == Token.ETH:
        # This live-price data would normally come from an exchange
        return {"price_series": [2010.1, 2012.3, 2020.1, 2019.2]}
    else:
        raise ValueError("Unexpected option found")

def output_formatter(inference_result: og.InferenceResult):
    return format(float(inference_result.model_output["std"].item()), ".3%")

run_model_tool = og.alphasense.create_run_model_tool(
    tool_type=og.alphasense.ToolType.LANGCHAIN,
    model_cid="QmZdSfHWGJyzBiB2K98egzu3MypPcv4R1ASypUxwZ1MFUG",
    tool_name="ReturnVolatilityTool",
    model_input_provider=model_input_provider,
    model_output_formatter=output_formatter,
    tool_input_schema=InputSchema,
    tool_description="This tool takes a token and measures the return volatility (standard deviation of returns).",
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


inputs_btc = {"messages": [("user", "what is the current volatility of BTC?")]}
print_stream(agent.stream(inputs_btc, stream_mode="values"))

inputs_eth = {"messages": [("user", "what is the current volatility of ETH?")]}
print_stream(agent.stream(inputs_eth, stream_mode="values"))
