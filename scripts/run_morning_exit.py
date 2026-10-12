import os
import sys
import yfinance as yf
from datetime import datetime

# Añadir raíz al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.live.ledger import TradesLedger

def main():
    now = datetime.now()
    weekday_idx = now.weekday()
    weekday_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    weekday_str = weekday_names[weekday_idx]
    
    print("=" * 80)
    print(" " * 18 + "BME CONTEST - APERTURA DE MERCADO (09:00:01 CET)")
    print(" " * 20 + f"Fecha: {now.strftime('%Y-%m-%d')} ({weekday_str}) | Hora: {now.strftime('%H:%M:%S')} CET")
    print("=" * 80)
    
    ledger = TradesLedger()
    open_pos = ledger.get_current_open_position()
    
    if not open_pos:
        print("\n[ESTADO: 100% LIQUIDEZ]")
        print("  • No tienes ninguna posición abierta pendiente de vender del día anterior.")
        print("  • La cartera se encuentra 100% en liquidez (varianza 0).")
        print("  • No se requiere realizar ninguna operación esta mañana.")
        print("  • La próxima evaluación de compra será hoy a las 17:15 CET.")
        print("=" * 80 + "\n")
        return

    ticker = open_pos['ticker']
    shares = open_pos['shares']
    buy_px = open_pos['buy_price']
    buy_amt = open_pos['buy_amount']
    buy_dt = open_pos['buy_date']
    
    # Obtener precio de apertura en tiempo real
    print(f"\n[OBTENIENDO PRECIO DE APERTURA PARA {ticker}]...")
    open_px = buy_px
    try:
        t = yf.Ticker(ticker)
        fi = t.fast_info
        px_cand = fi.get('open') or fi.get('last_price')
        if px_cand is not None and float(px_cand) > 0:
            open_px = float(px_cand)
    except Exception:
        pass
        
    est_sell_amt = round(shares * open_px, 2)
    pnl_eur = round(est_sell_amt - buy_amt, 2)
    pnl_pct = ((open_px - buy_px) / buy_px) * 100.0 if buy_px > 0 else 0.0
    sign = "+" if pnl_eur >= 0 else ""

    print("\n" + "=" * 80)
    print(f"  ¡ATENCIÓN! ORDEN OBLIGATORIA DE VENTA EN APERTURA (T+1)")
    print("=" * 80)
    print(f"  • Activo a Liquidar:        {ticker}")
    print(f"  • Títulos a Vender:         {shares} acciones (100% de la posición)")
    print(f"  • Compra realizada el:      {buy_dt} a {buy_px:.2f} € ({buy_amt:.2f} €)")
    print(f"  • Precio Apertura de Hoy:   {open_px:.2f} € (Total estimado: {est_sell_amt:.2f} €)")
    print(f"  • P&L Bruto Estimado:       {sign}{pnl_eur:.2f} € ({sign}{pnl_pct:.2f}%)")
    print("-" * 80)
    print("  INSTRUCCIÓN DE TRADING:")
    print(f"    Entra al broker de BME y lanza una orden de VENTA A MERCADO de tus {shares} accs.")
    print("=" * 80)
    
    # Registro interactivo inmediato
    print("\n¿DESEAS REGISTRAR LA VENTA EJECUTADA AHORA?")
    try:
        user_input = input(f"Introduce el precio real de venta ejecutado [Enter para {open_px:.2f} €]: ").strip()
    except (EOFError, KeyboardInterrupt):
        user_input = ""
        
    if user_input.lower() in ['n', 'no', 'cancel']:
        print("\nOperación cancelada. Puedes registrar la venta más tarde con:")
        print(f"  python scripts/log_trade.py --sell {ticker} {shares} [PRECIO_REAL]")
        print("=" * 80 + "\n")
        return
        
    try:
        real_sell_px = float(user_input.replace(',', '.')) if user_input else open_px
        real_sell_amt = round(shares * real_sell_px, 2)
        real_pnl_eur = round(real_sell_amt - buy_amt, 2)
        real_pnl_pct = ((real_sell_px - buy_px) / buy_px) * 100.0 if buy_px > 0 else 0.0
        real_sign = "+" if real_pnl_eur >= 0 else ""
        
        rec = ledger.record_trade('SELL', ticker, shares, real_sell_px)
        
        print("\n" + "-" * 80)
        print("[OK] VENTA REGISTRADA CON ÉXITO EN EL LIBRO OFICIAL BME:")
        print(f"     Ticker:             {ticker}")
        print(f"     Acciones vendidas:  {shares}")
        print(f"     Precio de venta:    {real_sell_px:.2f} € ({real_sell_amt:.2f} €)")
        print(f"     Resultado del trade:{real_sign}{real_pnl_eur:.2f} € ({real_sign}{real_pnl_pct:.2f}%)")
        print(f"     Estado de Cartera:  100% LIQUIDEZ (Posición cerrada)")
        print("-" * 80)
    except Exception as e:
        print(f"[ERROR] Error al registrar: {e}")
        
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()
