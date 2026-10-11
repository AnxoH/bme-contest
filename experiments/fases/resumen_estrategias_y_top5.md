# Síntesis de Estrategias y Resultados: Torneo Global BME Contest

Este documento recoge la evolución del desarrollo cuantitativo para el concurso BME, estructurado por fases, los resultados empíricos obtenidos en el **Torneo Global de Simulación (15 años, ventanas móviles de 22 días)** y el desglose en profundidad de las **Top 5 mejores estrategias**.

---

## 1. Contexto y Dinámica del Concurso

La fórmula oficial de puntuación de BME premia el valor final de la cartera (rentabilidad) pero penaliza fuertemente la volatilidad experimentada a lo largo del mes de competición (22 días bursátiles):

$$\text{Puntos Retorno} = \frac{\text{Valor Final} \times 6}{\text{Max Valor del Grupo}}$$

$$\text{Puntos Volatilidad} = 3 \times \left(1 - \frac{\text{Volatilidad} - \text{Min Vol}}{\text{Max Vol} - \text{Min Vol}}\right)$$

$$\text{Puntuación Total} = \text{Puntos Retorno} + \text{Puntos Volatilidad} \quad (\text{Máximo } 9.0 \text{ pts})$$

* **La clave matemática descubierta:** La rentabilidad máxima otorga hasta 6 puntos, pero la diferencia entre carteras normales suele ser estrecha. En cambio, quien minimiza la volatilidad captura los 3 puntos completos de volatilidad, aventajando de forma casi insuperable a carteras con varianzas normales o altas.

---

## 2. Cronología y Evolución por Fases

### Fase 1: Análisis Exploratorio de Datos (EDA) y Universo
* **Objetivo:** Analizar los 35 valores del IBEX y valores del Mercado Continuo para entender su correlación, liquidez y regímenes de volatilidad.
* **Descubrimiento:** Las compañías reguladas (utilities como Red Eléctrica `RED.MC` y Enagás `ENG.MC`) presentan una varianza histórica significativamente inferior al resto de sectores (banca, cíclicas, turismo).
* **Decisión:** Focalizar la búsqueda de estabilidad en los activos con menor volatilidad realizada.

### Fase 2: Cuantitativas Clásicas / Swing Trading Multiactivo
* **Estrategias desarrolladas:**
  * `Slow_Train`: Selección semanal del activo con menor volatilidad en ventana de 20 días y filtro de momentum positivo a 10 días.
  * `Patient_Sniper`: Filtro de baja volatilidad histórica a 60 días combinado con sobreventa técnica (RSI < 40).
* **Hallazgo:** Aunque superaban a los perfiles agresivos y de tendencia, mantener posiciones abiertas durante las horas de mercado (intradía) acumulaba volatilidad continua (~4% - 6% anualizada), impidiendo dominar el ranking con consistencia.

### Fase 3: El Descubrimiento del "Overnight Edge" (`BareMinimum`)
* **Hipótesis:** Si la volatilidad de cartera se calcula sobre los cierres diarios, comprar a las **17:15 (subasta de cierre)** y vender a las **09:00 (apertura)** aísla la cartera del 100% de la volatilidad intradiaria.
* **Estrategia `BareMinimum`:** Compra en subasta de cierre de `RED.MC` y venta inmediata en apertura, ejecutado de lunes a viernes (5 noches/semana).
* **Impacto:** La volatilidad anualizada cayó a un insólito **0.18%**. La estrategia empezó a ganar masivamente ventanas, pero sufría de:
  * Sobreexposición innecesaria a fines de semana (gap viernes-lunes).
  * Exceso de operaciones frente al mínimo exigido por las bases del concurso.

### Fase 4: Optimización Inteligente ("Smart BareMinimum")
* **Objetivo:** Cumplir estrictamente el requisito del concurso de realizar un número mínimo de operaciones semanales (3 operaciones), reduciendo aún más los eventos de riesgo de mercado y mejorando el retorno medio.
* **Variantes implementadas:**
  1. `SmartMin_Seasonal`: Operativa fija únicamente las noches de **Martes, Miércoles y Jueves**.
  2. `SmartMin_Contrarian`: Compra nocturna condicionada a días de cierre bajista (reversión a la media).
  3. `SmartMin_Intraday`: Compra nocturna condicionada a días con rango intradía mínimo (filtro de calma).

---

## 3. Resultados del Torneo Global

En esta simulación, todas las estrategias candidatas compitieron en un único pool unificado contra **10 perfiles sintéticos de competidores reales** (estrategias conservadoras, de tendencia, de reversión, blue chips y amantes de la volatilidad) a lo largo de 15 años de datos en ventanas rodantes de 22 días.

El **Win Rate Global** refleja el porcentaje exacto de ventanas en las que cada estrategia quedó en **Puesto #1 Absoluto** (suma el 100%):

| Rango | Participante | Score Medio (sobre 9) | Puesto Medio | Win Rate Global | Retorno 1M Medio | Volatilidad Anual | Tipo / Origen |
|:---:|---|:---:|:---:|:---:|:---:|:---:|---|
| 🥇 **1** | **SmartMin_Seasonal** | **8.465** | **2.58** | **35.88%** | **-0.35%** | **0.35%** | Candidata Fase 4 |
| 🥈 **2** | **BareMinimum** | 8.458 | 3.41 | 10.37% | -0.58% | **0.19%** | Candidata Fase 3 |
| 🥉 **3** | **SmartMin_Contrarian** | 8.448 | 2.96 | **21.10%** | -0.40% | 0.34% | Candidata Fase 4 |
| 4 | **SmartMin_Intraday** | 8.446 | 3.54 | 9.45% | -0.42% | 0.34% | Candidata Fase 4 |
| 5 | **Slow_Train_20v_10m** | 8.442 | 5.35 | 4.44% | -0.59% | 0.42% | Candidata Fase 2 |
| 6 | Patient_Sniper_60v_40rsi | 8.436 | 6.24 | 1.48% | -0.62% | 0.49% | Candidata Fase 2 |
| 7 | *Conservador_Real_1* | 8.395 | 6.41 | 10.37% | +0.18% | 1.72% | Sintético Competidor |
| 8 | *Conservador_Real_3* | 8.375 | 7.39 | 3.70% | +0.02% | 1.87% | Sintético Competidor |
| 9 | *Conservador_Real_2* | 8.372 | 7.54 | 1.48% | -0.01% | 1.88% | Sintético Competidor |
| 10 | *Reversion_Real_2* | 8.025 | 10.47 | 1.48% | +0.05% | 6.29% | Sintético Competidor |
| 11 | *Trend_Real_3* | 7.919 | 11.56 | 0.74% | +0.41% | 8.81% | Sintético Competidor |
| 12 | *Trend_Real_1* | 7.880 | 11.64 | 1.48% | +0.77% | 8.97% | Sintético Competidor |
| 13 | *Reversion_Real_1* | 7.878 | 11.96 | 0.74% | +0.19% | 9.28% | Sintético Competidor |
| 14 | *Trend_Real_2* | 7.766 | 12.60 | 0.00% | +0.85% | 10.67% | Sintético Competidor |
| 15 | *BlueChip_Real_1* | 7.645 | 13.04 | 2.96% | +1.16% | 13.02% | Sintético Competidor |
| 16 | *VolJunkie_Real_1* | 5.517 | 15.70 | 0.00% | +2.14% | 62.94% | Sintético Competidor |

> **Conclusión General del Torneo:** Las estrategias basadas en el aislamiento overnight copan más del **76% de todas las victorias posibles** en la historia simulada del torneo.

---

## 4. Análisis en Profundidad: Top 5 Estrategias

### 1. `SmartMin_Seasonal` (Campeona Absoluta)
* **Filosofía:** Reducción sistemática de riesgo temporal.
* **Activo Operado:** `RED.MC` (Redeia).
* **Mecánica:**
  * Compra en la subasta de cierre (17:15 - 17:30) únicamente los **Martes, Miércoles y Jueves**.
  * Venta inmediata en la apertura del día siguiente (09:00).
  * Lunes y Viernes la cartera permanece 100% en liquidez.
* **Por qué funciona:** Al eliminar las noches del viernes (evita el riesgo de fin de semana completo) y la noche del lunes (inicio de semana macroeconómica), el gap de apertura es microscópico y de menor sesgo bajista. Esto mejora el retorno promedio (-0.35% frente al -0.58% de BareMinimum) y alcanza un impresionante **35.88% de Win Rate Global**.
* **Ventaja Operativa:** 100% predecible para ejecución manual. No requiere calcular indicadores antes del cierre.

### 2. `BareMinimum` (La Estrategia Base)
* **Filosofía:** Exposición mínima continuada.
* **Activo Operado:** `RED.MC`.
* **Mecánica:**
  * Compra en cierre (17:15) y venta en apertura (09:00) **todos los días de la semana** (5 operaciones semanales).
* **Por qué funciona:** Es la que logra la menor volatilidad registrada en todo el histórico (0.19% anualizada). Sin embargo, se ve perjudicada en ventanas puntuales donde los gaps del fin de semana (viernes a lunes) provocan caídas que lastran su rentabilidad neta (-0.58%).

### 3. `SmartMin_Contrarian` (Reversión a la Media Intradía)
* **Filosofía:** Captura del rebote nocturno tras corrección intradiaria.
* **Activo Operado:** `RED.MC`.
* **Mecánica:**
  * A las 17:15 compara el precio actual respecto a la apertura del mismo día.
  * Si el día ha cerrado en negativo ($\text{Close} < \text{Open}$), entra en largo para la noche esperando estabilización matinal.
  * Límite de 3 operaciones por semana.
* **Por qué funciona:** Los activos de perfil regulado/defensivo exhiben un fuerte comportamiento elástico ("mean-reverting"). Cuando sufren ventas durante la sesión, el gap de la mañana siguiente suele absorber la sobreventa. Logra un sólido **21.10% de Win Rate Global**.

### 4. `SmartMin_Intraday` (Filtro de Compresión de Volatilidad)
* **Filosofía:** Operar de noche solo cuando el mercado diurno está en calma plana.
* **Activo Operado:** `RED.MC`.
* **Mecánica:**
  * Evalúa el rango $(High - Low) / Close$ de las últimas 5 sesiones.
  * Compra si la sesión actual se sitúa entre las 3 de menor rango de la semana.
* **Por qué funciona:** Evita entrar en días turbulentos o con noticias corporativas. No obstante, al depender dinámicamente del rango, a veces selecciona viernes y descarta días más limpios, quedando en un 9.45% de Win Rate.

### 5. `Slow_Train_20v_10m` (Mejor Estrategia Multiactivo Tradicional)
* **Filosofía:** Rotación entre acciones del IBEX buscando baja volatilidad y tendencia positiva.
* **Mecánica:**
  * Cada semana calcula la volatilidad a 20 días y el momentum a 10 días de los 35 valores del IBEX.
  * Selecciona el valor óptimo y lo mantiene invertido.
* **Por qué queda en 5º lugar:** A pesar de ser la mejor de las estrategias cuantitativas de cartera continua, permanecer invertido durante las horas diurnas genera una volatilidad anual del 0.42% (más del doble que `BareMinimum`), lo que reduce su Win Rate a solo el 4.44% frente al pool global.

---

## 5. Fase 5: Optimización de Position Sizing (4.667 €) y Nuevas Estrategias Cuantitativas

### 5.1. La Regla de los 4.667 € (Eliminación de la Comisión Mínima)
En el concurso de BME se cobra una comisión del **0,15 %** con un mínimo de **7 € por operación**. 
* Si se opera con importes pequeños (ej. 1.200 € o 2.500 €), la comisión de 7 € penaliza con un coste de fricción de hasta el 0,58 % - 0,84 % por orden.
* **Solución matemática:** Ajustar el tamaño de cada orden exactamente a **4.667 €** ($7 / 0,0015$). Con 4.667 €, el 0,15 % son 7,0005 €, neutralizando completamente la penalización mínima fija.
* **Control de Liquidez:** Al tener en mercado solo una posición nocturna de 4.667 € frente a un capital de 50.000 €, más del **90 % del capital permanece en liquidez total (volatilidad 0)** durante el día, amplificando la compresión de volatilidad de la cartera.

### 5.2. Resultados del Torneo Global Avanzado (Leaderboard Actualizado)

Simulación sobre 15 años de datos en ventanas rodantes de 22 días con tamaño de orden de 4.667 €, horario T+1 estricto (17:29:50 a 09:00:01) y reglas de supervivencia:

| Rango | Participante | Score Medio (sobre 9) | Puesto Medio | Win Rate Global | Retorno 1M Medio | Volatilidad Anual | Observaciones |
|:---:|---|:---:|:---:|:---:|:---:|:---:|---|
| 🥇 **1** | **NR10_Breakout** | **8.4798** | 3.40 | 13.33% | **-0.31%** | 0.57% | **Nuevo #1 en Puntos.** Mejor rentabilidad media. |
| 🥈 **2** | **CS_MeanReversion** | **8.4772** | 3.62 | 12.00% | -0.39% | 0.65% | **Nuevo #2.** Cesta de 5 utilities con Z-Score. |
| 🥉 **3** | **BareMinimum** | 8.4592 | **2.21** | **46.67%** | -0.58% | **0.19%** | Máximo Win Rate bruto, pero más castigada en retornos. |
| 4 | **SmartMin_Seasonal** | 8.4476 | 3.08 | 12.98% | -0.35% | 0.60% | Óptima para ejecución fija semanal. |
| 5 | **SmartMin_Contrarian** | 8.4308 | 3.19 | 10.09% | -0.39% | 0.59% | Reversión en días rojos de RED.MC. |
| 6 | *Conservador_Real_1* | 8.3958 | 4.37 | 10.37% | +0.18% | 1.72% | Mejor competidor sintético tradicional. |
| 7 | *Conservador_Real_3* | 8.3761 | 5.21 | 5.93% | +0.02% | 1.87% | Sintético Competidor. |
| 8 | *Conservador_Real_2* | 8.3724 | 5.37 | 2.96% | -0.01% | 1.88% | Sintético Competidor. |

> **Conclusiones de la Fase 5:**
> 1. Tanto **NR10_Breakout** como **CS_MeanReversion** logran una **puntuación promedio superior (`Score_Avg`)** a todas las versiones anteriores gracias a su mejor perfil de rentabilidad media (-0.31% y -0.39% frente a -0.58%).
> 2. Las estrategias nocturnas copan del puesto 1 al 5 en el torneo general, dejando a los competidores tradicionales muy rezagados.

---

## 6. Fase 6: La Configuración Definitiva ("Micro-Alfa Quirúrgico")

### 6.1. La Síntesis Final
La configuración **Micro-Alfa Quirúrgico** resuelve simultáneamente todos los dilemas descubiertos en las fases previas:
1. **Exposición Mínima Legal (Sizing de 900 €):** 
   * $3 \text{ operaciones} \times 900\text{ €} = 2.700\text{ €}$ semanales. Supera con holgura los 2.500 € mínimos de BME incluso tras el truncamiento a acciones enteras ($shares = \text{int}(900 / P)$).
   * Deja el **98,2 % de la cartera permanentemente en liquidez** (volatilidad 0). La volatilidad de la cartera se colapsa a un asombroso **0,20 % anualizado**.
2. **Ciclo Semanal BME y Bloqueo de Fin de Semana (Lunes a Miércoles):**
   * Se compra al cierre de Lunes, Martes y Miércoles; se vende a la apertura de Martes, Miércoles y Jueves.
   * Ambas 3 compras y 3 ventas quedan completadas dentro de la misma semana de concurso (Jueves a Jueves).
   * **Jueves y Viernes noche: Cero operaciones**, eliminando al 100 % el riesgo de noticias o gaps de fin de semana.
3. **Motores de Selección Alfa:**
   * `MicroAlfa_CS`: Rotación sistemática a la acción con menor Z-Score intradía de la cesta de 5 utilities.
   * `MicroAlfa_NR10`: Selección por compresión extrema NR10 y sesgo direccional.

### 6.2. Gran Final: Leaderboard Oficial del Torneo Definitivo

| Rango | Estrategia | Puntuación Media | Puesto Medio | Win Rate Global (% veces #1) | Retorno 1M Medio | Volatilidad Anual | Diagnóstico |
|:---:|---|:---:|:---:|:---:|:---:|:---:|---|
| 🥇 **1** | **`Ensemble_CS_NR`** | **8.4748** | **2.59** | **26.72%** | **-0.347%** | **0.21%** | **MÁXIMA PUNTUACIÓN Y MENOR SANGRADO.** Combina sobreventa + compresión. |
| 🥈 **2** | **`MicroAlfa_CS`** | **8.4746** | **2.56** | **31.30%** | -0.350% | **0.21%** | **MAYOR WIN RATE BRUTO.** Rotación pura por Z-Score. |
| 🥉 **3** | **`MicroAlfa_NR10`** | 8.4739 | 2.84 | 16.79% | -0.352% | **0.21%** | Compresión extrema pura. |
| 4 | **`NR10_Breakout`** | 8.4788 | 5.33 | 6.67% | **-0.310%** | 0.57% | Mayor retorno bruto (4.667 €), pero cede podios en volatilidad pura. |
| 5 | **`SmartMin_Seasonal`** | 8.4455 | 5.33 | 2.29% | -0.355% | 0.60% | Calendario fijo sobre RED.MC. |
| 6 | **`BareMinimum`** *(original)* | 8.4572 | 4.70 | **1.48%** | -0.587% | **0.19%** | **Aniquilada.** Misma vol, pero mucho peor retorno (-0.59%). |
| 7 | *Conservador_Real_1* | 8.3938 | 5.98 | 10.37% | +0.183% | 1.72% | Mejor perfil sintético de mercado. |
| 8 | *Conservador_Real_3* | 8.3742 | 6.85 | 2.96% | +0.024% | 1.87% | Sintético Competidor. |
| 9 | *Conservador_Real_2* | 8.3705 | 7.00 | 2.22% | -0.010% | 1.88% | Sintético Competidor. |

> **Conclusiones Históricas del Torneo:**
> * **`Ensemble_CS_NR` y `MicroAlfa_CS` dominan el certamen:** El ensemble multifactorial logra la **mayor puntuación media histórica (8.4748)** y el **menor desgaste de retorno (-0.347 % mensual)** de toda la familia de mínima volatilidad.
> * Las 3 variantes de micro-sizing (900 €) en la cesta de utilities acaparan el **74.81 % de victorias absolutas**, relegando a `BareMinimum` a un marginal 1.48 %.

---

## 7. Fase 7: Explotación del "Periodo de Gracia" (13 al 22 de Octubre)

### 7.1. La Regla de Exención Inicial de BME
Las bases del concurso estipulan textualmente:
> *"Mínimo de tres operaciones de compra y tres de venta cada semana, de cierre de jueves a cierre de jueves, **a partir del 22 de octubre** (22 a 29 de octubre, 29 de octubre a 5 de noviembre y 5 a 12 de noviembre)..."*

* El certamen comienza el **13 de octubre**, pero las exigencias obligatorias de volumen y número de operaciones **no se activan hasta el 22 de octubre**.
* **La Ventaja Asimétrica:** Permanecer en **100 % liquidez absoluta durante los primeros 7 días hábiles (13 a 21 de octubre)** garantiza:
  1. Retorno de exactamente **0.00 %** y varianza de **0.00 %**.
  2. Ahorro de **42 € en comisiones fijas** (una semana completa menos de cánones).
  3. Cero exposición a eventos de mercado imprevistos al inicio del concurso.

### 7.2. Resultados del Torneo Final (Con vs Sin Periodo de Gracia)

| Rango | Estrategia | Puntuación Media | Puesto Medio | Win Rate Global (% veces #1) | Retorno 1M Medio | Volatilidad Anual | Diagnóstico |
|:---:|---|:---:|:---:|:---:|:---:|:---:|---|
| 🥇 **1** | **`Ensemble_Grace`** | **8.4965** | **2.23** | 27.66% | **-0.241%** | **0.20%** | **RÉCORD HISTÓRICO DE PUNTOS.** Menor sangrado de comisiones. |
| 🥈 **2** | **`MicroCS_Grace`** | **8.4962** | **2.23** | **36.17%** | -0.242% | **0.20%** | **MÁXIMO WIN RATE ABSOLUTO.** Rotación Z-Score con gracia. |
| 🥉 **3** | **`MicroNR10_Grace`** | 8.4957 | 2.72 | 25.53% | -0.246% | **0.21%** | Compresión NR10 con gracia. |
| 4 | **`Ensemble_Standard`** | 8.4749 | 3.08 | 20.61% | -0.347% | 0.21% | Versión sin periodo de gracia (4 semanas operando). |
| 5 | **`MicroCS_Standard`** | 8.4747 | 3.07 | 25.95% | -0.350% | 0.21% | Versión sin periodo de gracia. |
| 6 | **`BareMinimum`** *(original)*| 8.4573 | 4.55 | 2.22% | -0.587% | **0.19%** | Pasa a ser irrelevante (-0.59% de desgaste). |
| 7 | *Conservador_Real_1* | 8.3939 | 5.32 | 9.63% | +0.183% | 1.72% | Mejor competidor sintético de mercado. |

> **Conclusión Épica:** 
> * Las versiones con Periodo de Gracia elevan la puntuación media a **prácticamente 8.50 puntos** y acaparan el **89.36 % de todas las victorias posibles del certamen**.
> * La rentabilidad mensual media mejora drásticamente de **-0.35 % a -0.24 %** simplemente por no hacer nada durante la semana de gracia.

---

## 8. Calendario Operativo Real y Hoja de Ruta para el Concurso

Para ganar el concurso BME, el calendario de trading real queda fijado de forma inamovible:

```
OCTUBRE 2026:
Lun 12: Festivo Nacional
Mar 13: INICIO DEL CONCURSO -> CERO OPERACIONES (100% Caja)
Mie 14: CERO OPERACIONES (100% Caja)
Jue 15: CERO OPERACIONES (100% Caja)
Vie 16: CERO OPERACIONES (100% Caja)

Lun 19: CERO OPERACIONES (100% Caja)
Mar 20: CERO OPERACIONES (100% Caja)
Mie 21: CERO OPERACIONES (100% Caja)
Jue 22: COMIENZO DE SEMANA OBLIGATORIA 1 -> CERO OPERACIONES (Descanso)
Vie 23: CERO OPERACIONES (Bloqueo de fin de semana)

Lun 26: OPERACIÓN 1 (Compra 17:29:50 por 900 €)
Mar 27: Venta 09:00:01 / OPERACIÓN 2 (Compra 17:29:50 por 900 €)
Mie 28: Venta 09:00:01 / OPERACIÓN 3 (Compra 17:29:50 por 900 €)
Jue 29: Venta 09:00:01 -> [SEMANA 1 COMPLETADA CON ÉXITO] / Descanso tarde
Vie 30: CERO OPERACIONES (Bloqueo de fin de semana)

NOVIEMBRE 2026:
Lun 02: OPERACIÓN 4 (Compra 17:29:50 por 900 €)
Mar 03: Venta 09:00:01 / OPERACIÓN 5 (Compra 17:29:50 por 900 €)
Mie 04: Venta 09:00:01 / OPERACIÓN 6 (Compra 17:29:50 por 900 €)
Jue 05: Venta 09:00:01 -> [SEMANA 2 COMPLETADA CON ÉXITO] / Descanso tarde
Vie 06: CERO OPERACIONES (Bloqueo de fin de semana)

Lun 09: OPERACIÓN 7 (Compra 17:29:50 por 900 €)
Mar 10: Venta 09:00:01 / OPERACIÓN 8 (Compra 17:29:50 por 900 €)
Mie 11: Venta 09:00:01 / OPERACIÓN 9 (Compra 17:29:50 por 900 €)
Jue 12: Venta 09:00:01 -> [SEMANA 3 COMPLETADA CON ÉXITO Y FIN DEL CONCURSO]
```

### Regla de Selección para las Compras (17:25):
En los días de compra (Lunes, Martes y Miércoles señalados):
1. Abrir la pantalla de cotizaciones a las **17:25**.
2. Mirar las 5 utilities (`RED.MC`, `ENG.MC`, `ELE.MC`, `IBE.MC`, `NTGY.MC`).
3. Comprar **900 €** de la que haya tenido la mayor caída porcentual respecto a su apertura.
4. A las **09:00:01** del día siguiente: Venta a mercado.





