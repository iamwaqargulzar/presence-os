# apps/core
Django core and control-plane modular monolith. Owns business modules and deterministic control logic. External side effects still go through the Action Broker; secrets through the Secrets Broker.

Current as of 2026-11-25 (R0-002): only the `presence_core` project package exists.
- `presence_core/settings.py`: every setting comes from the environment (see the root `.env.example`). PostgreSQL from `compose.yaml` since R0-002; one role for now, split into migration and runtime roles by R0-003.
- `presence_core/urls.py`: `GET /healthz` returns `{"status": "ok"}` and nothing else.
- `presence_core/observability.py`: request-ID middleware and JSON log formatter. A full OpenTelemetry setup is R0-006.

Run with `make dev-core`; test with `make test`. Setup: [developer bootstrap](../../docs/runbooks/developer-bootstrap.md).
