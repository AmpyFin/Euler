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

        with pytest.raises(ValueError, match="No price data available"):
            adapter.fetch_last_quote("^VIX")

    @patch("adapters.yfinance_adapter.yf")
    def test_fetch_last_quote_with_date_success(self, mock_yf, adapter):
        """Test successful quote fetching with date."""
        mock_ticker = Mock()
        mock_ticker.info = {"regularMarketPrice": 25.5}
        mock_yf.Ticker.return_value = mock_ticker

        price, date = adapter.fetch_last_quote_with_date("^VIX")

        assert price == 25.5
        assert isinstance(date, datetime)

    @patch("adapters.yfinance_adapter.yf")
    def test_fetch_historical_data_success(self, mock_yf, adapter):
        """Test successful historical data fetching."""
        mock_ticker = Mock()
        mock_data = Mock()
        mock_data.to_dict.return_value = {"Close": {datetime.now(): 25.5, datetime.now(): 26.0}}
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

    @patch("adapters.buffet_indicator_adapter.yf")
    def test_fetch_last_quote_success(self, mock_yf, adapter):
        """Test successful Buffett indicator calculation."""
        # Mock GDP data
        mock_gdp_ticker = Mock()
        mock_gdp_ticker.info = {"regularMarketPrice": 25000.0}  # GDP in billions

        # Mock market cap data
        mock_market_ticker = Mock()
        mock_market_ticker.info = {"marketCap": 50000000000000}  # 50 trillion

        mock_yf.Ticker.side_effect = [mock_gdp_ticker, mock_market_ticker]

        result = adapter.fetch_last_quote()

        # Expected: 50 trillion / 25 trillion = 200%
        expected = 200.0
        assert abs(result - expected) < 0.1

    @patch("adapters.buffet_indicator_adapter.yf")
    def test_fetch_last_quote_missing_data(self, mock_yf, adapter):
        """Test Buffett indicator with missing data."""
        mock_ticker = Mock()
        mock_ticker.info = {}
        mock_yf.Ticker.return_value = mock_ticker

        with pytest.raises(ValueError, match="Missing required data"):
            adapter.fetch_last_quote()

    @patch("adapters.buffet_indicator_adapter.yf")
    def test_fetch_historical_data(self, mock_yf, adapter):
        """Test historical data fetching for Buffett indicator."""
        mock_ticker = Mock()
        mock_data = Mock()
        mock_data.to_dict.return_value = {"Close": {datetime.now(): 200.0, datetime.now(): 180.0}}
        mock_ticker.history.return_value = mock_data
        mock_yf.Ticker.return_value = mock_ticker

        result = adapter.fetch_historical_data(days=30)

        assert isinstance(result, dict)
        assert len(result) > 0

    def test_calculate_buffett_ratio(self, adapter):
        """Test the Buffett ratio calculation logic."""
        # Test normal case
        result = adapter._calculate_buffett_ratio(50000000000000, 25000.0)
        assert result == 200.0

        # Test edge case with zero GDP
        with pytest.raises(ValueError, match="GDP cannot be zero"):
            adapter._calculate_buffett_ratio(50000000000000, 0)

        # Test edge case with negative values
        with pytest.raises(ValueError, match="Values must be positive"):
            adapter._calculate_buffett_ratio(-1000, 25000.0)
