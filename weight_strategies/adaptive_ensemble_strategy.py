"""
Adaptive Ensemble Strategy.

Meta-strategy that combines multiple weighting approaches and adapts based on market conditions.
"""

from typing import Dict
from .base_strategy import BaseWeightStrategy


class AdaptiveEnsembleStrategy(BaseWeightStrategy):
    """Meta-strategy that combines multiple approaches based on market conditions."""
    
    def __init__(self):
        super().__init__()
        
        # Define market regimes based on composite risk score
        self.regime_thresholds = {
            "euphoria": (0, 30),      # Very low risk - dangerous complacency
            "normal": (30, 50),       # Normal market conditions
            "stress": (50, 70),       # Elevated stress
            "crisis": (70, 100),      # High stress/crisis conditions
        }
        
        # Strategy weights for each regime
        self.regime_strategies = {
            "euphoria": {
                "risk_proportional": 0.4,    # Emphasize any risk signals
                "momentum": 0.3,              # Catch emerging trends
                "volatility_adjusted": 0.2,   # Stable signals
                "linear_static": 0.1,         # Traditional baseline
            },
            "normal": {
                "statistical_dynamic": 0.3,   # Sophisticated analysis
                "linear_static": 0.25,        # Expert judgment
                "volatility_adjusted": 0.25,  # Signal stability
                "risk_proportional": 0.2,     # Current conditions
            },
            "stress": {
                "momentum": 0.35,             # Catch accelerating risks
                "risk_proportional": 0.3,     # Current high risks
                "statistical_dynamic": 0.2,   # Advanced analysis
                "volatility_adjusted": 0.15,  # Reduce noise
            },
            "crisis": {
                "risk_proportional": 0.4,     # Maximize high-risk signals
                "momentum": 0.3,              # Track rapid changes
                "linear_static": 0.2,         # Reliable baseline
                "equal_weight": 0.1,          # Diversification
            }
        }
    
    def _determine_regime(self, current_scores: Dict[str, float]) -> str:
        """Determine current market regime based on average risk score."""
        if not current_scores:
            return "normal"
        
        avg_score = sum(current_scores.values()) / len(current_scores)
        
        for regime, (low, high) in self.regime_thresholds.items():
            if low <= avg_score < high:
                return regime
        
        return "crisis" if avg_score >= 70 else "normal"
    
    def _get_strategy_weights(self, strategy_name: str, current_scores: Dict[str, float]) -> Dict[str, float]:
        """Get weights from actual strategy implementations."""
        try:
            # Import and use actual strategy implementations
            if strategy_name == "equal_weight":
                from .equal_weight_strategy import EqualWeightStrategy
                strategy = EqualWeightStrategy()
                return strategy.calculate_weights(current_scores)
            
            elif strategy_name == "linear_static":
                from .linear_static_strategy import LinearStaticStrategy
                strategy = LinearStaticStrategy()
                return strategy.calculate_weights(current_scores)
            
            elif strategy_name == "risk_proportional":
                from .risk_proportional_strategy import RiskProportionalStrategy
                strategy = RiskProportionalStrategy()
                return strategy.calculate_weights(current_scores)
            
            elif strategy_name == "volatility_adjusted":
                from .volatility_adjusted_strategy import VolatilityAdjustedStrategy
                strategy = VolatilityAdjustedStrategy()
                return strategy.calculate_weights(current_scores)
            
            elif strategy_name == "momentum":
                from .momentum_based_strategy import MomentumBasedStrategy
                strategy = MomentumBasedStrategy()
                return strategy.calculate_weights(current_scores)
            
            elif strategy_name == "statistical_dynamic":
                from .statistical_dynamic_strategy import StatisticalDynamicStrategy
                strategy = StatisticalDynamicStrategy()
                return strategy.calculate_weights(current_scores)
            
            else:
                return self._equal_weights_fallback(current_scores)
                
        except Exception as e:
            # Fallback to equal weights if strategy fails
            return self._equal_weights_fallback(current_scores)
    
    def calculate_weights(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate ensemble weights based on current market regime."""
        if not current_scores:
            return {}
        
        # Determine current market regime
        regime = self._determine_regime(current_scores)
        
        # Get strategy mix for this regime
        strategy_mix = self.regime_strategies.get(regime, self.regime_strategies["normal"])
        
        # Calculate weighted combination of strategies
        ensemble_weights = {indicator: 0.0 for indicator in current_scores.keys()}
        
        for strategy_name, strategy_weight in strategy_mix.items():
            strategy_indicator_weights = self._get_strategy_weights(strategy_name, current_scores)
            
            # Add this strategy's contribution to the ensemble
            for indicator in ensemble_weights.keys():
                if indicator in strategy_indicator_weights:
                    ensemble_weights[indicator] += strategy_weight * strategy_indicator_weights[indicator]
        
        # Normalize final weights
        ensemble_weights = self._normalize_weights(ensemble_weights)
        self._validate_weights(ensemble_weights)
        return ensemble_weights
    
    def get_name(self) -> str:
        return "Adaptive Ensemble"
    
    def get_description(self) -> str:
        return (
            "Most sophisticated meta-strategy that combines multiple weighting approaches and adapts based on "
            "current market conditions. Automatically determines market regime (euphoria, normal, stress, crisis) "
            "and applies the optimal mix of strategies for each condition. In euphoria periods, emphasizes "
            "risk-proportional and momentum strategies to catch emerging risks. During normal conditions, "
            "balances statistical dynamic, linear static, and volatility-adjusted approaches. In stress periods, "
            "prioritizes momentum and risk-proportional strategies to track accelerating risks. During crisis, "
            "maximizes risk-proportional weighting while maintaining momentum tracking. This adaptive approach "
            "provides the most robust and context-aware risk assessment across all market conditions."
        )
    
    def get_category(self) -> str:
        return "Adaptive"
    
    def get_complexity(self) -> str:
        return "Advanced"
