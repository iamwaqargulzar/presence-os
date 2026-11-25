# Observability

Use OpenTelemetry as the instrumentation baseline.

Correlate:
- request_id
- trace_id
- tenant_id/profile_id
- workflow_id
- task_id
- action_id
- skill/version
- connector/provider
- model/harness/reasoning profile where applicable.

Metrics:
- API latency/error;
- workflow queue/backlog;
- action state/failure;
- connection health;
- tenant concurrency;
- GPU utilization/queue;
- browser queue;
- provider rate limits;
- cache hit;
- token/media cost;
- RLS/auth failures;
- domain/certificate state;
- backup/restore health.

Logs must not contain secrets, raw authorization tokens, passwords or unnecessary PII.

Prometheus/Grafana/Loki are acceptable initial choices when needed; avoid observability sprawl.
