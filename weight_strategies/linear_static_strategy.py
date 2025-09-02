"""
Linear Static Strategy.

Traditional fixed weights based on expert judgment and historical analysis.
"""

from typing import Dict
from .base_strategy import BaseWeightStrategy


class LinearStaticStrategy(BaseWeightStrategy):
    """Traditional fixed weights based on expert judgment."""
    
    def __init__(self):
        super().__init__()
        # Fixed weights based on traditional risk assessment and expert judgment
        # These weights reflect the historical importance and predictive power of each indicator
        self.static_weights = {
            "Buffett Indicator": 0.25,        # Structural overvaluation - highest weight
            "Put/Call Ratio": 0.20,           # Market sentiment and positioning
            "Near-term Stress Ratio": 0.20,   # Immediate volatility stress
            "^SKEW": 0.15,                     # Tail risk pricing and crash probability
            "3M Term Slope": 0.12,             # Medium-term yield curve structure
            "6M Term Slope": 0.08,             # Long-term yield curve structure
        }
    
    def calculate_weights(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """Return fixed weights regardless of current conditions."""
        # Only include indicators that are actually present
        present_indicators = set(current_scores.keys())
        available_weights = {k: v for k, v in self.static_weights.items() if k in present_indicators}
        
        # Normalize to sum to 1.0
        total_weight = sum(available_weights.values())
        if total_weight > 0:
            weights = {k: v/total_weight for k, v in available_weights.items()}
            self._validate_weights(weights)
            return weights
        else:
            # Fallback to equal weights if no known indicators
            return self._equal_weights_fallback(current_scores)
    
    def get_name(self) -> str:
        return "Linear Static"
    
    def get_description(self) -> str:
        return (
            "Traditional fixed weighting strategy based on expert judgment and historical analysis. "
            "Assigns predetermined weights that remain constant regardless of market conditions: "
            "Buffett Indicator (25%) for structural overvaluation, Put/Call Ratio (20%) for sentiment, "
            "Near-term Stress (20%) for immediate volatility, SKEW (15%) for tail risk, "
            "and term structure indicators (12%/8%) for yield curve analysis. "
            "Provides consistent, interpretable results based on established risk assessment principles."
        )
    
    def get_category(self) -> str:
        return "Static"
    
    def get_complexity(self) -> str:
        return "Simple"
