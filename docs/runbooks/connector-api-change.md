# Runbook — External API / Connector Change

1. Ecosystem Watch or error monitoring detects change.
2. Verify against official provider documentation.
3. Identify affected connector version/capabilities/tenants.
4. If urgent, degrade/disable unsafe affected actions.
5. Create task/spec and isolated branch.
6. Update adapter only; avoid leaking provider change across product modules.
7. Run contract/integration/security tests.
8. Test auth/scopes/rate limits.
9. Stage with test account.
10. rollout internal/canary.
11. promote stable.
12. update capability matrix and last-verified date.
13. preserve rollback adapter/version if feasible.
