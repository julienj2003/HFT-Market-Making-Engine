import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

def generate_charts():
    list_of_files = glob.glob('session_log_*.csv')
    if not list_of_files:
        print("No log files found.")
        return
    latest_file = max(list_of_files, key=os.path.getctime)
    print(f"Analyzing {latest_file}...")

    df = pd.read_csv(latest_file)
    df['elapsed'] = df['timestamp'] - df['timestamp'].iloc[0]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    plt.subplots_adjust(hspace=0.2)

    # Chart 1: Price Evolution
    ax1.plot(df['elapsed'], df['spot_fv'], label='Spot FV', color='#3498db', alpha=0.5)
    ax1.plot(df['elapsed'], df['perp_price'], label='Perp Price', color='#e67e22', linestyle='--')
    ax1.plot(df['elapsed'], df['fair_value'], label='Combined Fair Value', color='black', linewidth=1.5)
    
    ax1.set_title("Price Evolution & Lead-Lag Convergence", fontweight='bold')
    ax1.set_ylabel("Price (USD)")
    ax1.legend(loc='upper right')
    ax1.grid(True, linestyle=':', alpha=0.6)

    # Chart 2: Inventory Evolution
    ax2.fill_between(df['elapsed'], df['pos'], color='#2ecc71', alpha=0.2)
    ax2.plot(df['elapsed'], df['pos'], color='#27ae60', label='BTC Inventory')
    ax2.axhline(0, color='red', linewidth=0.8, linestyle='--')
    
    ax2.set_title("Inventory Mean Reversion (Skew Efficacy)", fontweight='bold')
    ax2.set_ylabel("Position (BTC)")
    ax2.set_xlabel("Seconds Elapsed")
    ax2.legend(loc='upper right')
    ax2.grid(True, linestyle=':', alpha=0.6)

    # Save to file
    output_name = "strategy_results.png"
    plt.savefig(output_name, dpi=300, bbox_inches='tight')
    print(f"Charts saved as {output_name}")
    plt.show()

if __name__ == "__main__":
    generate_charts()