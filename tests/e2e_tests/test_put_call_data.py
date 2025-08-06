"""
Test script to verify put-call ratio data access.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

import yfinance as yf
import pandas as pd


def main():
    """Test put-call ratio data access."""
    print("Testing put-call ratio data access...")

    # Try downloading all three ratios
    print("\nDownloading 5 days of data for all ratios:")
    df = yf.download(["^CPC", "^CPCE", "^CPCI"], period="5d", interval="1d")["Close"]
    print(df)

    # Try individual downloads
    print("\nTesting individual downloads:")

    print("\nTotal put/call (^CPC):")
    cpc = yf.download("^CPC", period="5d", interval="1d")["Close"]
    print(cpc)

    print("\nEquity-only put/call (^CPCE):")
    cpce = yf.download("^CPCE", period="5d", interval="1d")["Close"]
    print(cpce)

    print("\nIndex-only put/call (^CPCI):")
    cpci = yf.download("^CPCI", period="5d", interval="1d")["Close"]
    print(cpci)


if __name__ == "__main__":
    main()
