# Project Status

Last updated: 2026-11-25. Overwrite this file at every handoff; keep it short. Protocol: [README.md](README.md).

## Phase
R0 Engineering Foundation. R0-001 built (PR #1, waiting for review). R0-002 built (PR #2, stacked on #1), waiting for the owner's label. R0-003, R0-005 and R0-009 under way in parallel sessions (draft PRs against the R0-002 branch).

## Repository
- Public GitHub repository `iamwaqargulzar/presence-os`. `main` holds only the baseline commit `5eecb64`.
- PR #1 `feat/R0-001-repository-toolchain` → `main`. PR #2 `feat/R0-002-ci-environments` → PR #1's branch; retarget to `main` after #1 merges.
- The repository is public (owner decision, 2026-11-25). `main` requires a pull request and a green `gates` check, also for administrators (ADR-0035).

## Current task
R0-002 [CI and environments](../../specs/R0/R0-002-ci-environments.md) is done except for one step. Its first CI run failed only at `protected-paths`, as designed. The owner reviews PR #2 and adds `owner-approved-protected-change`; the green run's link then goes into [the report](../../evidence/R0/R0-002/report.md).

In parallel, each in its own worktree and draft PR against `feat/R0-002-ci-environments`:
- R0-003 (RLS);
- R0-005 (Temporal; tenant context is behind an interface until R0-003 lands);
- R0-009 (infrastructure as code and runbooks only).

The development controller (R0-011) and sandbox (R0-012) do not exist yet. Until they do, R0 tasks are built directly in a session that the operator starts and watches.

## Next step
PR #1 can't merge under branch protection, because it has no `gates` check. Retarget PR #2 to `main`, merge it after the label (it contains R0-001), and close PR #1. Then rebase the three draft PRs onto `main`, review each one's diff and CI, and merge them in order: R0-003, R0-005, R0-009. Next tasks after them: R0-006, then R0-004.

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
[log/2026-11-25-r0-002-ci-environments.md](log/2026-11-25-r0-002-ci-environments.md)
