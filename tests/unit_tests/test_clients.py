"""
Unit tests for client classes.
"""

from datetime import datetime
from typing import Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from clients.client import Client
from clients.fetch_client import FetchClient, MarketData
from clients.inference_client import InferenceClient, MarketAnalysis, MarketRegime
from clients.processing_client import ProcessedData, ProcessingClient
from indicators.indicator import Indicator


class TestIndicator(Indicator):
    """Mock indicator class for testing."""
    def get_name(self) -> str:
        """Get the indicator's name."""
        return "test"

    def fetch_last_quote(self) -> float:
        """Fetch the latest value for this indicator."""
        return 42.0


class TestClient:
    """Test the base Client class."""

    def test_client_is_abstract(self):
        """Test that Client is an abstract base class."""
        with pytest.raises(TypeError):
            Client()


class TestFetchClient:
    """Test the FetchClient class."""

    @pytest.fixture
    def fetch_client(self):
        """Create a FetchClient instance for testing."""
        return FetchClient()

    def test_initialization(self, fetch_client):
        """Test FetchClient initialization."""
        assert hasattr(fetch_client, "adapters")
        assert hasattr(fetch_client, "indicators")
        assert isinstance(fetch_client.adapters, dict)
        assert isinstance(fetch_client.indicators, list)

    @patch("clients.fetch_client.indicator_to_adapter_registry")
    def test_initialize_indicators_no_adapter(self, mock_registry, fetch_client):
        """Test indicator initialization when no adapter is found."""
        mock_indicator_class = Mock()
        mock_indicator_class.__name__ = "TestIndicator"
        
        with patch('clients.fetch_client.indicators', [mock_indicator_class]):
            mock_registry.get.return_value = None
    
            indicators = fetch_client._initialize_indicators()
    
            assert len(indicators) == 0

    @patch("clients.fetch_client.indicator_to_adapter_registry")
    def test_initialize_indicators_exception(self, mock_registry, fetch_client):
        """Test indicator initialization with exception."""
        mock_indicator_class = Mock()
        mock_indicator_class.__name__ = "TestIndicator"
        mock_indicator_class.side_effect = Exception("Initialization error")
        
        with patch('clients.fetch_client.indicators', [mock_indicator_class]):
            mock_registry.get.return_value = Mock()
    
            indicators = fetch_client._initialize_indicators()
    
            assert len(indicators) == 0


class TestProcessingClient:
    """Test the ProcessingClient class."""

    @pytest.fixture
    def processing_client(self):
        """Create a ProcessingClient instance for testing."""
        return ProcessingClient()

    def test_initialization(self, processing_client):
        """Test ProcessingClient initialization."""
        assert hasattr(processing_client, "data_buffer")
        assert isinstance(processing_client.data_buffer, dict)

    def test_calculate_score_vix_low(self, processing_client):
        """Test VIX score calculation for low values."""
        score = processing_client.calculate_score("VIX", 8.0)
        assert 0 <= score <= 20

    def test_calculate_score_vix_normal(self, processing_client):
        """Test VIX score calculation for normal values."""
        score = processing_client.calculate_score("VIX", 18.0)
        assert 35 <= score <= 50

    def test_calculate_score_vix_high(self, processing_client):
        """Test VIX score calculation for high values."""
        score = processing_client.calculate_score("VIX", 35.0)
        assert 75 <= score <= 90

    def test_calculate_score_vix_extreme(self, processing_client):
        """Test VIX score calculation for extreme values."""
        score = processing_client.calculate_score("VIX", 50.0)
        assert 90 <= score <= 100

    def test_calculate_score_skew_low(self, processing_client):
        """Test SKEW score calculation for low values."""
        score = processing_client.calculate_score("SKEW", 95.0)
        assert 0 <= score <= 25

    def test_calculate_score_skew_normal(self, processing_client):
        """Test SKEW score calculation for normal values."""
        score = processing_client.calculate_score("SKEW", 115.0)
        assert 40 <= score <= 55

    def test_calculate_score_skew_high(self, processing_client):
        """Test SKEW score calculation for high values."""
        score = processing_client.calculate_score("SKEW", 135.0)
        assert 75 <= score <= 90

    def test_calculate_score_put_call_low(self, processing_client):
        """Test Put/Call score calculation for low values."""
        score = processing_client.calculate_score("Put/Call", 0.3)
        assert 0 <= score <= 30

    def test_calculate_score_put_call_normal(self, processing_client):
        """Test Put/Call score calculation for normal values."""
        score = processing_client.calculate_score("Put/Call", 0.6)
        assert 40 <= score <= 55

    def test_calculate_score_put_call_high(self, processing_client):
        """Test Put/Call score calculation for high values."""
        score = processing_client.calculate_score("Put/Call", 1.2)
        assert 90 <= score <= 100

    def test_calculate_score_term_structure(self, processing_client):
        """Test term structure score calculation."""
        score = processing_client.calculate_score("Term Slope", 1.1)
        assert 85 <= score <= 95

    def test_calculate_score_buffett_low(self, processing_client):
        """Test Buffett indicator score calculation for low values."""
        score = processing_client.calculate_score("Buffett", 70.0)
        assert 0 <= score <= 20

    def test_calculate_score_buffett_normal(self, processing_client):
        """Test Buffett indicator score calculation for normal values."""
        score = processing_client.calculate_score("Buffett", 110.0)
        assert 40 <= score <= 60

    def test_calculate_score_buffett_high(self, processing_client):
        """Test Buffett indicator score calculation for high values."""
        score = processing_client.calculate_score("Buffett", 160.0)
        assert 85 <= score <= 95

    def test_calculate_score_unknown_indicator(self, processing_client):
        """Test score calculation for unknown indicator."""
        score = processing_client.calculate_score("Unknown", 50.0)
        assert score == 50.0  # Default score

    def test_calculate_score_exception_handling(self, processing_client):
        """Test exception handling in score calculation."""
        score = processing_client.calculate_score("VIX", "invalid")
        assert score == 50.0  # Default score on error


class TestInferenceClient:
    """Test the InferenceClient class."""

    @pytest.fixture
    def inference_client(self):
        """Create an InferenceClient instance for testing."""
        return InferenceClient()

    def test_initialization(self, inference_client):
        """Test InferenceClient initialization."""
        assert hasattr(inference_client, "data_buffer")
        assert isinstance(inference_client.data_buffer, dict)

    def test_get_indicator_weight(self, inference_client):
        """Test indicator weight calculation."""
        # Mock processed data
        mock_data = {"VIX": ProcessedData("VIX", 25.5, 65.0), "SKEW": ProcessedData("SKEW", 120.0, 55.0)}

        weight = inference_client.get_indicator_weight("^VIX", 25.5, 65.0, mock_data)
        assert isinstance(weight, float)
        assert weight > 0

    def test_analyze_market_state(self, inference_client):
        """Test market state analysis."""
        # Mock processed data
        inference_client.data_buffer = {
            "VIX": ProcessedData("VIX", 25.5, 65.0),
            "SKEW": ProcessedData("SKEW", 120.0, 55.0),
            "Put/Call": ProcessedData("Put/Call", 0.8, 70.0),
        }

        analysis = inference_client.analyze_market_state()

        assert isinstance(analysis, MarketAnalysis)
        assert hasattr(analysis, "score")
        assert hasattr(analysis, "regime")
        assert hasattr(analysis, "data")
        assert isinstance(analysis.score, float)
        assert isinstance(analysis.regime, MarketRegime)
        assert isinstance(analysis.data, dict)

    def test_analyze_market_state_empty_data(self, inference_client):
        """Test market state analysis with empty data."""
        inference_client.data_buffer = {}

        analysis = inference_client.analyze_market_state()

        assert analysis is None or isinstance(analysis, MarketAnalysis)

    def test_determine_regime(self, inference_client):
        """Test regime determination logic."""
        # Test different score ranges
        low_regime = inference_client.get_regime_from_score(25.0)
        assert "STABLE" in low_regime.label

        high_regime = inference_client.get_regime_from_score(75.0)
        assert "HIGH STRESS" in high_regime.label

        extreme_regime = inference_client.get_regime_from_score(95.0)
        assert "CRISIS" in extreme_regime.label
