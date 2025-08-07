# Euler Market Analysis - Testing

This directory contains comprehensive tests for the Euler Market Analysis system.

## Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and fixtures
├── unit_tests/                 # Unit tests for individual components
│   ├── test_adapters.py       # Tests for data adapters
│   ├── test_indicators.py     # Tests for market indicators
│   ├── test_clients.py        # Tests for client classes
│   └── test_system_client.py  # Tests for system orchestration
├── integration_tests/          # Integration tests
│   ├── test_full_analysis_cycle.py  # End-to-end analysis tests
│   └── test_network_broadcast.py    # Network functionality tests
├── e2e_tests/                 # End-to-end tests (existing)
└── run_tests.py               # Test runner script
```

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements-test.txt
```

### Running All Tests

```bash
# Run all tests
python tests/run_tests.py

# Run with verbose output
python tests/run_tests.py --verbose

# Run with coverage report
python tests/run_tests.py --coverage
```

### Running Specific Test Types

```bash
# Run only unit tests
python tests/run_tests.py --unit

# Run only integration tests
python tests/run_tests.py --integration

# Run with pytest directly
pytest tests/unit_tests/
pytest tests/integration_tests/
```

### Running with Coverage

```bash
# Generate coverage report
pytest --cov=clients --cov=adapters --cov=indicators --cov=registries --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Test Categories

### Unit Tests (`unit_tests/`)

- **test_adapters.py**: Tests for data adapters (YFinance, Buffett Indicator)
- **test_indicators.py**: Tests for market indicators (VIX, SKEW, Put/Call, etc.)
- **test_clients.py**: Tests for client classes (Fetch, Processing, Inference)
- **test_system_client.py**: Tests for system orchestration and GUI

### Integration Tests (`integration_tests/`)

- **test_full_analysis_cycle.py**: Tests the complete analysis pipeline
- **test_network_broadcast.py**: Tests network broadcast functionality

### End-to-End Tests (`e2e_tests/`)

- Existing end-to-end tests for complete system validation

## Test Fixtures

The `conftest.py` file provides common fixtures:

- `mock_adapter`: Mock data adapter
- `mock_indicator`: Mock market indicator
- `sample_market_data`: Sample market data
- `sample_processed_data`: Sample processed data
- `sample_market_analysis`: Sample market analysis
- `mock_fetch_client`: Mock fetch client
- `mock_processing_client`: Mock processing client
- `mock_inference_client`: Mock inference client

## Test Coverage

The test suite aims for:
- **Unit Tests**: 90%+ coverage of individual components
- **Integration Tests**: Full pipeline validation
- **Error Handling**: Comprehensive error scenario testing
- **Edge Cases**: Boundary condition testing

## Continuous Integration

Tests are automatically run on:
- Every pull request
- Every push to main/develop branches
- Multiple Python versions (3.9, 3.10, 3.11)

The CI pipeline includes:
- Unit and integration tests
- Code coverage reporting
- Linting (flake8, black, isort, mypy)
- Security scanning (bandit, safety)
- Package building

## Writing New Tests

### Unit Test Guidelines

1. Test one specific functionality per test
2. Use descriptive test names
3. Mock external dependencies
4. Test both success and failure cases
5. Test edge cases and boundary conditions

Example:
```python
def test_calculate_score_vix_normal(self, processing_client):
    """Test VIX score calculation for normal values."""
    score = processing_client.calculate_score("VIX", 18.0)
    assert 35 <= score <= 50
```

### Integration Test Guidelines

1. Test component interactions
2. Use realistic data scenarios
3. Test error propagation
4. Verify data integrity across components

Example:
```python
def test_data_processing_integration(self, fetch_client, processing_client):
    """Test integration of data processing across all indicators."""
    # Test complete data flow
    processed_data = {}
    for indicator in fetch_client.indicators:
        # Process each indicator
        # Verify results
```

## Debugging Tests

### Running Tests in Debug Mode

```bash
# Run with detailed output
pytest -v -s tests/

# Run specific test with debugger
pytest -s tests/unit_tests/test_clients.py::TestProcessingClient::test_calculate_score_vix_normal
```

### Common Issues

1. **Import Errors**: Ensure project root is in Python path
2. **Mock Issues**: Check mock setup in conftest.py
3. **GUI Tests**: GUI components are mocked to avoid display issues
4. **Network Tests**: Network calls are mocked to avoid external dependencies

## Performance Testing

For performance-critical components:

```bash
# Run performance tests
pytest tests/ -m "slow"

# Run with timing
pytest --durations=10 tests/
```

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Update this README if needed

## Test Configuration

The `pytest.ini` file configures:
- Test discovery patterns
- Coverage settings
- Markers for test categorization
- Output formatting 