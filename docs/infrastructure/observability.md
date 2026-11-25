# Observability

Use OpenTelemetry conventions as the instrumentation baseline. Logs must not contain secrets, raw authorization tokens, passwords or unnecessary personal data. Avoid observability sprawl: add a storage backend only when something needs it.

## Backends
Decided in ADR-0033: an OpenTelemetry Collector feeding Prometheus (metrics), Loki (logs) and Tempo (traces), viewed in Grafana, internal only. None is deployed yet (R0-006, [ADR-0038](../adrs/ADR-0038-audit-and-trace-correlation.md)). Until then:
- logs are one JSON object per line on standard output;
- traces use W3C Trace Context headers (`traceparent`), the OpenTelemetry default propagator, implemented in-house with no SDK;
- no metrics are exported.

Adding the OpenTelemetry SDK and Collector is a follow-up once the first backend runs. Sampling is then set at the Collector (start: 10% of traces, 100% of error traces).

## Correlation
| ID | Set by |
|---|---|
| `request_id` | `X-Request-ID` header if it is a short plain token, otherwise new (web proxy and core middleware) |
| `trace_id` | incoming valid `traceparent`, otherwise new; the web proxy forwards it to the core |
| `tenant_id` | `tenant_context()` |
| `profile_id`, `workflow_id`, `task_id`, `action_id` | `presence_core.observability.correlate(...)` in the code that knows them |

Also to correlate later: skill/version, connector/provider, model/harness/reasoning profile.

`correlate()` keeps the IDs for the current request or job. Every JSON log line and every audit event in the block carries them. Both apps return `X-Request-ID` and `traceparent` response headers. The worker hop arrives with the worker (`apps/worker` has no code yet).

## Redaction
`presence_core.observability.redact()` runs on every log line (message, fields and exception text) and every audit payload. It replaces with `[REDACTED]`:
- values under keys that name a password, secret, token, authorization, cookie, API key, credential, private key, session or OTP;
- bearer and basic credentials, JWTs, provider API keys (`sk-…`), GitHub, Slack and AWS key formats, private-key blocks, `key=value` credentials, cookie headers and email addresses, anywhere in text.

Known over-redaction: any key containing `token` (for example `tokens_used`) is redacted; rename such fields (`token_count`) rather than weakening the rule.

## Health signals
- `redactions`: count added to a log line when something sensitive was removed. A rising count means code is logging what it should not.
- `audit_write_failed` (ERROR): an audit append failed and its operation rolled back.
- `rls_denied` (WARNING): the database refused a cross-tenant access.
- Telemetry export failures: none yet, since nothing is exported.

## Baseline tenant-scoped queries
Tenant audit, as the runtime role (RLS limits it to the tenant in context):
```sql
-- inside tenant_context(tenant_id)
SELECT occurred_at, action, result, actor, request_id
FROM audit.tenant_event ORDER BY occurred_at DESC LIMIT 100;
```
Logs (Loki, once deployed), always filtered by tenant:
```
{app="presence-core"} | json | tenant_id="<tenant uuid>"
{app="presence-core"} | json | msg="audit_write_failed"
```
Operator views that join tenants must never be shared with a tenant.

## Metrics to add with their subsystems
API latency/error; workflow queue/backlog; action state/failure; connection health; tenant concurrency; GPU utilization/queue; browser queue; provider rate limits; cache hit; token/media cost; RLS/auth failures; domain/certificate state; backup/restore health.
