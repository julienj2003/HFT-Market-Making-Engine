import asyncio
from decimal import Decimal
from typing import Dict
import time
import csv

from providers.binance import BinanceProvider
from providers.coinbase import CoinbaseProvider
from providers.futures import BinanceFuturesProvider
from models.order_book import OrderBook
from models.inventory import InventoryManager
from strategy.fair_value import FairValueCalculator
from strategy.quoter import Quoter

class TradingEngine:
    def __init__(self):
        self.message_queue = asyncio.Queue()
        
        # Start long to see the skewed quoting mechanic
        self.inventory = InventoryManager(max_position=10.0)
        self.inventory.simulate_fill("sell", qty=2.5)
        
        self.order_books: Dict[str, OrderBook] = {
            "Binance": OrderBook("Binance"),
            "Coinbase": OrderBook("Coinbase"),
            "BinanceFutures": OrderBook("BinanceFutures") 
        }
        
        self.providers = [
            BinanceProvider(symbol="btcusdt"),
            CoinbaseProvider(symbol="BTC-USD"),
            BinanceFuturesProvider(symbol="btcusdt") 
        ]
        
        self.fv_calculator = FairValueCalculator()
        self.quoter = Quoter(base_spread=2.0, base_size=0.1)

        # Persistence: Initialize CSV Logger
        self.log_filename = f"session_log_{int(time.time())}.csv"
        self.log_file = open(self.log_filename, mode='w', newline='')
        self.csv_writer = csv.writer(self.log_file)
        self.csv_writer.writerow([
            "timestamp", "status", "spot_fv", "perp_price", 
            "fair_value", "basis_bps", "pos", "bid", "ask"
        ])

    async def _run_ingestion(self):
        """Start all providers concurrently"""
        tasks = [provider.connect(self.message_queue) for provider in self.providers]
        await asyncio.gather(*tasks)

    async def _process_messages(self):
        """Routes messages from the queue to the correct orderbook."""
        while True:
            msg = await self.message_queue.get()

            # Latency tracking
            if "exchange_timestamp" in msg and "local_timestamp" in msg:
                net_latency = (msg["local_timestamp"] - msg["exchange_timestamp"]) * 1000
                proc_latency = (time.time() - msg["local_timestamp"]) * 1000
                # print(f"DEBUG: {msg['exchange']} Net: {net_latency:.2f}ms | Proc: {proc_latency:.2f}ms")

            exchange = msg["exchange"]
            if exchange in self.order_books:
                book = self.order_books[exchange]
                if msg.get("type") == "snapshot":
                    book.apply_snapshot(msg["bids"], msg["asks"])
                else:
                    for side in ["bids", "asks"]:
                        for price, size in msg[side]:
                            book.update_level(side[:-1], price, size)

                self.fv_calculator.update_book(exchange, book)
            
            self.message_queue.task_done()

    async def _output_loop(self):
        """Emission every 500ms with simulated fill detection."""
        try:
            while True:
                await asyncio.sleep(0.5)
                fv_result = self.fv_calculator.calculate()
                fv = fv_result['fair_value']
                perp_p = fv_result.get('perp_price')
                spot_fv = fv_result.get('spot_fv')
            
                if not fv or not spot_fv or not perp_p or fv <= 0 or spot_fv <= 0 or perp_p <= 0:
                    print("STATUS: SUSPENDED // POSITION: 0.0 BTC")
                    continue

                current_position = self.inventory.get_position()
                quote = self.quoter.generate_quote(fv_result, current_position)

                self.csv_writer.writerow([
                        time.time(),
                        fv_result['status'],
                        fv_result.get('spot_fv', 0),
                        perp_p,
                        fv,
                        fv_result.get('basis_bps', 0),
                        current_position,
                        quote.get('bid_price', 0),
                        quote.get('ask_price', 0)
                    ])
                self.log_file.flush()

                # Simulated inventory fill logic
                if quote['ask_price'] and fv >= quote['ask_price']:
                    self.inventory.simulate_fill("sell", qty=0.1)
            
                elif quote['bid_price'] and fv <= quote['bid_price']:
                    self.inventory.simulate_fill("buy", qty=0.1)

                # Re-fetch position in case it changed due to a fill
                current_position = self.inventory.get_position()

                print(f"STATUS: {fv_result['status']} // POSITION: {current_position} BTC ---")
                print(f"SPOT FV: {fv_result['spot_fv']:.2f} | PERP: {perp_p} | BASIS: {fv_result['basis_bps']:.2f} bps")
                print(f"FAIR VALUE: {fv}")
                if quote['bid_price']:
                    print(f"QUOTE: BID {quote['bid_price']} at {quote['bid_size']} | "
                        f"ASK {quote['ask_price']} at {quote['ask_size']}")
                else:
                    print("QUOTE: SUSPENDED")
        except asyncio.CancelledError:
            self.log_file.close()

    async def run(self):
        print("INFO Starting Trading Engine...")
        await asyncio.gather(
            self._run_ingestion(),
            self._process_messages(),
            self._output_loop()
        )