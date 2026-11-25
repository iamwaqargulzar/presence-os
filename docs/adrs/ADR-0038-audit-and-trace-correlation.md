# ADR-0038 — Audit Schema, Redaction and Trace Correlation
Status: Accepted (2026-11-25). Made during R0-006 under the owner's delegation in ADR-0032 and ADR-0033. Independent review of the audit grants is pending.

## Context
R0-006 needs an append-only, tenant-scoped audit log, redaction of secrets and personal data in logs and audit payloads, and correlation IDs across the web and core apps. ADR-0033 picks the OpenTelemetry Collector, Prometheus, Loki, Tempo and Grafana, but none is deployed yet, and the worker has no code. ADR-0033 also says audit is readable only by the operator role, while the R0-006 spec lets the runtime role insert and select. By the authority order in `AGENTS.md`, the task contract wins; this ADR records how the two are reconciled.

## Decision
1. **Schema `audit`, two tables.** `audit.tenant_event` holds events about one tenant, with FORCE RLS like every tenant table (ADR-0036); `presence_app` may INSERT and SELECT under RLS. `audit.platform_event` holds events with no tenant; `presence_app` may INSERT only. Neither grants UPDATE, DELETE or TRUNCATE. Tests prove each is rejected.
2. **Readers.** A tenant's own events are readable in its tenant context (spec). Platform events are readable only by the owner role until an operator audit-reader role exists (ADR-0033).
3. **One append path.** `presence_core.audit.append_audit(AuditEvent)` writes in the caller's transaction and refuses to run outside one. A failed write logs `audit_write_failed` and raises, so the operation rolls back rather than proceeding unaudited. The tenant is always named explicitly, never taken from context.
4. **Redaction in one place.** `observability.redact()` runs on every JSON log line and every audit row: sensitive keys and credential or email patterns become `[REDACTED]`; log lines count hits in `redactions`.
5. **In-house W3C Trace Context.** Both apps read a valid `traceparent`, otherwise start a trace, and return one; the web proxy forwards it to the core. No OpenTelemetry SDK or Collector until a backend runs, so no new dependency.
6. **Correlation context.** `observability.correlate()` holds request, trace, tenant, profile, workflow, task and action IDs for the current request or job; `tenant_context()` adds the tenant.

## Alternatives considered
- One audit table with nullable `tenant_id`: an RLS policy would need a special case for platform rows, and the runtime role could read them. Rejected.
- Database triggers to block UPDATE/DELETE: grants already do it, and the owner can bypass triggers anyway. Rejected.
- OpenTelemetry SDK now: two dependencies and exporter configuration with nowhere to export to. Deferred.
- Django ORM model for audit: the ORM invites `update()` and `delete()` calls that would only fail at run time. Raw insert instead.

## Consequences
- Login, profile and workflow events are named in the catalogue (`docs/security/audit-ledger.md`) but wired by R0-004 and R0-005.
- Any key containing `token` is redacted, including harmless ones such as `tokens_used`; such fields must be renamed.
- Spans are not exported; a trace ID joins logs only.

## Security impact
Audit rows cannot be changed or removed by the runtime role. Tenant audit isolation is enforced by the database, not by application filters. Platform events, which may concern unknown users, are not readable by the runtime role. Redaction is a safety net; callers must still not log secrets.

## Cost
None. No new service or dependency.

## Migration/rollback
Migration `presence_core/0002_audit` creates the schema; its reverse drops it with all audit rows. Rolling back in production would lose audit history, so it is for development only.

## Supersedes
None. Refines ADR-0033 on audit readers.

## Superseded by
None.
