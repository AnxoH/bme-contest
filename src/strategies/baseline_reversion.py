class BaselineReversion:
    """
    Estrategia de Mean Reversion Long-Only.
    Genera senales vectorizadas para alimentar al backtester.
    """
    def __init__(self):
        self.name = "Fade the Winner (SMA200 + RSI3)"
        
    def calculate_indicators(self, adj_close):
        pass
        
    def generate_signals(self):
        pass
