"""
Risk Proportional Strategy.

Weights indicators directly proportional to their current risk scores.
"""

from typing import Dict
from .base_strategy import BaseWeightStrategy


class RiskProportionalStrategy(BaseWeightStrategy):
    """Weights directly proportional to current risk scores."""
    
    def calculate_weights(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """Weight indicators proportionally to their current risk scores."""
        if not current_scores:
            return {}
        
        # Use risk scores as weights (higher risk = higher weight)
        total_risk = sum(current_scores.values())
        
        if total_risk > 0:
            weights = {indicator: score/total_risk for indicator, score in current_scores.items()}
            self._validate_weights(weights)
            return weights
        else:
            # Fallback to equal weights if all scores are zero
            return self._equal_weights_fallback(current_scores)
    
    def get_name(self) -> str:
        return "Risk Proportional"
    
    def get_description(self) -> str:
        return (
            "Dynamic weighting strategy that assigns weights directly proportional to current risk scores. "
            "Indicators showing higher risk levels automatically receive higher weights in the composite calculation. "
            "This approach maximizes the influence of currently elevated risk signals while minimizing the impact "
            "of low-risk indicators. Particularly effective during crisis periods when certain indicators "
            "spike to extreme levels, ensuring the composite score reflects the most pressing risks. "
            "Simple yet responsive to changing market conditions."
        )
    
    def get_category(self) -> str:
        return "Dynamic"
    
    def get_complexity(self) -> str:
        return "Simple"
