import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Añadir raíz al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.live.data_feed import LiveDataFeed
from src.live.corporate_events import CorporateEventsChecker
from src.live.engine_cs import EngineMicroAlfaCS
from src.live.engine_nr import EngineMicroAlfaNR
from src.live.ledger import TradesLedger

def format_row(values, widths, aligns=None):
    if aligns is None:
        aligns = ['<'] * len(values)
    parts = []
    for val, w, al in zip(values, widths, aligns):
        val_str = str(val)
        if len(val_str) > w:
            val_str = val_str[:w-1] + "."
        if al == '>':
            parts.append(val_str.rjust(w))
        elif al == '^':
            parts.append(val_str.center(w))
        else:
            parts.append(val_str.ljust(w))
    return " | ".join(parts)

def main():
    now = datetime.now()
    weekday_idx = now.weekday()
    weekday_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    weekday_str = weekday_names[weekday_idx]
    
    print("=" * 95)
    print(" " * 22 + "BME CONTEST - MOTOR DE DECISIÓN EN VIVO (17:15 - 17:25 CET)")
    print(" " * 25 + f"Fecha: {now.strftime('%Y-%m-%d')} ({weekday_str}) | Hora: {now.strftime('%H:%M:%S')} CET")
    print("=" * 95)
    
    # 1. Auditoría del Estado Semanal BME y Posiciones Abiertas
    ledger = TradesLedger()
    stats = ledger.get_current_week_stats()
    open_pos = ledger.get_current_open_position()
    
    print("\n[1] ESTADO DE LA SEMANA DE CONCURSO (Jueves a Jueves):")
    print(f"  • Semana ID:           {stats['week_id']}")
    print(f"  • Compras ejecutadas:  {stats['buys_count']} de 3 compras obligatorias", end="")
    if stats['buys_count'] >= 3:
        print("  -->  [CUOTA SEMANAL CUMPLIDA]")
    else:
        print(f"  -->  (Faltan {stats['trades_remaining']} compras)")
        
    print(f"  • Volumen acumulado:   {stats['buy_volume_eur']:.2f} € de 2.500 € mínimos requeridos")
    
    if open_pos:
        print(f"\n  [ALERTA DE POSICIÓN ACTIVA]")
        print(f"  Tienes {open_pos['shares']} acciones de {open_pos['ticker']} compradas el {open_pos['buy_date']} a {open_pos['buy_price']:.2f} €.")
        print(f"  --> RECUERDA: Vender mañana a las 09:00:01 CET a precio de Apertura.")
    else:
        print(f"  • Posición abierta:    NINGUNA (100% Liquidez)")
        
    if weekday_idx == 4:
        print("\n" + "!" * 95)
        print("  AVISO CRÍTICO DE VIERNES: Micro-Alfa NO opera los viernes.")
        print("  Las posiciones overnight en fin de semana conllevan riesgo innecesario de gap de lunes.")
        print("!" * 95)
        return

    # 2. Ingesta de Datos en Vivo
    print("\n" + "-" * 95)
    print("[2] OBTENIENDO COTIZACIONES EN TIEMPO REAL (5 Utilities)...")
    feed = LiveDataFeed()
    market_data, snapshots = feed.get_full_market_data()
    
    # 3. Comprobación de Eventos Corporativos
    corp_checker = CorporateEventsChecker()
    corp_alerts = corp_checker.check_events()
    
    # 4. Evaluación de Motor 1: Micro-Alfa CS
    engine_cs = EngineMicroAlfaCS(window=20, target_order_eur=900.0)
    df_cs = engine_cs.evaluate(market_data, snapshots, corp_alerts)
    
    # 5. Evaluación de Motor 2: Micro-Alfa NR10
    engine_nr = EngineMicroAlfaNR(window=10, target_order_eur=900.0)
    df_nr = engine_nr.evaluate(market_data, snapshots, corp_alerts)
    
    # 6. Mostrar Resultados de Motor 1: CS Reversion
    print("\n" + "=" * 95)
    print("MOTOR 1: MICRO-ALFA CS (Cross-Sectional Reversion | Z-Score Intradía 20d)")
    print("Criterio: Menor Z-Score = Activo más sobrevendido del día frente a su media reciente")
    print("-" * 95)
    
    headers_cs = ["Rank", "Ticker", "Nombre", "Precio", "Ret. Intra", "Z-Score", "Accs (~900€)", "Total (€)", "Alertas"]
    widths_cs  = [4, 7, 20, 9, 10, 9, 12, 10, 8]
    aligns_cs  = ['^', '<', '<', '>', '>', '>', '>', '>', '^']
    
    print(format_row(headers_cs, widths_cs, aligns_cs))
    print("-" * 95)
    
    for _, r in df_cs.iterrows():
        z_str = f"{r['Z_Score']:+.2f}"
        ret_str = f"{r['Retorno_Intradia_%']:+.2f}%"
        px_str = f"{r['Precio_Actual']:.2f} €"
        tot_str = f"{r['Importe_EUR']:.2f} €"
        rank_str = f"{r['Rank']}º"
        
        row_vals = [
            rank_str,
            r['Ticker'],
            r['Nombre'],
            px_str,
            ret_str,
            z_str,
            str(r['Acciones']),
            tot_str,
            r['Info_Corporativa']
        ]
        
        line = format_row(row_vals, widths_cs, aligns_cs)
        if r['Rank'] == 1:
            print(">>> " + line + "  <-- RECOMENDADO CS")
        else:
            print("    " + line)
            
    top_cs = df_cs.iloc[0]
    print(f"\n--> SELECCIÓN MOTOR CS: Comprar {top_cs['Acciones']} acciones de {top_cs['Ticker']} ({top_cs['Importe_EUR']:.2f} €)")

    # 7. Mostrar Resultados de Motor 2: NR10 Compression
    print("\n" + "=" * 95)
    print("MOTOR 2: MICRO-ALFA NR10 (Narrow Range 10 | Compresión Extrema de Rango)")
    print("Criterio: Menor Ratio NR = Mayor contracción de volatilidad. Prioriza mitad inferior.")
    print("-" * 95)
    
    headers_nr = ["Rank", "Ticker", "Nombre", "Precio", "Rango Hoy", "Rango 10d", "Ratio NR", "Pos. Rango", "Accs", "Total (€)"]
    widths_nr  = [4, 7, 20, 9, 9, 9, 8, 10, 5, 9]
    aligns_nr  = ['^', '<', '<', '>', '>', '>', '>', '^', '>', '>']
    
    print(format_row(headers_nr, widths_nr, aligns_nr))
    print("-" * 95)
    
    for _, r in df_nr.iterrows():
        px_str = f"{r['Precio_Actual']:.2f} €"
        rg_hoy = f"{r['Rango_Hoy_%']:.2f}%"
        rg_10d = f"{r['Rango_Medio_10d_%']:.2f}%"
        ratio_str = f"{r['Ratio_NR']:.2f}"
        pos_str = f"{r['Posicion_Rango_%']:.0f}% (Inf)" if r['Mitad_Inferior'] else f"{r['Posicion_Rango_%']:.0f}% (Sup)"
        tot_str = f"{r['Importe_EUR']:.2f} €"
        rank_str = f"{r['Rank']}º"
        
        row_vals = [
            rank_str,
            r['Ticker'],
            r['Nombre'],
            px_str,
            rg_hoy,
            rg_10d,
            ratio_str,
            pos_str,
            str(r['Acciones']),
            tot_str
        ]
        
        line = format_row(row_vals, widths_nr, aligns_nr)
        if r['Rank'] == 1:
            print(">>> " + line + "  <-- RECOMENDADO NR10")
        else:
            print("    " + line)
            
    top_nr = df_nr.iloc[0]
    print(f"\n--> SELECCIÓN MOTOR NR10: Comprar {top_nr['Acciones']} acciones de {top_nr['Ticker']} ({top_nr['Importe_EUR']:.2f} €)")

    # 8. Instrucciones y Ficha de Ejecución
    print("\n" + "=" * 95)
    print("INSTRUCCIONES PARA EL TRADER:")
    print("  1. Compara las dos recomendaciones anteriores y decide cuál ejecutar.")
    print("  2. Introduce la orden a mercado en el broker de BME antes de las 17:29:50.")
    print("  3. Puedes registrar la compra directamente a continuación pulsando [1] o [2].")
    print("  4. Recuerda que la venta de salida se ejecutará mañana a las 09:00:01 CET a precio de Apertura.")
    print("=" * 95)

    # 9. Registro Interactivo Directo en Caliente
    print("\n" + "-" * 95)
    print("¿DESEAS REGISTRAR LA COMPRA EJECUTADA AHORA MISMO?")
    print(f"  [1] Registrar recomendación CS   --> {top_cs['Ticker']}: {top_cs['Acciones']} accs a ~{top_cs['Precio_Actual']:.2f} €")
    print(f"  [2] Registrar recomendación NR10 --> {top_nr['Ticker']}: {top_nr['Acciones']} accs a ~{top_nr['Precio_Actual']:.2f} €")
    print(f"  [3] Registrar manualmente otro activo / precio real")
    print(f"  [0 o Enter] Salir sin registrar por ahora")
    print("-" * 95)
    
    try:
        user_choice = input("Selecciona una opción [1/2/3/Enter]: ").strip()
    except (EOFError, KeyboardInterrupt):
        user_choice = ""
        
    if user_choice == '1':
        try:
            px_input = input(f"Precio real en broker [Enter para {top_cs['Precio_Actual']:.2f} €]: ").strip()
            final_px = float(px_input.replace(',', '.')) if px_input else top_cs['Precio_Actual']
            sh_input = input(f"Acciones ejecutadas [Enter para {top_cs['Acciones']}]: ").strip()
            final_sh = int(sh_input) if sh_input else top_cs['Acciones']
            
            rec = ledger.record_trade('BUY', top_cs['Ticker'], final_sh, final_px)
            print(f"\n[OK] COMPRA REGISTRADA EN EL LIBRO OFICIAL:")
            print(f"     {final_sh} acciones de {top_cs['Ticker']} a {final_px:.2f} € ({rec['Importe_EUR']:.2f} €)")
            print(f"     Mañana a las 09:00:00 se abrirá la tarea de salida para registrar la venta.")
        except Exception as e:
            print(f"[ERROR] No se pudo registrar: {e}")
            
    elif user_choice == '2':
        try:
            px_input = input(f"Precio real en broker [Enter para {top_nr['Precio_Actual']:.2f} €]: ").strip()
            final_px = float(px_input.replace(',', '.')) if px_input else top_nr['Precio_Actual']
            sh_input = input(f"Acciones ejecutadas [Enter para {top_nr['Acciones']}]: ").strip()
            final_sh = int(sh_input) if sh_input else top_nr['Acciones']
            
            rec = ledger.record_trade('BUY', top_nr['Ticker'], final_sh, final_px)
            print(f"\n[OK] COMPRA REGISTRADA EN EL LIBRO OFICIAL:")
            print(f"     {final_sh} acciones de {top_nr['Ticker']} a {final_px:.2f} € ({rec['Importe_EUR']:.2f} €)")
            print(f"     Mañana a las 09:00:00 se abrirá la tarea de salida para registrar la venta.")
        except Exception as e:
            print(f"[ERROR] No se pudo registrar: {e}")
            
    elif user_choice == '3':
        try:
            t_input = input("Ticker comprado (ej: ENG.MC, ELE.MC): ").strip().upper()
            sh_input = int(input("Número de acciones: ").strip())
            px_input = float(input("Precio real de ejecución (€): ").strip().replace(',', '.'))
            
            rec = ledger.record_trade('BUY', t_input, sh_input, px_input)
            print(f"\n[OK] COMPRA REGISTRADA EN EL LIBRO OFICIAL:")
            print(f"     {sh_input} acciones de {t_input} a {px_input:.2f} € ({rec['Importe_EUR']:.2f} €)")
        except Exception as e:
            print(f"[ERROR] No se pudo registrar: {e}")
    else:
        print("\nSesión finalizada. Recuerda que puedes registrar más tarde con 'python scripts/log_trade.py'.")
    print("=" * 95 + "\n")

if __name__ == '__main__':
    main()
