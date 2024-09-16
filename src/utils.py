# from src.types import ModelInput, InferenceMode, Abi, ModelOutput, Number, NumberTensor, StringTensor
import numpy as np
import logging
from decimal import Decimal
from typing import Dict, List, Tuple

def convert_to_fixed_point(number: float) -> Tuple[int, int]:
    """
    Converts input number to the Number tensor used by the sequencer.

    Returns a tuple of (value, decimal)
    """
    decimal_val = Decimal(number).normalize()
    sign, digits, exponent = decimal_val.as_tuple()
    value = int(''.join(map(str, digits)))
    if sign:
        value = -value
    decimals = int(-exponent)
    return value, decimals

def convert_to_model_input(inputs: Dict[str, np.ndarray]) -> Tuple[List[Tuple[str, List[Tuple[int, int]]]], List[Tuple[str, List[str]]]]:
    """
    Expect SDK input to be a dict with the format
        key: tensor name
        value: np.array

        Note: np.array types must be float or string. Ints currently not supported.

    Return a tuple of (number tensors, string tensors) depending on the input type
    """
    logging.debug("Converting the following input dictionary to ModelInput: %s", inputs)
    number_tensors = []
    string_tensors = []
    for tensor_name, tensor_data in inputs.items():
        if issubclass(tensor_data.dtype.type, np.floating):
            # Convert each integer to a fixed point
            input = (tensor_name, [convert_to_fixed_point(i) for (i) in tensor_data])
            logging.debug("\tFloating tensor input: %s", input)

            number_tensors.append(input)
        elif issubclass(tensor_data.dtype.type, np.str_):
            input = (tensor_name, [s for s in tensor_data])
            logging.debug("\tString tensor input: %s", input)

            string_tensors.append(input)
        else:
            raise TypeError(f"Data type {tensor_data.dtype.type} not recognized")
        
    logging.debug("Number tensors: %s", number_tensors)
    logging.debug("String tensors: %s", string_tensors)
    return number_tensors, string_tensors 