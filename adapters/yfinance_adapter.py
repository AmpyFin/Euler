"""
YFinance adapter for fetching real-time market data.
"""

import yfinance as yf
from datetime import datetime
from typing import Optional, Tuple, Dict

from .adapter import Adapter


class YFinanceAdapter(Adapter):
    """
    Adapter for fetching market data using the Yahoo Finance API.
    This adapter requires an index parameter to specify which symbol to fetch.
    """

    def fetch_last_quote(self, index: str) -> float:
        """
        Fetches the latest quote for the specified index/symbol.

        Args:
            index (str): The index symbol to fetch (e.g. "^VIX", "^GSPC")

        Returns:
            float: The latest quote value

        Raises:
            ValueError: If the quote cannot be fetched or is invalid
        """
        if not index:
            raise ValueError("Index symbol is required for YFinance adapter")

        try:
            # Create Ticker object
            ticker = yf.Ticker(index)

            # Get the latest quote
            info = ticker.info
            if "regularMarketPrice" not in info:
                raise ValueError(f"Could not find latest quote for {index}")

            return float(info["regularMarketPrice"])

        except Exception as e:
            raise ValueError(f"Failed to fetch quote for {index}: {str(e)}")

    def fetch_last_quote_with_date(self, index: str = None, date: datetime = None) -> Tuple[float, datetime]:
        """
        Fetches the latest quote for a given index and returns the date of the quote.

        Args:
            index (str): The index symbol to fetch
            date (datetime): The date to fetch data for

        Returns:
            Tuple[float, datetime]: The quote value and timestamp

        Raises:
            ValueError: If the data cannot be fetched or is invalid
        """
        if not index:
            raise ValueError("Index symbol is required for YFinance adapter")

        if not date:
            raise ValueError("Date is required for YFinance adapter")

        try:
            ticker = yf.Ticker(index)
            history = ticker.history(start=date, end=date)
            if history.empty:
                raise ValueError(f"No data found for {index} on {date}")

            return float(history.iloc[0]["Close"]), date

        except Exception as e:
            raise ValueError(f"Failed to fetch quote for {index} on {date}: {str(e)}")

    def fetch_historical_data(self, index: str = None, days: int = 30) -> Dict[datetime, float]:
        """
        Fetches historical data for the given index.

        Args:
            index (str): The index symbol to fetch
            days (int): Number of days of historical data to fetch

        Returns:
            Dict[datetime, float]: Historical data as date-value pairs

        Raises:
            ValueError: If the data cannot be fetched or is invalid
        """
        if not index:
            raise ValueError("Index symbol is required for YFinance adapter")

        try:
            ticker = yf.Ticker(index)
            data = ticker.history(period=f"{days}d")
            if data.empty:
                raise ValueError(f"No historical data available for index {index}")
            return {date.to_pydatetime(): float(close) for date, close in data["Close"].items()}

        except Exception as e:
            raise ValueError(f"Failed to fetch historical data for {index}: {str(e)}")
