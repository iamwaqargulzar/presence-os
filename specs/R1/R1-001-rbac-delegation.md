# R1-001 — RBAC and Delegated Access

> **Spec revision:** 3 — 2026-11-14. Amended by [ADR-0030](../../docs/adrs/ADR-0030-operator-run-agency-deployment.md); the "ADR-0030 amendments" section overrides any conflicting text below it. Revision 2 (2026-11-10): Expanded from a one-paragraph summary to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). The revision 1 summary is kept verbatim under Goal. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## ADR-0030 amendments (revision 3)
**Added to scope**
- **Operator** role: the single owner who runs the deployment. The operator holds platform authority and, for each tenant, an explicit `MANAGED_SERVICE` TenantAccessGrant created and audited when the tenant is created. The invariant "no tenant business-action authority without a TenantAccessGrant" is unchanged.
- **Client access levels** as tenant roles, assignable per client login and scoped to one tenant:
  - Client Viewer: read the tenant's properties, content, reports and audit summary;
  - Client Requester: Viewer plus submit change requests;
  - Client Approver: Requester plus approve or reject drafts presented to them.
- A permission, `manage_own_connections`, held by Client Requester and Client Approver: connect and disconnect the tenant's external accounts (R1-007).
- A dedicated permission, `start_ai_work`, that no client role holds. Client requests create queue items for the operator; they never start a run.

**Removed from scope**
- Platform Support as a distinct role; it may be added later if staff join.

**Added acceptance criteria**
- a client login can read and act only within its own tenant;
- a Client Requester's request produces a queue item and no run, no AI call and no external action;
- a Client Approver's approval can satisfy an approval requirement only for the artifact shown, and never widens authority;
- the operator's actions in a tenant are audited in the managed-operator capacity with the grant ID.

**Added tests**
- Permission matrix for the three client levels, including denial of `start_ai_work`.
- Cross-tenant: client of tenant A denied on every read and write in tenant B.

**Open decisions added**
- **Decided (owner, 2026-11-15):** a client cannot revoke or pause the operator's managed-service grant. Ending service is done by the operator from the operator console when the client asks. Clients can still see the grant, and can disconnect their own connected accounts (`manage_own_connections`). This overrides the revision 2 text that gave tenants list-and-revoke: clients get list only.

## Goal
Implement roles/permissions plus TenantAccessGrant, Managed Operator context, expiration/revocation and audited Break Glass scaffold. Platform Owner alone must not authorize tenant business actions.

## Why now
The Authorization Service (R1-002) can only mint a grant if it can answer "is this actor permitted to request this, in this tenant, in this capacity?". The operator manages every tenant through delegated access, and clients sign in with limited roles, so both must be explicit from the first kernel release.

## Context / linked docs / ADRs
- Edge cases added 2026-11-14 that this task must cover: E-071, E-072, E-086 ([register](../../docs/PROJECT_REAUDIT_2026-08-10.md)).
- [Delegation, managed service and break glass](../../docs/security/delegation-and-break-glass.md)
- [Person, profile and tenant model](../../docs/product/person-profile-tenant-model.md)
- [Admin and managed service](../../docs/product/admin-and-managed-service.md)
- [Audit ledger](../../docs/security/audit-ledger.md)
- [Re-audit edge cases E-012, E-060](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- Contract: [tenant-access-grant.schema.json](../../contracts/schemas/tenant-access-grant.schema.json)
- ADR-0003 (AI cannot mint authority), ADR-0004 (RLS)

## Depends on
- R0-003, R0-004, R0-006 *(derived)*.

## Invariants
- platform authority and tenant authority are separate; holding both is shown and audited as two distinct capacities;
- a Platform Owner has no tenant business-action authority without a TenantAccessGrant;
- managed access is an explicit grant the tenant can inspect, never an implicit super-admin privilege; only the operator revokes it (owner decision, 2026-11-15);
- break glass is not a convenient admin mode: explicit reason, short-lived, least scope, highly visible;
- permissions are evaluated deterministically in code, never by a model.

## In scope
- Role and Permission entities for tenant roles (Tenant Owner, Tenant Admin, Tenant Member, Contractor/Delegate) and the platform role (Operator, called Platform Owner in older text), kept in separate namespaces.
- Permission check service used by all modules.
- TenantAccessGrant: tenant, grantee (user or organisation), role, permissions, approval categories, valid_from, valid_until, granted_by, status (PENDING, ACTIVE, REVOKED, EXPIRED), reason (MANAGED_SERVICE, SUPPORT, TEMPORARY, CONTRACTOR, BREAK_GLASS).
- Managed Operator acting context, distinct from membership context, carried into audit.
- Expiry and revocation that take effect on the next permission check.
- Tenant-side list of grants (view only). Revocation is an operator action.
- Break Glass scaffold: request with reason, time-boxed grant, internal notification hook, audit, review list.
- Tenant-owner-only actions enumerated and enforced: ownership transfer, tenant deletion, removing the tenant owner, critical security settings, legal/financial commitments.

## Out of scope
- AuthorizationGrant minting (R1-002).
- Custom tenant-defined roles.
- Organisation/agency hierarchy beyond a grantee identifier.
- Full admin console UI.
- Automated periodic break-glass review workflow (list only).

## API / contract changes
- Permission check interface: `(acting context, permission, resource) → allow/deny + reason`.
- Grant management endpoints: create, list, revoke; break-glass request.
- `tenant-access-grant.schema.json`: add an `id`, and confirm the grantee type. Any change is reviewed.
- Acting-context contract from R0-004 extended with capacity (member, managed operator, break glass) and grant ID.

## Data / migration
- Tables: Role, Permission, role-permission mapping, TenantAccessGrant, break-glass record. Tenant-scoped ones under RLS.
- A grant lives in the granting tenant's scope; the grantee reads it through an explicit cross-tenant lookup that reveals only their own grants.
- Reverse migrations tested.

## Security / privacy threat notes
- Privilege escalation by self-granting or by a tenant admin granting above their own role.
- Platform staff reading tenant data by default (E-012).
- Expired or revoked grant still honoured through a cached decision.
- Capacity confusion: an action performed as managed operator recorded as the tenant owner.
- Break glass used routinely; reason field left meaningless.
- Bulk platform change turning into tenant business authority (E-060).

## Observability
- Audit: role assignment, grant created/activated/revoked/expired, managed-operator session start, break-glass request and use, every denied tenant-owner-only action.
- Metric: permission denials by reason; active grants; break-glass count.

## Acceptance criteria
- *(revision 1)* roles/permissions implemented;
- *(revision 1)* TenantAccessGrant with expiration and revocation;
- *(revision 1)* Managed Operator context;
- *(revision 1)* audited Break Glass scaffold;
- *(revision 1)* Platform Owner alone cannot authorize tenant business actions;
- a client can list grants on its own tenant and cannot revoke or pause them; a negative test proves it;
- *(derived)* dual-capacity person is audited distinctly per capacity;
- *(derived)* tenant-owner-only actions are denied to managed operators and break-glass sessions unless stronger confirmation is defined for them.

## Tests
- Unit: permission matrix per role.
- Integration: grant lifecycle, expiry at boundary time, revocation effective on next check.
- Security: platform owner without grant denied on every tenant-scoped write; grantee cannot read other tenants' grants; cross-tenant RLS suite on all new tables; self-escalation denied.
- Audit: each event recorded with capacity and grant ID.

## Rollback / failure recovery
Permission checks fail closed. Reverse migrations tested. If a role mapping is wrong, correct it with a forward data migration and add a regression test.

## Cost/resource budget
Negligible. Permission checks are on every request path: bound them to a small constant number of queries and measure.

## Documentation updates
- `docs/security/delegation-and-break-glass.md` (concrete permission list, tenant-owner-only list).
- `docs/product/person-profile-tenant-model.md`.
- Contract schema.

## Open decisions
- **Decision required:** initial permission catalogue and its naming scheme.
- **Decided (ADR-0033):** 60 minutes at most; the operator is notified by push and email.
- **Decided (ADR-0033):** Person only in R1.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review recorded.
