"""
SKEW Index (^SKEW) Indicator

Description:
-----------
Measures the perceived tail risk in the S&P 500 by analyzing the steepness of implied volatility skew.
Specifically tracks the relative cost of out-of-the-money put options versus at-the-money options.
End-of-day indicator that provides insight into the market's crash risk assessment.

Key Characteristics:
------------------
- Reflects demand for tail risk protection
- Computed from OTM put option prices
- Updates once per day (EOD)
- Independent of absolute volatility level

Typical Ranges:
-------------
- 115-150: Normal operating range
- >135-140: Heavy tail risk hedging
- <120: Flat skew/cheap crash protection
- Extreme readings warrant mean reversion watch

Signal Generation:
----------------
1. Silent Worry Detection:
   - High SKEW (>135) + Low VIX
   - Indicates quiet tape but active hedging
   - Often precedes volatility events

2. Capitulation Analysis:
   - SKEW collapse during high VIX
   - May signal market washout
   - Watch for stabilization potential

Signal Confirmation:
------------------
- Monitor put option volumes
- Track institutional positioning
- Watch correlation with VIX term structure

Known Limitations:
----------------
- End-of-day calculation only
- Affected by structured product flows
- Sensitive to systematic put writing
- Can produce false signals near expiration

Implementation Notes:
-------------------
- Use 5-day EMA for noise reduction
- Consider options expiration effects
- Track alongside other tail risk metrics
- Monitor changes in hedging patterns
"""

# Implementation below
