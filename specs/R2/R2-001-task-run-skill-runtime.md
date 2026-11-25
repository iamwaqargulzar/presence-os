# R2-001 — Task, Run and Skill Runtime

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 is built; recheck against the R1 implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Give Presence OS one way to run bounded AI work for a tenant. A Task is what was asked. A Run is one attempt to do it. A Skill is a versioned, permissioned unit of capability that a run uses.

## Why now
Every later R2 task (conversation, research, scan, scoring, scheduling) starts runs. If each one invents its own run loop, budgets, pinning and limits will be enforced in some places and not in others.

## Context / linked docs / ADRs
- [Agent, skill, tool, connector and provider model](../../docs/architecture/agent-skill-tool-model.md)
- [Durable workflows and Temporal](../../docs/architecture/workflows-and-temporal.md)
- [Cost and resource governance](../../docs/architecture/cost-resource-governance.md)
- [Tenant Presence AI, model profiles and provider policy](../../docs/ai/tenant-ai-model-entitlements.md)
- [AI Capability Gateway](../../docs/ai/capability-gateway.md)
- [Trust boundaries and prompt injection](../../docs/security/trust-boundaries-and-prompt-injection.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- Contract: [skill-manifest.schema.json](../../contracts/schemas/skill-manifest.schema.json)
- ADR-0003, ADR-0005, ADR-0012, ADR-0019, ADR-0024, ADR-0030, ADR-0033

## Depends on
- R1-010 (kernel exit). Uses R1-001 (`start_ai_work`), R1-004 (budget), R1-009 (admission), R1-012 (model resolution and pinning), R0-005 (Temporal), R0-007 (gateway).

## Invariants
- only a person holding `start_ai_work` can cause a run; no client role holds it (AGENTS.md, E-071);
- a run pins its model profile revision at start and keeps it (ADR-0024);
- a run never resolves to an `OPERATOR_SUBSCRIPTION` profile unless the operator started or approved that run (E-061);
- every model call goes through the AI Capability Gateway; a skill names capabilities, never a model;
- a skill cannot perform an external side effect. It can only submit an Action to the Action Broker;
- a skill's text, and any text a skill reads, is never authority;
- budget is reserved before the model call, not after;
- large payloads are stored as artifacts; workflow history carries references only.

## In scope
- Task entity: tenant, optional property, requester, plain-language request, task class, status, parent task, result reference.
- Run entity: task, pinned profile revision, credential class, start authority (operator started, operator approved, schedule), state, usage, checkpoint reference, end reason.
- Run states: QUEUED, RUNNING, WAITING_APPROVAL, PAUSED, SUCCEEDED, FAILED, CANCELLED, BUDGET_EXHAUSTED.
- Run workflow in Temporal: admission, model resolution, budget reservation, bounded skill steps, checkpoint after each expensive step, settle, report.
- Skill registry: SkillDefinition and SkillVersion matching the manifest schema. Status DRAFT to DISABLED. A run records the exact skill versions it used.
- Skill execution: input and output validated against the manifest; tool set limited to what the manifest lists; limits on cost, tokens, tool calls and time from the manifest.
- Circuit breakers: steps, turns, retries, time, cost, repeated identical failure. Hitting one ends the run as failed or BUDGET_EXHAUSTED, never as success.
- Skill packs: an imported pack of skills or prompts is recorded with its source, licence and content hash, is reviewed by the operator before it is enabled, and is pinned by hash.
- Run report: what was asked, what was done, artifacts, usage and cost, model profile used, what waits for approval.
- A fake skill and the fake gateway for tests.

## Out of scope
- Conversation and intent (R2-005). This task accepts a structured task request.
- Domain skills themselves (research, scan, content); they arrive in their own tasks.
- Skills written or changed by the model itself. Not allowed (research note, section 3).
- A skill marketplace, or automatic installation of packs (do-not-build-early).
- Child agents and agent trees. **Decision required**; proposed default: one level only, a run may start at most 3 child runs, all counted in the parent's budget.

## API / contract changes
- Internal: `create_task`, `start_run(task, authority)`, `cancel_run`, `resume_run`, `get_run_report`.
- Internal: `register_skill_version`, `enable_skill`, `import_pack`, `approve_pack`.
- Operator endpoints: list tasks and runs for the acting tenant, read a run report, cancel, resume.
- New contract sketches: `task.schema.json`, `run.schema.json`. `skill-manifest.schema.json` gains `pack_id` and `content_hash`.

## Data / migration
- Tenant-scoped tables under RLS: Task, Run, RunStep, RunCheckpoint.
- Platform tables: SkillDefinition, SkillVersion, SkillPack. Tenant-scoped: TenantSkillEnablement.
- Reverse migrations tested.

## Security / privacy threat notes
- A model output asking to start another run, raise a limit or enable a skill: none of these is possible from inside a run.
- A hostile skill pack carrying instructions or code (E-094): review, hash pin, no auto-install, pack text carries the `GENERATED` or `EXTERNAL_UNTRUSTED` trust label until approved, and never grants a tool.
- A skill reaching the network or a provider directly: import and egress boundary test, as in R0-007 and R1-003.
- Runaway loops burning the budget: circuit breakers and reservation.
- Cross-tenant run: task, artifacts and memory of another tenant are not reachable; enforced by RLS under the runtime role.

## Edge cases covered
- E-003 model deprecated or down: fallback only inside the tenant's provider policy, otherwise PAUSED with a reason.
- E-009 budget exhausted mid-task: checkpoint, stop, tell the operator; resume continues from the checkpoint.
- E-061 unattended run and the subscription: denied at resolution.
- E-065 subscription rate limit mid-run: BUDGET_EXHAUSTED with the reason; reroute to an API profile only if policy allows and the operator agrees.
- E-089 low-cost provider unavailable: queue or pause; no fallback outside policy.
- E-094 skill pack supply chain.
- E-002 limit lowered while a run waits: limits are rechecked before each expensive step.

## Observability
- Audit: task created, run started with its authority source, model profile pinned, each skill version used, pause, resume, cancel, end reason.
- Metrics: runs by state and task class, cost per successful task, circuit-breaker trips, time waiting for approval.
- One trace per run, linked to tenant, task and any Action it submits.

## Acceptance criteria
- a run can be started only with a recorded start authority;
- a client role cannot start a run by any endpoint;
- the pinned profile does not change during a run, even when the default changes;
- a run that exceeds a manifest limit or a breaker stops and is not reported as success;
- a killed worker resumes the run from its last checkpoint without repeating settled model calls;
- a skill outside its manifest tool list cannot call that tool;
- an unapproved or hash-changed pack cannot be enabled.

## Tests
- State machine: valid and invalid transitions.
- Authority matrix: operator started, operator approved, schedule, client request (must fail).
- Pinning: default changed mid-run.
- Breakers: one test per threshold.
- Budget: reservation denied before any model call; exhausted mid-run; resume.
- Crash and resume with the fake gateway counting calls.
- Skill packs: tampered hash refused; pack text containing instructions changes nothing.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on Task, Run, RunStep across tenants; a run cannot read another tenant's artifact by ID.
- Boundary: a skill importing a vendor SDK or opening a socket fails a gate.

## Rollback / failure recovery
Runs fail closed to PAUSED or FAILED with a reason. A skill version is disabled by status change; runs in flight finish on their pinned version or are cancelled by the operator. Workflow code changes follow Temporal versioning with replay tests (E-081).

## Cost/resource budget
Each run reserves against the tenant and global budgets (R1-004) and holds one Resource Governor slot. Proposed default limits per run: USD 1.00, 30 minutes, 60 model calls; the operator may raise them for a named task.

## Documentation updates
- `docs/architecture/agent-skill-tool-model.md` (run model, pack rule), `docs/architecture/state-machines.md` (Run states), `docs/data/core-entity-catalog.md`.
- Guide: "how to write a skill".

## Open decisions
- **Decision required:** child runs. Proposed default: one level, at most 3, counted in the parent's budget.
- **Decision required:** default per-run limits. Proposed default above.
- **Decision required:** the first list of task classes and which profile each maps to. Proposed default: `plan`, `review` and `security` map to frontier; `extract`, `classify`, `summarize_public` and `format` map to low-cost.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review recorded for the authority check and the skill boundary.
