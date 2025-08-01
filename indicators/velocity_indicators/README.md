# Velocity Indicators

## Overview

Velocity indicators track the first derivative (rate of change) of key volatility metrics. These indicators are essential for understanding the speed of market transitions and the momentum of volatility regime shifts.

## Time Horizons

Indicators are calculated on three time bases:
- 1-day (1D): Immediate momentum shifts
- 1-week (1W): Short-term trend development
- 1-month (1M): Medium-term momentum patterns

## Implementation Details

### Calculation Methodology

For each base indicator (VIX series, ratios, etc.):
1. Calculate point-to-point changes
2. Apply appropriate time scaling
3. Implement necessary smoothing
4. Generate standardized metrics (z-scores)

### Signal Generation

- **Positive Velocity**: Increasing metric
  - May indicate building market stress
  - Watch for acceleration confirmation
  - Consider positioning impacts

- **Negative Velocity**: Decreasing metric
  - May signal stress reduction
  - Monitor for stabilization
  - Track alongside absolute levels

### Usage Guidelines

1. **Trend Identification**:
   - Monitor velocity persistence
   - Watch for velocity divergences
   - Consider market context

2. **False Signal Mitigation**:
   - Apply appropriate smoothing
   - Consider calendar effects
   - Monitor alongside primary metrics

3. **Implementation Notes**:
   - Winsorize extreme values
   - Use consistent smoothing
   - Account for institutional effects

## Key Considerations

- Noise increases at shorter timeframes
- Calendar effects impact readings
- Institutional flows affect velocity
- Combine with primary indicators
- Use appropriate smoothing methods
- Consider regime context 