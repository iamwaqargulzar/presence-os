# R0-010 — R0 Exit Audit

> **Spec revision:** 2 — 2026-11-10. Expanded to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). Every revision 1 requirement, including the 2026-08-10 additional exit requirements, is retained. Items marked *(derived)* come from the linked focused documents.

## Goal
Prove the foundation is safe enough to start R1.

## Why now
R1 adds authority, external side effects and money. Starting it on an unverified foundation would make every R1 security claim unprovable.

## Context / linked docs / ADRs
- [R0 README](README.md) and every R0 task contract
- [Release plan](../../docs/delivery/release-plan.md)
- [Definition of done](../../docs/delivery/definition-of-done.md), [Testing strategy](../../docs/delivery/testing-strategy.md)
- [Threat model](../../docs/security/threat-model.md)
- [Re-audit and edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md) (all entries tagged R0)
- ADR-0017 (release sequence)

## Depends on
- R0-001 through R0-009, R0-011 and R0-012.

## Invariants
- R0 exits only when evidence is stored, not when an agent declares completion;
- a security-critical failure is a release blocker;
- the audit does not change code to make itself pass: defects become tasks in the owning spec.

## In scope
- Collect and verify evidence for every item below.
- Review each R0 edge case (E-006, E-024 to E-042, E-044) and record: control implemented, test reference, or accepted gap with owner and date.
- Compare the documentation tree and ADRs with what was built; raise corrections.
- Produce the R0 exit report.

## Out of scope
- New features.
- R1 planning beyond confirming the R1 task contracts are ready to execute.
- External certification or compliance attestation.

## API / contract changes
None. Confirms that the contracts introduced in R0 (gate commands, CI result, tenant context, audit append, gateway, DevelopmentRun) are documented and stable enough for R1.

## Data / migration
None. Confirms that all R0 migrations apply from empty and that reverse migrations were tested.

## Security / privacy threat notes
- The audit itself is the control against fabricated completion (E-039).
- The auditor must be independent of the implementing worker for the security-sensitive tasks (R0-003, R0-004, R0-008, R0-012).
- Evidence artifacts are redacted before storage.

## Observability
Evidence is stored under `evidence/R0/` with, for each item: what was run, commit SHA, date, result and who or what ran it.

## Acceptance criteria
Required evidence:
- CI green from clean clone;
- RLS isolation suite;
- Fetch Broker negative tests;
- backup restore drill;
- Temporal recovery test;
- secrets/redaction review;
- PresenceBench seed run;
- threat model reviewed;
- no production credentials in coding environments;
- documentation tree/current ADRs match implementation.

2026-08-10 additional exit requirements:
- R0-011 OpenHands/Prime controller-adapter gates pass;
- R0-012 autonomous-development sandbox/supply-chain gates pass;
- controller vs worker token/cost telemetry is separately attributable;
- Prime worker can be stopped/recovered without orphaned children;
- no production secret or management-network reachability from development worker.

*(Derived)*
- every R0 open decision is resolved in an ADR or explicitly carried forward with an owner;
- every R0-tagged edge case has a recorded disposition.

## Tests
No new tests are written here. The audit re-runs, from a clean clone at the candidate commit: the full CI pipeline, the RLS isolation suite, the Fetch Broker negative suite, the Temporal recovery test, the redaction tests, the controller cancel/orphan tests and the sandbox egress tests. The restore drill and network checks are taken from R0-009 operator evidence.

## Rollback / failure recovery
A failed audit does not roll anything back. It produces a list of blocking defects, each assigned to its owning task; the audit is re-run after they are fixed.

## Cost/resource budget
One full pipeline run plus the seed benchmark run. Review effort is bounded to the R0 scope.

## Documentation updates
- R0 exit report.
- Corrections to any document that no longer matches the implementation.
- `docs/DECISION_REGISTER.md` and ADR index updated with R0 decisions.
- `README.md` project status.

## Definition of done
The exit report exists, every acceptance item links to stored evidence, there are no open security-critical findings, and the owner has accepted the report. Only then may R1 implementation start.
