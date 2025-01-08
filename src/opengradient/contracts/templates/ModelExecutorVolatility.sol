// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import "../IModelExecutor.sol";
import "../historical/OGHistorical.sol";
import "../types/CommonTypes.sol";
import "../og_inference/OGInference.sol";

/**
 * @title ModelExecutorVolatility
 * @dev Implementation of IModelExecutor to predict ETH/USDT volatility using OpenGradient's model.
 */
contract ModelExecutorVolatility is IModelExecutor {
  

    constructor() {
        address historicalContractAddress = 0x00000000000000000000000000000000000000F5;

        historicalContract = OGHistorical(historicalContractAddress);
    }

    event InferenceResultEmitted(address indexed caller, ModelOutput result);

    /// @dev Stores the result of the last model inference
    ModelOutput private inferenceResult;
    OGHistorical public historicalContract;


    /**
     * @dev Executes the volatility model task.
     */
    function run() public override {

        CandleType[] memory candles = new CandleType[](4);
                candles[0]=CandleType.Open;
                candles[1]=CandleType.High;
                candles[2]=CandleType.Close;
                candles[3]=CandleType.Low;

        HistoricalInputQuery memory input_query = HistoricalInputQuery({
            currency_pair: "ETH/USD",
            total_candles: 10,
            candle_duration_in_mins: 30, 
            order: CandleOrder.Ascending,
            candle_types: candles
        });

        inferenceResult = historicalContract.runInferenceOnPriceFeed( // To check
                    "QmRhcpDXfYCKsimTmJYrAVM4Bbvck59Zb2onj3MHv9Kw5N",
                    "open_high_low_close",
                    input_query);

                // Emit the result as an event
                emit InferenceResultEmitted(msg.sender, inferenceResult);
            }

    /**
     * @dev Retrieves the result of the last executed task.
     * @return The stored `ModelOutput`.
     */
    function getInferenceResult() public view override returns (ModelOutput memory) {
        return inferenceResult;
    }
}