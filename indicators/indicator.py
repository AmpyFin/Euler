"""
Base indicator interface that all indicators must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional

from adapters.adapter import Adapter


class Indicator(ABC):
    """
    Abstract base class for all indicators.
    Each indicator must implement get_name() and fetch_last_quote().
    """

    def __init__(self, adapter: Adapter):
        """
        Initialize the indicator with its data adapter.

        Args:
            adapter: The data adapter instance to use for fetching quotes
        """
        self.adapter = adapter

    @abstractmethod
    def get_name(self) -> str:
        """
        Get the indicator's name.

        Returns:
            str: The indicator name
        """
        pass

    @abstractmethod
    def fetch_last_quote(self) -> float:
        """
        Fetch the latest value for this indicator.

        Returns:
            float: The latest indicator value

        Raises:
            ValueError: If the value cannot be fetched or is invalid
        """
        pass
