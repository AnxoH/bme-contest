# CONTEXTO DEL PROYECTO: Framework Cuantitativo - El Concurso de Bolsa

## 1. Descripción General del Proyecto
Este proyecto tiene como objetivo desarrollar un framework de trading algorítmico y backtesting diseñado específicamente para operar en "El Concurso de Bolsa" (edición 2026). El entorno de inversión está restringido exclusivamente al **Mercado Continuo Español**. 

El propósito de este repositorio es dotar a un agente automatizado y al desarrollador de la infraestructura necesaria para procesar datos históricos, aislar factores de riesgo, simular el impacto estricto de las reglas del concurso y evaluar la esperanza matemática de diferentes estrategias antes de su ejecución en el simulador en vivo.

## 2. Horizonte Temporal y Fases
*   **Periodo de Competición:** Del 13 de octubre al 12 de noviembre de 2026.
*   **Horario de Operativa:** Días hábiles bursátiles, de 9:00:00 a 17:29:59.
*   **Fase de Supervivencia:** Semanas de evaluación obligatoria a partir del 22 de octubre (cortes de evaluación: jueves al cierre de mercado).

## 3. Especificaciones del Entorno de Ejecución
*   **Capital Inicial:** 50.000 € virtuales.
*   **Universo de Activos:** Valores cotizados en el Mercado Continuo Español.
*   **Precios de Ejecución:** Todas las órdenes se ejecutan al *último precio cruzado* en el mercado en el momento de la ejecución. 
*   **Filtro de Subastas:** Se descartan los precios indicativos de las subastas de apertura y cierre. Solo se opera con precios de la sesión continua.
*   **Órdenes Fuera de Horario:** Las órdenes enviadas con el mercado cerrado (después de las 17:30:00) quedan en cola y se ejecutan al precio de apertura de la siguiente sesión.
*   **Límite de Frecuencia:** Máximo de 20 órdenes por minuto por participante.

## 4. Restricciones Operativas (Hard Constraints)
Cualquier sistema de backtesting diseñado en este proyecto debe incorporar estas restricciones de forma determinista para evitar la falsificación de resultados (*look-ahead bias* o *execution bias*):

*   **Restricción Direccional (Long-Only):** Prohibidas las posiciones cortas (*short selling*). Solo se pueden vender títulos previamente adquiridos.
*   **Restricción de Inventario (Regla T+1 estricta):** 
    *   Un valor comprado un día **no podrá venderse** hasta el día siguiente.
    *   Un valor vendido en una jornada **no podrá comprarse** de nuevo hasta la siguiente.
    *   *Regla de Agregación:* Ampliar una posición existente bloquea la posición completa. Si se añaden títulos a una posición antigua, todo el bloque queda inmovilizado para la venta hasta el día siguiente.
*   **Restricción de Supervivencia (Volumen Mínimo):** A partir del 22 de octubre, es obligatorio realizar un mínimo de **3 operaciones de compra y 3 de venta cada semana** (de cierre de jueves a cierre de jueves). 
    *   El volumen mínimo exigido es de 2.500 € agregados en compras y 2.500 € agregados en ventas por semana.
    *   El incumplimiento en una sola semana supone la exclusión de los premios.

## 5. Modelo de Fricción y Costes
Las simulaciones de la curva de *equity* deben descontar obligatoriamente la siguiente estructura de costes sobre el capital efectivo:
*   **Comisión de intermediación:** 0,15 % sobre el importe efectivo de cada operación (compra y venta).
*   **Comisión mínima:** 7 € fijos por operación (aplica a operaciones de volumen reducido donde el 0,15% no alcanza este umbral).
*   *Nota:* No se aplican cánones de bolsa ni otros gastos regulatorios; el 0,15% es el único coste transaccional.

## 6. Función Objetivo (Sistema de Puntuación)
El modelo no optimiza únicamente por rentabilidad absoluta, sino por una función objetivo ponderada compuesta por tres factores. La estrategia debe maximizar esta métrica conjunta:

La clasificación final se calcula entre los participantes que hayan cumplido los requisitos de participación, mediante un sistema de puntos en el que el peso de cada una de las tres variables será:

- Rentabilidad: 60 % de la clasificación (6 puntos a la mayor revalorización).
- Volatilidad: 30 % de la clasificación (3 puntos a la menor volatilidad).
- Logros educativos: 10 % de la clasificación (1 punto al máximo de aciertos).

En el caso de la rentabilidad, al usuario que tenga mayor valor final de cartera, entre quienes optan a premio, se le asignará un valor de 6 puntos totales en esta parte. Al segundo clasificado por valoración se le asignarán los puntos proporcionales que le correspondan en función de su valoración, tomando como base siempre los del primer clasificado. Y así se ordenarán todos los usuarios en orden descendente.

Ponemos un ejemplo: si el concursante que termina en primer lugar finaliza con una valoración final de 80.000 €, a este se le asignan 6 puntos al ser el primer clasificado. Si el segundo clasificado termina con 75.000 €, se hará su parte proporcional respecto al primero. Es decir:

Puntos del segundo clasificado = 75.000 × 6 / 80.000 = 5,625 puntos.

Con lo cual el sistema de cálculo de los puntos de cada usuario es:

Puntos de rentabilidad = Valor final de la cartera × 6 / Valor final de la cartera del primer clasificado

En cuanto a la variable volatilidad, se tomará la de cada participante calculada según la fórmula indicada con anterioridad. Entre quienes optan a premio, al participante con menor volatilidad se le asignarán 3 puntos y al de mayor volatilidad 0 puntos. Al resto se le asignará la parte proporcional entre ambos extremos:

Puntos de volatilidad = 3 × (1 − (V − Vmín) / (Vmáx − Vmín))

siendo V la volatilidad del participante, Vmín la menor y Vmáx la mayor entre quienes optan a premio. Si todos tuvieran la misma volatilidad, todos recibirían 3 puntos.

Es decir, los puntos a asignar a cada participante resultarán de la siguiente operación:

Participante con menor volatilidad (Vmín): 3 puntos.
Participante con mayor volatilidad (Vmáx): 0 puntos.
Cualquier otro participante, con volatilidad V: 3 × (1 − (V − Vmín) / (Vmáx − Vmín)).
Ejemplo, con cuatro participantes que optan a premio:

Participante A: volatilidad 0,80 % (la menor) → 3 puntos.
Participante B: volatilidad 1,20 % → 3 × (1 − 0,40 / 1,60) = 3 × 0,75 = 2,25 puntos.
Participante C: volatilidad 2,00 % → 3 × (1 − 1,20 / 1,60) = 3 × 0,25 = 0,75 puntos.
Participante D: volatilidad 2,40 % (la mayor) → 0 puntos.