# Person, Profile and Tenant Model

> **Updated 2026-11-14** for [ADR-0030](../adrs/ADR-0030-operator-run-agency-deployment.md): Presence OS is run by one operator for their own companies and managed clients. It is not sold as a product.

A login belongs to a **Person**. Sign-in is Google sign-in only, by invitation.

## Tenants

A tenant is the isolation and authority boundary for one of the operator's own companies or one managed client. Each tenant isolates:
- limits and budgets;
- connections and secrets;
- knowledge/memory/files;
- browser identities;
- skills and policies;
- usage and workflows;
- audit.

The operator switches between tenants with an explicit context selector, for example:
`Acting as: Company A / Client B / Client C`

## Roles

Platform roles and tenant roles are distinct.

Platform:
- **Operator** (the single owner who runs the deployment).

Tenant:
- Tenant Owner
- Tenant Admin
- Tenant Member
- Client Viewer: read the tenant's properties, content, reports and audit summary;
- Client Requester: Viewer plus submit change requests and connect or disconnect the tenant's external accounts;
- Client Approver: Requester plus approve or reject drafts shown to them;
- Contractor/Delegate.

The operator does not automatically possess tenant business-action authority. For each tenant the operator holds an explicit `TenantAccessGrant` (reason `MANAGED_SERVICE`), created when the tenant is created, and acts in the audited Managed Operator capacity.

No client role can start AI work. A client request creates a queue item for the operator.

## Tenant AI identity
Each tenant owns one stable logical `TenantAIIdentity` / Presence AI. The model behind it is selected by `TenantAIConfiguration` and the platform default; memory, authority and identity do not live in the model instance.

## Digital properties
Each tenant may own multiple `DigitalProperty` records. Property count, runtime and domain limits are per-tenant limits, not identity boundaries.

## Open decision
Whether an operator-owned personal profile is its own tenant or a profile inside a personal tenant (carried from R0-004).
