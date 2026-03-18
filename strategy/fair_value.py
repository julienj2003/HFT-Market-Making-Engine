import time
from decimal import Decimal
from typing import Dict, Optional, List
from models.order_book import OrderBook

class FairValueCalculator:
    def __init__(self, staleness_threshold: float = 2.0):
        self.books: Dict[str, OrderBook] = {}
        self.staleness_threshold = staleness_threshold
        self.last_update_times: Dict[str, float] = {}
        
        # Hyperparameters for Lead-Lag
        self.perp_weight = Decimal("0.30")  # 30% weight to the Future signal
        self.spot_weight = Decimal("0.70")  # 70% weight to the Spot consensus

    def update_book(self, exchange_id: str, book: OrderBook):
        self.books[exchange_id] = book
        self.last_update_times[exchange_id] = time.time()

    def _get_micro_price(self, book: OrderBook) -> Optional[Decimal]:
        """Calculate the micro price (taking into account Imbalance)"""
        (bid_price, bid_size), (ask_price, ask_size) = book.get_best_bid_ask()

        if not bid_price or not ask_price or (bid_size + ask_size) == 0:
            return None
        return (bid_price * ask_size + ask_price * bid_size) / (bid_size + ask_size) 
    
    def _get_spot_weights(self) -> Dict[str, Decimal]:
        """Calculates weights only for spot exchanges (Binance, Coinbase)."""
        now = time.time()
        liquidity_map = {}
        total_liquidity = Decimal("0")

        #Spot exchanges for the liquidity-weighted core
        spot_exchanges = ["Binance", "Coinbase"]

        for ex_id in spot_exchanges:
            if ex_id not in self.books:
                continue
                
            age = time.time() - self.last_update_times.get(ex_id, 0)
            if age < self.staleness_threshold:
                book = self.books[ex_id]
                (bid_p, bid_s), (ask_p, ask_s) = book.get_best_bid_ask()
                if bid_s and ask_s:
                    lq = bid_s + ask_s
                    liquidity_map[ex_id] = lq
                    total_liquidity += lq
        
        if total_liquidity == 0:
            return {}
        
        return {ex_id: lq / total_liquidity for ex_id, lq in liquidity_map.items()}
    
    def calculate(self) -> Dict:
        """Compute the Basis-Adjusted Fair Value using Spot and Perps."""
        #Calculate Spot Consensus
        spot_weights = self._get_spot_weights()
        spot_fv = Decimal("0")
        active_spot_sources = []

        for ex_id, weight in spot_weights.items():
            micro = self._get_micro_price(self.books[ex_id])
            if micro:
                spot_fv += micro * weight
                active_spot_sources.append(ex_id)

        #Get Perp Signal
        perp_price = None
        if "BinanceFutures" in self.books:
            age = time.time() - self.last_update_times.get("BinanceFutures", 0)
            if age < self.staleness_threshold:
                perp_price = self._get_micro_price(self.books["BinanceFutures"])

        #Combine Spot and Perp
        if spot_fv > 0 and perp_price:
            final_fv = (spot_fv * self.spot_weight) + (perp_price * self.perp_weight)
            status = "NORMAL" if len(active_spot_sources) >= 2 else "DEGRADED"
            basis_bps = ((perp_price - spot_fv) / spot_fv) * 10000
        elif spot_fv > 0:
            final_fv = spot_fv
            status = "DEGRADED"
            basis_bps = Decimal("0")
        elif perp_price:
            final_fv = perp_price
            status = "DEGRADED"
            basis_bps = Decimal("0")
        else:
            final_fv = None
            status = "SUSPENDED"
            basis_bps = Decimal("0")

        # In case perp and fair value are very far from each other.
        if basis_bps.copy_abs() > 15:
            print(f"LARGE BASIS ALERT: {basis_bps:.2f} bps | Perp: {perp_price} Spot: {spot_fv}")

        return {
            "fair_value": final_fv.quantize(Decimal("0.01")) if final_fv else None,
            "status": status,
            "active_sources": active_spot_sources + (["BinanceFutures"] if perp_price else []),
            "basis_bps": basis_bps,
            "spot_fv": spot_fv,
            "perp_price": perp_price.quantize(Decimal("0.01")) if perp_price else None
        }