import os
import json
import uuid
import pandas as pd
from datetime import datetime

class ExperimentTracker:
    def __init__(self, exp_dir='../experiments'):
        self.exp_dir = exp_dir
        self.logs_dir = os.path.join(exp_dir, 'logs')
        self.leaderboard_path = os.path.join(exp_dir, 'leaderboard.csv')
        
        os.makedirs(self.logs_dir, exist_ok=True)
        
    def log_experiment(self, strategy_name, metrics, metadata=None):
        """
        Logs a heterogeneous experiment.
        :param strategy_name: str, name of the strategy/model.
        :param metrics: dict, flat dictionary with standard metrics (Return, Volatility, Score, etc.)
        :param metadata: dict, flexible dictionary for any specific hyperparams, ML features, external data flags.
        """
        if metadata is None:
            metadata = {}
            
        run_id = f"EXP-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        timestamp = datetime.now().isoformat()
        
        log_data = {
            'run_id': run_id,
            'timestamp': timestamp,
            'strategy_name': strategy_name,
            'metrics': metrics,
            'metadata': metadata
        }
        
        json_path = os.path.join(self.logs_dir, f"{run_id}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=4)
            
        leaderboard_entry = {
            'Run_ID': run_id,
            'Date': timestamp[:10],
            'Strategy': strategy_name,
            'Score_Avg': metrics.get('Score_Avg', None),
            'Return_1M_Avg': metrics.get('Return_1M_Avg', None),
            'Vol_Ann_Avg': metrics.get('Vol_Ann_Avg', None),
            'Win_Rate': metrics.get('Win_Rate', None),
            'Qualification_Rate': metrics.get('Qualification_Rate', None)
        }
        
        df_entry = pd.DataFrame([leaderboard_entry])
        
        if os.path.exists(self.leaderboard_path):
            df_entry.to_csv(self.leaderboard_path, mode='a', header=False, index=False)
        else:
            df_entry.to_csv(self.leaderboard_path, index=False)
            
        print(f"\nExperiment {run_id} logged successfully.")
        print(f"Details saved to: {json_path}")
        
        return run_id
