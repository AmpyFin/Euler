"""
Buffett Indicator (Market Cap / GDP) implementation.
"""
from ..indicator import Indicator

class BuffettIndicator(Indicator):
    """
    Warren Buffett's favorite market valuation metric - Total Market Cap / GDP.
    """
    
    def get_name(self) -> str:
        return "Buffett Indicator"
        
    def fetch_last_quote(self) -> float:
        """
        Fetches the current Buffett Indicator value.
        
        Returns:
            float: The current Market Cap / GDP ratio as a percentage
            
        Raises:
            ValueError: If the value cannot be fetched
        """
        return self.adapter.fetch_last_quote()
