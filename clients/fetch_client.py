"""
Client for fetching market data.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

from adapters.buffet_indicator_adapter import BuffettIndicatorAdapter
from adapters.yfinance_adapter import YFinanceAdapter
from clients.client import Client
from clients.logging_config import fetch_logger as logger
from registries.indicator_registry import indicator_to_adapter_registry, indicators


@dataclass
class MarketData:
    """Container for market data."""

    indicator_name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    error: str = ""


class FetchClient(Client):
    """Client for fetching market data."""

    def __init__(self):
        """Initialize the fetch client."""
        logger.info("Initializing FetchClient")

        # Initialize adapters
        self.adapters = {YFinanceAdapter: YFinanceAdapter(), BuffettIndicatorAdapter: BuffettIndicatorAdapter()}

        # Initialize indicators
        self.indicators = self._initialize_indicators()

    def get_name(self) -> str:
        """Get the name of this client."""
        return "FetchClient"

    def run(self):
        """Run the fetch client independently."""
        logger.info("Running FetchClient independently")
        try:
            # Fetch data from all indicators
            market_data = []
            for indicator in self.indicators:
                try:
                    value = indicator.get_value()
                    data = MarketData(indicator_name=indicator.__class__.__name__, value=value, timestamp=datetime.now())
                    market_data.append(data)
                    logger.info(f"Fetched {indicator.__class__.__name__}: {value}")
                except Exception as e:
                    logger.error(f"Error fetching {indicator.__class__.__name__}: {str(e)}")
                    data = MarketData(
                        indicator_name=indicator.__class__.__name__, value=0.0, timestamp=datetime.now(), error=str(e)
                    )
                    market_data.append(data)

            logger.info(f"FetchClient completed. Fetched {len(market_data)} indicators.")
            return market_data

        except Exception as e:
            logger.error(f"Error in FetchClient run: {str(e)}")
            return []

    def _initialize_indicators(self) -> List:
        """Initialize all market indicators from registry."""
        initialized_indicators = []
        logger.info("\nInitializing indicators:")
        logger.info("-" * 80)

        for indicator_class in indicators:
            try:
                # Get the appropriate adapter for this indicator
                class_name = indicator_class.__name__
                logger.info(f"Initializing {class_name}...")

                adapter_class = indicator_to_adapter_registry.get(class_name)
                if adapter_class:
                    # Get or create adapter instance
                    adapter = self.adapters.get(adapter_class)
                    if not adapter:
                        logger.info(f"Creating new {adapter_class.__name__} instance")
                        adapter = adapter_class()
                        self.adapters[adapter_class] = adapter
                    else:
                        logger.info(f"Using existing {adapter_class.__name__} instance")

                    # Initialize indicator with adapter
                    indicator = indicator_class(adapter)
                    initialized_indicators.append(indicator)
                    logger.info(f"✓ Successfully initialized {class_name}")
                else:
                    logger.error(f"✗ No adapter found for {class_name}")

            except Exception as e:
                logger.error(f"✗ Failed to initialize {indicator_class.__name__}: {str(e)}")

        logger.info("-" * 80)
        logger.info(f"Initialized {len(initialized_indicators)} indicators:")
        for ind in initialized_indicators:
            logger.info(f"• {ind.__class__.__name__}")
        logger.info("")

        return initialized_indicators
