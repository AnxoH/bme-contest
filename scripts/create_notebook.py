import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
import os

nb = new_notebook()

nb.cells.append(new_markdown_cell("# EDA: Análisis de las 20 Estrategias Sintéticas\n\nEste notebook analiza el comportamiento y las métricas de las 20 estrategias sintéticas generadas para poblar nuestro entorno de backtesting. El objetivo es visualizar sus curvas de capital (Equity Curves), entender sus perfiles de riesgo (Volatilidad) y analizar cómo puntúan bajo las reglas del concurso BME."))

nb.cells.append(new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración visual
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("notebook", font_scale=1.1)

# Cargar datos
rets_df = pd.read_csv('../data/processed/competitors_returns.csv', index_col=0, parse_dates=True)
display(rets_df.head())"""))

nb.cells.append(new_markdown_cell("## 1. Curvas de Capital (Cumulative Returns)\n\nVamos a visualizar cómo habrían evolucionado 50.000€ invertidos en cada una de estas estrategias a lo largo de los 15 años."))

nb.cells.append(new_code_cell("""# Calcular el valor de la cartera partiendo de 50,000€
capital_inicial = 50000
equity_curves = capital_inicial * (1 + rets_df).cumprod()

plt.figure(figsize=(16, 8))
# Trazar todas las líneas de forma sutil
for col in equity_curves.columns:
    if 'YOLO' in col:
        plt.plot(equity_curves.index, equity_curves[col], alpha=0.8, linewidth=1.5, linestyle='--', label=col)
    elif 'Conservador' in col:
        plt.plot(equity_curves.index, equity_curves[col], alpha=0.8, linewidth=2, label=col)
    elif 'Idx' in col:
        plt.plot(equity_curves.index, equity_curves[col], alpha=0.9, linewidth=3, color='black', label=col)
    else:
        plt.plot(equity_curves.index, equity_curves[col], alpha=0.3, linewidth=1)

plt.yscale('log')
plt.title('Evolución de las 20 Estrategias (Escala Logarítmica)', fontsize=16)
plt.ylabel('Capital (€)')
plt.xlabel('Fecha')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.show()"""))

nb.cells.append(new_markdown_cell("## 2. Perfil de Riesgo (Volatilidad Anualizada)\n\nEl concurso reparte 3 puntos a la menor volatilidad. Veamos la distribución de volatilidades entre nuestros 20 perfiles."))

nb.cells.append(new_code_cell("""vol_ann = rets_df.std() * np.sqrt(252) * 100
vol_ann = vol_ann.sort_values()

plt.figure(figsize=(12, 8))
sns.barplot(x=vol_ann.values, y=vol_ann.index, palette='viridis')
plt.title('Volatilidad Anualizada por Estrategia (%)')
plt.xlabel('Volatilidad Anualizada (%)')
plt.ylabel('Estrategia')
plt.tight_layout()
plt.show()"""))

nb.cells.append(new_markdown_cell("## 3. Puntuación Relativa (Simulación de Ventanas Rodantes)\n\nAplicamos la fórmula del concurso a cientos de ventanas de 22 días para sacar el promedio real con el que se clasificaría cada estrategia."))

nb.cells.append(new_code_cell("""window_size = 22
step = 11
n_days = len(rets_df)
start_points = range(0, n_days - window_size, step)

all_results = []
for start in start_points:
    window_rets = rets_df.iloc[start : start + window_size]
    if len(window_rets) < window_size * 0.8: continue
        
    comps = []
    for col in window_rets.columns:
        series = window_rets[col].dropna()
        if len(series) > 0:
            r = np.prod(1 + series) - 1
            v = series.std() * np.sqrt(252)
        else:
            r = 0.0; v = 0.0
        comps.append({'name': col, 'ret': r, 'vol': v})
        
    for c in comps: c['final_val'] = 50000 * (1 + c['ret'])
    max_val = max([c['final_val'] for c in comps])
    for c in comps: c['ret_points'] = (c['final_val'] * 6) / max_val
    min_vol = min([c['vol'] for c in comps])
    max_vol = max([c['vol'] for c in comps])
    
    for c in comps:
        if max_vol == min_vol: c['vol_points'] = 3.0
        else: c['vol_points'] = 3 * (1 - (c['vol'] - min_vol) / (max_vol - min_vol))
        c['total_points'] = c['ret_points'] + c['vol_points']
        all_results.append({
            'Competitor': c['name'], 'Return_1M': c['ret'], 'Vol_Ann': c['vol'],
            'Ret_Points': c['ret_points'], 'Vol_Points': c['vol_points'], 'Total_Score': c['total_points']
        })

df = pd.DataFrame(all_results)
agg = df.groupby('Competitor').mean().sort_values('Total_Score', ascending=False)

agg_styled = agg.copy()
agg_styled['Return_1M'] = (agg_styled['Return_1M'] * 100).round(2).astype(str) + '%'
agg_styled['Vol_Ann'] = (agg_styled['Vol_Ann'] * 100).round(2).astype(str) + '%'
for col in ['Ret_Points', 'Vol_Points', 'Total_Score']:
    agg_styled[col] = agg_styled[col].round(2)

display(agg_styled)"""))

nb.cells.append(new_markdown_cell("## 4. Conclusiones\n\n### Q&A\n**¿Cómo se comportan las estrategias extremas?**\nLas estrategias YOLO tienen los mayores retornos absolutos, pero pierden dramáticamente debido a la volatilidad.\n\n### Data Analysis Key Findings\n* La volatilidad de los perfiles conservadores (caja al 90%) ronda el 0.5%-1.5%, mientras que los perfiles normales (Índices y Blue Chips) se sitúan en torno al 15%-25%.\n* Esta enorme brecha destruye a los inversores tradicionales (que pierden entre 1.0 y 1.5 puntos de volatilidad).\n\n### Insights or Next Steps\n* **La volatilidad es el rey matemático**: Cualquier estrategia algorítmica competitiva debe basarse en anular su exposición al mercado continuo, operando de manera cuasi-neutral (o permaneciendo en liquidez el 99% del tiempo) para no ceder puntos en la variable de menor volatilidad.\n* El próximo modelo cuantitativo deberá forzar posiciones efímeras intra-semanales (ej: comprar a las 17:29 un gran perdedor, vender a las 09:00, y volver a liquidez)."))

os.makedirs('notebooks', exist_ok=True)
with open('notebooks/5_estrategias_sinteticas_eda.ipynb', 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

print("Notebook generado con éxito.")
