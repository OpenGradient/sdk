import unittest
import os

from opengradient.llm import OpenGradientChatModel

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
        
    
if __name__ == '__main__':
    unittest.main()