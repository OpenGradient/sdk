"""Type definitions for models module."""

from dataclasses import dataclass, field


@dataclass
class WorkflowModelOutput:
    """
    Output definition for reading from a workflow model.
    """

    result: str
    """Result of the workflow formatted as a string."""

    block_explorer_link: str = field(default="")
    """(Optional) Block explorer link for the smart contract address of the workflow."""
