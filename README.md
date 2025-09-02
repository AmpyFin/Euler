# Euler System

An advanced **market risk assessment system** featuring **10 sophisticated weighting strategies** including **3 ML-enhanced ensemble methods** and **predictive risk indicators** to identify dangerous market conditions before they become crises. Euler focuses on **structural overvaluation risk** and **market stress signals** that precede major market corrections.

**Key Innovation**: Modular weighting system with strategies ranging from simple equal weighting to advanced ML-enhanced adaptive ensemble methods using scikit-learn that automatically learn optimal strategy combinations and adapt based on market conditions.

## Demo

[![Euler System Demo](https://img.youtube.com/vi/9MivM2AdHtM/0.jpg)](https://www.youtube.com/watch?v=9MivM2AdHtM)

*Click the image above to watch the demo video*

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

## Configuration & Updates

### System Configuration
The system behavior is controlled by the `control.py` file in the root directory:

```python
# control.py - System Mode Configuration
broadcast_mode = False      # Network broadcasting
GUI_mode = True            # GUI interface
run_continuously = True    # Continuous vs single run
broadcast_network = "127.0.0.1"  # Network settings
broadcast_port = 5000
```

**See the fully documented `control.py` file for detailed configuration options and usage examples.**

### Weighting Strategy Configuration
The weighting method is configured in `registries/weight_registry.py`:

```python
# registries/weight_registry.py - Weighting Strategy Configuration
DEFAULT_WEIGHTING_METHOD = WeightingMethod.STATISTICAL_DYNAMIC

# Available options:
# WeightingMethod.EQUAL_WEIGHT          # Baseline/benchmarking
# WeightingMethod.LINEAR_STATIC         # Conservative/traditional  
# WeightingMethod.RISK_PROPORTIONAL     # Crisis-focused
# WeightingMethod.STATISTICAL_DYNAMIC   # Auto-discovery (default)
# WeightingMethod.VOLATILITY_ADJUSTED   # Noise reduction
# WeightingMethod.MOMENTUM_BASED        # Trend following
# WeightingMethod.ADAPTIVE_ENSEMBLE     # Heuristic meta-strategy
# WeightingMethod.ML_ADAPTIVE_STACKING  # ML ensemble (most sophisticated)
# WeightingMethod.ML_ADAPTIVE_VOTING    # ML ensemble (robust averaging)
# WeightingMethod.ML_ADAPTIVE_BLENDING  # ML ensemble (custom weighting)
```

### System Updates & Maintenance

#### **Updating Dependencies**
```bash
# Update all packages to latest versions
pip install --upgrade -r requirements.txt

# Check for security vulnerabilities
pip audit

# Update specific packages
pip install --upgrade yfinance PyQt5 numpy pandas
```

#### **System Health Checks**
```bash
# Verify installation
python3 -c "import yfinance; import PyQt5; print('✅ Dependencies OK')"

# Test weighting system
python3 -c "from registries.weight_registry import get_strategy_summary; print(get_strategy_summary())"

# Quick system test
python3 clients/system_client.py  # Should run without errors
```

#### **Configuration Validation**
```python
# Test your configuration
from registries.weight_registry import weight_registry
print(f"Active strategy: {weight_registry.get_active_method()}")

# Test all strategies
from registries.weight_registry import WeightingMethod, set_weighting_method
for method in WeightingMethod:
    try:
        set_weighting_method(method)
        print(f"✅ {method.value} working")
    except Exception as e:
        print(f"❌ {method.value} error: {e}")
```

#### **Performance Monitoring**
```bash
# Monitor system resource usage
python3 -c "
import psutil
import time
print('Monitoring system performance...')
for i in range(5):
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    print(f'CPU: {cpu}% | Memory: {memory}%')
    time.sleep(1)
"

# Check data fetch performance
python3 -c "
import time
from indicators.risk_indicators.buffett_indicator import BuffettIndicator
from adapters.buffet_indicator_adapter import BuffettIndicatorAdapter

start = time.time()
indicator = BuffettIndicator(BuffettIndicatorAdapter())
value = indicator.fetch_last_quote()
duration = time.time() - start
print(f'Buffett Indicator fetch: {duration:.2f}s -> {value}')
"
```

#### **Backup & Recovery**
```bash
# Backup configuration
cp control.py control.py.backup
cp registries/weight_registry.py registries/weight_registry.py.backup

# Backup custom strategies
tar -czf custom_strategies_backup.tar.gz weight_strategies/

# Restore from backup
cp control.py.backup control.py
cp registries/weight_registry.py.backup registries/weight_registry.py
```

#### **Troubleshooting Common Issues**

1. **Import Errors**:
   ```bash
   # Fix Python path issues
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   
   # Reinstall dependencies
   pip install --force-reinstall -r requirements.txt
   ```

2. **GUI Not Displaying**:
   ```python
   # Check GUI configuration
   import control
   print(f"GUI_mode: {control.GUI_mode}")
   
   # Test PyQt5 installation
   from PyQt5.QtWidgets import QApplication
   app = QApplication([])
   print("✅ PyQt5 working")
   ```

3. **Network Issues**:
   ```python
   # Test network connectivity
   import yfinance as yf
   ticker = yf.Ticker("SPY")
   data = ticker.history(period="1d")
   print(f"✅ Yahoo Finance: {len(data)} records")
   ```

4. **Strategy Errors**:
   ```python
   # Debug strategy issues
   from registries.weight_registry import weight_registry
   
   try:
       weights = weight_registry.calculate_weights({
           'Buffett Indicator': 50,
           'Put/Call Ratio': 60
       })
       print(f"✅ Strategy working: {weights}")
   except Exception as e:
       print(f"❌ Strategy error: {e}")
   ```

#### **Version Management**
```bash
# Check current version
git describe --tags --always

# View recent changes
git log --oneline -10

# Update to latest version
git pull origin main

# Rollback if needed
git checkout <previous-commit-hash>
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

### Adding New Risk Indicators

1. Create risk indicator class in `indicators/risk_indicators/`:
```python
from indicators.indicator import Indicator

class MyNewRiskIndicator(Indicator):
    def __init__(self, adapter):
        super().__init__(adapter)
    
    def get_name(self) -> str:
        return "My Risk Indicator Name"
        
    def fetch_last_quote(self) -> float:
        return self.adapter.fetch_last_quote(self.get_name())
```

2. Register in `registries/indicator_registry.py` following Val architecture:
```python
from indicators.risk_indicators.my_new_risk_indicator import MyNewRiskIndicator

# Add to metric provider factories
_METRIC_PROVIDER_FACTORIES["my_risk_metric"] = {
    "provider_name": lambda: MyDataAdapter(),
}

# Set active provider
_ACTIVE_METRIC_PROVIDER["my_risk_metric"] = "provider_name"

# Add to indicator factories
_INDICATOR_FACTORIES["my_risk_metric"] = lambda: MyNewRiskIndicator

# Enable the indicator
_ENABLED_INDICATORS.append("my_risk_metric")
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

Euler is a **predictive market risk assessment system** featuring **10 sophisticated weighting strategies** including **3 ML-enhanced ensemble methods** that combine multiple forward-looking indicators to detect dangerous market conditions before they become crises. The modular architecture allows switching between different weighting approaches based on market conditions and analysis requirements.

### **Weighting Strategies Overview**

#### 🔸 **Static Strategies** (Simple)
- **Equal Weight**: Unbiased baseline - all indicators receive identical weights (1/N)
- **Linear Static**: Expert-based fixed weights derived from historical analysis and domain knowledge

#### 🔸 **Dynamic Strategies** (Simple to Moderate)  
- **Risk Proportional**: Weights directly proportional to current risk scores - crisis indicators get maximum weight
- **Volatility Adjusted**: Emphasizes stable indicators while reducing impact of noisy, high-volatility signals
- **Momentum Based**: Prioritizes indicators showing strong upward risk momentum and trend acceleration

#### 🔸 **Adaptive Strategies** (Advanced)
- **Statistical Dynamic**: Auto-discovery with regime adaptation, cross-correlation analysis, and historical performance tracking
- **Adaptive Ensemble**: Meta-strategy combining multiple approaches based on real-time market regime detection

#### 🔸 **ML-Adaptive Strategies** (Expert)
- **ML Adaptive Stacking**: Scikit-learn ensemble using stacking method - meta-learner combines base models for optimal predictions
- **ML Adaptive Voting**: Scikit-learn ensemble using voting method - robust averaging with optional performance-based weights
- **ML Adaptive Blending**: Scikit-learn ensemble using blending method - custom weighted combination with historical learning

### **Core Philosophy: Risk Score 0-100**
- **0-25 (Euphoria)**: Dangerous market complacency - high structural risk despite low volatility
- **25-60 (Normal)**: Balanced market conditions with moderate risk factors  
- **60-85 (Stress)**: Elevated risk with multiple warning signals activated
- **85-100 (Crisis)**: Imminent danger - multiple critical risk factors aligned

### **Key System Features**

1. **Modular Architecture**: Easy strategy switching via configuration - no code changes required
2. **Regime-Aware Processing**: Advanced strategies adapt weights based on market conditions
3. **Auto-Discovery Capabilities**: Automatic profiling and weighting of new indicators
4. **Multi-Strategy Validation**: Compare results across strategies for robust analysis
5. **Extensible Design**: Simple addition of new strategies via the `weight_strategies/` directory

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

### **Predictive Risk Indicators**

Euler uses **6 core predictive indicators** that gauge future market risk rather than react to current price movements:

#### **Structural Risk Indicators**
- **Buffett Indicator** (Market Cap/GDP): Detects structural overvaluation and bubble conditions
  - *Weight*: 30% in euphoria phases (primary bubble risk)
  - *Predictive Power*: 6+ months leading indicator for major corrections

#### **Sentiment & Positioning Indicators**  
- **Put/Call Ratio**: Market sentiment and defensive positioning analysis
  - *Weight*: 15-20% (higher in stress periods)
  - *Predictive Power*: 1-4 weeks leading indicator for volatility spikes

- **SKEW Index**: Tail risk pricing and crash probability assessment
  - *Weight*: 10-15% (higher when complacency is elevated)
  - *Predictive Power*: 2-8 weeks leading indicator for market corrections

#### **Volatility Structure Indicators**
- **Near-term Stress Ratio** (VIX9D/VIX): Immediate volatility structure analysis
  - *Weight*: 20% (critical for regime change detection)  
  - *Predictive Power*: 3-10 days leading indicator for volatility regime shifts

- **3-Month Term Slope** (VIX/VIX3M): Medium-term volatility expectations
  - *Weight*: 15% (important for trend identification)
  - *Predictive Power*: 2-6 weeks leading indicator for sustained stress periods

- **6-Month Term Slope** (VIX/VIX6M): Long-term volatility structure
  - *Weight*: 10% (structural volatility assessment)
  - *Predictive Power*: 1-3 months leading indicator for regime changes

### **Dynamic Weighting System**

Unlike traditional static weighting, Euler's **statistical dynamic weighting** system:

1. **Adapts to Market Regime**: Structural indicators get higher weight during euphoria; sentiment indicators dominate during stress
2. **Risk-Based Allocation**: Higher risk scores automatically receive higher weights
3. **Correlation Intelligence**: Reduces weights when indicators provide redundant information
4. **Auto-Discovery**: New indicators are automatically profiled and weighted appropriately
5. **Historical Validation**: Weights based on correlation with actual market crashes (2008, 2020, etc.)

**Example Weight Adaptation**:
- **Euphoria Period**: Buffett Indicator 45%, SKEW 22%, Put/Call 11%
- **Stress Period**: Put/Call 21%, Near-term Stress 20%, Buffett 30%

## Implementation Guidelines

### **Auto-Discovery Risk Scoring Architecture**

#### **1. Modular Provider System (Val Pattern)**
- Each risk metric can have multiple data providers
- Exactly one active provider per metric at runtime  
- Swappable adapters without touching core logic
- New indicators automatically discovered from registry

#### **2. Statistical Dynamic Weighting**
```python
# Automatic weight calculation based on:
base_weight = (
    crash_correlation * 0.3 +        # Historical crash prediction ability
    information_uniqueness * 0.3 +   # Non-redundant information content  
    signal_quality * 0.2 +           # Signal-to-noise ratio
    data_reliability * 0.2           # Consistency and data points
) * regime_multiplier * quality_adjustment
```

#### **3. Regime-Adaptive Processing**
- **Euphoria (0-25)**: Structural indicators prioritized (bubble detection)
- **Normal (25-60)**: Balanced weighting across all categories
- **Stress (60-85)**: Sentiment and positioning indicators emphasized  
- **Crisis (85-100)**: Near-term volatility structure dominates

#### **4. Auto-Discovery Process**
1. **Detection**: System scans registry for new indicators
2. **Classification**: Auto-categorizes by name and behavior patterns
3. **Profiling**: Builds statistical profile over time
4. **Weighting**: Assigns weights based on risk characteristics
5. **Correlation**: Learns relationships with existing indicators
6. **Adaptation**: Adjusts weights based on predictive performance

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

## Usage Notes & Best Practices

### **System Purpose**
- **Primary Use**: Early warning system for dangerous market conditions
- **Focus**: Structural overvaluation and stress signal detection
- **Timeframe**: Leading indicator system (days to months ahead of major moves)
- **Not For**: Day trading signals or short-term market timing

### **Interpretation Guidelines**
- **Score 0-25**: Dangerous euphoria - structural risks building despite low volatility
- **Score 25-60**: Normal conditions - balanced risk assessment
- **Score 60-85**: Elevated risk - multiple warning signals activated
- **Score 85-100**: Crisis conditions - imminent danger signals

### **System Features**
- **Auto-Discovery**: New indicators automatically integrated and weighted
- **Dynamic Weighting**: Risk-based weight allocation adapts to market conditions
- **Regime Intelligence**: System knows which indicators matter most in each market phase
- **Statistical Foundation**: Weights based on historical crash correlation analysis
- **Multiple Execution Modes**: GUI, headless, broadcast, single-run options

### **Adding New Indicators**
1. Create indicator class in `indicators/risk_indicators/`
2. Add to registry in `registries/indicator_registry.py`
3. System automatically discovers, profiles, and weights the new indicator
4. Higher risk scores automatically receive higher weights
5. No manual configuration required

### **Adding New Weighting Strategies**

Creating new weighting strategies is straightforward with Euler's modular architecture. Follow these steps:

#### **Step 1: Create Strategy File**

Create a new file in `weight_strategies/my_custom_strategy.py`:

```python
"""
My Custom Strategy.

Brief description of what this strategy does and when to use it.
"""

from typing import Dict
from .base_strategy import BaseWeightStrategy


class MyCustomStrategy(BaseWeightStrategy):
    """Detailed description of the strategy's approach and methodology."""
    
    def __init__(self):
        super().__init__()
        # Initialize any strategy-specific parameters here
        self.parameter1 = 0.5
        self.parameter2 = {"setting": "value"}
    
    def calculate_weights(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate weights based on your custom logic.
        
        Args:
            current_scores: Dict of indicator names to risk scores (0-100)
            
        Returns:
            Dict of indicator names to weights (must sum to 1.0)
        """
        if not current_scores:
            return {}
        
        # Your custom weighting logic here
        weights = {}
        
        for indicator, score in current_scores.items():
            # Example: Weight based on some custom formula
            if "Buffett" in indicator:
                weights[indicator] = score * 0.01 * self.parameter1
            elif "SKEW" in indicator:
                weights[indicator] = (score ** 1.5) * 0.005
            else:
                weights[indicator] = score * 0.008
        
        # Normalize weights to sum to 1.0 (required)
        weights = self._normalize_weights(weights)
        
        # Validate weights (recommended)
        self._validate_weights(weights)
        
        return weights
    
    def get_name(self) -> str:
        return "My Custom Strategy"
    
    def get_description(self) -> str:
        return (
            "Detailed description of how this strategy works, what market conditions "
            "it's designed for, and what makes it unique. Include the mathematical "
            "approach, key assumptions, and recommended use cases."
        )
    
    def get_category(self) -> str:
        return "Dynamic"  # Options: "Static", "Dynamic", "Adaptive"
    
    def get_complexity(self) -> str:
        return "Moderate"  # Options: "Simple", "Moderate", "Advanced"
```

#### **Step 2: Register Strategy**

Add your strategy to the system in `registries/weight_registry.py`:

```python
# 1. Import your strategy (add to imports section)
from weight_strategies import (
    # ... existing imports ...
    MyCustomStrategy  # Add this line
)

# 2. Add to WeightingMethod enum
class WeightingMethod(Enum):
    # ... existing methods ...
    MY_CUSTOM = "my_custom"  # Add this line

# 3. Add to registry initialization
class WeightRegistry:
    def __init__(self):
        self._strategies = {
            # ... existing strategies ...
            WeightingMethod.MY_CUSTOM: MyCustomStrategy(),  # Add this line
        }

# 4. Add to string mapping (in configure_weighting_from_string function)
method_map = {
    # ... existing mappings ...
    "my_custom": WeightingMethod.MY_CUSTOM,  # Add this line
    "custom": WeightingMethod.MY_CUSTOM,     # Optional: add aliases
}
```

#### **Step 3: Update Package Imports**

Add your strategy to `weight_strategies/__init__.py`:

```python
from .my_custom_strategy import MyCustomStrategy

__all__ = [
    # ... existing exports ...
    'MyCustomStrategy',  # Add this line
]
```

#### **Step 4: Use Your Strategy**

**Option A: Set as Default**
```python
# In registries/weight_registry.py
DEFAULT_WEIGHTING_METHOD = WeightingMethod.MY_CUSTOM
```

**Option B: Switch Programmatically**
```python
from registries.weight_registry import set_weighting_method, WeightingMethod
set_weighting_method(WeightingMethod.MY_CUSTOM)
```

**Option C: Test Your Strategy**
```python
from weight_strategies import MyCustomStrategy

# Test with sample data
strategy = MyCustomStrategy()
sample_scores = {
    'Buffett Indicator': 85,
    'Put/Call Ratio': 70,
    '^SKEW': 65
}

weights = strategy.calculate_weights(sample_scores)
print(f"Strategy: {strategy.get_name()}")
print(f"Weights: {weights}")
print(f"Sum: {sum(weights.values()):.3f}")  # Should be 1.000
```

#### **Strategy Development Best Practices**

1. **Weight Validation**: Always call `self._validate_weights(weights)` to ensure weights sum to 1.0

2. **Normalization**: Use `self._normalize_weights(weights)` to automatically normalize weights

3. **Fallback Handling**: Use `self._equal_weights_fallback(current_scores)` for error conditions

4. **Documentation**: Provide clear descriptions of when and why to use your strategy

5. **Categories**:
   - **Static**: Weights don't change based on current scores
   - **Dynamic**: Weights adapt to current market conditions
   - **Adaptive**: Advanced strategies that change behavior based on market regime

6. **Complexity Levels**:
   - **Simple**: Easy to understand, few parameters
   - **Moderate**: Some complexity, multiple factors considered
   - **Advanced**: Sophisticated algorithms, multiple techniques combined

#### **Testing Your Strategy**

Create a test script to validate your strategy:

```python
#!/usr/bin/env python3
"""Test script for custom weighting strategy."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from weight_strategies import MyCustomStrategy

def test_strategy():
    strategy = MyCustomStrategy()
    
    # Test with various market conditions
    test_cases = [
        {"name": "High Risk", "scores": {"Buffett Indicator": 95, "^SKEW": 85, "Put/Call Ratio": 75}},
        {"name": "Low Risk", "scores": {"Buffett Indicator": 25, "^SKEW": 30, "Put/Call Ratio": 35}},
        {"name": "Mixed Risk", "scores": {"Buffett Indicator": 80, "^SKEW": 40, "Put/Call Ratio": 60}},
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']} Scenario:")
        weights = strategy.calculate_weights(test_case['scores'])
        
        for indicator, weight in weights.items():
            score = test_case['scores'][indicator]
            print(f"  {indicator}: {weight:.1%} (Score: {score})")
        
        print(f"  Total Weight: {sum(weights.values()):.3f}")
        
        # Calculate weighted score
        weighted_score = sum(score * weight for score, weight in zip(test_case['scores'].values(), weights.values()))
        print(f"  Weighted Score: {weighted_score:.1f}")

if __name__ == "__main__":
    test_strategy()
```

#### **Advanced Strategy Examples**

**Time-Based Strategy**: Weights change based on time of day/week
**Volatility Regime Strategy**: Weights adapt to VIX levels
**Correlation-Aware Strategy**: Reduces weights of highly correlated indicators
**Machine Learning Strategy**: Uses trained models for weight allocation
**Multi-Timeframe Strategy**: Considers multiple time horizons

### **Technical Notes**
- GUI updates every 60 seconds in continuous mode
- System follows Val repository's modular architecture patterns
- Cross-correlation analysis prevents indicator redundancy
- Fallback mechanisms ensure robust operation

## Quick Start Guide

### **1. Basic Setup**
```bash
git clone https://github.com/AmpyFin/Euler.git
cd Euler
pip install -r requirements.txt
python3 -c "import yfinance; import PyQt5; print('✅ Setup complete!')"
```

### **2. Choose Your Weighting Strategy**
Edit `registries/weight_registry.py`:
```python
# For beginners - simple and interpretable
DEFAULT_WEIGHTING_METHOD = WeightingMethod.LINEAR_STATIC

# For crisis detection - emphasizes high-risk signals  
DEFAULT_WEIGHTING_METHOD = WeightingMethod.RISK_PROPORTIONAL

# For production - sophisticated auto-discovery (recommended)
DEFAULT_WEIGHTING_METHOD = WeightingMethod.STATISTICAL_DYNAMIC

# For advanced users - heuristic meta-strategy
DEFAULT_WEIGHTING_METHOD = WeightingMethod.ADAPTIVE_ENSEMBLE

# For maximum sophistication - ML ensemble methods
DEFAULT_WEIGHTING_METHOD = WeightingMethod.ML_ADAPTIVE_STACKING   # Best overall
DEFAULT_WEIGHTING_METHOD = WeightingMethod.ML_ADAPTIVE_VOTING     # Most robust
DEFAULT_WEIGHTING_METHOD = WeightingMethod.ML_ADAPTIVE_BLENDING   # Custom learning
```

### **3. Configure System Behavior**
Edit `control.py`:
```python
# For development/testing
GUI_mode = True
run_continuously = False

# For production monitoring  
GUI_mode = True
run_continuously = True

# For automation/scripting
GUI_mode = False
run_continuously = False
```

### **4. Run the System**
```bash
python3 clients/system_client.py
```

### **5. Monitor & Validate**
```bash
# Health check
python3 -c "from registries.weight_registry import get_strategy_summary; print(get_strategy_summary())"

# Test all strategies
python3 -c "from registries.weight_registry import WeightingMethod; [print(f'✅ {m.value}') for m in WeightingMethod]"

# Performance check
python3 -c "import time; start=time.time(); from clients.system_client import SystemClient; print(f'Load time: {time.time()-start:.2f}s')"
```

## Summary

**Euler** is now a **comprehensive, modular market risk assessment system** with:

- **🎯 7 Weighting Strategies**: From simple equal weighting to sophisticated adaptive ensemble methods
- **📊 6 Predictive Risk Indicators**: Structural overvaluation, sentiment, volatility, and yield curve analysis  
- **⚙️ Flexible Configuration**: Easy switching between strategies and operational modes
- **🔧 Extensible Architecture**: Simple addition of new strategies and indicators
- **📈 Production Ready**: Robust error handling, fallbacks, and comprehensive documentation

**Choose your strategy based on your needs:**
- **Research/Baseline**: Equal Weight
- **Conservative Analysis**: Linear Static  
- **Crisis Detection**: Risk Proportional or Momentum Based
- **Noise Reduction**: Volatility Adjusted
- **Production System**: Statistical Dynamic or Adaptive Ensemble

The system provides **early warning of market stress conditions** through sophisticated risk indicator analysis, helping identify dangerous market conditions before they become crises.