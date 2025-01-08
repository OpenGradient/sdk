// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import "../IModelExecutor.sol";
import "../historical/OGHistorical.sol";
import "../types/CommonTypes.sol";
import "../og_inference/OGInference.sol";

contract ModelExecutorHistorical is IModelExecutor {
    OGHistorical public historicalContract;
    ModelOutput private inferenceResult;
    string private modelCID;
    HistoricalInputQuery private inputQuery;
    string private inputTensorName;

    event InferenceResultEmitted(address indexed caller, ModelOutput result);

    constructor(
        string memory _modelCID,
        HistoricalInputQuery memory _inputQuery,
        address _historicalContractAddress,
        string memory _inputTensorName
    ) {
        modelCID = _modelCID;
        inputQuery = _inputQuery;
        historicalContract = OGHistorical(_historicalContractAddress);
        inputTensorName = _inputTensorName;
    }

    function run() public override {
        inferenceResult = historicalContract.runInferenceOnPriceFeed(
            modelCID,
            inputTensorName,
            inputQuery
        );

        emit InferenceResultEmitted(msg.sender, inferenceResult);
    }

    function getInferenceResult() public view override returns (ModelOutput memory) {
        return inferenceResult;
    }
}