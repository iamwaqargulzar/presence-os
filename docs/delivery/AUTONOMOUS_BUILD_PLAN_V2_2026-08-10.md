# Presence OS — Autonomous Build Plan v2

> Updated 2026-11-14 for ADR-0030 (operator-run, not sold; Claude Code worker adapter added beside Prime). Date of first version: 2026-08-10. This plan supersedes the older Codex-centric development handoff where it conflicts.

## Build objective

Use the specification package as executable engineering control: OpenHands-backed DevelopmentController schedules and supervises bounded work; Prime Agent is the default implementation worker; deterministic CI/security gates decide readiness; production authority remains separate.

The build is not “one agent builds everything in one conversation.” It is a durable task graph with bounded workers, checkpoints and independent verification.

## Development topology

`Owner → Git/specs → DevelopmentController(OpenHands) → PrimeWorkerAdapter → Prime Agent → model profile → isolated worktree/sandbox → gates/review → integration → staging → release authority`

### Default worker philosophy
- Prime Agent is the current implementation champion based on existing Presence evidence.
- Use the cheapest qualified model/reasoning profile that reliably completes the task class; the existing DeepSeek V4 Flash + Prime result is a useful starting implementation profile.
- Escalate architecture/security/recovery to stronger profiles only when task risk or evidence warrants it.
- Do not rerun broad synthetic harness comparisons; collect telemetry on useful project work.

## Stage A — Handoff/bootstrap integrity

Before code:
1. verify the package (done 2026-11-25: Git history now replaces `MANIFEST.sha256`);
2. read `00_START_HERE.md`, re-audit, Constitution, Decision Register and R0 README;
3. initialize Git if this package is being used as a new repository seed;
4. create protected branches/rules and CI credentials with least privilege;
5. pin initial OpenHands/Prime versions after installation/verification;
6. record development-controller and worker versions in the repo.

## Stage B — R0 Engineering Foundation

Recommended order with limited parallelism:

### Lane 1 — repo/CI
- R0-001 Repository and Toolchain
- R0-002 Local/CI Environments and Quality Gates

### Lane 2 — data/control substrate after R0-001
- R0-003 PostgreSQL Tenancy + RLS
- R0-004 Identity/Profile/Tenant Kernel
- R0-005 Temporal Foundation
- R0-006 Audit + Observability

### Lane 3 — AI/development factory after R0-001/002/006
- R0-007 AI Capability + Execution Profiles + PresenceBench
- R0-011 OpenHands DevelopmentController + PrimeWorkerAdapter
- R0-012 Autonomous Development Sandbox/Supply Chain

### Lane 4 — security/infrastructure
- R0-008 Fetch/File/Secrets boundaries
- R0-009 Proxmox/Network/Backup baseline

Then:
- R0-010 R0 Exit Audit

Do not force parallelism if tasks touch the same migration/security contracts. Keep max active coding workers low initially and raise only after clean integration evidence.

## Stage C — R1 Presence Kernel

Build in dependency order:
1. RBAC/delegation
2. Authorization Service
3. Action Broker
4. tenant limits, usage ledger and budgets
5. Hostname Registry
6. vanity/custom-domain foundations
7. Connection Broker
8. artifact/file ownership/versioning
9. Resource Governor
10. DigitalProperty/multi-property model
11. tenant Presence AI/model profiles/package AI entitlement
12. admin model-policy rollout/rollback
13. R1 E2E/security exit

R1 is the point where the product has a safe control kernel for multiple tenants, multiple hosted properties and per-tenant AI configuration.

## Stage D — R2 Presence Intelligence

Implement:
- conversation shell/director;
- Context Compiler;
- durable memory and canonical knowledge;
- research/Presence Scan;
- scoring/versioning;
- competitor and opportunity engine;
- Attention synthesis.

The tenant AI uses `TenantAIIdentity` and resolves an effective AIModelProfile per run/session. Memory remains in Presence stores and therefore survives model changes.

## Stage E — R3 Business Presence MVP

Deliver first commercial value:
- create/change website;
- multiple DigitalProperties subject to the tenant's limit;
- controlled supported custom-app runtime profiles;
- preview/deploy/health/rollback;
- custom domains;
- SEO/AEO/GEO basics;
- content/social/local basics;
- local image generation;
- action approvals and reporting.

Use R3 for real client work only after reliability, security, backup and usage accounting are proven. Nothing is sold (ADR-0030).

## Real-task telemetry loop

Every task automatically records:
- task/spec hash and start commit;
- controller/worker/model/reasoning/sandbox/gate revisions;
- controller LLM usage (expected zero for ordinary orchestration);
- Prime parent and child usage;
- cache read/write/fresh input/output/reasoning when exposed;
- model/tool calls, compactions, retries, wall time;
- test/review result and defects;
- changed files and final commit.

Use this data to adjust model routing while simultaneously building the product.

## Review ladder

1. deterministic formatter/lint/type/unit/integration/security gates;
2. cheap/qualified reviewer when useful;
3. stronger integration/security reviewer for high-risk tasks;
4. frontier architect only for novel/high-consequence ambiguity.

Do not spend frontier capacity to restate a stored specification.

## Stop conditions

Controller pauses a task instead of improvising when:
- task/spec conflict cannot be resolved from authoritative docs;
- required authority/secret/network permission is not permitted;
- budget/time/agent limits reached;
- migration conflicts with another active run;
- tests reveal an architectural invariant conflict;
- selected model profile lacks required capability;
- the only proposed fix weakens tenant/security boundaries.

## Production policy

Autonomous development can reach staging. Production remains a separate Release Controller/human-authorized action initially. Later canary automation may be introduced, but development agents still do not hold standing production credentials.
