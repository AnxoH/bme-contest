from src.strategies.base import BaseStrategy
import pandas as pd

class BareMinimumStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__(name="BareMinimum", **kwargs)
        # Usamos RED.MC (Redeia - Red Eléctrica) por ser el valor más refugio y de menor volatilidad
        self.dummy_asset = 'RED.MC'
        
    def generate_signals(self, current_date, market_data, portfolio):
        orders = []
        
        # 1. SIEMPRE VENDER A LA APERTURA (T+1)
        if self.dummy_asset in portfolio.positions:
            pos = portfolio.positions[self.dummy_asset]
            if pos['days_held'] >= 1:
                orders.append({
                    'ticker': self.dummy_asset,
                    'action': 'sell',
                    'price_type': 'open'
                })
                
        # 2. SIEMPRE COMPRAR AL CIERRE (1200€ diarios garantiza >5000€ a la semana, salvando cualquier solapamiento de ventana)
        orders.append({
            'ticker': self.dummy_asset,
            'action': 'buy',
            'amount_eur': 1200
        })
                
        return orders
