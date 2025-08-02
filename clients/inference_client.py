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

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from clients.processing_client import ProcessedData
from clients.logging_config import inference_logger as logger

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

class InferenceClient:
    def __init__(self):
        self.data_buffer: Dict[str, ProcessedData] = {}
        self.input_queue: queue.Queue = queue.Queue()
        self.output_queue: queue.Queue = queue.Queue()
        self.should_run = True
        self.inference_thread = threading.Thread(target=self.run_inference)

    def get_regime_from_score(self, score: float) -> MarketRegime:
        for regime in MarketRegime:
            if regime.lower <= score < regime.upper:
                return regime
        return MarketRegime.CRISIS if score >= 100 else MarketRegime.EXTREME_CALM

    def get_indicator_weight(self, indicator: str, value: float, score: float, all_data: Dict[str, ProcessedData]) -> float:
        """Calculate dynamic weight for each indicator."""
        base_weights = {
            # Core volatility indicators (35% total)
            "^VIX": 0.15,      # Most watched, highly reliable but can lag
            "^VIX9D": 0.08,    # Leading indicator but noisier
            "^VIX3M": 0.06,    # Medium-term expectations
            "^VIX6M": 0.06,    # Long-term expectations
            
            # Structural indicators (35% total)
            "Buffett Indicator": 0.20,  # Strong long-term signal
            "^SKEW": 0.15,             # Critical tail risk information
            
            # Tactical indicators (30% total)
            "Put/Call Ratio": 0.12,          # Strong tactical signal
            "Near-term Stress Ratio": 0.08,  # Good leading indicator
            "3M Term Slope": 0.05,           # Term structure information
            "6M Term Slope": 0.05            # Longer-term structure
        }
        
        weight = base_weights.get(indicator, 0.10)
        
        # Get other indicator values for cross-relationships
        indicator_dict = {name: (data.raw_value, data.score) for name, data in all_data.items()}
        
        # 1. Enhanced Term Structure Analysis
        if indicator.startswith("^VIX"):
            term_structure_stress = False
            term_structure_warning = False
            if "3M Term Slope" in indicator_dict and "6M Term Slope" in indicator_dict:
                ts_3m = indicator_dict["3M Term Slope"][0]
                ts_6m = indicator_dict["6M Term Slope"][0]
                if ts_3m > 1.0 or ts_6m > 1.0:  # Backwardation
                    term_structure_stress = True
                elif ts_3m > 0.95 or ts_6m > 0.95:  # Near backwardation
                    term_structure_warning = True
                    
            if term_structure_stress:
                if indicator == "^VIX9D":
                    weight *= 1.5  # Short-term critical in stress
                elif indicator in ["^VIX3M", "^VIX6M"]:
                    weight *= 1.4  # Long-term confirmation important
            elif term_structure_warning:
                if indicator == "^VIX9D":
                    weight *= 1.3
                elif indicator in ["^VIX3M", "^VIX6M"]:
                    weight *= 1.2
        
        # 2. Enhanced Volatility Regime Analysis
        vix_regime = "normal"
        if "^VIX" in indicator_dict:
            vix_value = indicator_dict["^VIX"][0]
            if vix_value > 35:
                vix_regime = "extreme"
            elif vix_value > 25:
                vix_regime = "high"
            elif vix_value < 12:
                vix_regime = "very_low"
            elif vix_value < 15:
                vix_regime = "low"
                
        # 3. Enhanced Cross-Signal Confirmation
        if indicator == "Put/Call Ratio":
            pc_value = value
            # Multi-factor confirmation
            confirmations = 0
            if "^VIX" in indicator_dict:
                vix_value = indicator_dict["^VIX"][0]
                if (pc_value > 1.0 and vix_value > 25) or (pc_value < 0.5 and vix_value < 15):
                    confirmations += 1
            if "^SKEW" in indicator_dict:
                skew_value = indicator_dict["^SKEW"][0]
                if (pc_value > 1.0 and skew_value > 135) or (pc_value < 0.5 and skew_value < 110):
                    confirmations += 1
                
            # Weight adjustment based on confirmations
            weight *= (1 + (0.15 * confirmations))
                    
        # 4. Enhanced SKEW Analysis
        if indicator == "^SKEW":
            skew_value = value
            # SKEW more important in certain regimes
            if vix_regime in ["very_low", "low"]:
                weight *= 1.6  # Critical in low vol
            elif vix_regime == "normal":
                weight *= 1.2  # Important in normal vol
                
            # Multi-factor confirmation
            if "Put/Call Ratio" in indicator_dict and "^VIX" in indicator_dict:
                pc_value = indicator_dict["Put/Call Ratio"][0]
                vix_value = indicator_dict["^VIX"][0]
                if skew_value > 140:
                    if pc_value > 0.9:  # High put buying
                        weight *= 1.3  # Confirmed tail risk
                    if vix_value < 15:  # Hidden risk in low vol
                        weight *= 1.4
                    
        # 5. Enhanced Buffett Indicator Analysis
        if indicator == "Buffett Indicator":
            buffett_value = value
            # More important in extreme regimes
            if vix_regime in ["extreme", "very_low"]:
                weight *= 1.3
            
            # Structural confirmation
            if "3M Term Slope" in indicator_dict and "6M Term Slope" in indicator_dict:
                ts_3m_score = indicator_dict["3M Term Slope"][1]
                ts_6m_score = indicator_dict["6M Term Slope"][1]
                if ts_3m_score > 70 and ts_6m_score > 70:
                    weight *= 1.25  # Strong structural confirmation
                elif ts_3m_score > 60 and ts_6m_score > 60:
                    weight *= 1.15  # Moderate structural confirmation
        
        # 6. Enhanced Stress Ratio Analysis
        if indicator == "Near-term Stress Ratio":
            stress_value = value
            # More important in transition periods
            if "3M Term Slope" in indicator_dict:
                ts_3m = indicator_dict["3M Term Slope"][0]
                if 0.9 <= ts_3m <= 1.1:  # Critical transition zone
                    weight *= 1.35
                elif 0.85 <= ts_3m <= 1.15:  # Important transition zone
                    weight *= 1.25
            
            # Volatility regime consideration
            if vix_regime in ["high", "extreme"]:
                weight *= 1.2
        
        # 7. Enhanced Term Slope Analysis
        if indicator in ["3M Term Slope", "6M Term Slope"]:
            # More important in stress transitions
            if vix_regime in ["high", "extreme"]:
                weight *= 1.3
            elif vix_regime in ["very_low", "low"]:
                weight *= 1.2  # Important for forward-looking risk
                
            # Cross-term confirmation
            other_term = "6M Term Slope" if indicator == "3M Term Slope" else "3M Term Slope"
            if other_term in indicator_dict:
                other_score = indicator_dict[other_term][1]
                if abs(score - other_score) > 20:  # Term structure dislocation
                    weight *= 1.25
        
        # 8. Base Condition Adjustments
        if score >= 85:
            weight *= 1.4  # Extreme readings more important
        elif score >= 75:
            weight *= 1.25  # Very high readings
        elif score <= 15:
            weight *= 1.3  # Extreme low also important
        elif score <= 25:
            weight *= 1.2  # Very low readings
            
        return weight

    def analyze_market_state(self) -> Optional[MarketAnalysis]:
        """Analyze current market state using all available indicators."""
        if not self.data_buffer:
            return None

        # Calculate weighted scores
        total_weight = 0
        weighted_score = 0
        
        # First pass: Calculate weighted score
        for name, data in self.data_buffer.items():
            weight = self.get_indicator_weight(name, data.raw_value, data.score, self.data_buffer)
            weighted_score += data.score * weight
            total_weight += weight

        # Calculate composite score
        avg_score = weighted_score / total_weight if total_weight > 0 else 50.0
        regime = self.get_regime_from_score(avg_score)

        # Log detailed analysis
        logger.info("\nMarket Analysis:")
        logger.info("-" * 80)
        logger.info("Current Indicators:")
        for name, data in sorted(self.data_buffer.items()):
            weight = self.get_indicator_weight(name, data.raw_value, data.score, self.data_buffer)
            contribution = (data.score * weight / total_weight) * 100 if total_weight > 0 else 0
            logger.info(
                f"{name:25} | Raw: {data.raw_value:8.2f} | Score: {data.score:6.2f} | "
                f"Weight: {weight:5.2f} | Contrib: {contribution:5.1f}%"
            )
        
        logger.info("-" * 80)
        logger.info(
            f"Composite Score: {avg_score:6.2f} | Regime: {regime.label}"
        )
        logger.info("-" * 80)

        return MarketAnalysis(avg_score, regime, self.data_buffer.copy())

    def run_inference(self):
        """Run market inference continuously."""
        logger.info("Starting inference loop")
        
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
        logger.info("Starting InferenceClient")
        self.inference_thread.start()
        logger.info("InferenceClient started successfully")

    def stop(self):
        logger.info("Stopping InferenceClient")
        self.should_run = False
        self.inference_thread.join()
        logger.info("InferenceClient stopped")
