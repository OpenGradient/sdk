"""Main Client class that unifies all OpenGradient service namespaces."""

from typing import Optional

from web3 import Web3

from ..defaults import (
    DEFAULT_API_URL,
    DEFAULT_INFERENCE_CONTRACT_ADDRESS,
    DEFAULT_OPENGRADIENT_LLM_SERVER_URL,
    DEFAULT_OPENGRADIENT_LLM_STREAMING_SERVER_URL,
    DEFAULT_RPC_URL,
)
from .alpha import Alpha
from .llm import LLM
from .model_hub import ModelHub
from .twins import Twins


class Client:
    """
    Main OpenGradient SDK client.

    Provides unified access to all OpenGradient services including LLM inference,
    on-chain model inference, and the Model Hub.

    The client operates across two chains:

    - **LLM inference** (``client.llm``) settles via x402 on **Base Sepolia**
      using OPG tokens (funded by ``private_key``).
    - **Alpha Testnet** (``client.alpha``) runs on the **OpenGradient network**
      using testnet gas tokens (funded by ``alpha_private_key``, or ``private_key``
      when not provided).

    Usage:
        client = og.Client(private_key="0x...")
        client = og.Client(private_key="0xBASE_KEY", alpha_private_key="0xALPHA_KEY")
        client.llm.ensure_opg_approval(opg_amount=5)  # one-time Permit2 approval
        result = client.llm.chat(model=TEE_LLM.CLAUDE_3_5_HAIKU, messages=[...])
        result = client.alpha.infer(model_cid, InferenceMode.VANILLA, input_data)
    """

    model_hub: ModelHub
    """Model Hub for creating, versioning, and uploading ML models."""

    llm: LLM
    """LLM chat and completion via TEE-verified execution."""

    alpha: Alpha
    """Alpha Testnet features including on-chain inference, workflow management, and ML model execution."""

    twins: Twins
    """Digital twins chat via OpenGradient verifiable inference."""

    def __init__(
        self,
        private_key: str,
        alpha_private_key: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        twins_api_key: Optional[str] = None,
        wallet_address: str = None,
        rpc_url: str = DEFAULT_RPC_URL,
        api_url: str = DEFAULT_API_URL,
        contract_address: str = DEFAULT_INFERENCE_CONTRACT_ADDRESS,
        og_llm_server_url: Optional[str] = DEFAULT_OPENGRADIENT_LLM_SERVER_URL,
        og_llm_streaming_server_url: Optional[str] = DEFAULT_OPENGRADIENT_LLM_STREAMING_SERVER_URL,
    ):
        """
        Initialize the OpenGradient client.

        The SDK uses two different chains. LLM inference (``client.llm``) settles
        via x402 on **Base Sepolia** using OPG tokens, while Alpha Testnet features
        (``client.alpha``) run on the **OpenGradient network** using testnet gas tokens.
        You can supply a separate ``alpha_private_key`` so each chain uses its own
        funded wallet. When omitted, ``private_key`` is used for both.

        Args:
            private_key: Private key whose wallet holds **Base Sepolia OPG tokens**
                for x402 LLM payments.
            alpha_private_key: Private key whose wallet holds **OpenGradient testnet
                gas tokens** for on-chain inference. Optional -- falls back to
                ``private_key`` for backward compatibility.
            email: Email for Model Hub authentication. Optional.
            password: Password for Model Hub authentication. Optional.
            twins_api_key: API key for digital twins chat (twin.fun). Optional.
            rpc_url: RPC URL for the OpenGradient Alpha Testnet.
            api_url: API URL for the OpenGradient API.
            contract_address: Inference contract address.
            og_llm_server_url: OpenGradient LLM server URL.
            og_llm_streaming_server_url: OpenGradient LLM streaming server URL.
        """
        blockchain = Web3(Web3.HTTPProvider(rpc_url))
        wallet_account = blockchain.eth.account.from_key(private_key)

        # Use a separate account for Alpha Testnet when provided
        if alpha_private_key is not None:
            alpha_wallet_account = blockchain.eth.account.from_key(alpha_private_key)
        else:
            alpha_wallet_account = wallet_account

        hub_user = None
        if email is not None:
            hub_user = ModelHub._login_to_hub(email, password)

        # Create namespaces
        self.model_hub = ModelHub(hub_user=hub_user)
        self.wallet_address = wallet_account.address

        self.llm = LLM(
            wallet_account=wallet_account,
            og_llm_server_url=og_llm_server_url,
            og_llm_streaming_server_url=og_llm_streaming_server_url,
        )

        self.alpha = Alpha(
            blockchain=blockchain,
            wallet_account=alpha_wallet_account,
            inference_hub_contract_address=contract_address,
            api_url=api_url,
        )

        if twins_api_key is not None:
            self.twins = Twins(api_key=twins_api_key)

    def close(self) -> None:
        """Close underlying SDK resources."""
        self.llm.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
