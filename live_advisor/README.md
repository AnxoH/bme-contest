# Módulo Live Advisor (Producción y Tiempo Real)

Este paquete contiene la arquitectura para la ejecución en vivo del concurso BME a las 17:25:

- `market_fetcher.py`: Descarga y estandariza los precios de la sesión (Open, High, Low, Close actual) de las 5 utilities (`RED.MC`, `ENG.MC`, `ELE.MC`, `IBE.MC`, `NTGY.MC`) e histórico de 20 días.
- `calendar_guard.py`: Valida si el día actual es hábil de compra (Lunes a Miércoles dentro de las 3 semanas de concurso), detecta festivos y asegura el cumplimiento del periodo de gracia (13 al 21 de octubre) y bloqueo de fin de semana.
- `decision_engine.py`: Implementa el cross-ranking de `Ensemble_CS_NR` y `MicroAlfa_CS` para determinar la acción óptima del día.
- `order_tracker.py`: Auditoría local en `logs/daily_trades.json` para llevar el control del volumen semanal acumulado (garantizando superar los 2.500 € con 3 órdenes de 900 €).

