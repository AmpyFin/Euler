"""
SKEW (^SKEW) Indicator implementation.
"""
from ..indicator import Indicator

class SKEWIndicator(Indicator):
    """
    CBOE SKEW index for tracking tail risk pricing.
    """
    
    def get_name(self) -> str:
        return "^SKEW"
        
    def fetch_last_quote(self) -> float:
        """
        Fetches the current SKEW value.
        
        Returns:
            float: The current SKEW level
            
        Raises:
            ValueError: If the value cannot be fetched
        """
        return self.adapter.fetch_last_quote("^SKEW")
