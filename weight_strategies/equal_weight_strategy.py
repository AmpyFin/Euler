"""
Equal Weight Strategy.

Simple baseline strategy that assigns equal weights to all indicators.
"""

from typing import Dict
from .base_strategy import BaseWeightStrategy


class EqualWeightStrategy(BaseWeightStrategy):
    """Simple equal weighting for all indicators."""
    
    def calculate_weights(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """Assign equal weights to all indicators."""
        n = len(current_scores)
        if n > 0:
            equal_weight = 1.0 / n
            weights = {indicator: equal_weight for indicator in current_scores.keys()}
            self._validate_weights(weights)
            return weights
        return {}
    
    def get_name(self) -> str:
        return "Equal Weight"
    
    def get_description(self) -> str:
        return (
            "Simple equal weighting strategy that assigns identical weights (1/N) to all indicators. "
            "This serves as an unbiased baseline that treats all risk indicators with equal importance, "
            "making no assumptions about their relative predictive power or market significance. "
            "Ideal for benchmarking and situations where no prior knowledge exists about indicator effectiveness."
        )
    
    def get_category(self) -> str:
        return "Static"
    
    def get_complexity(self) -> str:
        return "Simple"
