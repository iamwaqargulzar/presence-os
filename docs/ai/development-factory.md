# Autonomous Development Factory

> **Presence OS engineering source of truth**
>
> Baseline date: **2026-08-10** (Asia/Karachi project context).
> Models, harnesses and controllers are replaceable. Current vendor capabilities must be revalidated before implementation/update.

## Goal

Hands-free, budget-conscious development with deterministic gates and human control of production.

## Permanent architecture

Human goal
→ authoritative spec/task contract
→ DevelopmentController
→ task DAG / lease / isolated worktree
→ HarnessAdapter worker
→ deterministic gates
→ repair/review
→ integration candidate
→ staging
→ Release Controller / human production boundary

`DevelopmentRunProfile = DevelopmentController × ExecutionProfile × SandboxProfile × GatePolicy`

`ExecutionProfile = Model × Harness × ReasoningConfiguration × ContextStrategy`

## Initial implementations

- **DevelopmentController:** OpenHands-backed controller, initially CANARY on real R0 work.
- **Primary worker HarnessAdapter:** Prime Agent through Prime RPC/process adapter.
- **Fallback/challenger workers:** Codex, OpenCode, Oh My Pi, ReasoniX as retained qualified/candidate paths where useful.

Do not spend another broad synthetic harness campaign before implementation. Real R0/R1 tasks become PresenceBench evidence.

## Controller rule

Ordinary orchestration is deterministic and should make **zero LLM calls**:
- dependency readiness;
- scheduling;
- worktree allocation;
- process lifecycle;
- leases/timeouts;
- CI/gates;
- result state transitions;
- telemetry aggregation.

LLM supervisor reasoning is an explicit escalation with a separate budget/usage ID.

## Prime worker rule

Prime receives a bounded task contract and works until local gates pass or limits/blocker occur. Prime may use child agents only when the task's ExecutionProfile permits them; total-tree usage counts toward the run budget.

Prime's own quality gates are not final proof. Controller independently verifies in a clean context.

## Isolation

Each coding task gets:
- isolated Git worktree;
- isolated app/container/sandbox;
- temp database/ports/logs/browser when relevant;
- no production secrets;
- no management-LAN access;
- controlled egress;
- deterministic gate commands.

Prime's worker/kernel and OpenHands headless operation are not treated as the security boundary. External isolation is mandatory.

## Reproducibility

Every DevelopmentRun pins:
- task/spec hash;
- start commit;
- controller/harness/model/reasoning/context versions;
- sandbox and gate profiles;
- allowed paths/tools/network;
- budgets.

Prime `/refine` or similar self-modifying harness state is off for a pinned qualified profile unless separately reviewed/versioned.

## Autonomy ceiling

Initial target remains **Level 4**: spec → code → test → review → repair → merge candidate → staging automatically.

Production remains separately authorized initially.
