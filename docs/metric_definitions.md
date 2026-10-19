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
|---|---|---|---|---|---|
| | | | | | |
