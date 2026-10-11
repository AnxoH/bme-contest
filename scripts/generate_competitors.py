import pandas as pd
import numpy as np
import os

def main():
    # Load data
    close_df = pd.read_csv('data/raw/stocks_close_15y.csv', index_col='Date', parse_dates=True)
    market_df = pd.read_csv('data/raw/market_composition.csv')
    
    ibex_tickers = market_df[market_df['Is_IBEX35'] == True]['Ticker'].tolist()
    # Intersect with available columns
    ibex_tickers = [t for t in ibex_tickers if t in close_df.columns]
    
    # Calculate daily returns for all stocks
    rets = close_df.pct_change(fill_method=None).fillna(0)
    
    competitors = pd.DataFrame(index=rets.index)
    
    # 1. Los Índices (2)
    competitors['Idx_IBEX35_Proxy'] = rets[ibex_tickers].mean(axis=1)
    competitors['Idx_Continuous_Merc'] = rets.mean(axis=1)
    
    # 2. Los Blue-Chips (4)
    blue_chips = {'BH_Santander': 'SAN.MC', 'BH_Iberdrola': 'IBE.MC', 'BH_Inditex': 'ITX.MC', 'BH_Telefonica': 'TEF.MC'}
    for name, ticker in blue_chips.items():
        if ticker in rets.columns:
            competitors[name] = rets[ticker]
        else:
            competitors[name] = 0.0
            
    # 3. Los Trend Followers (3)
    # Buy top 5 of last N days
    for N, name in [(5, 'Trend_1W'), (10, 'Trend_2W'), (20, 'Trend_1M')]:
        # Momentum is the return over last N days
        mom = close_df.pct_change(periods=N, fill_method=None).shift(1) # shift 1 to avoid lookahead, we use mom at t-1 to invest at t
            
        # Optimize by using numpy
        mom_arr = mom.values
        daily_arr = rets.values
        trend_rets = np.zeros(len(rets))
        for i in range(len(rets)):
            row = mom_arr[i]
            valid = ~np.isnan(row)
            if valid.sum() >= 5:
                # get indices of top 5
                top5_idx = np.argpartition(row[valid], -5)[-5:]
                # the actual indices in the original array
                actual_idx = np.where(valid)[0][top5_idx]
                trend_rets[i] = np.nanmean(daily_arr[i, actual_idx])
            else:
                trend_rets[i] = 0.0
        competitors[name] = trend_rets

    # 4. Los Mean Reverters (3)
    for N, name in [(5, 'Revert_1W'), (10, 'Revert_2W'), (20, 'Revert_1M')]:
        mom = close_df.pct_change(periods=N, fill_method=None).shift(1)
        mom_arr = mom.values
        daily_arr = rets.values
        rev_rets = np.zeros(len(rets))
        for i in range(len(rets)):
            row = mom_arr[i]
            valid = ~np.isnan(row)
            if valid.sum() >= 5:
                # get indices of bottom 5
                bot5_idx = np.argpartition(row[valid], 5)[:5]
                actual_idx = np.where(valid)[0][bot5_idx]
                rev_rets[i] = np.nanmean(daily_arr[i, actual_idx])
            else:
                rev_rets[i] = 0.0
        competitors[name] = rev_rets

    # 5. Los Ludópatas / Chicharros (3)
    # Find 3 most volatile stocks overall
    vols = rets.std()
    top_vol_tickers = vols.nlargest(3).index.tolist()
    for i, ticker in enumerate(top_vol_tickers):
        competitors[f'YOLO_{i+1}'] = rets[ticker]
        
    # 6. Los Conservadores (3)
    # They hold 10% in low vol stocks, 90% cash.
    bot_vol_tickers = vols.nsmallest(3).index.tolist()
    for i, ticker in enumerate(bot_vol_tickers):
        competitors[f'Conservador_{i+1}'] = rets[ticker] * 0.10

    # 7. Los Caóticos (2)
    # Random stock picking each day
    np.random.seed(42)
    daily_arr = rets.values
    rand1_rets = np.zeros(len(rets))
    rand2_rets = np.zeros(len(rets))
    
    for i in range(len(rets)):
        valid_idx = np.where(~np.isnan(daily_arr[i]))[0]
        if len(valid_idx) > 0:
            r1_idx = np.random.choice(valid_idx, 1)
            rand1_rets[i] = np.nanmean(daily_arr[i, r1_idx])
            
            r2_idx = np.random.choice(valid_idx, min(5, len(valid_idx)))
            rand2_rets[i] = np.nanmean(daily_arr[i, r2_idx])
    
    competitors['Chaotic_1'] = rand1_rets
    competitors['Chaotic_5'] = rand2_rets
    
    # Fill NAs
    competitors = competitors.fillna(0)
    
    # Save to CSV
    os.makedirs('data/processed', exist_ok=True)
    out_path = 'data/processed/competitors_returns.csv'
    competitors.to_csv(out_path)
    print(f"Generados {competitors.shape[1]} competidores en {out_path}")

if __name__ == '__main__':
    main()
