"""
Client for market data inference and analysis.
"""

import logging
import os
import pickle
import queue
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from clients.client import Client
from clients.logging_config import inference_logger as logger
from clients.processing_client import ProcessedData
from registries.indicator_registry import indicator_to_weights

logger = logging.getLogger(__name__)


class MarketRegime(Enum):
    EXTREME_CALM = ("🟩 EXTREME CALM", 0, 10, "Market conditions are extremely calm with very low volatility")
    LOW_STRESS = ("🟩 LOW STRESS", 10, 20, "Market shows minimal stress with low volatility")
    STABLE = ("🟩 STABLE", 20, 30, "Market is stable with normal trading conditions")
    MILD_UNCERTAINTY = ("🟨 MILD UNCERTAINTY", 30, 40, "Some uncertainty present but within normal range")
    ELEVATED_CAUTION = ("🟨 ELEVATED CAUTION", 40, 50, "Increased caution warranted due to market conditions")
    HIGH_UNCERTAINTY = ("🟧 HIGH UNCERTAINTY", 50, 60, "High levels of uncertainty and potential volatility")
    STRESS_CONDITIONS = ("🟥 STRESS CONDITIONS", 60, 70, "Market under stress with elevated risk levels")
    HIGH_STRESS = ("🟥 HIGH STRESS", 70, 80, "High stress conditions with significant volatility")
    SEVERE_STRESS = ("⬛ SEVERE STRESS", 80, 90, "Severe market stress with extreme volatility")
    CRISIS = ("⬛ CRISIS", 90, 100, "Crisis conditions with potential market disruption")

    def __init__(self, label: str, lower: float, upper: float, description: str):
        self.label = label
        self.lower = lower
        self.upper = upper
        self.description = description


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
                    weighted_contributions[indicator_name] = {"score": score, "weight": weight, "contribution": weighted_score}

            # Calculate final weighted average
            final_score = total_score / total_weight if total_weight > 0 else 50.0

            # Log detailed analysis
            logger.debug(f"Linear Weighted Analysis:")
            for indicator_name, data in weighted_contributions.items():
                logger.debug(
                    f"  {indicator_name}: Score={data['score']:.2f}, Weight={data['weight']:.3f}, Contrib={data['contribution']:.2f}"
                )
            logger.debug(f"  Final Score: {final_score:.2f}")

            return final_score

        except Exception as e:
            logger.error(f"Error in linear weighted prediction: {str(e)}")
            return 50.0


class InferenceClient(Client):
    def __init__(self):
        self.data_buffer: Dict[str, ProcessedData] = {}
        self.input_queue: queue.Queue = queue.Queue()
        self.output_queue: queue.Queue = queue.Queue()
        self.should_run = True
        self.inference_thread = threading.Thread(target=self.run_inference)

        # Initialize linear weighted scorer
        self.weighted_scorer = LinearWeightedScorer()

    def get_name(self) -> str:
        """Get the name of this client."""
        return "InferenceClient"

    def run(self):
        """Run the inference client independently."""
        logger.info("Running InferenceClient independently")
        try:
            # Create sample processed data for independent testing
            from clients.processing_client import ProcessingClient

            processor = ProcessingClient()
            sample_data = [
                ProcessedData("^VIX", 25.5, processor.calculate_score("^VIX", 25.5)),
                ProcessedData("^SKEW", 125.0, processor.calculate_score("^SKEW", 125.0)),
                ProcessedData("Put/Call Ratio", 0.8, processor.calculate_score("Put/Call Ratio", 0.8)),
                ProcessedData("Buffett Indicator", 150.0, processor.calculate_score("Buffett Indicator", 150.0)),
            ]

            # Add sample data to buffer
            for data in sample_data:
                self.data_buffer[data.indicator_name] = data

            # Analyze market state
            analysis = self.analyze_market_state()
            if analysis:
                logger.info(f"InferenceClient completed. Market Score: {analysis.score:.2f}, Regime: {analysis.regime.label}")
                return analysis
            else:
                logger.warning("InferenceClient: No analysis generated")
                return None

        except Exception as e:
            logger.error(f"Error in InferenceClient run: {str(e)}")
            return None

    def get_regime_from_score(self, score: float) -> MarketRegime:
        for regime in MarketRegime:
            if regime.lower <= score < regime.upper:
                return regime
        return MarketRegime.CRISIS if score >= 100 else MarketRegime.EXTREME_CALM

    def get_all_indicators(self) -> List[str]:
        """Get list of all registered indicators."""
        return [
            "^VIX9D",
            "^VIX",
            "^VIX3M",
            "^VIX6M",
            "^SKEW",
            "Put/Call Ratio",
            "Near-term Stress Ratio",
            "3M Term Slope",
            "6M Term Slope",
            "Buffett Indicator",
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

            # Handle string values
            raw_value_str = str(data.raw_value) if isinstance(data.raw_value, str) else f"{data.raw_value:8.2f}"
            score_str = str(data.score) if isinstance(data.score, str) else f"{data.score:6.2f}"

            logger.info(
                f"{name:25} | Raw: {raw_value_str} | Score: {score_str} | "
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
                logger.debug(f"Received data: {data.indicator_name:25} | " f"Score: {data.score:6.2f}")

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
