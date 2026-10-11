import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from src.engine.backtester import Backtester
from src.engine.tracker import ExperimentTracker

from src.strategies.slow_train import SlowTrainStrategy
from src.strategies.patient_sniper import PatientSniperStrategy

print("Cargando datos históricos...")
close_prices = pd.read_csv('data/raw/stocks_close_15y.csv', index_col=0, parse_dates=True)
open_prices = pd.read_csv('data/raw/stocks_open_15y.csv', index_col=0, parse_dates=True)

# Usamos todos los valores del IBEX35 disponibles
market_df = pd.read_csv('data/raw/market_composition.csv')
ibex_tickers = market_df[market_df['Is_IBEX35'] == True]['Ticker'].tolist()
universe = [t for t in ibex_tickers if t in close_prices.columns]

# Limitamos a los ultimos 1500 dias para probar rápido
close_prices = close_prices[universe].tail(1500).ffill()
open_prices = open_prices[universe].tail(1500).ffill()

print("Inicializando Motor y Tracker...")
tracker = ExperimentTracker(exp_dir='experiments')
backtester = Backtester(data_close=close_prices, data_open=open_prices, window_size=22, step=11)

strategies = [
    SlowTrainStrategy(vol_window=20, mom_window=10, top_n_vol=5, order_amount=2500),
    PatientSniperStrategy(vol_window=60, rsi_window=14, rsi_threshold=40, base_amount=2500, snipe_amount=10000)
]

for strategy in strategies:
    print(f"\nInstanciando Estrategia: {strategy.name}...")
    results = backtester.run_strategy(strategy)

    print("="*40)
    print(f"RESULTADOS AGREGADOS {strategy.name}:")
    for k, v in results.items():
        if isinstance(v, float):
            print(f"{k}: {v:.4f}")
        else:
            print(f"{k}: {v}")
    print("="*40)

    tracker.log_experiment(
        strategy_name=strategy.name,
        metrics=results,
        metadata=strategy.get_metadata()
    )

print("\nHecho. Puedes ver el ranking final corriendo 'python scripts/evaluate_strategies.py'")
