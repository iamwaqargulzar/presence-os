# R1-011 — DigitalProperty, Environments and Multi-Property Ownership

> **Spec revision:** 2 — 2026-11-10. Expanded to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). Every revision 1 requirement is retained. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## Goal
Allow one tenant/profile to own multiple websites/apps without weakening tenant or runtime isolation.

## Why now
"One tenant, one site" is forbidden as a data-model assumption. If hostnames, artifacts, secrets and quotas are built without a property dimension, R3 hosting would need to re-key all of them.

## Context / linked docs / ADRs
- [Digital properties and multi-property hosting](../../docs/product/digital-properties-and-hosting.md)
- [Platform hostname model](../../docs/domains/hostname-model.md)
- [Tenant limits, budgets and usage](../../docs/commercial/plans-tenant limits-billing.md) (property hosting limits)
- [Secrets management](../../docs/security/secrets.md)
- [Re-audit edge cases E-013 to E-023](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- Contract: [digital-property.schema.json](../../contracts/schemas/digital-property.schema.json)
- ADR-0021 (DigitalProperty is first-class), ADR-0008, ADR-0016

## Depends on
- R1-001 RBAC
- R1-004 tenant limits/budgets
- R1-005 hostname registry
- R1-008 artifact ownership/versioning
- R1-009 resource governor

## Invariants
- a tenant/profile owns zero or more DigitalProperties;
- "same tenant" is not a reason to share secrets, runtime state or data: sharing requires an explicit, audited binding;
- hostname attachment uniqueness is enforced atomically by the Hostname Registry;
- no implicit path-sharing between independent properties;
- property hosting limits are separate from AI budgets;
- product behaviour does not depend heavily on the property-type enum;
- `tenant_id` on a property is never updated ad hoc; transfer is a separate privileged workflow.

## In scope
- DigitalProperty entity: tenant, profile, name, property_type (WEBSITE, WEB_APP, PORTAL, LANDING, BOOKING, STORE, DOCS_HELP, DASHBOARD, OTHER), status (DRAFT, ACTIVE, SUSPENDED, ARCHIVED, DELETING, DELETED), canonical hostname.
- PropertyEnvironment: PREVIEW, STAGING (optional), PRODUCTION.
- HostnameAttachment: one hostname to one environment/service route.
- Deployment record (data model and lifecycle states only): DRAFT → BUILT → VERIFIED → PREVIEW → AUTHORIZED → DEPLOYING → HEALTHY, with BUILD_FAILED, VERIFY_FAILED, DEPLOY_FAILED, UNHEALTHY, ROLLED_BACK, ARCHIVED.
- Property-scoped references: artifacts, secret references (namespace tenant + property + environment), PropertyDataBinding, audit.
- Quota enforcement through tenant limits: max active properties, max production properties.
- Resource-attribution hooks into the Resource Governor (per-property dimension).
- Archive and delete lifecycle: archive first, stop workloads, tombstone hostnames, retain reversible metadata, then delete per policy.
- Sensitive-preview rule: authenticated, randomized, `noindex`, expiring.

## Out of scope
- Building, running or serving property code; runtime profiles (R3).
- ServiceUnit runtime components beyond the entity placeholder.
- Property transfer between tenants (R3+; the invariant is enforced, the workflow is not built).
- Path/route composition under one hostname.
- Migration lanes and background-job reconciliation for property apps (R3/R4).

## API / contract changes
- Endpoints: create, list, get, update (with `base_version`), archive, delete property; manage environments; attach/detach hostname.
- `digital-property.schema.json` refined; add contract sketches for PropertyEnvironment, Deployment and HostnameAttachment.
- Confirms the hostname binding target chosen in R1-005.

## Data / migration
- Tables: DigitalProperty, PropertyEnvironment, HostnameAttachment, Deployment, PropertyDataBinding, ServiceUnit placeholder. All tenant-scoped under RLS, with profile scoping as decided in R0-003.
- Uniqueness: one active attachment per hostname, enforced by constraint.
- Secret reference namespace extended with property and environment.
- Reverse migrations tested.

## Security / privacy threat notes
- Cross-property access inside one tenant: a member with rights to one property acting on another, or one property reading another's secrets (E-022).
- Two properties claiming one hostname (E-014).
- Deleted property with a live domain (E-016): tombstone and safe holding response.
- Preview leak (E-023).
- Quota bypass by concurrent creation.
- One property exhausting tenant capacity (E-021).

## Observability
- Audit: property and environment lifecycle, hostname attach/detach, deployment state changes, binding created/removed.
- Metrics: properties by status per tenant, quota denials, attachments by type.
- All property-scoped work carries `property_id` in trace context.

## Acceptance criteria
- DigitalProperty and PropertyEnvironment entities with tenant/profile RLS;
- one tenant may create multiple properties subject to the tenant's limit;
- property-scoped artifacts, deployments, secrets/data binding references and audit;
- atomic hostname attachment uniqueness;
- preview/production environment distinction;
- archive/delete lifecycle with domain/hostname safety;
- cross-tenant/property negative tests;
- property quota enforcement and resource-attribution hooks;
- no implicit path-sharing between independent properties;
- *(derived)* a secret reference created for property A cannot be resolved in the context of property B without an explicit binding;
- *(derived)* archiving a property leaves its hostnames serving the safe holding response, not another property's content.

## Tests
- Create several properties up to quota; next creation denied; concurrent creation at the limit admits exactly the remainder.
- Hostname: parallel attach of one hostname to two environments.
- Cross-tenant RLS suite on every new table; cross-property secret and artifact access denied.
- Lifecycle: archive → hostnames tombstoned; delete blocked while a custom domain is active, or handled per the documented policy.
- Preview: unauthenticated access to a sensitive preview denied; noindex present; expiry enforced.
- Optimistic concurrency on property update.
- Path-sharing attempt rejected.

## Rollback / failure recovery
Archive is reversible within the retention window. Attach/detach is transactional. Reverse migrations tested. Deletion is a staged workflow that can resume after failure.

## Cost/resource budget
Property count and environment count are limit-bounded. No runtime resources are consumed in R1 since nothing is hosted yet.

## Documentation updates
- `docs/product/digital-properties-and-hosting.md` (concrete fields and states).
- `docs/data/core-entity-catalog.md`.
- Contract schemas and `contracts/README.md`.

## Open decisions
- **Decided (ADR-0033):** 30 days.
- **Decided (ADR-0033):** tenant roles apply to every property in R1.
- **Decided (ADR-0033):** deletion is blocked until the custom domain is detached.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review of cross-property isolation is recorded.
