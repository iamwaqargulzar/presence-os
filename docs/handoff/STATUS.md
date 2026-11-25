# Project Status

Last updated: 2026-11-25. Overwrite this file at every handoff; keep it short. Protocol: [README.md](README.md).

## Phase
Specification complete. Implementation has not started. Next release: **R0 Engineering Foundation**.

## Repository
- Git initialised on branch `main` on 2026-11-25. The specification package is the baseline; check `git log` for whether the first commit is made.
- Not yet pushed. Target: a private GitHub repository under the owner's account (ADR-0032). The owner runs or approves the command that creates it.

## Current task
None in progress. The next task is [R0-001 repository and toolchain](../../specs/R0/R0-001-repository-toolchain.md), followed by R0-002 (CI) and R0-003 (PostgreSQL row-level security). Order: [specs/R0/README.md](../../specs/R0/README.md).

The development controller (R0-011) and sandbox (R0-012) do not exist yet. Until they do, R0 tasks are built directly in a session that the operator starts and watches.

## Next step
Start a new session. Read this file, then R0-001, then build R0-001 step by step.

## Blockers
None for R0.

## Owner decisions waiting
- Registrable domain for hosted client sites and previews (needed before anything tenant-generated goes online).
- Cloud storage target for the offsite backup copy (needed before the first client's production data).
- 24 questions for R2 and R3, listed in [ASSUMPTIONS_AND_OPEN_QUESTIONS.md](../ASSUMPTIONS_AND_OPEN_QUESTIONS.md) under "For the owner". None blocks R0 or R1.

## Known gaps
- Version numbers and tool names (ADR-0032, ADR-0033) came from web search and memory; R0-001 and each first-use task verify them.
- R2 and R3 contracts are revision 1 with no second review; recheck before each release starts.

## Latest handoff
[log/2026-11-25-specification-baseline.md](log/2026-11-25-specification-baseline.md)
