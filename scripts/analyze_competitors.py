import pandas as pd
import numpy as np

def main():
    rets_df = pd.read_csv('data/processed/competitors_returns.csv', index_col=0, parse_dates=True)
    
    window_size = 22
    step = 11
    n_days = len(rets_df)
    start_points = range(0, n_days - window_size, step)
    
    all_results = []
    
    for start in start_points:
        window_rets = rets_df.iloc[start : start + window_size]
        if len(window_rets) < window_size * 0.8:
            continue
            
        comps = []
        for col in window_rets.columns:
            series = window_rets[col].dropna()
            if len(series) > 0:
                r = np.prod(1 + series) - 1
                v = series.std() * np.sqrt(252)
            else:
                r = 0.0
                v = 0.0
            comps.append({'name': col, 'ret': r, 'vol': v})
            
        for c in comps:
            c['final_val'] = 50000 * (1 + c['ret'])
            
        max_val = max([c['final_val'] for c in comps])
        for c in comps:
            c['ret_points'] = (c['final_val'] * 6) / max_val
            
        min_vol = min([c['vol'] for c in comps])
        max_vol = max([c['vol'] for c in comps])
        
        for c in comps:
            if max_vol == min_vol:
                c['vol_points'] = 3.0
            else:
                c['vol_points'] = 3 * (1 - (c['vol'] - min_vol) / (max_vol - min_vol))
                
            c['total_points'] = c['ret_points'] + c['vol_points']
            
            all_results.append({
                'Competitor': c['name'],
                'Return_1M': c['ret'],
                'Vol_Ann': c['vol'],
                'Ret_Points': c['ret_points'],
                'Vol_Points': c['vol_points'],
                'Total_Score': c['total_points']
            })
            
    df = pd.DataFrame(all_results)
    agg = df.groupby('Competitor').mean().sort_values('Total_Score', ascending=False)
    # Convert points to 2 decimal places and Returns to percentages
    agg['Return_1M'] = (agg['Return_1M'] * 100).round(2).astype(str) + '%'
    agg['Vol_Ann'] = (agg['Vol_Ann'] * 100).round(2).astype(str) + '%'
    agg['Ret_Points'] = agg['Ret_Points'].round(2)
    agg['Vol_Points'] = agg['Vol_Points'].round(2)
    agg['Total_Score'] = agg['Total_Score'].round(2)
    
    print(agg.to_string())

if __name__ == '__main__':
    main()
