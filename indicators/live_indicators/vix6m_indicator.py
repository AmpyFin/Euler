"""
VIX 6-Month (^VIX6M) Indicator implementation.
"""
from ..indicator import Indicator

class VIX6MIndicator(Indicator):
    """
    6-month VIX indicator for tracking long-term volatility expectations.
    """
    
    def get_name(self) -> str:
        return "^VIX6M"
        
    def fetch_last_quote(self) -> float:
        """
        Fetches the current 6-month VIX value.
        
        Returns:
            float: The current 6-month VIX level
            
        Raises:
            ValueError: If the value cannot be fetched
        """
        return self.adapter.fetch_last_quote("^VIX6M")
