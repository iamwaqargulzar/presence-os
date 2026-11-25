# PrimeWorkerAdapter Contract

> Initial worker adapter contract — 2026-08-10.

## Purpose

Control Prime Agent as a replaceable development worker without making OpenHands or Presence depend on Prime's TUI.

Preferred transport: `prime-agent --mode rpc` with JSONL event stream. JSON mode may be used for one-shot observation. CLI process commands may manage daemon-backed sessions as a recovery/operator path.

## Required adapter operations

- `capabilities()`
- `start(run_spec)`
- `resume(session_id)`
- `send(message, mode=steer|follow_up)`
- `get_state()`
- `stream_events()`
- `get_usage()`
- `get_children()`
- `abort_current()`
- `stop_tree()`
- `collect_changed_files()`
- `collect_session_artifacts()`
- `terminate()`

## Startup handshake

Before assigning work, verify:
- exact Prime version;
- requested provider/model observed;
- reasoning/effort setting observed;
- session directory is isolated;
- current working directory is expected worktree;
- context files are the expected project controls;
- allowed tool/extension/skill set;
- autonomous limits;
- no stale retained child agents/schedules/heartbeats from another run.

Fail closed if version/capability does not match the run spec.

## Event normalization

Normalize Prime events into Presence development events:
- RUN_STARTED
- TURN_STARTED / TURN_FINISHED
- MODEL_MESSAGE
- TOOL_STARTED / TOOL_FINISHED
- COMPACTION_STARTED / FINISHED
- RETRY_STARTED / FINISHED
- CHILD_CREATED / CHILD_FINISHED
- USAGE_SNAPSHOT
- WORKER_IDLE
- WORKER_FAILED
- RUN_FINISHED

Keep raw sanitized event artifacts for debugging, but business logic consumes normalized events.

## Leases and duplicate prevention

Each task run has a unique immutable `development_run_id`. Controller holds a renewable lease for the task/worktree. A disconnected controller must recover the existing session by run metadata rather than blindly launching a duplicate.

Prime session ID and process group ID are recorded. `stop_tree()` must stop root + retained children + run-owned schedules/heartbeats and verify termination.

## Usage

Do not rely solely on TUI totals. Parse persisted session/event usage when available. Record parent and child usage separately and preserve provenance grade. Never replace unavailable values with zero.

## Security

- no production credentials/environment;
- restricted egress;
- dedicated untrusted worker environment;
- session/log redaction;
- no unrestricted management-network access;
- no unreviewed Prime packages/extensions/skills;
- no self-refinement for a pinned qualified profile.

## Result contract

A Prime response saying “done” is not success. Adapter returns worker status; controller independently verifies repository diff and configured gates before declaring task completion.
