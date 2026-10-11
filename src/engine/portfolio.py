import pandas as pd

class Portfolio:
    def __init__(self, initial_capital=50000.0, commission_rate=0.0015, min_commission=7.0):
        """
        Mantiene el estado de la cuenta, calcula comisiones reales y gestiona el efectivo (cash).
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}
        
        self.commission_rate = commission_rate
        self.min_commission = min_commission
        self.trades_history = []
        
    def get_total_value(self, current_prices):
        """
        Calcula el Net Asset Value (NAV) de la cartera sumando Cash + Valor de mercado de las posiciones.
        """
        val = self.cash
        for ticker, pos in self.positions.items():
            if ticker in current_prices and not pd.isna(current_prices[ticker]):
                val += pos['shares'] * current_prices[ticker]
        return val
        
    def calculate_commission(self, trade_value):
        """ Calcula la comisión del concurso """
        return max(trade_value * self.commission_rate, self.min_commission)

    def execute_trade(self, ticker, action, shares, price, date):
        """ Ejecuta una compra o venta si hay liquidez suficiente. """
        if shares <= 0: return False
        
        trade_value = shares * price
        comm = self.calculate_commission(trade_value)
        total_cost = trade_value + comm
        
        if action == 'buy':
            if self.cash >= total_cost:
                self.cash -= total_cost
                self.positions[ticker] = {'shares': shares, 'entry_price': price, 'days_held': 0}
                self.trades_history.append({'date': date, 'ticker': ticker, 'action': 'buy', 'shares': shares, 'price': price, 'comm': comm})
                return True
        elif action == 'sell':
            if ticker in self.positions and self.positions[ticker]['shares'] >= shares:
                net_proceeds = trade_value - comm
                self.cash += net_proceeds
                
                self.positions[ticker]['shares'] -= shares
                if self.positions[ticker]['shares'] == 0:
                    del self.positions[ticker]
                
                self.trades_history.append({'date': date, 'ticker': ticker, 'action': 'sell', 'shares': shares, 'price': price, 'comm': comm})
                return True
        return False
        
    def update_days_held(self):
        """ Incrementa el contador de días para el requisito de retención T+1 """
        for ticker in self.positions:
            self.positions[ticker]['days_held'] += 1

