# OpenHands + Prime Agent Development Factory

> Authoritative development architecture — 2026-08-10.

## Decision

Use **OpenHands infrastructure/control-plane capabilities** as the initial development-controller implementation and **Prime Agent** as the primary coding worker. Keep both replaceable behind Presence-owned contracts.

Do not assume Prime must be a native OpenHands ACP agent. Initial integration is explicitly supported through a Presence-owned `PrimeWorkerAdapter` that launches/controls Prime using its process, JSON and RPC interfaces.

## Permanent abstraction

`DevelopmentRunProfile = DevelopmentController × ExecutionProfile × SandboxProfile × GatePolicy`

Where:
- `DevelopmentController` initially = OpenHands-backed controller;
- `ExecutionProfile` initially favors Prime Agent + qualified model/reasoning/context profile;
- `SandboxProfile` defines workspace/network/secret/resource isolation;
- `GatePolicy` defines deterministic and independent verification.

## Responsibilities

### OpenHands/control plane

Responsible for project-level lifecycle:
- task DAG / readiness;
- workspace/worktree allocation;
- launching/stopping worker processes;
- event/status collection;
- resource leases;
- CI/gate invocation;
- artifact/provenance aggregation;
- retries/recovery policy;
- integration/merge candidate workflow;
- human release boundary.

**Deterministic operations must not invoke an LLM by default.**

### Prime Agent worker

Responsible for bounded engineering reasoning:
- understand assigned task contract;
- inspect allowed repo context;
- implement;
- run local task gates;
- debug/repair;
- optionally use bounded child agents when task policy permits;
- return result + evidence.

Prime does not decide its own production release authority.

## Why this split

Prime has demonstrated strong single-agent completion and cache behavior on the existing Presence harness benchmark. OpenHands adds programmable agent/workspace/server orchestration. The combination should preserve Prime's worker efficiency while avoiding a second always-on reasoning loop.

## Controller AI policy

The OpenHands-backed controller has two modes:

1. **DETERMINISTIC** (default): zero controller LLM calls for task readiness, scheduling, worktree creation, process supervision, gate checks and state transitions.
2. **REASONING_ESCALATION**: optional bounded LLM use only for ambiguous decomposition, novel recovery or architecture questions that cannot be resolved by authoritative specs/rules.

All controller LLM usage has a distinct usage ID and budget. Never hide it inside worker cost.

## Task lifecycle

`PLANNED → READY → LEASED → WORKSPACE_READY → WORKER_RUNNING → VERIFYING → REVIEWING → INTEGRATING → MERGE_CANDIDATE → STAGING_READY`

Failure/interrupt states:
`BLOCKED`, `WORKER_FAILED`, `GATE_FAILED`, `REVIEW_FAILED`, `CONFLICT`, `TIMED_OUT`, `BUDGET_EXHAUSTED`, `CANCELLED`, `ORPHANED`.

Production release remains separately authorized.

## Task contract pinning

Each DevelopmentRun records:
- task/spec IDs;
- content hashes;
- authoritative ADR/constitution revision;
- start commit;
- allowed paths;
- allowed tools/network;
- selected ExecutionProfile revision;
- sandbox profile revision;
- gate policy revision;
- budget/time/turn limits.

Worker cannot silently mutate these controls. If a spec is wrong, stop and create a spec-change proposal/task.

## Parallelism

Two levels are allowed:
- project-level parallel tasks managed by controller;
- task-level Prime child agents managed by Prime.

Both consume the same tenant/project development resource budget. Enforce max root workers, max children, max depth, max total calls/tokens and affected-area conflict rules.

Serialize:
- schema migrations in the same data boundary;
- release manifest edits;
- high-conflict shared contracts;
- security policy migrations unless explicitly coordinated.

## Verification

Prime's own autonomous gates are useful but not authoritative completion evidence. Controller independently executes the gate set in a clean verification context.

Sensitive tasks additionally require an independent review profile. Protected tests/evals are not writable by implementation worker.

## Token/cost accounting

Every run separates:
- controller/orchestrator usage;
- Prime parent usage;
- Prime child/subagent usage;
- reviewer usage;
- external tools/build compute.

Capture fresh input, cache read, cache write, output, reasoning where available, model calls, tool calls, compactions, retries, wall time and actual/API-equivalent/subscription-capacity semantics separately.

Primary metric remains **verified useful work / total resource consumption**, not cache percentage alone.

## First-use policy

Do not spend a new synthetic benchmark campaign qualifying the controller. Instrument the first real R0 tasks. If controller overhead or reliability is poor, fall back to the same Presence DevelopmentController contract using direct Prime RPC without OpenHands. Product development must continue.

## Versioning

Pin OpenHands, Prime, adapters and model profile revisions for a development release train. Upgrade through canary tasks and rollback on regression.

Prime `/refine` or other self-modifying harness state is disabled for qualified production-development profiles unless a separate reviewed harness-state change is authorized and versioned.
