"""
OpenGradient Python SDK for interacting with AI models and infrastructure.
"""

from typing import Optional

from . import agents, alphasense
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

global_client: Optional[Client] = None
"""Global client instance. Set by calling :func:`init`."""


def init(
    private_key: str,
    email: Optional[str] = None,
    password: Optional[str] = None,
    **kwargs,
) -> Client:
    """Initialize the global OpenGradient client.

    Args:
        private_key: Private key for OpenGradient transactions.
        email: Email for Model Hub authentication. Optional.
        password: Password for Model Hub authentication. Optional.
        **kwargs: Additional arguments forwarded to :class:`Client`.

    Returns:
        The newly created :class:`Client` instance.
    """
    global global_client
    global_client = Client(private_key=private_key, email=email, password=password, **kwargs)
    return global_client


__all__ = [
    "Client",
    "global_client",
    "init",
    "LLM",
    "TEE_LLM",
    "InferenceMode",
    "HistoricalInputQuery",
    "SchedulerParams",
    "CandleType",
    "CandleOrder",
    "agents",
    "alphasense",
]

__pdoc__ = {
    "account": False,
    "cli": False,
    "client": True,
    "defaults": False,
    "agents": True,
    "alphasense": True,
    "proto": False,
    "types": False,
}
