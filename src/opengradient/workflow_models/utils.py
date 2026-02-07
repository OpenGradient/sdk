"""Utility functions for the models module."""

from typing import Callable

from opengradient.client.alpha import Alpha

from .constants import BLOCK_EXPLORER_URL
from .types import WorkflowModelOutput


def create_block_explorer_link_smart_contract(transaction_hash: str) -> str:
    """Create block explorer link for smart contract."""
    block_explorer_url = BLOCK_EXPLORER_URL + "address/" + transaction_hash
    return block_explorer_url


def create_block_explorer_link_transaction(transaction_hash: str) -> str:
    """Create block explorer link for transaction."""
    block_explorer_url = BLOCK_EXPLORER_URL + "tx/" + transaction_hash
    return block_explorer_url


def read_workflow_wrapper(alpha: Alpha, contract_address: str, format_function: Callable[..., str]) -> WorkflowModelOutput:
    """
    Wrapper function for reading from models through workflows.
    Args:
        alpha (Alpha): The alpha namespace from an initialized OpenGradient client (client.alpha).
        contract_address (str): Smart contract address of the workflow
        format_function (Callable): Function for formatting the result returned by read_workflow
    """
    try:
        result = alpha.read_workflow_result(contract_address)

        formatted_result = format_function(result)
        block_explorer_link = create_block_explorer_link_smart_contract(contract_address)

        return WorkflowModelOutput(
            result=formatted_result,
            block_explorer_link=block_explorer_link,
        )
    except Exception as e:
        raise RuntimeError(f"Error reading from workflow with address {contract_address}: {e!s}")
