# Euler System

A sophisticated volatility regime detection system that analyzes hidden macrotrends to identify market regime shifts. This system is designed not to predict specific market movements, but rather to understand the underlying volatility environment and market stress conditions.

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/AmpyFin/Euler.git
cd Euler
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Verify installation**:
```bash
python3 -c "import yfinance; import PyQt5; print('Installation successful!')"
```

## Configuration

The system behavior is controlled by the `control.py` file in the root directory. Edit this file to configure how the system runs:

```python
# control.py

# System Mode Configuration
broadcast_mode = False      # If True, broadcasts results over network
GUI_mode = True            # If True, displays GUI interface
run_continuously = True    # If True, runs continuously; if False, runs once and exits

# Network Configuration (for broadcast mode)
broadcast_network = "127.0.0.1"  # Network address to broadcast on
broadcast_port = 5000            # Port for broadcasting
```

### Configuration Options

- **`broadcast_mode`**: 
  - `True`: System broadcasts market analysis data over UDP network
  - `False`: System runs locally without broadcasting

- **`GUI_mode`**: 
  - `True`: Displays PyQt5 GUI with real-time market analysis
  - `False`: Console-only output

- **`run_continuously`**: 
  - `True`: System runs continuously, updating every 60 seconds
  - `False`: System runs one analysis cycle and exits

## Quick Start

### Basic Usage

```bash
# Run with default settings (GUI mode, continuous)
python3 clients/system_client.py
```

### Different Modes

1. **GUI Mode (Default)**:
```python
# control.py
broadcast_mode = False
GUI_mode = True
run_continuously = True
```

2. **Broadcast Mode**:
```python
# control.py
broadcast_mode = True
GUI_mode = False
run_continuously = True
```

3. **Single Run Mode**:
```python
# control.py
broadcast_mode = False
GUI_mode = True
run_continuously = False
```

4. **Console Only Mode**:
```python
# control.py
broadcast_mode = False
GUI_mode = False
run_continuously = True
```

### Testing Broadcast Mode

If using broadcast mode, you can test the network output with the provided receiver:

```bash
# Terminal 1: Start the system in broadcast mode
python3 clients/system_client.py

# Terminal 2: Start the broadcast receiver
python3 tests/e2e_tests/test_broadcast_receiver.py
```

## System Architecture

Euler uses a sequential, event-driven architecture with four main components:

1. **FetchClient**: Fetches market data from various sources
2. **ProcessingClient**: Calculates risk scores for each indicator
3. **InferenceClient**: Computes composite risk score and market regime
4. **SystemClient**: Orchestrates the system and provides GUI/broadcast interface

### Output Format

The system outputs a composite risk score (0-100) and market regime through:
1. Console logging
2. File logging (`logs/system.log`)
3. GUI interface (if enabled)
4. Network broadcast (if enabled)

Example output:
```
2025-08-02 15:09:13 | INFO | Market Risk Score: 78.49 | Current Regime: 🟥 HIGH STRESS
```

## GUI Interface

When `GUI_mode = True`, the system displays a PyQt5 interface with two tabs:

1. **Overview**: Overall market score, regime, and score history graph
2. **Details**: Individual indicator data with raw values, risk scores, weights, and contribution percentages

The GUI updates automatically every 60 seconds when `run_continuously = True`.

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

2. The callback receives updates whenever new data is processed, typically every 60 seconds.

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

## Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   pip install -r requirements.txt
   ```

2. **GUI Not Displaying**:
   - Ensure `GUI_mode = True` in `control.py`
   - Check PyQt5 installation: `pip install PyQt5`

3. **Network Broadcast Issues**:
   - Verify `broadcast_mode = True` in `control.py`
   - Check firewall settings
   - Use the test receiver: `python3 tests/e2e_tests/test_broadcast_receiver.py`

4. **No Data Updates**:
   - Check internet connection
   - Verify yfinance is working: `python3 -c "import yfinance; print(yfinance.Ticker('^VIX').info['regularMarketPrice'])"`

## Usage Notes

- System is designed for regime detection, not direct trading signals
- Combine multiple indicators for higher confidence readings
- Consider market context (OPEX, holidays, major events)
- Use z-scores to standardize across different volatility regimes
- GUI updates every 60 seconds in continuous mode
- System can be configured for single-run analysis or continuous monitoring