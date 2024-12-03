import unittest
import os

from opengradient.llm import OpenGradientChatModel
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

class TestLLM(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        private_key = os.environ.get('PRIVATE_KEY')
        if not private_key:
            raise ValueError("PRIVATE_KEY environment variable is not set")

        self.llm = OpenGradientChatModel(
            private_key=private_key,
            model_cid='meta-llama/Llama-3.1-70B-Instruct')
    
    def test_simple_completion(self):
        message = self.llm.invoke("say 'hello'. literally")
        self.assertIn("hello", message.content)

    def test_tool_call(self):
        @tool
        def get_balance():
            """Returns the user's balance"""
            return "Your balance is 0.145"

        agent_executor = create_react_agent(self.llm, [get_balance])
        events = agent_executor.stream(
            {"messages": [("user", "What is my balance?")]},
            stream_mode="values",
            debug=True
        )

        for event in events:
            event["messages"][-1].pretty_print()


if __name__ == '__main__':
    unittest.main()