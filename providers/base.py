import asyncio
import time
import json
import abc
import websockets
from typing import Dict, Any

class BaseProvider(abc.ABC):
    """Abstract Base class for all exchange websocket providers"""

    def __init__(self, symbol : str, stream_url: str):
        self.symbol = symbol
        self.stream_url = stream_url
        self.is_running = False

    async def connect(self, message_queue: asyncio.Queue):
        """Websocket connections and handle the messages"""
        self.is_running = True
        while self.is_running:
            try:
                async with websockets.connect(self.stream_url, max_size = None) as websocket:
                    print(f"Coonected to {self.__class__.__name__}")
                    await self._subscribe(websocket)

                    async for message in websocket:
                        arrival_time = time.time()
                        data = json.loads(message)
                        normalized = self._normalize_message(data)
                        if normalized:
                            normalized["local_timestamp"] = arrival_time #latency tracking
                            await message_queue.put(normalized)
                    
            except Exception as e:
                print(f"ERROR {self.__class__.__name__} Disconnected: {e}. Retrying in few seconds.")
                await asyncio.sleep(5)

    @abc.abstractmethod
    async def _subscribe(self,websocket):
        """Send subscription to the exchange (if required)."""
        pass

    @abc.abstractmethod
    def _normalize_message(self, data: Dict[str,Any]) -> Dict[str,Any]:
        """Convert into a standard dict."""
        pass


