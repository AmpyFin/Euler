"""
Unit tests for indicator classes.
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from indicators.indicator import Indicator
from indicators.live_indicators.buffett_indicator import BuffettIndicator
from indicators.live_indicators.cpc_indicator import CPCIndicator
from indicators.live_indicators.skew_indicator import SKEWIndicator
from indicators.live_indicators.vix_indicator import VIXIndicator


class TestIndicator:
    """Test the base Indicator class."""

    def test_indicator_is_abstract(self):
        """Test that Indicator is an abstract base class."""
        with pytest.raises(TypeError):
            Indicator(Mock())

    def test_indicator_initialization(self):
        """Test indicator initialization with adapter."""
        mock_adapter = Mock()

        # Create a concrete indicator class for testing
        class TestIndicator(Indicator):
            def get_name(self):
                return "Test"

            def fetch_last_quote(self):
                return 25.5

        indicator = TestIndicator(mock_adapter)
        assert indicator.adapter == mock_adapter


class TestVIXIndicator:
    """Test the VIXIndicator class."""

    @pytest.fixture
    def mock_adapter(self):
        """Create a mock adapter for VIX testing."""
        adapter = Mock()
        adapter.fetch_last_quote.return_value = 25.5
        return adapter

    @pytest.fixture
    def vix_indicator(self, mock_adapter):
        """Create a VIXIndicator instance for testing."""
        return VIXIndicator(mock_adapter)

    def test_get_name(self, vix_indicator):
        """Test VIX indicator name."""
        assert vix_indicator.get_name() == "^VIX"

    def test_fetch_last_quote_success(self, vix_indicator, mock_adapter):
        """Test successful VIX quote fetching."""
        result = vix_indicator.fetch_last_quote()

        assert result == 25.5
        mock_adapter.fetch_last_quote.assert_called_once_with("^VIX")

    def test_fetch_last_quote_error(self, mock_adapter):
        """Test VIX quote fetching with error."""
        mock_adapter.fetch_last_quote.side_effect = ValueError("API error")
        vix_indicator = VIXIndicator(mock_adapter)

        with pytest.raises(ValueError, match="API error"):
            vix_indicator.fetch_last_quote()


class TestSKEWIndicator:
    """Test the SKEWIndicator class."""

    @pytest.fixture
    def mock_adapter(self):
        """Create a mock adapter for SKEW testing."""
        adapter = Mock()
        adapter.fetch_last_quote.return_value = 120.0
        return adapter

    @pytest.fixture
    def skew_indicator(self, mock_adapter):
        """Create a SKEWIndicator instance for testing."""
        return SKEWIndicator(mock_adapter)

    def test_get_name(self, skew_indicator):
        """Test SKEW indicator name."""
        assert skew_indicator.get_name() == "^SKEW"

    def test_fetch_last_quote_success(self, skew_indicator, mock_adapter):
        """Test successful SKEW quote fetching."""
        result = skew_indicator.fetch_last_quote()

        assert result == 120.0
        mock_adapter.fetch_last_quote.assert_called_once_with("^SKEW")


class TestCPCIndicator:
    """Test the CPCIndicator class."""

    @pytest.fixture
    def mock_adapter(self):
        """Create a mock adapter for CPC testing."""
        adapter = Mock()
        adapter.fetch_last_quote.return_value = 0.8
        return adapter

    @pytest.fixture
    def cpc_indicator(self, mock_adapter):
        """Create a CPCIndicator instance for testing."""
        return CPCIndicator(mock_adapter)

    def test_get_name(self, cpc_indicator):
        """Test CPC indicator name."""
        assert cpc_indicator.get_name() == "Put/Call Ratio"

    def test_fetch_last_quote_success(self, cpc_indicator):
        """Test successful CPC quote fetching."""
        with patch("indicators.live_indicators.cpc_indicator.CPCIndicator._get_option_volumes") as mock_get_volumes:
            mock_get_volumes.return_value = ([100], [120], ["2025-12-31"])

            result = cpc_indicator.fetch_last_quote()

            assert result == 100 / 120


class TestBuffettIndicator:
    """Test the BuffettIndicator class."""

    @pytest.fixture
    def mock_adapter(self):
        """Create a mock adapter for Buffett testing."""
        adapter = Mock()
        adapter.fetch_last_quote.return_value = 150.0
        return adapter

    @pytest.fixture
    def buffett_indicator(self, mock_adapter):
        """Create a BuffettIndicator instance for testing."""
        return BuffettIndicator(mock_adapter)

    def test_get_name(self, buffett_indicator):
        """Test Buffett indicator name."""
        assert buffett_indicator.get_name() == "Buffett Indicator"

    def test_fetch_last_quote_success(self, buffett_indicator, mock_adapter):
        """Test successful Buffett indicator fetching."""
        result = buffett_indicator.fetch_last_quote()

        assert result == 150.0
        mock_adapter.fetch_last_quote.assert_called_once()


class TestIndicatorRegistry:
    """Test the indicator registry functionality."""

    def test_indicator_registry_imports(self):
        """Test that all indicators can be imported from registry."""
        from registries.indicator_registry import indicator_to_adapter_registry, indicators

        # Test that indicators list is not empty
        assert len(indicators) > 0

        # Test that registry has mappings
        assert len(indicator_to_adapter_registry) > 0

        # Test that all indicators have adapter mappings
        for indicator_class in indicators:
            class_name = indicator_class.__name__
            assert class_name in indicator_to_adapter_registry

    def test_indicator_weights(self):
        """Test that indicator weights are properly defined."""
        from registries.indicator_registry import indicator_to_weights

        # Test that weights are defined
        assert len(indicator_to_weights) > 0

        # Test that weights sum to approximately 1.0
        total_weight = sum(indicator_to_weights.values())
        assert 0.95 <= total_weight <= 1.05  # Allow small rounding differences

        # Test that all weights are positive
        for weight in indicator_to_weights.values():
            assert weight > 0
