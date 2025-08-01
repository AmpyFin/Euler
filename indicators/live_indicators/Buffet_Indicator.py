"""
Buffett Indicator

Description:
-----------
The Buffett Indicator, named after Warren Buffett, measures the total market value of all publicly traded stocks 
relative to the Gross Domestic Product (GDP). It serves as a broad measure of market valuation and potential overextension.

Calculation: Total Market Capitalization / GDP

Key Characteristics:
------------------
- Macro-level valuation metric
- Long-term regime indicator
- Mean-reverting tendency
- Leading indicator for structural shifts

Typical Ranges:
-------------
- <90%: Significantly undervalued
- 90-115%: Fairly valued
- 115-135%: Moderately overvalued
- >135%: Significantly overvalued
- >200%: Extreme bubble territory

Signal Generation:
----------------
1. Valuation Signals:
   - Extreme overvaluation: >2 std dev above mean
   - Extreme undervaluation: >2 std dev below mean
   - Track rate of change for regime shifts

2. Trend Analysis:
   - Monitor quarterly changes
   - Track relationship with VIX regimes
   - Consider alongside other macro indicators

Signal Confirmation:
------------------
- Monitor alongside:
  * Corporate profit margins
  * Interest rate environment
  * International market valuations
  * Credit market conditions

Known Limitations:
----------------
- GDP data lags by one quarter
- International revenue impacts ratio
- Structural shifts can change baseline
- Monetary policy affects interpretation
- Limited use for short-term signals

Implementation Notes:
-------------------
- Use quarterly GDP data
- Adjust for international revenue
- Consider monetary conditions
- Track both absolute levels and z-scores
- Monitor rate of change across timeframes
"""

# Implementation below
