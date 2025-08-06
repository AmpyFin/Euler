"""
Integration tests for the full market analysis cycle.
"""

import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

from clients.fetch_client import FetchClient
from clients.inference_client import InferenceClient
from clients.processing_client import ProcessingClient
from clients.system_client import SystemClient


class TestFullAnalysisCycle:
    """Test the complete market analysis cycle."""

    @pytest.fixture
    def mock_indicators(self):
        """Create mock indicators for testing."""
        indicators = []

        # Mock VIX indicator
        vix_indicator = Mock()
        vix_indicator.get_name.return_value = "VIX"
        vix_indicator.fetch_last_quote.return_value = 25.5
        indicators.append(vix_indicator)

        # Mock SKEW indicator
        skew_indicator = Mock()
        skew_indicator.get_name.return_value = "SKEW"
        skew_indicator.fetch_last_quote.return_value = 120.0
        indicators.append(skew_indicator)

        # Mock Put/Call indicator
        cpc_indicator = Mock()
        cpc_indicator.get_name.return_value = "Put/Call"
        cpc_indicator.fetch_last_quote.return_value = 0.8
        indicators.append(cpc_indicator)

        return indicators

    @pytest.fixture
    def fetch_client(self, mock_indicators):
        """Create a FetchClient with mock indicators."""
        client = FetchClient()
        client.indicators = mock_indicators
        return client

    @pytest.fixture
    def processing_client(self):
        """Create a ProcessingClient."""
        return ProcessingClient()

    @pytest.fixture
    def inference_client(self):
        """Create an InferenceClient."""
        return InferenceClient()

    def test_data_fetching_integration(self, fetch_client, mock_indicators):
        """Test integration of data fetching across all indicators."""
        # Fetch data from all indicators
        market_data = {}
        for indicator in fetch_client.indicators:
            try:
                name = indicator.get_name()
                value = indicator.fetch_last_quote()
                market_data[name] = value
            except Exception as e:
                pytest.fail(f"Failed to fetch data for {name}: {str(e)}")

        # Verify all indicators returned data
        assert len(market_data) == len(mock_indicators)
        assert "VIX" in market_data
        assert "SKEW" in market_data
        assert "Put/Call" in market_data

        # Verify data types and ranges
        assert isinstance(market_data["VIX"], (int, float))
        assert isinstance(market_data["SKEW"], (int, float))
        assert isinstance(market_data["Put/Call"], (int, float))
        assert market_data["VIX"] > 0
        assert market_data["SKEW"] > 0
        assert market_data["Put/Call"] > 0

    def test_data_processing_integration(self, fetch_client, processing_client, mock_indicators):
        """Test integration of data processing across all indicators."""
        # Fetch and process data
        processed_data = {}
        for indicator in fetch_client.indicators:
            try:
                name = indicator.get_name()
                raw_value = indicator.fetch_last_quote()
                score = processing_client.calculate_score(name, raw_value)
                processed_data[name] = {"raw_value": raw_value, "score": score}
            except Exception as e:
                pytest.fail(f"Failed to process data for {name}: {str(e)}")

        # Verify all indicators were processed
        assert len(processed_data) == len(mock_indicators)

        # Verify score ranges
        for name, data in processed_data.items():
            assert 0 <= data["score"] <= 100
            assert isinstance(data["score"], float)

    def test_market_analysis_integration(self, fetch_client, processing_client, inference_client, mock_indicators):
        """Test integration of market analysis with processed data."""
        # Fetch and process data
        processed_data_dict = {}
        for indicator in fetch_client.indicators:
            try:
                name = indicator.get_name()
                raw_value = indicator.fetch_last_quote()
                score = processing_client.calculate_score(name, raw_value)

                from clients.processing_client import ProcessedData

                processed_data = ProcessedData(indicator_name=name, raw_value=raw_value, score=score, timestamp=datetime.now())
                processed_data_dict[name] = processed_data
            except Exception as e:
                pytest.fail(f"Failed to process data for {name}: {str(e)}")

        # Run market analysis
        inference_client.data_buffer = processed_data_dict
        analysis = inference_client.analyze_market_state()

        # Verify analysis results
        assert analysis is not None
        assert hasattr(analysis, "score")
        assert hasattr(analysis, "regime")
        assert hasattr(analysis, "data")
        assert hasattr(analysis, "timestamp")

        # Verify score range
        assert 0 <= analysis.score <= 100
        assert isinstance(analysis.score, float)

        # Verify regime
        assert analysis.regime is not None
        assert hasattr(analysis.regime, "label")
        assert hasattr(analysis.regime, "description")
        assert isinstance(analysis.regime.label, str)

        # Verify data
        assert len(analysis.data) == len(processed_data_dict)
        for name, data in analysis.data.items():
            assert hasattr(data, "indicator_name")
            assert hasattr(data, "raw_value")
            assert hasattr(data, "score")
            assert data.indicator_name == name

    @patch("clients.system_client.QApplication")
    @patch("clients.system_client.control")
    def test_system_client_integration(self, mock_control, mock_qapp, mock_indicators):
        """Test integration of SystemClient with all components."""
        # Mock control settings
        mock_control.broadcast_mode = False
        mock_control.GUI_mode = False
        mock_control.run_continuously = False
        mock_control.broadcast_network = "127.0.0.1"
        mock_control.broadcast_port = 5001

        # Mock QApplication
        mock_qapp.instance.return_value = None
        mock_qapp.return_value = Mock()

        # Create system client
        system_client = SystemClient()

        # Mock the fetch client indicators
        system_client.fetch_client.indicators = mock_indicators

        # Run analysis cycle
        analysis = system_client.run_analysis_cycle()

        # Verify analysis was successful
        assert analysis is not None
        assert hasattr(analysis, "score")
        assert hasattr(analysis, "regime")
        assert hasattr(analysis, "data")

        # Verify all indicators were processed
        assert len(analysis.data) == len(mock_indicators)

        # Verify score calculation
        assert 0 <= analysis.score <= 100

    def test_error_handling_integration(self, fetch_client, processing_client, inference_client):
        """Test error handling across the full analysis cycle."""
        # Create indicators that will fail
        failing_indicators = []

        # Indicator that fails to fetch
        failing_fetch = Mock()
        failing_fetch.get_name.return_value = "FailingFetch"
        failing_fetch.fetch_last_quote.side_effect = ValueError("Fetch failed")
        failing_indicators.append(failing_fetch)

        # Indicator that fails to process
        failing_process = Mock()
        failing_process.get_name.return_value = "FailingProcess"
        failing_process.fetch_last_quote.return_value = "invalid_value"
        failing_indicators.append(failing_process)

        # Indicator that works
        working_indicator = Mock()
        working_indicator.get_name.return_value = "Working"
        working_indicator.fetch_last_quote.return_value = 25.5
        failing_indicators.append(working_indicator)

        # Test that system continues with working indicators
        processed_data_dict = {}
        for indicator in failing_indicators:
            try:
                name = indicator.get_name()
                raw_value = indicator.fetch_last_quote()
                score = processing_client.calculate_score(name, raw_value)

                from clients.processing_client import ProcessedData

                processed_data = ProcessedData(indicator_name=name, raw_value=raw_value, score=score, timestamp=datetime.now())
                processed_data_dict[name] = processed_data
            except Exception:
                # Expected for failing indicators
                continue

        # Should have at least one working indicator
        assert len(processed_data_dict) >= 1
        assert "Working" in processed_data_dict

        # Run analysis with partial data
        inference_client.data_buffer = processed_data_dict
        analysis = inference_client.analyze_market_state()

        # Analysis should still work with partial data
        assert analysis is not None
        assert len(analysis.data) == len(processed_data_dict)


class TestDataFlowIntegration:
    """Test data flow between components."""

    def test_market_data_flow(self):
        """Test data flow from MarketData to ProcessedData."""
        from clients.fetch_client import MarketData
        from clients.processing_client import ProcessedData

        # Create market data
        market_data = MarketData(indicator_name="Test", value=25.5, timestamp=datetime.now())

        # Process into processed data
        processing_client = ProcessingClient()
        score = processing_client.calculate_score("Test", market_data.value)

        processed_data = ProcessedData(
            indicator_name=market_data.indicator_name,
            raw_value=market_data.value,
            score=score,
            timestamp=market_data.timestamp,
        )

        # Verify data integrity
        assert processed_data.indicator_name == market_data.indicator_name
        assert processed_data.raw_value == market_data.value
        assert processed_data.timestamp == market_data.timestamp
        assert 0 <= processed_data.score <= 100

    def test_processed_data_to_analysis_flow(self):
        """Test data flow from ProcessedData to MarketAnalysis."""
        from clients.inference_client import InferenceClient
        from clients.processing_client import ProcessedData

        # Create processed data
        processed_data_dict = {
            "VIX": ProcessedData("VIX", 25.5, 65.0),
            "SKEW": ProcessedData("SKEW", 120.0, 55.0),
            "Put/Call": ProcessedData("Put/Call", 0.8, 70.0),
        }

        # Run analysis
        inference_client = InferenceClient()
        inference_client.data_buffer = processed_data_dict
        analysis = inference_client.analyze_market_state()

        # Verify data integrity
        assert len(analysis.data) == len(processed_data_dict)
        for name, data in analysis.data.items():
            assert data.indicator_name == processed_data_dict[name].indicator_name
            assert data.raw_value == processed_data_dict[name].raw_value
            assert data.score == processed_data_dict[name].score
