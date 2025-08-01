"""
VIX 6-Month (^VIX6M) Indicator

Description:
-----------
Tracks 6-month constant-maturity implied volatility on the S&P 500.
Provides insight into longer-term volatility expectations and structural market concerns.
Critical for identifying persistent regime shifts and tail hedging activity.

Key Characteristics:
------------------
- Longest-dated standard VIX measure
- Highly stable relative to shorter tenors
- Reflects institutional hedging demand
- Key indicator for structural market stress

Signal Generation:
----------------
1. Term Structure Analysis:
   - Calm markets: ^VIX/^VIX6M < 0.8 (steep contango)
   - Building stress: Ratio rising toward 1.0
   - Structural concern: Ratio > 1.0 (backwardation)

2. Event Risk Assessment:
   - Minimal ^VIX6M movement during ^VIX spikes
   - Indicates temporary/event-driven volatility
   - Useful for distinguishing regime change vs noise

Signal Confirmation:
------------------
- Monitor persistence of term structure signals
- Track institutional hedging flows
- Watch correlation with other long-dated metrics

Known Limitations:
----------------
- Heavy influence from systematic hedging programs
- Affected by structured product supply
- Requires patience - avoid single-day readings
- May miss short-term market stress

Implementation Notes:
-------------------
- Use rolling z-score(120d) for regime comparison
- Focus on multi-day signal persistence
- Consider institutional positioning effects
- Track alongside shorter-dated measures
"""

# Implementation below
