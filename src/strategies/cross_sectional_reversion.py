import pandas as pd
import numpy as np
from src.strategies.base import BaseStrategy

class CrossSectionalReversion(BaseStrategy):
    """
    Estrategia 1: Cross-Sectional Mean Reversion (Cesta de Utilities).
    
    Universo: Cesta de utilities de ultra-baja volatilidad (RED, ENG, ELE, IBE, NTGY).
    Señal a las 17:29:50: Z-Score de 20 periodos del retorno intradía (Close - Open) / Open.
    Selección: Activo con el Z-Score más negativo (el más sobrevendido del día).
    Filtro de Ruido: Z_score < -1.0.
    Supervivencia (Jueves/Viernes): Si operaciones semanales < 3, se omite el filtro de ruido
    para asegurar exactamente 3 operaciones semanales y evitar penalizaciones/descalificación.
    Sizing: 4.667 € por orden para diluir la comisión mínima de 7 €.
    Salida: 09:00:01 del día siguiente a precio de apertura (T+1 estricto).
    """
    def __init__(self, 
                 universe=None, 
                 order_amount=4667.0, 
                 z_threshold=-1.0, 
                 window=20, 
                 max_weekly_trades=3, 
                 **kwargs):
        super().__init__(name="CS_MeanReversion", **kwargs)
        if universe is None:
            self.universe = ['RED.MC', 'ENG.MC', 'ELE.MC', 'IBE.MC', 'NTGY.MC']
        else:
            self.universe = universe
        self.order_amount = order_amount
        self.z_threshold = z_threshold
        self.window = window
        self.max_weekly_trades = max_weekly_trades

    def generate_signals(self, current_date, market_data, portfolio):
        orders = []
        
        # 1. Salida en apertura (T+1 estricto): Vender cualquier posición que venga de ayer
        for ticker, pos in list(portfolio.positions.items()):
            if pos['days_held'] >= 1:
                orders.append({
                    'ticker': ticker,
                    'action': 'sell',
                    'price_type': 'open'
                })
                
        # 2. Control semanal estricto de ejecuciones (máximo 3 por semana)
        current_dt = pd.Timestamp(current_date)
        curr_year, curr_week, _ = current_dt.isocalendar()
        
        buys_this_week = 0
        for t in portfolio.trades_history:
            if t['action'] == 'buy':
                t_dt = pd.Timestamp(t['date'])
                t_year, t_week, _ = t_dt.isocalendar()
                if t_year == curr_year and t_week == curr_week:
                    buys_this_week += 1
                    
        if buys_this_week >= self.max_weekly_trades:
            return orders
            
        # 3. Comprobación de histórico
        close_df = market_data['close'].loc[:current_date]
        open_df = market_data['open'].loc[:current_date]
        
        avail = [t for t in self.universe if t in close_df.columns and t in open_df.columns]
        if not avail or len(close_df) < self.window:
            return orders
            
        # 4. Cálculo del Z-Score intradía de 20 periodos para cada activo
        # R_{i, t} = (C_{i, t} - O_{i, t}) / O_{i, t}
        recent_close = close_df[avail].tail(self.window)
        recent_open = open_df[avail].tail(self.window)
        
        intraday_ret = (recent_close - recent_open) / recent_open
        
        # Z-Scores para la sesión actual t
        z_scores = {}
        for col in avail:
            r_series = intraday_ret[col].dropna()
            if len(r_series) >= self.window * 0.7:
                mu = r_series.mean()
                sigma = r_series.std()
                today_ret = r_series.iloc[-1]
                z = (today_ret - mu) / sigma if sigma > 1e-8 else 0.0
                z_scores[col] = z
                
        if not z_scores:
            return orders
            
        # Activo con el Z-Score más negativo (más castigado)
        best_ticker = min(z_scores, key=z_scores.get)
        min_z = z_scores[best_ticker]
        
        # 5. Lógica de Decisión y Filtro de Ruido / Supervivencia
        day_of_week = current_dt.weekday() # 0: Lunes, 1: Martes, 2: Miércoles, 3: Jueves, 4: Viernes
        
        should_buy = False
        # Si es Jueves o Viernes y faltan operaciones para llegar a 3: supervivencia obligatoria
        if day_of_week >= 3 and buys_this_week < self.max_weekly_trades:
            should_buy = True
        else:
            # Filtro de ruido estándar: solo si Z < -1.0
            if min_z < self.z_threshold:
                should_buy = True
                
        if should_buy:
            orders.append({
                'ticker': best_ticker,
                'action': 'buy',
                'amount_eur': self.order_amount
            })
            
        return orders

