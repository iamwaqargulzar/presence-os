# R1-013 — Default Model Change with Preview and Rollback

> **Spec revision:** 4 — 2026-11-14. Rewritten as clean text after [ADR-0030](../../docs/adrs/ADR-0030-operator-run-agency-deployment.md): canary cohorts, staged change modes and emergency remap are removed because one operator runs the system and nothing is sold. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## Goal
Let the operator change the default model profile for a task class safely: see who is affected first, activate, and roll back.

## Why now
Models are deprecated, repriced and improved on a timescale of weeks. The first time a default must change, an unversioned edit would touch every tenant at once with no way back.

## Context / linked docs / ADRs
- [Model default change procedure](../../docs/operations/model-policy-change-management.md)
- [Tenant Presence AI, model profiles and provider policy](../../docs/ai/tenant-ai-model-entitlements.md)
- [Change management](../../docs/operations/change-management.md)
- [Model/harness qualification runbook](../../docs/runbooks/model-harness-qualification.md)
- [Edge cases E-001, E-003, E-060, E-063](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0024, ADR-0030

## Depends on
- R1-004
- R1-012
- R0-006 audit/observability

## Invariants
- every mapping change is a versioned ModelPolicyRevision; nothing is edited in place;
- tenant overrides are never changed by a default change;
- in-flight runs keep their pinned profile; the change applies at the next run or session boundary;
- a default change is a platform action and never mints tenant business authority;
- a tenant whose provider policy the new default would violate is excluded, not migrated.

## In scope
- ModelPolicyRevision: version, task-class → AIModelProfile revision mapping, created by, reason, preview result, activation time, rollback target, status (DRAFT, PREVIEWED, ACTIVE, ROLLED_BACK, SUPERSEDED).
- Pre-validation of the target profile's capability, privacy and price metadata.
- Preview: tenants that follow the default and will change, tenants that are pinned and will not, and tenants excluded by provider policy with the reason.
- Activation, which recomputes the affected set at that moment.
- Rollback to the recorded previous revision.
- Scheduled workflows re-resolve their profile before execution.
- Optional scope: apply to all followers or to selected tenants.

## Out of scope
- Canary cohorts, activation scheduling, forced migration of pinned tenants, a separate emergency-remap mode.
- Automatic rollback on metrics.
- Quality evaluation of the new model (PresenceBench and the qualification runbook).
- Console UI beyond minimal endpoints (the mobile console is R2/R3).

## API / contract changes
- Operator endpoints: create revision, preview, activate, roll back, inspect.
- New contract sketch `model-policy-revision.schema.json`.
- Adds "policy revision in force" as an input to the R1-012 resolver.

## Data / migration
- Platform-level tables: ModelPolicyRevision, preview result, per-tenant application record.
- Reverse migrations tested.

## Security / privacy threat notes
- A default change turning into a tenant side effect (E-060).
- New default violating a tenant's provider or local-only policy (E-007, E-063): excluded and reported.
- Stale preview applied after tenants changed: activation recomputes.
- Change made by anyone other than the operator: requires operator authority and a recorded reason.

## Observability
- Audit: every revision state change, preview, activation and rollback, with actor and reason; per-tenant application record.
- After activation: errors, cost and pause/fallback rate for affected tenants are visible for comparison.

## Acceptance criteria
- ModelPolicyRevision state and versioning;
- preview shows affected, pinned and excluded tenants;
- tenant overrides preserved;
- activation and rollback to the recorded revision;
- in-flight session pinning respected;
- scheduled workflows re-resolve before execution;
- every change audited and requires operator authority;
- *(derived)* activation recomputes the affected set;
- *(derived)* rollback restores the previous mapping for followers and leaves overrides untouched.

## Tests
- Preview correctness on a fixture of following, pinned and policy-excluded tenants.
- Activation then rollback.
- In-flight session keeps its pin through activation; a scheduled workflow starting after activation resolves the new revision.
- A local-only or provider-restricted tenant is excluded and its runs pause instead of using a forbidden profile.
- Non-operator denied.
- Audit completeness for one full change.
- All with the fake gateway adapter.

## Rollback / failure recovery
Rollback is a first-class operation to a recorded revision. Activation is idempotent and resumable per tenant so a partial failure can continue or be reversed. Reverse migrations tested.

## Cost/resource budget
Preview and activation iterate over tenants: run as background work under the Resource Governor. With tens of tenants this is small.

## Documentation updates
- `docs/operations/model-policy-change-management.md`.
- `docs/runbooks/model-harness-qualification.md` (handoff into a default change).
- Contract schema; `docs/data/core-entity-catalog.md`.

## Open decisions
- **Decision required:** final revision state names.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: one rehearsal of preview, activate and rollback recorded as evidence for R1-010.
