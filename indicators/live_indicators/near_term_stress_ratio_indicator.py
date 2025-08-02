"""
Near-term Stress Ratio (^VIX9D/^VIX) Indicator implementation.
"""
from ..indicator import Indicator

class NearTermStressRatioIndicator(Indicator):
    """
    Near-term stress ratio indicator for tracking immediate market stress through VIX term structure.
    """
    
    def get_name(self) -> str:
        return "Near-term Stress Ratio"
        
    def fetch_last_quote(self) -> float:
        """
        Calculates the current near-term stress ratio (^VIX9D/^VIX).
        
        Returns:
            float: The current ratio value
            
        Raises:
            ValueError: If the component values cannot be fetched
        """
        # Get both VIX values
        vix9d = self.adapter.fetch_last_quote("^VIX9D")
        vix = self.adapter.fetch_last_quote("^VIX")
        
        # Calculate ratio
        if vix == 0:
            raise ValueError("VIX value is zero - cannot calculate ratio")
            
        return vix9d / vix