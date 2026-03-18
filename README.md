# HFT-Market-Making-Engine
HFT engine designed for the BTC/USDT pair, utilizing multi-venue price discovery (Binance and Coinbase Spot &amp; Binance Perps) and automated inventory risk management.

## 📖 Project Overview

The engine connects to Binance Perpetuals and Coinbase Spot via WebSockets. It acknowledges that price discovery often happens first in the futures market (Lead) before reflecting in spot markets (Lag). By synthesizing these feeds, the engine calculates a Consolidated Fair Value and places Bid/Ask quotes around it. To manage risk, the engine dynamically skews its quotes based on its current inventory ($q$) to ensure it always returns to a neutral position.

## 📂 File Architecture & Roles

- ```Design Note```: The report of the project with explanations and plots from live runs

- ```main.py```: The entry point of the application. It initializes the TradingEngine, manages the asynchronous event loop, and handles graceful shutdowns.

- ```engine.py```: The "brain" of the project. It coordinates data flow between providers and the strategy, maintains the heartbeat loop, and logs telemetry.

- ```providers/```: Contains the WebSocket handlers for Binance and Coinbase. These classes manage connection persistence and normalize raw JSON data into internal OrderBook objects.

- ```models/```: Defines the core data structures, such as the OrderBook (for tracking liquidity) and the InventoryManager (for tracking positions and calculating PnL).

- ```strategy/fair_value.py```: Implements the Lead-Lag algorithm to compute the consolidated price.

- ```strategy/quoter.py```: Calculates the actual Bid and Ask prices using the $\pm \lambda \cdot q$ skewing logic.

## 🚀 Quick Start

### One-Command Setup & Run

Run the following command in your terminal to clone the repo, create the environment, install dependencies, and start the engine:

- Clone the repository:

```bash
git clone https://github.com/julienj2003/HFT-Market-Making-Engine.git
cd HFT-Market-Making-Engine
```

- Environment Setup & Execution
Linux / macOS:
```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python main.py
```

Windows (PowerShell):
```bash
python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt; python main.py
```

- Generate Plots

After running the engine and generating a log file, you can visualize the inventory rebalancing by running:

```bash
python results_plot.py
```


## 📊 Empirical Validation

The engine's ability to "mean-revert" inventory is visualized in the included plots:

- Short Run (-2.5 BTC): Demonstrates Bid-skewing to buy back short exposure.

- Long Run (+2.5 BTC): Demonstrates Ask-skewing to liquidate long exposure.

## 🖥️ Sample Terminal Output
When the engine is running, you will see a real-time telemetry stream. The example below shows a sample from a live run:

```text
[FILL] Simulated SELL of 1.5 BTC // New Position: -1.5
INFO Starting for a 10.0 seconds test run...
INFO Starting Trading Engine...
STATUS: SUSPENDED // POSITION: 0.0 BTC
Coonected to CoinbaseProvider
Connected to BinanceFutures (Perp)
[FILL] Simulated BUY of 0.1 BTC // New Position: -1.4
STATUS: DEGRADED // POSITION: -1.4 BTC ---
SPOT FV: 0.00 | PERP: 74362.68 | BASIS: 0.00 bps
FAIR VALUE: 74362.68
QUOTE: BID 74368.18 at 0.1 | ASK 74372.18 at 0.1
Coonected to BinanceProvider
[FILL] Simulated BUY of 0.1 BTC // New Position: -1.3
STATUS: DEGRADED // POSITION: -1.3 BTC ---
SPOT FV: 0.00 | PERP: 74362.67 | BASIS: 0.00 bps
FAIR VALUE: 74362.67
QUOTE: BID 74367.67 at 0.1 | ASK 74371.67 at 0.1
[FILL] Simulated BUY of 0.1 BTC // New Position: -1.2
STATUS: DEGRADED // POSITION: -1.2 BTC ---
SPOT FV: 74433.36 | PERP: 74362.65 | BASIS: -9.50 bps
FAIR VALUE: 74412.15
QUOTE: BID 74416.65 at 0.1 | ASK 74420.65 at 0.1
[FILL] Simulated BUY of 0.1 BTC // New Position: -1.1
STATUS: NORMAL // POSITION: -1.1 BTC ---
SPOT FV: 74404.91 | PERP: 74362.65 | BASIS: -5.68 bps
FAIR VALUE: 74392.23
QUOTE: BID 74397.23 at 0.1 | ASK 74399.23 at 0.1
[FILL] Simulated BUY of 0.1 BTC // New Position: -1.0
....
 INFO Test completed successfully after 10.0s.
INFO System offline.
```

