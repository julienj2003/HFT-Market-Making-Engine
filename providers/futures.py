import asyncio
import json
import websockets
import time
from decimal import Decimal

class BinanceFuturesProvider:
    def __init__(self, symbol: str = "btcusdt"):
        self.symbol = symbol.lower()
        self.url = f"wss://fstream.binance.com/ws/{self.symbol}@bookTicker"
        self.exchange_name = "BinanceFutures"

    async def connect(self, queue: asyncio.Queue):
        """Connects to Binance Futures and streams top-of-book prices."""
        while True:
            try:
                async with websockets.connect(self.url) as ws:
                    print(f"Connected to {self.exchange_name} (Perp)")
                    while True:
                        data = json.loads(await ws.recv())
                        local_ts = time.time()
                        msg = {
                            "exchange": self.exchange_name,
                            "type": "snapshot", # Simplified as we only need the best bid/ask
                            "local_timestamp": local_ts,
                            "bids": [[Decimal(data['b']), Decimal(data['B'])]],
                            "asks": [[Decimal(data['a']), Decimal(data['A'])]]
                        }
                        
                        await queue.put(msg)
                        
            except Exception as e:
                print(f"{self.exchange_name} Connection Error: {e}. Retrying in 5s...")
                await asyncio.sleep(5)