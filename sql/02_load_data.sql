-- Run from the repository root after `python src/clean_data.py`:
--   psql -d <database> -f sql/01_schema.sql
--   psql -d <database> -f sql/02_load_data.sql
-- This replaces the contents of the project tables on each load.

BEGIN;

TRUNCATE TABLE
  raven.monthly_subscription_snapshot,
  raven.feature_usage,
  raven.support_tickets,
  raven.churn_events,
  raven.subscriptions,
  raven.accounts
RESTART IDENTITY;

\copy raven.accounts FROM 'data/interim/accounts_clean.csv' WITH (FORMAT csv, HEADER true, NULL '')
\copy raven.subscriptions FROM 'data/interim/subscriptions_clean.csv' WITH (FORMAT csv, HEADER true, NULL '')
\copy raven.feature_usage (usage_id,subscription_id,usage_date,feature_name,usage_count,usage_duration_secs,error_count,is_beta_feature) FROM 'data/interim/feature_usage_clean.csv' WITH (FORMAT csv, HEADER true, NULL '')
\copy raven.support_tickets FROM 'data/interim/support_tickets_clean.csv' WITH (FORMAT csv, HEADER true, NULL '')
\copy raven.churn_events FROM 'data/interim/churn_events_clean.csv' WITH (FORMAT csv, HEADER true, NULL '')
\copy raven.monthly_subscription_snapshot FROM 'data/processed/monthly_subscription_snapshot.csv' WITH (FORMAT csv, HEADER true, NULL '')

COMMIT;
