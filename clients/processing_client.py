"""
Client for processing market data.
"""

import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from clients.client import Client
from clients.fetch_client import MarketData
from clients.logging_config import process_logger as logger

logger = logging.getLogger(__name__)


class ProcessedData:
    def __init__(self, indicator_name: str, raw_value: float, score: float, timestamp: datetime = None):
        self.indicator_name = indicator_name
        self.raw_value = raw_value
        self.score = score
        self.timestamp = timestamp or datetime.now()


class ProcessingClient(Client):
    """Client for processing market data."""

    def __init__(self):
        """Initialize the processing client."""
        logger.info("Initializing ProcessingClient")
        self.data_buffer: Dict[str, MarketData] = {}
        logger.info("ProcessingClient initialized successfully")

    def get_name(self) -> str:
        """Get the name of this client."""
        return "ProcessingClient"

    def run(self):
        """Run the processing client independently."""
        logger.info("Running ProcessingClient independently")
        try:
            # Create some sample data for independent testing
            sample_data = [
                MarketData("^VIX", 25.5, datetime.now()),
                MarketData("^SKEW", 125.0, datetime.now()),
                MarketData("Put/Call Ratio", 0.8, datetime.now()),
                MarketData("Buffett Indicator", 150.0, datetime.now()),
            ]

            processed_results = []
            for data in sample_data:
                score = self.calculate_score(data.indicator_name, data.value)
                processed_data = ProcessedData(
                    indicator_name=data.indicator_name, raw_value=data.value, score=score, timestamp=data.timestamp
                )
                processed_results.append(processed_data)
                logger.info(f"Processed {data.indicator_name}: {data.value} -> Score: {score:.2f}")

            logger.info(f"ProcessingClient completed. Processed {len(processed_results)} indicators.")
            return processed_results

        except Exception as e:
            logger.error(f"Error in ProcessingClient run: {str(e)}")
            return []

    def calculate_score(self, indicator_name: str, value: float) -> float:
        """Calculate risk score (0-100) for an indicator value."""
        try:
            # VIX-based indicators
            if "VIX" in indicator_name:
                if value <= 10:  # Extreme complacency
                    score = max(0, 20 - 40 * (10 - value))  # Very low VIX can be a contrarian risk
                elif value <= 15:  # Low volatility
                    score = 20 + 15 * (value - 10) / 5
                elif value <= 20:  # Normal range
                    score = 35 + 15 * (value - 15) / 5
                elif value <= 30:  # Elevated
                    score = 50 + 25 * (value - 20) / 10
                elif value <= 40:  # High stress
                    score = 75 + 15 * (value - 30) / 10
                else:  # Crisis
                    score = min(100, 90 + 10 * (value - 40) / 40)

            # SKEW indicator
            elif "SKEW" in indicator_name:
                if value <= 100:  # Below normal distribution
                    score = max(0, 25 - 25 * (100 - value) / 10)
                elif value <= 110:  # Normal low range
                    score = 25 + 15 * (value - 100) / 10
                elif value <= 120:  # Normal range
                    score = 40 + 15 * (value - 110) / 10
                elif value <= 130:  # Elevated
                    score = 55 + 20 * (value - 120) / 10
                elif value <= 140:  # High
                    score = 75 + 15 * (value - 130) / 10
                else:  # Extreme
                    score = min(100, 90 + 10 * (value - 140) / 10)

            # Put/Call Ratio
            elif "Put/Call" in indicator_name:
                if value <= 0.4:  # Extreme low - contrarian risk
                    score = max(0, 30 - 30 * (0.4 - value) / 0.1)
                elif value <= 0.5:  # Low but not extreme
                    score = 30 + 10 * (value - 0.4) / 0.1
                elif value <= 0.7:  # Normal range
                    score = 40 + 15 * (value - 0.5) / 0.2
                elif value <= 0.9:  # Elevated
                    score = 55 + 20 * (value - 0.7) / 0.2
                elif value <= 1.1:  # High
                    score = 75 + 15 * (value - 0.9) / 0.2
                else:  # Extreme high
                    score = min(100, 90 + 10 * (value - 1.1) / 0.2)

            # Term Structure and Stress Ratios
            elif "Term" in indicator_name or "Stress" in indicator_name:
                if value <= 0.7:  # Deep contango
                    score = max(0, 20 - 20 * (0.7 - value) / 0.1)
                elif value <= 0.85:  # Normal contango
                    score = 20 + 20 * (value - 0.7) / 0.15
                elif value <= 0.95:  # Mild contango
                    score = 40 + 20 * (value - 0.85) / 0.1
                elif value <= 1.05:  # Transition zone
                    score = 60 + 25 * (value - 0.95) / 0.1
                elif value <= 1.2:  # Backwardation
                    score = 85 + 10 * (value - 1.05) / 0.15
                else:  # Extreme backwardation
                    score = min(100, 95 + 5 * (value - 1.2) / 0.2)

            # Buffett Indicator
            elif "Buffett" in indicator_name:
                if value <= 80:  # Below historical average
                    score = max(0, 20 - 20 * (80 - value) / 20)
                elif value <= 100:  # Normal range
                    score = 20 + 20 * (value - 80) / 20
                elif value <= 120:  # Elevated
                    score = 40 + 20 * (value - 100) / 20
                elif value <= 150:  # High
                    score = 60 + 25 * (value - 120) / 30
                elif value <= 180:  # Very high
                    score = 85 + 10 * (value - 150) / 30
                else:  # Extreme
                    score = min(100, 95 + 5 * (value - 180) / 20)

            else:
                logger.warning(f"Unknown indicator type: {indicator_name}, using linear scale")
                score = min(max(value, 0), 100)

            logger.debug(f"Calculated score for {indicator_name}: {score:.2f} (value: {value:.2f})")
            return score

        except Exception as e:
            logger.error(f"Error calculating score for {indicator_name}: {str(e)}")
            return 50.0  # Default score on error
