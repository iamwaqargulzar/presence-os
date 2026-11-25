# R0-006 — Audit + Observability Foundation

> **Spec revision:** 2 — 2026-11-10. Expanded to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). Every revision 1 requirement is retained. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## Goal
Create structured audit events and OpenTelemetry correlation.

## Why now
"Evidence before claims" is a constitutional rule. Authorization, delegation, the Action Broker and the development controller all need an audit path and correlated traces from their first line of code.

## Context / linked docs / ADRs
- [Audit ledger](../../docs/security/audit-ledger.md)
- [Observability](../../docs/infrastructure/observability.md)
- [Privacy and data governance](../../docs/compliance/privacy-and-data-governance.md)
- [Model, harness and execution profile registry](../../docs/ai/model-harness-registry.md)
- [Re-audit edge case E-036](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0004 (RLS)

## Depends on
- R0-003.
- R0-004 and R0-005 for the representative login, profile and workflow events *(derived)*. If those merge later, their events are wired in as a follow-up within this task's acceptance.

## Invariants
- audit is append-oriented: the runtime role cannot update or delete audit records;
- no secrets, raw authorization tokens, passwords or unnecessary personal data in logs, traces or audit;
- a tenant can never read another tenant's audit or telemetry;
- avoid observability sprawl: add storage backends only when needed.

## In scope
- AuditEvent structure and append path covering: actor, tenant/profile, authority source, managed-operator context, action/task/workflow, request and artifact references, target, policy decision, connection, model/harness, time, result, rollback/revocation, break-glass reason, trace IDs. Fields not yet produced are reserved.
- OpenTelemetry instrumentation in `apps/core`, `apps/web` server side and `apps/worker`.
- Correlation IDs: request, trace, tenant, profile, workflow, task, action.
- Redaction layer for logs and audit payloads.
- Representative events: login, profile switch, workflow start/complete.
- A baseline set of queries or dashboards scoped by tenant.

## Out of scope
- Tamper-evident hashing or external audit anchoring.
- Customer-facing audit UI.
- Full metric catalogue for subsystems not built yet (GPU, browser, connectors, domains).
- Alerting and on-call rules.

## API / contract changes
- Internal audit-append interface used by all modules. This is a long-lived contract.
- Reserved attribution fields: model, harness, reasoning profile, execution profile ID, development run ID.
- No tenant-facing read API in R0.

## Data / migration
- Audit table(s), tenant-scoped under RLS, with a separate path for platform-level events that have no tenant.
- Database privileges: runtime role may INSERT and SELECT, not UPDATE or DELETE.
- Retention is policy-driven and not finalised in R0; do not build deletion here.

## Security / privacy threat notes
- Credential or token written to logs (E-036): redaction tests with seeded patterns.
- Audit record forged or altered by application code: privilege separation at the database.
- Telemetry backend exposing cross-tenant data to an operator view that is later shared with tenants.
- Audit failure silently dropping events: an action whose audit write fails must fail, not proceed unaudited.

## Observability
This task is the observability baseline. Additionally measure its own health: audit write failures, redaction hits, telemetry export failures.

## Acceptance criteria
- request/trace/tenant/profile/task/action IDs supported;
- redaction tests;
- audit append path;
- representative login/profile/workflow events;
- dashboards/queries can distinguish tenant without exposing another tenant's data;
- model/harness attribution fields reserved;
- *(derived)* runtime role cannot UPDATE or DELETE audit rows;
- *(derived)* an operation whose audit append fails does not commit.

## Tests
- Redaction: seeded bearer token, password, cookie and API-key patterns never appear in stored output.
- Append-only: UPDATE and DELETE by the runtime role are rejected.
- Cross-tenant audit read denied.
- Trace propagation across web → core → worker for one request.
- Audit-write failure rolls back the surrounding operation.

## Rollback / failure recovery
Reverse migration tested while the table is empty; once events exist, changes are forward-only and additive. Telemetry export failure must not take the application down.

## Cost/resource budget
Telemetry and audit storage grow with traffic. Set sampling for traces and record expected audit row size. No paid observability service is assumed.

## Documentation updates
- `docs/security/audit-ledger.md` (event catalogue, field definitions).
- `docs/infrastructure/observability.md` (chosen backends, correlation conventions).
- "How to emit an audit event" guide.

## Open decisions
- **Decided (ADR-0033):** OpenTelemetry Collector feeding Prometheus, Loki and Tempo, viewed in Grafana; internal only.
- **Decided (ADR-0033):** an append-only table in a separate PostgreSQL schema, readable only by the operator role.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: redaction test evidence is stored for the R0-010 secrets/redaction review.
