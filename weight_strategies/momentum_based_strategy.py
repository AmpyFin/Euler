"""
Momentum Based Strategy.

Weights indicators based on the momentum and trend direction of their risk scores.
"""

from typing import Dict
from .base_strategy import BaseWeightStrategy


class MomentumBasedStrategy(BaseWeightStrategy):
    """Weights indicators based on risk score momentum and trend direction."""
    
    def __init__(self):
        super().__init__()
        # Simulated historical scores for momentum calculation
        # In production, these would be maintained from actual historical data
        self.historical_scores = {
            "Buffett Indicator": [95, 98, 100, 100, 100],  # Strong upward momentum
            "Put/Call Ratio": [65, 68, 70, 72, 70],        # Moderate momentum, recent plateau
            "^SKEW": [85, 90, 95, 100, 100],               # Strong upward momentum
            "Near-term Stress Ratio": [40, 35, 32, 30, 32], # Downward then slight up
            "3M Term Slope": [50, 48, 46, 45, 46],         # Slight downward momentum
            "6M Term Slope": [35, 32, 30, 29, 30],         # Bottoming pattern
        }
        
        # No fixed base weights - all weights calculated from momentum
    
    def _calculate_momentum(self, scores: list) -> float:
        """Calculate momentum score from historical data."""
        if len(scores) < 2:
            return 0.0
        
        # Simple momentum: recent change + trend strength
        recent_change = scores[-1] - scores[-2] if len(scores) >= 2 else 0
        
        # Trend strength: correlation with time
        if len(scores) >= 3:
            n = len(scores)
            sum_x = sum(range(n))
            sum_y = sum(scores)
            sum_xy = sum(i * score for i, score in enumerate(scores))
            sum_x2 = sum(i * i for i in range(n))
            
            # Pearson correlation coefficient
            numerator = n * sum_xy - sum_x * sum_y
            denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum(s*s for s in scores) - sum_y * sum_y)) ** 0.5
            trend_strength = numerator / denominator if denominator != 0 else 0
        else:
            trend_strength = 0
        
        # Combine recent change and trend strength
        momentum = recent_change * 0.6 + trend_strength * 20 * 0.4  # Scale trend_strength
        return momentum
    
    def calculate_weights(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """Weight indicators based on momentum and trend direction."""
        if not current_scores:
            return {}
        
        weights = {}
        momentum_scores = {}
        
        # Calculate momentum for each indicator
        for indicator, current_score in current_scores.items():
            historical = self.historical_scores.get(indicator, [current_score] * 3)
            
            # Add current score to history (simulate real-time updates)
            recent_history = historical[-4:] + [current_score]
            momentum = self._calculate_momentum(recent_history)
            momentum_scores[indicator] = momentum
        
        # Normalize momentum scores to 0-1 range
        min_momentum = min(momentum_scores.values())
        max_momentum = max(momentum_scores.values())
        momentum_range = max_momentum - min_momentum
        
        for indicator, current_score in current_scores.items():            
            if momentum_range > 0:
                # Normalize momentum to 0-1
                normalized_momentum = (momentum_scores[indicator] - min_momentum) / momentum_range
                
                # Weight based on momentum strength
                # Strong positive momentum gets high weight, negative momentum gets low weight
                momentum_weight = 0.2 + 0.8 * normalized_momentum  # Range: 0.2 to 1.0
            else:
                # If no momentum range, use equal weighting
                momentum_weight = 1.0
            
            # Combine momentum with current risk level
            risk_level = current_score / 100.0
            
            # Final weight: momentum strength * risk amplification
            final_weight = momentum_weight * (0.7 + 0.3 * risk_level)
            weights[indicator] = final_weight
        
        # Normalize weights
        weights = self._normalize_weights(weights)
        self._validate_weights(weights)
        return weights
    
    def get_name(self) -> str:
        return "Momentum Based"
    
    def get_description(self) -> str:
        return (
            "Dynamic weighting strategy that emphasizes indicators showing strong momentum in their risk scores. "
            "Analyzes recent score changes and trend direction to identify indicators with accelerating risk signals. "
            "Indicators with strong upward momentum (increasing risk) receive higher weights, while those with "
            "downward momentum (decreasing risk) receive lower weights. This approach is particularly effective "
            "at catching emerging risks early and adapting quickly to changing market conditions. The strategy "
            "combines momentum analysis with current risk levels to provide a forward-looking risk assessment "
            "that anticipates rather than just reacts to market stress."
        )
    
    def get_category(self) -> str:
        return "Dynamic"
    
    def get_complexity(self) -> str:
        return "Moderate"
