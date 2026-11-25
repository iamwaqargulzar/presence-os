# Runbook — Vanity Hostname Claim

1. Normalize requested label.
2. Validate syntax.
3. Check reserved/protected patterns.
4. Run abuse/impersonation checks.
5. Informational availability check.
6. On claim, use atomic database transaction/unique constraint.
7. Bind VANITY hostname to same internal service as RANDOM_CANONICAL.
8. Verify routing.
9. Record entitlement/fee.
10. Audit owner/time.

On rename/release:
- keep canonical random host unchanged;
- redirect old vanity during transition if policy allows;
- quarantine before recycling.
