import pandas as pd
import numpy as np
import os

def main():
    print("Cargando datos históricos...")
    close_df = pd.read_csv('data/raw/stocks_close_15y.csv', index_col='Date', parse_dates=True)
    open_df = pd.read_csv('data/raw/stocks_open_15y.csv', index_col='Date', parse_dates=True)
    
    # Nos centramos en los últimos 1500 días para acelerar
    close_df = close_df.tail(1500).ffill()
    open_df = open_df.tail(1500).ffill()
    
    returns_cc = close_df.pct_change(fill_method=None).fillna(0) # Close to Close
    
    # PnL Overnight: (Open[t] / Close[t-1]) - 1
    # Nos da el retorno de comprar al cierre de t-1 y vender en apertura de t
    returns_overnight = (open_df / close_df.shift(1) - 1).fillna(0)
    
    competitors = {}
    
    # 1. Conservadores (1, 2, 3)
    # Lógica: Invierten 5000€ en el valor más aburrido. Hacen dummy trades de 2500€ L-M-V.
    vols = returns_cc.std()
    safest_tickers = vols.nsmallest(3).index.tolist()
    
    # Dias de trading donde t-1 fue Lunes(0), Miercoles(2), Viernes(4)
    # pandas weekday() para el index
    weekdays_t_minus_1 = close_df.index.to_series().shift(1).dt.weekday
    dummy_mask = weekdays_t_minus_1.isin([0, 2, 4])
    
    for i, ticker in enumerate(safest_tickers):
        passive_pnl = 5000 * returns_cc[ticker]
        dummy_pnl = 2500 * returns_overnight[ticker] * dummy_mask
        
        total_pnl = passive_pnl + dummy_pnl
        equity = 50000 + total_pnl.cumsum()
        daily_ret = total_pnl / equity.shift(1).fillna(50000)
        competitors[f'Conservador_Real_{i+1}'] = daily_ret

    # 2. Trend Followers (1, 2, 3)
    # Invierten 20.000€ en los valores con mejor momentum histórico de 1 año (252 dias)
    momentum = close_df.pct_change(periods=252).iloc[-1]
    top_trend_tickers = momentum.nlargest(3).index.tolist()
    
    for i, ticker in enumerate(top_trend_tickers):
        passive_pnl = 20000 * returns_cc[ticker]
        dummy_pnl = 2500 * returns_overnight[ticker] * dummy_mask
        
        total_pnl = passive_pnl + dummy_pnl
        equity = 50000 + total_pnl.cumsum()
        daily_ret = total_pnl / equity.shift(1).fillna(50000)
        competitors[f'Trend_Real_{i+1}'] = daily_ret

    # 3. Reversion Traders (1, 2)
    # Invierten 15.000€ en los valores más castigados (peor momentum)
    bot_trend_tickers = momentum.nsmallest(2).index.tolist()
    
    for i, ticker in enumerate(bot_trend_tickers):
        passive_pnl = 15000 * returns_cc[ticker]
        dummy_pnl = 2500 * returns_overnight[ticker] * dummy_mask
        
        total_pnl = passive_pnl + dummy_pnl
        equity = 50000 + total_pnl.cumsum()
        daily_ret = total_pnl / equity.shift(1).fillna(50000)
        competitors[f'Reversion_Real_{i+1}'] = daily_ret
        
    # 4. BlueChip Holder (1)
    # 30.000€ en Santander
    if 'SAN.MC' in returns_cc.columns:
        passive_pnl = 30000 * returns_cc['SAN.MC']
        dummy_pnl = 2500 * returns_overnight['SAN.MC'] * dummy_mask
        total_pnl = passive_pnl + dummy_pnl
        equity = 50000 + total_pnl.cumsum()
        daily_ret = total_pnl / equity.shift(1).fillna(50000)
        competitors['BlueChip_Real_1'] = daily_ret
        
    # 5. Volatility Junkie / Loco (1)
    # 45.000€ en el valor más volátil del mercado
    craziest_ticker = vols.idxmax()
    passive_pnl = 45000 * returns_cc[craziest_ticker]
    dummy_pnl = 2500 * returns_overnight[craziest_ticker] * dummy_mask
    total_pnl = passive_pnl + dummy_pnl
    equity = 50000 + total_pnl.cumsum()
    daily_ret = total_pnl / equity.shift(1).fillna(50000)
    competitors['VolJunkie_Real_1'] = daily_ret

    comp_df = pd.DataFrame(competitors)
    comp_df = comp_df.fillna(0)
    
    out_path = 'data/processed/competitors_returns.csv'
    comp_df.to_csv(out_path)
    print(f"Generados {comp_df.shape[1]} competidores 'Reales' (con dummy trades obligatorios) en {out_path}")

if __name__ == '__main__':
    main()

