# R2-009 — Task Scheduling

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 is built; recheck against the R1 implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Let the operator schedule a task once or on a recurrence. By default a scheduled task prepares its work and waits for the operator's approval. The operator can mark a specific low-risk task as unattended; it then runs on an API profile. A schedule never gives a run more authority than a manual run has.

## Why now
"Schedule my daily tasks" is one of the operator's main uses (ADR-0030). The owner decided the default on 2026-11-15. The rule that schedules get no shortcut must exist before any real side effect exists in R3.

## Context / linked docs / ADRs
- [Decision Register](../../docs/DECISION_REGISTER.md) (Scheduling)
- [Assumptions and open questions](../../docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md) (scheduled tasks decision)
- [Durable workflows and Temporal](../../docs/architecture/workflows-and-temporal.md)
- [Authority, authorization and Action Broker](../../docs/security/authority-and-action-broker.md)
- [Tenant Presence AI, model profiles and provider policy](../../docs/ai/tenant-ai-model-entitlements.md) (credential class)
- [Research: schedules](../../docs/research/OPEN_SOURCE_LANDSCAPE_OPERATOR_RUN_2026-11-14.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0003, ADR-0005, ADR-0029, ADR-0030

## Depends on
- R2-001 (runs), R2-007 (approvals), R2-008 (notifications). Uses R0-005 (Temporal schedules), R1-004, R1-009, R1-012.

## Invariants
- the scheduler is deterministic code. Firing a schedule spends no model tokens;
- only the operator can create, change, pause or delete a schedule. A model cannot. A client cannot;
- a schedule only starts a run. Every side effect of that run passes the same authority, limit and approval checks as a manual run (E-092);
- default mode is PREPARE_AND_WAIT;
- UNATTENDED is allowed only for a task whose skills are all low-risk and read-only or internal, and it always runs on an `API` credential-class profile, never the subscription (E-061, E-078);
- a task that posts, sends, deploys or spends beyond its budget always waits for approval, whatever its mode;
- nothing is run late without a decision and nothing is silently dropped (E-091).

## In scope
- ScheduledTask: tenant, task template (request, skills, parameters), mode (PREPARE_AND_WAIT, UNATTENDED), recurrence, timezone, local-time intent, next resolved instant, per-run budget, overlap policy, lateness window, state (ACTIVE, PAUSED, ENDED), owner.
- Recurrence: once, daily, weekly on chosen days, monthly; stored as local time plus IANA timezone, resolved to an instant for each occurrence.
- Daylight-saving and timezone rules: a nonexistent local time moves to the next valid minute; a repeated local time fires once.
- Temporal Schedule per ScheduledTask, firing a small workflow that: checks tenant state, limits and budget; resolves the model with start authority "schedule"; starts the run.
- PREPARE_AND_WAIT: the run does only preparation steps (research, drafts, plans); anything that would act becomes an ApprovalItem.
- UNATTENDED eligibility check at configuration time and again at each firing: every skill in the template has risk class LOW and declares no external action class. Validation fails closed.
- Frontier needed and nobody present: if resolution returns only an `OPERATOR_SUBSCRIPTION` profile, the run waits as an ApprovalItem "start this run"; it does not fall through.
- Overlap policy when the previous run is still going: SKIP (default), QUEUE_ONE, or CANCEL_PREVIOUS.
- Missed firings: after downtime, each missed occurrence inside the lateness window is listed for the operator as "missed, run now or skip"; outside the window it is recorded as MISSED. Unattended read-only tasks may be set to catch up once.
- Watches: a scheduled check that compares a result with the last one and notifies only on change.
- Console screens: create by conversation or form, list with next run time, pause, edit, history of occurrences.
- Tenant paused or budget reached: occurrences are skipped with a recorded reason and one notification.

## Out of scope
- Scheduling of social posts and deployments at a set time (R3-009, R3-003). They are delayed Actions in the broker, not ScheduledTasks.
- Client-created schedules.
- Event-driven triggers (webhooks, inbound mail).
- Cron expressions in the interface.

## API / contract changes
- Endpoints: create, update (with `base_version`), pause, resume, delete, list, occurrence history, resolve a missed occurrence.
- Internal: `fire(scheduled_task, occurrence)`, `validate_unattended(template)`.
- New contract sketch: `scheduled-task.schema.json`. A permission `schedule.manage` held by the operator only.

## Data / migration
- Tenant-scoped under RLS: ScheduledTask, ScheduleOccurrence.
- Temporal schedule IDs derived from the ScheduledTask ID; no tenant data in workflow history beyond references.
- Reverse migrations tested.

## Security / privacy threat notes
- A schedule treated as pre-approved (E-092): negative test that a scheduled run submitting a publish action without a grant is refused by the broker.
- A model, or injected content, creating or editing a schedule to gain repeated execution: `schedule.manage` requires an operator UI interaction reference.
- UNATTENDED template later edited to include a risky skill: eligibility is rechecked at every firing and when a skill version changes.
- Subscription used while the operator sleeps (E-061): resolver denies; test included.
- Schedule storm after an outage: missed occurrences are held, not replayed.
- Cross-tenant: a schedule fires only inside its own tenant context.

## Edge cases covered
- E-051 daylight-saving and timezone shifts.
- E-061 and E-078 subscription and frontier profile with nobody present.
- E-079 approvals pile up: prepared work expires per R2-007; the schedule shows it.
- E-091 system down at the scheduled time (task part; the post part is R3-009).
- E-092 schedule skips the broker.
- E-002 and E-052 limit lowered or tenant paused while scheduled.
- E-081 workflow code change with schedules in flight.

## Observability
- Audit: schedule created, changed, paused, deleted; each firing with its outcome (started, skipped with reason, missed, waiting).
- Metrics: firings by outcome, lateness, unattended runs and their cost, overlap skips.

## Acceptance criteria
- a daily task at 09:00 local time fires at 09:00 local time before and after a daylight-saving change;
- a default schedule produces prepared work and an approval item, and no side effect;
- marking a task UNATTENDED is refused if any of its skills is not low-risk or declares an external action;
- an unattended run never uses a subscription profile;
- a scheduled run that tries to act without a grant is refused by the Action Broker;
- after two hours of downtime, missed occurrences appear for the operator and none ran by itself (except read-only catch-up where configured);
- a second firing while the first run is active follows the overlap policy.

## Tests
- Time: recurrence resolution across DST forward and back, month ends, timezone change of the schedule.
- Mode matrix: PREPARE_AND_WAIT and UNATTENDED against skill risk classes.
- Credential-class matrix at firing.
- E-092 negative test in the protected suite.
- Downtime simulation with Temporal's test server: missed, late inside window, late outside window.
- Overlap: all three policies.
- Authority: client roles and a model-originated request cannot manage schedules.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on both tables; firing under tenant A cannot start a run in tenant B.
- Paused tenant and exhausted budget at firing.

## Rollback / failure recovery
A schedule can be paused at once. Occurrence records are append-only. Temporal schedule and database state are reconciled by a periodic job; the database is the truth. Reverse migrations tested.

## Cost/resource budget
Each schedule has a per-run budget and counts against the tenant's monthly cap. Scheduled work runs in the Resource Governor's "normal scheduled work" class, below interactive requests. Proposed default: at most 20 active schedules per tenant.

## Documentation updates
- `docs/architecture/workflows-and-temporal.md`, `docs/product/admin-and-managed-service.md`, `docs/data/core-entity-catalog.md`.

## Open decisions
- **Decision required:** lateness window. Proposed default: 2 hours for PREPARE_AND_WAIT, 12 hours for unattended read-only tasks.
- **Decision required:** per-tenant schedule limit. Proposed default above.
- **Decision required:** whether an unattended task may write to memory or facts. Proposed default: it may write TASK_STATE and Observations only; never a canonical fact, preference or decision.
- **Decision required:** default overlap policy. Proposed default: SKIP.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review recorded; the E-092 and E-061 tests are protected tests.
