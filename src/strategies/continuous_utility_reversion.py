import pandas as pd
import numpy as np
from src.strategies.base import BaseStrategy

class ContinuousUtilityReversion(BaseStrategy):
    """
    BareMinimum Alpha: Exposición Continua (5 días/semana) + Rotación Alfa Intradía.
    
    1. Chasis BareMinimum (Exposición Continua):
       Opera de lunes a viernes religiosamente para comprimir la varianza continua de la cartera.
       Elimina los filtros de umbral (no espera a Z < -1.0), eliminando días de retorno 0.
    2. Motor Alfa Cross-Sectional:
       Evalúa la cesta fija de 5 utilities (RED.MC, ENG.MC, ELE.MC, IBE.MC, NTGY.MC).
       A las 17:29:50 calcula el Z-Score de 20 periodos del retorno intradía (Close - Open) / Open.
       Compra siempre el activo que tenga el Z-Score más negativo del día (el más sobrevendido relativo).
    3. Sizing y T+1 Estricto:
       Compra 4.667 € al cierre. Venta a las 09:00:01 a precio de apertura.
    """
    def __init__(self, 
                 universe=None, 
                 order_amount=4667.0, 
                 window=20, 
                 name="BareMinimum_Alpha",
                 **kwargs):
        super().__init__(name=name, **kwargs)
        if universe is None:
            self.universe = ['RED.MC', 'ENG.MC', 'ELE.MC', 'IBE.MC', 'NTGY.MC']
        else:
            self.universe = universe
        self.order_amount = order_amount
        self.window = window

    def generate_signals(self, current_date, market_data, portfolio):
        orders = []
        
        # 1. Salida en apertura (T+1 estricto): Venta sistemática de lo comprado ayer
        for ticker, pos in list(portfolio.positions.items()):
            if pos['days_held'] >= 1:
                orders.append({
                    'ticker': ticker,
                    'action': 'sell',
                    'price_type': 'open'
                })
                
        # 2. Comprobación de histórico de datos
        close_df = market_data['close'].loc[:current_date]
        open_df = market_data['open'].loc[:current_date]
        
        avail = [t for t in self.universe if t in close_df.columns and t in open_df.columns]
        if not avail or len(close_df) < self.window:
            # Fallback si no hay histórico suficiente: comprar el primer activo disponible
            if avail:
                orders.append({
                    'ticker': avail[0],
                    'action': 'buy',
                    'amount_eur': self.order_amount
                })
            return orders
            
        # 3. Cálculo de Z-Score intradía de 20 periodos
        recent_close = close_df[avail].tail(self.window)
        recent_open = open_df[avail].tail(self.window)
        
        intraday_ret = (recent_close - recent_open) / recent_open
        
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
            # Fallback de emergencia
            selected_ticker = avail[0]
        else:
            # Seleccionar sistemáticamente el Z-Score más negativo (el más rezagado del día)
            selected_ticker = min(z_scores, key=z_scores.get)
            
        # 4. Compra diaria sistemática (Lunes a Viernes, 100% continua)
        orders.append({
            'ticker': selected_ticker,
            'action': 'buy',
            'amount_eur': self.order_amount
        })
        
        return orders

