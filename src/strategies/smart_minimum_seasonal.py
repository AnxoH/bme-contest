import pandas as pd
from src.strategies.base import BaseStrategy

class SmartMinimumSeasonal(BaseStrategy):
    """
    Opción C: Estacionalidad Pura.
    Solo opera 3 noches por semana. Descarta los Lunes (riesgo fin de semana)
    y los Viernes (riesgo de posiciones abiertas o baja liquidez).
    Opera religiosamente Martes, Miércoles y Jueves.
    Activo: RED.MC
    """
    def __init__(self, asset='RED.MC', trade_amount=2500, **kwargs):
        super().__init__(name="SmartMin_Seasonal", **kwargs)
        self.asset = asset
        self.trade_amount = trade_amount

    def generate_signals(self, current_date, market_data, portfolio):
        orders = []
        
        if self.asset in portfolio.positions:
            pos = portfolio.positions[self.asset]
            if pos['days_held'] >= 1:
                orders.append({'ticker': self.asset, 'action': 'sell', 'price_type': 'open'})
                
        day_of_week = pd.Timestamp(current_date).weekday()
        
        # Compramos Lunes(0), Martes (1), Miércoles (2)
        # BME define la semana de Jueves a Jueves. 
        # Operar Lunes(cierre->Martes ap), Martes(cierre->Miercoles ap), Miércoles(cierre->Jueves ap) nos da 3 trades antes del Jueves.
        if day_of_week in [0, 1, 2]:
            orders.append({'ticker': self.asset, 'action': 'buy', 'amount_eur': self.trade_amount})
                
        return orders

