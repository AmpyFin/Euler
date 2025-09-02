"""
E2E test to verify all live indicators can fetch quotes and names correctly.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple

from adapters.buffet_indicator_adapter import BuffettIndicatorAdapter

# Import adapters
from adapters.yfinance_adapter import YFinanceAdapter
from indicators.risk_indicators.buffett_indicator import BuffettIndicator
from indicators.risk_indicators.cpc_indicator import CPCIndicator
from indicators.risk_indicators.near_term_stress_ratio_indicator import NearTermStressRatioIndicator
from indicators.risk_indicators.six_month_term_slope_indicator import SixMonthTermSlopeIndicator
from indicators.risk_indicators.skew_indicator import SKEWIndicator
from indicators.risk_indicators.three_month_term_slope_indicator import ThreeMonthTermSlopeIndicator


@dataclass
class TestResult:
    indicator_name: str
    name_test_passed: bool
    quote_test_passed: bool
    error_message: str = ""
    quote_value: float = 0.0


def run_indicator_test(indicator_instance) -> TestResult:
    """Run tests for a single indicator."""
    result = TestResult(indicator_name="Unknown", name_test_passed=False, quote_test_passed=False)

    try:
        # Test get_name()
        name = indicator_instance.get_name()
        result.indicator_name = name
        result.name_test_passed = True

        # Test fetch_last_quote()
        quote = indicator_instance.fetch_last_quote()
        result.quote_test_passed = True
        result.quote_value = quote

    except Exception as e:
        result.error_message = str(e)

    return result


def print_test_report(results: List[TestResult]):
    """Print formatted test results."""
    print("\n" + "=" * 80)
    print(f"EULER SYSTEM E2E TEST REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Summary statistics
    total_tests = len(results) * 2  # name and quote test for each indicator
    passed_tests = sum([(r.name_test_passed + r.quote_test_passed) for r in results])

    print(f"\nOverall Status: {passed_tests}/{total_tests} tests passed")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%\n")

    # Detailed results
    print("Detailed Results:")
    print("-" * 80)
    print(f"{'Indicator':<30} {'Name Test':<15} {'Quote Test':<15} {'Value':<15}")
    print("-" * 80)

    for result in results:
        name_status = "✓" if result.name_test_passed else "✗"
        quote_status = "✓" if result.quote_test_passed else "✗"
        value = f"{result.quote_value:.2f}" if result.quote_test_passed else "N/A"

        print(f"{result.indicator_name:<30} {name_status:<15} {quote_status:<15} {value:<15}")

        if result.error_message:
            print(f"  Error: {result.error_message}")

    print("\n" + "=" * 80)


def main():
    """Main test execution."""
    # Initialize adapters
    yfinance_adapter = YFinanceAdapter()
    buffett_adapter = BuffettIndicatorAdapter()

    # Create risk indicator instances (predictive indicators only)
    indicators = [
        SKEWIndicator(yfinance_adapter),
        CPCIndicator(yfinance_adapter),
        NearTermStressRatioIndicator(yfinance_adapter),
        ThreeMonthTermSlopeIndicator(yfinance_adapter),
        SixMonthTermSlopeIndicator(yfinance_adapter),
        BuffettIndicator(buffett_adapter),
    ]

    # Run tests
    results = [run_indicator_test(indicator) for indicator in indicators]

    # Print report
    print_test_report(results)

    # Return success if all tests passed
    all_passed = all(r.name_test_passed and r.quote_test_passed for r in results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
