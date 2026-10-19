"""Shared paths and constants. Import this instead of hard-coding paths."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"

TABLES = {
    "accounts": dict(file="ravenstack_accounts.csv", dates=["signup_date"]),
    "subscriptions": dict(file="ravenstack_subscriptions.csv", dates=["start_date", "end_date"]),
    "feature_usage": dict(file="ravenstack_feature_usage.csv", dates=["usage_date"]),
    "support_tickets": dict(file="ravenstack_support_tickets.csv", dates=["submitted_at", "closed_at"]),
    "churn_events": dict(file="ravenstack_churn_events.csv", dates=["churn_date"]),
}
DATA_END = "2024-12-31"  # last date present in the data; used for 'active at end' snapshots
