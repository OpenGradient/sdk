import os
import unittest

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from opengradient.alphasense import create_read_workflow_tool, ToolType
from opengradient.llm import OpenGradientChatModel
from opengradient import LLM
from opengradient import init
from opengradient import read_workflow_result


class TestLLM(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        private_key = os.environ.get("PRIVATE_KEY")
        if not private_key:
            raise ValueError("PRIVATE_KEY environment variable is not set")

        init(private_key=private_key, email=None, password=None)
        self.llm = OpenGradientChatModel(private_key=private_key, model_cid=LLM.QWEN_2_5_72B_INSTRUCT)

    def test_simple_completion(self):
        message = self.llm.invoke("say 'hello'. literally")
        self.assertIn("hello", message.content)

    def test_tool_call(self):
        @tool
        def get_balance():
            """Returns the user's balance"""
            return "Your balance is 0.145"

        agent_executor = create_react_agent(self.llm, [get_balance])
        events = agent_executor.stream({"messages": [("user", "What is my balance?")]}, stream_mode="values", debug=False)

        self.assertIn("0.145", list(events)[-1]["messages"][-1].content)

    def test_workflow(self):
        # Read current workflow result
        workflow_result = read_workflow_result(contract_address="0x6e0641925b845A1ca8aA9a890C4DEF388E9197e0")
        expected_result = str(workflow_result.numbers["Y"][0])

        btc_workflow_tool = create_read_workflow_tool(
            tool_type=ToolType.LANGCHAIN,
            workflow_contract_address="0x6e0641925b845A1ca8aA9a890C4DEF388E9197e0",
            tool_name="ETH_Price_Forecast",
            tool_description="Reads latest forecast for ETH price",
            output_formatter=lambda x: x,
        )

        agent_executor = create_react_agent(self.llm, [btc_workflow_tool])
        events = agent_executor.stream(
            {"messages": [("user", "Please print the raw value of the latest ETH forecast?")]}, stream_mode="values", debug=False
        )

        # Just checks that the first 5 values are in the result
        self.assertIn(expected_result[:5], list(events)[-1]["messages"][-1].content)


if __name__ == "__main__":
    unittest.main()
