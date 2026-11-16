"""Build the monthly KPI table used by the dashboard.

Run from the repository root:   python src/build_monthly_kpis.py
Output: data/processed/monthly_kpis.csv   (one row per month-end, 24 months)

Inputs: data/interim/*_clean.csv (made by src/clean_data.py). If those are missing,
the original files in data/raw/ are used. If data/processed/monthly_subscription_snapshot.csv
exists, the MRR column is cross-checked against it.

Definitions (see docs/metric_definitions.md)
- Active at date D: start_date <= D and (end_date is empty or end_date > D); trials excluded.
- MRR = sum of mrr_amount of active paid subscriptions at the month-end.
- New MRR = mrr_amount of paid subscriptions whose start_date falls in the month.
- Churned MRR = mrr_amount of paid subscriptions whose end_date falls in the month.
- Bridge check = opening MRR + New MRR - Churned MRR - closing MRR (must be 0).
- Opening customers = accounts that signed up BEFORE the month starts.
- Churned customers = DISTINCT opening customers with a non-reactivation churn event in the month.
- Customer churn % = churned customers / opening customers x 100.
- Active customers = accounts with at least one active paid subscription at the month-end.
- ARPA = MRR / active customers.
- Avg monthly churn 12M % = average of the monthly customer churn % over the last 12 months.
- LTV (illustrative) = ARPA / (avg monthly churn 12M % / 100). Revenue only, no margin.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, INTERIM, PROCESSED = ROOT / "data" / "raw", ROOT / "data" / "interim", ROOT / "data" / "processed"


def read(name, dates):
    path = INTERIM / f"{name}_clean.csv"
    if not path.exists():
        path = RAW / f"ravenstack_{name}.csv"
    df = pd.read_csv(path, parse_dates=dates)
    print("read", path.relative_to(ROOT), len(df), "rows")
    return df


def to_bool(series):
    if series.dtype == bool:
        return series
    return series.astype(str).str.strip().str.lower().isin(["true", "1", "yes"])


accounts = read("accounts", ["signup_date"])
subs = read("subscriptions", ["start_date", "end_date"])
churn = read("churn_events", ["churn_date"])
subs["is_trial"] = to_bool(subs["is_trial"])
churn["is_reactivation"] = to_bool(churn["is_reactivation"])
paid = subs[~subs["is_trial"]]


def active_paid(day):
    day = pd.Timestamp(day)
    return paid[(paid.start_date <= day) & (paid.end_date.isna() | (paid.end_date > day))]


rows = []
for month_end in pd.date_range("2023-01-31", "2024-12-31", freq="ME"):
    month_start = month_end.replace(day=1)
    prev_end = month_start - pd.Timedelta(days=1)
    now, before = active_paid(month_end), active_paid(prev_end)
    new = paid[(paid.start_date >= month_start) & (paid.start_date <= month_end)]
    ended = paid[(paid.end_date >= month_start) & (paid.end_date <= month_end)]
    eligible = set(accounts.loc[accounts.signup_date < month_start, "account_id"])
    events = churn[(churn.churn_date >= month_start) & (churn.churn_date <= month_end)]
    lost = set(events.loc[~events.is_reactivation, "account_id"]) & eligible
    back = set(events.loc[events.is_reactivation, "account_id"]) & eligible
    mrr, opening = now.mrr_amount.sum(), before.mrr_amount.sum()
    active_customers = now.account_id.nunique()
    rows.append({
        "month_start": month_start.date(), "month_end": month_end.date(),
        "mrr_opening": opening, "new_mrr": new.mrr_amount.sum(), "churned_mrr": ended.mrr_amount.sum(),
        "mrr": mrr, "bridge_check": opening + new.mrr_amount.sum() - ended.mrr_amount.sum() - mrr,
        "revenue_churn_rate_pct": round(100 * ended.mrr_amount.sum() / opening, 2) if opening else np.nan,
        "active_paid_subscriptions": len(now), "new_paid_subscriptions": len(new), "ended_paid_subscriptions": len(ended),
        "opening_customers": len(eligible), "churned_customers": len(lost), "reactivation_customers": len(back),
        "customer_churn_rate_pct": round(100 * len(lost) / len(eligible), 2) if eligible else np.nan,
        "active_customers": active_customers,
        "arpa": round(mrr / active_customers, 1) if active_customers else np.nan,
    })
kpi = pd.DataFrame(rows)

avg, ltv = [], []
starts = pd.to_datetime(kpi.month_start)
for i, r in kpi.iterrows():
    window = kpi.loc[(starts > pd.Timestamp(r.month_end) - pd.DateOffset(months=12)) &
                     (starts <= pd.Timestamp(r.month_end)), "customer_churn_rate_pct"].dropna()
    mean = window.mean() if len(window) else np.nan
    avg.append(round(mean, 2) if not np.isnan(mean) else np.nan)
    ltv.append(round(r.arpa / (mean / 100)) if mean and mean > 0 and not np.isnan(r.arpa) else np.nan)
kpi["avg_monthly_churn_12m_pct"], kpi["ltv_illustrative"] = avg, ltv

PROCESSED.mkdir(parents=True, exist_ok=True)
out = PROCESSED / "monthly_kpis.csv"
kpi.to_csv(out, index=False)
print("Wrote", out.relative_to(ROOT), "rows =", len(kpi))
print("Bridge check is zero in every month:", bool((kpi.bridge_check == 0).all()))

snap_path = PROCESSED / "monthly_subscription_snapshot.csv"
if snap_path.exists():
    snap = pd.read_csv(snap_path, usecols=["month_end", "mrr_snapshot"], parse_dates=["month_end"])
    by_month = snap.groupby(snap.month_end.dt.date).mrr_snapshot.sum()
    same = all(abs(by_month.get(r.month_end, np.nan) - r.mrr) < 0.5 for r in kpi.itertuples())
    print("MRR equals the sum of mrr_snapshot in the snapshot for every month:", same)