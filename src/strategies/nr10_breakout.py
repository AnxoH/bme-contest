import pandas as pd
import numpy as np
from src.strategies.base import BaseStrategy

class NR10Breakout(BaseStrategy):
    """
    Estrategia 2: NR10 Breakout Nocturno (Contracción de Volatilidad).
    
    Universo: Cesta de utilities o activo de mínima varianza (RED, ENG, ELE, IBE, NTGY).
    Variable de Estado: Rango porcentual diario RG_t = (High_t - Low_t) / Open_t.
    Condición NR10: RG_t == min(RG_t, RG_{t-1}, ..., RG_{t-9}).
    Filtro Direccional Intradía: Close_t < (High_t + Low_t) / 2 (cierre en mitad inferior).
    Supervivencia (Jueves/Viernes): Si operaciones semanales < 3, se compra el activo con
    mayor compresión relativa para garantizar la cuota y evitar descalificación.
    Sizing: 4.667 € por orden (dilución de los 7 € de comisión mínima).
    Salida: 09:00:01 del día siguiente a precio de apertura (T+1 estricto).
    """
    def __init__(self, 
                 universe=None, 
                 order_amount=4667.0, 
                 window=10, 
                 max_weekly_trades=3, 
                 **kwargs):
        super().__init__(name="NR10_Breakout", **kwargs)
        if universe is None:
            self.universe = ['RED.MC', 'ENG.MC', 'ELE.MC', 'IBE.MC', 'NTGY.MC']
        else:
            self.universe = universe if isinstance(universe, list) else [universe]
        self.order_amount = order_amount
        self.window = window
        self.max_weekly_trades = max_weekly_trades

    def generate_signals(self, current_date, market_data, portfolio):
        orders = []
        
        # 1. Salida en apertura (T+1 estricto): Vender posiciones que vengan de ayer
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
            
        # 3. Comprobación de histórico de datos OHLC
        close_df = market_data['close'].loc[:current_date]
        open_df = market_data['open'].loc[:current_date]
        high_df = market_data.get('high', close_df).loc[:current_date]
        low_df = market_data.get('low', close_df).loc[:current_date]
        
        avail = [t for t in self.universe if t in close_df.columns and t in open_df.columns and t in high_df.columns and t in low_df.columns]
        if not avail or len(close_df) < self.window:
            return orders
            
        # 4. Cálculo de Rangos Porcentuales RG_t = (H_t - L_t) / O_t
        valid_candidates = []
        all_metrics = []
        
        for ticker in avail:
            h = high_df[ticker].tail(self.window)
            l = low_df[ticker].tail(self.window)
            o = open_df[ticker].tail(self.window)
            c = close_df[ticker].tail(self.window)
            
            if len(h) < self.window or len(l) < self.window or len(o) < self.window:
                continue
                
            rg_series = (h - l) / o
            today_rg = rg_series.iloc[-1]
            min_rg_window = rg_series.min()
            
            today_c = c.iloc[-1]
            today_mid = (h.iloc[-1] + l.iloc[-1]) / 2.0
            
            # Condición estricta NR10: rango de hoy es el mínimo de los últimos 10 días
            is_nr10 = (today_rg <= min_rg_window + 1e-8)
            # Filtro direccional: cierre en mitad inferior del rango diario
            is_lower_half = (today_c < today_mid)
            
            all_metrics.append({
                'ticker': ticker,
                'today_rg': today_rg,
                'is_nr10': is_nr10,
                'is_lower_half': is_lower_half,
                'rel_compression': today_rg / rg_series.mean() if rg_series.mean() > 0 else 1.0
            })
            
            if is_nr10 and is_lower_half:
                valid_candidates.append({
                    'ticker': ticker,
                    'today_rg': today_rg
                })
                
        # 5. Lógica de Decisión y Filtro de Ruido / Supervivencia
        day_of_week = current_dt.weekday() # 0: Lunes, 1: Martes, 2: Miércoles, 3: Jueves, 4: Viernes
        
        selected_ticker = None
        
        if valid_candidates:
            # Si hay candidatos puros NR10 + filtro direccional, elegir el de menor rango absoluto
            valid_candidates.sort(key=lambda x: x['today_rg'])
            selected_ticker = valid_candidates[0]['ticker']
        elif day_of_week >= 3 and buys_this_week < self.max_weekly_trades and all_metrics:
            # Supervivencia: es jueves o viernes y aún no tenemos las 3 operaciones semanales
            # Seleccionar el activo con mayor compresión relativa de la cesta
            all_metrics.sort(key=lambda x: x['rel_compression'])
            selected_ticker = all_metrics[0]['ticker']
            
        if selected_ticker:
            orders.append({
                'ticker': selected_ticker,
                'action': 'buy',
                'amount_eur': self.order_amount
            })
            
        return orders

