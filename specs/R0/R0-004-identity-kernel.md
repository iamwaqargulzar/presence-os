# R0-004 — Identity/Profile/Tenant Kernel

> **Spec revision:** 3 — 2026-11-14. Amended by [ADR-0030](../../docs/adrs/ADR-0030-operator-run-agency-deployment.md); the "ADR-0030 amendments" section overrides any conflicting text below it. Revision 2 (2026-11-10): Expanded to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). Every revision 1 requirement is retained. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## ADR-0030 amendments (revision 3)
**Added to scope**
- Sign-in is **Google sign-in (OpenID Connect) only**, for the operator and for clients. There is no password login, password reset, or open signup, and no password is stored.
- **Invitation allow-list:** only an email address the operator has invited, for a named tenant and role, can complete sign-in. Any other Google account is refused after authentication and no account is created for it.
- The identity is bound to Google's stable subject identifier, not to the email string alone, and only a verified email is accepted.
- Session controls: list and revoke sessions; revoking an invitation ends that person's sessions.

**Added acceptance criteria**
- no endpoint accepts a password;
- an uninvited Google account cannot create a user, a session or any tenant-visible record;
- a changed or recycled email address on a different Google subject does not inherit the earlier user's access;
- removing an invitation takes effect on the next request.

**Added threat notes**
- Password guessing against Presence OS is removed because there is no password. Account takeover risk moves to the person's Google account: the operator account must use two-step verification, and this is recorded as an operating requirement.
- Sign-in callback abuse: strict redirect URI, state and nonce checks, and sign-in attempt rate limiting.
- Google outage or a locked account blocks sign-in; the recovery procedure for the operator is documented and does not add a password back door.

**Open decisions changed**
- **Decided (ADR-0033):** django-allauth with only the Google provider enabled and password sign-in disabled, subject to dependency review.
- **Decided (ADR-0033):** (owner, 2026-11-15) the client creates a Google account on their existing email, or has no login and the operator records an operator-attested approval. No second sign-in method.

## Goal
Implement Person, Tenant, Profile, Membership and explicit active-profile context.

## Why now
Every authorization, audit, budget and resource decision needs to know who is acting and as which profile. R1 RBAC and delegation build directly on these entities.

## Context / linked docs / ADRs
- Edge cases added 2026-11-14 that this task must cover: E-067 to E-070, E-073, E-090 ([register](../../docs/PROJECT_REAUDIT_2026-08-10.md)).
- [Person, profile and tenant model](../../docs/product/person-profile-tenant-model.md)
- [Tenant lifecycle](../../docs/operations/tenant-lifecycle.md)
- [State machines](../../docs/architecture/state-machines.md)
- [Delegation and break glass](../../docs/security/delegation-and-break-glass.md)
- [Core entity catalog](../../docs/data/core-entity-catalog.md)
- ADR-0003 (AI cannot mint authority), ADR-0004 (RLS), ADR-0022 (stable tenant AI identity)

## Depends on
- R0-003 (RLS framework).
- R0-006 provides the audit append path; if it is not merged yet, emit audit events through a narrow interface that R0-006 implements *(derived)*.

## Invariants
- a login belongs to a Person, not to a tenant;
- platform roles and tenant roles are distinct; a Platform Owner has no implicit tenant business authority;
- the acting profile is always explicit and determined server-side;
- all tenant-scoped tables are under RLS using the R0-003 framework;
- one-tenant-one-site and one-tenant-one-model must not be assumed anywhere in the data model.

## In scope
- Entities: Person, Tenant, Profile (Individual or Company), Membership.
- Authentication sufficient for a Person to log in.
- Active-profile context: selection, switching, and server-side resolution on every request.
- Tenant lifecycle base states. Every tenant is managed by the operator; there is no operating-mode field.
- Membership with a minimal base role set, enough to distinguish owner from member.

## Out of scope
- Full RBAC, permissions, TenantAccessGrant and break glass (R1-001).
- Tenant limits and budgets (R1-004).
- TenantAIIdentity entity (R1-012); reserve nothing that blocks it.
- Lifecycle transitions beyond base states (offboarding workflow, deletion).
- Final onboarding UI.

## API / contract changes
- Endpoints for: current person, list operable profiles, switch active profile, read acting context.
- The acting-context structure (person, tenant, profile, membership role) is a contract consumed by audit, authorization and the RLS context.
- Resource identifiers alone never authorize access.

## Data / migration
- New tables for the four entities, with RLS on tenant-scoped ones.
- Tenant state uses the documented lifecycle: PROVISIONING, ACTIVE, PAUSED, OFFBOARDING, CLOSED, DELETION_PENDING, DELETED. R0 implements creation and the base states; later transitions are defined but not all reachable.
- Mutable resources carry a `version` for optimistic concurrency.
- Reverse migrations tested.

## Security / privacy threat notes
- Profile confusion: a request executes under a different profile than the user sees. Mitigation: server-side resolution, context shown in responses, switch audited.
- Membership enumeration across tenants.
- Platform staff acting on tenant data without a grant: must be impossible in R0, since no grant mechanism exists yet.
- Session fixation and credential handling follow the chosen library's secure defaults; no passwords or tokens in logs.
- Person data is personal data: minimise fields.

## Observability
- Audit events: login, logout, failed login, profile switch, tenant created, membership changed.
- All requests carry person, tenant and profile IDs in trace context.

## Acceptance criteria
- Person can operate individual/company profiles;
- profile switch audited;
- tenant lifecycle base states;
- only the operator can create a tenant;
- no implicit platform-owner tenant business authority;
- API/UI can determine acting profile deterministically;
- *(derived)* a Person with one Individual Profile and several Company Profiles sees only their own memberships;
- *(derived)* all new tenant-scoped tables pass the R0-003 isolation suite.

## Tests
- Unit: context resolution, lifecycle state validation.
- Integration: login, profile switch, switch to a profile without membership is denied.
- Security: cross-tenant read/write of Profile and Membership denied under the runtime role; a platform-owner account cannot perform a tenant-scoped write.
- Audit: each listed event is recorded once with correct actor and context.

## Rollback / failure recovery
Reverse migrations tested. Feature is internal until R1; a defect is fixed forward. No external side effects exist to compensate.

## Cost/resource budget
Negligible. No paid identity provider is assumed.

## Documentation updates
- `docs/product/person-profile-tenant-model.md` (concrete fields).
- `docs/operations/tenant-lifecycle.md` (which transitions R0 implements).
- ADR for the authentication library.

## Open decisions
- **Decided (ADR-0033):** django-allauth, Google provider only.
- **Decided (ADR-0033):** (owner, 2026-11-15) an individual profile is its own tenant.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent review of authentication and context-resolution code is recorded.
