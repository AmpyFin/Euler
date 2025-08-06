"""
Pytest configuration and fixtures for Euler market analysis tests.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
from datetime import datetime
from typing import Dict, List

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from clients.fetch_client import MarketData
from clients.processing_client import ProcessedData
from clients.inference_client import MarketAnalysis, MarketRegime
from adapters.adapter import Adapter
from indicators.indicator import Indicator


@pytest.fixture
def mock_adapter():
    """Create a mock adapter for testing."""
    adapter = Mock(spec=Adapter)
    adapter.fetch_last_quote.return_value = 25.5
    adapter.fetch_last_quote_with_date.return_value = (25.5, datetime.now())
    adapter.fetch_historical_data.return_value = {
        datetime.now(): 25.5,
        datetime.now(): 26.0
    }
    return adapter


@pytest.fixture
def mock_indicator(mock_adapter):
    """Create a mock indicator for testing."""
    indicator = Mock(spec=Indicator)
    indicator.adapter = mock_adapter
    indicator.get_name.return_value = "Test VIX"
    indicator.fetch_last_quote.return_value = 25.5
    return indicator


@pytest.fixture
def sample_market_data():
    """Create sample market data for testing."""
    return MarketData(
        indicator_name="Test VIX",
        value=25.5,
        timestamp=datetime.now()
    )


@pytest.fixture
def sample_processed_data():
    """Create sample processed data for testing."""
    return ProcessedData(
        indicator_name="Test VIX",
        raw_value=25.5,
        score=65.0,
        timestamp=datetime.now()
    )


@pytest.fixture
def sample_market_analysis():
    """Create sample market analysis for testing."""
    # Create mock regime
    regime = Mock(spec=MarketRegime)
    regime.label = "Elevated Risk"
    regime.description = "Market showing elevated risk levels"
    
    # Create sample data
    data = {
        "VIX": ProcessedData("VIX", 25.5, 65.0),
        "SKEW": ProcessedData("SKEW", 120.0, 55.0),
        "Put/Call": ProcessedData("Put/Call", 0.8, 70.0)
    }
    
    analysis = Mock(spec=MarketAnalysis)
    analysis.score = 63.3
    analysis.regime = regime
    analysis.data = data
    analysis.timestamp = datetime.now()
    
    return analysis


@pytest.fixture
def mock_fetch_client():
    """Create a mock fetch client for testing."""
    client = Mock()
    client.indicators = []
    client.adapters = {}
    return client


@pytest.fixture
def mock_processing_client():
    """Create a mock processing client for testing."""
    client = Mock()
    client.data_buffer = {}
    return client


@pytest.fixture
def mock_inference_client():
    """Create a mock inference client for testing."""
    client = Mock()
    client.data_buffer = {}
    client.get_indicator_weight.return_value = 1.0
    return client


@pytest.fixture
def sample_indicator_data():
    """Create sample indicator data for testing."""
    return {
        "VIX": {"raw_value": 25.5, "score": 65.0},
        "SKEW": {"raw_value": 120.0, "score": 55.0},
        "Put/Call": {"raw_value": 0.8, "score": 70.0},
        "Buffett": {"raw_value": 150.0, "score": 75.0}
    }


@pytest.fixture
def mock_socket():
    """Create a mock socket for testing network functionality."""
    socket_mock = Mock()
    socket_mock.sendto.return_value = 50  # bytes sent
    return socket_mock


@pytest.fixture
def test_config():
    """Test configuration settings."""
    return {
        "broadcast_mode": False,
        "gui_mode": False,
        "run_continuously": False,
        "broadcast_network": "127.0.0.1",
        "broadcast_port": 5001
    }


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment with mocked dependencies."""
    # Mock PyQt5 to avoid GUI issues in tests
    mock_qt = Mock()
    mock_qt.QApplication = Mock()
    mock_qt.QMainWindow = Mock()
    mock_qt.QWidget = Mock()
    mock_qt.QVBoxLayout = Mock()
    mock_qt.QHBoxLayout = Mock()
    mock_qt.QLabel = Mock()
    mock_qt.QTabWidget = Mock()
    mock_qt.QFrame = Mock()
    mock_qt.QTextEdit = Mock()
    mock_qt.QScrollArea = Mock()
    mock_qt.Qt = Mock()
    mock_qt.QTimer = Mock()
    mock_qt.QThread = Mock()
    mock_qt.pyqtSignal = Mock()
    
    # Use setitem for sys.modules instead of setattr
    monkeypatch.setitem(sys.modules, "PyQt5", mock_qt)
    monkeypatch.setitem(sys.modules, "PyQt5.QtWidgets", mock_qt)
    monkeypatch.setitem(sys.modules, "PyQt5.QtCore", mock_qt)
    
    # Mock matplotlib
    mock_matplotlib = Mock()
    mock_matplotlib.use = Mock()
    mock_matplotlib.backends = Mock()
    mock_matplotlib.figure = Mock()
    mock_matplotlib.pyplot = Mock()
    
    monkeypatch.setitem(sys.modules, "matplotlib", mock_matplotlib)
    monkeypatch.setitem(sys.modules, "matplotlib.backends.backend_qt5agg", mock_matplotlib)
    monkeypatch.setitem(sys.modules, "matplotlib.figure", mock_matplotlib)
    
    # Mock numpy
    mock_numpy = Mock()
    mock_numpy.array = Mock()
    mock_numpy.mean = Mock()
    mock_numpy.std = Mock()
    monkeypatch.setitem(sys.modules, "numpy", mock_numpy) 