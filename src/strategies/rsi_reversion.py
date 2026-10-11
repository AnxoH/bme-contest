import pandas as pd
import numpy as np
from src.strategies.base import BaseStrategy

class RsiOvernightReversion(BaseStrategy):
    def __init__(self, rsi_period=3, allocation_eur=2500, **kwargs):
        super().__init__(name=f"RSI_Overnight_{rsi_period}d", **kwargs)
        self.rsi_period = rsi_period
        self.allocation_eur = allocation_eur
        self.params.update({'rsi_period': rsi_period, 'allocation_eur': allocation_eur})

    def calculate_rsi(self, series, period):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def generate_signals(self, current_date, market_data, portfolio):
        orders = []
        close_prices = market_data['close']
        
        # 1. SIEMPRE VENDER A LA APERTURA (T+1)
        for ticker, pos in list(portfolio.positions.items()):
            if pos['days_held'] >= 1:
                orders.append({
                    'ticker': ticker,
                    'action': 'sell',
                    'price_type': 'open'
                })
                
        # 2. ENCONTRAR EL VALOR MÁS SOBREVENDIDO (RSI más bajo)
        if len(close_prices) > self.rsi_period + 1:
            rsis = {}
            for ticker in close_prices.columns:
                series = close_prices[ticker]
                if not series.isna().iloc[-1]:
                    rsi_series = self.calculate_rsi(series, self.rsi_period)
                    current_rsi = rsi_series.iloc[-1]
                    if not np.isnan(current_rsi):
                        rsis[ticker] = current_rsi
            
            if rsis:
                # Ordenar por RSI de menor a mayor
                sorted_rsis = sorted(rsis.items(), key=lambda x: x[1])
                target_ticker = sorted_rsis[0][0] # El más sobrevendido
                
                orders.append({
                    'ticker': target_ticker,
                    'action': 'buy',
                    'amount_eur': self.allocation_eur
                })
                
        return orders
