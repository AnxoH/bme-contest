import pandas as pd
import numpy as np

class EngineMicroAlfaNR:
    """
    Motor 2: Micro-Alfa NR10 (Narrow Range 10 - Compresión de Rango Intradía).
    
    1. Universo: RED.MC, ENG.MC, ELE.MC, IBE.MC, NTGY.MC.
    2. Rango Intradía: (High - Low) / Open.
    3. Normalización: Ratio frente a la media de 10 periodos.
    4. Filtro Direccional: Ubicación del precio actual en la mitad inferior del rango de hoy.
    5. Criterio de Selección: Activo con mayor contracción de rango (menor ratio relativo).
    6. Sizing: ~900 € por orden.
    """
    def __init__(self, universe=None, window=10, target_order_eur=900.0):
        self.universe = universe or ['RED.MC', 'ENG.MC', 'ELE.MC', 'IBE.MC', 'NTGY.MC']
        self.window = window
        self.target_order_eur = target_order_eur

    def evaluate(self, market_data: dict, snapshots: dict, corporate_alerts: dict = None) -> pd.DataFrame:
        high_df = market_data['high'][self.universe]
        low_df = market_data['low'][self.universe]
        open_df = market_data['open'][self.universe]
        
        # Rango histórico diario normalizado por Open
        norm_range = (high_df - low_df) / open_df
        
        records = []
        for ticker in self.universe:
            rg_series = norm_range[ticker].dropna()
            
            px_now = snapshots[ticker]['last']
            px_open = snapshots[ticker]['open']
            px_high = snapshots[ticker]['high']
            px_low = snapshots[ticker]['low']
            
            # Rango intradía de hoy
            today_rg = (px_high - px_low) / px_open if px_open > 0 else 0.0
            
            # Media de los 10 periodos previos (excluyendo hoy)
            hist_rg = rg_series.iloc[:-1].tail(self.window)
            mean_rg = hist_rg.mean() if len(hist_rg) >= self.window * 0.7 else today_rg
            
            ratio_nr = today_rg / mean_rg if mean_rg > 1e-8 else 1.0
            
            # Ubicación dentro del rango de hoy (0.0 = en el mínimo, 1.0 = en el máximo)
            rg_spread = px_high - px_low
            if rg_spread > 1e-8:
                pos_in_range = (px_now - px_low) / rg_spread
            else:
                pos_in_range = 0.5
                
            is_lower_half = pos_in_range <= 0.50
            
            # Sizing exacto
            shares = int(self.target_order_eur / px_now) if px_now > 0 else 0
            amount_eur = shares * px_now
            
            has_corp_risk = corporate_alerts.get(ticker, {}).get('has_risk', False) if corporate_alerts else False
            corp_status = corporate_alerts.get(ticker, {}).get('status_str', 'OK') if corporate_alerts else 'OK'
            
            records.append({
                'Ticker': ticker,
                'Nombre': snapshots[ticker]['name'],
                'Precio_Actual': px_now,
                'Rango_Hoy_%': today_rg * 100.0,
                'Rango_Medio_10d_%': mean_rg * 100.0,
                'Ratio_NR': ratio_nr,
                'Posicion_Rango_%': pos_in_range * 100.0,
                'Mitad_Inferior': is_lower_half,
                'Acciones': shares,
                'Importe_EUR': amount_eur,
                'Riesgo_Corporativo': has_corp_risk,
                'Info_Corporativa': corp_status
            })
            
        df = pd.DataFrame(records)
        
        # Ordenación: Menor Ratio_NR primero (mayor compresión).
        # Favorecemos activos en mitad inferior del rango; penalizamos los que tengan riesgo corporativo.
        df['Sort_Key'] = df.apply(
            lambda r: (1 if r['Riesgo_Corporativo'] else 0, 0 if r['Mitad_Inferior'] else 1, r['Ratio_NR']), 
            axis=1
        )
        df = df.sort_values('Sort_Key').reset_index(drop=True)
        df.drop(columns=['Sort_Key'], inplace=True)
        
        df.insert(0, 'Rank', range(1, len(df) + 1))
        return df
