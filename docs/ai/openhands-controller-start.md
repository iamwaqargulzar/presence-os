# OpenHands — Presence OS Development Controller Start

You are operating the Presence OS development control plane.

1. Read [`00_START_HERE.md`](../../00_START_HERE.md) completely.
2. Read `docs/PROJECT_REAUDIT_2026-08-10.md`.
3. Read `docs/ai/openhands-prime-development-factory.md` and `docs/ai/prime-worker-adapter.md`.
4. Read `docs/security/autonomous-development-security.md`.
5. Inspect repository state before creating/changing code.
6. Follow task contracts in `specs/` and dependency order.

## Role

Use OpenHands primarily as **DevelopmentController infrastructure**, not as a second always-on coding brain. Ordinary task DAG evaluation, worktree allocation, process supervision, leases, CI/gates and telemetry aggregation should be deterministic and spend zero LLM tokens.

Workers are Claude Code through the Claude Agent SDK (primary for R0/R1) and **Prime Agent** (qualified second worker), per [ADR-0033](../adrs/ADR-0033-technical-defaults-for-r0-and-r1.md). A run on the operator's subscription needs a recorded operator start or approval. Prime Agent is invoked through the Presence-owned PrimeWorkerAdapter/RPC/process contract. Do not assume native ACP support is required.

## Safety

- no production credentials;
- no Proxmox/management-LAN access;
- development worker sandbox only;
- do not expose unrestricted host Docker socket to agent-controlled code;
- do not let workers edit the authoritative task/spec/hidden tests for their run;
- controller independently verifies gates;
- production release is separately authorized.

## First implementation objective

If the repository is still specification-only, begin with `specs/R0/README.md`. Execute R0 in dependency order. Build the minimal controller/Prime adapter in R0-011 after its prerequisites; do not delay all R0 coding until a perfect factory exists.

## Token rule

Record controller usage separately from Prime parent/children/reviewer. If controller reasoning is not necessary, it must be zero. Never silently duplicate Prime's planning with another LLM.
