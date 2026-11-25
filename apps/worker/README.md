# apps/worker

Current as of 2026-11-25. Temporal worker for durable workflows (R0-005). Part of the root Python project (`pyproject.toml`).

- `presence_worker/workflows.py` — workflow definitions. Deterministic; never imports activities.
- `presence_worker/activities.py` — activities: idempotent, small typed inputs, large data by artifact reference.
- `presence_worker/contracts.py` — typed inputs and outputs shared by both.
- `presence_worker/client.py` — connection, payload limit, workflow ID convention, start helper.
- `python -m presence_worker` (or `make dev-worker`) runs a worker on the task queue `presence-default`.

Tests: `make test` runs unit and replay tests (no server). `make test-integration` starts Temporal from `compose.yaml` and runs the integration tests, including the worker-kill recovery test.

Rules and conventions: [Durable workflows and Temporal](../../docs/architecture/workflows-and-temporal.md) and [How to write a workflow](../../docs/architecture/how-to-write-a-workflow.md).

Untrusted generated code and risky parsing/browser activity must run under the documented isolation/network policies.
