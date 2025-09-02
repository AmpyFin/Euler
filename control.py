"""
Control Module - System Configuration Settings.

This module controls the operational behavior of the Euler market risk assessment system.
Configure these settings to control how the system runs and what features are enabled.

IMPORTANT: Weighting strategy configuration is now in registries/weight_registry.py
"""

# =============================================================================
# SYSTEM OPERATION SETTINGS
# =============================================================================

# GUI Configuration
GUI_mode = False          # True: Show GUI interface | False: Headless mode

# Runtime Configuration  
run_continuously = False  # True: Continuous monitoring | False: Single analysis run

# Network Broadcasting Configuration
broadcast_mode = False    # True: Broadcast results over network | False: Local only
broadcast_network = "127.0.0.1"  # Network address for broadcasting
broadcast_port = 5001     # UDP port for network broadcasting

# =============================================================================
# WEIGHTING STRATEGY CONFIGURATION
# =============================================================================

# WEIGHTING STRATEGIES ARE NOW CONFIGURED IN: registries/weight_registry.py
# 
# To change the active weighting strategy:
# 1. Open: registries/weight_registry.py
# 2. Find: DEFAULT_WEIGHTING_METHOD = WeightingMethod.STATISTICAL_DYNAMIC
# 3. Change to your preferred strategy:
#
# Available strategies:
# - WeightingMethod.EQUAL_WEIGHT          # Simple baseline (all indicators equal)
# - WeightingMethod.LINEAR_STATIC         # Expert judgment (fixed weights)
# - WeightingMethod.RISK_PROPORTIONAL     # Crisis-focused (high risk = high weight)
# - WeightingMethod.STATISTICAL_DYNAMIC   # Auto-discovery (default, most sophisticated)
# - WeightingMethod.VOLATILITY_ADJUSTED   # Noise reduction (stable indicators prioritized)
# - WeightingMethod.MOMENTUM_BASED        # Trend following (momentum-driven weights)
# - WeightingMethod.ADAPTIVE_ENSEMBLE     # Meta-strategy (combines multiple approaches)

# =============================================================================
# USAGE EXAMPLES
# =============================================================================

# Example 1: Basic GUI Mode
# GUI_mode = True
# run_continuously = True
# Result: Shows GUI with continuous market monitoring

# Example 2: Single Analysis Run
# GUI_mode = False  
# run_continuously = False
# Result: Performs one analysis and exits (good for automation)

# Example 3: Network Broadcasting
# broadcast_mode = True
# broadcast_network = "192.168.1.255"
# broadcast_port = 5001
# Result: Broadcasts analysis results to network clients

# =============================================================================
# QUICK START
# =============================================================================

# 1. For testing/development:
#    GUI_mode = True, run_continuously = False
#
# 2. For production monitoring:
#    GUI_mode = True, run_continuously = True
#
# 3. For automated analysis:
#    GUI_mode = False, run_continuously = False
#
# 4. For network integration:
#    broadcast_mode = True, configure network settings above
