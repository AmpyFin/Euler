"""
Dynamic Statistical Weighting System with Auto-Discovery.

This module automatically discovers new indicators from the registry and 
assigns statistical weights based on:
1. Real-time risk score analysis
2. Automatic statistical profiling
3. Cross-correlation detection
4. Information content analysis
5. Market regime sensitivity detection
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, deque
import math

logger = logging.getLogger(__name__)


class MarketRegime(Enum):
    """Market regimes for dynamic weighting."""
    EUPHORIA = "euphoria"        # Score 0-25: Dangerous complacency
    NORMAL = "normal"            # Score 25-60: Balanced conditions  
    STRESS = "stress"            # Score 60-85: Elevated risk
    CRISIS = "crisis"            # Score 85-100: Imminent danger


class IndicatorCategory(Enum):
    """Categories for automatic indicator classification."""
    STRUCTURAL = "structural"         # Long-term valuation/economic indicators
    SENTIMENT = "sentiment"           # Market sentiment and positioning
    VOLATILITY = "volatility"         # Volatility structure and pricing
    TECHNICAL = "technical"           # Technical analysis indicators
    FLOW = "flow"                    # Money flow and positioning indicators
    UNKNOWN = "unknown"              # Newly added, unclassified indicators


@dataclass
class DynamicIndicatorProfile:
    """Automatically generated statistical profile for any indicator."""
    name: str
    category: IndicatorCategory = IndicatorCategory.UNKNOWN
    
    # Auto-calculated statistics (updated as data comes in)
    score_history: deque = field(default_factory=lambda: deque(maxlen=100))
    regime_sensitivity: float = 0.5  # How much it varies across regimes
    average_score: float = 50.0      # Rolling average
    volatility: float = 0.5          # Score volatility
    trend_strength: float = 0.0      # Current trend direction (-1 to 1)
    
    # Cross-correlation analysis
    correlations: Dict[str, float] = field(default_factory=dict)
    information_uniqueness: float = 1.0  # 1.0 = completely unique, 0.0 = redundant
    
    # Risk characteristics (auto-learned)
    crisis_sensitivity: float = 0.5     # How much it spikes during stress
    euphoria_sensitivity: float = 0.5   # How much it drops during euphoria
    leading_lag_score: float = 0.0      # Positive = leading, negative = lagging
    
    # Quality metrics
    signal_noise_ratio: float = 0.5     # Signal quality
    reliability_score: float = 0.5      # Overall reliability
    data_points: int = 0                # Number of observations
    
    def update_with_score(self, score: float, market_regime: MarketRegime):
        """Update profile with new score observation."""
        self.score_history.append(score)
        self.data_points += 1
        
        # Update rolling statistics
        scores = list(self.score_history)
        self.average_score = np.mean(scores)
        self.volatility = np.std(scores) / 100.0 if len(scores) > 1 else 0.5
        
        # Update regime sensitivity
        self._update_regime_sensitivity(score, market_regime)
        
        # Update signal quality
        self._update_signal_quality()
    
    def _update_regime_sensitivity(self, score: float, regime: MarketRegime):
        """Update how sensitive this indicator is to regime changes."""
        if len(self.score_history) < 5:
            return
            
        if regime == MarketRegime.CRISIS:
            # Track how much it spikes during crisis
            recent_avg = np.mean(list(self.score_history)[-5:])
            historical_avg = np.mean(list(self.score_history)[:-5]) if len(self.score_history) > 5 else 50
            spike_ratio = recent_avg / max(historical_avg, 1.0)
            self.crisis_sensitivity = min(1.0, spike_ratio / 2.0)  # Normalize
            
        elif regime == MarketRegime.EUPHORIA:
            # Track how much it drops during euphoria
            recent_avg = np.mean(list(self.score_history)[-5:])
            historical_avg = np.mean(list(self.score_history)[:-5]) if len(self.score_history) > 5 else 50
            drop_ratio = historical_avg / max(recent_avg, 1.0)
            self.euphoria_sensitivity = min(1.0, drop_ratio / 2.0)  # Normalize
    
    def _update_signal_quality(self):
        """Update signal-to-noise ratio and reliability."""
        if len(self.score_history) < 10:
            return
            
        scores = np.array(list(self.score_history))
        
        # Calculate trend strength
        x = np.arange(len(scores))
        slope = np.polyfit(x, scores, 1)[0]
        self.trend_strength = np.tanh(slope / 10.0)  # Normalize to [-1, 1]
        
        # Calculate signal-to-noise (higher for more predictable patterns)
        if len(scores) > 20:
            # Use autocorrelation to measure signal quality
            autocorr = np.corrcoef(scores[:-1], scores[1:])[0, 1]
            self.signal_noise_ratio = max(0.1, abs(autocorr))
        
        # Update reliability based on consistency
        score_range = np.ptp(scores)  # Peak-to-peak range
        expected_range = 100.0  # Full 0-100 range
        consistency = 1.0 - (score_range / expected_range)
        self.reliability_score = (consistency + self.signal_noise_ratio) / 2.0


class AutoDiscoveryWeightCalculator:
    """
    Automatically discovers indicators and assigns dynamic statistical weights.
    
    This system:
    1. Auto-discovers new indicators from registry
    2. Automatically profiles their statistical characteristics
    3. Assigns weights based on real-time analysis
    4. Adapts to market regime changes
    5. Handles correlation analysis dynamically
    """
    
    def __init__(self):
        """Initialize with dynamic discovery capabilities."""
        self.indicator_profiles: Dict[str, DynamicIndicatorProfile] = {}
        self.regime_history: deque = field(default_factory=lambda: deque(maxlen=50))
        self.weight_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=20))
        
        logger.info("Initialized Auto-Discovery Weight Calculator")
        logger.info("System will automatically discover and profile new indicators")
    
    def discover_and_profile_indicators(self, current_scores: Dict[str, float]) -> None:
        """Automatically discover new indicators and update profiles."""
        from registries.indicator_registry import get_enabled_indicators
        
        # Get currently enabled indicators
        enabled_indicators = set(get_enabled_indicators())
        
        # Discover new indicators
        new_indicators = enabled_indicators - set(self.indicator_profiles.keys())
        if new_indicators:
            logger.debug(f"Auto-discovered new indicators: {new_indicators}")
            
            for indicator in new_indicators:
                # Create new profile with auto-classification
                category = self._auto_classify_indicator(indicator)
                profile = DynamicIndicatorProfile(name=indicator, category=category)
                self.indicator_profiles[indicator] = profile
                logger.debug(f"Created profile for {indicator} (category: {category.value})")
        
        # Remove indicators that are no longer enabled
        disabled_indicators = set(self.indicator_profiles.keys()) - enabled_indicators
        for indicator in disabled_indicators:
            del self.indicator_profiles[indicator]
            logger.info(f"🗑️ Removed profile for disabled indicator: {indicator}")
        
        # Update all profiles with current data
        current_regime = self._detect_regime(current_scores)
        for indicator, score in current_scores.items():
            if indicator in self.indicator_profiles:
                self.indicator_profiles[indicator].update_with_score(score, current_regime)
        
        # Update cross-correlations
        self._update_cross_correlations(current_scores)
    
    def _auto_classify_indicator(self, indicator_name: str) -> IndicatorCategory:
        """Automatically classify indicator based on name and characteristics."""
        name_lower = indicator_name.lower()
        
        # Structural/Valuation indicators
        if any(term in name_lower for term in ['buffett', 'cape', 'pe', 'pb', 'gdp', 'valuation', 'price_earnings']):
            return IndicatorCategory.STRUCTURAL
        
        # Sentiment indicators
        elif any(term in name_lower for term in ['put_call', 'sentiment', 'fear', 'greed', 'insider', 'survey']):
            return IndicatorCategory.SENTIMENT
        
        # Volatility indicators
        elif any(term in name_lower for term in ['vix', 'volatility', 'skew', 'stress', 'term_slope', 'vol']):
            return IndicatorCategory.VOLATILITY
        
        # Flow indicators
        elif any(term in name_lower for term in ['flow', 'volume', 'money', 'liquidity', 'margin']):
            return IndicatorCategory.FLOW
        
        # Technical indicators
        elif any(term in name_lower for term in ['rsi', 'macd', 'moving', 'momentum', 'trend', 'oscillator']):
            return IndicatorCategory.TECHNICAL
        
        else:
            return IndicatorCategory.UNKNOWN
    
    def _update_cross_correlations(self, current_scores: Dict[str, float]) -> None:
        """Update cross-correlation matrix between all indicators."""
        indicators = list(current_scores.keys())
        
        for i, ind1 in enumerate(indicators):
            for j, ind2 in enumerate(indicators):
                if i >= j or ind1 not in self.indicator_profiles or ind2 not in self.indicator_profiles:
                    continue
                
                # Calculate correlation if we have enough data
                profile1 = self.indicator_profiles[ind1]
                profile2 = self.indicator_profiles[ind2]
                
                if len(profile1.score_history) >= 10 and len(profile2.score_history) >= 10:
                    # Get overlapping history
                    min_len = min(len(profile1.score_history), len(profile2.score_history))
                    scores1 = np.array(list(profile1.score_history)[-min_len:])
                    scores2 = np.array(list(profile2.score_history)[-min_len:])
                    
                    correlation = np.corrcoef(scores1, scores2)[0, 1]
                    if not np.isnan(correlation):
                        profile1.correlations[ind2] = correlation
                        profile2.correlations[ind1] = correlation
        
        # Update information uniqueness based on correlations
        for profile in self.indicator_profiles.values():
            if profile.correlations:
                max_correlation = max(abs(corr) for corr in profile.correlations.values())
                profile.information_uniqueness = 1.0 - max_correlation
    
    def calculate_dynamic_weights(
        self, 
        current_scores: Dict[str, float],
        market_regime: Optional[MarketRegime] = None
    ) -> Dict[str, float]:
        """
        Calculate dynamic weights for all indicators (including new ones).
        
        Args:
            current_scores: Current risk scores for each indicator (0-100)
            market_regime: Current market regime (auto-detected if None)
            
        Returns:
            Dictionary of dynamic weights that sum to 1.0
        """
        # Step 1: Auto-discover and profile indicators
        self.discover_and_profile_indicators(current_scores)
        
        if not self.indicator_profiles:
            logger.warning("No indicators found - using equal weights")
            n = len(current_scores)
            return {indicator: 1.0/n for indicator in current_scores.keys()}
        
        # Step 2: Detect current regime
        if market_regime is None:
            market_regime = self._detect_regime(current_scores)
        
        # Step 3: Calculate base weights from statistical profiles
        base_weights = self._calculate_statistical_base_weights(current_scores)
        
        # Step 4: Apply regime-specific adjustments
        regime_weights = self._apply_dynamic_regime_multipliers(base_weights, market_regime, current_scores)
        
        # Step 5: Adjust for information content and correlation
        info_weights = self._adjust_for_dynamic_information_content(regime_weights, current_scores)
        
        # Step 6: Apply quality and reliability adjustments
        final_weights = self._apply_dynamic_quality_adjustments(info_weights)
        
        # Step 7: Normalize to sum to 1.0
        total_weight = sum(final_weights.values())
        if total_weight > 0:
            normalized_weights = {k: v/total_weight for k, v in final_weights.items()}
        else:
            # Fallback to equal weights
            n = len(current_scores)
            normalized_weights = {k: 1.0/n for k in current_scores.keys()}
        
        # Store weight history for analysis
        for indicator, weight in normalized_weights.items():
            self.weight_history[indicator].append(weight)
        
        logger.debug(f"Dynamic weights for {market_regime.value} regime: {normalized_weights}")
        return normalized_weights
    
    def _calculate_statistical_base_weights(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate base weights from real-time statistical analysis."""
        base_weights = {}
        
        for indicator, score in current_scores.items():
            if indicator not in self.indicator_profiles:
                # New indicator - assign moderate weight
                base_weights[indicator] = 0.5
                continue
            
            profile = self.indicator_profiles[indicator]
            
            # Base weight components:
            
            # 1. Crisis sensitivity (higher = more important during stress)
            crisis_component = profile.crisis_sensitivity * 0.3
            
            # 2. Information uniqueness (higher = less redundant)
            uniqueness_component = profile.information_uniqueness * 0.3
            
            # 3. Signal quality (higher = more reliable)
            quality_component = profile.signal_noise_ratio * 0.2
            
            # 4. Data reliability (more data = more confidence)
            reliability_component = min(1.0, profile.data_points / 50.0) * 0.2
            
            base_weight = crisis_component + uniqueness_component + quality_component + reliability_component
            base_weights[indicator] = max(0.1, base_weight)  # Minimum weight of 10%
        
        return base_weights
    
    def _apply_dynamic_regime_multipliers(
        self, 
        base_weights: Dict[str, float], 
        regime: MarketRegime,
        current_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Apply regime-specific multipliers based on indicator categories and behavior."""
        regime_weights = base_weights.copy()
        
        for indicator, weight in base_weights.items():
            if indicator not in self.indicator_profiles:
                continue
                
            profile = self.indicator_profiles[indicator]
            score = current_scores.get(indicator, 50)
            
            # Category-based regime adjustments
            if regime == MarketRegime.EUPHORIA:
                if profile.category == IndicatorCategory.STRUCTURAL:
                    regime_weights[indicator] *= 1.5  # Structural risk critical in euphoria
                elif profile.category == IndicatorCategory.SENTIMENT:
                    regime_weights[indicator] *= 0.8  # Sentiment less reliable in euphoria
                elif score < 30:  # Low scores in euphoria are dangerous
                    regime_weights[indicator] *= 1.3
                    
            elif regime == MarketRegime.STRESS:
                if profile.category == IndicatorCategory.SENTIMENT:
                    regime_weights[indicator] *= 1.4  # Sentiment critical in stress
                elif profile.category == IndicatorCategory.VOLATILITY:
                    regime_weights[indicator] *= 1.3  # Volatility structure important
                elif score > 70:  # High scores in stress are critical
                    regime_weights[indicator] *= 1.2
                    
            elif regime == MarketRegime.CRISIS:
                if profile.category == IndicatorCategory.VOLATILITY:
                    regime_weights[indicator] *= 1.5  # Volatility dominates in crisis
                elif profile.category == IndicatorCategory.SENTIMENT:
                    regime_weights[indicator] *= 1.3  # Panic indicators important
                elif profile.category == IndicatorCategory.STRUCTURAL:
                    regime_weights[indicator] *= 0.7  # Long-term less relevant in crisis
            
            # Adaptive adjustments based on indicator's own regime sensitivity
            regime_sensitivity_bonus = profile.regime_sensitivity * 0.2
            regime_weights[indicator] *= (1.0 + regime_sensitivity_bonus)
        
        return regime_weights
    
    def _adjust_for_dynamic_information_content(
        self, 
        regime_weights: Dict[str, float],
        current_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Dynamically adjust for information content and redundancy."""
        adjusted_weights = regime_weights.copy()
        
        for indicator, weight in regime_weights.items():
            if indicator not in self.indicator_profiles:
                continue
                
            profile = self.indicator_profiles[indicator]
            
            # Reduce weight if highly correlated with other indicators
            if profile.correlations:
                for other_indicator, correlation in profile.correlations.items():
                    if abs(correlation) > 0.6 and other_indicator in current_scores:
                        # Check if they're giving similar signals
                        score1 = current_scores[indicator]
                        score2 = current_scores[other_indicator]
                        
                        if abs(score1 - score2) < 15:  # Similar scores
                            # Reduce weight based on correlation strength
                            reduction = abs(correlation) * 0.3
                            adjusted_weights[indicator] *= (1.0 - reduction)
            
            # Boost weight for unique information
            uniqueness_bonus = profile.information_uniqueness * 0.2
            adjusted_weights[indicator] *= (1.0 + uniqueness_bonus)
        
        return adjusted_weights
    
    def _apply_dynamic_quality_adjustments(self, info_weights: Dict[str, float]) -> Dict[str, float]:
        """Apply quality adjustments based on dynamic reliability metrics."""
        final_weights = info_weights.copy()
        
        for indicator, weight in info_weights.items():
            if indicator not in self.indicator_profiles:
                continue
                
            profile = self.indicator_profiles[indicator]
            
            # Signal-to-noise adjustment
            snr_multiplier = 0.7 + (profile.signal_noise_ratio * 0.6)  # Range: 0.7 to 1.3
            final_weights[indicator] *= snr_multiplier
            
            # Reliability adjustment
            reliability_multiplier = 0.8 + (profile.reliability_score * 0.4)  # Range: 0.8 to 1.2
            final_weights[indicator] *= reliability_multiplier
            
            # Data confidence adjustment (more data = more confidence)
            confidence = min(1.0, profile.data_points / 30.0)
            confidence_multiplier = 0.9 + (confidence * 0.2)  # Range: 0.9 to 1.1
            final_weights[indicator] *= confidence_multiplier
        
        return final_weights
    
    def _detect_regime(self, current_scores: Dict[str, float]) -> MarketRegime:
        """Auto-detect current market regime from scores."""
        if not current_scores:
            return MarketRegime.NORMAL
            
        # Use dynamic weighting of scores for regime detection
        weighted_scores = []
        for indicator, score in current_scores.items():
            if indicator in self.indicator_profiles:
                profile = self.indicator_profiles[indicator]
                # Weight by regime sensitivity and reliability
                weight = profile.regime_sensitivity * profile.reliability_score
                weighted_scores.append(score * weight)
            else:
                weighted_scores.append(score)
        
        if not weighted_scores:
            return MarketRegime.NORMAL
            
        avg_score = np.average(weighted_scores)
        
        if avg_score <= 25:
            return MarketRegime.EUPHORIA
        elif avg_score <= 60:
            return MarketRegime.NORMAL
        elif avg_score <= 85:
            return MarketRegime.STRESS
        else:
            return MarketRegime.CRISIS
    
    def get_indicator_analysis(self, indicator: str) -> str:
        """Get detailed analysis of a specific indicator."""
        if indicator not in self.indicator_profiles:
            return f"Indicator '{indicator}' not found in profiles"
        
        profile = self.indicator_profiles[indicator]
        
        analysis = f"\n📊 **Analysis for {indicator.replace('_', ' ').title()}**\n"
        analysis += "-" * 50 + "\n"
        analysis += f"Category: {profile.category.value.title()}\n"
        analysis += f"Average Score: {profile.average_score:.1f}\n"
        analysis += f"Volatility: {profile.volatility:.2f}\n"
        analysis += f"Regime Sensitivity: {profile.regime_sensitivity:.2f}\n"
        analysis += f"Information Uniqueness: {profile.information_uniqueness:.2f}\n"
        analysis += f"Signal Quality: {profile.signal_noise_ratio:.2f}\n"
        analysis += f"Reliability: {profile.reliability_score:.2f}\n"
        analysis += f"Data Points: {profile.data_points}\n"
        
        if profile.correlations:
            analysis += f"\nTop Correlations:\n"
            sorted_corr = sorted(profile.correlations.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
            for other, corr in sorted_corr:
                analysis += f"  • {other}: {corr:.2f}\n"
        
        return analysis


# Singleton instance for use across the system
auto_discovery_weight_calculator = AutoDiscoveryWeightCalculator()
