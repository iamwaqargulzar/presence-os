# R0-011 — OpenHands Development Controller + Prime Worker Adapter

> **Spec revision:** 3 — 2026-11-14. Amended by [ADR-0030](../../docs/adrs/ADR-0030-operator-run-agency-deployment.md); the "ADR-0030 amendments" section overrides any conflicting text below it. Revision 2 (2026-11-10): Expanded to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). Every revision 1 requirement is retained. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## ADR-0030 amendments (revision 3)
**Added to scope**
- A second worker adapter, `ClaudeCodeWorkerAdapter`, implementing the same HarnessAdapter contract by driving the official Claude Code through the Claude Agent SDK. No OAuth token extraction, no header imitation, no TUI scraping. The "Out of scope" line about other adapters still applies to Codex, OpenCode, Oh My Pi and ReasoniX.
- **Operator start/approval gate:** a run on an `OPERATOR_SUBSCRIPTION` profile (R0-007) leaves READY only after a recorded operator start or approval. Scheduled and unattended runs use `API` profiles only.
- Minimal operator endpoints (no UI): submit task, approve/start, cancel, read run report. The mobile console that calls them is R2/R3 work.
- The adapter must not depend on how the provider bills Agent SDK usage: subscription limits and paid credit are both handled as usage data plus a "limit reached" terminal reason.

**Added acceptance criteria**
- the fixture task completes through `ClaudeCodeWorkerAdapter` with the same independent gate verification as Prime;
- a subscription-profile run without an operator start/approval record never reaches WORKER_RUNNING;
- hitting the subscription's rate limit ends the run as BUDGET_EXHAUSTED with the reason recorded, and the run can be resumed or rerouted to an `API` profile.

**Added tests**
- Gate: unattended trigger with a subscription profile is refused.
- Rate limit: simulated provider limit produces the correct terminal state.
- Both adapters pass the same adapter conformance suite using the fake harness.

**Open decisions added**
- **Decided (ADR-0033):** newest stable at implementation time, pinned exactly.
- **Decided (ADR-0033):** Claude Code through the Claude Agent SDK is primary; Prime Agent is the qualified second worker. The owner may reverse this.

## Goal
Build the minimal autonomous development control plane that can schedule bounded task contracts and execute Prime Agent as the primary worker without requiring controller LLM reasoning for ordinary lifecycle operations.

## Why now
R0/R1 are meant to be built largely by autonomous workers. Without a controller that leases tasks, pins specs and independently verifies gates, that work cannot be trusted or measured. It comes after its prerequisites so product work is not blocked waiting for a perfect factory.

## Context / linked docs / ADRs
- Edge cases added 2026-11-14 that this task must cover: E-061, E-065, E-066 ([register](../../docs/PROJECT_REAUDIT_2026-08-10.md)).
- [OpenHands + Prime development factory](../../docs/ai/openhands-prime-development-factory.md)
- [PrimeWorkerAdapter contract](../../docs/ai/prime-worker-adapter.md)
- [Model, harness and controller registry](../../docs/ai/model-harness-registry.md)
- [Autonomous development security](../../docs/security/autonomous-development-security.md)
- [Development cost routing](../../docs/ai/development-cost-routing.md)
- [Re-audit edge cases E-024 to E-033, E-039 to E-042](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- Contract: [development-run.schema.json](../../contracts/schemas/development-run.schema.json)
- [openhands-controller-start.md](../../docs/ai/openhands-controller-start.md), [PRIME_WORKER_TASK_TEMPLATE.md](../../templates/PRIME_WORKER_TASK_TEMPLATE.md)
- ADR-0025, ADR-0026, ADR-0027, ADR-0028

## Depends on
- R0-001 repository/toolchain
- R0-002 CI/environments
- R0-006 audit/observability
- R0-007 AI execution-profile/PresenceBench skeleton

## Invariants
- OpenHands and Prime are replaceable implementations, not business-domain dependencies.
- Prime integration uses a versioned Presence `PrimeWorkerAdapter` over RPC/process interfaces; do not assume native ACP.
- deterministic scheduling/worktree/gate/process operations make zero LLM calls by default.
- every run pins task/spec hash, start commit, controller/worker/model/sandbox/gate revisions.
- no production secrets or management-network access.
- a worker reporting "done" is not success; the controller verifies independently.
- a worker may not modify its task contract, protected tests or gate configuration.
- no TUI scraping.

## In scope
- DevelopmentRun entity and state machine: PLANNED → READY → LEASED → WORKSPACE_READY → WORKER_RUNNING → VERIFYING → REVIEWING → INTEGRATING → MERGE_CANDIDATE → STAGING_READY, with BLOCKED, WORKER_FAILED, GATE_FAILED, REVIEW_FAILED, CONFLICT, TIMED_OUT, BUDGET_EXHAUSTED, CANCELLED, ORPHANED.
- DevelopmentController implementation (OpenHands-backed) of: register_task_graph, ready_tasks, acquire_lease, create_workspace, launch_worker, monitor_worker, execute_gate_policy, request_review, integrate_candidate, recover_orphaned_run, cancel_run, aggregate_usage.
- Task graph read from `specs/` with dependency order.
- Renewable lease per task/worktree; isolated worktree allocation and cleanup.
- PrimeWorkerAdapter operations: capabilities, start, resume, send (steer/follow_up), get_state, stream_events, get_usage, get_children, abort_current, stop_tree, collect_changed_files, collect_session_artifacts, terminate.
- Startup handshake that fails closed on any mismatch.
- Event normalisation to the Presence development event set, persisted with redaction.
- Independent gate runner in a clean verification context.
- Separate usage records for controller, Prime parent, Prime children/reviewer and build/tool compute, with provenance grades.
- Direct-Prime fallback path behind the same DevelopmentController contract.
- Controller modes: DETERMINISTIC (default) and REASONING_ESCALATION (off unless budgeted).

## Out of scope
- automatic production deployment;
- unlimited parallel agents;
- native Prime ACP implementation unless separately justified;
- self-modifying/refining Prime harness state;
- sandbox, egress and supply-chain enforcement (R0-012; this task must run only in an environment that already has no production credentials);
- adapters for Codex, OpenCode, Oh My Pi or ReasoniX beyond the interface;
- an operator UI.

## API / contract changes
- `development-run.schema.json` refined to carry: spec content hash, authoritative ADR/constitution revision, allowed paths, allowed tools/network, execution/sandbox/gate profile revisions, limits, worker session ID, process group ID.
- New contract sketches if needed: TaskLease, GatePolicy, normalised development event.
- HarnessAdapter and DevelopmentController interfaces from R0-007 become implemented contracts.

## Data / migration
- Tables: DevelopmentRun, TaskLease, development events, usage records. Platform-level, not tenant-scoped; no tenant data is stored here.
- Raw sanitised event artifacts stored by reference outside the database.
- Reverse migrations tested.

## Security / privacy threat notes
- Duplicate worker after a network disconnect (E-027): single active lease, recover by run metadata.
- Runaway subagent tree (E-025) and surviving daemon (E-026): limits and verified `stop_tree`.
- Fabricated test results (E-039): independent gate run with recorded exit codes.
- Worker edits spec or tests (E-030, E-031): hash comparison against the pinned baseline.
- Credentials in session logs (E-036): redaction before persistence.
- Version drift (E-033) and self-refinement (E-032): exact-version handshake, refinement disabled.
- Repository and web content prompt-injecting the worker (E-035): only designated control files are trusted context.

## Observability
- Every state transition audited with run ID, task ID, spec hash and commit.
- Usage per actor class: fresh input, cache read, cache write, output, reasoning where available, model calls, tool calls, compactions, retries, wall time.
- Controller LLM usage has its own usage ID; in DETERMINISTIC mode it must be zero, and a non-zero value raises an alert (E-041).

## Acceptance criteria
- DevelopmentRun schema/entity/state machine;
- task lease prevents duplicate active worker for same task/worktree;
- isolated worktree allocation and cleanup;
- Prime RPC startup handshake verifies exact version/model/reasoning/cwd/session isolation;
- event stream normalized and persisted with redaction;
- parent + subagent usage attribution available when exposed;
- cancel/timeout stops root and run-owned child/session activity;
- independent gate runner verifies result after worker completion;
- controller usage and worker usage recorded separately;
- fallback path can operate Prime directly if OpenHands infrastructure is unavailable;
- integration test uses a tiny safe fixture repo, not production credentials;
- *(derived)* a run whose spec file changed after pinning is not accepted;
- *(derived)* a full lifecycle run in DETERMINISTIC mode records zero controller LLM calls.

## Tests
- State machine: valid and invalid transitions.
- Lease: two controllers contend for one task; exactly one worker starts.
- Reconnect: controller restart recovers the existing session and does not launch a duplicate.
- Handshake: wrong version, wrong model, wrong working directory and stale children each fail closed.
- Cancel and timeout: no process, child, schedule or heartbeat owned by the run survives.
- Gate independence: a worker that reports success with failing tests ends in GATE_FAILED.
- Spec/test tamper: a modified protected path ends the run as failed.
- Usage: unavailable values stored as unavailable; controller and worker totals separate.
- Fallback: the fixture task completes with OpenHands disabled.
- A fake harness adapter drives most tests so they are deterministic and spend no tokens.

## Rollback / failure recovery
Pinned OpenHands and Prime versions are kept so the previous pair can be restored. An orphaned run is recovered or terminated by `recover_orphaned_run`. If the controller proves unreliable, development continues through the direct-Prime path; Git and `specs/` remain the source of truth.

## Cost/resource budget
- Conservative initial maximum of root workers and children, raised only after clean integration evidence.
- Every run has limits for wall time, model calls, tokens, child count, child depth and retries; hitting one yields TIMED_OUT or BUDGET_EXHAUSTED.
- Integration tests with a real Prime worker use the cheapest qualified profile and a hard cap.

## Documentation updates
- `docs/ai/openhands-prime-development-factory.md`, `docs/ai/prime-worker-adapter.md` (observed behaviour versus documented).
- Pinned versions recorded in the repository.
- Operator guide: start, monitor, cancel and recover a run.

## Open decisions
- **Decided (ADR-0033):** newest stable at implementation time, pinned exactly.
- **Decided (ADR-0033):** newest stable at implementation time, pinned exactly (benchmark evidence used 0.7.1).
- **Decided (ADR-0033):** not used; the operator interface is the Presence console.
- **Decided (ADR-0033):** 2 root workers, each with at most 2 children.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: one real low-risk task has been run end to end through the controller with telemetry recorded, and independent review of the adapter's process-control code is recorded.
