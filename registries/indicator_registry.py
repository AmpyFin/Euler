"""
Registry mapping indicator names to their corresponding data adapters.
"""
from typing import Dict, Type, List

from adapters.adapter import Adapter
from adapters.yfinance_adapter import YFinanceAdapter
from adapters.buffet_indicator_adapter import BuffettIndicatorAdapter

from indicators.live_indicators.buffet_indicator import BuffettIndicator
from indicators.live_indicators.vix9d_indicator import VIX9DIndicator
from indicators.live_indicators.vix_indicator import VIXIndicator
from indicators.live_indicators.vix3m_indicator import VIX3MIndicator
from indicators.live_indicators.vix6m_indicator import VIX6MIndicator
from indicators.live_indicators.skew_indicator import SKEWIndicator
from indicators.live_indicators.cpc_indicator import CPCIndicator
from indicators.live_indicators.near_term_stress_ratio_indicator import NearTermStressRatioIndicator
from indicators.live_indicators.three_month_term_slope_indicator import ThreeMonthTermSlopeIndicator
from indicators.live_indicators.six_month_term_slope_indicator import SixMonthTermSlopeIndicator

# Registry mapping indicator class names to their adapter classes
indicator_to_adapter_registry: Dict[str, Type[Adapter]] = {
    # VIX Series
    "VIX9DIndicator": YFinanceAdapter,         # 9-day VIX
    "VIXIndicator": YFinanceAdapter,           # Standard 30-day VIX
    "VIX3MIndicator": YFinanceAdapter,         # 3-month VIX
    "VIX6MIndicator": YFinanceAdapter,         # 6-month VIX
    
    # Market Sentiment
    "SKEWIndicator": YFinanceAdapter,          # CBOE SKEW Index
    "CPCIndicator": YFinanceAdapter,           # Put/Call Ratio
    
    # Term Structure Ratios
    "NearTermStressRatioIndicator": YFinanceAdapter,      # VIX9D/VIX
    "ThreeMonthTermSlopeIndicator": YFinanceAdapter,      # VIX/VIX3M
    "SixMonthTermSlopeIndicator": YFinanceAdapter,        # VIX/VIX6M
    
    # Valuation Metrics
    "BuffettIndicator": BuffettIndicatorAdapter,          # Market Cap / GDP
}

# List of all available indicator classes
indicators: List[Type] = [
    VIX9DIndicator,
    VIXIndicator,
    VIX3MIndicator,
    VIX6MIndicator,
    SKEWIndicator,
    CPCIndicator,
    NearTermStressRatioIndicator,
    ThreeMonthTermSlopeIndicator,
    SixMonthTermSlopeIndicator,
    BuffettIndicator,
]

indicator_to_weights: Dict[str, float] = {
    "^VIX9D": 0.11,                            # 9-day VIX
    "^VIX": 0.11,                              # VIX (1M)
    "^VIX3M": 0.09,                            # VIX3M
    "^VIX6M": 0.08,                            # VIX6M
    "Near-term Stress Ratio": 0.07,            # Near-Term Stress (9D/1M)
    "3M Term Slope": 0.07,                     # 3M Term Slope (1M/3M)
    "6M Term Slope": 0.06,                     # 6M Term Slope (1M/6M)
    "^SKEW": 0.11,                             # SKEW Index
    "Put/Call Ratio": 0.15,                    # Put/Call Ratio
    "Buffett Indicator": 0.15,                 # Buffett Indicator
}