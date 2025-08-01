"""
VIX 30-Day (^VIX) Indicator

Description:
-----------
The classic "fear gauge" - tracks 1-month constant-maturity implied volatility on the S&P 500.
Serves as the baseline measure of market anxiety and expected near-term volatility.

Key Characteristics:
------------------
- Industry standard measure of implied volatility
- Reflects 30-day forward-looking market expectations
- Highly liquid and widely monitored

Regime Bands:
-----------
- <13: Complacent market conditions
- 13-20: Normal market operation
- 20-30: Elevated caution
- >30: Acute market stress

Signal Generation:
----------------
1. Stress Onset Detection:
   - Primary: ^VIX z-score(60d) > +1.0
   - Confirmation: ^VIX/^VIX3M > 1.0 (backwardation)

2. Capitulation Signals:
   - Intraday spike > +8-10 points from 5-day median
   - Often coincides with forced de-leveraging

Signal Confirmation:
------------------
Watch for concurrent moves in:
- HYG (down) + LQD (up) = Growth scare
- HYG (down) + LQD (down) = Rates shock
- UUP (up) = Risk-off positioning

Known Limitations:
----------------
- Can be mechanically lifted by OPEX effects
- Large overwrite programs may distort readings
- Level alone insufficient - pair with term structure

Implementation Notes:
-------------------
- Use both absolute level and z-score analysis
- Monitor term structure ratios for context
- Track persistence of backwardation
- Consider options market calendar effects
"""

# Implementation below
