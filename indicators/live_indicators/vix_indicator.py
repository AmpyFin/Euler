"""
VIX (^VIX) Indicator implementation.
"""

from ..indicator import Indicator


class VIXIndicator(Indicator):
    """
    Standard 30-day VIX indicator for tracking market volatility.
    """

    def get_name(self) -> str:
        return "^VIX"

    def fetch_last_quote(self) -> float:
        """
        Fetches the current VIX value.

        Returns:
            float: The current VIX level

        Raises:
            ValueError: If the value cannot be fetched
        """
        return self.adapter.fetch_last_quote("^VIX")
