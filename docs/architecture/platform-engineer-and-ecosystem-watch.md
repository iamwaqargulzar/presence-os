# Platform Engineer and Ecosystem Watch

These are later-stage capabilities, not R0/R1.

## Platform Engineer

Safe self-maintenance pipeline:
incident/feature → logs/source/docs → branch → change → tests/security/migrations/E2E → staging → report → platform-owner approval → canary → stable → health/rollback.

No:
- self-approval;
- direct production edits;
- production secrets in coding sandboxes.

Feature rollout states:
- OFF
- INTERNAL
- BETA
- SELECTED_CLIENTS
- ALL

Release channels:
- DEV
- STAGING
- CANARY
- STABLE

## Ecosystem Watch

Monitors relevant:
- API versions/deprecations;
- OAuth changes;
- pricing/rate limits;
- platform policies;
- SDKs/browser changes;
- model releases;
- security advisories;
- SEO/search/commerce ecosystem changes.

It creates actionable, relevant tasks; it does not auto-modify production.
