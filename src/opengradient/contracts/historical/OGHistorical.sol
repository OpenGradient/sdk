// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "../types/CommonTypes.sol";
import "../og_inference/OGInference.sol";

interface OGHistorical {
    function queryHistoricalCandles(HistoricalInputQuery memory input) external returns (TensorLib.Number[] memory);
    function runInferenceOnPriceFeed(string memory model_id, string memory input_name, HistoricalInputQuery memory input) external returns (ModelOutput memory);
}