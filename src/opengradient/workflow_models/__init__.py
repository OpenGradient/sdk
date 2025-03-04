"""
OpenGradient Hardcoded Models
"""

from .workflow_models import *
from .types import WorkflowModelOutput

__all__ = [
    "read_eth_usdt_one_hour_volatility_forecast",
    "read_btc_1_hour_price_forecast",
    "read_eth_1_hour_price_forecast",
    "read_sol_1_hour_price_forecast",
    "read_sui_1_hour_price_forecast",
    "read_sui_usdt_30_min_price_forecast",
    "read_sui_usdt_6_hour_price_forecast",
    "WorkflowModelOutput",
]

__pdoc__ = {
    "read_eth_usdt_one_hour_volatility_forecast": False,
    "read_btc_1_hour_price_forecast": False,
    "read_eth_1_hour_price_forecast": False,
    "read_sol_1_hour_price_forecast": False,
    "read_sui_1_hour_price_forecast": False,
    "read_sui_usdt_30_min_price_forecast": False,
    "read_sui_usdt_6_hour_price_forecast": False,
    "WorkflowModelOutput": False,
}
