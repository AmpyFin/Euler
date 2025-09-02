"""
Weight Registry - Centralized Management of Different Weighting Systems.

This module provides a clean interface to switch between different weighting
algorithms without changing core system code. All strategies are loaded from
the weight_strategies package.
"""

from typing import Dict, List, Optional
from enum import Enum
import logging

# Import all weight strategies
from weight_strategies import (
    EqualWeightStrategy,
    LinearStaticStrategy,
    RiskProportionalStrategy,
    StatisticalDynamicStrategy,
    VolatilityAdjustedStrategy,
    MomentumBasedStrategy,
    AdaptiveEnsembleStrategy
)
from weight_strategies.ml_adaptive_ensemble_strategy import MLAdaptiveEnsembleStrategy

logger = logging.getLogger(__name__)


class WeightingMethod(Enum):
    """Available weighting methods."""
    EQUAL_WEIGHT = "equal_weight"                    # Simple equal weighting
    LINEAR_STATIC = "linear_static"                  # Traditional fixed weights
    RISK_PROPORTIONAL = "risk_proportional"         # Weights proportional to risk scores
    STATISTICAL_DYNAMIC = "statistical_dynamic"     # Auto-discovery with regime adaptation
    VOLATILITY_ADJUSTED = "volatility_adjusted"     # Volatility-based weighting
    MOMENTUM_BASED = "momentum_based"                # Momentum-driven weighting
    ADAPTIVE_ENSEMBLE = "adaptive_ensemble"          # Meta-strategy combining approaches
    ML_ADAPTIVE_STACKING = "ml_adaptive_stacking"    # ML ensemble using stacking method
    ML_ADAPTIVE_VOTING = "ml_adaptive_voting"        # ML ensemble using voting method
    ML_ADAPTIVE_BLENDING = "ml_adaptive_blending"    # ML ensemble using blending method


# Configuration: Set the default weighting method here
DEFAULT_WEIGHTING_METHOD = WeightingMethod.MOMENTUM_BASED

# Alternative methods for different use cases:
# WeightingMethod.EQUAL_WEIGHT          # Baseline/benchmarking
# WeightingMethod.LINEAR_STATIC         # Conservative/traditional
# WeightingMethod.RISK_PROPORTIONAL     # Crisis-focused
# WeightingMethod.VOLATILITY_ADJUSTED   # Noise reduction
# WeightingMethod.MOMENTUM_BASED        # Trend following
# WeightingMethod.ADAPTIVE_ENSEMBLE     # Heuristic meta-strategy
# WeightingMethod.ML_ADAPTIVE_STACKING  # ML ensemble (most sophisticated)
# WeightingMethod.ML_ADAPTIVE_VOTING    # ML ensemble (robust averaging)
# WeightingMethod.ML_ADAPTIVE_BLENDING  # ML ensemble (custom weighting)


class WeightRegistry:
    """Registry for managing different weighting systems."""
    
    def __init__(self):
        """Initialize with all available weighting strategies."""
        self._strategies = {
            WeightingMethod.EQUAL_WEIGHT: EqualWeightStrategy(),
            WeightingMethod.LINEAR_STATIC: LinearStaticStrategy(),
            WeightingMethod.RISK_PROPORTIONAL: RiskProportionalStrategy(),
            WeightingMethod.STATISTICAL_DYNAMIC: StatisticalDynamicStrategy(),
            WeightingMethod.VOLATILITY_ADJUSTED: VolatilityAdjustedStrategy(),
            WeightingMethod.MOMENTUM_BASED: MomentumBasedStrategy(),
            WeightingMethod.ADAPTIVE_ENSEMBLE: AdaptiveEnsembleStrategy(),
            WeightingMethod.ML_ADAPTIVE_STACKING: MLAdaptiveEnsembleStrategy(ensemble_method="stacking"),
            WeightingMethod.ML_ADAPTIVE_VOTING: MLAdaptiveEnsembleStrategy(ensemble_method="voting"),
            WeightingMethod.ML_ADAPTIVE_BLENDING: MLAdaptiveEnsembleStrategy(ensemble_method="blending"),
        }
        
        # Use configured default method
        self._active_method = DEFAULT_WEIGHTING_METHOD
        
        logger.info(f"Weight Registry initialized with {len(self._strategies)} strategies")
        logger.info(f"Active method: {self._active_method.value}")
        logger.info(f"Available strategies: {[method.value for method in self._strategies.keys()]}")
    
    def set_active_method(self, method: WeightingMethod) -> None:
        """Set the active weighting method."""
        if method not in self._strategies:
            raise ValueError(f"Unknown weighting method: {method}")
        
        old_method = self._active_method
        self._active_method = method
        logger.info(f"Changed weighting method: {old_method.value} → {method.value}")
    
    def get_active_method(self) -> WeightingMethod:
        """Get the currently active weighting method."""
        return self._active_method
    
    def calculate_weights(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate weights using the active strategy."""
        strategy = self._strategies[self._active_method]
        weights = strategy.calculate_weights(current_scores)
        
        logger.debug(f"Calculated weights using {strategy.get_name()}: {weights}")
        return weights
    
    def get_available_methods(self) -> List[WeightingMethod]:
        """Get list of available weighting methods."""
        return list(self._strategies.keys())
    
    def get_method_info(self, method: WeightingMethod) -> Dict[str, str]:
        """Get information about a specific weighting method."""
        if method not in self._strategies:
            raise ValueError(f"Unknown weighting method: {method}")
        
        strategy = self._strategies[method]
        return {
            "name": strategy.get_name(),
            "description": strategy.get_description(),
            "category": strategy.get_category(),
            "complexity": strategy.get_complexity(),
            "active": method == self._active_method
        }
    
    def get_all_methods_info(self) -> Dict[str, Dict[str, str]]:
        """Get information about all available weighting methods."""
        return {
            method.value: self.get_method_info(method) 
            for method in self._strategies.keys()
        }


# Singleton instance for global use
weight_registry = WeightRegistry()


# Convenience functions for easy access
def set_weighting_method(method: WeightingMethod) -> None:
    """Set the active weighting method."""
    weight_registry.set_active_method(method)


def get_current_weights(current_scores: Dict[str, float]) -> Dict[str, float]:
    """Get weights using the currently active method."""
    return weight_registry.calculate_weights(current_scores)


def get_weighting_methods() -> Dict[str, Dict[str, str]]:
    """Get information about all available weighting methods."""
    return weight_registry.get_all_methods_info()


def configure_weighting_from_string(method_name: str) -> None:
    """Configure weighting method from string name."""
    method_map = {
        # Existing methods
        "equal": WeightingMethod.EQUAL_WEIGHT,
        "equal_weight": WeightingMethod.EQUAL_WEIGHT,
        "linear": WeightingMethod.LINEAR_STATIC,
        "linear_static": WeightingMethod.LINEAR_STATIC,
        "risk": WeightingMethod.RISK_PROPORTIONAL,
        "risk_proportional": WeightingMethod.RISK_PROPORTIONAL,
        "statistical": WeightingMethod.STATISTICAL_DYNAMIC,
        "statistical_dynamic": WeightingMethod.STATISTICAL_DYNAMIC,
        # New methods
        "volatility": WeightingMethod.VOLATILITY_ADJUSTED,
        "volatility_adjusted": WeightingMethod.VOLATILITY_ADJUSTED,
        "momentum": WeightingMethod.MOMENTUM_BASED,
        "momentum_based": WeightingMethod.MOMENTUM_BASED,
        "ensemble": WeightingMethod.ADAPTIVE_ENSEMBLE,
        "adaptive": WeightingMethod.ADAPTIVE_ENSEMBLE,
        "adaptive_ensemble": WeightingMethod.ADAPTIVE_ENSEMBLE,
        # ML methods
        "ml": WeightingMethod.ML_ADAPTIVE_STACKING,
        "ml_stacking": WeightingMethod.ML_ADAPTIVE_STACKING,
        "ml_adaptive_stacking": WeightingMethod.ML_ADAPTIVE_STACKING,
        "ml_voting": WeightingMethod.ML_ADAPTIVE_VOTING,
        "ml_adaptive_voting": WeightingMethod.ML_ADAPTIVE_VOTING,
        "ml_blending": WeightingMethod.ML_ADAPTIVE_BLENDING,
        "ml_adaptive_blending": WeightingMethod.ML_ADAPTIVE_BLENDING,
    }
    
    method_name_lower = method_name.lower()
    if method_name_lower in method_map:
        set_weighting_method(method_map[method_name_lower])
    else:
        available = ", ".join(sorted(method_map.keys()))
        raise ValueError(f"Unknown method '{method_name}'. Available: {available}")


def get_strategy_summary() -> str:
    """Get a formatted summary of all available strategies."""
    info = get_weighting_methods()
    
    summary = "📊 AVAILABLE WEIGHTING STRATEGIES\n"
    summary += "=" * 50 + "\n\n"
    
    # Group by category
    categories = {}
    for method_key, method_info in info.items():
        category = method_info.get('category', 'Other')
        if category not in categories:
            categories[category] = []
        categories[category].append((method_key, method_info))
    
    for category, methods in categories.items():
        summary += f"🔸 {category.upper()} STRATEGIES:\n"
        for method_key, method_info in methods:
            active = "✓ ACTIVE" if method_info.get('active', False) else ""
            complexity = method_info.get('complexity', 'Unknown')
            summary += f"  • {method_info['name']} ({complexity}) {active}\n"
            summary += f"    {method_info['description'][:100]}...\n\n"
    
    return summary
