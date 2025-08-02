"""
Client for processing market data.
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
import logging

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from clients.fetch_client import MarketData
from clients.logging_config import process_logger as logger

logger = logging.getLogger(__name__)

class ProcessedData:
    def __init__(self, indicator_name: str, raw_value: float, score: float, timestamp: datetime = None):
        self.indicator_name = indicator_name
        self.raw_value = raw_value
        self.score = score
        self.timestamp = timestamp or datetime.now()

class ProcessingClient:
    """Client for processing market data."""
    
    def __init__(self):
        """Initialize the processing client."""
        logger.info("Initializing ProcessingClient")
        self.data_buffer: Dict[str, MarketData] = {}
        self.input_queue: queue.Queue = queue.Queue()
        self.output_queue: queue.Queue = queue.Queue()
        self.should_run = True
        self.processing_thread = threading.Thread(target=self.process_data)
        logger.info("ProcessingClient initialized successfully")
        
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
    
    def process_data(self):
        """Process market data continuously."""
        logger.info("Starting data processing loop")
        
        while self.should_run:
            try:
                # Get market data with timeout
                market_data: MarketData = self.input_queue.get(timeout=1.0)
                
                # Update buffer
                self.data_buffer[market_data.indicator_name] = market_data
                
                # Calculate score
                score = self.calculate_score(market_data.indicator_name, market_data.value)
                
                # Create processed data
                processed = ProcessedData(
                    indicator_name=market_data.indicator_name,
                    raw_value=market_data.value,
                    score=score,
                    timestamp=market_data.timestamp  # Pass through the original timestamp
                )
                
                # Log processing result with detailed info
                logger.info(
                    f"Processed {processed.indicator_name:25} | "
                    f"Raw: {processed.raw_value:8.2f} → Score: {processed.score:6.2f}"
                )
                
                # Put processed data in output queue
                self.output_queue.put(processed)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing data: {str(e)}")
    
    def start(self):
        """Start the processing client."""
        logger.info("Starting ProcessingClient")
        self.processing_thread.start()
        logger.info("ProcessingClient started successfully")
    
    def stop(self):
        """Stop the processing client."""
        logger.info("Stopping ProcessingClient")
        self.should_run = False
        self.processing_thread.join()
        logger.info("ProcessingClient stopped")
