import pandas as pd
import numpy as np
from src.strategies.base import BaseStrategy

class PatientSniperStrategy(BaseStrategy):
    """
    El Francotirador Paciente (Patient Sniper)
    
    1. Selects the absolute least volatile asset in the market over a long window (e.g. 60 days).
    2. Trades the bare minimum (2500€) every day to stay strictly compliant.
    3. If that asset experiences a notable drop (RSI < 40 or negative return yesterday), it buys a larger amount (e.g. 10000€) to capture the bounce.
    """
    def __init__(self, vol_window=60, rsi_window=14, rsi_threshold=40, base_amount=2500, snipe_amount=10000, **kwargs):
        super().__init__(name=f"Patient_Sniper_{vol_window}v_{rsi_threshold}rsi", **kwargs)
        self.vol_window = vol_window
        self.rsi_window = rsi_window
        self.rsi_threshold = rsi_threshold
        self.base_amount = base_amount
        self.snipe_amount = snipe_amount

    def _calculate_rsi(self, prices, window):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        
        avg_gain = gain.rolling(window=window, min_periods=1).mean()
        avg_loss = loss.rolling(window=window, min_periods=1).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.replace([np.inf, -np.inf], 100)

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
                
        hist_data = market_data['close'].loc[:current_date]
        if len(hist_data) < max(self.vol_window, self.rsi_window):
            return orders
            
        # Volatilidad a 60 días
        recent_data = hist_data.tail(self.vol_window + 1)
        returns = recent_data.pct_change()
        volatility = returns.std().dropna()
        
        if len(volatility) == 0:
            return orders
            
        # Activo menos volatil
        safest_asset = volatility.idxmin()
        
        # Calcular RSI para ese activo
        asset_prices = hist_data[safest_asset].tail(self.rsi_window + 1)
        rsi_series = self._calculate_rsi(asset_prices, self.rsi_window)
        current_rsi = rsi_series.iloc[-1]
        
        # Determinar importe
        amount = self.base_amount
        if pd.notna(current_rsi) and current_rsi < self.rsi_threshold:
            amount = self.snipe_amount
            
        orders.append({
            'ticker': safest_asset,
            'action': 'buy',
            'amount_eur': amount
        })
            
        return orders
