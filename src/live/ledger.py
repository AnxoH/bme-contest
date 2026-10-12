import pandas as pd
import numpy as np
import os
from datetime import datetime, date

class TradesLedger:
    """
    Gestor del libro de órdenes auditado para el concurso real de BME.
    Almacena las compras y ventas confirmadas manualmente por el usuario en 'data/live/trades_ledger.csv'.
    """
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    LEDGER_PATH = os.path.join(PROJECT_ROOT, 'data', 'live', 'trades_ledger.csv')
    COLUMNS = ['Fecha', 'Hora', 'Accion', 'Ticker', 'Titulos', 'Precio', 'Importe_EUR', 'Semana_BME']

    def __init__(self, path=None):
        self.path = path or self.LEDGER_PATH
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            df_init = pd.DataFrame(columns=self.COLUMNS)
            df_init.to_csv(self.path, index=False)

    def load_trades(self) -> pd.DataFrame:
        if not os.path.exists(self.path):
            return pd.DataFrame(columns=self.COLUMNS)
        try:
            return pd.read_csv(self.path)
        except Exception:
            return pd.DataFrame(columns=self.COLUMNS)

    @staticmethod
    def get_bme_week_id(dt: datetime = None) -> str:
        """
        Calcula el identificador de semana BME (de Jueves 17:30 a Jueves 17:30).
        """
        if dt is None:
            dt = datetime.now()
        # En BME la semana de liquidación y concurso computa de Jueves a Jueves
        # Usamos el año y el número de semana ISO como referencia base
        cal = dt.isocalendar()
        return f"{cal[0]}-W{cal[1]:02d}"

    def record_trade(self, action: str, ticker: str, shares: int, price: float, dt: datetime = None) -> dict:
        """
        Registra una compra ('BUY') o venta ('SELL') confirmada por el usuario.
        """
        if dt is None:
            dt = datetime.now()
            
        action = action.upper().strip()
        ticker = ticker.upper().strip()
        shares = int(shares)
        price = float(price)
        amount_eur = round(shares * price, 2)
        week_id = self.get_bme_week_id(dt)
        
        record = {
            'Fecha': dt.strftime('%Y-%m-%d'),
            'Hora': dt.strftime('%H:%M:%S'),
            'Accion': action,
            'Ticker': ticker,
            'Titulos': shares,
            'Precio': price,
            'Importe_EUR': amount_eur,
            'Semana_BME': week_id
        }
        
        df = self.load_trades()
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        df.to_csv(self.path, index=False)
        return record

    def get_current_open_position(self) -> dict | None:
        """
        Comprueba si hay una posición abierta (comprada al cierre y pendiente de venta a las 09:00).
        """
        df = self.load_trades()
        if len(df) == 0:
            return None
            
        # Agrupamos por ticker para ver balance neto de títulos
        buys = df[df['Accion'] == 'BUY'].groupby('Ticker')['Titulos'].sum()
        sells = df[df['Accion'] == 'SELL'].groupby('Ticker')['Titulos'].sum()
        
        open_positions = {}
        for t in buys.index:
            net_shares = buys[t] - sells.get(t, 0)
            if net_shares > 0:
                last_buy = df[(df['Ticker'] == t) & (df['Accion'] == 'BUY')].iloc[-1]
                open_positions[t] = {
                    'ticker': t,
                    'shares': int(net_shares),
                    'buy_date': last_buy['Fecha'],
                    'buy_price': last_buy['Precio'],
                    'buy_amount': round(net_shares * last_buy['Precio'], 2)
                }
                
        if len(open_positions) > 0:
            # Retornar la primera activa (en micro-alfa solo hay 1 a la vez)
            return list(open_positions.values())[0]
        return None

    def get_current_week_stats(self) -> dict:
        """
        Audita el cumplimiento de las bases del concurso para la semana actual:
        - Mínimo 3 operaciones
        - Mínimo 2.500 € en compras
        """
        df = self.load_trades()
        current_week = self.get_bme_week_id()
        
        if len(df) == 0:
            return {
                'week_id': current_week,
                'buys_count': 0,
                'sells_count': 0,
                'total_trades': 0,
                'buy_volume_eur': 0.0,
                'sell_volume_eur': 0.0,
                'target_trades': 3,
                'target_volume_eur': 2500.0,
                'trades_remaining': 3,
                'quota_fulfilled': False
            }
            
        sub = df[df['Semana_BME'] == current_week]
        buys = sub[sub['Accion'] == 'BUY']
        sells = sub[sub['Accion'] == 'SELL']
        
        buys_count = len(buys)
        sells_count = len(sells)
        buy_vol = float(buys['Importe_EUR'].sum()) if buys_count > 0 else 0.0
        sell_vol = float(sells['Importe_EUR'].sum()) if sells_count > 0 else 0.0
        
        quota_fulfilled = (buys_count >= 3) and (buy_vol >= 2400.0)
        trades_rem = max(0, 3 - buys_count)
        
        return {
            'week_id': current_week,
            'buys_count': buys_count,
            'sells_count': sells_count,
            'total_trades': buys_count + sells_count,
            'buy_volume_eur': buy_vol,
            'sell_volume_eur': sell_vol,
            'target_trades': 3,
            'target_volume_eur': 2500.0,
            'trades_remaining': trades_rem,
            'quota_fulfilled': quota_fulfilled
        }
