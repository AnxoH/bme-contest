import pandas as pd
import json
import glob
import os

def main():
    log_files = glob.glob('experiments/logs/*.json')
    if not log_files:
        print("No experiments found.")
        return
        
    records = []
    for f in log_files:
        with open(f, 'r') as file:
            data = json.load(file)
            metrics = data.get('metrics', {})
            strategy_name = data.get('strategy_name', 'Unknown')
            timestamp = data.get('timestamp', '')
            
            record = {'Strategy': strategy_name, 'Timestamp': timestamp}
            record.update(metrics)
            records.append(record)
            
    df = pd.DataFrame(records)
    
    # Sort by Score_Avg descending
    if 'Score_Avg' in df.columns:
        # Group by strategy and take the most recent run
        df = df.sort_values('Timestamp', ascending=False).drop_duplicates(subset=['Strategy'])
        df = df.sort_values('Score_Avg', ascending=False)
        
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()
