# How to Write a Workflow

Current as of 2026-11-25. For later tasks that add workflows. The reference is `ReferenceWorkflow` in `apps/worker/presence_worker/workflows.py`. Rules: [Durable workflows and Temporal](workflows-and-temporal.md).

## Steps
1. **Contracts.** Add frozen dataclasses for inputs and outputs to `contracts.py`. Every workflow input starts with `ctx: TenantContext`. Inputs and outputs stay small: put large data in the artifact store and pass an `ArtifactRef`.
2. **Activities.** Add them to `activities.py` (or a new module beside it) with `@activity.defn(name="...")`. Each activity:
   - starts with `with tenant_scope(inp.ctx):`, so logs and (after R0-003) the database use the workflow's tenant;
   - is idempotent: a side effect takes an idempotency key derived from the workflow ID, never a random value;
   - checkpoints expensive work: store the result, record a marker, and return the stored reference on a retry;
   - calls `revalidate(ctx, action)` before any external side effect, because time has passed since the human decided.
3. **Workflow.** Add it to `workflows.py` with `@workflow.defn(name="...")`. Call activities by name with `result_type=`. Do not import activities, `os`, `time`, `random`, `uuid` or I/O; use `workflow.now()`, `workflow.uuid4()` and `workflow.wait_condition`. Give every activity a timeout and a retry policy. Use `WAIT_CANCELLATION_COMPLETED` when an activity must clean up on cancel.
4. **Signals.** A signal is a message, not a permission. Record who sent it, accept only the first decision, and check authority in an activity before acting.
5. **Start.** Build the workflow ID with `client.workflow_id(kind, ctx, business_key)` and start it like `client.start_reference`: conflict policy "use existing", reuse policy "reject duplicate".
6. **Register.** Add the workflow and activities to the `Worker` in `__main__.py`.
7. **Tests.**
   - Unit: call activities directly; check idempotency, the checkpoint and tenant separation.
   - Integration (`test_integration.py`, needs `make services-up`): happy path, timeout, cancel during wait and during an activity, retry keeps the tenant, worker kill and restart.
   - Replay: record a history (`PRESENCE_RECORD_HISTORY=1`), commit it under `tests/histories/`, and replay it in the unit tests.

## Changing a workflow that may be running
Read the versioning policy in [Durable workflows and Temporal](workflows-and-temporal.md#versioning-and-worker-deployment). Never edit the command order of a released workflow without `workflow.patched(...)` or a new workflow type, and keep the old replay history passing.
