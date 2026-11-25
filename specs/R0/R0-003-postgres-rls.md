# R0-003 — PostgreSQL Tenancy + RLS Foundation

> **Spec revision:** 2 — 2026-11-10. Expanded to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). Every revision 1 requirement is retained. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## Goal
Implement runtime/migration roles, tenant context and first protected tables under RLS.

## Why now
Tenant isolation is the foundation every business table sits on. Retrofitting RLS after modules exist is expensive and error-prone, and cross-tenant access is a release blocker.

## Context / linked docs / ADRs
- [Database tenancy and RLS](../../docs/security/database-tenancy-rls.md)
- [Threat model](../../docs/security/threat-model.md)
- [Concurrency, idempotency and consistency](../../docs/architecture/concurrency-idempotency.md)
- [Re-audit edge cases E-043, E-044](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- [PostgreSQL row security reference](../../docs/SOURCE_REGISTRY.md)
- ADR-0004 (shared PostgreSQL + RLS)

## Depends on
- R0-001, R0-002 *(derived from build-plan lane 2)*.

## Invariants
- shared PostgreSQL with `tenant_id` and Row Level Security; no database per tenant;
- the runtime role does not own tables and does not have BYPASSRLS;
- never rely on an application filter alone;
- never weaken tenant isolation to make a test pass;
- missing tenant context fails closed.

## In scope
- Roles: migration/owner role (schema ownership, never used at runtime) and runtime application role.
- Transaction-safe tenant/profile execution context that the pool cannot leak between requests.
- A reusable way to declare a table as tenant-protected, generating its policies consistently.
- First protected tables: a minimal fixture table sufficient to prove the pattern (real entities arrive in R0-004).
- A reusable RLS test framework that later modules call with their own tables.
- Guidance on foreign keys and integrity checks, which can behave outside ordinary RLS expectations.

## Out of scope
- Business entities (R0-004 onward).
- Vector retrieval isolation (R2; the framework must be able to cover it later).
- Read/reporting roles beyond a documented placeholder.
- Per-tenant databases or schemas.

## API / contract changes
- Internal only: the tenant-context interface (set, read, clear) and the protected-table declaration used by all modules.
- The RLS test framework's interface is a contract for later tasks; R0-010 and R1-010 rely on it.

## Data / migration
- Migrations run as the migration role; application connections use the runtime role.
- Policies are created in the same migration as the table they protect.
- `FORCE ROW LEVEL SECURITY` is applied where selected by design, with the choice recorded per table.
- Rollback: each migration has a tested reverse, or a documented forward-fix where reversal is unsafe.

## Security / privacy threat notes
- Pooled connection reuses a previous tenant's context.
- Table created without a policy, or with a policy that permits rows when context is unset.
- Runtime role accidentally granted ownership or BYPASSRLS by a later migration.
- Foreign-key checks revealing the existence of another tenant's rows.
- Shared caches keyed without tenant (E-044): out of scope to implement, in scope to document as a rule.

## Observability
- Count and log RLS/authorization failures with tenant and trace correlation, without logging row contents.
- A check (test or startup assertion) reports any tenant-scoped table lacking a policy.

## Acceptance criteria
- runtime role is not table owner;
- runtime role has no BYPASSRLS;
- tenant A cannot SELECT/INSERT/UPDATE/DELETE tenant B;
- pooled connection cannot leak tenant context;
- missing tenant context fails closed;
- FORCE RLS used where selected by design;
- RLS helper/test framework reusable by all later modules;
- *(derived)* a table without a policy is detected automatically;
- *(derived)* isolation also holds through joins and relationships on the fixture tables.

## Tests
All executed under the runtime role against a real PostgreSQL instance:
- role attribute assertions (not owner, no BYPASSRLS);
- cross-tenant SELECT, INSERT, UPDATE, DELETE each denied;
- join/relationship traversal denied;
- sequential requests on one pooled connection with different tenants;
- no tenant context: zero rows and writes rejected;
- seeded unprotected table trips the detection check.

## Rollback / failure recovery
Reverse migrations are tested in CI. If a policy defect is found after merge, the fix is a forward migration plus a new negative test; isolation is never relaxed as a workaround.

## Cost/resource budget
Negligible runtime cost. Note the per-transaction cost of setting context and confirm it is compatible with the chosen pooling mode.

## Documentation updates
- `docs/security/database-tenancy-rls.md` (concrete role names, context mechanism, per-table FORCE decisions).
- A short "how to add a tenant table" guide for later tasks.
- ADR if the pooling mode or context mechanism constrains future choices.

## Open decisions
- **Decided (ADR-0033):** no external pooler at the start; tenant context is a transaction-scoped setting set at the start of every transaction, never a session-scoped one.
- **Decided (ADR-0033):** R0 enforces tenant at the database layer; profile is enforced in the service layer until R1.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: the isolation suite runs in CI under the runtime role, and independent review of the policy and role migrations is recorded (security-sensitive task).
