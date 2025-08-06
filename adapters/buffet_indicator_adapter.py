"""
Adapter for fetching Buffett Indicator data.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
import requests
from bs4 import BeautifulSoup
import re

from .adapter import Adapter


class BuffettIndicatorAdapter(Adapter):
    """Adapter for fetching Buffett Indicator (Market Cap / GDP) data."""

    def __init__(self):
        """Initialize the adapter."""
        self.url = "https://buffettindicator.net/"

    def fetch_last_quote(self, index: Optional[str] = None) -> float:
        """
        Fetch the latest Buffett Indicator value by web scraping buffettindicator.net.

        Returns:
            float: The latest Buffett Indicator value (Market Cap / GDP * 100)

        Raises:
            ValueError: If the data cannot be fetched or is invalid
        """
        try:
            # Fetch the webpage content
            response = requests.get(self.url)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Parse the HTML content
            soup = BeautifulSoup(response.text, "html.parser")

            # Look for the text containing the ratio
            target_text = "Based on today's updated data, the Market Cap to GDP Ratio is"
            for text in soup.stripped_strings:
                if target_text in text:
                    # Extract the number that follows the text
                    match = re.search(rf"{target_text}\s*([\d.]+)", text)
                    if match:
                        return float(match.group(1))

            # If we didn't find it in the text, try looking in script tags for autoRatio
            script_tags = soup.find_all("script")
            for script in script_tags:
                if script.string and "autoRatio" in script.string:
                    match = re.search(r"let autoRatio = ([\d.]+);", script.string)
                    if match:
                        return float(match.group(1))

            raise ValueError("Could not find Buffett Indicator value in webpage")

        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch webpage: {str(e)}")
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Failed to parse Buffett Indicator value: {str(e)}")

    def fetch_last_quote_with_date(self, index: Optional[str] = None) -> Tuple[float, datetime]:
        """
        Fetch the latest Buffett Indicator value with timestamp.

        Returns:
            Tuple[float, datetime]: The indicator value and timestamp

        Raises:
            ValueError: If the data cannot be fetched or is invalid
        """
        try:
            value = self.fetch_last_quote()
            return value, datetime.now()
        except Exception as e:
            raise ValueError(f"Failed to fetch Buffett Indicator with date: {str(e)}")

    def fetch_historical_data(self, index: Optional[str] = None, days: int = 30) -> Dict[datetime, float]:
        """
        Fetch historical Buffett Indicator data.

        Args:
            days (int): Number of days of historical data to fetch

        Returns:
            Dict[datetime, float]: Historical data as date-value pairs

        Raises:
            ValueError: If the data cannot be fetched or is invalid
            NotImplementedError: Historical data is not available via web scraping
        """
        raise NotImplementedError("Historical data fetching for Buffett Indicator via web scraping is not implemented.")
