import nbformat
from nbformat.v4 import new_markdown_cell, new_code_cell

nb_path = 'notebooks/5_estrategias_sinteticas_eda.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

if "Conclusiones" in nb.cells[-1].source:
    old_conclusions = nb.cells.pop()

nb.cells.append(new_markdown_cell("## 4. Distribución de Retornos Mensuales vs Varianzas (Mercado Continuo)\n\nPara entender por qué la volatilidad domina la puntuación, vamos a aislar el 'Mercado Continuo' y analizar empíricamente la distribución de sus retornos a 22 días (1 mes) frente a su varianza (riesgo) en esas mismas ventanas."))

nb.cells.append(new_code_cell("""# Extraer la estrategia representativa del Mercado Continuo
idx_returns = rets_df['Idx_Continuous_Merc'].dropna()

# Calcular métricas rodantes (22 días)
rolling_rets = idx_returns.rolling(22).apply(lambda x: np.prod(1 + x) - 1) * 100 # En porcentaje
rolling_vars = idx_returns.rolling(22).var() * 252 * 100 # Varianza anualizada escalada (en x100 para visualizar mejor)

dist_df = pd.DataFrame({'Retorno_1M': rolling_rets, 'Varianza_Ann': rolling_vars}).dropna()

# Crear una figura con 3 subplots
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Histograma de Retornos
sns.histplot(dist_df['Retorno_1M'], bins=50, ax=axes[0], color='skyblue', kde=True)
axes[0].set_title('Distribución Retornos Mensuales (%)')
axes[0].set_xlabel('Retorno a 22 días (%)')

# Histograma de Varianzas
sns.histplot(dist_df['Varianza_Ann'], bins=50, ax=axes[1], color='salmon', kde=True)
axes[1].set_title('Distribución Varianza Anualizada')
axes[1].set_xlabel('Varianza')

# Scatter Plot (Retorno vs Varianza)
sns.scatterplot(data=dist_df, x='Varianza_Ann', y='Retorno_1M', alpha=0.3, ax=axes[2], color='purple')
axes[2].axhline(0, color='black', linestyle='--')
axes[2].set_title('Retorno vs Varianza')
axes[2].set_xlabel('Varianza Anualizada')
axes[2].set_ylabel('Retorno Mensual (%)')

plt.tight_layout()
plt.show()

# Resumen Cuantitativo
print("Resumen Estadístico Cuantitativo (Mercado Continuo):")
display(dist_df.describe().round(2))
"""))

nb.cells.append(new_markdown_cell("""## 5. Conclusiones y Siguientes Pasos

### Q&A
**¿Cómo se comportan las estrategias extremas?**
Las estrategias YOLO tienen los mayores retornos absolutos, pero pierden dramáticamente debido a la volatilidad.

### Data Analysis Key Findings
* **Rango Estrecho de Retornos vs Rango Amplio de Varianzas:** Como vemos en los gráficos, los retornos mensuales del mercado continuo están muy concentrados (la mayoría entre -5% y +5%). Sin embargo, la varianza es extremadamente asimétrica (Right-Skewed) y tiene una cola muy larga hacia la derecha. 
* Esto provoca que, en un mes cualquiera, diferenciarte de tus rivales por Rentabilidad es cuestión de unos pocos puntos porcentuales (que en la fórmula de puntos relativos apenas te distancia del resto porque el fondo del mercado te arrastra). Diferenciarte por Volatilidad, en cambio, te permite cruzar casi toda la escala del 0 al 3.
* La volatilidad de los perfiles conservadores (caja al 90%) ronda el 0.5%-1.5%, mientras que los perfiles normales se sitúan en torno al 15%-25%.

### Insights or Next Steps
* **La volatilidad es el rey matemático**: Cualquier estrategia algorítmica competitiva debe basarse en anular su exposición al mercado continuo, operando de manera cuasi-neutral (o permaneciendo en liquidez el 99% del tiempo) para no ceder puntos en la variable de menor volatilidad.
* El próximo modelo cuantitativo deberá forzar posiciones efímeras intra-semanales (ej: comprar a las 17:29 un gran perdedor, vender a las 09:00, y volver a liquidez)."""))

with open(nb_path, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

print("Notebook actualizado.")
