
"""
Adapter for fetching Buffett Indicator data.
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
import yfinance as yf
import requests

from .adapter import Adapter

class BuffettIndicatorAdapter(Adapter):
    """Adapter for fetching Buffett Indicator (Market Cap / GDP) data."""
    
    def __init__(self):
        """Initialize the adapter."""
        self.wilshire_index = "^W5000"  # Wilshire 5000 Total Market Index
        
    def fetch_last_quote(self, index: Optional[str] = None) -> float:
        """
        Fetch the latest Buffett Indicator value.
        
        Returns:
            float: The latest Buffett Indicator value (Market Cap / GDP * 100)
            
        Raises:
            ValueError: If the data cannot be fetched or is invalid
        """
        try:
            # Get Wilshire 5000 data (proxy for total market cap)
            ticker = yf.Ticker(self.wilshire_index)
            market_data = ticker.history(period="1d")
            if market_data.empty:
                raise ValueError("No market cap data available")
            
            market_cap = float(market_data['Close'].iloc[-1])
            
            # For demo purposes, using a fixed GDP value
            # In production, this should fetch the latest GDP data from a reliable source
            gdp = 25460  # Latest US GDP in billions (Q2 2023)
            
            # Calculate Buffett Indicator (Market Cap / GDP * 100)
            buffett_indicator = (market_cap / gdp) * 100
            
            return buffett_indicator
            
        except Exception as e:
            raise ValueError(f"Failed to calculate Buffett Indicator: {str(e)}")
    
    def fetch_last_quote_with_date(self, index: Optional[str] = None) -> Tuple[float, datetime]:
        """
        Fetch the latest Buffett Indicator value with timestamp.
        
        Returns:
            Tuple[float, datetime]: The indicator value and timestamp
            
        Raises:
            ValueError: If the data cannot be fetched or is invalid
        """
        try:
            value = self.fetch_last_quote()
            return value, datetime.now()
        except Exception as e:
            raise ValueError(f"Failed to fetch Buffett Indicator with date: {str(e)}")
    
    def fetch_historical_data(self, index: Optional[str] = None, days: int = 30) -> Dict[datetime, float]:
        """
        Fetch historical Buffett Indicator data.
        
        Args:
            days (int): Number of days of historical data to fetch
            
        Returns:
            Dict[datetime, float]: Historical data as date-value pairs
            
        Raises:
            ValueError: If the data cannot be fetched or is invalid
        """
        try:
            # Get Wilshire 5000 historical data
            ticker = yf.Ticker(self.wilshire_index)
            market_data = ticker.history(period=f"{days}d")
            if market_data.empty:
                raise ValueError("No historical market cap data available")
            
            # For demo purposes, using a fixed GDP value
            gdp = 25460  # Latest US GDP in billions (Q2 2023)
            
            # Calculate historical Buffett Indicator values
            historical_data = {}
            for date, row in market_data.iterrows():
                market_cap = float(row['Close'])
                buffett_indicator = (market_cap / gdp) * 100
                historical_data[date.to_pydatetime()] = buffett_indicator
            
            return historical_data
            
        except Exception as e:
            raise ValueError(f"Failed to fetch historical Buffett Indicator data: {str(e)}")