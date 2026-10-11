import sys
import os
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.backtester import Backtester
from src.analysis.evaluator import Evaluator

from src.strategies.bare_minimum import BareMinimumStrategy
from src.strategies.smart_minimum_seasonal import SmartMinimumSeasonal
from src.strategies.smart_minimum_contrarian import SmartMinimumContrarian
from src.strategies.cross_sectional_reversion import CrossSectionalReversion
from src.strategies.nr10_breakout import NR10Breakout

print("Cargando datos históricos completos (Open, High, Low, Close)...")
close_prices = pd.read_csv('data/raw/stocks_close_15y.csv', index_col=0, parse_dates=True)
open_prices = pd.read_csv('data/raw/stocks_open_15y.csv', index_col=0, parse_dates=True)
high_prices = pd.read_csv('data/raw/stocks_high_15y.csv', index_col=0, parse_dates=True)
low_prices = pd.read_csv('data/raw/stocks_low_15y.csv', index_col=0, parse_dates=True)

market_df = pd.read_csv('data/raw/market_composition.csv')
ibex_tickers = market_df[market_df['Is_IBEX35'] == True]['Ticker'].tolist()
universe = [t for t in ibex_tickers if t in close_prices.columns]

close_prices = close_prices[universe].tail(1500).ffill()
open_prices = open_prices[universe].tail(1500).ffill()
high_prices = high_prices[universe].tail(1500).ffill()
low_prices = low_prices[universe].tail(1500).ffill()

backtester = Backtester(
    data_close=close_prices, 
    data_open=open_prices, 
    data_high=high_prices, 
    data_low=low_prices, 
    window_size=22, 
    step=11
)

strategies = [
    CrossSectionalReversion(order_amount=4667.0),
    NR10Breakout(order_amount=4667.0),
    SmartMinimumSeasonal(trade_amount=4667.0),
    SmartMinimumContrarian(trade_amount=4667.0),
    BareMinimumStrategy()
]

print("Ejecutando backtests de estrategias candidatas...")
raw_results = {}
for s in strategies:
    print(f"  -> Ejecutando {s.name}...")
    df_raw = backtester.run_strategy(s, return_raw=True)
    if not df_raw.empty:
        raw_results[s.name] = df_raw
    else:
        print(f"     [AVISO] {s.name} no generó resultados.")

print("Cargando competidores sintéticos para Torneo Global...")
Evaluator.load_competitors()
comp_df = Evaluator._competitors_df

ref_name = list(raw_results.keys())[0]
ref_df = raw_results[ref_name]

tournament_results = []

for idx, row in ref_df.iterrows():
    window_start = row['window_start']
    window_end = row['window_end']
    
    participants = []
    
    for s_name, s_df in raw_results.items():
        s_row = s_df[(s_df['window_start'] == window_start) & (s_df['window_end'] == window_end)]
        if len(s_row) > 0:
            s_row = s_row.iloc[0]
            if s_row['Qualified']:
                participants.append({'name': s_name, 'ret': s_row['Return_1M'], 'vol': s_row['Vol_Ann']})
            else:
                participants.append({'name': s_name, 'ret': 0.0, 'vol': 0.0, 'disqualified': True})
                
    dates = close_prices.loc[window_start:window_end].index
    valid_dates = [d for d in dates if d in comp_df.index]
    if len(valid_dates) > 0:
        comp_slice = comp_df.loc[valid_dates]
        for col in comp_slice.columns:
            daily_rets = comp_slice[col].dropna()
            if len(daily_rets) > 0:
                ret = np.prod(1 + daily_rets) - 1
                vol = daily_rets.std() * np.sqrt(252)
                participants.append({'name': col, 'ret': ret, 'vol': vol})
                
    valid_participants = [p for p in participants if not p.get('disqualified', False)]
    for p in valid_participants: 
        p['final_val'] = 50000 * (1 + p['ret'])
    if not valid_participants: 
        continue
    
    max_val = max([p['final_val'] for p in valid_participants])
    for p in valid_participants: 
        p['ret_points'] = (p['final_val'] * 6) / max_val
    
    min_vol = min([p['vol'] for p in valid_participants])
    max_vol = max([p['vol'] for p in valid_participants])
    
    if min_vol == max_vol:
        for p in valid_participants:
            p['vol_points'] = 3.0
            p['total_points'] = p['ret_points'] + p['vol_points']
    else:
        for p in valid_participants:
            p['vol_points'] = 3 * (1 - (p['vol'] - min_vol) / (max_vol - min_vol))
            p['total_points'] = p['ret_points'] + p['vol_points']
            
    valid_participants = sorted(valid_participants, key=lambda x: x['total_points'], reverse=True)
    for i, p in enumerate(valid_participants):
        tournament_results.append({
            'Window_End': window_end,
            'Name': p['name'],
            'Score': p['total_points'],
            'Rank': i + 1,
            'Return_1M': p['ret'],
            'Vol_Ann': p['vol']
        })

tournament_df = pd.DataFrame(tournament_results)

summary = []
for name in tournament_df['Name'].unique():
    sub_df = tournament_df[tournament_df['Name'] == name]
    score_avg = sub_df['Score'].mean()
    rank_avg = sub_df['Rank'].mean()
    win_rate = (sub_df['Rank'] == 1).mean()
    ret_avg = sub_df['Return_1M'].mean()
    vol_avg = sub_df['Vol_Ann'].mean()
    
    summary.append({
        'Participant': name,
        'Score_Avg': score_avg,
        'Avg_Rank': rank_avg,
        'Win_Rate_Global': win_rate,
        'Return_1M_Avg': ret_avg,
        'Vol_Ann_Avg': vol_avg
    })

sum_df = pd.DataFrame(summary).sort_values('Score_Avg', ascending=False)
os.makedirs('experiments', exist_ok=True)
sum_df.to_csv('experiments/advanced_tournament_summary.csv', index=False)
print("\n" + "="*70)
print("RESULTADOS DEL TORNEO GLOBAL AVANZADO (CON SIZING 4.667 € Y NUEVAS ESTRATEGIAS):")
print("="*70)
print(sum_df.to_string(index=False))

