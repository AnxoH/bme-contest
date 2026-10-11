from src.strategies.base import BaseStrategy
import pandas as pd
import numpy as np

class MeanReversionStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__(name="MeanReversion_Surv", **kwargs)
        self.universe = ['CABK.MC', 'RED.MC', 'VIS.MC', 'SAN.MC']
        # Preferimos valores defensivos para trades de mantenimiento
        self.low_vol_assets = ['RED.MC', 'VIS.MC', 'CABK.MC', 'SAN.MC'] 
        
    def generate_signals(self, current_date, market_data, portfolio):
        orders = []
        close_data = market_data['close']
        
        # 1. EVALUAR SALIDAS (Ventas)
        for ticker in list(portfolio.positions.keys()):
            pos = portfolio.positions[ticker]
            # Si lo compramos ayer, hoy podemos venderlo en la apertura
            if pos['days_held'] >= 1:
                orders.append({
                    'ticker': ticker,
                    'action': 'sell',
                    'price_type': 'open'
                })
                
        # Calcular cuota semanal
        # El jueves es el día 3 de la semana. La semana acaba el jueves.
        current_week = (current_date + pd.Timedelta(days=3)).isocalendar().week
        buys = 0
        buy_vol = 0
        
        for t in portfolio.trades_history:
            t_date = pd.to_datetime(t['date'])
            t_week = (t_date + pd.Timedelta(days=3)).isocalendar().week
            if t_week == current_week and t['action'] == 'buy':
                buys += 1
                buy_vol += t['shares'] * t['price']
                
        # 2. EVALUAR COMPRAS GENUINAS
        if len(close_data) > 200:
            sma200 = close_data.rolling(200).mean().loc[current_date]
            
            delta = close_data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(3).mean().loc[current_date]
            loss = (-delta.where(delta < 0, 0)).rolling(3).mean().loc[current_date]
            
            # Avoid division by zero
            loss = loss.replace(0, 1e-5)
            rs = gain / loss
            rsi3 = 100 - (100 / (1 + rs))
            
            available_cash = portfolio.cash
            
            for ticker in self.universe:
                if ticker not in portfolio.positions and available_cash >= 10500:
                    if close_data.loc[current_date, ticker] > sma200[ticker] and rsi3[ticker] < 15:
                        orders.append({
                            'ticker': ticker,
                            'action': 'buy',
                            'amount_eur': 10000
                        })
                        available_cash -= 10000
                        buys += 1
                        buy_vol += 10000
                        
        # 3. TRADES DE SUPERVIVENCIA
        # Si hoy es Miércoles (dayofweek == 2), garantizamos que la cuota esté cumplida
        # para que mañana (Jueves) se vendan en la apertura y cumplan la cuota de ventas.
        if current_date.dayofweek == 2:
            needed_buys = max(0, 3 - buys)
            needed_vol = max(0, 2500 - buy_vol)
            
            if needed_buys > 0 or needed_vol > 0:
                trades_to_do = max(needed_buys, 1 if needed_vol > 0 else 0)
                vol_per_trade = max(needed_vol / trades_to_do, 900) # Un poco más del mínimo
                
                genuines = [o['ticker'] for o in orders if o['action'] == 'buy']
                
                for ticker in self.low_vol_assets:
                    if trades_to_do <= 0: break
                    if ticker not in portfolio.positions and ticker not in genuines:
                        orders.append({
                            'ticker': ticker,
                            'action': 'buy',
                            'amount_eur': vol_per_trade
                        })
                        trades_to_do -= 1

        return orders
