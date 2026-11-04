-- Month-end MRR from the processed subscription-month panel.
-- Inactive and trial subscriptions have zero mrr_snapshot.
SELECT month_end,
       COUNT(*) FILTER (WHERE is_active_paid) AS active_paid_subs,
       SUM(mrr_snapshot) AS mrr
FROM raven.monthly_subscription_snapshot
GROUP BY month_end
ORDER BY month_end;
