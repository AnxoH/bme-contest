import pandas as pd
from src.analysis.evaluator import Evaluator

# Mocking some trades
# Imagine a window starting on 2020-01-01
dates = pd.bdate_range('2020-01-01', periods=22)
trades_history = []
for d in dates:
    trades_history.append({'date': d, 'action': 'buy', 'shares': 100, 'price': 10})
    trades_history.append({'date': d, 'action': 'sell', 'shares': 100, 'price': 10})

df_trades = pd.DataFrame(trades_history)
df_trades['week_group'] = (df_trades['date'] + pd.Timedelta(days=3)).dt.isocalendar().week

groups = df_trades.groupby('week_group')
weeks_passed = 0
for week, group in groups:
    buys = group[group['action'] == 'buy']
    sells = group[group['action'] == 'sell']
    buy_count = len(buys)
    sell_count = len(sells)
    buy_vol = (buys['shares'] * buys['price']).sum()
    sell_vol = (sells['shares'] * sells['price']).sum()
    print(f"Week {week}: buys={buy_count}({buy_vol}€), sells={sell_count}({sell_vol}€)")
    if buy_count >= 3 and sell_count >= 3 and buy_vol >= 2500 and sell_vol >= 2500:
        weeks_passed += 1

print(f"Total weeks passed: {weeks_passed}")
