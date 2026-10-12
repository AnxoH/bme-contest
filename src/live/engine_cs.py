import pandas as pd
import numpy as np

class EngineMicroAlfaCS:
    """
    Motor 1: Micro-Alfa Cross-Sectional Reversion (Z-Score Intradía).
    
    1. Universo: RED.MC, ENG.MC, ELE.MC, IBE.MC, NTGY.MC.
    2. Retorno Intradía: (Close_today - Open_today) / Open_today.
    3. Normalización: Z-Score de 20 periodos.
    4. Criterio de Selección: Activo con el Z-Score más negativo (más sobrevendido).
    5. Sizing: ~900 € (3 operaciones semanales = ~2.670 € > 2.500 € mínimos de BME).
    """
    def __init__(self, universe=None, window=20, target_order_eur=900.0):
        self.universe = universe or ['RED.MC', 'ENG.MC', 'ELE.MC', 'IBE.MC', 'NTGY.MC']
        self.window = window
        self.target_order_eur = target_order_eur

    def evaluate(self, market_data: dict, snapshots: dict, corporate_alerts: dict = None) -> pd.DataFrame:
        close_df = market_data['close'][self.universe]
        open_df = market_data['open'][self.universe]
        
        # Retornos intradía históricos de las últimas 25 sesiones
        intraday_rets = (close_df - open_df) / open_df
        
        records = []
        for ticker in self.universe:
            r_series = intraday_rets[ticker].dropna()
            px_now = snapshots[ticker]['last']
            px_open = snapshots[ticker]['open']
            
            # Retorno intradía de hoy
            today_ret = (px_now - px_open) / px_open if px_open > 0 else 0.0
            
            # Media y desviación estándar de los 20 periodos previos (excluyendo hoy)
            hist_series = r_series.iloc[:-1].tail(self.window)
            if len(hist_series) >= self.window * 0.7:
                mu = hist_series.mean()
                sigma = hist_series.std()
                z_score = (today_ret - mu) / sigma if sigma > 1e-8 else 0.0
            else:
                mu, sigma, z_score = 0.0, 1.0, 0.0
                
            # Sizing exacto
            shares = int(self.target_order_eur / px_now) if px_now > 0 else 0
            amount_eur = shares * px_now
            
            has_corp_risk = corporate_alerts.get(ticker, {}).get('has_risk', False) if corporate_alerts else False
            corp_status = corporate_alerts.get(ticker, {}).get('status_str', 'OK') if corporate_alerts else 'OK'
            
            records.append({
                'Ticker': ticker,
                'Nombre': snapshots[ticker]['name'],
                'Precio_Actual': px_now,
                'Retorno_Intradia_%': today_ret * 100.0,
                'Media_20d_%': mu * 100.0,
                'Vol_Intradia_%': sigma * 100.0,
                'Z_Score': z_score,
                'Acciones': shares,
                'Importe_EUR': amount_eur,
                'Riesgo_Corporativo': has_corp_risk,
                'Info_Corporativa': corp_status
            })
            
        df = pd.DataFrame(records)
        
        # Ordenación: Menor Z-Score primero (más sobrevendido).
        # Si un activo tiene riesgo corporativo crítico, se desplaza al final.
        df['Sort_Key'] = df.apply(lambda r: (1 if r['Riesgo_Corporativo'] else 0, r['Z_Score']), axis=1)
        df = df.sort_values('Sort_Key').reset_index(drop=True)
        df.drop(columns=['Sort_Key'], inplace=True)
        
        df.insert(0, 'Rank', range(1, len(df) + 1))
        return df
