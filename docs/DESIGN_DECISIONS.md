# DOCUMENTO DE DISEÑO ARQUITECTÓNICO (DESIGN_DECISIONS.md)
**Proyecto:** Framework Cuantitativo - El Concurso de Bolsa 2026
**Objetivo:** Especificación de restricciones del simulador y decisiones de ingeniería algorítmica.

---

## 1. RESTRICCIONES ESTRUCTURALES DEL ENTORNO (Bases del Concurso)

Cualquier backtest que no integre estas reglas generará *look-ahead bias* o *execution bias*, invalidando la esperanza matemática del modelo.

*   **Restricción Direccional (Long-Only):** Prohibidas las posiciones cortas. El modelo solo puede generar retornos capturando alzas directas en el precio de los activos.
*   **Bloqueo de Inventario (Regla T+1):** 
    *   Activo comprado en Día 0 no puede venderse hasta el Día 1.
    *   Activo vendido en Día 0 no puede recomprarse hasta el Día 1.
    *   *Efecto de Agregación:* Ampliar una posición antigua bloquea la totalidad del bloque hasta la siguiente sesión.
*   **Fricción de Capital (Comisiones):** 0,15% sobre efectivo con un mínimo de 7 € por operación. 
    *   *Derivada Matemática:* El tamaño mínimo absoluto por orden debe ser **4.667 €**. Órdenes inferiores sufren un impacto porcentual asimétrico que destruye el Alpha. Se establece un target de **10.000 € por operación**.
*   **Restricción de Supervivencia:** Desde el 22 de octubre, ejecución obligatoria de mínimo 3 compras y 3 ventas por semana (mínimo 2.500 € agregados por lado).
*   **Métricas de Evaluación:** Ranking relativo de Rentabilidad (60%) y penalización por Volatilidad Diaria de la cartera (30%). El efectivo tiene volatilidad cero.

---

## 2. DECISIONES DE INGENIERÍA Y MICROESTRUCTURA

Para adaptar el algoritmo a las restricciones operativas y a la infraestructura de datos gratuita, se han consolidado las siguientes decisiones de diseño:

### 2.1. Ingesta y Universo de Datos
*   **Proveedor de Datos:** APIs gratuitas (EOD) mediante `yfinance` (sufijo `.MC`), utilizando precios ajustados (`Adj Close`) para absorber dividendos y *splits*.
*   **Profundidad Histórica:** Limitada a los últimos **5 a 10 años** (aprox. 1.250 - 2.500 sesiones).
    *   *Razón:* Previene el *Concept Drift* (cambio de régimen de mercado, MiFID II, HFT) y minimiza el *Survivorship Bias* (sesgo de supervivencia al no tener datos de empresas quebradas/excluidas hace 15 años). Evita además datos pre-Euro o de sistemas de negociación obsoletos.
*   **Filtro Estricto de Liquidez (Exclusión de "Chicharros"):** El universo invertible se restringe al IBEX 35 y Midcaps de alta liquidez.
    *   *Razón 1 (Regla de los 2 minutos):* El simulador bloquea órdenes si el activo no cruza operaciones en 2 minutos. Los activos ilíquidos provocarían fallos continuos de ejecución algorítmica.
    *   *Razón 2 (Market Impact):* Órdenes de 10.000 € en activos de bajísimo volumen distorsionarían el precio real. Operarlos en el simulador genera *Paper Trading Alpha* (ganancias falsas imposibles de replicar en el mercado real).

### 2.2. Paradigma de Ejecución (End-of-Day vs Intradía)
*   **Ventana de Ejecución:** El algoritmo se ejecutará diariamente a las **17:29 h**, un minuto antes de la subasta de cierre (17:30 h). No se operará intradía (ej. 12:00 h).
    *   *Razón 1 (Consistencia de Datos):* Los indicadores técnicos (RSI, Bollinger) o features de ML basados en gráficos diarios solo adquieren validez matemática en el cierre de la sesión.
    *   *Razón 2 (Gestión del Riesgo T+1):* Comprar a las 10:00 h obliga a asumir 7.5 horas de exposición a mercado con las manos atadas (no se puede vender por la regla T+1). Comprar a las 17:29 h minimiza el riesgo del Día 0 y habilita la venta inmediata en la apertura del Día 1.
*   **Exclusión de Subastas de Volatilidad:** Se ignoran por completo los precios indicativos de las subastas de apertura (08:30-09:00) y cierre (17:30-17:35).
    *   *Razón:* Son precios de equilibrio teóricos sujetos a manipulación de volumen institucional (*Spoofing*) y cancelaciones de último segundo. No son ejecutables en la realidad ni válidos en el simulador.

---

## 3. PIPELINE DE DESARROLLO DEL FRAMEWORK

El flujo de trabajo en VSCode seguirá una arquitectura secuencial estricta:

1.  **Data Pipeline:** Ingesta vectorizada de 5-10 años de datos (`yfinance`), limpieza y aplicación del filtro de liquidez (volumen medio negociado).
2.  **Constraints Engine (El Backtester):** Construcción del motor de simulación. Se debe programar la clase base que asimile matemáticamente las comisiones (0.15% / 7€) y los bloqueos de inventario (T+1).
3.  **Exploratory Data Analysis (EDA):** Medición estadística de la volatilidad intrínseca del universo filtrado, gaps overnight y distribución de los retornos diarios.
4.  **Alpha Generation:** Codificación de señales heurísticas o entrenamiento del modelo de Machine Learning.
5.  **Simulación y Validación:** Inyección de las señales en el *Constraints Engine*. Evaluación del Ratio de Sharpe, Expectativa Matemática por trade y Maximum Drawdown.
6.  **Módulo de Producción:** Script final que lee los datos diarios en vivo y escupe las órdenes exactas a introducir manualmente en la plataforma del concurso a las 17:29 h.


## 4. OTROS ELEMENTOS IMPORTANTES
Además de la generación de alpha mediante estrategias de trading algorítmico, se deberán de tener en cuenta elementos del calendario corporativo relevantes dentro del mercado español, como por ejemplo:
1. Reparto de dividendos
2. Presentación de resultados Q3
3. Reunión para fijar los tipos del BCE
4. Presentación de resultados de empleo EE.UU
5. Elecciones midterm EE.UU