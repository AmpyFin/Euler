"""
VIX 9-Day (^VIX9D) Indicator implementation.
"""

from ..indicator import Indicator


class VIX9DIndicator(Indicator):
    """
    9-day VIX indicator for tracking near-term implied volatility.
    """

    def get_name(self) -> str:
        return "^VIX9D"

    def fetch_last_quote(self) -> float:
        """
        Fetches the current 9-day VIX value.

        Returns:
            float: The current 9-day VIX level

        Raises:
            ValueError: If the value cannot be fetched
        """
        return self.adapter.fetch_last_quote("^VIX9D")
