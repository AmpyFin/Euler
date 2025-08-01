# Live Indicators

## Overview

Live indicators provide real-time insights into market volatility conditions and stress levels. This suite of indicators combines various VIX-based metrics and their relationships to identify market regimes, stress levels, and potential regime transitions.

## Core Indicators

### Primary VIX Series
- **^VIX9D**: 9-day implied volatility (near-term event risk)
- **^VIX**: 30-day implied volatility (classic "fear gauge")
- **^VIX3M**: 3-month implied volatility (medium-term outlook)
- **^VIX6M**: 6-month implied volatility (structural risk assessment)

### Derivative Metrics
- **^SKEW**: Tail risk pricing indicator
- **^CPC**: Put/Call ratio for sentiment analysis

### Term Structure Ratios
- **Near-term Stress**: ^VIX9D/^VIX (event risk)
- **3M Term Slope**: ^VIX/^VIX3M (medium-term stress)
- **6M Term Slope**: ^VIX/^VIX6M (structural stress)

## Implementation Guidelines

### Signal Processing
1. **Standardization**:
   - Compute appropriate z-scores
   - Track persistence metrics
   - Winsorize extreme values

2. **Smoothing**:
   - Apply 5-day EMA where appropriate
   - Consider calendar effects
   - Handle roll/OPEX distortions

### Market State Classification

**Green (Calm)**:
- ^VIX9D/^VIX < 1.0
- ^VIX/^VIX3M < 0.95
- ^VIX z60d < +0.5

**Yellow (Event Risk)**:
- ^VIX9D/^VIX ≥ 1.05 OR
- ^CPC 5d > 0.85 OR
- ^SKEW > 135

**Red (Escalating)**:
- ^VIX/^VIX3M ≥ 1.0 AND
- ^VIX z60d ≥ +1.0 AND
- persistence(^VIX/^VIX3M > 1, ≥3 days)

## Key Considerations

- Focus on term structure relationships
- Monitor persistence of signals
- Consider institutional effects
- Account for calendar impacts
- Use appropriate smoothing
- Combine multiple indicators for confidence 