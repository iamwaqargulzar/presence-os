# Model Default Change Procedure

> **Updated 2026-11-14** for [ADR-0030](../adrs/ADR-0030-operator-run-agency-deployment.md): Presence OS is run by one operator for their own companies and managed clients. It is not sold as a product.

Canary cohorts, staged change modes and emergency remap were removed. One operator changes one default at a time.

## Procedure

1. Qualify the new profile on real tasks (see the [qualification runbook](../runbooks/model-harness-qualification.md)).
2. Create a draft `ModelPolicyRevision` with the new task-class mapping and a reason.
3. Preview: which tenants follow the default and will change, which are pinned and will not, which are excluded by their provider policy.
4. Activate. The affected set is recomputed at that moment.
5. Watch errors, cost and pause/fallback rate for the affected tenants.
6. Roll back to the recorded previous revision if needed.

## Rules

- Nothing is edited in place; every change is a new revision.
- Tenant overrides are never changed by a default change.
- In-flight runs keep their pinned profile. Scheduled workflows re-resolve before they execute.
- A tenant the new default would violate (provider policy, local-only) is excluded and reported.
- Every step is audited with actor and reason. A default change never mints tenant business authority.

## Provider outage or deprecation

Use the same procedure. If no qualified replacement exists, affected runs pause with a reason; they do not silently move to a provider the tenant's policy forbids.
