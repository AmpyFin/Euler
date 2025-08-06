"""
Base adapter interface responsible for standardizing API requests and data formatting.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Optional, Tuple


class Adapter(ABC):
    """
    Abstract base class for data adapters.
    All adapters must implement the fetch_last_quote method.
    """

    @abstractmethod
    def fetch_last_quote(self, index: str) -> float:
        """
        Fetches the latest quote for a given index.

        Args:
            index (str): The index symbol to fetch. May be None for adapters that don't require an index.

        Returns:
            float: The latest quote value

        Raises:
            ValueError: If the quote cannot be fetched or is invalid
        """
        pass

    @abstractmethod
    def fetch_last_quote_with_date(self, index: str = None, date: datetime = None) -> Tuple[float, datetime]:
        """
        Fetches the latest quote for a given index and returns the date of the quote.
        """
        pass

    @abstractmethod
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
        pass
