# Source-Data Inventory

 Generated from the raw files in `data/raw/` .

## Dataset provenance

- **Name:** RavenStack: Synthetic SaaS Dataset (Multi-Table)
- **Author:** River @ Rivalytics (credit required)
- **Licence:** MIT-like; fully synthetic, no personal data
- **Format:** 5 CSV files, one per table
- **Coverage:** January 2023 to December 2024 (24 months)
- **Nature:** synthetic, generated with Python (pandas, numpy, uuid). Patterns such as churn rates and usage are simulated, so findings describe this dataset, not a real company.

## Tables at a glance

| Table | File | Rows | Columns | Grain (one row = ...) | Primary key | Foreign keys | Date range |
|---|---|---:|---:|---|---|---|---|
| accounts | `ravenstack_accounts.csv` | 500 | 10 | One row per customer account (company) | account_id | — | 2023-01-02 to 2024-12-31 |
| subscriptions | `ravenstack_subscriptions.csv` | 5,000 | 14 | One row per billable subscription period; an account can hold several at once | subscription_id | account_id → accounts | 2023-01-09 to 2024-12-31 |
| feature_usage | `ravenstack_feature_usage.csv` | 25,000 | 8 | One row per usage record of a feature on a day | usage_id (NOT unique: 21 collisions) | subscription_id → subscriptions | 2023-01-01 to 2024-12-31 |
| support_tickets | `ravenstack_support_tickets.csv` | 2,000 | 9 | One row per support ticket | ticket_id | account_id → accounts | 2023-01-02 to 2024-12-31 |
| churn_events | `ravenstack_churn_events.csv` | 600 | 9 | One row per churn event; an account can have several | churn_event_id | account_id → accounts | 2023-01-25 to 2024-12-31 |

## Purpose of each table

- **accounts:** Customer attributes: industry, country, signup date, referral source, initial plan
- **subscriptions:** Revenue source: plan, seats, MRR/ARR, billing frequency, upgrade/downgrade flags, end date
- **feature_usage:** Product engagement: feature, usage count, duration, errors, beta flag
- **support_tickets:** Support load and quality: priority, response and resolution time, satisfaction, escalation
- **churn_events:** Churn timing and reasons, refunds, reactivation flag, feedback

## Relationships

```
accounts (account_id)
 ├── subscriptions (account_id)
 │     └── feature_usage (subscription_id)
 ├── support_tickets (account_id)
 └── churn_events (account_id)
```

All foreign keys resolve: there are no orphan rows in any child table (checked in `reports/data_quality_audit.csv`).

## Missing values (columns with nulls)

| Table | Column | Nulls | Share of rows | Meaning |
|---|---|---:|---:|---|
| subscriptions | end_date | 4,514 | 90.3% | Subscription still active (no end date) |
| support_tickets | satisfaction_score | 825 | 41.2% | Customer gave no score |
| churn_events | feedback_text | 148 | 24.7% | No feedback given |

## Key categorical fields

- **plan_tier (subscriptions):** Enterprise (1,723), Pro (1,675), Basic (1,602)
- **billing_frequency:** monthly (51%), annual (49%)
- **referral_source (accounts):** organic (114), other (103), ads (98), event (96), partner (89)
- **industry (accounts):** 5 values; **country:** 7 values
- **reason_code (churn_events):** features (114), support (104), budget (104), unknown (95), competitor (92), pricing (91)
- **priority (support_tickets):** urgent (514), high (510), medium (491), low (485)
- **feature_name (feature_usage):** 40 distinct features

## Fields in the project brief that this dataset does NOT contain

| Brief mentions | Available? | How we handle it |
|---|---|---|
| Acquisition cost, marketing spend | No | CAC is not calculated. LTV only as a clearly labelled revenue-based estimate |
| Discounts, taxes | No | One price per seat per plan; MRR = `mrr_amount` as given |
| Currency | No (single currency, USD assumed) | No conversion needed; stated as an assumption |
| Payment events | No | Not analysed |
| Refunds | Only `refund_amount_usd` in churn_events | Reported as a churn-side metric; not subtracted from MRR |
| Upgrade/downgrade amounts | No, only boolean flags | Expansion and contraction MRR are derived from changes in account-level MRR |
| Subscription status field | No | Derived from `end_date` (null = active) |

## Known data characteristics to keep in mind

(Details and counts: `reports/data_quality_audit.csv`.)

- Accounts hold about 10 subscriptions each, and most overlap in time, so MRR must be summed across active subscriptions without collapsing rows.
- About 90% of subscriptions never end, so month-end MRR rises almost every month.
- Three churn sources disagree: `accounts.churn_flag`, `churn_events`, and subscription `end_date`.
- `mrr_amount` is already monthly, even for annual billing (`arr_amount` = 12 × `mrr_amount` in every row).
- 21 `usage_id` values appear twice with different content.
- Many usage rows are dated before their subscription start date.
- Trial subscriptions carry MRR of 0.

