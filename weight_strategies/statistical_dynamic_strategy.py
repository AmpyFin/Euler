"""
Statistical Dynamic Strategy.

Advanced statistical weighting with auto-discovery and regime adaptation.
"""

from typing import Dict
from .base_strategy import BaseWeightStrategy


class StatisticalDynamicStrategy(BaseWeightStrategy):
    """Advanced statistical weighting with auto-discovery and regime adaptation."""
    
    def __init__(self):
        super().__init__()
        # Mapping from display names to internal names for the statistical system
        self.display_to_internal = {
            "Buffett Indicator": "buffett_indicator",
            "Put/Call Ratio": "put_call_ratio", 
            "^SKEW": "skew_index",
            "Near-term Stress Ratio": "near_term_stress_ratio",
            "3M Term Slope": "three_month_term_slope",
            "6M Term Slope": "six_month_term_slope"
        }
        # Reverse mapping
        self.internal_to_display = {v: k for k, v in self.display_to_internal.items()}
    
    def calculate_weights(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """Use the sophisticated auto-discovery system."""
        try:
            from registries.dynamic_statistical_weights import auto_discovery_weight_calculator
            
            # Convert display names to internal names for the statistical system
            internal_scores = {}
            for display_name, score in current_scores.items():
                internal_name = self.display_to_internal.get(display_name, display_name)
                internal_scores[internal_name] = score
            
            # Get weights using internal names
            internal_weights = auto_discovery_weight_calculator.calculate_dynamic_weights(internal_scores)
            
            # Convert back to display names
            display_weights = {}
            for internal_name, weight in internal_weights.items():
                display_name = self.internal_to_display.get(internal_name, internal_name)
                display_weights[display_name] = weight
            
            self._validate_weights(display_weights)
            return display_weights
            
        except Exception as e:
            # Fallback to equal weights if statistical system fails
            return self._equal_weights_fallback(current_scores)
    
    def get_name(self) -> str:
        return "Statistical Dynamic"
    
    def get_description(self) -> str:
        return (
            "Advanced statistical weighting strategy with auto-discovery and regime adaptation capabilities. "
            "Automatically discovers new indicators, profiles their statistical characteristics, and assigns "
            "weights based on real-time risk analysis. Features include: regime-sensitive weighting that "
            "adapts to market conditions (euphoria vs crisis), cross-correlation analysis to reduce redundancy, "
            "historical performance tracking, and automatic risk-based allocation where higher risk scores "
            "receive higher weights. The most sophisticated strategy, ideal for production environments "
            "requiring adaptive, statistically-driven risk assessment."
        )
    
    def get_category(self) -> str:
        return "Adaptive"
    
    def get_complexity(self) -> str:
        return "Advanced"
