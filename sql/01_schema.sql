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

CREATE TABLE IF NOT EXISTS raven.monthly_subscription_snapshot (
  subscription_id TEXT NOT NULL REFERENCES raven.subscriptions(subscription_id),
  month_end DATE NOT NULL, account_id TEXT NOT NULL REFERENCES raven.accounts(account_id),
  plan_tier TEXT, seats INT, billing_frequency TEXT, start_date DATE, end_date DATE,
  is_trial BOOLEAN, is_active BOOLEAN NOT NULL, is_active_paid BOOLEAN NOT NULL,
  is_new_subscription BOOLEAN NOT NULL, is_churned_subscription BOOLEAN NOT NULL,
  mrr_snapshot NUMERIC NOT NULL, arr_snapshot NUMERIC NOT NULL,
  PRIMARY KEY (subscription_id, month_end)
);

CREATE INDEX IF NOT EXISTS idx_monthly_snapshot_month_end
  ON raven.monthly_subscription_snapshot(month_end);

-- Load cleaned interim tables and the processed snapshot with sql/02_load_data.sql.
