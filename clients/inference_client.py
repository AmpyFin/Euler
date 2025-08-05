"""
Client for market data inference and analysis.
"""
import os
import sys
from pathlib import Path
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import threading
import queue
from enum import Enum
import logging
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import pickle

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from clients.processing_client import ProcessedData
from clients.logging_config import inference_logger as logger
from registries.indicator_registry import indicator_to_weights

logger = logging.getLogger(__name__)

class MarketRegime(Enum):
    EXTREME_CALM = ("🟩 EXTREME CALM", 0, 10)
    LOW_STRESS = ("🟩 LOW STRESS", 10, 20)
    STABLE = ("🟩 STABLE", 20, 30)
    MILD_UNCERTAINTY = ("🟨 MILD UNCERTAINTY", 30, 40)
    ELEVATED_CAUTION = ("🟨 ELEVATED CAUTION", 40, 50)
    HIGH_UNCERTAINTY = ("🟧 HIGH UNCERTAINTY", 50, 60)
    STRESS_CONDITIONS = ("🟥 STRESS CONDITIONS", 60, 70)
    HIGH_STRESS = ("🟥 HIGH STRESS", 70, 80)
    SEVERE_STRESS = ("⬛ SEVERE STRESS", 80, 90)
    CRISIS = ("⬛ CRISIS", 90, 100)

    def __init__(self, label: str, lower: float, upper: float):
        self.label = label
        self.lower = lower
        self.upper = upper

class MarketAnalysis:
    def __init__(self, score: float, regime: MarketRegime, data: Dict[str, ProcessedData]):
        self.score = score
        self.regime = regime
        self.data = data
        self.timestamp = datetime.now()

class LinearWeightedScorer:
    """Linear weighted composite for market regime detection."""
    
    def __init__(self):
        self.weights = indicator_to_weights
        self._validate_weights()
        logger.info("Initialized Linear Weighted Scorer")
        logger.info(f"Using weights: {self.weights}")
    
    def _validate_weights(self):
        """Validate that weights are properly configured."""
        total_weight = sum(self.weights.values())
        logger.info(f"Total weight sum: {total_weight:.3f}")
        if total_weight < 0.9 or total_weight > 1.1:
            logger.warning(f"Weight sum ({total_weight:.3f}) is not close to 1.0 - this may affect scoring accuracy")
    
    def predict_score(self, indicator_scores: Dict[str, float]) -> float:
        """Predict market stress score using linear weighted average."""
        try:
            total_score = 0.0
            total_weight = 0.0
            weighted_contributions = {}
            
            for indicator_name, score in indicator_scores.items():
                # Get the weight for this indicator
                weight = self.weights.get(indicator_name, 0.0)
                
                if weight > 0:
                    weighted_score = score * weight
                    total_score += weighted_score
                    total_weight += weight
                    weighted_contributions[indicator_name] = {
                        'score': score,
                        'weight': weight,
                        'contribution': weighted_score
                    }
            
            # Calculate final weighted average
            final_score = total_score / total_weight if total_weight > 0 else 50.0
            
            # Log detailed analysis
            logger.debug(f"Linear Weighted Analysis:")
            for indicator_name, data in weighted_contributions.items():
                logger.debug(f"  {indicator_name}: Score={data['score']:.2f}, Weight={data['weight']:.3f}, Contrib={data['contribution']:.2f}")
            logger.debug(f"  Final Score: {final_score:.2f}")
            
            return final_score
            
        except Exception as e:
            logger.error(f"Error in linear weighted prediction: {str(e)}")
            return 50.0

class InferenceClient:
    def __init__(self):
        self.data_buffer: Dict[str, ProcessedData] = {}
        self.input_queue: queue.Queue = queue.Queue()
        self.output_queue: queue.Queue = queue.Queue()
        self.should_run = True
        self.inference_thread = threading.Thread(target=self.run_inference)
        
        # Initialize linear weighted scorer
        self.weighted_scorer = LinearWeightedScorer()

    def get_regime_from_score(self, score: float) -> MarketRegime:
        for regime in MarketRegime:
            if regime.lower <= score < regime.upper:
                return regime
        return MarketRegime.CRISIS if score >= 100 else MarketRegime.EXTREME_CALM

    def get_all_indicators(self) -> List[str]:
        """Get list of all registered indicators."""
        return [
            "^VIX9D", "^VIX", "^VIX3M", "^VIX6M", "^SKEW", 
            "Put/Call Ratio", "Near-term Stress Ratio", 
            "3M Term Slope", "6M Term Slope", "Buffett Indicator"
        ]

    def get_indicator_weight(self, indicator: str, value: float, score: float, all_data: Dict[str, ProcessedData]) -> float:
        """Get weight for indicator from registry."""
        return indicator_to_weights.get(indicator, 0.0)

    def analyze_market_state(self) -> Optional[MarketAnalysis]:
        """Analyze current market state using linear weighted composite."""
        if not self.data_buffer:
            return None

        # Extract processed scores for weighted analysis
        indicator_scores = {}
        for name, data in self.data_buffer.items():
            indicator_scores[name] = data.score
        
        # Get weighted prediction
        weighted_score = self.weighted_scorer.predict_score(indicator_scores)
        
        # Get regime from weighted score
        regime = self.get_regime_from_score(weighted_score)
        
        # Log detailed analysis
        logger.info("\nMarket Analysis (Linear Weighted Composite):")
        logger.info("-" * 80)
        logger.info("Current Indicators:")
        
        # Calculate weighted contributions for display
        for name, data in sorted(self.data_buffer.items()):
            weight = self.get_indicator_weight(name, data.raw_value, data.score, self.data_buffer)
            contribution = (data.score * weight / weighted_score) * 100 if weighted_score > 0 else 0
            
            logger.info(
                f"{name:25} | Raw: {data.raw_value:8.2f} | Score: {data.score:6.2f} | "
                f"Weight: {weight:6.3f} | Contrib: {contribution:5.1f}%"
            )
        
        logger.info("-" * 80)
        logger.info(f"Weighted Score: {weighted_score:6.2f} | Regime: {regime.label}")
        logger.info("-" * 80)

        return MarketAnalysis(weighted_score, regime, self.data_buffer.copy())

    def run_inference(self):
        """Run market inference continuously."""
        logger.info("Starting linear weighted inference loop")
        
        while self.should_run:
            try:
                # Get new data from input queue
                data: ProcessedData = self.input_queue.get(timeout=1.0)
                
                # Log received data
                logger.debug(
                    f"Received data: {data.indicator_name:25} | "
                    f"Score: {data.score:6.2f}"
                )
                
                self.data_buffer[data.indicator_name] = data

                # Analyze market state
                analysis = self.analyze_market_state()
                if analysis:
                    self.output_queue.put(analysis)

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in inference loop: {str(e)}")

    def start(self):
        """Start the inference client."""
        logger.info("Starting Linear Weighted InferenceClient")
        self.inference_thread.start()
        logger.info("InferenceClient started successfully")

    def stop(self):
        logger.info("Stopping InferenceClient")
        self.should_run = False
        self.inference_thread.join()
        logger.info("InferenceClient stopped")
