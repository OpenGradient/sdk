from typing import Any, List, Optional

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM

from opengradient import Client
from opengradient.defaults import DEFAULT_INFERENCE_CONTRACT_ADDRESS, DEFAULT_RPC_URL

class OpenGradientLLM(LLM):

    client: Client
    model_cid: str

    def __init__(self, private_key: str, model_cid: str):
        self.client = Client(
            private_key=private_key,
            rpc_url=DEFAULT_RPC_URL,
            contract_address=DEFAULT_INFERENCE_CONTRACT_ADDRESS,
            email=None,
            password=None)
        self.model_cid = model_cid

    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
        ) -> str:
        _tx_hash, completion = self.client.llm_completion(
            model_cid=self.model_cid,
            prompt=prompt,
            stop_sequence=stop,
            max_tokens=300)

        return completion