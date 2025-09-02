"""
Market Risk Indicator Registry - Following Val architecture patterns.
Maps risk indicators to their data adapters and manages active providers.
"""

from typing import Dict, List, Type, Callable

from adapters.adapter import Adapter
from adapters.buffet_indicator_adapter import BuffettIndicatorAdapter
from adapters.yfinance_adapter import YFinanceAdapter
from indicators.risk_indicators.buffett_indicator import BuffettIndicator
from indicators.risk_indicators.cpc_indicator import CPCIndicator
from indicators.risk_indicators.near_term_stress_ratio_indicator import NearTermStressRatioIndicator
from indicators.risk_indicators.six_month_term_slope_indicator import SixMonthTermSlopeIndicator
from indicators.risk_indicators.skew_indicator import SKEWIndicator
from indicators.risk_indicators.three_month_term_slope_indicator import ThreeMonthTermSlopeIndicator


# ========== METRIC PROVIDER FACTORIES (Val Pattern) ==========
# Each indicator metric can have multiple data providers
_METRIC_PROVIDER_FACTORIES: Dict[str, Dict[str, Callable[[], Adapter]]] = {
    "buffett_indicator": {
        "fred_buffett": lambda: BuffettIndicatorAdapter(),
    },
    "put_call_ratio": {
        "yfinance_spy_options": lambda: YFinanceAdapter(),
    },
    "skew_index": {
        "yfinance_skew": lambda: YFinanceAdapter(),
    },
    "near_term_stress_ratio": {
        "yfinance_vix_term": lambda: YFinanceAdapter(),
    },
    "three_month_term_slope": {
        "yfinance_vix_term": lambda: YFinanceAdapter(),
    },
    "six_month_term_slope": {
        "yfinance_vix_term": lambda: YFinanceAdapter(),
    },
}

# ========== ACTIVE PROVIDERS (Val Pattern) ==========
# Exactly one active provider per metric
_ACTIVE_METRIC_PROVIDER: Dict[str, str] = {
    "buffett_indicator": "fred_buffett",
    "put_call_ratio": "yfinance_spy_options",
    "skew_index": "yfinance_skew",
    "near_term_stress_ratio": "yfinance_vix_term",
    "three_month_term_slope": "yfinance_vix_term",
    "six_month_term_slope": "yfinance_vix_term",
    
}

# ========== INDICATOR FACTORIES (Val Pattern) ==========
# Maps metric names to indicator classes
_INDICATOR_FACTORIES: Dict[str, Callable[[], object]] = {
    "buffett_indicator": lambda: BuffettIndicator,
    "put_call_ratio": lambda: CPCIndicator,
    "skew_index": lambda: SKEWIndicator,
    "near_term_stress_ratio": lambda: NearTermStressRatioIndicator,
    "three_month_term_slope": lambda: ThreeMonthTermSlopeIndicator,
    "six_month_term_slope": lambda: SixMonthTermSlopeIndicator,
    
}

# ========== ENABLED INDICATORS (Val Pattern) ==========
# Only these indicators will be used in risk scoring
_ENABLED_INDICATORS: List[str] = [
    "buffett_indicator",
    "put_call_ratio", 
    "skew_index",
    "near_term_stress_ratio",
    "three_month_term_slope",
    "six_month_term_slope",

]

# ========== STATISTICAL RISK WEIGHTS ==========
# Dynamic weights calculated using statistical analysis
# See statistical_weights.py for the sophisticated weighting algorithm

def get_dynamic_weights(current_scores: Dict[str, float]) -> Dict[str, float]:
    """
    Get weights using the currently configured weighting method.
    
    This system supports multiple weighting methods:
    1. Statistical Dynamic: Auto-discovery with regime adaptation (default)
    2. Linear Static: Traditional fixed weights
    3. Equal Weight: Simple equal weighting
    4. Risk Proportional: Weights proportional to risk scores
    
    Configure method using weight_registry or control.py
    
    Args:
        current_scores: Dict of indicator names to current risk scores (0-100)
        
    Returns:
        Dict of indicator names to weights (sum = 1.0)
    """
    from registries.weight_registry import get_current_weights
    return get_current_weights(current_scores)

# Fallback static weights (only used if statistical calculation fails)
_FALLBACK_WEIGHTS: Dict[str, float] = {
    "buffett_indicator": 0.30,        # Primary valuation risk gauge
    "put_call_ratio": 0.15,           # Market sentiment/positioning
    "skew_index": 0.10,               # Tail risk pricing
    "near_term_stress_ratio": 0.20,   # VIX term structure stress
    "three_month_term_slope": 0.15,   # Medium-term volatility regime
    "six_month_term_slope": 0.10,     # Long-term volatility backdrop
}

# ========== PUBLIC API (Val Pattern) ==========

def get_active_provider(metric: str) -> Adapter:
    """Get the active data provider for a metric."""
    if metric not in _ACTIVE_METRIC_PROVIDER:
        raise ValueError(f"No active provider configured for metric: {metric}")
    
    provider_name = _ACTIVE_METRIC_PROVIDER[metric]
    
    if metric not in _METRIC_PROVIDER_FACTORIES:
        raise ValueError(f"No providers available for metric: {metric}")
    
    if provider_name not in _METRIC_PROVIDER_FACTORIES[metric]:
        raise ValueError(f"Provider '{provider_name}' not found for metric: {metric}")
    
    return _METRIC_PROVIDER_FACTORIES[metric][provider_name]()

def get_indicator_factory(metric: str) -> Callable[[], object]:
    """Get the indicator factory for a metric."""
    if metric not in _INDICATOR_FACTORIES:
        raise ValueError(f"No indicator factory for metric: {metric}")
    return _INDICATOR_FACTORIES[metric]

def get_enabled_indicators() -> List[str]:
    """Get list of enabled indicator metrics."""
    return _ENABLED_INDICATORS.copy()

def get_indicator_weight(metric: str, current_scores: Dict[str, float] = None) -> float:
    """
    Get the risk weight for an indicator.
    
    Args:
        metric: The indicator metric name
        current_scores: Optional dict of current scores for dynamic weighting
        
    Returns:
        Weight for the indicator (0.0 to 1.0)
    """
    if current_scores:
        # Use dynamic statistical weighting
        try:
            dynamic_weights = get_dynamic_weights(current_scores)
            return dynamic_weights.get(metric, 0.0)
        except Exception as e:
            # Fall back to static weights on error
            return _FALLBACK_WEIGHTS.get(metric, 0.0)
    else:
        # Use fallback static weights
        return _FALLBACK_WEIGHTS.get(metric, 0.0)
