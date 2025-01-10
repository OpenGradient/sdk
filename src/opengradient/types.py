from dataclasses import dataclass
from typing import List, Tuple, Union
from enum import Enum, IntEnum

class CandleOrder(IntEnum):
    ASCENDING = 0
    DESCENDING = 1

class CandleType(IntEnum):
    HIGH = 0
    LOW = 1
    OPEN = 2
    CLOSE = 3

@dataclass
class HistoricalInputQuery:
    currency_pair: str
    total_candles: int
    candle_duration_in_mins: int
    order: CandleOrder
    candle_types: List[CandleType]

    def to_abi_format(self) -> tuple:
        """Convert to format expected by contract ABI"""
        return (
            self.currency_pair,
            self.total_candles,
            self.candle_duration_in_mins,
            int(self.order),
            [int(ct) for ct in self.candle_types]
        )

    @classmethod
    def from_dict(cls, data: dict) -> 'HistoricalInputQuery':
        """Create HistoricalInputQuery from dictionary format"""
        order = CandleOrder[data['order'].upper()]
        candle_types = [CandleType[ct.upper()] for ct in data['candle_types']]
        
        return cls(
            currency_pair=data['currency_pair'],
            total_candles=int(data['total_candles']),
            candle_duration_in_mins=int(data['candle_duration_in_mins']),
            order=order,
            candle_types=candle_types
        )

@dataclass
class Number:
    value: int
    decimals: int

@dataclass
class NumberTensor:
    name: str
    values: List[Tuple[int, int]]

@dataclass
class StringTensor:
    name: str
    values: List[str]

@dataclass
class ModelInput:
    numbers: List[NumberTensor]
    strings: List[StringTensor]

class InferenceMode:
    VANILLA = 0
    ZKML = 1
    TEE = 2

class LlmInferenceMode:
    VANILLA = 0
    TEE = 1

@dataclass
class ModelOutput:
    numbers: List[NumberTensor]
    strings: List[StringTensor]
    is_simulation_result: bool

@dataclass
class AbiFunction:
    name: str
    inputs: List[Union[str, 'AbiFunction']]
    outputs: List[Union[str, 'AbiFunction']]
    state_mutability: str

@dataclass
class Abi:
    functions: List[AbiFunction]

    @classmethod
    def from_json(cls, abi_json):
        functions = []
        for item in abi_json:
            if item['type'] == 'function':
                inputs = cls._parse_inputs_outputs(item['inputs'])
                outputs = cls._parse_inputs_outputs(item['outputs'])
                functions.append(AbiFunction(
                    name=item['name'],
                    inputs=inputs,
                    outputs=outputs,
                    state_mutability=item['stateMutability']
                ))
        return cls(functions=functions)

    @staticmethod
    def _parse_inputs_outputs(items):
        result = []
        for item in items:
            if 'components' in item:
                result.append(AbiFunction(
                    name=item['name'],
                    inputs=Abi._parse_inputs_outputs(item['components']),
                    outputs=[],
                    state_mutability=''
                ))
            else:
                result.append(f"{item['name']}:{item['type']}")
        return result
    
class LLM(str, Enum):
    """Enum for available LLM models"""

    META_LLAMA_3_8B_INSTRUCT = "meta-llama/Meta-Llama-3-8B-Instruct"
    LLAMA_3_2_3B_INSTRUCT = "meta-llama/Llama-3.2-3B-Instruct"
    MISTRAL_7B_INSTRUCT_V3 = "mistralai/Mistral-7B-Instruct-v0.3"
    HERMES_3_LLAMA_3_1_70B = "NousResearch/Hermes-3-Llama-3.1-70B"
    META_LLAMA_3_1_70B_INSTRUCT = "meta-llama/Llama-3.1-70B-Instruct"

class TEE_LLM(str, Enum):
    """Enum for LLM models available for TEE execution"""

    META_LLAMA_3_1_70B_INSTRUCT = "meta-llama/Llama-3.1-70B-Instruct"