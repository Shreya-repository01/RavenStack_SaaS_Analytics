-- STARTER EXAMPLE (KPI owner to validate): month-end MRR from active, non-trial subscriptions.
-- A subscription is active at month-end M if start_date <= M and (end_date IS NULL OR end_date > M).
WITH months AS (
  SELECT (date_trunc('month', d) + interval '1 month - 1 day')::date AS month_end
  FROM generate_series('2023-01-01'::date, '2024-12-01'::date, interval '1 month') d)
SELECT m.month_end,
       COUNT(*)            AS active_paid_subs,
       SUM(s.mrr_amount)   AS mrr
FROM months m
JOIN raven.subscriptions s
  ON s.start_date <= m.month_end AND (s.end_date IS NULL OR s.end_date > m.month_end)
WHERE s.is_trial = FALSE
GROUP BY m.month_end ORDER BY m.month_end;
