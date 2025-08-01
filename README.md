# Euler-Model

A sophisticated volatility regime detection system that analyzes hidden macrotrends to identify market regime shifts. This system is designed not to predict specific market movements, but rather to understand the underlying volatility environment and market stress conditions.

## System Overview

The Euler model combines multiple volatility indicators across different time horizons to provide a holistic view of market conditions. It processes data on three main dimensions:

1. **Live Indicators**: Real-time market stress and volatility metrics
2. **Velocity Indicators**: Rate of change analysis (1D, 1W, 1M basis)
3. **Acceleration Indicators**: Change in rate of change (1D, 1W, 1M basis)

### Live Indicators

These indicators provide real-time insights into market conditions:

- **^VIX9D**: 9-day implied volatility for near-term event risk detection
- **^VIX**: 30-day implied volatility (the classic "fear gauge")
- **^VIX3M**: 3-month implied volatility for medium-term stress assessment
- **^VIX6M**: 6-month implied volatility for structural risk evaluation
- **^SKEW**: Tail risk pricing indicator
- **^CPC**: Put/Call ratio for sentiment analysis
- **Near-term Stress Ratio**: ^VIX9D/^VIX for event window analysis
- **3M Term Slope**: ^VIX/^VIX3M for contango/backwardation analysis
- **6M Term Slope**: ^VIX/^VIX6M for long-term volatility regime assessment

### Velocity Indicators (1D, 1W, 1M)

Track the rate of change in key metrics to identify momentum and trend development:
- First derivative of volatility metrics
- Measures speed of regime transitions
- Helps identify acceleration/deceleration in market stress

### Acceleration Indicators (1D, 1W, 1M)

Monitor changes in the rate of change to detect regime shift catalysts:
- Second derivative of volatility metrics
- Identifies inflection points in market stress
- Crucial for early detection of regime transitions

## Implementation Guidelines

### Signal Processing

1. **Standardization**:
   - Compute z-scores (20d/60d/120d)
   - Track persistence counters for key ratios
   - Winsorize 1% tails to handle outliers

2. **Market State Classification**:

   **Green (Calm)**:
   - ^VIX9D/^VIX < 1.0
   - ^VIX/^VIX3M < 0.95
   - ^VIX z60d < +0.5

   **Yellow (Event Risk)**:
   - ^VIX9D/^VIX ≥ 1.05 OR
   - ^CPC 5d > 0.85 OR
   - ^SKEW > 135

   **Red (Escalating)**:
   - ^VIX/^VIX3M ≥ 1.0 AND
   - ^VIX z60d ≥ +1.0 AND
   - persistence(^VIX/^VIX3M > 1, ≥3 days)

3. **Signal Smoothing**:
   - Use 5-day EMA for noise reduction
   - Apply to ^CPC and ^SKEW particularly

## Usage Notes

- System is designed for regime detection, not direct trading signals
- Combine multiple indicators for higher confidence readings
- Consider market context (OPEX, holidays, major events)
- Use z-scores to standardize across different volatility regimes