import pandas as pd

snap = pd.read_csv('data/processed/monthly_subscription_snapshot.csv', parse_dates=['month_end'])
raw = pd.read_csv('data/raw/ravenstack_subscriptions.csv', parse_dates=['start_date', 'end_date'])

print('columns:', list(snap.columns))
print('rows', len(snap), 'expected', len(raw) * snap.month_end.nunique())
print('duplicates', snap.duplicated(['subscription_id', 'month_end']).sum())

d = pd.Timestamp('2024-06-30')
act = raw[(raw.start_date <= d) & (raw.end_date.isna() | (raw.end_date > d)) & (~raw.is_trial)]
print('MRR June 2024', act.mrr_amount.sum(), 'snapshot', snap[snap.month_end == d].mrr_snapshot.sum())

new = snap[snap.is_new_subscription]
print('new flags', len(new), 'of which trial', new.is_trial.sum(), 'subscriptions in raw', len(raw))
ch = snap[snap.is_churned_subscription]
print('churn flags', len(ch), 'subscriptions with an end_date', raw.end_date.notna().sum())
same = raw[raw.end_date.notna() & (raw.start_date.dt.to_period('M') == raw.end_date.dt.to_period('M'))]
print('start and end in same month', len(same))
