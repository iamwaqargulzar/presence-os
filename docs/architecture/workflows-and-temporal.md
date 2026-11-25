# Durable Workflows and Temporal

Current as of 2026-11-25. Concrete conventions added by R0-005 ([ADR-0036](../adrs/ADR-0036-temporal-foundation.md)); how-to: [How to write a workflow](how-to-write-a-workflow.md).

## Principle

Agents do bounded work. Temporal (or the durable workflow layer) owns long waits, retries, schedules and recoverability.

Use workflows for:
- approvals/waits;
- scheduled publication;
- domain verification;
- multi-stage research;
- onboarding;
- campaigns;
- long-running connection repair;
- deployment;
- offboarding;
- human-in-the-loop tasks.

## Workflow design

- Activity/tool calls must be idempotent.
- Checkpoint meaningful expensive stages.
- Retry from the failed stage, not from the beginning.
- Store large model/tool/research/media payloads in object storage/Postgres; workflow history carries artifact references.
- Use deterministic workflow code.
- Give long-lived workflows explicit versioning/upgrade policy.
- Support cancellation/revocation.
- Revalidate authorization and entitlements before delayed side effects.

## Conventions (R0-005)

| Topic | Rule |
|---|---|
| Code | `apps/worker/presence_worker`: `workflows.py` (deterministic, never imports activities), `activities.py`, `contracts.py`, `client.py`. |
| Task queue | `presence-default` until a workload needs its own queue. |
| Workflow ID | `{kind}/{tenant_id}/{business_key}`; repeated start returns the existing run; a finished ID cannot be reused. |
| Context | Every input carries `TenantContext` (tenant, profile, trace ID). Activities take the tenant from their input, never from the worker, so a retry on another worker keeps the same tenant. |
| Logs | Each activity logs workflow ID, run ID, activity, attempt, tenant, profile and trace ID. |
| Payloads | One payload at most 64 KiB, enforced by the shared data converter. Larger data goes to the artifact store; history carries `ArtifactRef` (sha256, size). |
| Idempotency | A side effect uses a key derived from the workflow ID (for example `{workflow_id}/apply`) and records it once. |
| Checkpoints | An expensive stage stores its result and a marker keyed by workflow ID; a retry returns the stored reference. |
| Human waits | `wait_condition` with a timeout; the first decision wins; a signal carries no authority (ADR-0003); authority is rechecked before the side effect. |
| Cancellation | Workflows let cancellation propagate; activities that must clean up use `WAIT_CANCELLATION_COMPLETED` and heartbeat. |
| Local service | `compose.yaml` runs the Temporal development server on `127.0.0.1` only. Production: newest stable server with its own PostgreSQL database (ADR-0033, R0-009). |

## Versioning and worker deployment

A running workflow is replayed by whatever worker picks it up, so workflow code must stay compatible with histories already recorded.

1. A change that does not alter the order or kind of commands (activities, timers, signals awaited) may ship directly.
2. A change that alters them must use `workflow.patched("<change-id>")` around the new path, or ship as a new workflow type (`Reference` → `ReferenceV2`) while the old type drains. Remove a patch only after no run that started before it remains.
3. Every workflow has a recorded history in `apps/worker/presence_worker/tests/histories/`. The replay test must pass before a worker is deployed (E-081). A new incompatible version adds a new history file; old files stay until their runs are gone.
4. Deploy: start new workers, check they poll, then stop old workers with a graceful shutdown. Roll back by redeploying the previous worker image; histories created by the new version must still replay on it, which rule 2 guarantees.
5. Temporal Worker Versioning (build IDs) is a capability to adopt when deployments need it, not a reason to deploy Kubernetes early. Rollout automation is out of scope for R0.

## Outbox design (not built yet)

Business code that must both change tenant data and start a workflow or publish an event writes an `outbox` row in the same database transaction. Columns: `id`, `tenant_id` (RLS, R0-003), `kind`, `payload` (small JSON, references only), `idempotency_key` (unique per tenant), `created_at`, `dispatched_at`. A dispatcher reads undispatched rows with `FOR UPDATE SKIP LOCKED`, starts the workflow using the idempotency key as business key (so a repeated dispatch returns the same run) and sets `dispatched_at`. The table is built by the first task that needs it, after R0-003, because it must be under row-level security.

## Eventing

Start with transaction outbox + internal event handling where needed. Do not introduce Kafka until event volume/independent consumers justify it.
