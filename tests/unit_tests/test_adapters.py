"""
Unit tests for adapter classes.
"""

from datetime import datetime
from typing import Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from adapters.adapter import Adapter
from adapters.buffet_indicator_adapter import BuffettIndicatorAdapter
from adapters.yfinance_adapter import YFinanceAdapter


class TestAdapter:
    """Test the base Adapter class."""

    def test_adapter_is_abstract(self):
        """Test that Adapter is an abstract base class."""
        with pytest.raises(TypeError):
            Adapter()


class TestYFinanceAdapter:
    """Test the YFinanceAdapter class."""

    @pytest.fixture
    def adapter(self):
        """Create a YFinanceAdapter instance for testing."""
        return YFinanceAdapter()

    @patch("adapters.yfinance_adapter.yf")
    def test_fetch_last_quote_success(self, mock_yf, adapter):
        """Test successful quote fetching."""
        # Mock the yfinance response
        mock_ticker = Mock()
        mock_ticker.info = {"regularMarketPrice": 25.5}
        mock_yf.Ticker.return_value = mock_ticker

        result = adapter.fetch_last_quote("^VIX")

        assert result == 25.5
        mock_yf.Ticker.assert_called_once_with("^VIX")

    @patch("adapters.yfinance_adapter.yf")
    def test_fetch_last_quote_no_price(self, mock_yf, adapter):
        """Test quote fetching when no price is available."""
        mock_ticker = Mock()
        mock_ticker.info = {}
        mock_yf.Ticker.return_value = mock_ticker

        with pytest.raises(ValueError, match="Could not find latest quote for"):
            adapter.fetch_last_quote("^VIX")

    @patch("adapters.yfinance_adapter.yf")
    def test_fetch_last_quote_with_date_success(self, mock_yf, adapter):
        """Test successful quote fetching with date."""
        mock_ticker = Mock()
        mock_df = MagicMock()
        mock_df.empty = False
        mock_df.iloc.__getitem__.return_value = {"Close": 25.5}
        mock_ticker.history.return_value = mock_df
        mock_yf.Ticker.return_value = mock_ticker

        price, date = adapter.fetch_last_quote_with_date("^VIX", date=datetime.now())

        assert price == 25.5
        assert isinstance(date, datetime)

    @patch("adapters.yfinance_adapter.yf")
    def test_fetch_historical_data_success(self, mock_yf, adapter):
        """Test successful historical data fetching."""
        mock_ticker = Mock()

        # Create a mock DataFrame for the history data
        mock_data = MagicMock()
        mock_data.empty = False

        # Create a dictionary to simulate the data
        hist_data = {datetime(2023, 1, 1): 25.5, datetime(2023, 1, 2): 26.0}

        # Mock the 'Close' series and its items() method
        mock_series = Mock()
        mock_series.items.return_value = hist_data.items()
        mock_data.__getitem__.return_value = mock_series

        mock_ticker.history.return_value = mock_data
        mock_yf.Ticker.return_value = mock_ticker

        result = adapter.fetch_historical_data("^VIX", days=30)

        assert isinstance(result, dict)
        assert len(result) > 0
        mock_ticker.history.assert_called_once()

    @patch("adapters.yfinance_adapter.yf")
    def test_fetch_last_quote_exception_handling(self, mock_yf, adapter):
        """Test exception handling in quote fetching."""
        mock_yf.Ticker.side_effect = Exception("Network error")

        with pytest.raises(ValueError, match="Failed to fetch quote"):
            adapter.fetch_last_quote("^VIX")


class TestBuffettIndicatorAdapter:
    """Test the BuffettIndicatorAdapter class."""

    @pytest.fixture
    def adapter(self):
        """Create a BuffettIndicatorAdapter instance for testing."""
        return BuffettIndicatorAdapter()

    @patch("adapters.buffet_indicator_adapter.requests.get")
    def test_fetch_last_quote_success(self, mock_get, adapter):
        """Test successful Buffett indicator calculation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><script>let autoRatio = 150.0;</script></body></html>"
        mock_get.return_value = mock_response

        result = adapter.fetch_last_quote()

        assert result == 150.0

    @patch("adapters.buffet_indicator_adapter.requests.get")
    def test_fetch_last_quote_missing_data(self, mock_get, adapter):
        """Test Buffett indicator with missing data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body></body></html>"
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Could not find Buffett Indicator value in webpage"):
            adapter.fetch_last_quote()

    def test_fetch_historical_data(self, adapter):
        """Test historical data fetching for Buffett indicator."""
        with pytest.raises(NotImplementedError):
            adapter.fetch_historical_data(days=30)
