"""
Near-term Stress Ratio (^VIX9D/^VIX) Indicator

Description:
-----------
Measures the relationship between 9-day and 30-day implied volatility.
Provides insight into immediate market stress and event risk pricing.
Particularly useful for identifying short-term volatility spikes and event windows.

Key Characteristics:
------------------
- Highly sensitive to near-term events
- Mean-reverting tendency
- Updates intraday
- Useful for position sizing decisions

Signal Thresholds:
----------------
- >1.05: Caution - mild event risk
- >1.10: Warning - firm event risk
- >1.20: Alert - acute event risk
- <1.00: Normal market conditions

Signal Generation:
----------------
1. Event Risk Detection:
   - Monitor ratio crossings of key levels
   - Track persistence above thresholds
   - Watch rate of change in ratio

2. Position Sizing Signals:
   - Use for tactical exposure management
   - Consider reducing risk when elevated
   - Potential to add risk post-event

Signal Confirmation:
------------------
- Monitor absolute VIX levels
- Track term structure changes
- Watch market internals
- Consider event calendar

Known Limitations:
----------------
- Highly mean-reverting nature
- Can produce false signals
- Not suitable for directional calls
- Sensitive to calendar effects

Implementation Notes:
-------------------
- Calculate ratio intraday
- Use for position size adjustment
- Monitor alongside event calendar
- Consider holiday/OPEX effects
"""

# Implementation below