import nbformat
from nbformat.v4 import new_markdown_cell, new_code_cell

nb_path = 'notebooks/5_estrategias_sinteticas_eda.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

# Find the index of the Conclusions cell
conclusions_idx = -1
for i, cell in enumerate(nb.cells):
    if "## 5. Conclusiones y Siguientes Pasos" in cell.source:
        conclusions_idx = i
        break

if conclusions_idx != -1:
    # We will insert the new cells right before conclusions
    
    md_cell = new_markdown_cell("## 5. Frecuencia de Victorias (Win Rate)\n\nEn lugar de mirar los promedios, vamos a analizar **cuántas veces gana cada estrategia**. \nComo calculamos los resultados para cientos de ventanas de 22 días, podemos ver qué estrategia obtiene la mayor puntuación total (`Total_Score`) en cada ventana individual.")
    
    code_cell = new_code_cell("""# Como df contiene exactamente 20 filas por cada ventana simulada,
# podemos agruparlas para encontrar al ganador de cada mes.
num_windows = len(df) // 20
df['Window_ID'] = np.repeat(np.arange(num_windows), 20)

# Encontrar el índice del máximo Total_Score por ventana
ganadores_idx = df.groupby('Window_ID')['Total_Score'].idxmax()
ganadores = df.loc[ganadores_idx, 'Competitor']

# Contar victorias
conteo_victorias = ganadores.value_counts()

# Calcular porcentaje
pct_victorias = (conteo_victorias / num_windows * 100).round(1)

plt.figure(figsize=(12, 6))
sns.barplot(x=conteo_victorias.values, y=conteo_victorias.index, palette='magma')
plt.title(f'Número de Victorias Absolutas por Estrategia (Total Ventanas: {num_windows})')
plt.xlabel('Número de veces que quedó en 1ª posición')
plt.ylabel('Estrategia')

# Añadir el porcentaje como texto en las barras
for i, v in enumerate(conteo_victorias.values):
    plt.text(v + 1, i, f"{pct_victorias.iloc[i]}%", va='center')

plt.tight_layout()
plt.show()

print("Tabla de Victorias:")
display(pd.DataFrame({'Victorias': conteo_victorias, 'Porcentaje (%)': pct_victorias}))
""")
    
    # Update the title of the conclusions cell
    nb.cells[conclusions_idx].source = nb.cells[conclusions_idx].source.replace("## 5.", "## 6.")
    
    # Insert the new cells
    nb.cells.insert(conclusions_idx, md_cell)
    nb.cells.insert(conclusions_idx + 1, code_cell)
    
    with open(nb_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
    
    print("Notebook modificado correctamente.")
else:
    print("No se encontró la celda de conclusiones.")

