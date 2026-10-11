import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 1. Cargar Datos
close_prices = pd.read_csv('../data/raw/stocks_close_15y.csv', index_col=0, parse_dates=True)
open_prices = pd.read_csv('../data/raw/stocks_open_15y.csv', index_col=0, parse_dates=True)

universe = ['CABK.MC', 'RED.MC', 'VIS.MC', 'SAN.MC']
close_prices = close_prices[universe].tail(1500).fillna(method='ffill')
open_prices = open_prices[universe].tail(1500).fillna(method='ffill')

# 2. Indicadores Baseline
sma200 = close_prices.rolling(200).mean()
sma5 = close_prices.rolling(5).mean()

delta = close_prices.diff()
gain = (delta.where(delta > 0, 0)).rolling(window=3).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=3).mean()
rs = gain / loss
rsi3 = 100 - (100 / (1 + rs))

# 3. Motor de Simulación (Bucle Diario)
def run_simulation(start_idx, window_len, initial_capital=50000):
    cash = initial_capital
    portfolio = {t: {'shares': 0, 'entry': 0, 'days': 0} for t in universe}
    history = []
    trades = 0
    
    for i in range(start_idx, start_idx + window_len):
        if i >= len(close_prices): break
        
        # --- APERTURA DEL DÍA T ---
        # Evaluar salidas Close-to-Open (Take Profit en Gaps Alcistas)
        for t in universe:
            if portfolio[t]['shares'] > 0:
                portfolio[t]['days'] += 1
                
                # Regla T+1 cumplida porque ya es el día siguiente
                open_px = open_prices[t].iloc[i]
                entry_px = portfolio[t]['entry']
                
                # Salida 1: Gap alcista (>0.5% de ganancia)
                if open_px > (entry_px * 1.005):
                    shares = portfolio[t]['shares']
                    val = shares * open_px
                    comm = max(val * 0.0015, 7.0)
                    cash += (val - comm)
                    portfolio[t] = {'shares': 0, 'entry': 0, 'days': 0}
                    trades += 1
                    
        # --- CIERRE DEL DÍA T ---
        # 1. Evaluar resto de salidas al cierre (RSI>70 o Time Exit T+3)
        for t in universe:
            if portfolio[t]['shares'] > 0:
                close_px = close_prices[t].iloc[i]
                days = portfolio[t]['days']
                
                exit_signal = (rsi3[t].iloc[i] > 70) or (close_px > sma5[t].iloc[i]) or (days >= 3)
                if exit_signal:
                    shares = portfolio[t]['shares']
                    val = shares * close_px
                    comm = max(val * 0.0015, 7.0)
                    cash += (val - comm)
                    portfolio[t] = {'shares': 0, 'entry': 0, 'days': 0}
                    trades += 1

        # 2. Evaluar nuevas compras al Cierre
        for t in universe:
            if portfolio[t]['shares'] == 0:
                close_px = close_prices[t].iloc[i]
                # Señal: En tendencia alcista macro, pero pánico micro
                if (close_px > sma200[t].iloc[i]) and (rsi3[t].iloc[i] < 15) and (cash >= 10500):
                    val = 10000
                    comm = max(val * 0.0015, 7.0)
                    shares = int(val / close_px)
                    real_val = shares * close_px
                    real_comm = max(real_val * 0.0015, 7.0)
                    
                    cash -= (real_val + real_comm)
                    portfolio[t] = {'shares': shares, 'entry': close_px, 'days': 0}
                    
        # Calcular valor total
        port_val = cash + sum([portfolio[t]['shares'] * close_prices[t].iloc[i] for t in universe])
        history.append(port_val)
        
    final_val = history[-1] if history else initial_capital
    ret = (final_val / initial_capital) - 1
    
    # Volatilidad (simplificada) de los retornos diarios de la cartera
    rets = pd.Series(history).pct_change().dropna()
    vol = rets.std() * np.sqrt(252) if len(rets) > 0 else 0
    
    return ret, vol, trades

# 4. Validacion por Ventanas de 1 Mes (22 días)
# Haremos 50 simulaciones independientes
window_size = 22
results = []
start_points = range(200, len(close_prices) - window_size, int(window_size/2))

for start in start_points:
    r, v, t = run_simulation(start, window_size)
    if t > 0: # Solo guardamos meses donde hubo operaciones
        # Score del concurso (0.6 Retorno - 0.3 Volatilidad)
        score = (0.6 * r) - (0.3 * v)
        results.append({'Return': r, 'Volatility': v, 'Trades': t, 'ContestScore': score})

res_df = pd.DataFrame(results)

output = f\"\"\"# RESULTADOS DEL BACKTESTER (BASELINE: CLOSE-TO-OPEN)
Total de meses (ventanas de 22 días) simulados con actividad: {len(res_df)}

### MÉTRICAS PROMEDIO MENSUALES:
- **Rentabilidad Media Mensual:** {res_df['Return'].mean()*100:.2f}%
- **Volatilidad Promedio:** {res_df['Volatility'].mean()*100:.2f}%
- **Score Concurso Promedio (0.6R - 0.3V):** {res_df['ContestScore'].mean()*100:.3f}
- **Operaciones Promedio por Mes:** {res_df['Trades'].mean():.1f}

### DISTRIBUCIÓN DE PROBABILIDAD (Win Rate):
- Porcentaje de meses cerrados en positivo: {(res_df['Return'] > 0).mean()*100:.1f}%
- Mejor mes simulado: {res_df['Return'].max()*100:.2f}%
- Peor mes simulado: {res_df['Return'].min()*100:.2f}%
\"\"\"

with open('../docs/baseline_results.md', 'w', encoding='utf-8') as f:
    f.write(output)

print("Backtest completado. Resultados guardados en docs/baseline_results.md")

