"""
Put/Call Ratio (^CPC) Indicator

Description:
-----------
Tracks the ratio of put option volume to call option volume across all CBOE markets.
Provides insight into market sentiment and hedging behavior through options activity.
End-of-day indicator useful for contrarian signal generation.

Key Characteristics:
------------------
- Sentiment indicator based on options flow
- Updates once per day (EOD)
- Includes both index and equity options
- Mean-reverting tendency at extremes

Typical Ranges:
-------------
- 0.6-0.9: Normal daily range
- >0.9-1.1: Elevated hedging/fear
- <0.5: Potential complacency
- Extreme readings often precede reversals

Signal Generation:
----------------
1. Contrarian Signals:
   - Use 5-day moving average
   - Extreme readings suggest mean reversion
   - High readings often precede bounces
   - Low readings may precede pullbacks

2. Context Analysis:
   - Pair with VIX term structure
   - Consider market regime
   - Watch for confirmation in price action

Signal Confirmation:
------------------
- Monitor VIX term structure
- Track institutional positioning
- Watch for price confirmation
- Consider market breadth metrics

Known Limitations:
----------------
- End-of-day calculation only
- Mix of index/equity options affects reading
- Can be skewed by large institutional trades
- May produce false signals in trending markets

Implementation Notes:
-------------------
- Use 5-day moving average for smoothing
- Consider tracking ^CPCE (equity-only) ratio
- Monitor alongside other sentiment indicators
- Watch for divergences with price action
"""

# Implementation below
