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
        Verifica la regla: de cierre de jueves a cierre de jueves,
        >= 3 compras (>=2500€) y >= 3 ventas (>=2500€).
        Para adaptarlo al histórico, dividimos la ventana de 22 días en 
        bloques consecutivos de 7 días naturales o agrupar por semanas del año.
        """
        if not trades_history:
            return False
            
        df_trades = pd.DataFrame(trades_history)
        df_trades['date'] = pd.to_datetime(df_trades['date'])
        
        # Agrupamos por la semana ISO (empieza el lunes, pero nos sirve como proxy de 7 días)
        # Para ser precisos con el 'Jueves a Jueves', podemos desplazar los días 3 días (Lunes -> Jueves)
        df_trades['week_group'] = (df_trades['date'] + pd.Timedelta(days=3)).dt.isocalendar().week
        
        # Obtenemos las semanas que cayeron completas dentro de la ventana
        # (Descartamos la primera y última si son de muy pocos días, o evaluamos todas)
        groups = df_trades.groupby('week_group')
        
        # Si la ventana es de 22 días de trading, suele abarcar 4 semanas
        weeks_passed = 0
        for week, group in groups:
            buys = group[group['action'] == 'buy']
            sells = group[group['action'] == 'sell']
            
            buy_count = len(buys)
            sell_count = len(sells)
            
            buy_vol = (buys['shares'] * buys['price']).sum() if buy_count > 0 else 0
            sell_vol = (sells['shares'] * sells['price']).sum() if sell_count > 0 else 0
            
            # Condición estricta
            if buy_count >= 3 and sell_count >= 3 and buy_vol >= 2500 and sell_vol >= 2500:
                weeks_passed += 1
                
        # Un mes de 22 días suele abarcar 3 semanas de jueves a jueves (como indica el concurso: 22-29, 29-5, 5-12)
        return weeks_passed >= 3

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
