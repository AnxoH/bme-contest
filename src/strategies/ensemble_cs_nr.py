import pandas as pd
import numpy as np
from src.strategies.base import BaseStrategy

class EnsembleCSNR(BaseStrategy):
    """
    Estrategia Final: Ensemble Cross-Ranking (Reversión Z-Score + Compresión NR).
    
    1. Universo:
       Cesta cerrada de 5 utilities: RED.MC, ENG.MC, ELE.MC, IBE.MC, NTGY.MC.
    2. Factor 1 (Z-Score de Reversión):
       Retorno intradía (Cierre - Apertura) / Apertura normalizado a 20 periodos.
       Ranking de 1 (más negativo/sobrevendido) a 5 (más positivo).
    3. Factor 2 (Compresión de Rango):
       Rango porcentual de la sesión (High - Low) / Open comparado con la media de 10 periodos.
       Ranking de 1 (más comprimido relativo) a 5 (más expandido).
    4. Matriz de Puntuación (Cross-Ranking):
       Score = Rank(Z-Score) + Rank(Compresión).
       Selecciona el activo con menor Score combinado (consenso óptimo sobreventa + compresión).
    5. Frecuencia y Sizing:
       Opera Lunes, Martes y Miércoles (semana BME Jueves-Jueves, bloqueo de fin de semana).
       Sizing de 900 € para garantizar superar los 2.500 € legales de BME tras el redondeo a acciones enteras.
       Salida a mercado a las 09:00:01 del día siguiente (T+1 estricto).
    """
    def __init__(self, 
                 universe=None, 
                 order_amount=900.0, 
                 window_z=20, 
                 window_range=10, 
                 name="Ensemble_CS_NR", 
                 grace_period_days=0,
                 **kwargs):
        super().__init__(name=name, **kwargs)
        if universe is None:
            self.universe = ['RED.MC', 'ENG.MC', 'ELE.MC', 'IBE.MC', 'NTGY.MC']
        else:
            self.universe = universe
            
        self.order_amount = order_amount
        self.window_z = window_z
        self.window_range = window_range
        self.grace_period_days = grace_period_days

    def generate_signals(self, current_date, market_data, portfolio):
        orders = []
        
        # 1. Salida estricta en apertura (T+1): Vender cualquier posición abierta ayer
        for ticker, pos in list(portfolio.positions.items()):
            if pos['days_held'] >= 1:
                orders.append({
                    'ticker': ticker,
                    'action': 'sell',
                    'price_type': 'open'
                })
                
        # 2. Control de Periodo de Gracia (Primeros días sin cuota obligatoria de BME)
        window_day = getattr(portfolio, 'window_day', 99)
        if window_day < self.grace_period_days:
            return orders
                
        # 3. Control semanal BME (Jueves a Jueves):
        # Compras: Lunes (0), Martes (1) y Miércoles (2) al cierre (17:29:50).
        # Ventas: Martes, Miércoles y Jueves a la apertura (09:00:01).
        # Jueves noche, Viernes, Sábado y Domingo: Cero operaciones (cero fin de semana).
        current_dt = pd.Timestamp(current_date)
        day_of_week = current_dt.weekday()
        if day_of_week not in [0, 1, 2]:
            return orders
            
        # 3. Datos históricos
        close_df = market_data['close'].loc[:current_date]
        open_df = market_data['open'].loc[:current_date]
        high_df = market_data.get('high', close_df).loc[:current_date]
        low_df = market_data.get('low', close_df).loc[:current_date]
        
        avail = [t for t in self.universe if t in close_df.columns and t in open_df.columns and t in high_df.columns and t in low_df.columns]
        req_window = max(self.window_z, self.window_range)
        if not avail or len(close_df) < req_window:
            if avail:
                orders.append({'ticker': avail[0], 'action': 'buy', 'amount_eur': self.order_amount})
            return orders

        # 4. Cálculo de Factor 1: Z-Score de Reversión Intradía
        z_scores = {}
        recent_close = close_df[avail].tail(self.window_z)
        recent_open = open_df[avail].tail(self.window_z)
        intraday_ret = (recent_close - recent_open) / recent_open
        
        for col in avail:
            r_series = intraday_ret[col].dropna()
            if len(r_series) >= self.window_z * 0.7:
                mu = r_series.mean()
                sigma = r_series.std()
                today_ret = r_series.iloc[-1]
                z = (today_ret - mu) / sigma if sigma > 1e-8 else 0.0
                z_scores[col] = z
            else:
                z_scores[col] = 0.0

        # 5. Cálculo de Factor 2: Ratio de Compresión de Rango
        rg_ratios = {}
        for col in avail:
            h = high_df[col].tail(self.window_range)
            l = low_df[col].tail(self.window_range)
            o = open_df[col].tail(self.window_range)
            
            if len(h) >= self.window_range * 0.7 and len(l) >= self.window_range * 0.7 and len(o) >= self.window_range * 0.7:
                rg_series = (h - l) / o
                today_rg = rg_series.iloc[-1]
                mean_rg = rg_series.mean()
                ratio = today_rg / mean_rg if mean_rg > 1e-8 else 1.0
                rg_ratios[col] = ratio
            else:
                rg_ratios[col] = 1.0

        # 6. Matriz de Puntuación (Cross-Ranking)
        # Factor 1: Rank de menor a mayor Z-Score (1 = más sobrevendido)
        sorted_by_z = sorted(avail, key=lambda t: z_scores[t])
        rank_z = {t: i + 1 for i, t in enumerate(sorted_by_z)}
        
        # Factor 2: Rank de menor a mayor Ratio de Rango (1 = más comprimido)
        sorted_by_rg = sorted(avail, key=lambda t: rg_ratios[t])
        rank_rg = {t: i + 1 for i, t in enumerate(sorted_by_rg)}
        
        # Score combinado
        combined_scores = {t: rank_z[t] + rank_rg[t] for t in avail}
        
        # Seleccionar activo con menor Score combinado (desempate por Z-Score)
        best_ticker = min(avail, key=lambda t: (combined_scores[t], z_scores[t]))
        
        # 7. Ejecución de orden
        orders.append({
            'ticker': best_ticker,
            'action': 'buy',
            'amount_eur': self.order_amount
        })
        
        return orders

