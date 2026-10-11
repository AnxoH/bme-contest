import pandas as pd
import numpy as np
from src.strategies.base import BaseStrategy

class SlowTrainStrategy(BaseStrategy):
    """
    El Tren Lento (Slow Train)
    
    1. Selects the 5 least volatile assets over the last 20 days.
    2. From those 5, selects the one with the highest momentum (return over last 10 days).
    3. Trades strictly the minimum amount (2500€) every single day on that asset.
    """
    def __init__(self, vol_window=20, mom_window=10, top_n_vol=5, order_amount=2500, **kwargs):
        super().__init__(name=f"Slow_Train_{vol_window}v_{mom_window}m", **kwargs)
        self.vol_window = vol_window
        self.mom_window = mom_window
        self.top_n_vol = top_n_vol
        self.order_amount = order_amount

    def generate_signals(self, current_date, market_data, portfolio):
        orders = []
        
        # 1. Vender cualquier posición existente en la apertura
        for ticker, pos in portfolio.positions.items():
            if pos['days_held'] >= 1:
                orders.append({
                    'ticker': ticker,
                    'action': 'sell',
                    'price_type': 'open'
                })
        
        # Necesitamos datos suficientes
        hist_data = market_data['close'].loc[:current_date]
        if len(hist_data) < max(self.vol_window, self.mom_window):
            return orders
            
        # Calcular volatilidad (usamos pct_change sobre los ultimos N dias)
        recent_data = hist_data.tail(self.vol_window + 1)
        returns = recent_data.pct_change()
        volatility = returns.std()
        
        # Calcular momentum (retorno en ultimos M dias)
        mom_data = hist_data.tail(self.mom_window + 1)
        momentum = (mom_data.iloc[-1] / mom_data.iloc[0]) - 1
        
        # Filtrar activos validos
        valid_assets = volatility.dropna().index.intersection(momentum.dropna().index)
        if len(valid_assets) == 0:
            return orders
            
        vol_valid = volatility[valid_assets]
        mom_valid = momentum[valid_assets]
        
        # Top N menor volatilidad
        least_vol = vol_valid.nsmallest(self.top_n_vol).index
        
        # El de mayor momentum entre ellos
        if len(least_vol) > 0:
            best_asset = mom_valid[least_vol].idxmax()
            
            orders.append({
                'ticker': best_asset,
                'action': 'buy',
                'amount_eur': self.order_amount
            })
            
        return orders
