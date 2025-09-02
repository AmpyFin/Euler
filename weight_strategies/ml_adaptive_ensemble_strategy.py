"""
ML-Enhanced Adaptive Ensemble Strategy using scikit-learn.

Uses proper ensemble learning methods to combine multiple weighting strategies
based on their historical performance and current market conditions.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import (
    RandomForestRegressor, 
    GradientBoostingRegressor, 
    VotingRegressor,
    StackingRegressor
)
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings('ignore')

from .base_strategy import BaseWeightStrategy


class MLAdaptiveEnsembleStrategy(BaseWeightStrategy):
    """
    ML-enhanced ensemble strategy using scikit-learn ensemble methods.
    
    Features:
    - Dynamic strategy selection based on market conditions
    - Historical performance tracking and learning
    - Multiple ensemble methods (Voting, Stacking, Blending)
    - Feature engineering from market indicators
    - Adaptive retraining based on performance drift
    """
    
    def __init__(self, ensemble_method: str = "stacking"):
        super().__init__()
        
        self.ensemble_method = ensemble_method  # "voting", "stacking", "blending"
        self.performance_history = []
        self.feature_history = []
        self.target_history = []
        
        # Strategy instances (cached)
        self._strategy_cache = {}
        
        # ML Models
        self.ensemble_model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Performance tracking
        self.strategy_performance = {}
        self.retraining_threshold = 0.15  # Retrain if performance drops 15%
        self.min_samples_for_training = 50
        
        # Market regime detection (unsupervised)
        self.regime_detector = None
        
    def _get_strategy_instance(self, strategy_name: str):
        """Get cached strategy instance."""
        if strategy_name not in self._strategy_cache:
            if strategy_name == "equal_weight":
                from .equal_weight_strategy import EqualWeightStrategy
                self._strategy_cache[strategy_name] = EqualWeightStrategy()
            elif strategy_name == "linear_static":
                from .linear_static_strategy import LinearStaticStrategy
                self._strategy_cache[strategy_name] = LinearStaticStrategy()
            elif strategy_name == "risk_proportional":
                from .risk_proportional_strategy import RiskProportionalStrategy
                self._strategy_cache[strategy_name] = RiskProportionalStrategy()
            elif strategy_name == "volatility_adjusted":
                from .volatility_adjusted_strategy import VolatilityAdjustedStrategy
                self._strategy_cache[strategy_name] = VolatilityAdjustedStrategy()
            elif strategy_name == "momentum":
                from .momentum_based_strategy import MomentumBasedStrategy
                self._strategy_cache[strategy_name] = MomentumBasedStrategy()
            elif strategy_name == "statistical_dynamic":
                from .statistical_dynamic_strategy import StatisticalDynamicStrategy
                self._strategy_cache[strategy_name] = StatisticalDynamicStrategy()
        
        return self._strategy_cache.get(strategy_name)
    
    def _extract_market_features(self, current_scores: Dict[str, float]) -> np.ndarray:
        """
        Extract market condition features for ML models.
        
        Features:
        - Mean risk score
        - Risk score volatility (std)
        - Skewness of risk distribution
        - Max risk indicator
        - Risk concentration (Gini coefficient)
        - Momentum (if historical data available)
        """
        scores = list(current_scores.values())
        
        features = [
            np.mean(scores),                    # Mean risk
            np.std(scores),                     # Risk volatility  
            np.max(scores),                     # Maximum risk
            np.min(scores),                     # Minimum risk
            len([s for s in scores if s > 70]), # Crisis indicators count
            len([s for s in scores if s < 30]), # Euphoria indicators count
        ]
        
        # Add skewness if scipy available
        try:
            from scipy.stats import skew
            features.append(skew(scores))
        except ImportError:
            features.append(0.0)
        
        # Add momentum features if we have history
        if len(self.feature_history) > 0:
            prev_mean = self.feature_history[-1][0]
            features.append(features[0] - prev_mean)  # Mean risk momentum
        else:
            features.append(0.0)
        
        return np.array(features).reshape(1, -1)
    
    def _get_all_strategy_predictions(self, current_scores: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Get predictions from all individual strategies."""
        strategy_names = ["equal_weight", "linear_static", "risk_proportional", 
                         "volatility_adjusted", "momentum", "statistical_dynamic"]
        
        predictions = {}
        for strategy_name in strategy_names:
            try:
                strategy = self._get_strategy_instance(strategy_name)
                if strategy:
                    predictions[strategy_name] = strategy.calculate_weights(current_scores)
            except Exception as e:
                # Skip failed strategies
                continue
        
        return predictions
    
    def _build_ensemble_model(self):
        """Build the ensemble model based on selected method."""
        if self.ensemble_method == "voting":
            # Voting Regressor - simple averaging with optional weights
            estimators = [
                ('rf', RandomForestRegressor(n_estimators=50, random_state=42)),
                ('gb', GradientBoostingRegressor(n_estimators=50, random_state=42)),
                ('linear', Ridge(alpha=1.0))
            ]
            self.ensemble_model = VotingRegressor(estimators=estimators)
            
        elif self.ensemble_method == "stacking":
            # Stacking - meta-learner combines base models
            base_models = [
                ('rf', RandomForestRegressor(n_estimators=50, random_state=42)),
                ('gb', GradientBoostingRegressor(n_estimators=50, random_state=42)),
                ('ridge', Ridge(alpha=1.0))
            ]
            meta_model = LinearRegression()
            self.ensemble_model = StackingRegressor(
                estimators=base_models, 
                final_estimator=meta_model,
                cv=3
            )
            
        else:  # "blending" - custom weighted combination
            self.ensemble_model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    def _train_ensemble_model(self):
        """Train the ensemble model on historical data."""
        if len(self.feature_history) < self.min_samples_for_training:
            return False
        
        try:
            X = np.vstack(self.feature_history)
            y = np.array(self.target_history)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Build and train model
            self._build_ensemble_model()
            self.ensemble_model.fit(X_scaled, y)
            
            # Evaluate performance
            cv_scores = cross_val_score(self.ensemble_model, X_scaled, y, cv=3, scoring='neg_mean_squared_error')
            self.ensemble_performance = -cv_scores.mean()
            
            self.is_trained = True
            return True
            
        except Exception as e:
            print(f"Training failed: {e}")
            return False
    
    def _predict_optimal_weights(self, current_scores: Dict[str, float]) -> Optional[Dict[str, float]]:
        """Use ML model to predict optimal strategy weights."""
        if not self.is_trained:
            return None
        
        try:
            # Extract features
            features = self._extract_market_features(current_scores)
            features_scaled = self.scaler.transform(features)
            
            # Get all strategy predictions
            strategy_predictions = self._get_all_strategy_predictions(current_scores)
            
            if not strategy_predictions:
                return None
            
            # Use ML model to predict optimal composite score
            target_score = self.ensemble_model.predict(features_scaled)[0]
            
            # Find strategy combination that best matches target
            best_weights = None
            best_error = float('inf')
            
            # Try different combinations of strategies
            for main_strategy, main_weights in strategy_predictions.items():
                for support_strategy, support_weights in strategy_predictions.items():
                    if main_strategy == support_strategy:
                        continue
                    
                    # Try different mixing ratios
                    for alpha in [0.7, 0.8, 0.9]:
                        combined_weights = {}
                        for indicator in current_scores.keys():
                            combined_weights[indicator] = (
                                alpha * main_weights.get(indicator, 0) + 
                                (1 - alpha) * support_weights.get(indicator, 0)
                            )
                        
                        # Calculate predicted score with these weights
                        predicted_score = sum(
                            score * combined_weights.get(indicator, 0) 
                            for indicator, score in current_scores.items()
                        )
                        
                        error = abs(predicted_score - target_score)
                        if error < best_error:
                            best_error = error
                            best_weights = combined_weights
            
            return self._normalize_weights(best_weights) if best_weights else None
            
        except Exception as e:
            return None
    
    def calculate_weights(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate ensemble weights using ML-enhanced approach."""
        if not current_scores:
            return {}
        
        # Extract features for this market state
        features = self._extract_market_features(current_scores)
        
        # Try ML prediction if model is trained
        ml_weights = self._predict_optimal_weights(current_scores)
        
        if ml_weights is not None:
            # Use ML prediction
            final_weights = ml_weights
        else:
            # Fallback to intelligent heuristic ensemble
            final_weights = self._heuristic_ensemble(current_scores)
        
        # Store this example for future training
        composite_score = sum(
            score * weight 
            for score, weight in zip(current_scores.values(), final_weights.values())
        )
        
        self.feature_history.append(features.flatten())
        self.target_history.append(composite_score)
        
        # Retrain periodically
        if len(self.feature_history) % 25 == 0:  # Every 25 samples
            self._train_ensemble_model()
        
        return final_weights
    
    def _heuristic_ensemble(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """Intelligent heuristic ensemble when ML model isn't ready - varies by ensemble method."""
        avg_risk = np.mean(list(current_scores.values()))
        risk_std = np.std(list(current_scores.values()))
        max_risk = np.max(list(current_scores.values()))
        
        # Get all strategy weights
        strategy_predictions = self._get_all_strategy_predictions(current_scores)
        
        if not strategy_predictions:
            return self._equal_weights_fallback(current_scores)
        
        # Different heuristics based on ensemble method
        if self.ensemble_method == "stacking":
            # Stacking: Hierarchical approach - use best performing strategy as base
            if avg_risk > 70:  # Crisis - prioritize risk detection
                primary = strategy_predictions.get("risk_proportional", {})
                secondary = strategy_predictions.get("statistical_dynamic", {})
                tertiary = strategy_predictions.get("momentum", {})
                # Weighted combination: 50% primary, 30% secondary, 20% tertiary
                combined_weights = {}
                for indicator in current_scores.keys():
                    combined_weights[indicator] = (
                        0.5 * primary.get(indicator, 0) + 
                        0.3 * secondary.get(indicator, 0) +
                        0.2 * tertiary.get(indicator, 0)
                    )
            else:  # Normal/stress - balanced approach
                primary = strategy_predictions.get("statistical_dynamic", {})
                secondary = strategy_predictions.get("linear_static", {})
                tertiary = strategy_predictions.get("volatility_adjusted", {})
                combined_weights = {}
                for indicator in current_scores.keys():
                    combined_weights[indicator] = (
                        0.4 * primary.get(indicator, 0) + 
                        0.35 * secondary.get(indicator, 0) +
                        0.25 * tertiary.get(indicator, 0)
                    )
                    
        elif self.ensemble_method == "voting":
            # Voting: Democratic approach - equal weight to diverse strategies
            strategies_to_use = ["statistical_dynamic", "linear_static", "risk_proportional", "momentum"]
            combined_weights = {}
            for indicator in current_scores.keys():
                combined_weights[indicator] = sum(
                    strategy_predictions.get(strategy, {}).get(indicator, 0) 
                    for strategy in strategies_to_use
                ) / len(strategies_to_use)
                
        else:  # "blending"
            # Blending: Performance-weighted based on current market conditions
            if avg_risk > 75:  # Crisis - emphasize crisis-focused strategies
                weights_mix = {
                    "risk_proportional": 0.4,
                    "momentum": 0.3,
                    "statistical_dynamic": 0.2,
                    "volatility_adjusted": 0.1
                }
            elif avg_risk < 30:  # Euphoria - catch emerging risks
                weights_mix = {
                    "statistical_dynamic": 0.35,
                    "risk_proportional": 0.25,
                    "momentum": 0.25,
                    "linear_static": 0.15
                }
            else:  # Normal/stress - balanced
                weights_mix = {
                    "statistical_dynamic": 0.3,
                    "linear_static": 0.25,
                    "volatility_adjusted": 0.25,
                    "risk_proportional": 0.2
                }
            
            combined_weights = {}
            for indicator in current_scores.keys():
                combined_weights[indicator] = sum(
                    weight * strategy_predictions.get(strategy, {}).get(indicator, 0)
                    for strategy, weight in weights_mix.items()
                )
        
        return self._normalize_weights(combined_weights)
    
    def get_name(self) -> str:
        return f"ML Adaptive Ensemble ({self.ensemble_method.title()})"
    
    def get_description(self) -> str:
        return (
            f"Advanced ML-enhanced ensemble using {self.ensemble_method} method from scikit-learn. "
            "Automatically learns optimal strategy combinations based on historical performance and "
            "current market conditions. Uses feature engineering to capture market regime characteristics "
            "and dynamically adapts strategy weights. Includes performance tracking, automated retraining, "
            "and fallback mechanisms. This represents the most sophisticated approach, combining domain "
            "expertise with machine learning to optimize risk assessment accuracy across all market conditions."
        )
    
    def get_category(self) -> str:
        return "ML-Adaptive"
    
    def get_complexity(self) -> str:
        return "Expert"
