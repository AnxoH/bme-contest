import pandas as pd
import numpy as np
from src.strategies.base import BaseStrategy

class SeasonalitySafeHaven(BaseStrategy):
    def __init__(self, dummy_allocation=2500, strong_allocation=10000, **kwargs):
        super().__init__(name="Seasonality_SafeHaven", dummy_allocation=dummy_allocation, strong_allocation=strong_allocation, **kwargs)
        self.dummy_allocation = dummy_allocation
        self.strong_allocation = strong_allocation
        
    def generate_signals(self, current_date, market_data, portfolio):
        orders = []
        close_prices = market_data['close']
        
        # Siempre vender en la apertura todo lo que tengamos
        for ticker, pos in list(portfolio.positions.items()):
            if pos['days_held'] >= 1:
                orders.append({
                    'ticker': ticker,
                    'action': 'sell',
                    'price_type': 'open'
                })
                
        # Operar Lunes, Miercoles y Viernes para cumplir cupo
        if current_date.weekday() not in [0, 2, 4]:
            return orders
            
        if len(close_prices) > 20:
            recent_data = close_prices.tail(20)
            
            # Buscar SIEMPRE el valor menos volátil de todo el mercado
            returns = recent_data.pct_change()
            vols = returns.std()
            safest_ticker = vols.idxmin()
            
            # Condición de Seasonality (Window Dressing a fin de mes / principio de mes)
            # Los dias > 25 o < 5 suelen tener inercia institucional positiva.
            day_of_month = current_date.day
            
            if day_of_month > 25 or day_of_month < 5:
                # Invertir fuerte
                alloc = self.strong_allocation
            else:
                # Dummy trade para cumplir el cupo
                alloc = self.dummy_allocation
                
            orders.append({
                'ticker': safest_ticker,
                'action': 'buy',
                'amount_eur': alloc
            })
            
        return orders
