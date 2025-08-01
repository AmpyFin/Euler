"""
6-Month Term Slope (^VIX/^VIX6M) Indicator

Description:
-----------
Measures the relationship between 30-day and 180-day implied volatility.
Long-term term structure indicator for identifying persistent volatility regimes.
Critical for distinguishing between temporary and structural market stress.

Key Characteristics:
------------------
- Longest-term structure comparison
- Updates intraday
- Slower-moving than shorter-term ratios
- Important for regime identification

Signal Thresholds:
----------------
- >1.0: Severe stress (structural)
- 0.8-1.0: Building stress
- <0.8: Normal/calm (steep contango)
- Persistence key for confidence

Signal Generation:
----------------
1. Structural Stress Detection:
   - Monitor for sustained ratio > 1.0
   - Track 3-5 session persistence
   - Watch rate of change in ratio

2. Regime Analysis:
   - Brief spikes = event risk
   - Sustained elevation = regime shift
   - Gradual changes = structural shift

Signal Confirmation:
------------------
- Monitor shorter-term ratios
- Track institutional positioning
- Watch market internals
- Consider macro environment

Known Limitations:
----------------
- Very slow to respond to changes
- Heavy influence from structured products
- May miss short-term stress events
- Complex institutional effects

Implementation Notes:
-------------------
- Calculate ratio intraday
- Use rolling z-score(120d)
- Focus on multi-day persistence
- Monitor alongside shorter-term metrics
"""

# Implementation below