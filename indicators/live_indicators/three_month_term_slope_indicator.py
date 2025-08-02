"""
3-Month Term Slope (^VIX/^VIX3M) Indicator implementation.
"""
from ..indicator import Indicator

class ThreeMonthTermSlopeIndicator(Indicator):
    """
    3-month term slope indicator for tracking medium-term market stress through VIX term structure.
    """
    
    def get_name(self) -> str:
        return "3M Term Slope"
        
    def fetch_last_quote(self) -> float:
        """
        Calculates the current 3-month term slope (^VIX/^VIX3M).
        
        Returns:
            float: The current ratio value
            
        Raises:
            ValueError: If the component values cannot be fetched
        """
        # Get both VIX values
        vix = self.adapter.fetch_last_quote("^VIX")
        vix3m = self.adapter.fetch_last_quote("^VIX3M")
        
        # Calculate ratio
        if vix3m == 0:
            raise ValueError("VIX3M value is zero - cannot calculate ratio")
            
        return vix / vix3m
