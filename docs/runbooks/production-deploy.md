# Runbook — Production Deployment

Initial policy: coding agents may build to staging; production is controlled separately.

1. Confirm task/commit/build provenance.
2. Confirm CI/test/review/security gates.
3. Confirm migration plan and backup/rollback.
4. Confirm feature-flag state.
5. Confirm no unresolved high-severity findings.
6. authorize release through Release Controller/human.
7. deploy/canary.
8. run health/synthetic/E2E checks.
9. monitor errors/workflows/actions.
10. promote stable.
11. record deployment and resulting versions.
12. rollback/disable flag if thresholds breached.
