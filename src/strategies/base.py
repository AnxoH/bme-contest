from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    def __init__(self, name="BaseStrategy", **kwargs):
        """
        :param name: Name of the strategy.
        :param kwargs: Arbitrary hyperparameters for the specific model.
        """
        self.name = name
        self.params = kwargs

    @abstractmethod
    def generate_signals(self, current_date, market_data, portfolio_state):
        """
        This is the core method every strategy must implement.
        It should return a list of orders or target weights for the current_date.
        
        :param current_date: Timestamp of the current simulation step.
        :param market_data: A dict/object providing access to OHLCV, macro data, predictions up to current_date.
        :param portfolio_state: A dict/object with current cash and open positions.
        
        :return: List of dicts representing orders, e.g., [{'ticker': 'SAN.MC', 'action': 'buy', 'amount_eur': 10000}]
                 or a target allocation dictionary.
        """
        pass
        
    def get_metadata(self):
        """
        Returns a dictionary with all the heterogeneous details of the model.
        Override this to include ML model paths, feature lists, exotic params, etc.
        """
        return {
            'strategy_class': self.__class__.__name__,
            'params': self.params
        }
