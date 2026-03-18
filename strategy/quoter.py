from decimal import Decimal
from typing import Dict, Optional

class Quoter:
    def __init__(self, base_spread: float = 2.0, base_size: float = 0.1, risk_gamma: float = 5.0):
        self.base_spread = Decimal(str(base_spread))
        self.base_size = Decimal(str(base_size))
        self.risk_gamma = Decimal(str(risk_gamma))

    def generate_quote(self, fv_result: Dict, inventory_btc: Decimal) -> Dict:
        """From Fair value and Inventory, it outputs recommended quotes for a market maker.
        It is risk adjusted quote, with risk_gamma param that indicates how to move the price when inventory
        is non zero (inventory risk)."""

        fv = fv_result.get("fair_value")
        status = fv_result.get("status", "SUSPENDED")

        if status == "SUSPENDED" or fv is None:
            return self._empty_quote("SUSPENDED")
        
        offset = inventory_btc * self.risk_gamma
        current_spread = self.base_spread
        if status == "DEGRADED":
            current_spread *= 2
        
        skewed_mid = fv - offset
        bid_price = skewed_mid - (current_spread /2)
        ask_price = skewed_mid + (current_spread /2)
        bid_size = self.base_size
        ask_size = self.base_size

        return {
            "bid_price": bid_price.quantize(Decimal("0.01")),
            "bid_size": bid_size,
            "ask_price": ask_price.quantize(Decimal("0.01")),
            "ask_size": ask_size,
            "quote_status": "ACTIVE" if status == "NORMAL" else "DEGRADED"
        }
    
    def _empty_quote(self, status: str) -> Dict:
        return {
            "bid_price": None,
            "bid_size": None,
            "ask_price": None,
            "ask_size": None,
            "quote_status": status
        }

