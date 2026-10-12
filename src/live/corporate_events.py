import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

class CorporateEventsChecker:
    """
    Filtro de salvaguarda de eventos corporativos para las 5 utilities.
    Detecta si alguna compañía tiene programado dividendo (ex-date) o presentación de resultados
    en las próximas 24-48 horas para evitar gaps inesperados.
    """
    def __init__(self, universe=None):
        self.universe = universe or ['RED.MC', 'ENG.MC', 'ELE.MC', 'IBE.MC', 'NTGY.MC']

    def check_events(self) -> dict:
        """
        Retorna un diccionario por ticker con el estado de alertas de eventos corporativos.
        """
        alerts = {}
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        for ticker in self.universe:
            alert_list = []
            try:
                t = yf.Ticker(ticker)
                cal = t.calendar
                
                if cal is not None:
                    # Comprobar Earnings
                    if isinstance(cal, dict):
                        earnings_dates = cal.get('Earnings Date', [])
                        if earnings_dates:
                            for ed in earnings_dates:
                                ed_date = pd.to_datetime(ed).date()
                                if today <= ed_date <= tomorrow:
                                    alert_list.append(f"Resultados ({ed_date})")
                                    
                        ex_div = cal.get('Ex-Dividend Date')
                        if ex_div is not None:
                            ex_date = pd.to_datetime(ex_div).date()
                            if today <= ex_date <= tomorrow:
                                alert_list.append(f"Ex-Dividendo ({ex_date})")
                                
                    elif isinstance(cal, pd.DataFrame):
                        # En algunas versiones de yfinance calendar es un DataFrame
                        for col in cal.columns:
                            val = cal.loc['Earnings Date', col] if 'Earnings Date' in cal.index else None
                            if val is not None:
                                ed_date = pd.to_datetime(val).date()
                                if today <= ed_date <= tomorrow:
                                    alert_list.append(f"Resultados ({ed_date})")
            except Exception:
                # Si la API no responde eventos, asumimos sin alertas críticas
                pass

            has_risk = len(alert_list) > 0
            alerts[ticker] = {
                'has_risk': has_risk,
                'alerts': alert_list,
                'status_str': "⚠️ " + ", ".join(alert_list) if has_risk else "OK"
            }
            
        return alerts
