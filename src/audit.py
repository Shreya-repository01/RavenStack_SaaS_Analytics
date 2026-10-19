"""Week 1 data-quality audit. Writes reports/data_quality_audit.csv.
Run:  python src/audit.py
Each check = (table, check, count, note). Document every finding and cleaning decision; do NOT silently drop rows.
"""
import pandas as pd
from config import REPORTS, DATA_END
from load_data import load_all

d = load_all()
a, s, f, t, c = (d[k] for k in ["accounts", "subscriptions", "feature_usage", "support_tickets", "churn_events"])
rows = []


def add(table, check, count, note=""):
    rows.append(dict(table=table, check=check, count=int(count), note=note))


# 1. Identifiers
add("accounts", "duplicate account_id", a.account_id.duplicated().sum())
add("subscriptions", "duplicate subscription_id", s.subscription_id.duplicated().sum())
add("feature_usage", "duplicate usage_id (ID collision, content differs)", f.usage_id.duplicated().sum(), "flag, do not drop")
add("support_tickets", "duplicate ticket_id", t.ticket_id.duplicated().sum())
add("churn_events", "duplicate churn_event_id", c.churn_event_id.duplicated().sum())

# 2. Referential integrity
add("subscriptions", "orphan account_id", (~s.account_id.isin(a.account_id)).sum())
add("feature_usage", "orphan subscription_id", (~f.subscription_id.isin(s.subscription_id)).sum())
add("support_tickets", "orphan account_id", (~t.account_id.isin(a.account_id)).sum())
add("churn_events", "orphan account_id", (~c.account_id.isin(a.account_id)).sum())

# 3. Missing values
for name, df in d.items():
    for col, n in df.isna().sum().items():
        if n:
            add(name, f"nulls in {col}", n)

# 4. Subscription logic
add("subscriptions", "end_date < start_date", (s.end_date < s.start_date).sum())
add("subscriptions", "churn_flag True but end_date null", (s.churn_flag & s.end_date.isna()).sum())
add("subscriptions", "trial rows (mrr should be 0)", s.is_trial.sum())
add("subscriptions", "non-trial rows with mrr == 0", ((s.mrr_amount == 0) & ~s.is_trial).sum())
add("subscriptions", "arr_amount != 12 * mrr_amount", (s.arr_amount != 12 * s.mrr_amount).sum(),
    "mrr_amount is already monthly, even for annual billing")
add("subscriptions", "upgrade_flag AND downgrade_flag both True", (s.upgrade_flag & s.downgrade_flag).sum())

s2 = s.sort_values(["account_id", "start_date"]).copy()
s2["end_f"] = s2.end_date.fillna(pd.Timestamp(DATA_END))
s2["prev_end"] = s2.groupby("account_id").end_f.shift()
add("subscriptions", "rows overlapping another sub of same account", (s2.start_date < s2.prev_end).sum(),
    "decide subscription grain before summing MRR")
add("subscriptions", "subscriptions still active at data end", s.end_date.isna().sum(),
    "MRR snapshot will rise nearly monotonically")

m = s.merge(a[["account_id", "signup_date", "plan_tier"]], on="account_id", suffixes=("", "_acct"))
add("subscriptions", "start_date before account signup_date", (m.start_date < m.signup_date).sum())
add("subscriptions", "sub plan_tier != accounts.plan_tier", (m.plan_tier != m.plan_tier_acct).sum(),
    "accounts.plan_tier = initial plan only")

# 5. Churn consistency across three sources
add("accounts", "accounts with churn_flag True", a.churn_flag.sum())
add("churn_events", "distinct accounts with a churn event", c.account_id.nunique())
add("churn_events", "accounts with >1 churn event", (c.groupby("account_id").size() > 1).sum())
add("accounts", "churn_flag True but no churn event", (a.churn_flag & ~a.account_id.isin(c.account_id)).sum())
add("accounts", "churn event exists but churn_flag False", (~a.churn_flag & a.account_id.isin(c.account_id)).sum())
act = s[s.end_date.isna()].account_id.unique()
add("accounts", "churn_flag True yet has an active subscription", (a.churn_flag & a.account_id.isin(act)).sum())

# 6. Usage / tickets
u = f.merge(s[["subscription_id", "start_date"]], on="subscription_id")
add("feature_usage", "usage_date before its subscription start_date", (u.usage_date < u.start_date).sum())
add("support_tickets", "closed_at < submitted_at", (t.closed_at < t.submitted_at).sum())

out = pd.DataFrame(rows)
REPORTS.mkdir(exist_ok=True)
out.to_csv(REPORTS / "data_quality_audit.csv", index=False)
pd.set_option("display.width", 200, "display.max_colwidth", 70)
print(out.to_string(index=False))
