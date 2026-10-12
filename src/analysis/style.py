import matplotlib.pyplot as plt
from cycler import cycler

# ==============================================================================
# BME CONTEST 2026 — INSTITUTIONAL VISUAL IDENTITY SYSTEM
# ==============================================================================

BME_PURPLE = '#3d1696'
BME_GREEN = '#6bb030'
TEXT_GRAY = '#666666'
GRID_GRAY = '#f0f0f0'
ACCENT_ORANGE = '#FF9F1C'
ACCENT_RED = '#E71D36'

BME_PALETTE = [BME_PURPLE, BME_GREEN, ACCENT_ORANGE, ACCENT_RED]

def set_bme_style():
    """
    Apply unified BME institutional aesthetic parameters to matplotlib rcParams.
    - Minimalist white canvas with zero top/right/left spines
    - Subtle horizontal dashed grid lines (#f0f0f0)
    - Corporate color cycle (BME Purple, BME Green, Orange, Red)
    - Frameless legends and softened text hierarchy
    """
    plt.rcParams.update({
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.spines.left': False,
        'axes.spines.bottom': True,
        'axes.edgecolor': GRID_GRAY,
        'axes.grid': True,
        'axes.grid.axis': 'y',
        'grid.color': GRID_GRAY,
        'grid.linestyle': '--',
        'grid.linewidth': 1.0,
        'xtick.color': TEXT_GRAY,
        'ytick.color': TEXT_GRAY,
        'xtick.bottom': False,
        'ytick.left': False,
        'font.family': 'sans-serif',
        'text.color': '#333333',
        'axes.labelcolor': TEXT_GRAY,
        'axes.prop_cycle': cycler('color', BME_PALETTE),
        'legend.frameon': False,
        'legend.loc': 'upper right',
        'legend.fontsize': 10
    })

if __name__ == '__main__':
    set_bme_style()
    print("BME visual style applied successfully.")

