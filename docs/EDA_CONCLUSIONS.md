# CONCLUSIONES EXHAUSTIVAS DEL ANÁLISIS EXPLORATORIO (EDA)
**Proyecto:** Concurso Algorítmico BME (Bolsa de Madrid)
**Objetivo:** Desarrollar un motor de trading rentable bajo restricciones estrictas (Long-Only, comisiones fijas, regla T+1, capital inicial de 50.000€).

---

## 1. Naturaleza Estructural del Mercado Español
El IBEX 35 y el Mercado Continuo no se comportan como los mercados tecnológicos americanos. Las dinámicas estructurales son únicas:

*   **Sesgo a la Reversión a la Media:** El análisis de Momentum Transversal (Cross-Sectional Rank Correlation) demostró que el 62.5% del tiempo el mercado español castiga a los ganadores del día anterior y premia los rebotes de los perdedores. La ventaja matemática está en comprar soporte y vender resistencia (*Fade the Winner / Buy the Fear*).
*   **Concentración Extrema (La Tiranía de los Gigantes):** El índice es un oligopolio dominado por Inditex, Santander, BBVA, CaixaBank e Iberdrola. Los flujos pasivos (ETFs) hacia estos gigantes arrastran mecánicamente a las empresas de mediana capitalización. El "Riesgo de Mercado" (Medido vía PCA) puede llegar a explicar más del 60% de la varianza en momentos de estrés.
*   **La Trampa del Dividendo:** Las caídas bruscas de precio en la fecha "Ex-Dividend" destruyen las métricas de los osciladores técnicos básicos. **Regla de Oro:** Todos los indicadores técnicos deben alimentarse con *Adjusted Close Prices* (Total Return).

---

## 2. Modelado de Riesgo y Sensibilidad Macro
No se puede operar estadísticamente en vacío; las empresas españolas son, en gran medida, derivados de variables macroeconómicas.

*   **Sector Bancario:** Fuerte correlación positiva con los rendimientos del Bono Soberano a 10 años.
*   **Sector Utilities y Energía:** Fuerte correlación inversa entre las Utilities (Endesa, Iberdrola) y el precio de la energía frente a productores directos (Repsol).
*   **Exposición Divisa LATAM:** BBVA actúa como un *proxy* del Peso Mexicano (MXN). Santander y Telefónica son altamente vulnerables al Real Brasileño (BRL). Estos factores actuarán como **Filtros de Régimen** en el algoritmo.

---

## 3. Comportamiento Cuantitativo (Estocástica)
El análisis dividió el mercado en dos cestas operativas, pero requiere mitigaciones específicas por las reglas del concurso:

*   **Cesta A (Reversión Pura):** Activos altamente elásticos (Hurst < 0.45 y Autocorrelación Lag 1 negativa) como Viscofan, Puig, Acciona Energía y CaixaBank. 
    *   *Filtro Direccional Obligatorio (El Cuchillo Cayendo):* Al estar restringidos a *Long-Only*, comprar la debilidad asume falsamente un mercado bidireccional. Si compramos en un mercado estructuralmente bajista, destruiremos el capital. Toda operación de la Cesta A requiere un filtro direccional primario (ej. que el Precio o el Índice esté por encima de su SMA de 200 días).
*   **Cesta B (Momentum/Tendencia):** Anomalías del mercado español con inercia direccional (Hurst > 0.50) como PharmaMar, Ence o IAG.
*   **Riesgo Nocturno y Eventos Programados (Earnings):** La vasta mayoría del mercado exhibe *Fat Tails* (curtosis extrema). Sin embargo, estos "gaps" de apertura no son totalmente aleatorios; se concentran alrededor de las presentaciones de resultados trimestrales. **Mantener una posición T+1 el día previo a un Earnings Release no es estadística, es apostar.** El algoritmo debe incorporar un bloqueo de calendario de resultados.

---

## 4. Fricción y Liquidez (Restricciones del Concurso)
La comisión de **0.15% (con mínimo de 7€)** exige un tamaño de operación superior a 4.666€ para no regalar *edge* matemático.

*   **Lista Negra (Activos Inoperables):** El algoritmo tiene prohibido operar en el percentil 10 inferior de liquidez (para evitar *slippage*): `GSJ.MC`, `CASH.MC`, `TLGO.MC`, `DOM.MC`, `TUB.MC`, `FAE.MC`, etc.

---

## 5. Modelo de Position Sizing (Gestión de Capital)
Identificar el tamaño mínimo (4.666€) no es suficiente. Cuando el sistema arroje múltiples señales simultáneas, la asignación de capital deberá seguir reglas matemáticas estrictas:

*   **Paridad de Riesgo (Inverse Volatility):** El capital no se asignará de forma equiponderada (Equal Weight). Los activos con mayor volatilidad histórica (ATR) o mayor curtosis recibirán menos capital, garantizando que el riesgo contribuido por cada posición al portfolio total sea idéntico.
*   **Función de Desempate (Tie-Breaker):** Si el motor genera 15 señales concurrentes pero el efectivo disponible (o la regla de diversificación) solo permite 4 operaciones, el algoritmo priorizará las acciones ordenándolas por su *Z-Score* de desviación sobre la media o por el mayor *Amihud Liquidity Score*.

---

## 6. Decaimiento de la Señal y Lógica de Salida (Signal Decay)
Entrar bien es la mitad del problema; retener el capital es la clave. Dado que la Autocorrelación (ACF) en el Lag 1 indica reversión para T+1, la retención prolongada deteriora la ventaja estocástica.

*   **Time Exit (Límite Máximo de Retención):** Si el modelo predecía un rebote que no se materializa, el tiempo juega en contra. Se impondrá un cierre por expiración de tiempo (ej. T+3 o T+5) si la operación sigue lateral.
*   **Trailing Stops Adaptativos:** Se usarán paradas dinámicas vinculadas al *Average True Range (ATR)* del activo en lugar de porcentajes fijos, para permitir a los valores volátiles respirar sin ser estrangulados prematuramente.
*   **Take Profits:** Órdenes límite en niveles de resistencia matemática inmediatos (ej. reversión hacia la media móvil de corto plazo).

---

## 7. Diseño Definitivo de la Arquitectura del Backtester
El motor de simulación histórico deberá seguir un modelo secuencial de 5 capas:

1.  **Capa 1: Generador de Señales:** Escáner matemático sobre precios ajustados (Mean-Reversion para Cesta A y Momentum para Cesta B).
2.  **Capa 2: Filtros de Régimen Macro y Tendencial:** Verifica el entorno (SMA 200, Bonos, Petróleo, PCA). Si el mercado está cayendo en tendencia o en pánico correlacionado, aborta.
3.  **Capa 3: Filtro de Calendario (Event Risk):** Bloquea compras y fuerza el cierre de posiciones en la víspera de la Presentación de Resultados de la empresa (Earnings Release).
4.  **Capa 4: Optimizador de Fricción (El Cajero):** Verifica la comisión de 7€ y excluye operaciones que choquen con la "Lista Negra" de liquidez.
5.  **Capa 5: Gestor de Riesgo y Asignación (Módulo Final):** Desempata señales recurrentes, calcula el *Position Sizing* vía *Inverse Volatility ATR*, impone límites de concentración sectorial y define el andamiaje del *Exit Logic* (Trailing Stops + Time Exits).
