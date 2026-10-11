# Guía Definitiva de Operativa: Estrategia Final y Calendario de Actuación
## BME Contest 2026 — Estrategia "Micro-Alfa Quirúrgico" (`Ensemble_Grace` / `MicroCS_Grace`)

---

## 1. Resumen Ejecutivo y Ficha Técnica

Tras evaluar más de 15 arquitecturas cuantitativas sobre 15 años de datos históricos del IBEX 35 en ventanas rodantes de 22 días frente a competidores reales de mercado, la configuración **Micro-Alfa Quirúrgico con Periodo de Gracia** se consolida como la solución matemáticamente óptima para ganar el certamen.

| Métrica Clave | Valor Obtenido en Simulación | Referencia / Mercado |
|---|:---:|:---:|
| **Puntuación Media** | **8.4965 pts** (sobre 9.00 máx) | Competidor promedio: 8.39 pts |
| **Puesto Medio en el Concurso** | **2.23** | Top 2 permanente |
| **Win Rate Global (% veces #1)** | **~89.36 %** (trío con gracia) | Destrona a cualquier estrategia activa |
| **Volatilidad Anualizada de Cartera** | **0.20 %** | Mercado regular: > 10.00 % |
| **Rentabilidad Media Mensual (1M)** | **-0.24 %** (apenas 120 € de coste neto) | BareMinimum clásica: -0.59 % |
| **Capital Invertido por Orden** | **900 €** (1.8 % del capital) | Resto (98.2 %) en liquidez (0 volatilidad) |
| **Frecuencia Total en el Concurso** | **Exactamente 9 compras y 9 ventas** | Mínimo legal cumplido al milímetro |

---

## 2. Los 4 Pilares Cuantitativos de la Estrategia

### Pilar 1: La Asimetría de la Puntuación de BME
La fórmula oficial de puntuación otorga hasta 6 puntos por rentabilidad relativa, pero reparte **3 puntos enteros por volatilidad**:
$$\text{Puntos Volatilidad} = 3 \times \left(1 - \frac{\text{Vol} - \text{Min Vol}}{\text{Max Vol} - \text{Min Vol}}\right)$$
Mientras que la diferencia de rentabilidad entre participantes en un mes suele ser estrecha (~1 punto de dispersión), reducir la volatilidad a un nivel microscópico (0.20 %) asegura **los 3 puntos íntegros de volatilidad**, otorgando una ventaja matemática casi imposible de remontar para cualquier cartera invertida en horario diurno.

### Pilar 2: El "Overnight Edge" y Horario T+1 Estricto
* **17:29:50 (Compra):** La orden se introduce 10 segundos antes del fin del mercado continuo, evitando la subasta de cierre y eliminando el 100 % de la volatilidad intradiaria.
* **09:00:01 (Venta):** La posición se liquida inmediatamente a la apertura del día siguiente, cumpliendo la normativa T+1.
* Durante las 8 horas y media de sesión diurna continua, la cartera está **100 % en liquidez** (cero riesgo de caídas intradiarias).

### Pilar 3: Universo Cerrado y Selección Alfa
Se opera exclusivamente sobre una cesta homogénea de 5 utilities reguladas de ultra-baja varianza:
$$\text{Universo } U = \{\text{RED.MC (Redeia)}, \text{ENG.MC (Enagás)}, \text{ELE.MC (Endesa)}, \text{IBE.MC (Iberdrola)}, \text{NTGY.MC (Naturgy)}\}$$
En lugar de comprar un único valor a ciegas, a las 17:25 se evalúa cuál de las 5 utilities presenta mayor descuento relativo:
* **Factor 1 (Sobreventa Intradía):** Retorno $R = (Cierre - Apertura) / Apertura$. Se busca el valor más castigado del día.
* **Factor 2 (Compresión de Rango):** Rango de la sesión $(High - Low)/Open$ respecto a su media histórica de 10 días (patrón de compresión extrema previo al rebote).
* Comprar la más sobrevendida y comprimida captura el rebote matinal en la apertura siguiente, reduciendo el sangrado de cánones a la mitad (-0.24 % vs -0.59 %).

### Pilar 4: Exposición Mínima Legal Segura (900 €)
* Las bases exigen mover al menos 2.500 € semanales entre las compras de la semana.
* Al dividir 2.500 € entre 3 órdenes ($833.33$ €), el redondeo de acciones enteras en el broker ($shares = \text{int}(834 / P)$) causaba déficits accidentales (ej. 2.463 €), provocando descalificación.
* Con **900 € por orden**, 3 operaciones suman **2.700 € garantizados**, cumpliendo la legalidad con margen de seguridad absoluto mientras se mantiene el **98.2 % de la cuenta permanentemente en liquidez**.

---

## 3. La Cláusula de Exención: El "Periodo de Gracia"

Las bases oficiales de BME estipulan:
> *"Mínimo de tres operaciones de compra y tres de venta cada semana, de cierre de jueves a cierre de jueves, **a partir del 22 de octubre** (22 a 29 de octubre, 29 de octubre a 5 de noviembre y 5 a 12 de noviembre), moviendo entre las compras de la semana al menos 2.500 €..."*

* El concurso se inaugura el **13 de octubre**, pero las semanas de cómputo obligatorio **comienzan el 22 de octubre**.
* **Decisión Estratégica:** Entre el **13 y el 21 de octubre (primeros 7 días hábiles)** no se ejecuta **ninguna orden**.
* **Impacto Directo:** 
  * Retorno de exactamente **0.00 %** y volatilidad de **0.00 %** durante los primeros 7 días.
  * Ahorro directo de **42 € en comisiones fijas** (una semana menos de cánones).
  * Reduce la operativa de todo el mes a solo **3 semanas (9 operaciones de compra y 9 de venta en total)**.

---

## 4. Calendario Operativo Oficial (Día a Día)

Este es el calendario maestro a seguir durante todo el concurso:

```
========================================================================================
FASE 1: PERIODO DE GRACIA (100% LIQUIDEZ / CERO OPERACIONES)
========================================================================================
Mar 13 Oct: INICIO DEL CONCURSO  -> [CERO OPERACIONES] - Cartera: 50.000,00 € Caja
Mié 14 Oct: Sesión Ordinaria     -> [CERO OPERACIONES] - Cartera: 50.000,00 € Caja
Jue 15 Oct: Sesión Ordinaria     -> [CERO OPERACIONES] - Cartera: 50.000,00 € Caja
Vie 16 Oct: Sesión Ordinaria     -> [CERO OPERACIONES] - Cartera: 50.000,00 € Caja

Lun 19 Oct: Sesión Ordinaria     -> [CERO OPERACIONES] - Cartera: 50.000,00 € Caja
Mar 20 Oct: Sesión Ordinaria     -> [CERO OPERACIONES] - Cartera: 50.000,00 € Caja
Mié 21 Oct: Sesión Ordinaria     -> [CERO OPERACIONES] - Cartera: 50.000,00 € Caja
Jue 22 Oct: CORTE INICIAL BME    -> [CERO OPERACIONES] - Inicio formal de Semana 1
Vie 23 Oct: Fin de Semana        -> [CERO OPERACIONES] - Bloqueo de fin de semana

========================================================================================
FASE 2: SEMANA OBLIGATORIA 1 (22 A 29 DE OCTUBRE)
========================================================================================
Lun 26 Oct: 17:25 Chequeo -> 17:29:50 COMPRA 1 (900 € en la utility más sobrevendida)
Mar 27 Oct: 09:00:01 VENTA 1 a mercado
            17:25 Chequeo -> 17:29:50 COMPRA 2 (900 € en la utility más sobrevendida)
Mié 28 Oct: 09:00:01 VENTA 2 a mercado
            17:25 Chequeo -> 17:29:50 COMPRA 3 (900 € en la utility más sobrevendida)
Jue 29 Oct: 09:00:01 VENTA 3 a mercado
            -> [SEMANA 1 SUPERADA CON ÉXITO: 2.700 € Compras / 2.700 € Ventas]
            17:30 Tarde: DESCANSO TOTAL (100% Caja)
Vie 30 Oct: [CERO OPERACIONES] - Bloqueo de fin de semana

========================================================================================
FASE 3: SEMANA OBLIGATORIA 2 (29 DE OCTUBRE A 5 DE NOVIEMBRE)
========================================================================================
Lun 02 Nov: 17:25 Chequeo -> 17:29:50 COMPRA 4 (900 € en la utility más sobrevendida)
Mar 03 Nov: 09:00:01 VENTA 4 a mercado
            17:25 Chequeo -> 17:29:50 COMPRA 5 (900 € en la utility más sobrevendida)
Mié 04 Nov: 09:00:01 VENTA 5 a mercado
            17:25 Chequeo -> 17:29:50 COMPRA 6 (900 € en la utility más sobrevendida)
Jue 05 Nov: 09:00:01 VENTA 6 a mercado
            -> [SEMANA 2 SUPERADA CON ÉXITO: 2.700 € Compras / 2.700 € Ventas]
            17:30 Tarde: DESCANSO TOTAL (100% Caja)
Vie 06 Nov: [CERO OPERACIONES] - Bloqueo de fin de semana

========================================================================================
FASE 4: SEMANA OBLIGATORIA 3 (5 A 12 DE NOVIEMBRE) — RECTA FINAL
========================================================================================
Lun 09 Nov: 17:25 Chequeo -> 17:29:50 COMPRA 7 (900 € en la utility más sobrevendida)
Mar 10 Nov: 09:00:01 VENTA 7 a mercado
            17:25 Chequeo -> 17:29:50 COMPRA 8 (900 € en la utility más sobrevendida)
Mié 11 Nov: 09:00:01 VENTA 8 a mercado
            17:25 Chequeo -> 17:29:50 COMPRA 9 (900 € en la utility más sobrevendida)
Jue 12 Nov: 09:00:01 VENTA 9 a mercado
            -> [SEMANA 3 SUPERADA: FIN DEL CONCURSO — 100% LIQUIDEZ Y CLASIFICACIÓN FINAL]
========================================================================================
```

---

## 5. Protocolo Paso a Paso para la Ejecución Manual

Solo necesitas estar frente a la pantalla **6 minutos al día, únicamente los Lunes, Martes y Miércoles**:

### Paso 1: A las 17:25 (Chequeo de 2 minutos)
Abre la plataforma de BME o tu broker y revisa los precios de las 5 acciones:
* `RED.MC` (Redeia)
* `ENG.MC` (Enagás)
* `ELE.MC` (Endesa)
* `IBE.MC` (Iberdrola)
* `NTGY.MC` (Naturgy)

Calcula el porcentaje de caída intradía respecto a la apertura:
$$\text{Retorno Intradía} = \frac{\text{Último Precio} - \text{Precio de Apertura}}{\text{Precio de Apertura}}$$

* **Selección Rápida (`MicroAlfa_CS`):** Elige directamente la acción que tenga el valor más negativo (la que más haya caído hoy).
* **Selección Avanzada (`Ensemble`):** Si hay empate o quieres filtrar compresión, clasifícalas del 1 al 5 por mayor caída y del 1 al 5 por menor rango $(High - Low)/Open$. Suma ambos puestos y elige la que tenga menor suma.

### Paso 2: A las 17:29:50 (Lanzamiento de Compra)
* Lanza una **orden de compra a mercado** (o limitada al último precio cruzado) por importe de **900 €**.
* La orden se ejecutará inmediatamente en el mercado continuo sin quedar atrapada en la subasta de cierre de las 17:30.

### Paso 3: A las 09:00:01 del día siguiente (Venta en Apertura)
* Apenas abra la sesión continua a las 09:00:01, lanza una **orden de venta a mercado** por la totalidad de las acciones compradas la tarde anterior.
* Cumples estrictamente la norma T+1 y la cuenta vuelve a estar al 100 % en caja para el resto del día.

---

## 6. Respuestas a Situaciones de Emergencia (Planes de Contingencia)

* **¿Qué pasa si un lunes o martes es festivo bursátil?**
  Si hay un festivo entre semana (ej. 1 de noviembre), traslada la operación pendiente al **Jueves por la tarde (compra a las 17:29:50 y venta el viernes a las 09:00:01)**. El viernes nunca se debe pasar la noche invertido, pero cerrar a las 09:00:01 del viernes es seguro.
* **¿Qué pasa si a las 17:25 hay noticias graves de resultados en una utility?**
  Si una utility cae más de un 4 % por una noticia corporativa disruptiva o recorte de dividendo, descártala del día y pasa a la segunda utility más sobrevendida para evitar un gap bajista adicional.
* **¿Puedo operar con importes superiores a 900 €?**
  No es recomendable. Como demostró la simulación de Fase 5, subir a 4.667 € multiplica la volatilidad de la cartera por 4 (de 0.20 % a 0.83 %), reduciendo los puntos de la fórmula. 900 € es el punto óptimo de mínima varianza.

