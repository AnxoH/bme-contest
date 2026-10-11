import pandas as pd
import numpy as np
from src.strategies.base import BaseStrategy

class SingleAssetMaster(BaseStrategy):
    def __init__(self, target_ticker='IBE.MC', allocation_eur=2500, **kwargs):
        super().__init__(name=f"SingleAsset_{target_ticker.split('.')[0]}", target_ticker=target_ticker, allocation_eur=allocation_eur, **kwargs)
        self.target_ticker = target_ticker
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
                
        # Operar Lunes, Miercoles y Viernes para cumplir cupo
        if current_date.weekday() not in [0, 2, 4]:
            return orders
            
        if self.target_ticker in close_prices.columns and len(close_prices) >= 2:
            current_price = close_prices[self.target_ticker].iloc[-1]
            prev_price = close_prices[self.target_ticker].iloc[-2]
            
            # Si bajó, compramos el doble (Mean Reversion intraday sobre activo seguro)
            # Si subió o se mantuvo, compramos lo mínimo para el cupo
            if current_price < prev_price:
                alloc = self.allocation_eur * 2
            else:
                alloc = self.allocation_eur
                
            orders.append({
                'ticker': self.target_ticker,
                'action': 'buy',
                'amount_eur': alloc
            })
            
        return orders
