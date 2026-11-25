# Project Status

Last updated: 2026-11-25. Overwrite this file at every handoff; keep it short. Protocol: [README.md](README.md).

## Phase
R0 Engineering Foundation. R0-001 built (PR #1, waiting for review). R0-002 built (PR #2, stacked on #1); CI evidence and implementation report still to record.

## Repository
- Private GitHub repository `iamwaqargulzar/presence-os`. `main` holds only the baseline commit `5eecb64`.
- PR #1 `feat/R0-001-repository-toolchain` → `main`. PR #2 `feat/R0-002-ci-environments` → PR #1's branch; retarget to `main` after #1 merges.
- The repository is public (owner decision, 2026-11-25). `main` requires a pull request and a green `gates` check, also for administrators (ADR-0035).

## Current task
R0-002 [CI and environments](../../specs/R0/R0-002-ci-environments.md). Code, workflow and docs are pushed. Not finished:
1. Record the first CI run of PR #2: the `protected-paths` stage is expected to fail until the owner adds the label `owner-approved-protected-change`; after the label, the run should be green.
2. Write `evidence/R0/R0-002/report.md` with both run links, the `ci-result.json` stage table and the self-test output, then a handoff log entry.

The development controller (R0-011) and sandbox (R0-012) do not exist yet. Until they do, R0 tasks are built directly in a session that the operator starts and watches.

## Next step
Read the CI result of PR #2 (`gh pr checks 2`, artifact `ci-reports`), then finish item 2 above. After that: R0-003 (PostgreSQL row-level security).

## How to work on the code
Machine setup and gate commands: [developer bootstrap](../runbooks/developer-bootstrap.md). Run `make check` before every commit; the pre-commit hook runs the secret scan and needs Docker.

## Blockers
None for R0.

## Owner decisions waiting
- Registrable domain for hosted client sites and previews (needed before anything tenant-generated goes online).
- Cloud storage target for the offsite backup copy (needed before the first client's production data).
- 24 questions for R2 and R3, listed in [ASSUMPTIONS_AND_OPEN_QUESTIONS.md](../ASSUMPTIONS_AND_OPEN_QUESTIONS.md) under "For the owner". None blocks R0 or R1.

## Known gaps
- The licence-check gate in [gates.md](../delivery/gates.md) has no owning R0 task. Proposal: a small follow-up task.
- `uv audit` is experimental in uv 0.13.10.
- Versions for later tools (Temporal, Redis, PostgreSQL 18 minor, Caddy, cloudflared) are still unchecked; each first-use task verifies them.
- R2 and R3 contracts are revision 1 with no second review; recheck before each release starts.

## Latest handoff
[log/2026-11-25-r0-001-repository-toolchain.md](log/2026-11-25-r0-001-repository-toolchain.md)
