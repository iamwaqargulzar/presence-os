# Runbook — Security Incident

1. Declare severity.
2. Pause affected autonomous actions globally or per tenant.
3. Revoke relevant AuthorizationGrants/tokens/connections.
4. Isolate compromised worker/tenant/service.
5. Preserve immutable audit/log/provenance.
6. Rotate compromised secrets.
7. Assess cross-tenant exposure.
8. Restore known-good state.
9. Validate tenant integrity and external side effects.
10. Notify required internal/customer/legal parties according to policy.
11. Build a regression test/PresenceBench case.
12. Complete postmortem and remediation.

Do not let an agent autonomously erase evidence during remediation.
