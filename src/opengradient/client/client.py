import json
from pathlib import Path
from typing import Dict, Optional

from eth_account.account import LocalAccount
from web3 import Web3

from ..defaults import (
    DEFAULT_OPENGRADIENT_LLM_SERVER_URL,
    DEFAULT_OPENGRADIENT_LLM_STREAMING_SERVER_URL,
)
from .llm import LLMMixin
from .model_hub import ModelHubMixin
from .model_hub_inference import InferenceMixin


class Client(ModelHubMixin, LLMMixin, InferenceMixin):
    _inference_hub_contract_address: str
    _blockchain: Web3
    _wallet_account: LocalAccount

    _hub_user: Optional[Dict]
    _api_url: str
    _inference_abi: Dict
    _precompile_abi: Dict

    def __init__(
        self,
        private_key: str,
        rpc_url: str,
        api_url: str,
        contract_address: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        og_llm_server_url: Optional[str] = DEFAULT_OPENGRADIENT_LLM_SERVER_URL,
        og_llm_streaming_server_url: Optional[str] = DEFAULT_OPENGRADIENT_LLM_STREAMING_SERVER_URL,
    ):
        """
        Initialize the Client with private key, RPC URL, and contract address.

        Args:
            private_key (str): The private key for the wallet.
            rpc_url (str): The RPC URL for the Ethereum node.
            contract_address (str): The contract address for the smart contract.
            email (str, optional): Email for authentication. Defaults to "test@test.com".
            password (str, optional): Password for authentication. Defaults to "Test-123".
        """
        self._inference_hub_contract_address = contract_address
        self._blockchain = Web3(Web3.HTTPProvider(rpc_url))
        self._api_url = api_url
        self._wallet_account = self._blockchain.eth.account.from_key(private_key)

        abi_path = Path(__file__).parent.parent / "abi" / "inference.abi"
        with open(abi_path, "r") as abi_file:
            self._inference_abi = json.load(abi_file)

        abi_path = Path(__file__).parent.parent / "abi" / "InferencePrecompile.abi"
        with open(abi_path, "r") as abi_file:
            self._precompile_abi = json.load(abi_file)

        if email is not None:
            self._hub_user = self._login_to_hub(email, password)
        else:
            self._hub_user = None

        self._og_llm_server_url = og_llm_server_url
        self._og_llm_streaming_server_url = og_llm_streaming_server_url

        self._alpha = None  # Lazy initialization for alpha namespace

    @property
    def alpha(self):
        """
        Access Alpha Testnet features.

        Returns:
            Alpha: Alpha namespace with workflow and ML model execution methods.

        Example:
            client = og.new_client(...)
            result = client.alpha.new_workflow(model_cid, input_query, input_tensor_name)
        """
        if self._alpha is None:
            from ..alpha import Alpha

            self._alpha = Alpha(self)
        return self._alpha
