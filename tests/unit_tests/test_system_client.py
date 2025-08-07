"""
Unit tests for the SystemClient class.
"""

import socket
import sys
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from clients.system_client import AnalysisWorker, SystemClient, SystemGUI


class TestAnalysisWorker:
    """Test the AnalysisWorker class."""

    @pytest.fixture
    def mock_system_client(self):
        """Create a mock system client for testing."""
        client = Mock()
        client.run_analysis_cycle.return_value = Mock()
        return client

    @pytest.fixture
    def worker(self, mock_system_client):
        """Create an AnalysisWorker instance for testing."""
        return AnalysisWorker(mock_system_client)

    def test_initialization(self, worker, mock_system_client):
        """Test AnalysisWorker initialization."""
        assert worker.system_client == mock_system_client
        assert worker.running is True

    def test_stop(self, worker):
        """Test stopping the worker thread."""
        worker.stop()
        assert worker.running is False

    @patch("clients.system_client.QThread")
    def test_run_success(self, mock_qthread, worker, mock_system_client):
        """Test successful worker run."""
        # Mock the analysis result
        mock_analysis = Mock()
        mock_system_client.run_analysis_cycle.return_value = mock_analysis

        # Mock QThread.sleep to avoid actual sleeping
        mock_qthread.sleep = Mock()

        # Set running to False after first iteration
        def stop_after_first(*args, **kwargs):
            worker.running = False

        mock_qthread.sleep.side_effect = stop_after_first

        # Run the worker
        worker.run()

        # Verify analysis was called
        mock_system_client.run_analysis_cycle.assert_called()

    @patch("clients.system_client.QThread")
    def test_run_exception_handling(self, mock_qthread, worker, mock_system_client):
        """Test exception handling in worker run."""
        # Mock exception in analysis cycle
        mock_system_client.run_analysis_cycle.side_effect = Exception("Test error")

        # Mock QThread.sleep to avoid actual sleeping
        mock_qthread.sleep = Mock()

        # Set running to False after first iteration
        def stop_after_first(*args, **kwargs):
            worker.running = False

        mock_qthread.sleep.side_effect = stop_after_first

        # Run the worker (should not raise exception)
        worker.run()

        # Verify analysis was called despite exception
        mock_system_client.run_analysis_cycle.assert_called()


class TestSystemGUI:
    """Test the SystemGUI class."""

    @pytest.mark.skip(reason="GUI tests disabled in CI environment")
    @pytest.fixture
    def mock_inference_client(self):
        """Create a mock inference client for testing."""
        client = Mock()
        client.get_indicator_weight.return_value = 1.0
        return client

    @pytest.mark.skip(reason="GUI tests disabled in CI environment")
    @pytest.fixture
    def gui(self, mock_inference_client):
        """Create a SystemGUI instance for testing."""
        try:
            return SystemGUI(mock_inference_client)
        except Exception:
            # Skip GUI tests if there are issues
            pytest.skip("GUI tests skipped due to environment issues")

    @pytest.mark.skip(reason="GUI tests disabled in CI environment")
    def test_initialization(self, gui, mock_inference_client):
        """Test SystemGUI initialization."""
        assert gui.inference_client == mock_inference_client
        assert hasattr(gui, "history")
        assert hasattr(gui, "tabs")

    @pytest.mark.skip(reason="GUI tests disabled in CI environment")
    def test_setup_overview_tab(self, gui):
        """Test overview tab setup."""
        # Verify overview tab was created
        assert gui.tabs.count() > 0
        assert gui.tabs.tabText(0) == "Overview"

    @pytest.mark.skip(reason="GUI tests disabled in CI environment")
    def test_setup_details_tab(self, gui):
        """Test details tab setup."""
        # Verify details tab was created
        assert gui.tabs.count() > 1
        assert gui.tabs.tabText(1) == "Indicator Details"

    @pytest.mark.skip(reason="GUI tests disabled in CI environment")
    def test_create_indicator_frame(self, gui):
        """Test indicator frame creation."""
        frame_data = gui._create_indicator_frame("Test Indicator")

        assert "Test Indicator" in gui.indicator_frames
        assert frame_data == gui.indicator_frames["Test Indicator"]
        assert hasattr(frame_data, "frame")
        assert hasattr(frame_data, "fig")
        assert hasattr(frame_data, "ax")
        assert hasattr(frame_data, "canvas")

    @pytest.mark.skip(reason="GUI tests disabled in CI environment")
    def test_update_display(self, gui, sample_market_analysis):
        """Test display update with analysis results."""
        # Update display
        gui.update_display(sample_market_analysis)

        # Verify history was updated
        assert len(gui.history["scores"]) > 0
        assert len(gui.history["regimes"]) > 0
        assert len(gui.history["timestamps"]) > 0

        # Verify score label was updated
        expected_score = f"Market Risk Score: {sample_market_analysis.score:.2f}"
        assert gui.score_label.text() == expected_score

    @pytest.mark.skip(reason="GUI tests disabled in CI environment")
    def test_update_display_exception_handling(self, gui):
        """Test exception handling in display update."""
        # Create invalid analysis that will cause exception
        invalid_analysis = Mock()
        invalid_analysis.score = "invalid"
        invalid_analysis.regime = Mock()
        invalid_analysis.regime.label = "Test"
        invalid_analysis.data = {}

        # Should not raise exception
        gui.update_display(invalid_analysis)


class TestSystemClient:
    """Test the SystemClient class."""

    @patch("clients.system_client.InferenceClient")
    @patch("clients.system_client.ProcessingClient")
    @patch("clients.system_client.FetchClient")
    @patch("clients.system_client.QApplication")
    def test_initialization(self, mock_qapp, mock_fetch, mock_processing, mock_inference, monkeypatch):
        """Test SystemClient initialization."""
        # Mock control settings
        mock_control = MagicMock()
        mock_control.broadcast_mode = False
        mock_control.GUI_mode = False
        mock_control.run_continuously = False
        mock_control.broadcast_network = "127.0.0.1"
        mock_control.broadcast_port = 5001
        monkeypatch.setitem(sys.modules, "control", mock_control)

        # Mock QApplication
        mock_qapp.instance.return_value = None
        mock_qapp.return_value = Mock()

        client = SystemClient()

        assert hasattr(client, "fetch_client")
        assert hasattr(client, "processing_client")
        assert hasattr(client, "inference_client")
        assert hasattr(client, "broadcast_mode")
        assert hasattr(client, "gui_mode")
        assert hasattr(client, "run_continuously")

    @patch("clients.system_client.socket")
    @patch("clients.system_client.InferenceClient")
    @patch("clients.system_client.ProcessingClient")
    @patch("clients.system_client.FetchClient")
    @patch("clients.system_client.QApplication")
    def test_initialization_broadcast_mode(
        self, mock_qapp, mock_fetch, mock_processing, mock_inference, mock_socket, monkeypatch
    ):
        """Test SystemClient initialization with broadcast mode."""
        # Mock control settings
        mock_control = MagicMock()
        mock_control.broadcast_mode = True
        mock_control.GUI_mode = False
        mock_control.run_continuously = False
        mock_control.broadcast_network = "127.0.0.1"
        mock_control.broadcast_port = 5001
        monkeypatch.setitem(sys.modules, "control", mock_control)

        # Mock QApplication
        mock_qapp.instance.return_value = None
        mock_qapp.return_value = Mock()

        # Mock socket
        mock_socket_instance = Mock()
        mock_socket.socket.return_value = mock_socket_instance

        client = SystemClient()

        assert client.broadcast_mode is True
        assert client.socket is not None
        mock_socket.socket.assert_called_once()

    @patch("clients.system_client.SystemGUI")
    @patch("clients.system_client.InferenceClient")
    @patch("clients.system_client.ProcessingClient")
    @patch("clients.system_client.FetchClient")
    @patch("clients.system_client.QApplication")
    def test_initialization_gui_mode(self, mock_qapp, mock_fetch, mock_processing, mock_inference, mock_gui, monkeypatch):
        """Test SystemClient initialization with GUI mode."""
        # Mock control settings
        mock_control = MagicMock()
        mock_control.broadcast_mode = False
        mock_control.GUI_mode = True
        mock_control.run_continuously = False
        mock_control.broadcast_network = "127.0.0.1"
        mock_control.broadcast_port = 5001
        monkeypatch.setitem(sys.modules, "control", mock_control)

        # Mock QApplication
        mock_qapp.instance.return_value = None
        mock_qapp.return_value = Mock()

        client = SystemClient()

        assert client.gui_mode is True
        assert client.gui is not None

    def test_handle_analysis_results(self, sample_market_analysis):
        """Test handling of analysis results."""
        with patch("clients.system_client.SystemClient.__init__", return_value=None):
            client = SystemClient()
            client.broadcast_mode = False
            client.gui = None

            # Should not raise exception
            client.handle_analysis_results(sample_market_analysis)

    def test_handle_analysis_results_with_broadcast(self, sample_market_analysis, mock_socket):
        """Test handling of analysis results with broadcast mode."""
        with patch("clients.system_client.SystemClient.__init__", return_value=None):
            client = SystemClient()
            client.broadcast_mode = True
            client.socket = mock_socket
            client.gui = None
            client.broadcast_network = "127.0.0.1"
            client.broadcast_port = 5001

            client.handle_analysis_results(sample_market_analysis)

            # Verify broadcast was called
            mock_socket.sendto.assert_called_once()

    @pytest.mark.skip(reason="GUI tests are causing crashes in the test environment")
    def test_handle_analysis_results_with_gui(self, sample_market_analysis, mock_inference_client):
        """Test handling of analysis results with GUI."""
        with patch("clients.system_client.SystemClient.__init__", return_value=None):
            client = SystemClient()
            client.broadcast_mode = False
            client.gui = SystemGUI(mock_inference_client)

            client.handle_analysis_results(sample_market_analysis)

            # Verify GUI was updated
            assert len(client.gui.history["scores"]) > 0

    @patch("clients.system_client.AnalysisWorker")
    def test_run_analysis_cycle(self, mock_worker_class):
        """Test running a single analysis cycle."""
        with patch("clients.system_client.SystemClient.__init__", return_value=None):
            client = SystemClient()
            client.fetch_client = Mock()
            client.processing_client = Mock()
            client.inference_client = Mock()

            # Mock indicators
            mock_indicator = Mock()
            mock_indicator.get_name.return_value = "Test"
            mock_indicator.fetch_last_quote.return_value = 25.5
            client.fetch_client.indicators = [mock_indicator]

            # Mock processing
            client.processing_client.calculate_score.return_value = 65.0

            # Mock inference
            mock_analysis = Mock()
            client.inference_client.analyze_market_state.return_value = mock_analysis

            result = client.run_analysis_cycle()

            assert result == mock_analysis
            mock_indicator.fetch_last_quote.assert_called_once()
            client.processing_client.calculate_score.assert_called_once()
            client.inference_client.analyze_market_state.assert_called_once()

    def test_broadcast_analysis(self, sample_market_analysis, mock_socket):
        """Test broadcasting analysis results."""
        with patch("clients.system_client.SystemClient.__init__", return_value=None):
            client = SystemClient()
            client.broadcast_mode = True
            client.socket = mock_socket
            client.broadcast_network = "127.0.0.1"
            client.broadcast_port = 5001

            client.broadcast_analysis(sample_market_analysis)

            # Verify message was sent
            mock_socket.sendto.assert_called_once()
            args, kwargs = mock_socket.sendto.call_args
            message = args[0].decode()
            assert "EULER|" in message
            assert str(sample_market_analysis.score) in message
            assert sample_market_analysis.regime.label in message

    def test_broadcast_analysis_disabled(self, sample_market_analysis):
        """Test broadcasting when disabled."""
        with patch("clients.system_client.SystemClient.__init__", return_value=None):
            client = SystemClient()
            client.broadcast_mode = False
            client.socket = None

            # Should not raise exception
            client.broadcast_analysis(sample_market_analysis)
