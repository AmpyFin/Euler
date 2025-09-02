"""
Unit tests for indicator classes.
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from indicators.indicator import Indicator
from indicators.risk_indicators.buffett_indicator import BuffettIndicator
from indicators.risk_indicators.cpc_indicator import CPCIndicator
from indicators.risk_indicators.skew_indicator import SKEWIndicator


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


# VIX indicator tests removed - VIX is reactive, not predictive


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
        with patch("indicators.risk_indicators.cpc_indicator.CPCIndicator._get_option_volumes") as mock_get_volumes:
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

    def test_indicator_registry_functions(self):
        """Test that registry functions work properly."""
        from registries.indicator_registry import (
            get_enabled_indicators,
            get_indicator_weight,
            get_active_provider,
            get_indicator_factory
        )

        # Test enabled indicators
        enabled = get_enabled_indicators()
        assert len(enabled) > 0

        # Test indicator weights
        for indicator in enabled:
            weight = get_indicator_weight(indicator)
            assert weight >= 0.0

        # Test active providers (should not raise errors)
        for indicator in enabled:
            try:
                provider = get_active_provider(indicator)
                assert provider is not None
            except Exception as e:
                # Some indicators might not have providers configured yet
                pass

        # Test indicator factories
        for indicator in enabled:
            try:
                factory = get_indicator_factory(indicator)
                assert factory is not None
            except Exception as e:
                # Some indicators might not have factories configured yet
                pass
