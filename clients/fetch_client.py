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
from registries.indicator_registry import (
    get_enabled_indicators,
    get_active_provider,
    get_indicator_factory
)


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
                    value = indicator.fetch_last_quote()
                    data = MarketData(indicator_name=indicator.get_name(), value=value, timestamp=datetime.now())
                    market_data.append(data)
                    logger.info(f"Fetched {indicator.get_name()}: {value}")
                except Exception as e:
                    logger.error(f"Error fetching {indicator.get_name()}: {str(e)}")
                    data = MarketData(
                        indicator_name=indicator.get_name(), value=0.0, timestamp=datetime.now(), error=str(e)
                    )
                    market_data.append(data)

            logger.info(f"FetchClient completed. Fetched {len(market_data)} indicators.")
            return market_data

        except Exception as e:
            logger.error(f"Error in FetchClient run: {str(e)}")
            return []

    def _initialize_indicators(self) -> List:
        """Initialize all enabled risk indicators from registry."""
        initialized_indicators = []
        logger.info("\nInitializing risk indicators:")
        logger.info("-" * 80)

        enabled_indicators = get_enabled_indicators()
        
        for metric_name in enabled_indicators:
            try:
                logger.info(f"Initializing {metric_name}...")

                # Get the active provider for this metric
                adapter = get_active_provider(metric_name)
                logger.info(f"Using provider: {adapter.__class__.__name__}")

                # Get the indicator factory and create indicator class
                indicator_factory = get_indicator_factory(metric_name)
                indicator_class = indicator_factory()
                
                # Initialize indicator with adapter
                indicator = indicator_class(adapter)
                initialized_indicators.append(indicator)
                logger.info(f"✓ Successfully initialized {metric_name}")

            except Exception as e:
                logger.error(f"✗ Failed to initialize {metric_name}: {str(e)}")

        logger.info("-" * 80)
        logger.info(f"Initialized {len(initialized_indicators)} risk indicators:")
        for ind in initialized_indicators:
            logger.info(f"• {ind.get_name()}")
        logger.info("")

        return initialized_indicators
