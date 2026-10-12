import pandas as pd
import numpy as np
import yfinance as yf
import time
import os
from datetime import datetime

class LiveDataFeed:
    """
    Ingesta de datos en tiempo real para las 5 utilities del concurso BME.
    Combina el histórico reciente (40 días) con la cotización viva de la sesión actual (fast_info).
    """
    UNIVERSE = ['RED.MC', 'ENG.MC', 'ELE.MC', 'IBE.MC', 'NTGY.MC']
    TICKER_NAMES = {
        'RED.MC': 'Redeia Corporación',
        'ENG.MC': 'Enagás',
        'ELE.MC': 'Endesa',
        'IBE.MC': 'Iberdrola',
        'NTGY.MC': 'Naturgy Energy Group'
    }

    def __init__(self, universe=None):
        self.universe = universe or self.UNIVERSE

    def fetch_live_snapshots(self) -> dict:
        """
        Obtiene los precios en vivo (Open, High, Low, Last) para los activos del universo.
        Utiliza fast_info de yfinance con latencia < 2 segundos.
        """
        snapshots = {}
        for ticker in self.universe:
            try:
                t = yf.Ticker(ticker)
                fi = t.fast_info
                
                last_px = float(fi['last_price']) if fi['last_price'] is not None else np.nan
                open_px = float(fi['open']) if fi['open'] is not None else np.nan
                high_px = float(fi['day_high']) if fi['day_high'] is not None else np.nan
                low_px = float(fi['day_low']) if fi['day_low'] is not None else np.nan
                prev_close = float(fi['previous_close']) if fi['previous_close'] is not None else np.nan
                
                # En caso de que high/low/open vengan vacíos o 0
                if pd.isna(high_px) or high_px <= 0:
                    high_px = max(open_px, last_px)
                if pd.isna(low_px) or low_px <= 0:
                    low_px = min(open_px, last_px)
                    
                intraday_ret = ((last_px - open_px) / open_px) * 100.0 if open_px > 0 else 0.0
                day_change = ((last_px - prev_close) / prev_close) * 100.0 if prev_close > 0 else 0.0
                
                snapshots[ticker] = {
                    'name': self.TICKER_NAMES.get(ticker, ticker),
                    'last': last_px,
                    'open': open_px,
                    'high': high_px,
                    'low': low_px,
                    'prev_close': prev_close,
                    'intraday_ret_%': intraday_ret,
                    'day_change_%': day_change,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            except Exception as e:
                snapshots[ticker] = {
                    'name': self.TICKER_NAMES.get(ticker, ticker),
                    'error': str(e),
                    'last': np.nan,
                    'open': np.nan,
                    'high': np.nan,
                    'low': np.nan,
                    'intraday_ret_%': 0.0
                }
                
        return snapshots

    def get_full_market_data(self) -> tuple[dict, dict]:
        """
        Descarga el histórico reciente de 45 días y concatena la sesión de hoy.
        Retorna:
          - market_data: dict con DataFrames 'close', 'open', 'high', 'low'
          - snapshots: dict con los precios en vivo de hoy
        """
        snapshots = self.fetch_live_snapshots()
        today_date = pd.Timestamp.now().normalize()
        
        # 1. Intentar descargar histórico reciente vía yfinance
        try:
            df_hist = yf.download(
                self.universe, 
                period='45d', 
                interval='1d', 
                auto_adjust=False, 
                progress=False
            )
            
            close_df = df_hist['Close'].copy()
            open_df = df_hist['Open'].copy()
            high_df = df_hist['High'].copy()
            low_df = df_hist['Low'].copy()
        except Exception:
            # Fallback a archivos locales si no hay conexión
            close_df = pd.read_csv('data/raw/stocks_close_15y.csv', index_col=0, parse_dates=True)[self.universe].tail(35)
            open_df = pd.read_csv('data/raw/stocks_open_15y.csv', index_col=0, parse_dates=True)[self.universe].tail(35)
            high_df = pd.read_csv('data/raw/stocks_high_15y.csv', index_col=0, parse_dates=True)[self.universe].tail(35)
            low_df = pd.read_csv('data/raw/stocks_low_15y.csv', index_col=0, parse_dates=True)[self.universe].tail(35)

        # 2. Asegurarnos de que la barra viva de hoy esté presente y actualizada en la última fila
        if today_date in close_df.index:
            for t in self.universe:
                if t in snapshots and not pd.isna(snapshots[t]['last']):
                    close_df.loc[today_date, t] = snapshots[t]['last']
                    open_df.loc[today_date, t] = snapshots[t]['open']
                    high_df.loc[today_date, t] = snapshots[t]['high']
                    low_df.loc[today_date, t] = snapshots[t]['low']
        else:
            # Agregar fila de hoy
            row_c = {t: snapshots[t]['last'] for t in self.universe}
            row_o = {t: snapshots[t]['open'] for t in self.universe}
            row_h = {t: snapshots[t]['high'] for t in self.universe}
            row_l = {t: snapshots[t]['low'] for t in self.universe}
            
            close_df.loc[today_date] = row_c
            open_df.loc[today_date] = row_o
            high_df.loc[today_date] = row_h
            low_df.loc[today_date] = row_l

        # Forward fill / backward fill si hay algún dato puntual faltante
        close_df = close_df.ffill().bfill()
        open_df = open_df.ffill().bfill()
        high_df = high_df.ffill().bfill()
        low_df = low_df.ffill().bfill()

        market_data = {
            'close': close_df,
            'open': open_df,
            'high': high_df,
            'low': low_df
        }
        
        return market_data, snapshots
