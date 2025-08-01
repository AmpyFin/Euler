"""
VIX 3-Month (^VIX3M) Indicator

Description:
-----------
Tracks 3-month constant-maturity implied volatility on the S&P 500.
Provides a medium-term view of expected market volatility and serves as a key
component in term structure analysis.

Key Characteristics:
------------------
- More stable than short-dated VIX measures
- Less sensitive to short-term market noise
- Critical for term structure analysis
- "Sticky" nature helps identify persistent stress

Signal Generation:
----------------
1. Persistence Analysis:
   - Primary: Monitor ^VIX/^VIX3M ratio
   - Stress signal: Ratio > 1.0 (backwardation)
   - Confirmation: Backwardation persisting ≥3 sessions

2. Mean Reversion Assessment:
   - ^VIX3M stays muted while ^VIX spikes
   - Indicates market expects temporary shock
   - Useful for distinguishing temporary vs. structural stress

Signal Confirmation:
------------------
- Track VX futures curve shape
- Monitor 1M/3M ratio persistence
- Watch correlation with other term structure metrics

Known Limitations:
----------------
- Slower to respond to market changes
- May miss very short-term stress events
- Less sensitive to immediate market catalysts

Implementation Notes:
-------------------
- Use z-score(120d) for regime-independent analysis
- Focus on persistence of term structure signals
- Consider institutional positioning effects
- Track alongside shorter-dated measures for context
"""

# Implementation below
