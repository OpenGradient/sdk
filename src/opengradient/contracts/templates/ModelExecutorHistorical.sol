// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "../IModelExecutor.sol";
import "../historical/OGHistorical.sol";
import "../types/CommonTypes.sol";
import "../og_inference/OGInference.sol";

contract ModelExecutorHistorical is IModelExecutor {
    OGHistorical public historicalContract;
    TensorLib.Number[4] private resultValues;  // Fixed size array for OHLC values
    uint8 private numValues;  // Track how many values we actually have
    string private modelCID;
    HistoricalInputQuery private inputQuery;
    OGInference private inferenceContract;

    event InferenceResultEmitted(address indexed caller, ModelOutput result);

    constructor(
        string memory _modelCID,
        HistoricalInputQuery memory _inputQuery,
        address _historicalContractAddress
    ) {
        modelCID = _modelCID;
        inputQuery = _inputQuery;
        historicalContract = OGHistorical(_historicalContractAddress);
        inferenceContract = OGInference(OG_INFERENCE_ADDRESS);
        numValues = 0;
    }

    function run(
        string memory _modelCID,
        uint8 _inferenceMode,
        ModelInput memory _input
    ) public override {
        // Update modelCID if provided
        if (bytes(_modelCID).length > 0) {
            modelCID = _modelCID;
        }
        
        // Query historical data first
        TensorLib.Number[] memory historicalData = historicalContract.queryHistoricalCandles(inputQuery);
        
        // Create tensor from historical data
        TensorLib.MultiDimensionalNumberTensor[] memory numbers = new TensorLib.MultiDimensionalNumberTensor[](1);
        numbers[0] = TensorLib.numberTensor1D("open_high_low_close", historicalData);
        
        // Use provided input or create new one
        ModelInput memory modelInput = _input;
        if (_input.numbers.length == 0) {
            modelInput = ModelInput({
                numbers: numbers,
                strings: new TensorLib.StringTensor[](0)
            });
        }
        
        // Create and execute the inference request
        ModelInferenceRequest memory request = ModelInferenceRequest({
            mode: ModelInferenceMode(_inferenceMode),
            modelCID: modelCID,
            input: modelInput
        });
        
        // Run the inference through the inference contract
        ModelOutput memory result = inferenceContract.runModelInference(request);
        
        // Store all available numeric values
        if (result.numbers.length > 0) {
            TensorLib.Number[] memory values = result.numbers[0].values;
            numValues = uint8(values.length > 4 ? 4 : values.length);
            for (uint8 i = 0; i < numValues; i++) {
                resultValues[i] = values[i];
            }
        } else {
            numValues = 0;
        }
        
        emit InferenceResultEmitted(msg.sender, result);
    }

    function getInferenceResult() public view override returns (ModelOutput memory) {
        require(numValues > 0, "No inference result available");
        
        // Create a ModelOutput with all stored numeric values
        TensorLib.Number[] memory values = new TensorLib.Number[](numValues);
        for (uint8 i = 0; i < numValues; i++) {
            values[i] = resultValues[i];
        }
        
        TensorLib.MultiDimensionalNumberTensor[] memory numbers = new TensorLib.MultiDimensionalNumberTensor[](1);
        numbers[0] = TensorLib.numberTensor1D("result", values);
        
        TensorLib.StringTensor[] memory strings = new TensorLib.StringTensor[](0);
        TensorLib.JsonScalar[] memory jsons = new TensorLib.JsonScalar[](0);
        
        return ModelOutput(numbers, strings, jsons, false);
    }
} 