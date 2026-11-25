# R0-005 — Temporal Durable Workflow Foundation

> **Spec revision:** 2 — 2026-11-10. Expanded to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). Every revision 1 requirement is retained. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## Goal
Establish Temporal service/client/workers, conventions and a reference human-wait/retry workflow.

## Why now
Approvals, scheduled actions, domain verification and offboarding all wait, retry and resume. The Action Broker (R1-003) needs durable delayed execution with revalidation, so the conventions must exist first.

## Context / linked docs / ADRs
- Edge cases added 2026-11-14 that this task must cover: E-081 ([register](../../docs/PROJECT_REAUDIT_2026-08-10.md)).
- [Durable workflows and Temporal](../../docs/architecture/workflows-and-temporal.md)
- [Concurrency, idempotency and consistency](../../docs/architecture/concurrency-idempotency.md)
- [Network and service exposure](../../docs/security/network-and-service-exposure.md)
- [Temporal references](../../docs/SOURCE_REGISTRY.md)
- ADR-0005 (Temporal for durable workflows)

## Depends on
- R0-001, R0-002.
- R0-003 for tenant context propagation into activities *(derived)*.

## Invariants
- workflow code is deterministic;
- activities are idempotent;
- large artifacts stay outside Temporal history; history carries references;
- Temporal is never exposed publicly;
- authorization and tenant limits are revalidated before any delayed side effect (enforced in R1; the pattern is established here);
- no Kafka: eventing starts with a transactional outbox.

## In scope
- Temporal service for local and CI use, a client, and at least one worker process in `apps/worker`.
- Package conventions separating workflow definitions from activities.
- Reference workflow: start, wait for a human signal with a timeout, run a retrying idempotent activity, complete; supports cancellation.
- Checkpoint pattern: an expensive stage stores its result as an artifact reference and is not recomputed on retry.
- Tenant/profile/trace context propagation from workflow start into activities.
- Versioning and worker deployment policy document.
- Transactional outbox pattern, minimal implementation or documented design *(derived from `concurrency-idempotency.md`)*.

## Out of scope
- Business workflows (approvals, publishing, deployment, offboarding).
- Production Temporal deployment and persistence sizing (R0-009 hosts it).
- Worker Versioning rollout automation.

## API / contract changes
- Internal: workflow start interface carrying tenant/profile/trace context and an idempotent workflow ID convention.
- Activity interface convention: inputs and outputs are small, typed, and reference artifacts by ID.

## Data / migration
- Temporal's own persistence store, separate from business tables.
- Outbox table if implemented in this task (tenant-scoped, under RLS).
- Reference workflow artifacts go to the object store or Postgres, not history.

## Security / privacy threat notes
- Tenant data or secrets written into workflow history: forbid by convention and test payload size/content.
- An activity running under the wrong tenant context after a retry on another worker.
- Temporal UI/API reachable beyond the private network.
- A signal from an unauthorised source completing a human wait: signals carry no authority by themselves (ADR-0003).

## Observability
- Workflow ID, run ID, tenant, profile and trace ID correlated in logs and spans.
- Metrics: queue backlog, activity failures and retries, workflow duration.

## Acceptance criteria
- workflow/activity packages separated correctly;
- deterministic workflow test;
- idempotent activity example;
- cancellation;
- checkpoint/artifact-reference pattern;
- versioning/deployment policy documented;
- large payload not stored directly in history;
- *(derived)* a worker killed mid-workflow resumes from the last completed stage (this is the "Temporal recovery test" required by R0-010);
- *(derived)* tenant context in an activity matches the workflow's tenant after retry.

## Tests
- Replay/determinism test of the reference workflow.
- Activity invoked twice with the same idempotency key produces one effect.
- Cancellation during the human wait and during the activity.
- Worker restart mid-run: completes without repeating the checkpointed stage.
- Seeded oversized payload is rejected or stored by reference.

## Rollback / failure recovery
Workflow definitions are versioned; an incompatible change follows the documented versioning policy instead of editing running workflow code. The reference workflow has no external effects.

## Cost/resource budget
One Temporal service and one worker on the Core VM initially. Record baseline memory and storage use to inform R0-009 sizing.

## Documentation updates
- `docs/architecture/workflows-and-temporal.md` (concrete conventions, versioning policy).
- "How to write a workflow" guide for later tasks.

## Open decisions
- **Decided (ADR-0033):** newest stable Temporal server, pinned; workflows use the Python SDK.
- **Decided (ADR-0033):** PostgreSQL, in a separate database with its own role; never shared with tenant tables.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: the recovery test result is stored as evidence for R0-010.
