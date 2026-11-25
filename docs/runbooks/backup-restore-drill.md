# Runbook — Backup Restore Drill

## Frequency

Set an initial cadence in R0 and tighten as production importance grows.

## Drill

1. Select backup set and target recovery point.
2. Restore into isolated environment.
3. Restore PostgreSQL.
4. Restore object storage/artifacts.
5. Restore required application config.
6. Validate secrets recovery without leaking recovery material.
7. Start services.
8. Run:
   - login;
   - tenant/RLS checks;
   - knowledge queries;
   - workflow state;
   - action audit;
   - domain metadata;
   - representative file/artifact access.
9. Measure recovery duration and data-loss window.
10. Destroy drill environment safely.
11. Record results and defects.

A backup that has never been restored is not considered proven.
