# R2-017 — R2 Exit

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 is built; recheck against the R1 implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Prove with evidence that R2 works end to end and fails closed. From a phone, the operator creates a tenant, gets a snapshot and a plan, asks for work, schedules it, and approves it. A client signs in, requests a change and approves a draft. Nothing reaches the outside world except through the Action Broker with a fake connector.

## Why now
R3 adds real publishing, hosting and posting. Every boundary that R3 relies on must be proven while all connectors are still fake.

## Context / linked docs / ADRs
- [R2 README](README.md) and every R2 task contract
- [Gates](../../docs/delivery/gates.md)
- [Testing strategy](../../docs/delivery/testing-strategy.md)
- [Threat model](../../docs/security/threat-model.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md) (all entries tagged R2)
- [R1 exit](../R1/R1-010-kernel-exit.md)
- ADR-0002, ADR-0003, ADR-0014, ADR-0017, ADR-0030

## Depends on
- R2-001 to R2-016.

## Invariants
- evidence, not declaration, closes the release;
- a cross-tenant access, an unauthorised side effect, a client-started run or a subscription-backed unattended run is a release blocker;
- the suite uses fake providers, fake connectors, fixture sites and synthetic data only;
- defects are fixed in the owning task, not patched in the exit suite;
- the exit suite is a protected path.

## In scope
- End-to-end harness with at least three tenants (one operator-owned, two clients that list each other as competitors), the operator, and one client user per role.
- Positive journeys:
  1. new tenant → scan → snapshot → scores → opportunities → 30-day plan;
  2. operator asks in conversation → task → run → report;
  3. scheduled task prepares → push → approval → Action with the fake connector;
  4. client request → queue item → operator accepts → draft → client approval → Action with the fake connector.
- Negative variants, each must fail closed: client starts a run; scheduled run acts without a grant; unattended run resolves to the subscription; draft changed after approval; approval expired; injected "approve" text in a page, a file and a client request; cross-tenant read through memory, facts, vector search, cache, context, reports, notifications and attention; provider-policy violation in compile and in fallback; budget exhausted mid-run; paused tenant; stolen-session start of a development run without step-up.
- Disposition of every R2-tagged edge case: E-003, E-009, E-010, E-011, E-043, E-045, E-046, E-051, E-078, E-079, E-092, E-094, and the R2 part of E-091.
- Cost evidence: measured cost of each journey against the starting caps (USD 20 per client per month).
- Accessibility evidence: automated results and the recorded manual pass for the core journeys.
- Workflow replay tests for every R2 workflow (E-081).
- R2 exit report.

## Out of scope
- Real providers, real push to third parties beyond the staging device test in R2-008, real websites.
- Load testing beyond a small concurrency check of the Resource Governor classes used by R2.
- External penetration test. **Decision required**; see open decisions.

## API / contract changes
None. Confirms that every R2 contract sketch added under `contracts/schemas/` validates and matches the implementation.

## Data / migration
None. Confirms the full R0+R1+R2 migration chain applies from empty and reverses, and that the RLS coverage check reports no unprotected tenant table, including the vector tables.

## Security / privacy threat notes
The suite is the regression barrier for the R2 threat model: authority from language, memory poisoning, context leakage, schedule shortcuts and notification leakage. It runs under the runtime database role.

## Edge cases covered
All R2-tagged entries listed above. Each gets one of: covered by test (with the test name), covered by design (with the reason), or deferred (with the release and a note in the open questions file).

## Observability
The exit report links one full trace per positive journey, from the operator's message to the fake connector call, and the audit trail for each negative variant.

## Acceptance criteria
- all four positive journeys pass on a clean environment built from an empty database;
- every negative variant fails closed with an audit record that names the reason;
- no R2-tagged edge case is without a disposition;
- the measured monthly cost of the default schedules for one client is inside the client cap, with the figures in the report;
- no critical accessibility defect is open on a core journey;
- the report is accepted by the operator.

## Tests
The suite itself. In addition:
- mutation check on the main guards: removing the `start_ai_work` check, the hash binding, the provider-policy filter or the tenant filter makes at least one exit test fail;
- protected-path check: an implementation worker cannot change the suite in the same run.

## Rollback / failure recovery
A failed exit keeps R3 closed. Each failure becomes a defect on the owning task.

## Cost/resource budget
The whole suite runs on fakes and spends no API money. One optional smoke run on real model profiles is capped at USD 5 and needs the operator's start.

## Documentation updates
- R2 exit report under `evidence/`.
- `docs/PROJECT_REAUDIT_2026-08-10.md`: mark the R2 dispositions.
- `docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`: close or carry forward each R2 open decision.
- Recheck every R3 contract against what R2 actually built; record spec revisions.

## Open decisions
- **Decision required (owner):** an outside security review before R3 handles real client accounts. Proposed default: an independent review by a second model profile and a manual checklist at R2 exit; a paid external test is considered before the first client's social account is connected.
- **Decision required:** the pass threshold for the intent test set in R2-005. Proposed default: 95% correct mode, and zero cases where a non-implementation message is resolved as IMPLEMENT.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent review of the exit evidence is recorded; the operator has accepted the report.
