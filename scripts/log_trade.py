import os
import sys
import argparse
from datetime import datetime

# Añadir raíz al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.live.ledger import TradesLedger

def print_ledger_summary(ledger):
    stats = ledger.get_current_week_stats()
    open_pos = ledger.get_current_open_position()
    
    print("\n" + "=" * 65)
    print("           ESTADO ACTUAL DEL LIBRO DE ÓRDENES (LEDGER)")
    print("=" * 65)
    print(f"Semana BME Actual:    {stats['week_id']}")
    print(f"Compras de la semana: {stats['buys_count']} / {stats['target_trades']} (Faltan {stats['trades_remaining']})")
    print(f"Volumen de compras:   {stats['buy_volume_eur']:.2f} € / {stats['target_volume_eur']:.2f} €")
    print(f"Cuota BME semanal:    {'CUMPLIDA' if stats['quota_fulfilled'] else 'PENDIENTE'}")
    print("-" * 65)
    if open_pos:
        print(f"POSICIÓN ABIERTA:     {open_pos['shares']} acciones de {open_pos['ticker']}")
        print(f"Comprada el:          {open_pos['buy_date']} a {open_pos['buy_price']:.2f} € ({open_pos['buy_amount']:.2f} €)")
        print(f"Salida requerida:     Mañana a las 09:00:01 CET a precio de Apertura")
    else:
        print("POSICIÓN ABIERTA:     NINGUNA (100% Liquidez)")
    print("=" * 65 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Registro manual de operaciones reales en el concurso BME")
    parser.add_argument('--buy', nargs=3, metavar=('TICKER', 'ACCIONES', 'PRECIO'), help="Registrar compra (ej: --buy ELE.MC 21 42.53)")
    parser.add_argument('--sell', nargs=3, metavar=('TICKER', 'ACCIONES', 'PRECIO'), help="Registrar venta (ej: --sell ELE.MC 21 42.65)")
    parser.add_argument('--status', action='store_true', help="Ver el estado de la semana y posición abierta")
    parser.add_argument('--history', action='store_true', help="Mostrar todo el historial de trades registrados")
    
    args = parser.parse_args()
    ledger = TradesLedger()
    
    if args.status:
        print_ledger_summary(ledger)
        return
        
    if args.history:
        df = ledger.load_trades()
        if len(df) == 0:
            print("El historial de operaciones está vacío.")
        else:
            print(df.to_string(index=False))
        return
        
    if args.buy:
        ticker, shares, price = args.buy
        rec = ledger.record_trade('BUY', ticker, int(shares), float(price))
        print(f"\n[OK] COMPRA REGISTRADA:")
        print(f"     Ticker:   {rec['Ticker']}")
        print(f"     Acciones: {rec['Titulos']}")
        print(f"     Precio:   {rec['Precio']:.2f} €")
        print(f"     Importe:  {rec['Importe_EUR']:.2f} €")
        print(f"     Fecha:    {rec['Fecha']} {rec['Hora']}")
        print_ledger_summary(ledger)
        return
        
    if args.sell:
        ticker, shares, price = args.sell
        rec = ledger.record_trade('SELL', ticker, int(shares), float(price))
        print(f"\n[OK] VENTA REGISTRADA:")
        print(f"     Ticker:   {rec['Ticker']}")
        print(f"     Acciones: {rec['Titulos']}")
        print(f"     Precio:   {rec['Precio']:.2f} €")
        print(f"     Importe:  {rec['Importe_EUR']:.2f} €")
        print(f"     Fecha:    {rec['Fecha']} {rec['Hora']}")
        print_ledger_summary(ledger)
        return

    # Si no se pasan argumentos, entrar en modo interactivo guiado
    print("\n" + "=" * 65)
    print("      REGISTRO MANUAL DE OPERACIONES - BME CONTEST")
    print("=" * 65)
    print("1. Registrar COMPRA (al cierre ~17:25 CET)")
    print("2. Registrar VENTA (a la apertura ~09:00 CET)")
    print("3. Ver Estado y Cuota Semanal")
    print("4. Ver Historial Completo")
    print("5. Salir")
    print("-" * 65)
    
    choice = input("Selecciona una opción [1-5]: ").strip()
    
    if choice == '1':
        ticker = input("Ticker comprado (ej: RED.MC, ELE.MC): ").strip().upper()
        shares = int(input("Número de títulos/acciones ejecutadas: ").strip())
        price = float(input("Precio real de ejecución en el broker (€): ").strip().replace(',', '.'))
        rec = ledger.record_trade('BUY', ticker, shares, price)
        print(f"\n[OK] Compra registrada con éxito: {shares} accs de {ticker} a {price:.2f} € ({rec['Importe_EUR']:.2f} €)")
        print_ledger_summary(ledger)
        
    elif choice == '2':
        ticker = input("Ticker vendido (ej: RED.MC, ELE.MC): ").strip().upper()
        shares = int(input("Número de títulos vendidos: ").strip())
        price = float(input("Precio de venta en la apertura (€): ").strip().replace(',', '.'))
        rec = ledger.record_trade('SELL', ticker, shares, price)
        print(f"\n[OK] Venta registrada con éxito: {shares} accs de {ticker} a {price:.2f} € ({rec['Importe_EUR']:.2f} €)")
        print_ledger_summary(ledger)
        
    elif choice == '3':
        print_ledger_summary(ledger)
        
    elif choice == '4':
        df = ledger.load_trades()
        if len(df) == 0:
            print("El historial de operaciones está vacío.")
        else:
            print(df.to_string(index=False))
            
    else:
        print("Operación cancelada.")

if __name__ == '__main__':
    main()

