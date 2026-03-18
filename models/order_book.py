from decimal import Decimal
from sortedcontainers import SortedDict
from typing import Dict, List, Tuple

class OrderBook: 
    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name
        self._bids = SortedDict() # Highest bid first
        self._asks = SortedDict() # Lowest asks first
        self.last_update_id = None
        self.timestamp = None

    def apply_snapshot(self, bids: List[List[str]], asks: List[List[str]], update_id: int = None):
        """Reset the book with snapshot received."""
        self._bids.clear()
        self._asks.clear()
        self.last_update_id = update_id

        for price, size in bids:
            self.update_level("bid", price, size)
        for price, size in asks:
            self.update_level("ask", price, size)
    
    def update_level(self, side: str, price: str, size: str):
        """Update the price level (or remove it)."""

        price_dec = Decimal(price)
        size_dec = Decimal(size)

        target_dict = self._bids if side == "bid" else self._asks
        key = -price_dec if side == "bid" else price_dec

        if size_dec == 0:
            target_dict.pop(key, None)
        else :
            target_dict[key] = size_dec

    def get_best_bid_ask(self) -> Tuple[Tuple[Decimal, Decimal], Tuple[Decimal, Decimal]]:
        """Return ((best_bid_price, size), (best_ask_price, size))"""
        best_bid = (None,None)
        best_ask = (None, None)
        
        if self._bids:
            price_key, size = self._bids.peekitem(0)
            best_bid = (-price_key, size)

        if self._asks:
            best_ask = self._asks.peekitem(0)

        return best_bid, best_ask
    
    def get_mid_price(self) -> Decimal:
        bid, ask = self.get_best_bid_ask()
        if bid[0] and ask[0]:
            return (bid[0] + ask[0]) / 2
        return None
