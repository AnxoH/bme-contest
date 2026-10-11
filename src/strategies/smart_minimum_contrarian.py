import pandas as pd
from src.strategies.base import BaseStrategy

class SmartMinimumContrarian(BaseStrategy):
    """
    Opción B: Contrarian de Apertura.
    Solo opera 3 noches por semana basándose en debilidad intradía.
    Intenta comprar el activo refugio cuando ha tenido un día malo.
    """
    def __init__(self, asset='RED.MC', trade_amount=2500, **kwargs):
        super().__init__(name="SmartMin_Contrarian", **kwargs)
        self.asset = asset
        self.trade_amount = trade_amount

    def generate_signals(self, current_date, market_data, portfolio):
        orders = []
        
        if self.asset in portfolio.positions:
            pos = portfolio.positions[self.asset]
            if pos['days_held'] >= 1:
                orders.append({'ticker': self.asset, 'action': 'sell', 'price_type': 'open'})
                
        hist_close = market_data['close'].loc[:current_date]
        hist_open = market_data['open'].loc[:current_date]
        
        should_buy = False
        day_of_week = pd.Timestamp(current_date).weekday() # 0=Mon, 4=Fri
        
        if len(hist_close) > 0 and len(hist_open) > 0:
            today_close = hist_close[self.asset].iloc[-1]
            today_open = hist_open[self.asset].iloc[-1]
            
            is_red_day = today_close < today_open
            
            # Buscamos 3 trades. Lunes, Martes y Miércoles somos selectivos.
            if day_of_week in [0, 1, 2]:
                should_buy = is_red_day
            else:
                # Si llega el Jueves y Viernes, no deberíamos tener que forzar si hemos guardado el state,
                # pero sin state forzamos para garantizar los trades semanales.
                should_buy = True
        else:
            should_buy = True
            
        if should_buy:
            orders.append({'ticker': self.asset, 'action': 'buy', 'amount_eur': self.trade_amount})
                
        return orders
