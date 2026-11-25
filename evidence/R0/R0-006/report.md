# Implementation Report — R0-006 Audit and Observability

Written 2026-11-25. Spec: [R0-006](../../../specs/R0/R0-006-audit-observability.md). Decisions: [ADR-0038](../../../docs/adrs/ADR-0038-audit-and-trace-correlation.md).

- Starting commit: `219e776` (R0-003 branch head), which was still the tip of `origin/feat/R0-003-postgres-rls` at commit time.
- Resulting commit: the head of branch `feat/R0-006-audit-observability`. It contains this report, so it cannot name its own hash.
- Execution profile: side session started by the operator's interactive session; owner away; no controller yet (R0-011).
- Harness: Claude Code, desktop app. Model: Claude Opus 5.5 (`claude-opus-5-5`). Reasoning: default for the session.
- Task/spec hash: sha256 `d4107100c8b57bf6d389f8ed659ae04784e873e6957c4d0374c8a12664d0bd17` of `specs/R0/R0-006-audit-observability.md`.
- Changed files: `apps/core/presence_core/{audit.py (new), observability.py, tenancy.py, tests.py, migrations/0002_audit.py (new)}`, `apps/web/{proxy.ts, test/smoke.test.js}`, `docs/security/audit-ledger.md`, `docs/infrastructure/observability.md`, ADR-0038, `docs/DECISION_REGISTER.md`, `CHANGELOG.md`, generated exports.
- Migrations: `presence_core/0002_audit` creates schema `audit`, tables `tenant_event` (FORCE RLS) and `platform_event`, indexes and grants. Reverse drops the schema; tested by the existing `migrate presence_core zero` integration test and by hand (0002 → 0001 → 0002) on the dev database.
- Rollback: revert the branch and run the reverse migration while audit tables are empty. Once events exist, changes are forward-only (spec).

## Dependencies (review)
None added. Tracing is in-house W3C Trace Context; the OpenTelemetry SDK and Collector wait until a backend runs (ADR-0038).

## Tests
- `make check` passes: format, lint, mypy strict, `tsc`, Django unit tests (redaction and correlation included), contract schemas, web build and 3 web smoke tests. The smoke tests were run with `PRESENCE_SMOKE_PORT=3197`, because another session's `next start` held port 3199 (see Known limitations).
- `make test-integration` passes: 18 tests as the runtime role against PostgreSQL 18.7, including 6 audit tests.
- `tools/gate_selftest.sh` passes: every gate rejects its seeded violation.
- Mutation check: granting UPDATE and DELETE on the audit tables to `presence_app` made the append-only tests fail, so they catch the regression. The grant was then removed.
- Output: [test-output.txt](test-output.txt).

| Spec test | Where |
|---|---|
| Seeded bearer token, password, cookie and API-key patterns never stored | `RedactionTests`, `AuditTests` (checks the stored row and log output) |
| UPDATE and DELETE by the runtime role rejected | `AuditTests` (both tables, plus TRUNCATE) |
| Cross-tenant audit read denied | `AuditTests` |
| Trace propagation web → core → worker | web → core: smoke test and `CorrelationTests`. Worker hop not built: `apps/worker` has no code. |
| Audit-write failure rolls back the operation | `AuditTests` |

## Security checks
- `make scan-secrets`: gitleaks found no leaks. Seeded secrets in tests are built at run time from fragments, and the evidence files contain none of them ([redaction-sample.txt](redaction-sample.txt)).
- Runtime role: INSERT and SELECT (tenant table, under RLS), INSERT only (platform table); no UPDATE, DELETE or TRUNCATE.
- Tenant is never taken from correlation context into an audit row; RLS rejects a mismatched tenant.
- Incoming `traceparent` and `X-Request-ID` are validated; invalid ones are replaced, so they cannot forge log lines.
- `append_audit` refuses to run outside a transaction; on failure it logs `audit_write_failed` without the event and re-raises.

## Acceptance criteria
| Criterion | Result |
|---|---|
| request/trace/tenant/profile/task/action IDs supported | yes, `correlate()`; tenant set by `tenant_context()` |
| redaction tests | yes |
| audit append path | yes, `append_audit(AuditEvent)` |
| representative login/profile/workflow events | names and fields fixed in the catalogue; wiring follows when R0-004 and R0-005 merge (spec dependency note) |
| dashboards/queries distinguish tenant without exposing others | baseline tenant-scoped SQL and log queries in `docs/infrastructure/observability.md`; Grafana not deployed |
| model/harness attribution fields reserved | yes, five reserved fields |
| runtime role cannot UPDATE or DELETE audit rows | yes, tested |
| an operation whose audit append fails does not commit | yes, tested |

## Reviewer
No independent review yet. The audit grants are security-critical; the owner or a second worker should review migration `0002_audit` and `audit.py` before merge.

## Cost/tokens/cache
Not measured; the desktop session does not expose usage to the worker. No paid service used.

## Known limitations and follow-ups
- Wire login, logout, profile-switch and workflow events into R0-004 and R0-005.
- Worker trace hop when `apps/worker` gains code.
- OpenTelemetry SDK, Collector and telemetry-export-failure metric once a backend runs; Grafana dashboards.
- Operator audit-reader role so platform events are readable without the owner role.
- Any key containing `token` is redacted (over-redaction); rename such fields.
- The web smoke test defaults to port 3199. While another `next start` holds that port, plain `make check` fails; set `PRESENCE_SMOKE_PORT` to a free port.

## Docs updated
`docs/security/audit-ledger.md` (storage, fields, event catalogue, how to emit an event), `docs/infrastructure/observability.md` (backends, correlation, redaction, health signals, baseline queries), ADR-0038, `docs/DECISION_REGISTER.md`, `CHANGELOG.md`, generated exports.
