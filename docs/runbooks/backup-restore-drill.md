# Runbook — Backup Restore Drill

## Frequency

Set an initial cadence in R0 and tighten as production importance grows.

R0 cadence (R0-009): one full drill before R0 closes, then one each quarter and after any change to the backup setup. Record each drill from `evidence/R0/R0-009/restore-drill.md` and compare it with the objectives in `docs/infrastructure/backup-disaster-recovery.md`. Monthly from the first client's production data.

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
