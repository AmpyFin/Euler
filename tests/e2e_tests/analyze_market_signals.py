"""
E2E test to analyze market signals from all indicators.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Tuple

from adapters.buffet_indicator_adapter import BuffettIndicatorAdapter

# Import adapters
from adapters.yfinance_adapter import YFinanceAdapter
from indicators.live_indicators.buffet_indicator import BuffettIndicator
from indicators.live_indicators.cpc_indicator import CPCIndicator
from indicators.live_indicators.near_term_stress_ratio_indicator import NearTermStressRatioIndicator
from indicators.live_indicators.six_month_term_slope_indicator import SixMonthTermSlopeIndicator
from indicators.live_indicators.skew_indicator import SKEWIndicator
from indicators.live_indicators.three_month_term_slope_indicator import ThreeMonthTermSlopeIndicator
from indicators.live_indicators.vix3m_indicator import VIX3MIndicator
from indicators.live_indicators.vix6m_indicator import VIX6MIndicator

# Import all indicators
from indicators.live_indicators.vix9d_indicator import VIX9DIndicator
from indicators.live_indicators.vix_indicator import VIXIndicator


class MarketRegime(Enum):
    VERY_LOW = "🟩 VERY LOW RISK"  # 0-20: Dark Green
    LOW = "💚 LOW RISK"  # 21-40: Light Green
    MODERATE = "🟣 MODERATE RISK"  # 41-60: Purple
    HIGH = "🟥 HIGH RISK"  # 61-80: Light Red
    SEVERE = "⛔️ SEVERE RISK"  # 81-100: Deep Red


@dataclass
class SignalAnalysis:
    indicator_name: str
    current_value: float
    score: float  # 0-100 score
    regime: MarketRegime
    interpretation: str
    error_message: str = ""


def get_regime_from_score(score: float) -> MarketRegime:
    """Convert 0-100 score to market regime."""
    if score <= 20:
        return MarketRegime.VERY_LOW
    elif score <= 40:
        return MarketRegime.LOW
    elif score <= 60:
        return MarketRegime.MODERATE
    elif score <= 80:
        return MarketRegime.HIGH
    return MarketRegime.SEVERE


def analyze_vix(value: float) -> Tuple[float, MarketRegime]:
    """
    Analyze VIX level and return 0-100 score.

    VIX characteristics:
    - Mean reversion tendency around 15-20
    - Log-normal distribution
    - Spikes are more significant than dips
    - Historical ranges: 9-80, with 90% between 12-35
    """
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

    return score, get_regime_from_score(score)


def analyze_skew(value: float) -> Tuple[float, MarketRegime]:
    """
    Analyze SKEW level and return 0-100 score.

    SKEW characteristics:
    - Measures tail risk pricing
    - Base level ~100 (log-normal distribution)
    - Range typically 100-150
    - More sensitive in higher ranges
    - Predictive power increases with extreme readings
    """
    if value <= 100:  # Below normal distribution
        score = max(0, 25 - 25 * (100 - value) / 10)  # Very low SKEW can indicate complacency
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

    return score, get_regime_from_score(score)


def analyze_pc_ratio(value: float) -> Tuple[float, MarketRegime]:
    """
    Analyze Put/Call ratio and return 0-100 score.

    P/C Ratio characteristics:
    - Mean reversion around 0.7
    - Contrarian indicator at extremes
    - Range typically 0.3-1.2
    - More significant above 1.0 (rare territory)
    - Exponential scaling in extremes
    """
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

    return score, get_regime_from_score(score)


def analyze_term_structure(value: float) -> Tuple[float, MarketRegime]:
    """
    Analyze term structure ratios and return 0-100 score.

    Term Structure characteristics:
    - Normal state is contango (ratio < 1)
    - Backwardation (ratio > 1) is significant
    - More sensitive near 1.0 (contango/backwardation boundary)
    - Extreme readings more meaningful in backwardation
    """
    if value <= 0.7:  # Deep contango
        score = max(0, 20 - 20 * (0.7 - value) / 0.1)  # Extreme contango can indicate complacency
    elif value <= 0.85:  # Normal contango
        score = 20 + 20 * (value - 0.7) / 0.15
    elif value <= 0.95:  # Mild contango
        score = 40 + 20 * (value - 0.85) / 0.1
    elif value <= 1.05:  # Transition zone
        score = 60 + 25 * (value - 0.95) / 0.1  # More sensitive around 1.0
    elif value <= 1.2:  # Backwardation
        score = 85 + 10 * (value - 1.05) / 0.15
    else:  # Extreme backwardation
        score = min(100, 95 + 5 * (value - 1.2) / 0.2)

    return score, get_regime_from_score(score)


def analyze_buffett(value: float) -> Tuple[float, MarketRegime]:
    """
    Analyze Buffett Indicator and return 0-100 score.

    Buffett Indicator characteristics:
    - Historical mean ~80-90
    - Considers structural changes in economy
    - More significant above historical mean
    - Extreme readings are very rare
    - Non-linear relationship with future returns
    """
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

    return score, get_regime_from_score(score)


def get_interpretation(indicator: str, value: float, score: float, regime: MarketRegime) -> str:
    """Get sophisticated interpretation of the signal based on value and score."""
    if indicator == "^VIX9D":
        if score <= 20:
            return "Extremely low near-term volatility - potential contrarian risk signal"
        elif score <= 40:
            return "Low near-term volatility within normal range for stable markets"
        elif score <= 60:
            return "Near-term volatility at typical levels suggesting balanced risk perception"
        elif score <= 80:
            return "Elevated near-term volatility indicating increased hedging demand"
        return "Extreme near-term volatility suggesting acute market stress"

    elif indicator == "^VIX":
        if score <= 20:
            return "VIX at unsustainably low levels - potential complacency risk"
        elif score <= 40:
            return "VIX suggesting confident market conditions with moderate hedging"
        elif score <= 60:
            return "VIX at normal levels indicating balanced risk assessment"
        elif score <= 80:
            return "Elevated VIX showing significant uncertainty and hedging activity"
        return "Crisis-level VIX indicating extreme market fear and potential opportunities"

    elif indicator == "^VIX3M":
        if score <= 20:
            return "Unusually subdued medium-term volatility expectations - possible complacency"
        elif score <= 40:
            return "Low but sustainable medium-term volatility expectations"
        elif score <= 60:
            return "Normal medium-term volatility structure indicating stable conditions"
        elif score <= 80:
            return "Elevated medium-term volatility suggesting persistent uncertainty"
        return "Extreme medium-term volatility pricing indicating structural market stress"

    elif indicator == "^VIX6M":
        if score <= 20:
            return "Very low long-term volatility suggesting strong structural stability"
        elif score <= 40:
            return "Low long-term volatility indicating confident market outlook"
        elif score <= 60:
            return "Normal long-term volatility structure suggesting stable conditions"
        elif score <= 80:
            return "Elevated long-term volatility indicating sustained uncertainty ahead"
        return "Extreme long-term volatility suggesting major structural concerns"

    elif indicator == "^SKEW":
        if score <= 20:
            return "Unusually low tail risk pricing - potential hidden risks"
        elif score <= 40:
            return "Below-average tail risk hedging but within normal range"
        elif score <= 60:
            return "Normal tail risk pricing indicating balanced market positioning"
        elif score <= 80:
            return "Elevated tail risk hedging suggesting increased crash concerns"
        return "Extreme tail risk pricing indicating severe downside protection buying"

    elif indicator == "Put/Call Ratio":
        if score <= 20:
            return "Extremely low put demand - contrarian risk from potential complacency"
        elif score <= 40:
            return "Low put/call ratio within normal range for bullish markets"
        elif score <= 60:
            return "Balanced options activity showing neutral sentiment"
        elif score <= 80:
            return "Elevated put buying indicating defensive positioning"
        return "Extreme put/call ratio suggesting potential capitulation"

    elif indicator == "Near-term Stress Ratio":
        if score <= 20:
            return "Very low near-term/spot volatility spread indicating calm conditions"
        elif score <= 40:
            return "Low but normal near-term risk premium structure"
        elif score <= 60:
            return "Typical near-term volatility premium indicating stable conditions"
        elif score <= 80:
            return "Elevated near-term risk premium suggesting approaching stress"
        return "Extreme near-term stress premium indicating imminent concerns"

    elif indicator == "3M Term Slope":
        if score <= 20:
            return "Deep contango indicating very strong risk appetite - possible complacency"
        elif score <= 40:
            return "Normal contango suggesting healthy volatility term structure"
        elif score <= 60:
            return "Moderate term structure slope indicating balanced conditions"
        elif score <= 80:
            return "Flattening/inverted term structure suggesting increasing stress"
        return "Severe backwardation indicating significant market dislocation"

    elif indicator == "6M Term Slope":
        if score <= 20:
            return "Strong long-term contango showing confidence in market stability"
        elif score <= 40:
            return "Healthy long-term volatility structure supporting risk assets"
        elif score <= 60:
            return "Normal long-term term structure indicating stable conditions"
        elif score <= 80:
            return "Concerning long-term volatility structure suggesting sustained stress"
        return "Severe long-term backwardation indicating major market dislocation"

    elif indicator == "Buffett Indicator":
        if score <= 20:
            return "Market cap significantly below historical GDP relationship"
        elif score <= 40:
            return "Market cap/GDP ratio suggesting reasonable equity valuations"
        elif score <= 60:
            return "Market cap/GDP near historical norms indicating fair value"
        elif score <= 80:
            return "Elevated market cap/GDP ratio suggesting extended valuations"
        return "Extreme market cap/GDP ratio indicating significant overvaluation"

    return "No interpretation available"


def analyze_indicator(indicator_instance) -> SignalAnalysis:
    """Analyze a single indicator."""
    try:
        name = indicator_instance.get_name()
        value = indicator_instance.fetch_last_quote()

        # Determine regime based on indicator type
        if name in ["^VIX", "^VIX9D", "^VIX3M", "^VIX6M"]:
            score, regime = analyze_vix(value)
        elif name == "^SKEW":
            score, regime = analyze_skew(value)
        elif name == "Put/Call Ratio":
            score, regime = analyze_pc_ratio(value)
        elif "Term" in name or "Stress" in name:
            score, regime = analyze_term_structure(value)
        elif "Buffett" in name:
            score, regime = analyze_buffett(value)
        else:
            regime = MarketRegime.MODERATE  # Default to neutral if not handled

        interpretation = get_interpretation(name, value, score, regime)

        return SignalAnalysis(
            indicator_name=name, current_value=value, score=score, regime=regime, interpretation=interpretation
        )

    except Exception as e:
        return SignalAnalysis(
            indicator_name=name if "name" in locals() else "Unknown",
            current_value=0.0,
            score=0.0,
            regime=MarketRegime.MODERATE,  # Default to neutral on error
            interpretation="Error fetching data",
            error_message=str(e),
        )


def print_signal_report(results: List[SignalAnalysis]):
    """Print formatted signal analysis report."""
    print("\n" + "=" * 120)
    print(f"EULER SYSTEM MARKET SIGNAL ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 120)

    # Calculate composite score and contributions
    composite_score, contributions, risk_factors, regime = calculate_composite_risk_score(results)

    # Count regimes
    regime_counts = {regime: 0 for regime in MarketRegime}
    for result in results:
        regime_counts[result.regime] += 1

    # Print overall market state
    print("\nOVERALL MARKET STATE:")
    print("-" * 120)
    print(f"Composite Market Risk Score: {composite_score:.1f}/100")

    print("\nRisk Factor Analysis:")
    risk_factor_order = ["volatility", "tail_risk", "structural", "tactical", "sentiment"]
    for factor in risk_factor_order:
        if risk_factors[factor] >= 30:
            status = "CRITICAL"
            symbol = "⛔️"
        elif risk_factors[factor] >= 20:
            status = "ELEVATED"
            symbol = "🟥"
        elif risk_factors[factor] >= 10:
            status = "MODERATE"
            symbol = "🟡"
        else:
            status = "LOW"
            symbol = "🟢"
        print(f"{symbol} {factor.replace('_', ' ').title():<15} {risk_factors[factor]:>6.1f}% ({status})")

    print("\nKey Contributors to Risk Score:")
    sorted_contributions = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
    for indicator, contribution in sorted_contributions[:3]:
        print(f"• {indicator:<25} {contribution:>6.1f}% contribution")

    print("\nRisk Level Distribution:")
    for regime in MarketRegime:
        print(f"{regime.value}: {regime_counts[regime]} indicators")

    # Print detailed analysis
    print("\nDETAILED SIGNAL ANALYSIS:")
    print("-" * 120)
    print(f"{'Indicator':<25} {'Value':<10} {'Risk Score':<12} {'Weight':<8} {'Risk Level':<20} {'Interpretation':<45}")
    print("-" * 120)

    # Sort results by risk score for better visualization
    sorted_results = sorted(results, key=lambda x: x.score, reverse=True)

    for result in sorted_results:
        if result.score > 0:  # Only show valid results
            value = f"{result.current_value:.2f}" if result.current_value != 0 else "N/A"
            score = f"{result.score:.1f}"
            weight = f"{get_indicator_weight(result.indicator_name, result.current_value, result.score, results):.2f}"
            print(
                f"{result.indicator_name:<25} {value:<10} {score:<12} {weight:<8} {result.regime.value:<20} {result.interpretation:<45}"
            )
        if result.error_message:
            print(f"  Error: {result.error_message}")

    print("\n" + "=" * 120)

    # Print market summary
    print("\nMARKET SUMMARY:")
    print("-" * 120)
    print(regime)

    print("=" * 120 + "\n")


def get_indicator_weight(indicator: str, value: float, score: float, all_results: List[SignalAnalysis]) -> float:
    """
    Calculate dynamic weight for each indicator based on its characteristics, current value,
    and cross-indicator relationships.

    Weight Adjustment Principles:
    1. Base weights reflect historical reliability and importance
    2. Dynamic adjustments based on current market regime
    3. Cross-indicator relationships affect weights
    4. Term structure influences volatility weights
    5. Correlation-based adjustments
    6. Momentum and trend considerations
    7. Volatility regime impact
    8. Structural vs tactical balance
    """
    base_weights = {
        # Core volatility indicators (35% total)
        "^VIX": 0.15,  # Most watched, highly reliable but can lag
        "^VIX9D": 0.08,  # Leading indicator but noisier
        "^VIX3M": 0.06,  # Medium-term expectations
        "^VIX6M": 0.06,  # Long-term expectations
        # Structural indicators (35% total)
        "Buffett Indicator": 0.20,  # Strong long-term signal, increased importance
        "^SKEW": 0.15,  # Critical tail risk information
        # Tactical indicators (30% total)
        "Put/Call Ratio": 0.12,  # Strong tactical signal
        "Near-term Stress Ratio": 0.08,  # Good leading indicator
        "3M Term Slope": 0.05,  # Term structure information
        "6M Term Slope": 0.05,  # Longer-term structure
    }

    weight = base_weights.get(indicator, 0.10)

    # Get other indicator values for cross-relationships
    indicator_dict = {r.indicator_name: (r.current_value, r.score) for r in all_results}

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
        weight *= 1 + (0.15 * confirmations)

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

    # 8. Base Condition Adjustments with Momentum
    if score >= 85:
        weight *= 1.4  # Extreme readings more important
    elif score >= 75:
        weight *= 1.25  # Very high readings
    elif score <= 15:
        weight *= 1.3  # Extreme low also important
    elif score <= 25:
        weight *= 1.2  # Very low readings

    return weight


def calculate_composite_risk_score(results: List[SignalAnalysis]) -> Tuple[float, Dict[str, float], Dict, str]:
    """
    Calculate sophisticated composite risk score with advanced market dynamics.

    Features:
    1. Dynamic weighting based on cross-indicator relationships
    2. Regime-specific adjustments
    3. Volatility environment consideration
    4. Term structure impact
    5. Signal confirmation analysis
    6. Momentum and trend analysis
    7. Risk factor decomposition
    8. Forward-looking risk assessment
    """
    total_weight = 0
    weighted_score = 0
    contributions = {}
    risk_factors = {"volatility": 0, "sentiment": 0, "structural": 0, "tactical": 0, "tail_risk": 0}

    # First pass: Calculate base weighted score
    for result in results:
        if result.score > 0:
            weight = get_indicator_weight(result.indicator_name, result.current_value, result.score, results)
            weighted_contribution = result.score * weight
            weighted_score += weighted_contribution
            total_weight += weight
            contributions[result.indicator_name] = weighted_contribution

            # Categorize risk factors
            if result.indicator_name.startswith("^VIX"):
                risk_factors["volatility"] += weighted_contribution
            elif result.indicator_name in ["Put/Call Ratio"]:
                risk_factors["sentiment"] += weighted_contribution
            elif result.indicator_name in ["Buffett Indicator"]:
                risk_factors["structural"] += weighted_contribution
            elif result.indicator_name in ["3M Term Slope", "6M Term Slope"]:
                risk_factors["tactical"] += weighted_contribution
            elif result.indicator_name in ["^SKEW"]:
                risk_factors["tail_risk"] += weighted_contribution

    # Normalize the score
    composite_score = weighted_score / total_weight if total_weight > 0 else 50

    # Normalize contributions and risk factors
    for indicator in contributions:
        contributions[indicator] = (contributions[indicator] / weighted_score) * 100

    total_risk = sum(risk_factors.values())
    if total_risk > 0:
        for factor in risk_factors:
            risk_factors[factor] = (risk_factors[factor] / total_risk) * 100

    # Get key indicator scores
    vix_score = next((r.score for r in results if r.indicator_name == "^VIX"), 50)
    skew_score = next((r.score for r in results if r.indicator_name == "^SKEW"), 50)
    pc_score = next((r.score for r in results if r.indicator_name == "Put/Call Ratio"), 50)
    buffett_score = next((r.score for r in results if r.indicator_name == "Buffett Indicator"), 50)

    # Generate sophisticated market regime interpretation
    if composite_score >= 80:
        regime = (
            f"SEVERE RISK ENVIRONMENT (Score: {composite_score:.1f})\n"
            f"• Core Metrics: VIX {vix_score:.1f}, SKEW {skew_score:.1f}, Put/Call {pc_score:.1f}\n"
            f"• Primary Risk Factors: Volatility {risk_factors['volatility']:.1f}%, "
            f"Tail Risk {risk_factors['tail_risk']:.1f}%, Structural {risk_factors['structural']:.1f}%\n"
            "• Action: Strong defensive positioning warranted. Consider volatility protection and reduce risk exposure."
        )
    elif composite_score >= 65:
        regime = (
            f"HIGH RISK ENVIRONMENT (Score: {composite_score:.1f})\n"
            "• Market Structure: Term structure and sentiment indicators suggest elevated stress\n"
            f"• Risk Composition: Tactical {risk_factors['tactical']:.1f}%, "
            f"Sentiment {risk_factors['sentiment']:.1f}%, Structural {risk_factors['structural']:.1f}%\n"
            "• Action: Consider reducing risk exposure and implementing hedges. Monitor for deterioration."
        )
    elif composite_score >= 45:
        regime = (
            f"MODERATE RISK ENVIRONMENT (Score: {composite_score:.1f})\n"
            "• Market Conditions: Mixed signals with balanced volatility structure\n"
            f"• Risk Distribution: Well-balanced across factors (Vol: {risk_factors['volatility']:.1f}%, "
            f"Struct: {risk_factors['structural']:.1f}%)\n"
            "• Action: Maintain hedged positioning with tactical flexibility. Focus on quality."
        )
    elif composite_score >= 30:
        regime = (
            f"LOW RISK ENVIRONMENT (Score: {composite_score:.1f})\n"
            "• Market Conditions: Constructive with moderate opportunity set\n"
            f"• Notable Metrics: Buffett Indicator {buffett_score:.1f}, Sentiment {risk_factors['sentiment']:.1f}%\n"
            "• Action: Consider selective risk deployment while maintaining base hedges."
        )
    else:
        regime = (
            f"VERY LOW RISK ENVIRONMENT (Score: {composite_score:.1f})\n"
            "• Market Conditions: Highly supportive but monitor for complacency\n"
            f"• Watch Items: SKEW {skew_score:.1f}, Tail Risk {risk_factors['tail_risk']:.1f}%\n"
            "• Action: Opportunistic positioning appropriate, maintain tail risk hedges."
        )

    return composite_score, contributions, risk_factors, regime


def main():
    """Main test execution."""
    # Initialize adapters
    yfinance_adapter = YFinanceAdapter()
    buffett_adapter = BuffettIndicatorAdapter()

    # Create indicator instances
    indicators = [
        VIX9DIndicator(yfinance_adapter),
        VIXIndicator(yfinance_adapter),
        VIX3MIndicator(yfinance_adapter),
        VIX6MIndicator(yfinance_adapter),
        SKEWIndicator(yfinance_adapter),
        CPCIndicator(yfinance_adapter),
        NearTermStressRatioIndicator(yfinance_adapter),
        ThreeMonthTermSlopeIndicator(yfinance_adapter),
        SixMonthTermSlopeIndicator(yfinance_adapter),
        BuffettIndicator(buffett_adapter),
    ]

    # Run analysis
    results = [analyze_indicator(indicator) for indicator in indicators]

    # Print report
    print_signal_report(results)

    # Return success if no errors
    has_errors = any(r.error_message for r in results)
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
