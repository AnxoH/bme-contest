import pandas as pd
from datetime import datetime

# ==============================================================================
# CALENDARIO DE RIESGO Y EVENTOS CORPORATIVOS (BME CONTEST 2026)
# Extraído de las reglas del concurso y calendario oficial (Octubre - Noviembre 2026).
# Fuente estática in-memory: 100% fiable, sin dependencias dinámicas ni scrapers lentos.
# ==============================================================================

# 1. Calendario Macroeconómico (Bancos Centrales)
MACRO_CALENDAR = {
    '2026-10-29': [
        "BCE: Decisión de Tipos de Interés (14:15h CET) - Impacto directo en coste de deuda de utilities.",
        "BCE: Rueda de Prensa de Christine Lagarde (14:45h CET) - Alta volatilidad en mercado continuo."
    ],
    '2026-11-04': [
        "FED: Decisión de Tipos en EEUU (20:00h CET) - Condiciona la apertura europea de mañana jueves."
    ],
    '2026-11-05': [
        "BoE: Decisión de Tipos en UK (13:00h CET) - Riesgo específico para Iberdrola (IBE.MC)."
    ]
}

# 2. Calendario de Resultados 9M (Noche de Alerta a las 17:15 CET)
# La alerta salta la tarde anterior (T-1) porque la orden overnight se mantendría durante el gap de apertura.
CORPORATE_EVENING_ALERTS = {
    # Lunes 19 Oct: Enagás presenta el martes 20 BMO
    '2026-10-19': {
        'ENG.MC': "Resultados 9M mañana BMO (08:30h). Riesgo de GAP en apertura."
    },
    # Martes 20 Oct: Iberdrola presenta el miércoles 21 BMO
    '2026-10-20': {
        'IBE.MC': "Resultados 9M mañana BMO (08:30h). Riesgo de GAP en apertura."
    },
    # Martes 27 Oct: Redeia presenta el miércoles 28 BMO
    '2026-10-27': {
        'RED.MC': "Resultados 9M mañana BMO (08:30h). Riesgo de GAP en apertura."
    },
    # Jueves 29 Oct: Naturgy presenta el viernes 30 BMO
    '2026-10-29': {
        'NTGY.MC': "Resultados 9M mañana BMO (08:30h). Riesgo de GAP en apertura."
    },
    # Lunes 02 Nov: Endesa presenta el martes 3 BMO
    '2026-11-02': {
        'ELE.MC': "Resultados 9M mañana BMO (08:30h). Riesgo de GAP en apertura."
    },
    # Miércoles 04 Nov: Naturgy descuenta dividendo a cuenta el jueves 5 nov
    '2026-11-04': {
        'NTGY.MC': "Ex-Dividendo a cuenta mañana (descuento automático en precio de apertura)."
    }
}

# 3. Calendario Corporativo para la Sesión de Mañana (09:00 CET)
# Informa de eventos activos hoy para la posición que se va a liquidar en apertura.
CORPORATE_MORNING_ALERTS = {
    '2026-10-20': {
        'ENG.MC': "Resultados 9M publicados hoy BMO (08:30h)."
    },
    '2026-10-21': {
        'IBE.MC': "Resultados 9M publicados hoy BMO (08:30h)."
    },
    '2026-10-28': {
        'RED.MC': "Resultados 9M publicados hoy BMO (08:30h)."
    },
    '2026-10-30': {
        'NTGY.MC': "Resultados 9M publicados hoy BMO (08:30h)."
    },
    '2026-11-03': {
        'ELE.MC': "Resultados 9M publicados hoy BMO (08:30h)."
    },
    '2026-11-05': {
        'NTGY.MC': "Ex-Dividendo efectivo hoy (el precio descuenta el importe del cupón)."
    }
}

class CorporateEventsChecker:
    """
    Gestor estático del calendario de riesgo y eventos corporativos para el BME Contest 2026.
    Proporciona alertas transparentes sin alterar las señales cuantitativas del modelo.
    """
    def __init__(self, universe=None):
        self.universe = universe or ['RED.MC', 'ENG.MC', 'ELE.MC', 'IBE.MC', 'NTGY.MC']

    def check_events(self, date_str: str = None) -> dict:
        """
        Retorna el estado de alertas corporativas vespertinas (17:15 CET) para cada ticker.
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
            
        today_events = CORPORATE_EVENING_ALERTS.get(date_str, {})
        alerts = {}
        for ticker in self.universe:
            event_text = today_events.get(ticker)
            has_risk = event_text is not None
            
            # Format concise status tag for summary tables
            short_tag = "OK"
            if has_risk:
                if "Resultados" in event_text or "Earnings" in event_text:
                    short_tag = "[WARN] Earnings"
                elif "Ex-Dividendo" in event_text or "Ex-Div" in event_text:
                    short_tag = "[WARN] Ex-Div"
                else:
                    short_tag = "[WARN] Event"
                    
            alerts[ticker] = {
                'has_risk': has_risk,
                'alerts': [event_text] if has_risk else [],
                'status_str': short_tag,
                'detail': event_text or ""
            }
        return alerts

    def get_macro_alerts(self, date_str: str = None) -> list:
        """
        Retorna la lista de alertas macroeconómicas del día (BCE, FED, BoE).
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        return MACRO_CALENDAR.get(date_str, [])

    def get_morning_alerts(self, date_str: str = None) -> dict:
        """
        Retorna eventos que afectan a la apertura de mercado a las 09:00 CET.
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        return CORPORATE_MORNING_ALERTS.get(date_str, {})

    def get_all_alerts_summary(self, date_str: str = None) -> dict:
        """
        Retorna un resumen consolidado de alertas macro y corporativas para la sesión vespertina.
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
            
        macro = self.get_macro_alerts(date_str)
        corp = self.check_events(date_str)
        active_corp = {t: data for t, data in corp.items() if data['has_risk']}
        
        return {
            'date': date_str,
            'macro_alerts': macro,
            'has_macro': len(macro) > 0,
            'corporate_alerts': corp,
            'active_corporate': active_corp,
            'has_corporate': len(active_corp) > 0
        }

# Module-level convenience functions for quick access
_default_checker = CorporateEventsChecker()

def get_daily_macro_alerts(date_str: str = None) -> list:
    """Return active macroeconomic alerts for date_str."""
    return _default_checker.get_macro_alerts(date_str)

def get_evening_corporate_alerts(date_str: str = None) -> dict:
    """Return active corporate alerts for evening 17:15 CET session."""
    return _default_checker.check_events(date_str)

