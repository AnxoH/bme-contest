import pandas as pd
import numpy as np

# Load data
close_prices = pd.read_csv('../data/raw/stocks_close_15y.csv', index_col=0, parse_dates=True)

# Define 1 month window (22 days)
window = 22

returns = close_prices.pct_change()

# 1. IBEX 35 Proxy (35 most consistent stocks)
valid_counts = close_prices.count()
top_35_tickers = valid_counts.nlargest(35).index
returns_top35 = returns[top_35_tickers]
ibex_eq_returns = returns_top35.mean(axis=1)

# 3. Constant Rebalanced Portfolio (CRP) - Daily Equal Weight of all stocks
crp_returns = returns.mean(axis=1)

def evaluate_rolling_windows(daily_returns, window_size=22, step=11):
    results = []
    n_days = len(daily_returns)
    start_points = range(0, n_days - window_size, step)
    
    for start in start_points:
        window_rets = daily_returns.iloc[start:start+window_size].dropna()
        if len(window_rets) < window_size * 0.8:
            continue
            
        ret = (1 + window_rets).prod() - 1
        vol = window_rets.std() * np.sqrt(252)
        score = (0.6 * ret) - (0.3 * vol)
        results.append({'Return': ret, 'Volatility': vol, 'Score': score})
        
    return pd.DataFrame(results)

def evaluate_buy_and_hold(prices, window_size=22, step=11):
    results = []
    n_days = len(prices)
    start_points = range(0, n_days - window_size, step)
    
    for start in start_points:
        # Drop stocks that have NaN in this specific window to simulate B&H of active universe
        window_prices = prices.iloc[start:start+window_size].dropna(axis=1, how='any')
        if window_prices.empty or len(window_prices) < window_size * 0.8:
            continue
            
        # Equal capital at start: normalize prices to 1 at start
        norm_prices = window_prices / window_prices.iloc[0]
        port_val = norm_prices.mean(axis=1)
        port_rets = port_val.pct_change().dropna()
        
        ret = port_val.iloc[-1] - 1
        vol = port_rets.std() * np.sqrt(252)
        score = (0.6 * ret) - (0.3 * vol)
        
        results.append({'Return': ret, 'Volatility': vol, 'Score': score})
    return pd.DataFrame(results)

crp_res = evaluate_rolling_windows(crp_returns)
ibex_res = evaluate_rolling_windows(ibex_eq_returns)
bah_res = evaluate_buy_and_hold(close_prices)

def summarize(df, name):
    print(f"--- {name} ---")
    print(f"Mean Return: {df['Return'].mean()*100:.2f}%")
    print(f"Mean Volatility: {df['Volatility'].mean()*100:.2f}%")
    print(f"Mean Score: {df['Score'].mean()*100:.3f}")
    print(f"Win Rate: {(df['Return']>0).mean()*100:.2f}%\n")

summarize(bah_res, "Buy and Hold (All Stocks)")
summarize(crp_res, "Constant Rebalanced Portfolio (Daily Equal Weight)")
summarize(ibex_res, "IBEX 35 Proxy (Top 35 Daily Equal Weight)")
