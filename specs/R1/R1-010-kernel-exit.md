# R1-010 — Kernel E2E/Security Exit

> **Spec revision:** 2 — 2026-11-10. Expanded to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). The revision 1 summary is kept verbatim under Goal and the 2026-08-10 additional exit requirements are retained. Items marked *(derived)* come from the linked focused documents.

## Goal
Prove an authorized tenant action can travel request → intent/authorization → Action Broker → fake/test connector with audit/idempotency, while unauthorized/cross-tenant/stale-artifact/revoked/over-budget variants fail closed.

## Why now
R2 adds conversation and agents on top of the kernel. Agents will probe every boundary by accident; the boundaries must be proven with a deterministic end-to-end suite first.

## Context / linked docs / ADRs
- [R1 README](README.md) and every R1 task contract
- [Authority and Action Broker](../../docs/security/authority-and-action-broker.md)
- [Threat model](../../docs/security/threat-model.md)
- [Testing strategy](../../docs/delivery/testing-strategy.md)
- [Re-audit and edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md) (all entries tagged R1)
- ADR-0002, ADR-0003, ADR-0004, ADR-0021 to ADR-0024

## Depends on
- R1-001 through R1-009, R1-011, R1-012, R1-013.

## Invariants
- evidence, not declaration, closes the release;
- any cross-tenant access or unauthorised side effect is a release blocker;
- the exit suite uses only fake/test connectors and synthetic data;
- defects found are fixed in the owning task, not patched in the exit suite.

## In scope
- End-to-end test harness with at least two tenants, a managed operator, and a platform owner.
- The positive path and every negative variant below.
- Confirmation that no default-deny stub from R1-003 remains.
- Disposition of every R1-tagged edge case.
- R1 exit report.

## Out of scope
- Conversation/intent resolution (the suite submits structured intents).
- Real providers and real DNS changes.
- Performance and load qualification beyond the R1-009 fairness evidence.
- External penetration test.

## API / contract changes
None. Confirms that kernel contracts (acting context, permission check, grant, action, tenant limit, reservation, hostname, connection, artifact reference, admission, property, model-profile resolution) are documented and their schemas match the implementation.

## Data / migration
None. Confirms the full R0+R1 migration chain applies from empty and that the RLS coverage check reports no unprotected tenant table.

## Security / privacy threat notes
The suite is the regression barrier for the kernel's threat model. It must run under the runtime database role, and it must be a protected path that implementation workers cannot edit in the same run.

## Observability
For the positive path, assert on the audit trail itself: who, under which authority source and capacity, to which tenant, using which artifact, through which connection, with what result. Evidence stored under `evidence/R1/`.

## Acceptance criteria
Positive path:
- an authorised human request produces a grant, an action, one fake-connector effect, a settled reservation and a complete audit trail; a retried execution produces no second effect.

Fail-closed variants (each must produce no connector call):
- unauthorised actor;
- platform owner without a grant;
- cross-tenant grant, artifact, connection or hostname reference;
- stale artifact (edited after approval);
- revoked grant; expired grant;
- revoked or unhealthy connection at execution time;
- over-budget; tenant limit lowered while queued;
- suspended tenant;
- high-risk action without confirmation;
- approval-like text arriving in untrusted content.

2026-08-10 additional exit requirements:
- multiple DigitalProperties per tenant pass ownership/RLS/quota/hostname tests;
- TenantAIIdentity/model-profile resolution passes override, provider-policy, credential-class and fallback tests;
- default model change supports preview, activation and rollback and preserves tenant overrides;
- effective model profile is pinned per run/session and observable/auditable.

*(Derived)*
- every R1-tagged edge case has a recorded disposition;
- every R1 open decision is resolved in an ADR or carried forward with an owner.

## Tests
The acceptance list is the test list. Additionally re-run from a clean clone at the candidate commit: the full CI pipeline, the RLS isolation suite across all R1 tables, and each task's security suite.

## Rollback / failure recovery
A failed exit produces blocking defects assigned to owning tasks; the suite is re-run after fixes. Nothing is rolled back by this task.

## Cost/resource budget
One full pipeline run. No model calls are required; any AI-profile test uses the fake gateway adapter.

## Documentation updates
- R1 exit report.
- Corrections to documents and schemas that no longer match the implementation.
- `docs/DECISION_REGISTER.md`, ADR index, `README.md` status.
- Draft of R2 task contracts may begin only after acceptance.

## Definition of done
The exit report exists, every acceptance item links to stored evidence, there are no open security-critical findings, an independent reviewer has signed off the suite, and the owner has accepted the report.
