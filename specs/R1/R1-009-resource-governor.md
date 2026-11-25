# R1-009 — Resource Governor

> **Spec revision:** 2 — 2026-11-10. Expanded from a one-paragraph summary to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). The revision 1 summary is kept verbatim under Goal. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## Goal
Implement baseline per-tenant concurrency/admission controls for background/interactive/browser/AI tasks and priority classes. Ensure cost budget alone cannot create noisy-neighbor starvation.

## Why now
The platform runs on one host and one GPU. A tenant with plenty of budget could still occupy every worker slot. Capacity has to be governed separately from money before multi-tenant workloads exist.

## Context / linked docs / ADRs
- [Cost and resource governance](../../docs/architecture/cost-resource-governance.md)
- [Capacity and noisy-neighbor operations](../../docs/operations/capacity-and-noisy-neighbor.md)
- [Service levels and SLO](../../docs/operations/service-levels-and-slo.md)
- [Durable workflows and Temporal](../../docs/architecture/workflows-and-temporal.md)
- [Re-audit edge case E-021](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0019 (Resource Governor separate from Cost Governor)

## Depends on
- R0-005 (queues/workers), R0-006, R1-004 (tenant limits).

## Invariants
- resource governance is separate from cost governance: having budget never bypasses admission;
- no tenant can starve another;
- background and video work never make realtime or interactive work unusable;
- admission decisions are deterministic and explainable;
- no new infrastructure product is introduced for this (no Kafka, no separate scheduler service).

## In scope
- Resource classes: tenant total concurrency, LLM concurrency, GPU queue, browser concurrency, crawl concurrency, media queue. R1 enforces the classes that have workloads; the rest are declared.
- Priority classes, highest first: realtime voice; interactive user request; tenant foreground; normal scheduled work; internal scans; video/background.
- Admission interface: `acquire(tenant, class, priority) → slot | queued | rejected(reason)` and `release`, safe under crashes (lease with expiry).
- Per-tenant limits sourced from R1-004 with platform defaults.
- Fair scheduling across tenants within a priority class (weighted).
- Hooks for per-property attribution so R1-011 can add property-level limits.
- Integration with Temporal task dispatch for background/interactive classes.

## Out of scope
- GPU scheduling on the inference host itself (the Inference Gateway owns its queue; this task defines the class and limit).
- Autoscaling.
- Provider rate-limit tracking per connection (declared, implemented with connectors).
- Capacity alerting rules.

## API / contract changes
- Internal admission interface and a slot/lease record.
- Limit keys added to the R1-004 tenant limit catalogue.

## Data / migration
- Slot/lease state in Redis or Postgres (decide), with tenant-scoped counters; limit configuration (platform-level defaults plus tenant limit overrides).
- If Postgres tables are used, tenant-scoped ones are under RLS. Reverse migrations tested.

## Security / privacy threat notes
- Denial of service by one tenant against others, deliberately or by a runaway workflow.
- Slot leak after a worker crash permanently reducing capacity.
- Priority abuse: a caller labelling background work as interactive. Priority is assigned by the platform from the request type, never by tenant input or by a model.
- Queue metadata visible across tenants.

## Observability
- Metrics per tenant and class: in-use slots, queue depth, wait time, rejections, lease expiries.
- Platform metrics: total utilisation per class.
- Tenant-facing views show only that tenant's numbers.

## Acceptance criteria
- *(revision 1)* per-tenant concurrency and admission controls for background, interactive, browser and AI tasks;
- *(revision 1)* priority classes;
- *(revision 1)* cost budget alone cannot create noisy-neighbor starvation;
- *(derived)* with tenant A saturating its limit, tenant B's interactive request is admitted within the defined bound;
- *(derived)* crashed holders' slots are reclaimed automatically;
- *(derived)* a tenant with unlimited budget still cannot exceed its concurrency limit.

## Tests
- Unit: limit resolution from R1-004; priority ordering.
- Concurrency: N acquirers against limit M; never more than M held.
- Fairness: saturating tenant versus light tenant, measured wait for the light tenant.
- Starvation: continuous high-priority load does not block lower classes forever, or the documented policy for that case is verified.
- Crash: holder killed, slot reclaimed after lease expiry.
- Budget independence: large budget, small limit.
- Cross-tenant isolation of counters and queue views.

## Rollback / failure recovery
If the governor's state store is unavailable, admission fails to a conservative mode (documented: reject background, allow a small interactive floor), never to unlimited. Limits are configuration and can be reverted.

## Cost/resource budget
The governor is on the dispatch path: constant-time acquire/release. Initial limits are set conservatively from R0-009 capacity measurements.

## Documentation updates
- `docs/architecture/cost-resource-governance.md`, `docs/operations/capacity-and-noisy-neighbor.md` (classes, defaults, degraded mode).
- Guide: "how to run work under the governor".

## Open decisions
- **Decided (ADR-0033):** Redis, with expiry times on leases.
- **Decision required:** initial per-class limits and fairness weights.
- **Decided (ADR-0033):** no new heavy or AI work starts while the store is down; it queues.
- **Decided (ADR-0033):** a waiting job gains priority with age; the lowest class always keeps one slot.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: a recorded fairness test result against the defined bound.
