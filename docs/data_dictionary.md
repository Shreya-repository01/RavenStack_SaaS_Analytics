# Data Dictionary

## Source and conventions

This project uses the fully synthetic RavenStack SaaS dataset by River @ Rivalytics.
Credit the author when reusing the dataset. Original CSVs are stored unchanged in
`data/raw/`; `src/clean_data.py` writes normalized copies to `data/interim/` and the
monthly analytical panel to `data/processed/`.

Empty source values remain null. Cleaning trims surrounding whitespace, parses dates,
normalizes boolean spellings, and converts numeric fields without removing rows.
`feature_usage.usage_id` is not unique (21 source collisions); keep every event row,
and use the SQL surrogate `row_id` as its primary key.

## Source and cleaned tables

| Table | Grain / key | Fields |
|---|---|---|
| `accounts` | One account; `account_id` | `account_id` (text, PK); `account_name` (text); `industry` (text); `country` (text); `signup_date` (date); `referral_source` (text); `plan_tier` (text, initial account plan); `seats` (integer); `is_trial` (boolean); `churn_flag` (boolean, source account-level flag). |
| `subscriptions` | One subscription; `subscription_id` | `subscription_id` (text, PK); `account_id` (text, FK to accounts); `start_date` (date); `end_date` (nullable date); `plan_tier` (text); `seats` (integer); `mrr_amount` and `arr_amount` (numeric USD); `is_trial`, `upgrade_flag`, `downgrade_flag`, `churn_flag`, `auto_renew_flag` (boolean); `billing_frequency` (text). Source MRR is already monthly, including annual billing; ARR is 12 × MRR. |
| `feature_usage` | One usage-event row; `usage_id` is a non-unique source identifier | `usage_id` (text, not a key); `subscription_id` (text, FK); `usage_date` (date); `feature_name` (text); `usage_count`, `usage_duration_secs`, `error_count` (integer); `is_beta_feature` (boolean). SQL assigns a surrogate `row_id` primary key. |
| `support_tickets` | One support ticket; `ticket_id` | `ticket_id` (text, PK); `account_id` (text, FK); `submitted_at`, `closed_at` (nullable timestamps); `resolution_time_hours` (numeric); `priority` (text); `first_response_time_minutes` (nullable integer); `satisfaction_score` (nullable numeric, source scale 1–5); `escalation_flag` (boolean). |
| `churn_events` | One churn-event row; `churn_event_id` | `churn_event_id` (text, PK); `account_id` (text, FK); `churn_date` (date); `reason_code` (text); `refund_amount_usd` (numeric); `preceding_upgrade_flag`, `preceding_downgrade_flag`, `is_reactivation` (boolean); `feedback_text` (nullable text). |

Cleaned CSV file names are `<table>_clean.csv` under `data/interim/`. Their fields
retain the source names and row grain.

## Processed table: `monthly_subscription_snapshot`

Output: `data/processed/monthly_subscription_snapshot.csv`; SQL table:
`raven.monthly_subscription_snapshot`.

**Grain:** exactly one row per source subscription per calendar month-end, from the
month of the earliest subscription start through `DATA_END` (2024-12-31). The panel
includes inactive subscriptions too; this avoids confusing “not active” with a missing
subscription-month.

| Field | Type | Definition |
|---|---|---|
| `subscription_id` | text | Subscription identifier; part of the composite key. |
| `month_end` | date | Calendar month-end snapshot date; part of the composite key. |
| `account_id` | text | Owning account. |
| `plan_tier` | text | Subscription plan for the source record. |
| `seats` | integer | Source licensed seat count. |
| `billing_frequency` | text | Source billing interval. |
| `start_date`, `end_date` | date | Source subscription interval; `end_date` may be null. |
| `is_trial` | boolean | Source trial indicator. |
| `is_active` | boolean | True when `start_date <= month_end` and (`end_date` is null or `end_date > month_end`). |
| `is_active_paid` | boolean | `is_active` and not a trial. |
| `is_new_subscription` | boolean | Start date falls after the preceding month-end and on/before this month-end. |
| `is_churned_subscription` | boolean | Non-null end date falls after the preceding month-end and on/before this month-end. |
| `mrr_snapshot` | numeric USD | Source MRR for active, paid subscriptions; zero otherwise. Never divide annual plans by 12 again. |
| `arr_snapshot` | numeric USD | Source ARR for active, paid subscriptions; zero otherwise. |

Example monthly MRR query:

```sql
SELECT month_end,
       COUNT(*) FILTER (WHERE is_active_paid) AS active_paid_subs,
       SUM(mrr_snapshot) AS mrr
FROM raven.monthly_subscription_snapshot
GROUP BY month_end
ORDER BY month_end;
```

The snapshot reflects source subscription rows as provided. It does not infer
mid-period price changes from upgrade/downgrade flags, resolve overlapping
subscriptions, or reconcile conflicting account and churn-event flags. Those are
documented source limitations, not cleaning rules.
