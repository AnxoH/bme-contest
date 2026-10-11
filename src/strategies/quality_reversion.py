import pandas as pd
import numpy as np
from src.strategies.base import BaseStrategy

class OvernightQualityReversion(BaseStrategy):
    def __init__(self, allocation_eur=2500, sma_period=200, min_sma_dist=1.05, **kwargs):
        super().__init__(name=f"Quality_Reversion_{sma_period}", allocation_eur=allocation_eur, sma_period=sma_period, min_sma_dist=min_sma_dist, **kwargs)
        self.allocation_eur = allocation_eur
        self.sma_period = sma_period
        self.min_sma_dist = min_sma_dist # Debe estar un 5% por encima de la SMA
        
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
        
        if len(close_prices) > self.sma_period + 1:
            # Calcular SMA-200 actual (solo necesitamos los ultimos SMA_period datos para el valor actual)
            # Para mayor rendimiento, sacamos el mean del tail de sma_period
            recent_data = close_prices.tail(self.sma_period)
            sma = recent_data.mean()
            current_price = close_prices.iloc[-1]
            prev_price = close_prices.iloc[-2]
            
            # Filtro 1: Precio actual > SMA * min_sma_dist
            quality_mask = current_price > (sma * self.min_sma_dist)
            quality_tickers = quality_mask[quality_mask].index.tolist()
            
            if quality_tickers:
                # Filtro 2: El que haya tenido la peor caída hoy entre los de calidad
                returns_today = current_price[quality_tickers] / prev_price[quality_tickers] - 1
                target_ticker = returns_today.idxmin()
                
                # Para asegurar liquidez/seguridad, operamos.
                # Nota: como hay que hacer 3 operaciones por semana, si cada día se ejecuta
                # esto, tendremos ~5 por semana (una diaria).
                orders.append({
                    'ticker': target_ticker,
                    'action': 'buy',
                    'amount_eur': self.allocation_eur
                })
                
        return orders
