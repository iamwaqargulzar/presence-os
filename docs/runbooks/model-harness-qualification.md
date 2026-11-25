# Runbook — Model/Harness Qualification

1. Register candidate model/provider/harness versions.
2. Record supported reasoning variants and API behavior.
3. Run quick screening.
4. If viable, run full PresenceBench on eligible roles.
5. Run multiple trials on stochastic/security-critical cases.
6. Compute quality/cost/cache/autonomy/security metrics.
7. Reject on any hard security gate.
8. Qualify specific execution profiles/roles, not “the model” universally.
9. Run shadow traffic/tasks.
10. Canary low-risk workload.
11. Promote to ACTIVE if thresholds hold.
12. Retain champion for rollback.
13. Re-evaluate after meaningful model/harness/prompt/tool changes.

External leaderboard performance can trigger step 1 only.
