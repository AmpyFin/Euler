"""
Base Weight Strategy Interface.

Defines the common interface that all weighting strategies must implement.
"""

from typing import Dict, Protocol
from abc import ABC, abstractmethod


class WeightStrategy(Protocol):
    """Protocol that all weight strategies must implement."""
    
    def calculate_weights(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate weights for indicators based on current scores.
        
        Args:
            current_scores: Dict of indicator names to current risk scores (0-100)
            
        Returns:
            Dict of indicator names to weights (sum = 1.0)
        """
        ...
    
    def get_name(self) -> str:
        """Get the name of this weighting strategy."""
        ...
    
    def get_description(self) -> str:
        """Get a detailed description of how this strategy works."""
        ...
    
    def get_category(self) -> str:
        """Get the category this strategy belongs to (e.g., 'Static', 'Dynamic', 'Adaptive')."""
        ...
    
    def get_complexity(self) -> str:
        """Get the complexity level ('Simple', 'Moderate', 'Advanced')."""
        ...


class BaseWeightStrategy(ABC):
    """Abstract base class for weight strategies with common functionality."""
    
    def __init__(self):
        self.name = self.__class__.__name__.replace('Strategy', '').replace('Weight', '')
    
    @abstractmethod
    def calculate_weights(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate weights for indicators."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get strategy name."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get strategy description."""
        pass
    
    @abstractmethod
    def get_category(self) -> str:
        """Get strategy category."""
        pass
    
    @abstractmethod
    def get_complexity(self) -> str:
        """Get strategy complexity."""
        pass
    
    def _validate_weights(self, weights: Dict[str, float]) -> None:
        """Validate that weights sum to approximately 1.0."""
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total:.3f}")
    
    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Normalize weights to sum to 1.0."""
        total = sum(weights.values())
        if total > 0:
            return {k: v / total for k, v in weights.items()}
        else:
            # Equal weights fallback
            n = len(weights)
            return {k: 1.0 / n for k in weights.keys()}
    
    def _equal_weights_fallback(self, indicators: Dict[str, float]) -> Dict[str, float]:
        """Generate equal weights as fallback."""
        n = len(indicators)
        return {indicator: 1.0 / n for indicator in indicators.keys()}
