-- Expected: 500, 5000, 25000, 2000, 600, 120000
SELECT 'accounts' AS table_name, COUNT(*) AS row_count FROM raven.accounts
UNION ALL SELECT 'subscriptions', COUNT(*) FROM raven.subscriptions
UNION ALL SELECT 'feature_usage', COUNT(*) FROM raven.feature_usage
UNION ALL SELECT 'support_tickets', COUNT(*) FROM raven.support_tickets
UNION ALL SELECT 'churn_events', COUNT(*) FROM raven.churn_events
UNION ALL SELECT 'monthly_subscription_snapshot', COUNT(*) FROM raven.monthly_subscription_snapshot;

-- Expected: 3833405
SELECT SUM(mrr_snapshot) AS mrr_june_2024
FROM raven.monthly_subscription_snapshot
WHERE month_end = '2024-06-30';

-- Expected: 0 (no snapshot rows without a subscription)
SELECT COUNT(*) AS orphan_snapshot_rows
FROM raven.monthly_subscription_snapshot m
LEFT JOIN raven.subscriptions s USING (subscription_id)
WHERE s.subscription_id IS NULL;