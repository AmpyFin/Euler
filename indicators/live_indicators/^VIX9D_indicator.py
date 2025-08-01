"""
VIX 9-Day (^VIX9D) Indicator

Description:
-----------
Tracks the 9-day constant-maturity implied volatility on the S&P 500, built from weekly SPX options.
This indicator is particularly sensitive to near-term catalysts and event risk.

Key Characteristics:
------------------
- Highly responsive to near-term events (CPI, Fed, earnings, geopolitics)
- Influenced by weekly options flow and dealer gamma positioning
- Provides early warning for event-driven volatility spikes

Typical Ranges:
-------------
- Low-teens: Quiet market conditions
- High-teens/20s: Pre-event risk pricing
- >30: Elevated stress / significant market concern

Signal Generation:
----------------
1. Event Window Analysis:
   - Mild concern: ^VIX9D/^VIX > 1.05
   - Firm concern: ^VIX9D/^VIX > 1.10
   - Acute stress: ^VIX9D/^VIX > 1.20

2. Momentum Check:
   - Significant repricing: 3-day change (Δ3d) > +5 points

Signal Confirmation:
------------------
- Watch for concurrent moves in:
  * HYG (down)
  * UUP (up)
  * SPX futures depth thinning

Known Limitations:
----------------
- Can be artificially low during holiday weeks
- Subject to OPEX week distortions
- 0DTE flow can create false signals

Implementation Notes:
-------------------
- Use 60-day z-score for regime-independent analysis
- Monitor ratio vs ^VIX to detect relative stress
- Winsorize 1% tails to handle outliers
- Consider holiday/OPEX calendar effects
"""

# Implementation below
