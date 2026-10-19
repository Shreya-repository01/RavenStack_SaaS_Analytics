# Team Roles & 4-Week Plan

| Role | Owner | Main outputs |
|---|---|---|
| Team lead / Report & QA | | README, report, reconciliation of dashboard vs Python/SQL, PR reviews |
| Data engineer | | Postgres schema, loaders, data dictionary, data-quality report, interim tables |
| KPI analyst | | MRR/New/Expansion/Contraction/Churned MRR, churn rates, metric dictionary |
| Retention analyst | | Cohorts, segment comparison (plan/channel/industry), churn drivers (tickets, usage) |
| BI developer | | Power BI model + 4-page dashboard |

| Week | Goal | Done when |
|---|---|---|
| 1 | Ingest, audit, data dictionary, freeze metric definitions | `reports/data_quality_audit.csv` reviewed, `docs/metric_definitions.md` agreed |
| 2 | MRR, movements, churn | Monthly KPI table validated on hand-checked examples |
| 3 | Cohorts, drivers, (forecast only if it beats a naive baseline) | Cohort matrix + findings list |
| 4 | Dashboard, report, presentation | Dashboard totals match `data/processed/` tables |

## Git rules
- Never commit to `main` directly. Branch per task: `feature/<name>-<topic>`.
- Commit small and often, message format: `type: what` (data: / kpi: / eda: / dash: / docs: / fix:).
- Open a Pull Request; lead reviews and merges. Pull `main` before starting work each day.
