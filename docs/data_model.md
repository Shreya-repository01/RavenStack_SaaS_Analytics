# Data Model

## Relational model

```text
accounts (1) ────────< subscriptions (1) ────────< feature_usage
    │
    ├────────────────< support_tickets
    └────────────────< churn_events

subscriptions (1) ───< monthly_subscription_snapshot >─── (1) accounts
```

| Relation | Key / cardinality | Notes |
|---|---|---|
| `accounts` → `subscriptions` | `accounts.account_id` → `subscriptions.account_id`, one-to-many | An account may have multiple concurrent or sequential subscription rows. Do not collapse these into one subscription. |
| `subscriptions` → `feature_usage` | `subscriptions.subscription_id` → `feature_usage.subscription_id`, one-to-many | `usage_id` has 21 collisions; SQL uses `row_id` as the usage table key. |
| `accounts` → `support_tickets` | `accounts.account_id` → `support_tickets.account_id`, one-to-many | Ticket timestamps and feedback can be null. |
| `accounts` → `churn_events` | `accounts.account_id` → `churn_events.account_id`, one-to-many | Reactivations can produce multiple events for one account. |
| `subscriptions` → `monthly_subscription_snapshot` | `subscription_id` plus `month_end`, one-to-many | Composite primary key; one row per subscription and month-end, including inactive periods. `account_id` is repeated for convenient analysis. |

The PostgreSQL schema is defined in `sql/01_schema.sql`. It uses foreign keys for
the relationships above and a composite key on the snapshot. `sql/02_load_data.sql`
loads the cleaned CSVs and processed snapshot after `python src/clean_data.py`;
the transactional load replaces the project table contents on each run.

## Snapshot rules

- Reporting months start with the month containing the earliest source
  `subscriptions.start_date` and end with `DATA_END` from `src/config.py`.
- A subscription is active at month-end when it has started by that date and has
  no end date on or before that date.
- Trials are retained in the panel but do not contribute to paid MRR or ARR.
- Inactive and trial rows have `mrr_snapshot = 0` and `arr_snapshot = 0`.
- `is_new_subscription` and `is_churned_subscription` indicate dates within the
  month, using the preceding month-end as the lower exclusive boundary.
- Source `mrr_amount` is already monthly. The `billing_frequency` field does not
  change the calculation.

## Known source limitations

Account and subscription records overlap by design; subscription rows remain the
revenue grain. The source has conflicting churn signals, 23 subscriptions with both
upgrade and downgrade flags, and feature-use records preceding subscription starts.
The model preserves these observations and does not fabricate reconciliation logic.
