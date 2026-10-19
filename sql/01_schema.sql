-- PostgreSQL schema for RavenStack. Run in psql:  \i sql/01_schema.sql
CREATE SCHEMA IF NOT EXISTS raven;

CREATE TABLE IF NOT EXISTS raven.accounts (
  account_id TEXT PRIMARY KEY, account_name TEXT, industry TEXT, country TEXT,
  signup_date DATE, referral_source TEXT, plan_tier TEXT, seats INT,
  is_trial BOOLEAN, churn_flag BOOLEAN);

CREATE TABLE IF NOT EXISTS raven.subscriptions (
  subscription_id TEXT PRIMARY KEY, account_id TEXT REFERENCES raven.accounts(account_id),
  start_date DATE, end_date DATE, plan_tier TEXT, seats INT, mrr_amount NUMERIC, arr_amount NUMERIC,
  is_trial BOOLEAN, upgrade_flag BOOLEAN, downgrade_flag BOOLEAN, churn_flag BOOLEAN,
  billing_frequency TEXT, auto_renew_flag BOOLEAN);

-- usage_id is NOT unique in the source (21 collisions) -> no PK, add surrogate key
CREATE TABLE IF NOT EXISTS raven.feature_usage (
  row_id BIGSERIAL PRIMARY KEY, usage_id TEXT, subscription_id TEXT REFERENCES raven.subscriptions(subscription_id),
  usage_date DATE, feature_name TEXT, usage_count INT, usage_duration_secs INT,
  error_count INT, is_beta_feature BOOLEAN);

CREATE TABLE IF NOT EXISTS raven.support_tickets (
  ticket_id TEXT PRIMARY KEY, account_id TEXT REFERENCES raven.accounts(account_id),
  submitted_at TIMESTAMP, closed_at TIMESTAMP, resolution_time_hours NUMERIC, priority TEXT,
  first_response_time_minutes INT, satisfaction_score NUMERIC, escalation_flag BOOLEAN);

CREATE TABLE IF NOT EXISTS raven.churn_events (
  churn_event_id TEXT PRIMARY KEY, account_id TEXT REFERENCES raven.accounts(account_id),
  churn_date DATE, reason_code TEXT, refund_amount_usd NUMERIC, preceding_upgrade_flag BOOLEAN,
  preceding_downgrade_flag BOOLEAN, is_reactivation BOOLEAN, feedback_text TEXT);

-- Load (run from repo root in psql):
\copy raven.accounts FROM 'data/raw/ravenstack_accounts.csv' CSV HEADER
\copy raven.subscriptions FROM 'data/raw/ravenstack_subscriptions.csv' CSV HEADER
\copy raven.feature_usage (usage_id,subscription_id,usage_date,feature_name,usage_count,usage_duration_secs,error_count,is_beta_feature) FROM 'data/raw/ravenstack_feature_usage.csv' CSV HEADER
\copy raven.support_tickets FROM 'data/raw/ravenstack_support_tickets.csv' CSV HEADER
\copy raven.churn_events FROM 'data/raw/ravenstack_churn_events.csv' CSV HEADER
