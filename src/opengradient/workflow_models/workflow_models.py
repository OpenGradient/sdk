"""Repository of OpenGradient quantitative workflow models."""

import opengradient as og
from .constants import (
    ETH_USDT_1_HOUR_VOLATILITY_ADDRESS,
    BTC_1_HOUR_PRICE_FORECAST_ADDRESS,
    ETH_1_HOUR_PRICE_FORECAST_ADDRESS,
    SOL_1_HOUR_PRICE_FORECAST_ADDRESS,
    SUI_1_HOUR_PRICE_FORECAST_ADDRESS,
    SUI_30_MINUTE_PRICE_FORECAST_ADDRESS,
    SUI_6_HOUR_PRICE_FORECAST_ADDRESS,
)
from .utils import read_workflow_wrapper
from .types import WorkflowModelOutput


def read_eth_usdt_one_hour_volatility_forecast() -> WorkflowModelOutput:
    """
    Read from the ETH/USDT one hour volatility forecast model workflow on the OpenGradient network.

    More information on this model can be found at https://hub.opengradient.ai/models/OpenGradient/og-1hr-volatility-ethusdt.
    """
    return read_workflow_wrapper(
        contract_address=ETH_USDT_1_HOUR_VOLATILITY_ADDRESS, format_function=lambda x: format(float(x.numbers["Y"].item()), ".10%")
    )


def read_btc_1_hour_price_forecast() -> WorkflowModelOutput:
    """
    Read from the BTC one hour return forecast workflow on the OpenGradient network.

    More information on this model can be found at https://hub.opengradient.ai/models/OpenGradient/og-btc-1hr-forecast.
    """
    return read_workflow_wrapper(
        contract_address=BTC_1_HOUR_PRICE_FORECAST_ADDRESS,
        format_function=lambda x: format(float(x.numbers["regression_output"].item()), ".10%"),
    )


def read_eth_1_hour_price_forecast() -> WorkflowModelOutput:
    """
    Read from the ETH one hour return forecast workflow on the OpenGradient network.

    More information on this model can be found at https://hub.opengradient.ai/models/OpenGradient/og-eth-1hr-forecast.
    """
    return read_workflow_wrapper(
        contract_address=ETH_1_HOUR_PRICE_FORECAST_ADDRESS,
        format_function=lambda x: format(float(x.numbers["regression_output"].item()), ".10%"),
    )


def read_sol_1_hour_price_forecast() -> WorkflowModelOutput:
    """
    Read from the SOL one hour return forecast workflow on the OpenGradient network.

    More information on this model can be found at https://hub.opengradient.ai/models/OpenGradient/og-sol-1hr-forecast.
    """
    return read_workflow_wrapper(
        contract_address=SOL_1_HOUR_PRICE_FORECAST_ADDRESS,
        format_function=lambda x: format(float(x.numbers["regression_output"].item()), ".10%"),
    )


def read_sui_1_hour_price_forecast() -> WorkflowModelOutput:
    """
    Read from the SUI one hour return forecast workflow on the OpenGradient network.

    More information on this model can be found at https://hub.opengradient.ai/models/OpenGradient/og-sui-1hr-forecast.
    """
    return read_workflow_wrapper(
        contract_address=SUI_1_HOUR_PRICE_FORECAST_ADDRESS,
        format_function=lambda x: format(float(x.numbers["regression_output"].item()), ".10%"),
    )


def read_sui_usdt_30_min_price_forecast() -> WorkflowModelOutput:
    """
    Read from the SUI/USDT pair 30 min return forecast workflow on the OpenGradient network.

    More information on this model can be found at https://hub.opengradient.ai/models/OpenGradient/og-30min-return-suiusdt.
    """
    return read_workflow_wrapper(
        contract_address=SUI_30_MINUTE_PRICE_FORECAST_ADDRESS,
        format_function=lambda x: format(float(x.numbers["destandardized_prediction"].item()), ".10%"),
    )


def read_sui_usdt_6_hour_price_forecast() -> WorkflowModelOutput:
    """
    Read from the SUI/USDT pair 6 hour return forecast workflow on the OpenGradient network.

    More information on this model can be found at https://hub.opengradient.ai/models/OpenGradient/og-6h-return-suiusdt.
    """
    return read_workflow_wrapper(
        contract_address=SUI_6_HOUR_PRICE_FORECAST_ADDRESS,
        format_function=lambda x: format(float(x.numbers["destandardized_prediction"].item()), ".10%"),
    )
