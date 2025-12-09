import time
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Dict, List, Optional, Tuple, Union, DefaultDict
import numpy as np


class CandleOrder(IntEnum):
    ASCENDING = 0
    DESCENDING = 1


class CandleType(IntEnum):
    HIGH = 0
    LOW = 1
    OPEN = 2
    CLOSE = 3
    VOLUME = 4


@dataclass
class HistoricalInputQuery:
    base: str
    quote: str
    total_candles: int
    candle_duration_in_mins: int
    order: CandleOrder
    candle_types: List[CandleType]

    def to_abi_format(self) -> tuple:
        """Convert to format expected by contract ABI"""
        return (
            self.base,
            self.quote,
            self.total_candles,
            self.candle_duration_in_mins,
            int(self.order),
            [int(ct) for ct in self.candle_types],
        )


@dataclass
class Number:
    value: int
    decimals: int


@dataclass
class NumberTensor:
    """
    A container for numeric tensor data used as input for ONNX models.

    Attributes:

        name: Identifier for this tensor in the model.

        values: List of integer tuples representing the tensor data.
    """

    name: str
    values: List[Tuple[int, int]]


@dataclass
class StringTensor:
    """
    A container for string tensor data used as input for ONNX models.

    Attributes:

        name: Identifier for this tensor in the model.

        values: List of strings representing the tensor data.
    """

    name: str
    values: List[str]


@dataclass
class ModelInput:
    """
    A collection of tensor inputs required for ONNX model inference.

    Attributes:

        numbers: Collection of numeric tensors for the model.

        strings: Collection of string tensors for the model.
    """

    numbers: List[NumberTensor]
    strings: List[StringTensor]


class InferenceMode(Enum):
    """Enum for the different inference modes available for inference (VANILLA, ZKML, TEE)"""

    VANILLA = 0
    ZKML = 1
    TEE = 2


class LlmInferenceMode(Enum):
    """Enum for differetn inference modes available for LLM inferences (VANILLA, TEE)"""

    VANILLA = 0
    TEE = 1


@dataclass
class ModelOutput:
    """
    Model output struct based on translations from smart contract.
    """

    numbers: Dict[str, np.ndarray]
    strings: Dict[str, np.ndarray]
    jsons: Dict[str, np.ndarray]  # Converts to JSON dictionary
    is_simulation_result: bool


@dataclass
class InferenceResult:
    """
    Output for ML inference requests.
    This class has two fields
        transaction_hash (str): Blockchain hash for the transaction
        model_output (Dict[str, np.ndarray]): Output of the ONNX model
    """

    transaction_hash: str
    model_output: Dict[str, np.ndarray]


@dataclass
class TextGenerationOutput:
    """
    Output structure for text generation requests.
    """

    transaction_hash: str
    """Blockchain hash for the transaction."""

    finish_reason: Optional[str] = None
    """Reason for completion (e.g., 'tool_call', 'stop', 'error'). Empty string if not applicable."""

    chat_output: Optional[Dict] = None
    """Dictionary of chat response containing role, message content, tool call parameters, etc.. Empty dict if not applicable."""

    completion_output: Optional[str] = None
    """Raw text output from completion-style generation. Empty string if not applicable."""


@dataclass
class AbiFunction:
    name: str
    inputs: List[Union[str, "AbiFunction"]]
    outputs: List[Union[str, "AbiFunction"]]
    state_mutability: str


@dataclass
class Abi:
    functions: List[AbiFunction]

    @classmethod
    def from_json(cls, abi_json):
        functions = []
        for item in abi_json:
            if item["type"] == "function":
                inputs = cls._parse_inputs_outputs(item["inputs"])
                outputs = cls._parse_inputs_outputs(item["outputs"])
                functions.append(AbiFunction(name=item["name"], inputs=inputs, outputs=outputs, state_mutability=item["stateMutability"]))
        return cls(functions=functions)

    @staticmethod
    def _parse_inputs_outputs(items):
        result = []
        for item in items:
            if "components" in item:
                result.append(
                    AbiFunction(name=item["name"], inputs=Abi._parse_inputs_outputs(item["components"]), outputs=[], state_mutability="")
                )
            else:
                result.append(f"{item['name']}:{item['type']}")
        return result


class LLM(str, Enum):
    """Enum for available LLM models"""

    META_LLAMA_3_8B_INSTRUCT = "meta-llama/Meta-Llama-3-8B-Instruct"
    LLAMA_3_2_3B_INSTRUCT = "meta-llama/Llama-3.2-3B-Instruct"
    QWEN_2_5_72B_INSTRUCT = "Qwen/Qwen2.5-72B-Instruct"
    META_LLAMA_3_1_70B_INSTRUCT = "meta-llama/Llama-3.1-70B-Instruct"
    DOBBY_UNHINGED_3_1_8B = "SentientAGI/Dobby-Mini-Unhinged-Llama-3.1-8B"
    DOBBY_LEASHED_3_1_8B = "SentientAGI/Dobby-Mini-Leashed-Llama-3.1-8B"


class TEE_LLM(str, Enum):
    """Enum for LLM models available for TEE execution"""

    META_LLAMA_3_1_70B_INSTRUCT = "meta-llama/Llama-3.1-70B-Instruct"


@dataclass
class SchedulerParams:
    frequency: int
    duration_hours: int

    @property
    def end_time(self) -> int:
        return int(time.time()) + (self.duration_hours * 60 * 60)

    @staticmethod
    def from_dict(data: Optional[Dict[str, int]]) -> Optional["SchedulerParams"]:
        if data is None:
            return None
        return SchedulerParams(frequency=data.get("frequency", 600), duration_hours=data.get("duration_hours", 2))


@dataclass
class ModelRepository:
    name: str
    initialVersion: str


@dataclass
class FileUploadResult:
    modelCid: str
    size: int
