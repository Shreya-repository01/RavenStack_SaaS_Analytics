# Metric Definitions (DRAFT — team must confirm in Week 1, then freeze)

Status legend: PROPOSED = mentor suggestion, needs team decision.

| Decision | Proposed rule | Why |
|---|---|---|
| Subscription grain | Each row in `subscriptions` is one billable subscription; accounts can hold several at once | 87% of rows overlap another sub of the same account; collapsing them would invent data |
| Active at date D | `start_date <= D AND (end_date IS NULL OR end_date > D)` | Handles open-ended subs |
| MRR | Sum of `mrr_amount` for active, non-trial subscriptions at month-end | `mrr_amount` is already monthly (ARR = 12 x MRR for all rows); do NOT divide annual plans again |
| Trials | Excluded from MRR; used for trial-to-paid conversion | All 778 trial rows have MRR = 0 |
| New subscriptions | `is_new_subscription` includes trials; use `is_new_paid_subscription` (or filter `NOT is_trial`) for paid-only counts | Both flags use the same month boundary; the paid-only flag is false for trials |
| New MRR | MRR of non-trial subscriptions whose `start_date` falls in the month | |
| Churned MRR | MRR of subscriptions whose `end_date` falls in the month | |
| Conflicting movement flags | Keep both source flags for subscriptions where `upgrade_flag` and `downgrade_flag` are true; do not choose precedence or infer net movement | Treat as ambiguous; exclude from exclusive upgrade/downgrade counts or report separately |
| Expansion / Contraction | PROPOSED: month-over-month change in an account's total active MRR attributable to continuing subscriptions (seat/plan change) — validate on 3–5 hand-checked accounts | No before/after amounts in data; flags only |
| Subscription churn rate | Subs ended in month / active subs at start of month | Uses `end_date` |
| Customer (account) churn | PROPOSED: account with a `churn_events` row in the period / accounts active at period start; reactivations (`is_reactivation = True`) reported separately | Account `churn_flag` (110) and churn_events (352 accounts) disagree; document both |
| Revenue churn rate | Churned MRR / starting MRR (state whether contraction is included) | |
| Cohort | Account `signup_date` month; retained = account still has >= 1 active paid subscription OR no churn event (pick one, document) | |
| CAC / LTV | CAC: NOT SUPPORTED (no spend). LTV: revenue-based estimate only, labelled as such | Brief: include only if data supports |

## Snapshot location

Run `python src/clean_data.py` from the repository root to generate the snapshot at
`data/processed/monthly_subscription_snapshot.csv`. Most of `data/processed/` is
ignored by Git; this snapshot is explicitly tracked in the repository. If it is
missing locally, regenerate it with the command above.

## Cleaning decisions log

Counts below are from the source-data audit; affected counts refer to source rows
unless otherwise noted. No source rows are dropped for these findings.

| Date | Table | Issue | Decision | Rows affected | Owner |
|---|---|---|---|---:|---|
| 2026-11-14 | subscriptions | 778 trial subscriptions; trial starts were included in `is_new_subscription` | Preserve trials and the inclusive flag; add `is_new_paid_subscription` for paid-only counts. Trials remain excluded from MRR/ARR. | 778 subscriptions | |
| 2026-11-14 | subscriptions | Both `upgrade_flag` and `downgrade_flag` are true | Preserve both flags; apply no precedence, infer no net movement, and treat as ambiguous for exclusive movement analysis. | 23 subscriptions | |
| 2026-11-14 | feature_usage | 21 repeated `usage_id` values identify distinct records | Preserve all rows; do not deduplicate on `usage_id` (the SQL table uses `row_id` as its key). | 21 duplicate-ID rows | |
| 2026-11-14 | subscriptions | Rows overlap another subscription for the same account | Keep subscription rows as the revenue grain; do not collapse overlapping subscriptions. | 4,370 subscriptions | |
| 2026-11-14 | feature_usage | Usage precedes the linked subscription start | Preserve source dates and flag as a source-quality limitation; do not discard usage records. | 19,142 rows | |
| 2026-11-14 | accounts / churn_events | Churn signals disagree: 35 flagged accounts have no event; 277 event accounts are not flagged; 110 flagged accounts still have an active subscription | Preserve each source signal; do not reconcile or treat them as equivalent. | 35 + 277 + 110 account observations | |
