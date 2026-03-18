from .base import BaseProvider
from typing import Dict, Any

class BinanceProvider(BaseProvider):
    def __init__(self, symbol: str = "btcusdt"):
        url = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@depth"
        super().__init__(symbol, url)

    async def _subscribe(self, websocket):
        pass

    def _normalize_message(self, data: Dict[str,Any]) -> Dict[str,Any]:
        if data.get("e") == "depthUpdate":
            binance_ts = float(data["E"]) / 1000.0 #latency tracking
            return {
                "exchange": "Binance",
                "symbol": data["s"],
                "bids": data["b"], # [price,qty] list
                "asks": data["a"], # [price,qty] list
                "exchange_timestamp": binance_ts,
                "timestamp": data["E"]
            }
        return None