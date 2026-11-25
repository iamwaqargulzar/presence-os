# R1-004 — Tenant Limits, Usage Ledger and Budgets

> **Spec revision:** 4 — 2026-11-14. Rewritten as clean text after [ADR-0030](../../docs/adrs/ADR-0030-operator-run-agency-deployment.md): plans, subscriptions, seats and billing are removed because Presence OS is run by one operator and is not sold. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## Goal
Implement versioned per-tenant limits, an append-only usage ledger, tenant and global budgets, and atomic budget reservation and settlement.

## Why now
The Action Broker checks a limit and a budget before every side effect. Property counts (R1-011) and AI spending (R1-012) are both expressed as limits. Without atomic reservation, concurrent workers can all pass a balance pre-check and overspend the operator's money.

## Context / linked docs / ADRs
- [Tenant limits, budgets and usage](../../docs/commercial/plans-entitlements-billing.md)
- [Cost and resource governance](../../docs/architecture/cost-resource-governance.md)
- [Tenant lifecycle](../../docs/operations/tenant-lifecycle.md)
- [Edge cases E-009, E-053, E-060, E-064, E-065](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- Contract: [budget-reservation.schema.json](../../contracts/schemas/budget-reservation.schema.json)
- ADR-0019 (Resource Governor separate from Cost Governor), ADR-0030

## Depends on
- R0-003, R0-004, R0-006.
- Supplies the limit and budget check implementations for R1-003.

## Invariants
- limits are versioned; a change never rewrites history;
- reserve, execute, settle, refund: no expensive operation runs on a pre-check alone;
- money (Cost Governor) and capacity (Resource Governor, R1-009) are separate controls;
- limits and prices are data, not code;
- every cost is attributable to tenant, task/workflow/action and provider/model;
- only the operator sets limits and budgets; a client role can read its own tenant's usage but change nothing.

## In scope
- TenantLimit: versioned key/limit/period records per tenant, set by the operator (for example property count, runs per day, posts per day, monthly AI budget).
- Limit check service: `(tenant, key, quantity) → allow/deny + reason`, resolved against the revision in force.
- Usage ledger (append-only UsageRecord) separating Platform Actions, AI usage and External Services.
- TenantBudget: a money cap per tenant and period.
- GlobalBudget: a money cap across all tenants per period, checked in addition to the tenant budget.
- BudgetReservation: RESERVED → SETTLED / RELEASED / EXPIRED, atomic under concurrency, with a price snapshot taken at reservation.
- Tenant operating state, set by the operator: ACTIVE or PAUSED. A paused tenant blocks new work through the Action Broker.
- Circuit-breaker thresholds as limits (steps, retries, cost per workflow), definition only.
- Cost report per tenant and period, produced from the ledger.

## Out of scope
- Plans, packages, subscriptions, trials, seats, invoices, payment processing and tax (removed by ADR-0030).
- Charging clients. If the operator bills clients, that happens outside Presence OS; the cost report is the input.
- AI Compute Units. Reservations are in money.
- Model choice per tenant (R1-012) and property rules (R1-011), which consume this task's mechanisms.

## API / contract changes
- Limit check and usage-record interfaces.
- Reservation interface: reserve, settle(actual), release.
- `budget-reservation.schema.json`: add the price-snapshot reference and the budget scope (tenant, global). Changes are reviewed.

## Data / migration
- Tables: TenantLimit (versioned), UsageRecord, TenantBudget, GlobalBudget, BudgetReservation, tenant operating state. Tenant-scoped ones under RLS; GlobalBudget is platform-level.
- The usage ledger is append-only at the database privilege level.
- Reservation atomicity is enforced by the database (constraint or locked balance row), not by application pre-checks.
- Reverse migrations tested.

## Security / privacy threat notes
- Race: concurrent reservations exceeding the balance.
- Limit reached mid-task (E-009): checkpoint and stop, no uncontrolled overage.
- Price change after reservation (E-053): snapshot at reservation, settle actual.
- One client's activity exhausting the global budget and stopping every other client (E-064): tenant budgets are checked first, and the global budget has an alert threshold below its cap.
- A client reading another tenant's usage or cost.
- An operator limit change must not become tenant business authority (E-060).

## Observability
- Audit: limit revision change, budget change, tenant pause/resume, reservation lifecycle, manual corrections.
- Metrics: reservations by state, expired reservations, denials by limit key, budget thresholds reached per tenant and globally.

## Acceptance criteria
- versioned limits;
- usage ledger;
- atomic budget reservation and settlement;
- *(derived)* N concurrent reservations never exceed the available balance;
- *(derived)* unused reservation is refunded on settle; an abandoned reservation expires and is released;
- a paused tenant blocks new work through the Action Broker;
- a reservation that would exceed either the tenant budget or the global budget is denied;
- a per-tenant cost report for a period can be produced from the ledger alone;
- a client role cannot change any limit or budget.

## Tests
- Concurrency: parallel reserve calls against a small balance.
- Lifecycle: reserve → settle lower than reserved → refund; reserve → release; reserve → expire.
- Limit revision: a change takes effect for new checks, history unchanged.
- Pause: paused tenant denied at the Action Broker; resume restores.
- Tenant budget and global budget each deny independently.
- Cross-tenant RLS suite on every new table; ledger UPDATE/DELETE rejected.
- Price snapshot: price changes between reserve and settle.

## Rollback / failure recovery
Checks fail closed. Reservations have an expiry so a crashed worker cannot hold budget forever. Ledger corrections are compensating entries, never edits. Reverse migrations tested before data exists; forward-only afterwards.

## Cost/resource budget
Limit checks sit on hot paths: bound query count and consider short-lived caching keyed by tenant and limit revision (E-044 rules apply).

## Documentation updates
- `docs/commercial/plans-entitlements-billing.md` (limit key catalogue).
- `docs/architecture/cost-resource-governance.md`.
- Contract schema.

## Open decisions
- **Decision required:** initial limit keys and default budgets.
- Decided (owner, 2026-11-15): budgets, reservations and the ledger are in US dollars. The console shows a rupee amount beside each figure at an operator-set rate, for reading only; no check uses it. Starting caps are in the decision register.
- **Decided (ADR-0033):** reserved actions not yet started are cancelled and released; an action already executing finishes.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: the R1-003 limit and budget stubs are replaced by this implementation.
