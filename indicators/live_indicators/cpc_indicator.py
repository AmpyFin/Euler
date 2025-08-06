"""
Put/Call Ratio Indicator implementation.
Calculates put-call ratio from SPY options volume for nearest expirations.
"""

from typing import Dict, List, Tuple
import yfinance as yf
import pandas as pd
from ..indicator import Indicator


class CPCIndicator(Indicator):
    """
    CBOE Put/Call ratio proxy calculated from SPY options activity.
    Uses volume from nearest expiration dates to gauge market sentiment.
    """

    def __init__(self, adapter, nearest_n: int = 2):
        """
        Initialize with number of nearest expirations to use.

        Args:
            adapter: The data adapter (not used in this implementation)
            nearest_n: Number of nearest expiration dates to include
        """
        super().__init__(adapter)
        self.nearest_n = nearest_n

    def get_name(self) -> str:
        return "Put/Call Ratio"

    def _get_option_volumes(self) -> Tuple[List[float], List[float], List[str]]:
        """
        Get put and call volumes for nearest expirations.

        Returns:
            Tuple of (put volumes, call volumes, expiration dates)
        """
        spy = yf.Ticker("SPY")
        exps = spy.options[: self.nearest_n]  # grab nearest expirations

        puts, calls = [], []
        for exp in exps:
            chain = spy.option_chain(exp)
            puts.append(chain.puts[["volume"]].sum().values[0])
            calls.append(chain.calls[["volume"]].sum().values[0])

        return puts, calls, exps

    def fetch_last_quote(self) -> float:
        """
        Calculates current Put/Call ratio from SPY options volume.
        Uses the nearest expiration dates for a more reactive signal.

        Returns:
            float: The current Put/Call ratio

        Raises:
            ValueError: If the ratio cannot be calculated
        """
        try:
            puts, calls, _ = self._get_option_volumes()

            total_puts = float(pd.Series(puts).sum())
            total_calls = float(pd.Series(calls).sum())

            # Avoid division by zero
            return total_puts / max(total_calls, 1.0)

        except Exception as e:
            raise ValueError(f"Failed to calculate put-call ratio: {str(e)}")

    def fetch_detail(self) -> Dict[str, float]:
        """
        Fetches detailed put-call data including per-expiration ratios.

        Returns:
            Dict containing:
            - total_ratio: overall P/C ratio
            - put_volume: total put volume
            - call_volume: total call volume
            - expirations: dict of expiration date -> P/C ratio

        Raises:
            ValueError: If the data cannot be fetched
        """
        try:
            puts, calls, exps = self._get_option_volumes()

            # Calculate total volumes
            total_puts = float(pd.Series(puts).sum())
            total_calls = float(pd.Series(calls).sum())

            # Calculate per-expiration ratios
            exp_ratios = {}
            for i, exp in enumerate(exps):
                exp_ratios[exp] = puts[i] / max(calls[i], 1.0)

            return {
                "total_ratio": total_puts / max(total_calls, 1.0),
                "put_volume": total_puts,
                "call_volume": total_calls,
                "expirations": exp_ratios,
            }

        except Exception as e:
            raise ValueError(f"Failed to fetch detailed put-call data: {str(e)}")

    def get_description(self) -> str:
        """Returns a description of how this indicator is calculated."""
        return f"""Put/Call Ratio (SPY Options)
        - Calculated from SPY options volume
        - Uses {self.nearest_n} nearest expiration dates
        - Higher values indicate more defensive positioning
        - Typical ranges: <0.5 bullish, >1.0 bearish
        """
