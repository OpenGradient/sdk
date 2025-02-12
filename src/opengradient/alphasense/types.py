from enum import Enum


class ToolType(str, Enum):
    """Indicates the framework the tool is compatible with."""

    LANGCHAIN = "langchain"
    SWARM = "swarm"

    def __str__(self) -> str:
        return self.value
