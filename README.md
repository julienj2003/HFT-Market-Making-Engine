# HFT-Market-Making-Engine
HFT engine designed for the BTC/USDT pair, utilizing multi-venue price discovery (Binance and Coinbase Spot &amp; Binance Perps) and automated inventory risk management.

## 📖 Project Overview

The engine connects to Binance Perpetuals and Coinbase Spot via WebSockets. It acknowledges that price discovery often happens first in the futures market (Lead) before reflecting in spot markets (Lag). By synthesizing these feeds, the engine calculates a "Consolidated Fair Value" and places Bid/Ask quotes around it. To manage risk, the engine dynamically skews its quotes based on its current inventory ($q$) to ensure it always returns to a neutral position.

## 📂 File Architecture & Roles

The project is organized into modular components to ensure separation of concerns between data ingestion, mathematical logic, and order execution.

### 📍 Root Directory

main.py: The entry point of the application. It initializes the TradingEngine, manages the asynchronous event loop, and handles graceful shutdowns.

requirements.txt: Lists all Python dependencies (WebSockets, Pandas, Matplotlib) required to run the engine.

.gitignore: Prevents environment-specific files (like venv/) and local temporary logs from being committed to the repository.

### 🏗️ Source Code

engine.py: The "brain" of the project. It coordinates data flow between providers and the strategy, maintains the heartbeat loop, and logs telemetry.

providers/: Contains the WebSocket handlers for Binance and Coinbase. These classes manage connection persistence and normalize raw JSON data into internal OrderBook objects.

models/: Defines the core data structures, such as the OrderBook (for tracking liquidity) and the InventoryManager (for tracking positions and calculating PnL).

```text strategy/fair_value.py```: Implements the Lead-Lag algorithm to compute the consolidated price.

strategy/quoter.py: Calculates the actual Bid and Ask prices using the $\pm \lambda \cdot q$ skewing logic.

## 🚀 Quick Start

### One-Command Setup & Run

Run the following command in your terminal to create the environment, install dependencies, and start the engine:

Linux / macOS:
```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python main.py
```

Windows (PowerShell):
```bash
python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt; python main.py
```

### Generating Plots

After running the engine and generating a log file, you can visualize the inventory rebalancing by running:

```bash
python results_plot.py
```


## 📊 Empirical Validation

The engine's ability to "mean-revert" inventory is visualized in the included plots:

Short Run (-2.5 BTC): Demonstrates Bid-skewing to buy back short exposure.

Long Run (+2.5 BTC): Demonstrates Ask-skewing to liquidate long exposure.

