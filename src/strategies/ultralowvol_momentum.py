import pandas as pd
import numpy as np
from src.strategies.base import BaseStrategy

class UltraLowVolMomentum(BaseStrategy):
    def __init__(self, allocation_eur=2500, **kwargs):
        super().__init__(name="UltraLowVol_Momentum", allocation_eur=allocation_eur, **kwargs)
        self.allocation_eur = allocation_eur
        
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
                
        # Operar solo 3 días a la semana para minimizar exposición (Lunes, Miercoles, Viernes)
        if current_date.weekday() not in [0, 2, 4]:
            return orders
            
        if len(close_prices) > 20:
            recent_data = close_prices.tail(20)
            
            # 1. Volatilidad de 20 días
            returns = recent_data.pct_change()
            vols = returns.std()
            
            # Seleccionar los 5 valores menos volátiles
            safest_tickers = vols.nsmallest(5).index.tolist()
            
            # 2. Momentum de 5 días sobre esos 5
            momentum_data = close_prices[safest_tickers].tail(6)
            momentum = momentum_data.iloc[-1] / momentum_data.iloc[0] - 1
            
            # Elegir el que tenga mayor momentum positivo
            best_ticker = momentum.idxmax()
            
            orders.append({
                'ticker': best_ticker,
                'action': 'buy',
                'amount_eur': self.allocation_eur
            })
            
        return orders
