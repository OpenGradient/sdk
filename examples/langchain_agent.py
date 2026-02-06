"""
Basic LangChain agent using OpenGradient.

Creates a simple ReAct agent with a tool, powered by an OpenGradient LLM.

Usage:
    export OG_PRIVATE_KEY="your_private_key"
    python examples/langchain_agent.py
"""

import os

import opengradient as og
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# Create the OpenGradient LangChain adapter
llm = og.agents.langchain_adapter(
    private_key=os.environ.get("OG_PRIVATE_KEY"),
    model_cid=og.TEE_LLM.CLAUDE_3_5_HAIKU,
    max_tokens=300,
)


# Define a simple tool
@tool
def get_balance(account: str) -> str:
    """Returns the balance for a given account name."""
    balances = {"main": "1.25 ETH", "savings": "10.0 ETH", "treasury": "100.0 ETH"}
    return balances.get(account, "Account not found")


# Create a ReAct agent with the tool
agent = create_react_agent(llm, [get_balance])

# Run the agent
result = agent.invoke({"messages": [("user", "What is the balance of my 'treasury' account?")]})

print(result["messages"][-1].content)
