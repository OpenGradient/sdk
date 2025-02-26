import os
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import BaseTool
import opengradient as og
from typing import List

llm = og.llm.langchain_adapter(private_key=os.environ.get("OG_PRIVATE_KEY"), model_cid=og.LLM.QWEN_2_5_72B_INSTRUCT)

# You define tools here
tools: List[BaseTool] = []

agent = create_react_agent(model=llm, tools=tools, prompt="You are a friendly agent...")


# Helper to print agent steps
def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


inputs = {"messages": [("user", "what is the weather in sf?")]}
print_stream(agent.stream(inputs, stream_mode="values"))
