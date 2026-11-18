# Metric Definitions and Business Rules

**Project:** RavenStack SaaS Revenue & Subscription Analytics   
**Data period:** January 2023 – December 2024  
**Snapshot end date:** 31 December 2024

## 1. Purpose

This document defines the business rules and KPI calculation methods used in the RavenStack SaaS analytics project. These definitions provide a consistent basis for revenue, subscription, churn, and retention analysis in SQL and Power BI.

## 2. Subscription and Revenue Metrics

| Metric / Decision | Final definition | Business interpretation |
|---|---|---|
| Subscription grain | Each row in `subscriptions` represents one subscription. An account may have multiple subscriptions. | Subscription records are retained individually. Overlapping subscriptions are not automatically combined or removed. |
| Active subscription | A subscription is active on date D when `start_date <= D` and (`end_date` is null or `end_date > D`). | A subscription ending on date D is not considered active at the end of that date. |
| Active paid subscription | An active subscription where `is_trial = FALSE`. | Trial subscriptions are excluded from paid subscription counts. |
| MRR | Sum of `mrr_amount` for active, non-trial subscriptions at month-end. | Source MRR is already monthly. Annual plan amounts are not divided again. |
| ARR | MRR multiplied by 12. | Annualized recurring revenue based on monthly recurring revenue. |
| Trial subscriptions | Subscriptions with `is_trial = TRUE`. | Excluded from MRR and ARR; considered separately in trial analysis. |
| New paid subscriptions | Non-trial subscriptions whose `start_date` falls within the reporting month. | Measures new paid subscription starts. |
| New MRR | Sum of `mrr_amount` for non-trial subscriptions whose `start_date` falls within the reporting month. | Measures recurring revenue associated with new paid subscriptions. |
|Opening MRR | MRR at the last day of the previous month|
| Churned subscriptions | Subscriptions whose `end_date` falls within the reporting month. | Measures subscription endings recorded in the source data. |
| Churned MRR | Sum of `mrr_amount` for subscriptions whose `end_date` falls within the reporting month. | Uses the recorded subscription MRR; historical price changes are not reconstructed. |
| Subscription churn rate | Number of subscriptions ending during the month divided by the number of active subscriptions at the beginning of the month, multiplied by 100. | Measures subscription-level churn, not account-level churn. |
| Expansion MRR | Not calculated as a definitive monetary KPI. | Upgrade and downgrade flags do not provide reliable before-and-after revenue amounts. |
| Contraction MRR | Not calculated as a definitive monetary KPI. | The available fields do not establish the exact recurring revenue reduction. |
| Bridge | Opening MRR + New MRR − Churned MRR = Closing MRR. Checked: difference 0 in all 24 months|

## 3. Customer Churn and Retention Metrics

| Metric / Decision | Final definition | Business interpretation |
|---|---|---|
|Eligible accounts (opening customers) | Distinct accounts whose signup_date is before the first day of the reporting month. | Denominator for monthly customer churn (June 2024: 327; December 2024: 483). Accounts that sign up during the month are not in the denominator, so they are also excluded from the numerator.. |
| Monthly customer churn | Distinct eligible accounts with at least one non-reactivation churn event during the reporting month. | Each account is counted only once per month, even if it has multiple churn-event records. |
| Monthly customer churn rate | Distinct eligible accounts with at least one non-reactivation churn event during the month divided by eligible accounts at the beginning of the month, multiplied by 100. | Measures account-level churn rather than the number of churn-event records. |
| Reactivations | Events with `is_reactivation = TRUE` are reported separately from regular customer churn. | Reactivations are not added to the regular churn numerator. |
| Account churn flag | The source `accounts.churn_flag` is treated as a separate source indicator. | It is not substituted for the churn-events calculation because the two sources do not fully agree. |
| Retention cohort | Accounts are grouped by the month of their `signup_date`. | Provides a consistent account acquisition cohort. |
Cohort size = accounts that signed up in the cohort month 
Cohort retention % = retained accounts ÷ cohort size × 100.
| Retained account | An account in a signup cohort is retained at month N when it has no non-reactivation churn event on or before the end of the Nth month after its signup month (month 0 = signup month). | A subscription-activity rule was tested and rejected: it showed retention rising from about 40% to 99%, because accounts start paying weeks after signup and every account keeps an active subscription. |
| Revenue churn rate | Churned MRR divided by starting MRR, multiplied by 100. | Measures recurring revenue lost through subscriptions ending during the period. Contraction is excluded because it is not reliably measurable. |

**Customer churn counting rule:** Use distinct eligible accounts, not raw event-record counts. An account is counted once in the monthly churn numerator. Reactivation events are reported separately. Accounts with both event types in the same month must be checked to avoid double-counting.

## 4. Metrics Not Fully Supported by the Dataset

| Metric | Decision | Reason |
|---|---|---|
| Expansion MRR | Excluded as a definitive monetary KPI. | Upgrade and downgrade flags do not provide reliable before-and-after MRR values. |
| Contraction MRR | Excluded as a definitive monetary KPI. | The available fields do not establish the exact revenue reduction. |
| Customer Acquisition Cost (CAC) | Not calculated. | Marketing and sales acquisition expenditure is not available. |
| Lifetime Value (LTV) | Shown only as an illustrative revenue-based estimate: ARPA ÷ average monthly customer churn over the last 12 months. It uses revenue only (no margin or cost), is labelled ‘illustrative’ on the dashboard, and is not a profitability KPI. |
| Historical price-change analysis | Not calculated. | Historical subscription price changes cannot be reconstructed reliably from the available fields. |

## 5. Data Quality and Business Rule Limitations

The following source-data conditions were identified during validation. They are documented as analytical limitations and are not automatically corrected by the cleaning process.

| Finding | Treatment in the project |
|---|---|
| Multiple subscriptions belonging to the same account, including overlapping periods | Subscription records are retained separately. Account-level MRR is calculated by aggregating qualifying active subscriptions. |
| Feature usage records dated before subscription start dates | Records are retained and flagged as a source-data limitation. |
| Conflicting account churn flags and churn events | Both sources are treated separately; churn-event-based account churn is used for the defined KPI. |
| Records containing both upgrade and downgrade flags | No automatic classification is applied. Expansion and contraction MRR are not treated as definitive. |
| Differences between initial account plan tiers and subscription plan tiers | Source values are retained; no automatic reconciliation is performed. |
| Missing subscription end dates | Preserved as null and treated as open-ended for active-subscription calculations. |
| Missing satisfaction scores and feedback text | Preserved as null; not replaced with zero or removed. |
| Duplicate `feature_usage.usage_id` values | All event rows are retained. SQL uses a surrogate `row_id` as the primary key. |

## 6. Cleaning and Validation Decisions Log

| Date | Table | Validation / Issue | Decision | Result | Owner |
|---|---|---|---|---|---|
| 16-Nov-2026 | All five source tables | Row-count validation | All source rows retained during cleaning. | 33,100 rows validated; 0 removed. | Data Cleaning |
| 16-Nov-2026 | subscriptions | Missing `end_date` values | Null values preserved; treated as open-ended where applicable. | 4,514 null values. | Data Cleaning |
| 16-Nov-2026 | support_tickets | Missing `satisfaction_score` values | Null values preserved; no automatic replacement. | 825 null values. | Data Cleaning |
| 16-Nov-2026 | churn_events | Missing `feedback_text` values | Null values preserved; no automatic replacement. | 148 null values. | Data Cleaning |
| 16-Nov-2026 | feature_usage | Duplicate usage identifiers | All records retained; collisions documented. | 21 ID collisions. | Auditor |
| 16-Nov-2026 | monthly_subscription_snapshot | Snapshot row and grain validation | Subscription-month uniqueness and required identifiers checked. | 120,000 rows across 24 months; no duplicate subscription-month pairs. | BI Developer |
| 16-Nov-2026 | data/raw | Raw source integrity | Original tracked source files were not modified during local validation. | No differences detected. | Auditor |


## 7. Final Reporting Principles

1. Revenue KPIs use subscription-level data and the defined month-end active-subscription rule.
2. Trial subscriptions are excluded from paid MRR and ARR.
3. Missing source values are preserved unless a documented business rule requires otherwise.
4. Source records are not silently deleted to resolve data-quality findings.
5. Subscription-level churn and account-level churn are reported as separate measures.
6. Customer churn counts distinct eligible accounts, not raw event records.
7. Reactivations are reported separately from regular customer churn.
8. Unsupported metrics are excluded or clearly labelled rather than estimated without sufficient evidence.
9. Data-quality limitations are disclosed when interpreting dashboard results.

## 8. Conclusion and Key Analytical Findings

The RavenStack SaaS Revenue & Subscription Analytics project analysed five synthetic datasets containing **33,100 source records** across accounts, subscriptions, feature usage, support tickets, and churn events, covering January 2023 to December 2024.

The data preparation and validation process retained all original records while standardising data types, handling date and Boolean fields, and preserving missing values. All five cleaned tables maintained their original row counts, with no records removed. The monthly subscription snapshot contained **120,000 subscription-month records across 24 months**, with no duplicate subscription-month combinations or missing subscription identifiers and month dates.

The analysis established several important findings:

1. **Subscription and revenue measurement:** Subscription-level analysis is essential because accounts can have multiple subscriptions, including overlapping subscription periods. MRR is calculated using active, non-trial subscriptions, while ARR is derived as 12 times MRR. The source data also showed that all 778 trial subscriptions had zero MRR, supporting their exclusion from paid recurring revenue calculations.

2. **Data quality and customer activity:** The dataset contains 4,514 missing subscription end dates, 825 missing support-ticket satisfaction scores, and 148 missing churn-event feedback values. These values were preserved rather than automatically replaced or removed. In addition, 21 duplicate `feature_usage.usage_id` values were identified and retained as separate event records, with a surrogate SQL `row_id` used as the primary key.

3. **Customer churn and retention:** Account-level churn indicators and churn-event records do not fully agree. The source account churn flag identifies 110 accounts, whereas churn events involve 352 distinct accounts. This difference highlights why customer churn must be calculated using a clearly defined eligibility rule and distinct account counts rather than raw event counts. Reactivations are reported separately to avoid overstating customer churn.

4. **Feature usage and subscription consistency:** The validation identified 19,142 feature-usage records dated before their associated subscription start dates. These records were retained and documented as a source-data limitation rather than silently deleted. This finding is important when interpreting product adoption and engagement patterns.

5. **Revenue movement limitations:** Although the dataset contains upgrade and downgrade indicators, 23 subscriptions have both flags set to true. Since reliable before-and-after revenue amounts are not available, expansion MRR and contraction MRR cannot be treated as definitive monetary measures. Similarly, CAC cannot be calculated because acquisition expenditure is not provided, and profitability-based LTV is outside the scope of the available data.

Overall, the project establishes a consistent analytical framework for monitoring recurring revenue, subscription activity, customer churn, and retention. It demonstrates the importance of validating data at the correct analytical grain, distinguishing subscription-level metrics from account-level metrics, and documenting source-data limitations before drawing business conclusions.

The resulting cleaned datasets, monthly subscription snapshot, documented KPI definitions, SQL analysis, and Power BI reporting provide a structured foundation for SaaS performance monitoring and business decision-making. The findings should be interpreted within the limitations of the synthetic dataset and the business rules defined in this project.
