import nbformat as nbf

nb_path = '../notebooks/04_contest_specific_eda.ipynb'

# Load the notebook
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

markdown_text = """## 4. Análisis de Métricas Baseline (Benchmarks)

Para poder evaluar el rendimiento de nuestras estrategias algorítmicas, necesitamos establecer un **baseline del mercado continuo**. Vamos a analizar qué rendimiento y métricas hubiéramos obtenido si hubiéramos operado estrategias pasivas evaluadas en **ventanas rodantes de 1 mes (22 días de trading)**, exactamente la misma metodología de validación que usaremos para nuestro algoritmo.

Vamos a evaluar tres portfolios:
1. **Buy and Hold (B&H) - Mercado Continuo:** Comprar todo el universo disponible a partes iguales a inicio de mes y mantener.
2. **Constant Rebalanced Portfolio (CRP):** Un portfolio equiponderado de todas las acciones del mercado, que se rebalancea diariamente a pesos iguales.
3. **IBEX 35 Proxy:** Un portfolio equiponderado de las 35 acciones con mayor volumen de cotización (las más líquidas/grandes) rebalanceado diariamente.
"""

code_text = """import pandas as pd
import numpy as np

# Cargar datos
close_prices = pd.read_csv('../data/raw/stocks_close_15y.csv', index_col=0, parse_dates=True)

# 1. Definir funciones de evaluación para ventanas de 22 días (1 mes)
def evaluate_rolling_windows(daily_returns, window_size=22, step=11):
    results = []
    n_days = len(daily_returns)
    start_points = range(0, n_days - window_size, step)
    
    for start in start_points:
        window_rets = daily_returns.iloc[start:start+window_size].dropna()
        if len(window_rets) < window_size * 0.8:
            continue
            
        ret = (1 + window_rets).prod() - 1
        vol_ann = window_rets.std() * np.sqrt(252) # Volatilidad anualizada
        vol_daily = window_rets.std() # Volatilidad diaria
        
        # Asumimos que el concurso usa Volatilidad anualizada para la métrica
        score = (0.6 * ret) - (0.3 * vol_ann)
        
        results.append({
            'Return_1M': ret, 
            'Vol_Ann': vol_ann, 
            'Vol_Daily': vol_daily, 
            'Score': score
        })
    return pd.DataFrame(results)

def evaluate_buy_and_hold(prices, window_size=22, step=11):
    results = []
    n_days = len(prices)
    start_points = range(0, n_days - window_size, step)
    
    for start in start_points:
        window_prices = prices.iloc[start:start+window_size].dropna(axis=1, how='any')
        if window_prices.empty or len(window_prices) < window_size * 0.8:
            continue
            
        norm_prices = window_prices / window_prices.iloc[0]
        port_val = norm_prices.mean(axis=1)
        port_rets = port_val.pct_change().dropna()
        
        ret = port_val.iloc[-1] - 1
        vol_ann = port_rets.std() * np.sqrt(252)
        vol_daily = port_rets.std()
        
        score = (0.6 * ret) - (0.3 * vol_ann)
        results.append({
            'Return_1M': ret, 
            'Vol_Ann': vol_ann, 
            'Vol_Daily': vol_daily,
            'Score': score
        })
    return pd.DataFrame(results)

# 2. Calcular los portfolios
returns = close_prices.pct_change()

# CRP
crp_returns = returns.mean(axis=1)

# IBEX 35 Proxy
top_35_tickers = close_prices.count().nlargest(35).index
ibex_eq_returns = returns[top_35_tickers].mean(axis=1)

# 3. Evaluar
crp_res = evaluate_rolling_windows(crp_returns)
ibex_res = evaluate_rolling_windows(ibex_eq_returns)
bah_res = evaluate_buy_and_hold(close_prices)

def summarize(df, name):
    print(f"\\n{'='*10} {name} {'='*10}")
    print(f"Retorno Promedio Mensual:      {df['Return_1M'].mean()*100:>6.2f}%")
    print(f"Volatilidad Promedio (Anual):  {df['Vol_Ann'].mean()*100:>6.2f}%")
    print(f"Volatilidad Promedio (Diaria): {df['Vol_Daily'].mean()*100:>6.2f}%")
    print(f"Score Concurso (0.6R - 0.3V):  {df['Score'].mean()*100:>6.3f}")
    print(f"Win Rate (Meses positivos):    {(df['Return_1M']>0).mean()*100:>6.2f}%")

summarize(bah_res, "Buy and Hold (Mercado Continuo)")
summarize(crp_res, "Constant Rebalanced Portfolio (Equiponderado)")
summarize(ibex_res, "IBEX 35 Proxy (Top 35 Equiponderado)")
"""

markdown_cell = nbf.v4.new_markdown_cell(markdown_text)
code_cell = nbf.v4.new_code_cell(code_text)

nb.cells.extend([markdown_cell, code_cell])

with open(nb_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Cells appended to notebook.")
