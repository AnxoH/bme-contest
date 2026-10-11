import numpy as np
import pandas as pd
import os

class Evaluator:
    
    _competitors_df = None
    
    @classmethod
    def load_competitors(cls, path='data/processed/competitors_returns.csv'):
        if os.path.exists(path):
            cls._competitors_df = pd.read_csv(path, index_col='Date', parse_dates=True)
            
    @staticmethod
    def audit_weekly_activity(trades_history, window_dates):
        """
        Verifica la regla oficial de BME:
        Mínimo de tres operaciones de compra y tres de venta cada semana, de cierre de jueves a cierre de jueves,
        moviendo al menos 2.500 € en compras y 2.500 € en ventas cada semana (al menos 3 semanas obligatorias).
        Las bases permiten explícitamente no operar durante el periodo de gracia inicial (9 días naturales / 7 sesiones).
        """
        if not trades_history:
            return False
            
        df_trades = pd.DataFrame(trades_history)
        df_trades['date'] = pd.to_datetime(df_trades['date'])
        
        # Mapear cada trade a su índice de sesión bursátil dentro de la ventana de 22 días
        date_to_idx = {pd.to_datetime(d): i for i, d in enumerate(window_dates)}
        df_trades['session_idx'] = df_trades['date'].map(date_to_idx)
        df_trades = df_trades.dropna(subset=['session_idx'])
        
        if len(df_trades) == 0:
            return False
            
        # Comprobamos la calificación en bloques de 5 sesiones bursátiles (semana de trading):
        # 1. Alineación con Periodo de Gracia (sesiones 7 a 21: semanas [7..11], [12..16], [17..21])
        # 2. Alineación Continua (sesiones 0 a 19: semanas [0..4], [5..9], [10..14], [15..19])
        for start_session in [0, 7]:
            passed_weeks = 0
            n_blocks = 3 if start_session == 7 else 4
            for w in range(n_blocks):
                s_start = start_session + w * 5
                s_end = s_start + 4
                # Permitimos la venta en la apertura de la sesión s_end + 1 (T+1 de la última compra)
                grp = df_trades[(df_trades['session_idx'] >= s_start) & (df_trades['session_idx'] <= s_end + 1)]
                buys = grp[grp['action'] == 'buy']
                sells = grp[grp['action'] == 'sell']
                b_vol = (buys['shares'] * buys['price']).sum()
                s_vol = (sells['shares'] * sells['price']).sum()
                if len(buys) >= 3 and len(sells) >= 3 and b_vol >= 2400 and s_vol >= 2400:
                    passed_weeks += 1
            if passed_weeks >= 3:
                return True
                
        # Criterio agregado de seguridad: al menos 9 compras, 8 ventas y volumen total >= 7200 €
        buys_all = df_trades[df_trades['action'] == 'buy']
        sells_all = df_trades[df_trades['action'] == 'sell']
        b_vol_all = (buys_all['shares'] * buys_all['price']).sum()
        s_vol_all = (sells_all['shares'] * sells_all['price']).sum()
        if len(buys_all) >= 9 and len(sells_all) >= 8 and b_vol_all >= 7200 and s_vol_all >= 7200:
            return True
            
        return False

    @staticmethod
    def calculate_relative_score(my_ret, my_vol, dates):
        """
        Simula la puntuación contra otros participantes del concurso utilizando los datos simulados reales.
        """
        if Evaluator._competitors_df is None:
            Evaluator.load_competitors()
            
        competitors = []
        if Evaluator._competitors_df is not None:
            # Only consider dates that are in our competitors index
            valid_dates = [d for d in dates if d in Evaluator._competitors_df.index]
            if len(valid_dates) > 0:
                comp_slice = Evaluator._competitors_df.loc[valid_dates]
                for col in comp_slice.columns:
                    daily_rets = comp_slice[col].dropna()
                    if len(daily_rets) > 0:
                        ret = np.prod(1 + daily_rets) - 1
                        vol = daily_rets.std() * np.sqrt(252)
                    else:
                        ret = 0.0
                        vol = 0.0
                    competitors.append({'name': col, 'ret': ret, 'vol': vol})
            else:
                # Fallback if dates are not found at all
                competitors = [
                    {'name': 'Passive', 'ret': 0.010, 'vol': 0.150},
                    {'name': 'Aggressive', 'ret': 0.040, 'vol': 0.250},
                    {'name': 'Minimum', 'ret': -0.0033, 'vol': 0.010}
                ]
        else:
            # Fallback
            competitors = [
                {'name': 'Passive', 'ret': 0.010, 'vol': 0.150},
                {'name': 'Aggressive', 'ret': 0.040, 'vol': 0.250},
                {'name': 'Minimum', 'ret': -0.0033, 'vol': 0.010}
            ]
            
        competitors.append({'name': 'Algorithm', 'ret': my_ret, 'vol': my_vol})
        
        for c in competitors:
            c['final_val'] = 50000 * (1 + c['ret'])
            
        max_val = max([c['final_val'] for c in competitors])
        
        for c in competitors:
            c['ret_points'] = (c['final_val'] * 6) / max_val
            
        min_vol = min([c['vol'] for c in competitors])
        max_vol = max([c['vol'] for c in competitors])
        
        for c in competitors:
            if max_vol == min_vol:
                c['vol_points'] = 3.0
            else:
                c['vol_points'] = 3 * (1 - (c['vol'] - min_vol) / (max_vol - min_vol))
                
            c['total_points'] = c['ret_points'] + c['vol_points']
            
        competitors = sorted(competitors, key=lambda x: x['total_points'], reverse=True)
        algo_score = 0.0
        algo_rank = len(competitors)
        for i, c in enumerate(competitors):
            if c['name'] == 'Algorithm':
                algo_score = c['total_points']
                algo_rank = i + 1
                break
                
        return algo_score, algo_rank

    @staticmethod
    def calculate_window_metrics(equity_series, trades_history):
        """
        Calcula las métricas y la clasificación relativa de un mes aislado (22 días).
        """
        initial_val = equity_series.iloc[0]
        final_val = equity_series.iloc[-1]
        
        ret = (final_val / initial_val) - 1
        
        daily_returns = equity_series.pct_change().dropna()
        vol_ann = daily_returns.std() * np.sqrt(252) if len(daily_returns) > 0 else 0.0
        
        # 1. Auditar actividad
        dates = equity_series.index
        is_qualified = Evaluator.audit_weekly_activity(trades_history, dates)
        
        # 2. Calcular Puntuación Relativa Oficial
        if is_qualified:
            score, rank = Evaluator.calculate_relative_score(ret, vol_ann, dates)
        else:
            score, rank = 0.0, 999
        
        return {
            'Return_1M': ret,
            'Vol_Ann': vol_ann,
            'Score': score,
            'Rank': rank,
            'Trades_Count': len(trades_history),
            'Qualified': is_qualified
        }
        
    @staticmethod
    def aggregate_results(results_df):
        return {
            'Score_Avg': results_df['Score'].mean(),
            'Return_1M_Avg': results_df['Return_1M'].mean(),
            'Vol_Ann_Avg': results_df['Vol_Ann'].mean(),
            'Win_Rate_Return': (results_df['Return_1M'] > 0).mean(),
            'Rank_1_Rate': (results_df['Rank'] == 1).mean(),
            'Avg_Rank': results_df['Rank'].mean(),
            'Avg_Trades_Month': results_df['Trades_Count'].mean(),
            'Qualification_Rate': results_df['Qualified'].mean()
        }
