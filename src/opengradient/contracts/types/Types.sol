// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

enum CandleOrder {
    Ascending,
    Descending
}

enum CandleType {
    High,
    Low,
    Open,
    Close
}

struct HistoricalInputQuery {
    string currency_pair;
    uint32 total_candles;
    uint32 candle_duration_in_mins;
    CandleOrder order;
    CandleType[] candle_types;
}

library TensorLib {
    struct Number {
        uint256 value;
    }
}

struct ModelOutput {
    uint256 value;
} 