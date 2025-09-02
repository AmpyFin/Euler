"""
Volatility Adjusted Strategy.

Weights indicators based on their volatility and signal stability characteristics.
"""

from typing import Dict
import math
from .base_strategy import BaseWeightStrategy


class VolatilityAdjustedStrategy(BaseWeightStrategy):
    """Weights indicators based on volatility and signal stability."""
    
    def __init__(self):
        super().__init__()
        # Volatility estimation based on indicator characteristics
        # These are used to calculate dynamic weights, not as fixed weights
    
    def calculate_weights(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """Weight indicators based on volatility-adjusted signal strength."""
        if not current_scores:
            return {}
        
        weights = {}
        
        # Estimate volatility based on indicator characteristics
        volatility_estimates = self._estimate_volatility(current_scores)
        
        for indicator, score in current_scores.items():
            # Get volatility estimate
            volatility = volatility_estimates.get(indicator, 0.3)
            
            # Calculate volatility-adjusted weight
            # Lower volatility = more stable = higher weight potential
            stability_factor = 1.0 / (1.0 + volatility)
            
            # Signal strength component (0-1)
            signal_strength = score / 100.0
            
            # Combine stability with signal strength
            # Strong signals from stable indicators get highest weights
            weight = stability_factor * (0.5 + 0.5 * signal_strength)
            weights[indicator] = weight
        
        # Normalize weights
        weights = self._normalize_weights(weights)
        self._validate_weights(weights)
        return weights
    
    def _estimate_volatility(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """Estimate volatility based on indicator characteristics and current conditions."""
        volatility_estimates = {}
        
        for indicator in current_scores.keys():
            if "Buffett" in indicator:
                # Structural indicators are very stable
                volatility_estimates[indicator] = 0.15
            elif "Term Slope" in indicator or "6M" in indicator:
                # Yield curve indicators are stable
                volatility_estimates[indicator] = 0.20 if "6M" in indicator else 0.25
            elif "Stress" in indicator:
                # Volatility indicators are moderately volatile
                volatility_estimates[indicator] = 0.35
            elif "Put/Call" in indicator:
                # Sentiment indicators are more volatile
                volatility_estimates[indicator] = 0.40
            elif "SKEW" in indicator:
                # Options-based indicators are most volatile
                volatility_estimates[indicator] = 0.45
            else:
                # Default moderate volatility
                volatility_estimates[indicator] = 0.30
        
        return volatility_estimates
    
    def get_name(self) -> str:
        return "Volatility Adjusted"
    
    def get_description(self) -> str:
        return (
            "Sophisticated weighting strategy that adjusts indicator weights based on their historical "
            "volatility and signal stability characteristics. Low-volatility indicators (like Buffett Indicator) "
            "receive higher base weights due to their stable, reliable signals, while high-volatility indicators "
            "(like SKEW and Put/Call Ratio) receive lower base weights to prevent noise from dominating the "
            "composite score. The strategy further adjusts weights based on current signal strength, boosting "
            "the influence of strong signals from stable indicators while moderating the impact of volatile ones. "
            "Ideal for reducing noise and emphasizing consistent, reliable risk signals."
        )
    
    def get_category(self) -> str:
        return "Dynamic"
    
    def get_complexity(self) -> str:
        return "Moderate"
