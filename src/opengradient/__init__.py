"""
OpenGradient Python SDK for interacting with AI models and infrastructure.
"""

from typing import Optional

from . import alphasense, llm
from .client import Client
from .types import (
    LLM,
    TEE_LLM,
    CandleOrder,
    CandleType,
    FileUploadResult,
    HistoricalInputQuery,
    InferenceMode,
    InferenceResult,
    ModelOutput,
    ModelRepository,
    SchedulerParams,
    TextGenerationOutput,
    TextGenerationStream,
    x402SettlementMode,
)

client: Optional[Client] = None
"""Global client instance. Set by calling :func:`init`."""


def init(
    private_key: str,
    email: Optional[str] = None,
    password: Optional[str] = None,
    **kwargs,
) -> Client:
    """Initialize the global OpenGradient client.

    This creates a :class:`Client` and stores it as ``opengradient.client``
    so that tools and other SDK helpers can use it without explicit passing.

    Args:
        private_key: Private key for OpenGradient transactions.
        email: Email for Model Hub authentication. Optional.
        password: Password for Model Hub authentication. Optional.
        **kwargs: Additional arguments forwarded to :class:`Client`.

    Returns:
        The newly created :class:`Client` instance.
    """
    global client
    client = Client(private_key=private_key, email=email, password=password, **kwargs)
    return client


__all__ = [
    "Client",
    "client",
    "init",
    "LLM",
    "TEE_LLM",
    "InferenceMode",
    "HistoricalInputQuery",
    "SchedulerParams",
    "CandleType",
    "CandleOrder",
    "llm",
    "alphasense",
]

__pdoc__ = {
    "account": False,
    "cli": False,
    "client": False,
    "defaults": False,
    "llm": True,
    "alphasense": True,
    "proto": False,
    "types": False,
}
