"""
3-Month Term Slope (^VIX/^VIX3M) Indicator

Description:
-----------
Measures the relationship between 30-day and 90-day implied volatility.
Key indicator for volatility term structure analysis and market stress detection.
Provides clean proxy for contango/backwardation conditions.

Key Characteristics:
------------------
- Primary term structure indicator
- Updates intraday
- Mean-reverting tendency
- Critical for regime identification

Signal Thresholds:
----------------
- >1.0: Backwardation (stress)
- <1.0: Contango (calm)
- <0.9: Steep contango (very calm)
- Persistence ≥3 days increases confidence

Signal Generation:
----------------
1. Stress Detection:
   - Monitor for crossover above 1.0
   - Track persistence of backwardation
   - Watch rate of change in ratio

2. Regime Identification:
   - Sustained backwardation = stress regime
   - Deep contango = low stress regime
   - Transition zones = regime shift potential

Signal Confirmation:
------------------
- Monitor absolute VIX levels
- Track other term structure ratios
- Watch market internals
- Consider institutional flows

Known Limitations:
----------------
- Single-day flips can be noise
- OPEX effects can distort readings
- Roll effects near futures expiration
- May lag in fast-moving markets

Implementation Notes:
-------------------
- Calculate ratio intraday
- Focus on multi-day persistence
- Consider calendar effects
- Monitor alongside other term structure metrics
"""

# Implementation below
