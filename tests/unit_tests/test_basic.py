"""
Basic tests to verify the test setup is working correctly.
"""

import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)


class TestBasicSetup:
    """Basic tests to verify the test environment is set up correctly."""

    def test_imports_work(self):
        """Test that basic imports work."""
        try:
            from clients.fetch_client import FetchClient
            from clients.processing_client import ProcessingClient
            from clients.inference_client import InferenceClient
            from adapters.adapter import Adapter
            from indicators.indicator import Indicator

            assert True
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")

    def test_project_structure(self):
        """Test that the project structure is correct."""
        project_root = Path(__file__).parent.parent.parent

        # Check that key directories exist
        assert (project_root / "clients").exists()
        assert (project_root / "adapters").exists()
        assert (project_root / "indicators").exists()
        assert (project_root / "registries").exists()
        assert (project_root / "tests").exists()

        # Check that key files exist
        assert (project_root / "requirements.txt").exists()
        assert (project_root / "requirements-test.txt").exists()
        assert (project_root / "setup.py").exists()
        assert (project_root / "pytest.ini").exists()

    def test_pytest_working(self):
        """Test that pytest is working correctly."""
        assert True  # If this runs, pytest is working

    def test_fixtures_available(self, mock_adapter, mock_indicator):
        """Test that fixtures are available."""
        assert mock_adapter is not None
        assert mock_indicator is not None
        assert hasattr(mock_adapter, "fetch_last_quote")
        assert hasattr(mock_indicator, "get_name")

    def test_sample_data_fixtures(self, sample_market_data, sample_processed_data):
        """Test that sample data fixtures work."""
        assert sample_market_data is not None
        assert sample_processed_data is not None
        assert hasattr(sample_market_data, "indicator_name")
        assert hasattr(sample_processed_data, "indicator_name")

    def test_mock_clients(self, mock_fetch_client, mock_processing_client, mock_inference_client):
        """Test that mock client fixtures work."""
        assert mock_fetch_client is not None
        assert mock_processing_client is not None
        assert mock_inference_client is not None


class TestConfiguration:
    """Test configuration and settings."""

    def test_python_version(self):
        """Test that we're using a supported Python version."""
        version = sys.version_info
        assert version.major == 3
        assert version.minor >= 8, "Python 3.8+ required"

    def test_project_path_in_sys_path(self):
        """Test that the project root is in sys.path."""
        project_root = str(Path(__file__).parent.parent.parent)
        assert project_root in sys.path

    def test_test_environment(self):
        """Test that we're in a test environment."""
        # This test should run in the test environment
        assert "pytest" in sys.modules or "test" in __file__


class TestDependencies:
    """Test that required dependencies are available."""

    def test_pytest_available(self):
        """Test that pytest is available."""
        import pytest

        assert pytest is not None

    def test_mock_available(self):
        """Test that unittest.mock is available."""
        from unittest.mock import Mock, patch

        assert Mock is not None
        assert patch is not None

    def test_datetime_available(self):
        """Test that datetime is available."""
        from datetime import datetime

        assert datetime is not None
        assert datetime.now() is not None
