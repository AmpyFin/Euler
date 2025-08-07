"""
Integration tests for network broadcast functionality.
"""

import socket
import threading
import time
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from clients.system_client import SystemClient


@pytest.fixture
def mock_socket():
    """Create a mock socket for testing."""
    mock_sock = Mock()
    mock_sock.sendto.return_value = 50  # bytes sent
    return mock_sock


@pytest.fixture
def sample_analysis():
    """Create a sample market analysis for testing."""
    # Create mock regime
    regime = Mock()
    regime.label = "Elevated Risk"
    regime.description = "Market showing elevated risk levels"

    # Create sample data
    from clients.processing_client import ProcessedData

    data = {
        "VIX": ProcessedData("VIX", 25.5, 65.0),
        "SKEW": ProcessedData("SKEW", 120.0, 55.0),
        "Put/Call": ProcessedData("Put/Call", 0.8, 70.0),
    }

    analysis = Mock()
    analysis.score = 63.3
    analysis.regime = regime
    analysis.data = data
    analysis.timestamp = datetime.now()

    return analysis


class TestNetworkBroadcast:
    """Test network broadcast functionality."""

    def test_broadcast_message_format(self, sample_analysis, mock_socket):
        """Test the format of broadcast messages."""
        with patch("clients.system_client.SystemClient.__init__", return_value=None):
            client = SystemClient()
            client.broadcast_mode = True
            client.socket = mock_socket
            client.broadcast_network = "127.0.0.1"
            client.broadcast_port = 5001

            client.broadcast_analysis(sample_analysis)

            # Verify message was sent
            mock_socket.sendto.assert_called_once()
            args, kwargs = mock_socket.sendto.call_args

            # Decode message
            message = args[0].decode()
            target_address = args[1]

            # Verify message format: "EULER|score|regime"
            parts = message.split("|")
            assert len(parts) == 3
            assert parts[0] == "EULER"
            # Compare float values with tolerance
            score_diff = abs(float(parts[1]) - sample_analysis.score)
            assert score_diff < 0.1, f"Score difference {score_diff} exceeds tolerance"
            assert parts[2] == sample_analysis.regime.label

            # Verify target address
            assert target_address == ("127.0.0.1", 5001)

    def test_broadcast_disabled(self, sample_analysis):
        """Test that broadcast is disabled when not in broadcast mode."""
        with patch("clients.system_client.SystemClient.__init__", return_value=None):
            client = SystemClient()
            client.broadcast_mode = False
            client.socket = None

            # Should not raise exception
            client.broadcast_analysis(sample_analysis)

    def test_broadcast_no_socket(self, sample_analysis):
        """Test broadcast behavior when socket is None."""
        with patch("clients.system_client.SystemClient.__init__", return_value=None):
            client = SystemClient()
            client.broadcast_mode = True
            client.socket = None
            client.broadcast_network = "127.0.0.1"
            client.broadcast_port = 5001

            # Should not raise exception
            client.broadcast_analysis(sample_analysis)

    def test_broadcast_socket_error(self, sample_analysis, mock_socket):
        """Test broadcast behavior when socket send fails."""
        with patch("clients.system_client.SystemClient.__init__", return_value=None):
            client = SystemClient()
            client.broadcast_mode = True
            client.socket = mock_socket
            client.broadcast_network = "127.0.0.1"
            client.broadcast_port = 5001

            # Mock socket error
            mock_socket.sendto.side_effect = socket.error("Network error")

            # Should not raise exception
            client.broadcast_analysis(sample_analysis)

    @patch("clients.system_client.socket")
    def test_socket_initialization(self, mock_socket_module, sample_analysis):
        """Test socket initialization in broadcast mode."""
        # Create a mock control module
        mock_control = Mock()
        mock_control.broadcast_mode = True
        mock_control.GUI_mode = False
        mock_control.run_continuously = False
        mock_control.broadcast_network = "127.0.0.1"
        mock_control.broadcast_port = 5001

        # Mock QApplication
        with patch("clients.system_client.QApplication") as mock_qapp:
            mock_qapp.instance.return_value = None
            mock_qapp.return_value = Mock()

            # Mock socket
            mock_socket_instance = Mock()
            mock_socket_module.socket.return_value = mock_socket_instance

            # Mock control module import
            with patch.dict("sys.modules", {"control": mock_control}):
                client = SystemClient()

                # Verify socket was created
                assert client.broadcast_mode is True
                assert client.socket is not None
                mock_socket_module.socket.assert_called_once()
                mock_socket_instance.setsockopt.assert_called()
                mock_socket_instance.bind.assert_called_once()

    def test_broadcast_integration_with_analysis(self, sample_analysis, mock_socket):
        """Test broadcast integration with analysis results handling."""
        with patch("clients.system_client.SystemClient.__init__", return_value=None):
            client = SystemClient()
            client.broadcast_mode = True
            client.socket = mock_socket
            client.gui = None
            client.broadcast_network = "127.0.0.1"
            client.broadcast_port = 5001

            # Handle analysis results (which should trigger broadcast)
            client.handle_analysis_results(sample_analysis)

            # Verify broadcast was called
            mock_socket.sendto.assert_called_once()

    def test_multiple_broadcasts(self, sample_analysis, mock_socket):
        """Test multiple consecutive broadcasts."""
        with patch("clients.system_client.SystemClient.__init__", return_value=None):
            client = SystemClient()
            client.broadcast_mode = True
            client.socket = mock_socket
            client.broadcast_network = "127.0.0.1"
            client.broadcast_port = 5001

            # Send multiple broadcasts
            for i in range(3):
                # Modify score for each broadcast
                sample_analysis.score = 50.0 + i * 10.0
                client.broadcast_analysis(sample_analysis)

            # Verify all broadcasts were sent
            assert mock_socket.sendto.call_count == 3

            # Verify different messages were sent
            calls = mock_socket.sendto.call_args_list
            messages = [call[0][0].decode() for call in calls]

            # Should have different scores
            scores = [float(msg.split("|")[1]) for msg in messages]
            assert len(set(scores)) == 3  # All different scores


class TestNetworkReceiver:
    """Test network receiver functionality."""

    def test_receive_broadcast_message(self):
        """Test receiving a broadcast message."""
        # Create a test message
        test_message = "EULER|63.3|Elevated Risk"
        message_bytes = test_message.encode()

        # Parse the message
        parts = test_message.split("|")
        assert len(parts) == 3
        assert parts[0] == "EULER"
        score = float(parts[1])
        regime = parts[2]

        # Verify parsed values
        assert score == 63.3
        assert regime == "Elevated Risk"

    def test_invalid_message_format(self):
        """Test handling of invalid message formats."""
        invalid_messages = [
            "INVALID|63.3|Elevated Risk",  # Wrong prefix
            "EULER|63.3",  # Missing regime
            "EULER||Elevated Risk",  # Missing score
            "EULER|invalid|Elevated Risk",  # Invalid score
            "EULER|63.3|",  # Missing regime
        ]

        for message in invalid_messages:
            parts = message.split("|")

            # Test message validation
            if len(parts) != 3:
                continue  # Invalid format

            if parts[0] != "EULER":
                continue  # Wrong prefix

            try:
                score = float(parts[1])
            except ValueError:
                continue  # Invalid score

            if not parts[2]:
                continue  # Missing regime

            # If we get here, the message is valid
            assert False, f"Message should be invalid: {message}"

    def test_message_parsing_edge_cases(self):
        """Test edge cases in message parsing."""
        # Test with different score formats
        valid_messages = [
            "EULER|0.0|Low Risk",
            "EULER|100.0|Extreme Risk",
            "EULER|50.5|Normal Risk",
            "EULER|99.99|High Risk",
        ]

        for message in valid_messages:
            parts = message.split("|")
            assert len(parts) == 3
            assert parts[0] == "EULER"

            score = float(parts[1])
            assert 0.0 <= score <= 100.0

            regime = parts[2]
            assert len(regime) > 0


class TestNetworkPerformance:
    """Test network performance characteristics."""

    def test_broadcast_message_size(self, sample_analysis, mock_socket):
        """Test that broadcast messages are reasonably sized."""
        with patch("clients.system_client.SystemClient.__init__", return_value=None):
            client = SystemClient()
            client.broadcast_mode = True
            client.socket = mock_socket
            client.broadcast_network = "127.0.0.1"
            client.broadcast_port = 5001

            client.broadcast_analysis(sample_analysis)

            # Get the sent message
            args, kwargs = mock_socket.sendto.call_args
            message_bytes = args[0]

            # Verify message size is reasonable (should be small)
            assert len(message_bytes) < 1000  # Less than 1KB

            # Verify message is not empty
            assert len(message_bytes) > 0

    def test_broadcast_frequency(self, sample_analysis, mock_socket):
        """Test broadcast frequency handling."""
        with patch("clients.system_client.SystemClient.__init__", return_value=None):
            client = SystemClient()
            client.broadcast_mode = True
            client.socket = mock_socket
            client.broadcast_network = "127.0.0.1"
            client.broadcast_port = 5001

            # Send many broadcasts quickly
            start_time = time.time()
            for i in range(100):
                sample_analysis.score = 50.0 + i * 0.1
                client.broadcast_analysis(sample_analysis)
            end_time = time.time()

            # Verify all broadcasts were sent
            assert mock_socket.sendto.call_count == 100

            # Verify performance (should be fast)
            duration = end_time - start_time
            assert duration < 1.0  # Should complete in less than 1 second
