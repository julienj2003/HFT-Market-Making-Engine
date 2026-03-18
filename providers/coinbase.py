import json
from .base import BaseProvider
from typing import Dict, Any, Optional
from datetime import datetime

class CoinbaseProvider(BaseProvider):
    def __init__(self, symbol: str = "BTC-USD"):
        url = "wss://advanced-trade-ws.coinbase.com"
        super().__init__(symbol, url)

    async def _subscribe(self, websocket):
        subscribe_msg = {
            "type": "subscribe",
            "product_ids": [self.symbol],
            "channel": "level2"
        }
        await websocket.send(json.dumps(subscribe_msg))

    def _normalize_message(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:

        if data.get("channel") != "l2_data":
            return None

        events = data.get("events", [])
        for event in events:
            event_type = event.get("type")
            if event_type not in ["snapshot", "update"]:
                continue

            product_id = event.get("product_id")
            updates = event.get("updates", [])
            bids = []
            asks = []
            for u in updates:
                price = u.get("price_level")
                quantity = u.get("new_quantity")
                
                if u["side"] == "bid":
                    bids.append([price, quantity])
                else:
                    asks.append([price, quantity])

            if bids or asks:
                timestamp_coinbase = data.get("timestamp")
                coinbase_ts = datetime.fromisoformat(timestamp_coinbase.replace("Z", "+00:00")).timestamp()
                return {
                    "exchange": "Coinbase",
                    "symbol": product_id,
                    "type": event_type, 
                    "bids": bids,
                    "asks": asks,
                    "exchange_timestamp": coinbase_ts, #latency tracking
                    "timestamp": timestamp_coinbase
                }
        return None
        