import asyncio
import sys
from engine import TradingEngine

async def main():
    engine = TradingEngine()
    test_duration = 15.0
    print(f"INFO Starting for a {test_duration} seconds test run...")
    try:
        await asyncio.wait_for(engine.run(), timeout = test_duration)
    except asyncio.TimeoutError:
        print(f"\n INFO Test completed successfully after {test_duration}s.")
    except KeyboardInterrupt:
        print("\nINFO Closing connections...")
    except Exception as e:
        print(f"\n ERROR in engine: {e}")
    finally:
        print("INFO System offline.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
