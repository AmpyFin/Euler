# Euler System

A sophisticated volatility regime detection system that analyzes hidden macrotrends to identify market regime shifts. This system is designed not to predict specific market movements, but rather to understand the underlying volatility environment and market stress conditions.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the system
python clients/system_client.py
```

## System Architecture

Euler uses a multi-threaded, event-driven architecture with four main components:

1. **FetchClient**: Continuously fetches market data (1-second intervals)
2. **ProcessingClient**: Calculates risk scores for each indicator
3. **InferenceClient**: Computes composite risk score and market regime
4. **SystemClient**: Orchestrates the system and provides callback interface

### Output Format

The system outputs a composite risk score (0-100) and market regime through:
1. Console logging
2. File logging (`logs/system.log`)
3. Callback interface for external system integration

Example output:
```
2025-08-02 15:09:13 | INFO | Market Risk Score: 78.49 | Current Regime: 🟥 HIGH STRESS
```

## Integration Guide

### Using Euler as a Subsystem

1. Import the SystemClient:
```python
from clients.system_client import SystemClient

def my_callback(analysis):
    """Handle market analysis updates.
    
    Args:
        analysis: MarketAnalysis object with:
            - score (float): 0-100 risk score
            - regime (MarketRegime): Current regime enum
            - data (Dict[str, ProcessedData]): Individual indicator data
    """
    score = analysis.score  # 0-100 float
    regime = analysis.regime  # MarketRegime enum
    # Your system's logic here

# Initialize and start
system = SystemClient(callback=my_callback)
system.start()
```

2. The callback receives updates whenever new data is processed, typically every 1-2 seconds.

## Customization Guide

### Adding New Indicators

1. Create indicator class in `indicators/live_indicators/`:
```python
from indicators.indicator import Indicator

class MyNewIndicator(Indicator):
    def __init__(self, adapter):
        super().__init__(adapter)
    
    def get_name(self) -> str:
        return "My Indicator Name"
        
    def fetch_last_quote(self) -> float:
        return self.adapter.fetch_last_quote(self.get_name())
```

2. Register in `registries/indicator_registry.py`:
```python
from indicators.live_indicators.my_new_indicator import MyNewIndicator

indicator_to_adapter_registry = {
    "MyNewIndicator": YFinanceAdapter  # or your custom adapter
}
```

### Adding New Data Adapters

1. Create adapter class in `adapters/`:
```python
from adapters.adapter import Adapter
from typing import Optional, Tuple, Dict, Any
from datetime import datetime

class MyNewAdapter(Adapter):
    def fetch_last_quote(self, symbol: str) -> float:
        # Implement data fetching logic
        pass
        
    def fetch_last_quote_with_date(self, symbol: str) -> Tuple[float, datetime]:
        # Implement with timestamp
        pass
        
    def fetch_historical_data(
        self, 
        symbol: str, 
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> Dict[datetime, Any]:
        # Implement historical data fetching
        pass
```

2. Use in indicator initialization:
```python
my_adapter = MyNewAdapter()
my_indicator = MyNewIndicator(my_adapter)
```

### Adding New Clients

1. Create client class in `clients/`:
```python
import logging
from queue import Queue
from threading import Thread, Event

class MyNewClient:
    def __init__(self):
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.should_run = False
        self.logger = logging.getLogger('MyNewClient')
        
    def start(self):
        self.should_run = True
        self.process_thread = Thread(target=self._process_loop)
        self.process_thread.start()
        
    def stop(self):
        self.should_run = False
        self.process_thread.join()
        
    def _process_loop(self):
        while self.should_run:
            # Implement processing logic
            pass
```

2. Integrate with SystemClient:
```python
class SystemClient:
    def __init__(self, callback=None):
        self.my_new_client = MyNewClient()
        # Connect queues
        self.my_new_client.output_queue = self.some_other_client.input_queue
```

## System Overview

The Euler system combines multiple volatility indicators across different time horizons to provide a holistic view of market conditions. It processes data on three main dimensions:

1. **Live Indicators**: Real-time market stress and volatility metrics
2. **Velocity Indicators**: Rate of change analysis (1D, 1W, 1M basis)
3. **Acceleration Indicators**: Change in rate of change (1D, 1W, 1M basis)

## Market Regime Levels (0-100 Scale)

The system outputs a score from 0-100 and classifies market conditions into ten distinct regimes:

1. **Extreme Calm (0-10)** 🟩
   - Unusually low volatility across all timeframes
   - Strong risk appetite, potentially complacent conditions
   - Historical examples: Extended bull markets, peak QE periods
   - Warning: May indicate market complacency

2. **Low Stress (10-20)** 🟩
   - Below-average volatility
   - Healthy market functioning with normal trading volumes
   - Term structure in steady contango
   - Favorable conditions for systematic strategies

3. **Stable (20-30)** 🟩
   - Normal market functioning
   - Volatility near long-term averages
   - Balanced put/call activity
   - Constructive trading environment

4. **Mild Uncertainty (30-40)** 🟨
   - Early signs of hedging activity
   - Slight elevation in near-term volatility
   - Minor term structure distortions
   - Typical pre-event positioning

5. **Elevated Caution (40-50)** 🟨
   - Above-average volatility
   - Increased hedging costs
   - Early signs of risk reduction
   - Heightened market sensitivity

6. **High Uncertainty (50-60)** 🟧
   - Significant volatility elevation
   - Notable increase in tail risk pricing
   - Term structure flattening
   - Active defensive positioning

7. **Stress Conditions (60-70)** 🟥
   - Material risk reduction across assets
   - Volatility term structure inversions
   - Elevated put/call ratios
   - Liquidity deterioration

8. **High Stress (70-80)** 🟥
   - Broad risk aversion
   - Sharp volatility spikes
   - Significant defensive positioning
   - Systematic strategy deleveraging

9. **Severe Stress (80-90)** ⬛
   - Acute market stress
   - Extreme volatility levels
   - Widespread forced liquidation
   - Major systematic strategy disruption

10. **Crisis (90-100)** ⬛
    - Extreme market dislocation
    - Historic volatility levels
    - Market functioning impaired
    - Potential intervention conditions

### Live Indicators

These indicators provide real-time insights into market conditions:

- **^VIX9D**: 9-day implied volatility for near-term event risk detection
- **^VIX**: 30-day implied volatility (the classic "fear gauge")
- **^VIX3M**: 3-month implied volatility for medium-term stress assessment
- **^VIX6M**: 6-month implied volatility for structural risk evaluation
- **^SKEW**: Tail risk pricing indicator
- **^CPC**: Put/Call ratio for sentiment analysis
- **Near-term Stress Ratio**: ^VIX9D/^VIX for event window analysis
- **3M Term Slope**: ^VIX/^VIX3M for contango/backwardation analysis
- **6M Term Slope**: ^VIX/^VIX6M for long-term volatility regime assessment
- **Buffett Indicator**: Total Market Cap/GDP for macro valuation regime detection

### Velocity Indicators (1D, 1W, 1M)

Track the rate of change in key metrics to identify momentum and trend development:
- First derivative of volatility metrics
- Measures speed of regime transitions
- Helps identify acceleration/deceleration in market stress

### Acceleration Indicators (1D, 1W, 1M)

Monitor changes in the rate of change to detect regime shift catalysts:
- Second derivative of volatility metrics
- Identifies inflection points in market stress
- Crucial for early detection of regime transitions

## Implementation Guidelines

### Signal Processing

1. **Standardization**:
   - Compute z-scores (20d/60d/120d)
   - Track persistence counters for key ratios 
   - Winsorize 1% tails to handle outliers

2. **Market State Classification**:

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

3. **Signal Smoothing**:
   - Use 5-day EMA for noise reduction
   - Apply to ^CPC and ^SKEW particularly

## Usage Notes

- System is designed for regime detection, not direct trading signals
- Combine multiple indicators for higher confidence readings
- Consider market context (OPEX, holidays, major events)
- Use z-scores to standardize across different volatility regimes