# SaaS Revenue & Subscription Analytics (RavenStack)

Team project: MRR, subscription movements, churn and retention analysis, with a Power BI dashboard and report.

## Data source and credit
Project 2 uses the RavenStack synthetic SaaS dataset by **River @ Rivalytics**
(fully synthetic, no PII, MIT-like licence, credit required). 5 tables: accounts (500),
subscriptions (5,000), feature_usage (25,000), support_tickets (2,000), churn_events (600).
Date range: 2023-01 to 2024-12. The source dataset and author are credited; no Project 3
sales datasets are included in this SaaS repository.
Original files in `data/raw/` are **never edited**.

## Repository structure
```
data/raw/        original CSVs (read-only)
data/interim/    cleaned intermediate tables (generated)
data/processed/  final analytical/KPI tables for Power BI (generated)
notebooks/       numbered notebooks: 01_ingestion_audit, 02_mrr_churn, 03_cohorts, ...
src/             reusable scripts (config, loaders, audit, KPI functions)
sql/             PostgreSQL schema + KPI queries
reports/figures/ charts exported for the report
docs/            metric definitions, data dictionary, data-quality decisions, team plan
```

## Setup
```bash
git clone <repo-url> && cd ravenstack-saas-analytics
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/load_data.py        # sanity check: row counts
python src/audit.py            # writes reports/data_quality_audit.csv
python src/clean_data.py       # writes cleaned interim CSVs and monthly snapshot
```
PostgreSQL (optional but recommended): after generating the CSVs, run these from the
repository root:
```bash
psql -v ON_ERROR_STOP=1 -d <db> -f sql/01_schema.sql
psql -v ON_ERROR_STOP=1 -d <db> -f sql/02_load_data.sql
```
The load script replaces the contents of the project tables. See
[`docs/data_dictionary.md`](docs/data_dictionary.md) and
[`docs/data_model.md`](docs/data_model.md) for field definitions, table grains, and
snapshot semantics.

## Metric definitions
See `docs/metric_definitions.md` (single source of truth: every number in the dashboard and report must follow it).

## Known limitations
- No acquisition spend/marketing cost -> **CAC is not calculable**; LTV only as a labelled revenue-based estimate.
- No discounts, taxes, currency or payment events (single USD price per seat).
- Expansion/contraction MRR must be derived (only boolean flags exist).
- Synthetic data: ~90% of subscriptions never end, accounts have ~10 overlapping subscriptions, and three churn
  sources disagree (see `reports/data_quality_audit.csv`).
