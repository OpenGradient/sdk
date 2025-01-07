// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "../IModelExecutor.sol";
import "../historical/OGHistorical.sol";
import "../types/CommonTypes.sol";
import "../og_inference/OGInference.sol";

abstract contract ModelExecutorHistorical is IModelExecutor {
    OGHistorical public historicalContract;
    ModelOutput private inferenceResult;
    string private modelCID;
    HistoricalInputQuery private inputQuery;

    event InferenceResultEmitted(address indexed caller, string result);

    constructor(
        string memory _modelCID,
        HistoricalInputQuery memory _inputQuery,
        address _historicalContractAddress
    ) {
        modelCID = _modelCID;
        inputQuery = _inputQuery;
        historicalContract = OGHistorical(_historicalContractAddress);
    }

    function run() public {

        // CandleType[] memory candles = new CandleType[](4);
        //         candles[0]=CandleType.Open;
        //         candles[1]=CandleType.High;
        //         candles[2]=CandleType.Close;
        //         candles[3]=CandleType.Low;

        // HistoricalInputQuery memory input_query = HistoricalInputQuery({
        //     currency_pair: "ETH/USD",
        //     total_candles: 10,
        //     candle_duration_in_mins: 30, 
        //     order: CandleOrder.Ascending,
        //     candle_types: candles
        // });


        // inferenceResult = historicalContract.runInferenceOnPriceFeed( // To check
        //             "QmRhcpDXfYCKsimTmJYrAVM4Bbvck59Zb2onj3MHv9Kw5N",
        //             "open_high_low_close",
        //             input_query);

        // // Emit the result as an event
        emit InferenceResultEmitted(msg.sender, "test");
    }

    function getInferenceResult() external view override returns (ModelOutput memory) {
        return inferenceResult;
    }
} 