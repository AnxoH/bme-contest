# Calendario de Riesgo: Torneo de Bolsa (Octubre - Noviembre 2026)

Este documento detalla las fechas y horas críticas durante el periodo de competición (13 de octubre - 12 de noviembre de 2026). Al operar una estrategia de exposición nocturna (*MicroCS_Grace*), el objetivo no es predecir estos eventos, sino **aislar la cartera** de ellos mediante la exclusión temporal (*blacklist*) del activo afectado.

## 🏛️ 1. Calendario Macroeconómico (Bancos Centrales)
*Nota: Como la estrategia mantiene el capital 100% en liquidez durante el día, tu algoritmo es naturalmente inmune a la volatilidad intradiaria que generan estas reuniones. Sin embargo, marcan el tono del mercado.*

| Fecha | Evento | Hora (CET/Madrid) | Impacto / Riesgo |
| :--- | :--- | :--- | :--- |
| Jueves, 29 de Octubre | **BCE** - Decisión de Tipos | 14:15 h | Alto. Afecta directamente al coste de deuda de las eléctricas. |
| Jueves, 29 de Octubre | **BCE** - Rueda de Prensa | 14:45 h | Alta volatilidad intradiaria en el mercado continuo. |
| Miércoles, 4 de Noviembre| **FED** - Decisión de Tipos (EEUU)| 20:00 h | Condiciona la apertura europea del jueves, 5 de noviembre. |
| Jueves, 5 de Noviembre | **BoE** - Decisión de Tipos (UK) | 13:00 h | Riesgo direccional específico para **Iberdrola** (IBE.MC). |

---

## 📊 2. Calendario Corporativo: Resultados 9M 2026
*Regla de algoritmo: Si una empresa presenta resultados el día `T` antes de la apertura (BMO), su cotización sufrirá un gap masivo a las 09:00h. **PROHIBIDO** comprar esa acción en la sesión `T-1` a las 17:29h, sin importar su Z-Score.*

| Fecha (Proyectada) | Empresa | Ticker | Hora de Publicación | Noche de Exclusión (No comprar) |
| :--- | :--- | :--- | :--- | :--- |
| Martes, 20 de Octubre | **Enagás** | ENG.MC | BMO (Antes de las 08:30) | Lunes, 19 de Oct (*Estás en liquidez*) |
| Miércoles, 21 de Octubre| **Iberdrola**| IBE.MC | BMO (Antes de las 08:30) | Martes, 20 de Oct (*Estás en liquidez*) |
| Miércoles, 28 de Octubre| **Redeia** | RED.MC | BMO (Antes de las 08:30) | **Martes, 27 de Octubre** |
| Viernes, 30 de Octubre | **Naturgy** | NTGY.MC| BMO (Antes de las 08:30) | Jueves, 29 de Octubre |
| Martes, 3 de Noviembre | **Endesa** | ELE.MC | BMO (Antes de las 08:30) | **Lunes, 2 de Noviembre** |

---

## 💰 3. Calendario de Dividendos (Ex-Date)
*Regla de algoritmo: En la fecha "Ex-Dividend", el precio de la acción amanecerá con el descuento del dividendo. Comprar la tarde anterior garantiza una pérdida automática en la apertura si el simulador no compensa el efectivo al instante.*

| Fecha Ex-Dividend (Est.) | Empresa | Ticker | Evento | Noche de Exclusión (No comprar) |
| :--- | :--- | :--- | :--- | :--- |
| Jueves, 5 de Noviembre | **Naturgy** | NTGY.MC| Dividendo a cuenta | **Miércoles, 4 de Noviembre** |

*(Nota: Redeia, Enagás, Endesa e Iberdrola no suelen repartir dividendos durante esta ventana temporal específica de octubre/noviembre, sus abonos caen en diciembre o enero).*

---

## 🛑 Resumen de Ejecución: "La Blacklist"
Para implementar esto en tu operativa manual o en tu código, esta es la lista de exclusión exacta por días:

*   **13 al 21 de octubre:** Periodo de Gracia. No se opera. (Te saltas el riesgo de ENG e IBE).
*   **Martes 27 de octubre (17:25):** Calcular Z-Score de la cesta, pero **IGNORAR a RED.MC**. Si RED.MC es la más sobrevendida, comprar la segunda más sobrevendida.
*   **Jueves 29 de octubre (17:25):** Calcular Z-Score, pero **IGNORAR a NTGY.MC** (Resultados viernes).
*   **Lunes 2 de noviembre:** No operas (estamos evitando los lunes por regla de la estrategia), lo cual te salva perfectamente del gap de resultados de Endesa del martes 3.
*   **Miércoles 4 de noviembre (17:25):** Calcular Z-Score, pero **IGNORAR a NTGY.MC** (Corte de dividendo al día siguiente).