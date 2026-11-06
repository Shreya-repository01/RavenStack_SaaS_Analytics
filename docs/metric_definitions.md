# Metric Definitions (DRAFT — team must confirm in Week 1, then freeze)

Status legend: PROPOSED = mentor suggestion, needs team decision.

| Decision | Proposed rule | Why |
|---|---|---|
| Subscription grain | Each row in `subscriptions` is one billable subscription; accounts can hold several at once | 87% of rows overlap another sub of the same account; collapsing them would invent data |
| Active at date D | `start_date <= D AND (end_date IS NULL OR end_date > D)` | Handles open-ended subs |
| MRR | Sum of `mrr_amount` for active, non-trial subscriptions at month-end | `mrr_amount` is already monthly (ARR = 12 x MRR for all rows); do NOT divide annual plans again |
| Trials | Excluded from MRR; used for trial-to-paid conversion | All 778 trial rows have MRR = 0 |
| New MRR | MRR of subscriptions whose `start_date` falls in the month (non-trial) | |
| Churned MRR | MRR of subscriptions whose `end_date` falls in the month | |
| Expansion / Contraction | PROPOSED: month-over-month change in an account's total active MRR attributable to continuing subscriptions (seat/plan change) — validate on 3–5 hand-checked accounts | No before/after amounts in data; flags only |
| Subscription churn rate | Subs ended in month / active subs at start of month | Uses `end_date` |
| Customer (account) churn | PROPOSED: account with a `churn_events` row in the period / accounts active at period start; reactivations (`is_reactivation = True`) reported separately | Account `churn_flag` (110) and churn_events (352 accounts) disagree; document both |
| Revenue churn rate | Churned MRR / starting MRR (state whether contraction is included) | |
| Cohort | Account `signup_date` month; retained = account still has >= 1 active paid subscription OR no churn event (pick one, document) | |
| CAC / LTV | CAC: NOT SUPPORTED (no spend). LTV: revenue-based estimate only, labelled as such | Brief: include only if data supports |

## Cleaning decisions log (append as you go)
| Date | Table | Issue | Decision | Rows affected | Owner |
|2026-11-06| monthly_subscription_snapshot| Duplicate subscription-month records| Checked using subscription_id + month_end; no duplicates found. No rows removed.| 0| BI Developer
2026-11-06| monthly_subscription_snapshot| Snapshot validation| Validated 5,000 subscriptions across 24 months; snapshot contains 120,000 rows.| 120,000 validated| BI Developer
2026-11-06| monthly_subscription_snapshot| June 2024 MRR validation| Confirmed June 2024 MRR of 3,833,405 matches raw data.| 0 mismatch| BI Developer
2026-11-06| monthly_subscription_snapshot| New subscription KPI includes trials| Created a paid-only New Paid Subscriptions measure using is_trial = FALSE.| Not yet recorded| BI Developer|

### Upgrade and downgrade flag conflict
23 subscriptions have both upgrade and downgrade flags. These records are not automatically classified as upgrades or downgrades. The final treatment is pending confirmation from the KPI Analyst. No assumptions have been applied in the dashboard.
### Snapshot file location
The generated monthly snapshot is stored at "data/processed/monthly_subscription_snapshot.csv". The "data/processed/" folder is excluded from Git tracking, so the snapshot may not appear in the repository. Regenerate it by running:
```bash 
python src/clean_data.py
```
