"""
VIX 3-Month (^VIX3M) Indicator implementation.
"""
from ..indicator import Indicator

class VIX3MIndicator(Indicator):
    """
    3-month VIX indicator for tracking medium-term volatility expectations.
    """
    
    def get_name(self) -> str:
        return "^VIX3M"
        
    def fetch_last_quote(self) -> float:
        """
        Fetches the current 3-month VIX value.
        
        Returns:
            float: The current 3-month VIX level
            
        Raises:
            ValueError: If the value cannot be fetched
        """
        return self.adapter.fetch_last_quote("^VIX3M")
