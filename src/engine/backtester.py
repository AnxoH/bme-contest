import pandas as pd
import numpy as np
from src.engine.portfolio import Portfolio
from src.analysis.evaluator import Evaluator

class Backtester:
    def __init__(self, data_close, data_open, data_high=None, data_low=None, window_size=22, step=11, initial_capital=50000.0):
        """
        Motor de simulación principal. Implementa Walk-Forward (Rolling Windows).
        """
        self.data_close = data_close
        self.data_open = data_open
        self.data_high = data_high
        self.data_low = data_low
        self.window_size = window_size
        self.step = step
        self.initial_capital = initial_capital
        
    def run_strategy(self, strategy, return_raw=False):
        """
        Ejecuta la estrategia a lo largo de múltiples ventanas rodantes independientes.
        """
        results = []
        n_days = len(self.data_close)
        start_points = range(0, n_days - self.window_size, self.step)
        
        for start in start_points:
            window_dates = self.data_close.index[start : start + self.window_size]
            if len(window_dates) < self.window_size * 0.8:
                continue
                
            portfolio = Portfolio(initial_capital=self.initial_capital)
            equity_curve = []
            
            for i, date in enumerate(window_dates):
                portfolio.window_day = i
                portfolio.update_days_held()
                
                current_data_close = self.data_close.loc[:date]
                current_data_open = self.data_open.loc[:date]
                
                market_data = {
                    'close': current_data_close,
                    'open': current_data_open
                }
                if self.data_high is not None:
                    market_data['high'] = self.data_high.loc[:date]
                if self.data_low is not None:
                    market_data['low'] = self.data_low.loc[:date]
                
                orders = strategy.generate_signals(date, market_data, portfolio)
                
                for order in orders:
                    ticker = order['ticker']
                    action = order['action']
                    
                    if action == 'sell':
                        shares = portfolio.positions[ticker]['shares']
                        price_type = order.get('price_type', 'close')
                        px = self.data_open.loc[date, ticker] if price_type == 'open' else self.data_close.loc[date, ticker]
                        
                        portfolio.execute_trade(ticker, 'sell', shares, px, date)
                        
                    elif action == 'buy':
                        px = self.data_close.loc[date, ticker]
                        target_eur = order['amount_eur']
                        shares = int(target_eur / px)
                        
                        portfolio.execute_trade(ticker, 'buy', shares, px, date)
                
                current_close_prices = self.data_close.loc[date]
                nav = portfolio.get_total_value(current_close_prices)
                equity_curve.append(nav)
                
            eq_series = pd.Series(equity_curve, index=window_dates)
            metrics = Evaluator.calculate_window_metrics(eq_series, portfolio.trades_history)
            metrics['window_start'] = window_dates[0]
            metrics['window_end'] = window_dates[-1]
            
            if len(portfolio.trades_history) > 0:
                results.append(metrics)
                
        if len(results) == 0:
            return pd.DataFrame() if return_raw else {"Error": "No trades executed."}
            
        final_df = pd.DataFrame(results)
        return final_df if return_raw else Evaluator.aggregate_results(final_df)
