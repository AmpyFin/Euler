"""
6-Month Term Slope (^VIX/^VIX6M) Indicator implementation.
"""

from ..indicator import Indicator


class SixMonthTermSlopeIndicator(Indicator):
    """
    6-month term slope indicator for tracking long-term market stress through VIX term structure.
    """

    def get_name(self) -> str:
        return "6M Term Slope"

    def fetch_last_quote(self) -> float:
        """
        Calculates the current 6-month term slope (^VIX/^VIX6M).

        Returns:
            float: The current ratio value

        Raises:
            ValueError: If the component values cannot be fetched
        """
        # Get both VIX values
        vix = self.adapter.fetch_last_quote("^VIX")
        vix6m = self.adapter.fetch_last_quote("^VIX6M")

        # Calculate ratio
        if vix6m == 0:
            raise ValueError("VIX6M value is zero - cannot calculate ratio")

        return vix / vix6m
