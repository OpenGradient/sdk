from dataclasses import dataclass
from typing import List, Tuple, Union
from enum import Enum

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
    META_LLAMA3_8B_INSTRUCT = "meta-llama/Meta-Llama-3-8B-Instruct"
    LLAMA_3_2_3B_INSTRUCT = "meta-llama/Llama-3.2-3B-Instruct"
    MISTRAL_7B_INSTRUCT_V3 = "mistralai/Mistral-7B-Instruct-v0.3"