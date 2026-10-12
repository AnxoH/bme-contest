import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.portfolio import Portfolio
from src.analysis.evaluator import Evaluator
from src.engine.tracker import ExperimentTracker

# Import 21 strategies
from src.strategies.bare_minimum import BareMinimumStrategy
from src.strategies.baseline_reversion import BaselineReversion
from src.strategies.conservative_rotation import ConservativeBlueChipRotation
from src.strategies.continuous_utility_reversion import ContinuousUtilityReversion
from src.strategies.cross_sectional_reversion import CrossSectionalReversion
from src.strategies.ensemble_cs_nr import EnsembleCSNR
from src.strategies.mean_reversion import MeanReversionStrategy
from src.strategies.micro_alfa_quirurgico import MicroAlfaQuirurgico
from src.strategies.nr10_breakout import NR10Breakout
from src.strategies.patient_sniper import PatientSniperStrategy
from src.strategies.quality_reversion import OvernightQualityReversion
from src.strategies.rsi_reversion import RsiOvernightReversion
from src.strategies.seasonality_safehaven import SeasonalitySafeHaven
from src.strategies.single_asset import SingleAssetMaster
from src.strategies.slow_train import SlowTrainStrategy
from src.strategies.smart_minimum_contrarian import SmartMinimumContrarian
from src.strategies.smart_minimum_intraday import SmartMinimumIntraday
from src.strategies.smart_minimum_seasonal import SmartMinimumSeasonal
from src.strategies.turnaround_tuesday import TurnaroundTuesday
from src.strategies.ultralowvol_momentum import UltraLowVolMomentum

def main():
    print("=" * 80)
    print("TORNEO MAESTRO BME CONTEST: 31 PARTICIPANTES (21 ESTRATEGIAS + 10 COMPETIDORES)")
    print("=" * 80)
    
    # 1. Cargar datos de mercado
    print("\n[1/6] Cargando datos historicos OHLCV de 15 anos...")
    close_prices = pd.read_csv('data/raw/stocks_close_15y.csv', index_col=0, parse_dates=True)
    open_prices = pd.read_csv('data/raw/stocks_open_15y.csv', index_col=0, parse_dates=True)
    high_prices = pd.read_csv('data/raw/stocks_high_15y.csv', index_col=0, parse_dates=True)
    low_prices = pd.read_csv('data/raw/stocks_low_15y.csv', index_col=0, parse_dates=True)
    
    market_df = pd.read_csv('data/raw/market_composition.csv')
    ibex_tickers = market_df[market_df['Is_IBEX35'] == True]['Ticker'].tolist()
    universe = [t for t in ibex_tickers if t in close_prices.columns]
    
    # Ultimos 1500 dias de mercado
    N_DAYS = 1500
    close_prices = close_prices[universe].tail(N_DAYS).ffill()
    open_prices = open_prices[universe].tail(N_DAYS).ffill()
    high_prices = high_prices[universe].tail(N_DAYS).ffill()
    low_prices = low_prices[universe].tail(N_DAYS).ffill()
    
    # 2. Cargar competidores sinteticos
    print("\n[2/6] Cargando competidores sinteticos (rivales del concurso)...")
    Evaluator.load_competitors('data/processed/competitors_returns.csv')
    comp_df = Evaluator._competitors_df
    if comp_df is None:
        raise ValueError("No se encontro data/processed/competitors_returns.csv")
        
    synthetic_names = comp_df.columns.tolist()
    print(f"Competidores sinteticos cargados ({len(synthetic_names)}): {synthetic_names}")
    
    # 3. Instanciar las 21 estrategias con sus parametros nativos
    print("\n[3/6] Instanciando las 21 estrategias propias con parametros nativos...")
    strategies = [
        BareMinimumStrategy(),
        BaselineReversion(),
        ConservativeBlueChipRotation(allocation_eur=2500),
        ContinuousUtilityReversion(order_amount=4667.0, window=20),
        CrossSectionalReversion(order_amount=4667.0, z_threshold=-1.0, window=20, max_weekly_trades=3),
        EnsembleCSNR(order_amount=900.0, window_z=20, window_range=10, grace_period_days=5, name='Ensemble_CS_NR'),
        MeanReversionStrategy(),
        MicroAlfaQuirurgico(order_amount=900.0, engine='cs_reversion', grace_period_days=5, name='MicroAlfa_CS'),
        MicroAlfaQuirurgico(order_amount=900.0, engine='nr10', grace_period_days=5, name='MicroAlfa_NR10'),
        NR10Breakout(order_amount=4667.0, window=10, max_weekly_trades=3),
        PatientSniperStrategy(vol_window=60, rsi_window=14, rsi_threshold=40, base_amount=2500, snipe_amount=10000),
        OvernightQualityReversion(allocation_eur=2500, sma_period=200, min_sma_dist=1.05),
        RsiOvernightReversion(rsi_period=3, allocation_eur=2500),
        SeasonalitySafeHaven(dummy_allocation=2500, strong_allocation=10000),
        SingleAssetMaster(target_ticker='IBE.MC', allocation_eur=2500),
        SlowTrainStrategy(vol_window=20, mom_window=10, top_n_vol=5, order_amount=2500),
        SmartMinimumContrarian(asset='RED.MC', trade_amount=2500),
        SmartMinimumIntraday(asset='RED.MC', trade_amount=2500, window=10),
        SmartMinimumSeasonal(asset='RED.MC', trade_amount=2500),
        TurnaroundTuesday(allocation_eur=10000, dummy_allocation=2500),
        UltraLowVolMomentum(allocation_eur=2500)
    ]
    
    strat_names = [s.name for s in strategies]
    print(f"Estrategias propias instanciadas ({len(strategies)}):")
    for s in strategies:
        print(f"  - {s.name} (Clase: {s.__class__.__name__})")
        
    print(f"\nPOOL TOTAL DE PARTICIPANTES: {len(strategies) + len(synthetic_names)} (21 Propias + 10 Rivales)")
    
    # 4. Definir ventanas rodantes de 22 dias bursatiles con paso 11
    WINDOW_SIZE = 22
    STEP = 11
    INITIAL_CAPITAL = 50000.0
    
    n_days = len(close_prices)
    start_points = list(range(0, n_days - WINDOW_SIZE, STEP))
    total_windows = len(start_points)
    print(f"\n[4/6] Ejecutando simulacion a lo largo de {total_windows} ventanas rodantes...")
    
    # Colecciones de datos granulares
    all_windows_raw = []      # Fila por ventana x participante
    all_daily_nav = []        # Curvas de equity diarias
    all_trades_audit = []     # Todos los trades ejecutados
    
    # Pre-ejecutar cada estrategia a traves de todas las ventanas
    # Guardamos los resultados por estrategia y ventana para cruzar simultaneamente
    strategy_window_runs = {} # {strat_name: {win_idx: {metrics, equity, trades}}}
    
    for s_idx, strat in enumerate(strategies):
        print(f"  [{s_idx+1:02d}/{len(strategies)}] Simulando estrategia: {strat.name}...")
        strategy_window_runs[strat.name] = {}
        
        for w_idx, start in enumerate(start_points):
            window_dates = close_prices.index[start : start + WINDOW_SIZE]
            if len(window_dates) < WINDOW_SIZE * 0.8:
                continue
                
            portfolio = Portfolio(initial_capital=INITIAL_CAPITAL)
            equity_curve = []
            
            for i, date in enumerate(window_dates):
                portfolio.window_day = i
                portfolio.update_days_held()
                
                market_data = {
                    'close': close_prices.loc[:date],
                    'open': open_prices.loc[:date],
                    'high': high_prices.loc[:date],
                    'low': low_prices.loc[:date]
                }
                
                orders = strat.generate_signals(date, market_data, portfolio)
                
                for order in orders:
                    ticker = order['ticker']
                    action = order['action']
                    
                    if action == 'sell':
                        shares = portfolio.positions[ticker]['shares']
                        price_type = order.get('price_type', 'close')
                        px = open_prices.loc[date, ticker] if price_type == 'open' else close_prices.loc[date, ticker]
                        if pd.isna(px) or px <= 0:
                            continue
                        portfolio.execute_trade(ticker, 'sell', shares, px, date)
                        
                    elif action == 'buy':
                        px = close_prices.loc[date, ticker]
                        if pd.isna(px) or px <= 0:
                            continue
                        target_eur = order['amount_eur']
                        shares = int(target_eur / px)
                        if shares <= 0:
                            continue
                        portfolio.execute_trade(ticker, 'buy', shares, px, date)
                
                current_nav = portfolio.get_total_value(close_prices.loc[date])
                equity_curve.append(current_nav)
                
            eq_series = pd.Series(equity_curve, index=window_dates)
            ret_1m = (eq_series.iloc[-1] / eq_series.iloc[0]) - 1.0
            daily_pct = eq_series.pct_change().dropna()
            vol_ann = daily_pct.std() * np.sqrt(252) if len(daily_pct) > 0 else 0.0
            
            # Auditoria de reglas BME
            is_qualified = Evaluator.audit_weekly_activity(portfolio.trades_history, window_dates)
            
            strategy_window_runs[strat.name][w_idx] = {
                'window_start': window_dates[0],
                'window_end': window_dates[-1],
                'dates': window_dates,
                'equity_curve': equity_curve,
                'daily_returns': daily_pct.tolist(),
                'return_1m': ret_1m,
                'vol_ann': vol_ann,
                'qualified': is_qualified,
                'trades': portfolio.trades_history,
                'trades_count': len(portfolio.trades_history)
            }
            
            # Guardar trades para la auditoria exhaustiva
            for tr in portfolio.trades_history:
                all_trades_audit.append({
                    'Window_Index': w_idx,
                    'Window_Start': window_dates[0].strftime('%Y-%m-%d'),
                    'Window_End': window_dates[-1].strftime('%Y-%m-%d'),
                    'Participant': strat.name,
                    'Date': str(tr['date'])[:10],
                    'Ticker': tr['ticker'],
                    'Action': tr['action'],
                    'Shares': tr['shares'],
                    'Price': tr['price'],
                    'Amount_Eur': tr['shares'] * tr['price']
                })

    # 5. Cruzar todas las ventanas en el Torneo Oficial BME de 31 participantes
    print("\n[5/6] Cruzando resultados en el Torneo Oficial BME (Formula de 31 participantes)...")
    
    for w_idx, start in enumerate(start_points):
        window_dates = close_prices.index[start : start + WINDOW_SIZE]
        if len(window_dates) < WINDOW_SIZE * 0.8:
            continue
            
        w_start_str = window_dates[0].strftime('%Y-%m-%d')
        w_end_str = window_dates[-1].strftime('%Y-%m-%d')
        
        participants_data = []
        
        # A) Estrategias Propias
        for strat in strategies:
            run_data = strategy_window_runs[strat.name].get(w_idx)
            if run_data is not None:
                participants_data.append({
                    'name': strat.name,
                    'type': 'Strategy',
                    'ret': run_data['return_1m'],
                    'vol': run_data['vol_ann'],
                    'qualified': run_data['qualified'],
                    'trades_count': run_data['trades_count'],
                    'equity_curve': run_data['equity_curve'],
                    'dates': run_data['dates']
                })
                
        # B) Competidores Sinteticos
        valid_dates = [d for d in window_dates if d in comp_df.index]
        if len(valid_dates) > 0:
            comp_slice = comp_df.loc[valid_dates]
            for col in synthetic_names:
                daily_rets = comp_slice[col].dropna()
                if len(daily_rets) > 0:
                    ret = np.prod(1 + daily_rets) - 1.0
                    vol = daily_rets.std() * np.sqrt(252)
                    comp_equity = (INITIAL_CAPITAL * (1 + daily_rets).cumprod()).tolist()
                else:
                    ret = 0.0
                    vol = 0.0
                    comp_equity = [INITIAL_CAPITAL] * len(valid_dates)
                    
                participants_data.append({
                    'name': col,
                    'type': 'Synthetic_Competitor',
                    'ret': ret,
                    'vol': vol,
                    'qualified': True, # Creados cumpliendo las reglas
                    'trades_count': 18, # 3 compras + 3 ventas por 3 semanas
                    'equity_curve': comp_equity,
                    'dates': valid_dates
                })
                
        # Calcular puntuaciones oficiales BME
        # Final NAV para calificados
        for p in participants_data:
            p['final_val'] = INITIAL_CAPITAL * (1 + p['ret'])
            
        qualified_participants = [p for p in participants_data if p['qualified']]
        
        if len(qualified_participants) > 0:
            max_val = max([p['final_val'] for p in qualified_participants])
            min_vol = min([p['vol'] for p in qualified_participants])
            max_vol = max([p['vol'] for p in qualified_participants])
            
            for p in qualified_participants:
                p['score_ret'] = (p['final_val'] * 6.0) / max_val if max_val > 0 else 0.0
                if max_vol == min_vol:
                    p['score_vol'] = 3.0
                else:
                    p['score_vol'] = 3.0 * (1.0 - (p['vol'] - min_vol) / (max_vol - min_vol))
                p['score_total'] = p['score_ret'] + p['score_vol']
                
            qualified_participants.sort(key=lambda x: x['score_total'], reverse=True)
            for rank_i, p in enumerate(qualified_participants):
                p['rank'] = rank_i + 1
        else:
            max_val = INITIAL_CAPITAL
            min_vol, max_vol = 0.0, 0.0
            
        # Asignar rank a descalificados
        disqualified_participants = [p for p in participants_data if not p['qualified']]
        for p in disqualified_participants:
            p['score_ret'] = 0.0
            p['score_vol'] = 0.0
            p['score_total'] = 0.0
            p['rank'] = len(participants_data)
            
        # Registrar datos ventana a ventana
        for p in participants_data:
            all_windows_raw.append({
                'Window_Index': w_idx,
                'Window_Start': w_start_str,
                'Window_End': w_end_str,
                'Participant': p['name'],
                'Type': p['type'],
                'Return_1M': p['ret'],
                'Vol_Ann': p['vol'],
                'Final_Nav': p['final_val'],
                'Score_Ret': p['score_ret'],
                'Score_Vol': p['score_vol'],
                'Score_Total': p['score_total'],
                'Rank': p['rank'],
                'Trades_Count': p['trades_count'],
                'Qualified': p['qualified']
            })
            
            # Registrar NAV diario
            for d_idx, (dt, eq) in enumerate(zip(p['dates'], p['equity_curve'])):
                all_daily_nav.append({
                    'Window_Index': w_idx,
                    'Date': dt.strftime('%Y-%m-%d'),
                    'Participant': p['name'],
                    'Type': p['type'],
                    'Nav': eq
                })

    df_windows_raw = pd.DataFrame(all_windows_raw)
    df_daily_nav = pd.DataFrame(all_daily_nav)
    df_trades_audit = pd.DataFrame(all_trades_audit)
    
    # 6. Construir Master Summary
    print("\n[6/6] Agregando estadisticas y construyendo Master Leaderboard...")
    summary_records = []
    
    for participant in df_windows_raw['Participant'].unique():
        sub = df_windows_raw[df_windows_raw['Participant'] == participant]
        p_type = sub['Type'].iloc[0]
        
        n_windows = len(sub)
        score_avg = sub['Score_Total'].mean()
        score_median = sub['Score_Total'].median()
        score_std = sub['Score_Total'].std()
        
        avg_rank = sub['Rank'].mean()
        median_rank = sub['Rank'].median()
        best_rank = sub['Rank'].min()
        worst_rank = sub['Rank'].max()
        
        win_rate = (sub['Rank'] == 1).mean()
        top3_rate = (sub['Rank'] <= 3).mean()
        top5_rate = (sub['Rank'] <= 5).mean()
        
        ret_avg = sub['Return_1M'].mean()
        ret_median = sub['Return_1M'].median()
        ret_std = sub['Return_1M'].std()
        
        vol_avg = sub['Vol_Ann'].mean()
        trades_avg = sub['Trades_Count'].mean()
        qual_rate = sub['Qualified'].mean()
        
        summary_records.append({
            'Participant': participant,
            'Type': p_type,
            'Score_Avg': score_avg,
            'Score_Median': score_median,
            'Score_Std': score_std,
            'Avg_Rank': avg_rank,
            'Median_Rank': median_rank,
            'Best_Rank': best_rank,
            'Worst_Rank': worst_rank,
            'Win_Rate_Global': win_rate,
            'Top3_Rate': top3_rate,
            'Top5_Rate': top5_rate,
            'Return_1M_Avg': ret_avg,
            'Return_1M_Median': ret_median,
            'Return_1M_Std': ret_std,
            'Vol_Ann_Avg': vol_avg,
            'Trades_Count_Avg': trades_avg,
            'Qualification_Rate': qual_rate
        })
        
    df_summary = pd.DataFrame(summary_records).sort_values(['Score_Median', 'Score_Avg'], ascending=[False, False]).reset_index(drop=True)
    df_summary.insert(0, 'Rank_Overall', range(1, len(df_summary) + 1))
    
    # Guardar todos los macro documentos
    os.makedirs('experiments', exist_ok=True)
    os.makedirs('experiments/fases', exist_ok=True)
    
    path_summary = 'experiments/master_tournament_summary.csv'
    path_raw = 'experiments/master_tournament_windows_raw.csv'
    path_daily = 'experiments/master_tournament_daily_nav.csv'
    path_trades = 'experiments/master_trades_audit.csv'
    
    df_summary.to_csv(path_summary, index=False)
    df_windows_raw.to_csv(path_raw, index=False)
    df_daily_nav.to_csv(path_daily, index=False)
    df_trades_audit.to_csv(path_trades, index=False)
    
    print("\n" + "=" * 80)
    print("ARCHIVOS MAESTROS GENERADOS EXITOSAMENTE:")
    print(f"  1. Resumen Ejecutivo (Leaderboard): {path_summary} ({len(df_summary)} filas)")
    print(f"  2. Auditoria Ventana a Ventana:     {path_raw} ({len(df_windows_raw)} filas)")
    print(f"  3. Curvas de Equity Diarias:        {path_daily} ({len(df_daily_nav)} filas)")
    print(f"  4. Registro Exhaustivo de Trades:   {path_trades} ({len(df_trades_audit)} filas)")
    print("=" * 80)
    
    print("\nTOP 15 PARTICIPANTES:")
    cols_display = ['Rank_Overall', 'Participant', 'Score_Avg', 'Avg_Rank', 'Win_Rate_Global', 'Top3_Rate', 'Return_1M_Avg', 'Vol_Ann_Avg']
    print(df_summary[cols_display].head(15).to_string(index=False))

    # Guardar tambien reporte en Markdown
    md_report_path = 'experiments/fases/master_tournament_31_participantes.md'
    with open(md_report_path, 'w', encoding='utf-8') as f:
        f.write("# Resultados del Macro-Torneo BME: 31 Participantes (Pool Completo)\n\n")
        f.write(f"Fecha de generacion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("Este informe recoge la evaluacion unificada de **todas y cada una de las estrategias validas** (21 estrategias con sus parametros nativos) y los **10 perfiles sinteticos de competidores** simulados a lo largo de 1.500 dias bursatiles en ventanas rodantes de 22 dias.\n\n")
        f.write("## Clasificacion General (Leaderboard Completo)\n\n")
        f.write("| Puesto | Participante | Tipo | Score Medio | Puesto Medio | Win Rate #1 | Top 3 Rate | Retorno 1M | Vol Anual | Calif. |\n")
        f.write("|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n")
        for _, r in df_summary.iterrows():
            f.write(f"| {r['Rank_Overall']} | **{r['Participant']}** | {r['Type']} | {r['Score_Avg']:.4f} | {r['Avg_Rank']:.2f} | {r['Win_Rate_Global']*100:.2f}% | {r['Top3_Rate']*100:.2f}% | {r['Return_1M_Avg']*100:.2f}% | {r['Vol_Ann_Avg']*100:.2f}% | {r['Qualification_Rate']*100:.1f}% |\n")
        f.write("\n## Archivos de Datos Asociados\n\n")
        f.write("- [experiments/master_tournament_summary.csv](file:///d:/Escritorio/Profesional/BME%20contest/experiments/master_tournament_summary.csv)\n")
        f.write("- [experiments/master_tournament_windows_raw.csv](file:///d:/Escritorio/Profesional/BME%20contest/experiments/master_tournament_windows_raw.csv)\n")
        f.write("- [experiments/master_tournament_daily_nav.csv](file:///d:/Escritorio/Profesional/BME%20contest/experiments/master_tournament_daily_nav.csv)\n")
        f.write("- [experiments/master_trades_audit.csv](file:///d:/Escritorio/Profesional/BME%20contest/experiments/master_trades_audit.csv)\n")

    print(f"\nReporte Markdown guardado en: {md_report_path}")

if __name__ == '__main__':
    main()
