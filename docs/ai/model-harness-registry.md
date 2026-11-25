# Model, Harness, Controller and Execution Profile Registry

> **Presence OS engineering source of truth**
>
> Baseline date: **2026-08-10**.

## Key abstractions

`ExecutionProfile = Model × Harness × ReasoningConfiguration × ContextStrategy`

For autonomous development:

`DevelopmentRunProfile = DevelopmentController × ExecutionProfile × SandboxProfile × GatePolicy`

Controller and harness are deliberately separate. OpenHands may be the project-control runtime while Prime is the worker harness.

## Current initial status

### Development controller
- **OpenHands-backed controller — CANARY/SELECTED** for R0. Validate overhead/recovery on real R0 tasks, not a new synthetic campaign.
- Direct Presence controller → Prime RPC remains fallback so OpenHands is not a single point of project progress.

### Worker harnesses
- **Prime Agent — ACTIVE_CHAMPION** for general implementation based on the 2026-08-08 controlled Presence benchmark (single-trial evidence, not a permanent monopoly).
- Codex — retained OpenAI-native/reference fallback.
- Oh My Pi — retained challenger/fallback; previous run invalid due operator instrumentation.
- OpenCode — retained challenger/fallback; previous run insufficient.
- ReasoniX — retained DeepSeek specialist/orchestrator candidate; strict single-agent run was disqualified due worker activity.

- **Claude Code through the Claude Agent SDK — CANDIDATE** (ADR-0030). Runs the official harness on the Worker VM with the operator's subscription, for operator-started or approved runs only. Whether it replaces Prime as primary worker is an open decision.

### Models
- A frontier profile for planning, architecture, security-sensitive work and review.
- A low-cost API profile (intended: DeepSeek) for high-volume, machine-checkable work. Exact model and price are data and must be revalidated.

### Credential class
Every ExecutionProfile is `OPERATOR_SUBSCRIPTION` or `API`. Unattended and scheduled runs resolve `API` profiles only.

No harness/model/controller is embedded into product business logic.

## HarnessAdapter contract

Conceptual operations:
- capabilities()
- start_run()
- resume_run()
- cancel_run()
- set_model()
- set_reasoning_level()
- set_workspace()
- set_task_contract()
- set_allowed_tools()
- set_environment()
- stream_events()
- get_usage()
- get_cache_usage()
- get_cost()
- get_changed_files()
- get_session_id()
- terminate_tree()

## DevelopmentController contract

- register_task_graph()
- ready_tasks()
- acquire_lease()
- create_workspace()
- launch_worker()
- monitor_worker()
- execute_gate_policy()
- request_review()
- integrate_candidate()
- recover_orphaned_run()
- cancel_run()
- aggregate_usage()

Deterministic methods above do not require an LLM.

## Telemetry provenance

Every usage field carries source/reliability where possible:
A provider exact; B provider usage persisted by harness; C harness calculation; D derived estimate; X unavailable.

Never merge provider prompt-cache usage with local harness caches.

## Reasoning level

Reasoning/thinking configuration remains a benchmarked routing dimension. Use progressive escalation; exact labels and support are provider-specific and versioned.
