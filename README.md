# BME Algorithmic Trading Contest Framework

Este repositorio contiene la arquitectura cuantitativa para el concurso algorítmico de BME (Bolsa de Madrid). El sistema está diseñado para separar estrictamente la lógica de simulación (motor) de la lógica de negocio (estrategias), facilitando la iteración rápida, la validación estricta y un *tracking* de experimentos exhaustivo.

## 🏗️ Arquitectura de Directorios

El framework está dividido en bloques modulares:

```text
BME_contest/
├── data/                  # Almacenamiento de datos estáticos
│   ├── raw/               # CSVs originales sin procesar (OHLCV)
│   └── processed/         # Datos limpios y normalizados (listos para ingestión)
├── src/                   # Código fuente principal del framework
│   ├── engine/            # Motor agnóstico de simulación
│   │   ├── backtester.py  # Bucle principal y control de ventanas rodantes (1 mes)
│   │   ├── portfolio.py   # Gestión de caja, comisiones (min 7€), posiciones y rebalanceo
│   │   └── tracker.py     # Sistema de logging (guarda hiperparámetros y JSONs de experimentos)
│   ├── analysis/          # Evaluación y cálculo de scores (0.6R - 0.3V)
│   ├── strategies/        # Definición de modelos (TA, ML, Exóticos)
│   │   └── base.py        # Interfaz BaseStrategy de la que heredan todas las estrategias
│   └── utils/             # Funciones auxiliares y helpers
├── experiments/           # Almacén de resultados (Experiment Tracking)
│   ├── logs/              # Archivos JSON detallados de cada corrida (metadata heterogénea)
│   └── leaderboard.csv    # Tabla de clasificación para comparar rápidamente modelos
├── notebooks/             # Entornos de investigación (EDA y prototipado)
├── scripts/               # Puntos de entrada ejecutables (ej. run_experiment.py)
├── docs/                  # Documentación generada (Conclusiones del EDA, planes)
└── notes/                 # Notas misceláneas del usuario
```

## 🔬 Sistema de Experiment Tracking (Leaderboard)

Dado que las estrategias que vamos a probar son **altamente heterogéneas** (desde simples cruces de medias hasta modelos de XGBoost o lógicas que requieran datos externos), una tabla plana de hiperparámetros no es suficiente. Por ello, hemos implementado un sistema híbrido en `src/engine/tracker.py`:

1. **JSON Logs (`experiments/logs/`):** Al ejecutar un experimento, el sistema genera un identificador único (ej. `EXP-20261007-1A2B3C`). Se crea un archivo `.json` que contiene todos los metadatos de la corrida. Aquí se guardan diccionarios anidados con listas de *features* usadas, rutas a modelos de ML, configuraciones exóticas, o la curva de *equity* diaria.
2. **Leaderboard (`experiments/leaderboard.csv`):** Un archivo plano que actúa como el ranking del concurso. Contiene el `Run_ID`, el nombre del modelo y las métricas oficiales agregadas (`Score`, `Return_1M`, `Vol_Ann`, `Win_Rate`). 
3. **Flujo de trabajo:** Miras el Leaderboard para ver qué modelo encabeza el concurso. Copias su `Run_ID` y abres su `.json` en la carpeta `logs/` para inspeccionar con qué configuraciones exactas o modelo de ML se consiguió ese resultado.

## 🚀 Cómo crear un nuevo modelo

1. Crea un nuevo archivo en `src/strategies/` (ej. `mi_estrategia.py`).
2. Haz que tu clase herede de `BaseStrategy` (desde `src/strategies/base.py`).
3. Sobrescribe el método `generate_signals()`, que recibirá los datos de mercado y devolverá las órdenes o pesos objetivo.
4. (Opcional) Sobrescribe `get_metadata()` para guardar parámetros específicos de tu modelo (hiperparámetros de la red neuronal, variables macro usadas, etc.) en los logs JSON.

## ⚖️ Metodología de Validación (Rolling Windows)

El concurso dura exactamente un mes natural de trading. Hacer un backtest tradicional (una única curva a 15 años) produce sobreoptimización irreal. Por ello, nuestro `backtester.py` utiliza **Ventanas Rodantes de 22 días** con aislamiento de capital:
* Resetea el capital cada iteración.
* Calcula las rentabilidades y penaliza duramente la volatilidad en ventanas estancadas de un mes.
* Extrae el **Valor Esperado**, el **Mejor Caso** y el **Peor Caso** que sufriríamos si somos lanzados a un mes aleatorio de mercado.
