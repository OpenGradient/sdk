// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

/// @dev The OGInfernece contract's address.
address constant OG_INFERENCE_ADDRESS = 0x00000000000000000000000000000000000000F4;

/// @dev The OGInference contract's instance.
OGInference constant OG_INFERENCE_CONTRACT = OGInference(OG_INFERENCE_ADDRESS);

///////////
// LLM
///////////

enum LLMInferenceMode { VANILLA, TEE }

struct LLMCompletionRequest {
    LLMInferenceMode mode;
    string modelCID;
    string prompt;
    uint32 max_tokens;
    string[] stop_sequence;
    uint32 temperature; // 0-100
}

struct LLMCompletionResponse {
    string answer;
}

struct ToolDefinition {
    string description;
    string name;
    string parameters; // This must be a JSON 
}

struct LLMChatRequest {
    LLMInferenceMode mode;
    string modelCID;
    ChatMessage[] messages;
    ToolDefinition[] tools; 
    string tool_choice;
    uint32 max_tokens;
    string[] stop_sequence;
    uint32 temperature; // 0-100
}

struct LLMChatResponse {
    string finish_reason;
    ChatMessage message;
}

struct ChatMessage {
  string role;
  string content;
  string name;
  string tool_call_id; // only used for tool response
  ToolCall[] tool_calls;
}

struct ToolCall {
  string id;
  string name;
  string arguments; // formatted as json
}

///////////////
// ML Models
///////////////

enum ModelInferenceMode { VANILLA, ZK, TEE }

/**
 * Model inference request.
 */
struct ModelInferenceRequest {
    ModelInferenceMode mode;
    string modelCID;
    ModelInput input;
}

/**
 * Model input, made up of various tensors of either numbers or strings.
 */
struct ModelInput {
    TensorLib.MultiDimensionalNumberTensor[] numbers;
    TensorLib.StringTensor[] strings;
}

/**
 * Model output, made up of tensors of either numbers or strings, ordered
 * as defined by the model. 
 *
 * For example, if a model's output is: [number_tensor_1, string_tensor_1, number_tensor_2],
 * you could access them like this:
 * number_tensor_1 = output.numbers[0];
 * string_tensor_1 = output.strings[0];
 * number_tensor_2 = output.numbers[1];
 */
struct ModelOutput {
    TensorLib.MultiDimensionalNumberTensor[] numbers;
    TensorLib.StringTensor[] strings;
    TensorLib.JsonScalar[] jsons;
    bool is_simulation_result;
}

////////////////////////
// Inference Contract
////////////////////////

interface OGInference {
    function runModelInference(ModelInferenceRequest memory request) external returns (ModelOutput memory);

    function runLLMCompletion(LLMCompletionRequest memory request) external returns (LLMCompletionResponse memory);
    function runLLMChat(LLMChatRequest memory request) external returns (LLMChatResponse memory);
}

////////////////////////
// Tensor types
////////////////////////

library TensorLib {

    /**
    * Can be used to represent a floating-point number or integer.
    *
    * eg 10 can be represented as Number(10, 0),
    * and 1.5 can be represented as Number(15, 1)
    */
    struct Number {
        int128 value;
        int128 decimals;
    }

    struct MultiDimensionalNumberTensor {
        string name;
        Number[] values;
        uint32[] shape;
    }

    function numberTensor1D(string memory name, Number[] memory values) internal pure returns (MultiDimensionalNumberTensor memory) {
        uint32[] memory shape = new uint32[](1);
        shape[0] = uint32(values.length);

        return MultiDimensionalNumberTensor(name, values, shape);
    }

    function numberTensor2D(string memory name, Number[][] memory values) internal pure returns (MultiDimensionalNumberTensor memory) {
        require(values.length > 0 && values[0].length > 0, "Input array must be non-empty");
        
        uint32 rows = uint32(values.length);
        uint32 cols = uint32(values[0].length);
        
        for (uint i = 1; i < values.length; i++) {
            require(values[i].length == uint(cols), "All rows must have the same length");
        }
        
        Number[] memory flattenedValues = new Number[](uint(rows * cols));
        uint flatIndex = 0;
        for (uint i = 0; i < values.length; i++) {
            for (uint j = 0; j < values[i].length; j++) {
                flattenedValues[flatIndex] = values[i][j];
                flatIndex++;
            }
        }
        
        uint32[] memory shape = new uint32[](2);
        shape[0] = rows;
        shape[1] = cols;
        
        return MultiDimensionalNumberTensor(name, flattenedValues, shape);
    }

    function numberTensorND(string memory name, uint32[] memory dimensions) internal pure returns (MultiDimensionalNumberTensor memory) {
        require(dimensions.length > 0, "Dimensions array must not be empty");
        
        uint256 totalSize = 1;
        for (uint i = 0; i < dimensions.length; i++) {
            require(dimensions[i] > 0, "All dimensions must be positive");
            totalSize *= uint256(dimensions[i]);
        }
        
        Number[] memory emptyValues = new Number[](totalSize);
        
        return MultiDimensionalNumberTensor(name, emptyValues, dimensions);
    }

    function setValue(MultiDimensionalNumberTensor memory self, uint32 pos, Number memory value) internal pure {
        require(self.shape.length == 1, "This function is for 1D tensors only");
        uint32[] memory indices = new uint32[](1);
        indices[0] = pos;
        setValue(self, indices, value);
    }

    function setValue(MultiDimensionalNumberTensor memory self, uint32 row, uint32 col, Number memory value) internal pure {
        require(self.shape.length == 2, "This function is for 2D tensors only");
        uint32[] memory indices = new uint32[](2);
        indices[0] = row;
        indices[1] = col;
        setValue(self, indices, value);
    }

    function setValue(MultiDimensionalNumberTensor memory self, uint32 dim1, uint32 dim2, uint32 dim3, Number memory value) internal pure {
        require(self.shape.length == 3, "This function is for 3D tensors only");
        uint32[] memory indices = new uint32[](3);
        indices[0] = dim1;
        indices[1] = dim2;
        indices[2] = dim3;
        setValue(self, indices, value);
    }

    function setValue(MultiDimensionalNumberTensor memory self, uint32[] memory indices, Number memory value) internal pure {
        require(indices.length == self.shape.length, "Indices dimension mismatch");
        
        uint256 flatIndex = getFlatIndex(self.shape, indices);
        require(flatIndex < self.values.length, "Index out of bounds");
        
        self.values[flatIndex] = value;
    }

    function getValue(MultiDimensionalNumberTensor memory self, uint32[] memory indices) internal pure returns (Number memory) {
        require(indices.length == self.shape.length, "Indices dimension mismatch");
        
        uint256 flatIndex = getFlatIndex(self.shape, indices);
        require(flatIndex < self.values.length, "Index out of bounds");
        
        return self.values[flatIndex];
    }

    function getFlatIndex(uint32[] memory shape, uint32[] memory indices) private pure returns (uint256) {
        uint256 flatIndex = 0;
        uint256 multiplier = 1;

        for (uint256 i = shape.length; i > 0; i--) {
            require(indices[i-1] >= 0 && indices[i-1] < shape[i-1], "Index out of bounds");
            flatIndex += uint256(indices[i-1]) * multiplier;
            multiplier *= uint256(shape[i-1]);
        }

        return flatIndex;
    }

    struct StringTensor {
        string name;
        string[] values;
    }

    struct JsonScalar {
        string name;
        string value;
    }
}