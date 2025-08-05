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

indicator_to_weights = {
    "Buffett Indicator":       0.20,  # valuation "pilot light" sets baseline risk
    "SPY Put/Call Ratio":      0.10,  # flows, but lighter than a pure tactical model
    "^VIX9D":                  0.07,  # shock sensor
    "Near-term Stress Ratio":  0.12,  # VIX9D / VIX(1M) → backwardation/stress
    "3M Term Slope":           0.16,  # VIX(1M) / VIX(3M) → regime backdrop
    "6M Term Slope":           0.12,  # VIX(1M) / VIX(6M)
    "^VIX":                    0.07,  # 30-day implied level
    "^SKEW":                   0.06,  # priced tail risk
    "^VIX3M":                  0.06,  # medium anchor
    "^VIX6M":                  0.04,  # slow anchor
}
