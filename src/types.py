from typing import List, Union
from dataclasses import dataclass

@dataclass
class OGNumber:
    value: int
    decimals: int

@dataclass
class OGNumberTensor:
    name: str
    values: List[OGNumber]

@dataclass
class OGStringTensor:
    name: str
    values: List[str]

@dataclass
class OGModelInput:
    numbers: List[OGNumberTensor]
    strings: List[OGStringTensor]

class OGInferenceMode:
    VANILLA = 0
    PRIVATE = 1
    VERIFIED = 2

@dataclass
class OGModelOutput:
    numbers: List[OGNumberTensor]
    strings: List[OGStringTensor]
    is_simulation_result: bool

@dataclass
class OGAbiFunction:
    name: str
    inputs: List[Union[str, 'OGAbiFunction']]
    outputs: List[Union[str, 'OGAbiFunction']]
    stateMutability: str

@dataclass
class OGAbi:
    functions: List[OGAbiFunction]

    @classmethod
    def from_json(cls, abi_json):
        functions = []
        for item in abi_json:
            if item['type'] == 'function':
                inputs = cls._parse_inputs_outputs(item['inputs'])
                outputs = cls._parse_inputs_outputs(item['outputs'])
                functions.append(OGAbiFunction(
                    name=item['name'],
                    inputs=inputs,
                    outputs=outputs,
                    stateMutability=item['stateMutability']
                ))
        return cls(functions=functions)

    @staticmethod
    def _parse_inputs_outputs(items):
        result = []
        for item in items:
            if 'components' in item:
                result.append(OGAbiFunction(
                    name=item['name'],
                    inputs=OGAbi._parse_inputs_outputs(item['components']),
                    outputs=[],
                    stateMutability=''
                ))
            else:
                result.append(f"{item['name']}:{item['type']}")
        return result