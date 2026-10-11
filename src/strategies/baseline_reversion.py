from src.strategies.base import BaseStrategy
import pandas as pd
import numpy as np

class BaselineReversion(BaseStrategy):
    """
    Estrategia Baseline de Mean Reversion Long-Only: Fade the Winner (SMA200 + RSI3).
    """
    def __init__(self, order_amount=2500, rsi_period=3, sma_period=200, **kwargs):
        super().__init__(name="Fade the Winner (SMA200 + RSI3)", **kwargs)
        self.order_amount = order_amount
        self.rsi_period = rsi_period
        self.sma_period = sma_period

    def generate_signals(self, current_date, market_data, portfolio):
        orders = []
        close_data = market_data['close']
        
        # 1. Salida en apertura (T+1)
        for ticker, pos in list(portfolio.positions.items()):
            if pos['days_held'] >= 1:
                orders.append({
                    'ticker': ticker,
                    'action': 'sell',
                    'price_type': 'open'
                })
                
        # 2. Entrada: Valor más sobrevendido por RSI3
        if len(close_data) > self.rsi_period + 1:
            delta = close_data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(self.rsi_period).mean().loc[current_date]
            loss = (-delta.where(delta < 0, 0)).rolling(self.rsi_period).mean().loc[current_date].replace(0, 1e-5)
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # Filtro SMA y no-NaN en precio actual
            current_px = close_data.loc[current_date]
            valid_px = ~current_px.isna() & (current_px > 0)
            if len(close_data) > self.sma_period:
                sma = close_data.rolling(self.sma_period).mean().loc[current_date]
                valid_mask = valid_px & (current_px > sma)
                candidate_rsi = rsi[valid_mask].dropna()
            else:
                candidate_rsi = rsi[valid_px].dropna()
                
            if not candidate_rsi.empty:
                best_ticker = candidate_rsi.idxmin()
                orders.append({
                    'ticker': best_ticker,
                    'action': 'buy',
                    'amount_eur': self.order_amount
                })
        return orders
