import pandas as pd
import numpy as np
from src.strategies.base import BaseStrategy

class ConservativeBlueChipRotation(BaseStrategy):
    def __init__(self, allocation_eur=2500, **kwargs):
        super().__init__(name="Conservative_BC_Rotation", allocation_eur=allocation_eur, **kwargs)
        self.allocation_eur = allocation_eur
        self.blue_chips = ['SAN.MC', 'IBE.MC', 'ITX.MC', 'BBVA.MC', 'CABK.MC']
        
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
                
        # Solo operar 3 dias a la semana para minimizar riesgo (ej: Lunes, Miercoles, Viernes)
        # weekday: 0=Mon, 2=Wed, 4=Fri
        if current_date.weekday() not in [0, 2, 4]:
            return orders
            
        if len(close_prices) > 5:
            # Disponibles
            available_bc = [t for t in self.blue_chips if t in close_prices.columns]
            if not available_bc:
                return orders
                
            # Calculamos momentum de 5 dias
            recent_prices = close_prices[available_bc].tail(6)
            momentum = recent_prices.iloc[-1] / recent_prices.iloc[0] - 1
            
            best_ticker = momentum.idxmax()
            
            orders.append({
                'ticker': best_ticker,
                'action': 'buy',
                'amount_eur': self.allocation_eur
            })
            
        return orders
