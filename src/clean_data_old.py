"""Create cleaned interim tables and a subscription-by-month-end snapshot."""
import pandas as pd

from config import DATA_END, INTERIM, PROCESSED, TABLES
from load_data import load_all

BOOLEAN_COLUMNS = {
    "accounts": ["is_trial", "churn_flag"],
    "subscriptions": [
        "is_trial",
        "upgrade_flag",
        "downgrade_flag",
        "churn_flag",
        "auto_renew_flag",
    ],
    "feature_usage": ["is_beta_feature"],
    "support_tickets": ["escalation_flag"],
    "churn_events": [
        "preceding_upgrade_flag",
        "preceding_downgrade_flag",
        "is_reactivation",
    ],
}

INTEGER_COLUMNS = {
    "accounts": ["seats"],
    "subscriptions": ["seats"],
    "feature_usage": ["usage_count", "usage_duration_secs", "error_count"],
    "support_tickets": ["first_response_time_minutes"],
}

NUMERIC_COLUMNS = {
    "subscriptions": ["mrr_amount", "arr_amount"],
    "churn_events": ["refund_amount_usd"],
    "support_tickets": ["resolution_time_hours", "satisfaction_score"],
}


def _normalize_table(name: str, frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize whitespace and source types without dropping source rows."""
    cleaned = frame.copy()

    for column in cleaned.select_dtypes(include=["object", "string"]).columns:
        values = cleaned[column].astype("string").str.strip()
        cleaned[column] = values.mask(values.eq(""), pd.NA)

    for column in TABLES[name]["dates"]:
        parsed = pd.to_datetime(cleaned[column], errors="coerce")
        invalid = cleaned[column].notna() & parsed.isna()
        if invalid.any():
            raise ValueError(
                f"{name}.{column} has {int(invalid.sum())} invalid date value(s)"
            )
        cleaned[column] = parsed

    for column in BOOLEAN_COLUMNS[name]:
        values = cleaned[column].astype("string").str.strip().str.lower()
        mapped = values.map(
            {
                "true": True,
                "1": True,
                "yes": True,
                "false": False,
                "0": False,
                "no": False,
            }
        )
        invalid = values.notna() & mapped.isna()
        if invalid.any():
            unexpected = sorted(values[invalid].unique().tolist())
            raise ValueError(
                f"{name}.{column} has invalid boolean value(s): {unexpected}"
            )
        cleaned[column] = mapped.astype("boolean")

    for column in INTEGER_COLUMNS.get(name, []):
        cleaned[column] = pd.to_numeric(cleaned[column], errors="raise").astype(
            "Int64"
        )

    for column in NUMERIC_COLUMNS.get(name, []):
        cleaned[column] = pd.to_numeric(cleaned[column], errors="raise").astype(
            "Float64"
        )

    return cleaned


def _validate_tables(tables: dict[str, pd.DataFrame]) -> None:
    primary_keys = {
        "accounts": "account_id",
        "subscriptions": "subscription_id",
        "support_tickets": "ticket_id",
        "churn_events": "churn_event_id",
    }
    for name, key in primary_keys.items():
        if tables[name][key].isna().any() or tables[name][key].duplicated().any():
            raise ValueError(f"{name}.{key} must contain unique, non-null values")

    foreign_keys = [
        ("subscriptions", "account_id", "accounts", "account_id"),
        ("feature_usage", "subscription_id", "subscriptions", "subscription_id"),
        ("support_tickets", "account_id", "accounts", "account_id"),
        ("churn_events", "account_id", "accounts", "account_id"),
    ]
    for child, child_key, parent, parent_key in foreign_keys:
        orphans = ~tables[child][child_key].isin(tables[parent][parent_key])
        if orphans.any():
            raise ValueError(
                f"{child}.{child_key} has {int(orphans.sum())} orphan value(s)"
            )

    subscriptions = tables["subscriptions"]
    invalid_intervals = (
        subscriptions["end_date"].notna()
        & (subscriptions["end_date"] < subscriptions["start_date"])
    )
    if invalid_intervals.any():
        raise ValueError(
            f"subscriptions has {int(invalid_intervals.sum())} end date(s) "
            "before the start date"
        )


def build_monthly_snapshot(subscriptions: pd.DataFrame) -> pd.DataFrame:
    """Build a complete subscription/month-end panel with active status flags."""
    first_month = subscriptions["start_date"].min().to_period("M")
    last_month = pd.Timestamp(DATA_END).to_period("M")
    if first_month > last_month:
        raise ValueError("DATA_END is earlier than the first subscription start date")

    periods = pd.period_range(first_month, last_month, freq="M")
    month_ends = pd.DataFrame(
        {"month_end": periods.to_timestamp(how="end").normalize()}
    )
    panel = subscriptions.merge(month_ends, how="cross")
    previous_month_end = panel["month_end"] - pd.offsets.MonthEnd(1)

    panel["is_active"] = (
        panel["start_date"].le(panel["month_end"])
        & (
            panel["end_date"].isna()
            | panel["end_date"].gt(panel["month_end"])
        )
    )
    panel["is_active_paid"] = panel["is_active"] & ~panel["is_trial"].fillna(False)
    panel["is_new_subscription"] = (
        panel["start_date"].gt(previous_month_end)
        & panel["start_date"].le(panel["month_end"])
    )
    panel["is_churned_subscription"] = (
        panel["end_date"].notna()
        & panel["end_date"].gt(previous_month_end)
        & panel["end_date"].le(panel["month_end"])
    )
    panel["mrr_snapshot"] = panel["mrr_amount"].where(
        panel["is_active_paid"], 0
    )
    panel["arr_snapshot"] = panel["arr_amount"].where(
        panel["is_active_paid"], 0
    )

    columns = [
        "subscription_id",
        "month_end",
        "account_id",
        "plan_tier",
        "seats",
        "billing_frequency",
        "start_date",
        "end_date",
        "is_trial",
        "is_active",
        "is_active_paid",
        "is_new_subscription",
        "is_churned_subscription",
        "mrr_snapshot",
        "arr_snapshot",
    ]
    snapshot = panel[columns].sort_values(
        ["month_end", "subscription_id"], kind="stable"
    )
    if snapshot.duplicated(["subscription_id", "month_end"]).any():
        raise ValueError("Monthly snapshot contains duplicate subscription/month rows")
    return snapshot


def main() -> None:
    INTERIM.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    raw_tables = load_all()
    cleaned_tables = {
        name: _normalize_table(name, frame)
        for name, frame in raw_tables.items()
    }
    _validate_tables(cleaned_tables)

    for name, frame in cleaned_tables.items():
        path = INTERIM / f"{name}_clean.csv"
        frame.to_csv(path, index=False, na_rep="")
        print(f"Wrote {path.relative_to(INTERIM.parent.parent)} rows={len(frame)}")

    snapshot = build_monthly_snapshot(cleaned_tables["subscriptions"])
    snapshot_path = PROCESSED / "monthly_subscription_snapshot.csv"
    snapshot.to_csv(snapshot_path, index=False, na_rep="")
    print(
        f"Wrote {snapshot_path.relative_to(PROCESSED.parent.parent)} "
        f"rows={len(snapshot)} months={snapshot['month_end'].nunique()}"
    )


if __name__ == "__main__":
    main()
