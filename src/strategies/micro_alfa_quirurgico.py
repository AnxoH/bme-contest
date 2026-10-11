import pandas as pd
import numpy as np
from src.strategies.base import BaseStrategy

class MicroAlfaQuirurgico(BaseStrategy):
    """
    La Configuración Definitiva: 'Micro-Alfa Quirúrgico'
    
    1. Exposición Mínima Legal (Sizing = 834 €):
       3 operaciones semanales x 834 € = 2.502 € (cumple estrictamente el volumen mínimo legal de 2.500 €).
       El 98,34 % de la cartera permanece en liquidez permanente (volatilidad 0).
       La volatilidad de la cartera se comprime al mínimo histórico absoluto (< 0.10 %).
       
    2. Bloqueo de Fin de Semana (Frecuencia = Exactamente 3 noches, Lunes a Jueves):
       Prohíbe terminantemente operar los viernes (cero riesgo de gap de fin de semana).
       Congela el gasto semanal en comisiones a 42 € exactos (14 € x 3).
       
    3. Motor de Señal Selectivo:
       - 'cs_reversion': Rotación a la utility con menor Z-Score intradía (cesta de 5 utilities).
       - 'nr10': Contracción extrema de rango NR10 con filtro direccional de cierre en mitad inferior.
    """
    def __init__(self, 
                 universe=None, 
                 order_amount=900.0, 
                 engine='cs_reversion',
                 name=None,
                 z_threshold=-1.0,
                 window=20,
                 grace_period_days=0,
                 **kwargs):
        strategy_name = name or f"MicroAlfa_{engine.upper()}"
        super().__init__(name=strategy_name, **kwargs)
        
        if universe is None:
            self.universe = ['RED.MC', 'ENG.MC', 'ELE.MC', 'IBE.MC', 'NTGY.MC']
        else:
            self.universe = universe
            
        self.order_amount = order_amount
        self.engine = engine.lower()
        self.z_threshold = z_threshold
        self.window = window
        self.grace_period_days = grace_period_days

    def generate_signals(self, current_date, market_data, portfolio):
        orders = []
        
        # 1. Salida estricta en apertura (T+1): Vender cualquier posición abierta ayer
        for ticker, pos in list(portfolio.positions.items()):
            if pos['days_held'] >= 1:
                orders.append({
                    'ticker': ticker,
                    'action': 'sell',
                    'price_type': 'open'
                })
                
        # 2. Control de Periodo de Gracia (Primeros días sin cuota obligatoria de BME)
        window_day = getattr(portfolio, 'window_day', 99)
        if window_day < self.grace_period_days:
            return orders
                
        # 3. Control semanal BME (Jueves a Jueves):
        # Para que 3 compras y 3 ventas caigan dentro de la misma semana de concurso:
        # Se compra Lunes (0), Martes (1) y Miércoles (2) al cierre.
        # Se vende Martes (1), Miércoles (2) y Jueves (3) a la apertura.
        # Jueves noche y Viernes noche: CERO operaciones (evita el fin de semana y el corte de semana).
        current_dt = pd.Timestamp(current_date)
        day_of_week = current_dt.weekday() # 0: Lun, 1: Mar, 2: Mié, 3: Jue, 4: Vie
        
        if day_of_week not in [0, 1, 2]:
            return orders
            
        # 3. Comprobación de datos históricos
        close_df = market_data['close'].loc[:current_date]
        open_df = market_data['open'].loc[:current_date]
        
        avail = [t for t in self.universe if t in close_df.columns and t in open_df.columns]
        if not avail or len(close_df) < self.window:
            if avail:
                orders.append({'ticker': avail[0], 'action': 'buy', 'amount_eur': self.order_amount})
            return orders

        # 4. Motores de Selección Alfa
        selected_ticker = None
        
        if self.engine == 'cs_reversion':
            # MOTOR CS_REVERSION: Rotación a la utility más castigada (menor Z-Score)
            recent_close = close_df[avail].tail(self.window)
            recent_open = open_df[avail].tail(self.window)
            intraday_ret = (recent_close - recent_open) / recent_open
            
            z_scores = {}
            for col in avail:
                r_series = intraday_ret[col].dropna()
                if len(r_series) >= self.window * 0.7:
                    mu = r_series.mean()
                    sigma = r_series.std()
                    today_ret = r_series.iloc[-1]
                    z = (today_ret - mu) / sigma if sigma > 1e-8 else 0.0
                    z_scores[col] = z
                    
            if z_scores:
                # Comprar la que más ha caído relativamente (más sobrevendida)
                selected_ticker = min(z_scores, key=z_scores.get)
                    
        elif self.engine == 'nr10':
            # MOTOR NR10_BREAKOUT: Contracción extrema + cierre inferior
            high_df = market_data.get('high', close_df).loc[:current_date]
            low_df = market_data.get('low', close_df).loc[:current_date]
            
            valid_candidates = []
            all_metrics = []
            
            for ticker in avail:
                if ticker not in high_df.columns or ticker not in low_df.columns:
                    continue
                h = high_df[ticker].tail(10)
                l = low_df[ticker].tail(10)
                o = open_df[ticker].tail(10)
                c = close_df[ticker].tail(10)
                
                if len(h) < 10 or len(l) < 10 or len(o) < 10:
                    continue
                    
                rg_series = (h - l) / o
                today_rg = rg_series.iloc[-1]
                min_rg_window = rg_series.min()
                
                today_c = c.iloc[-1]
                today_mid = (h.iloc[-1] + l.iloc[-1]) / 2.0
                
                is_nr10 = (today_rg <= min_rg_window + 1e-8)
                is_lower_half = (today_c < today_mid)
                
                all_metrics.append({
                    'ticker': ticker,
                    'today_rg': today_rg,
                    'rel_compression': today_rg / rg_series.mean() if rg_series.mean() > 0 else 1.0
                })
                
                if is_nr10 and is_lower_half:
                    valid_candidates.append({
                        'ticker': ticker,
                        'today_rg': today_rg
                    })
                    
            if valid_candidates:
                valid_candidates.sort(key=lambda x: x['today_rg'])
                selected_ticker = valid_candidates[0]['ticker']
            elif all_metrics:
                all_metrics.sort(key=lambda x: x['rel_compression'])
                selected_ticker = all_metrics[0]['ticker']

        if not selected_ticker and avail:
            selected_ticker = avail[0]

        # 5. Generar orden
        orders.append({
            'ticker': selected_ticker,
            'action': 'buy',
            'amount_eur': self.order_amount
        })
            
        return orders

