# Project Status

Last updated: 2026-11-25. Overwrite this file at every handoff; keep it short. Protocol: [README.md](README.md).

## Phase
R0 Engineering Foundation. R0-001 is built and its gates pass; it waits for the owner's review and merge.

## Repository
- Private GitHub repository `iamwaqargulzar/presence-os`, created by the owner on 2026-11-25. `main` holds the baseline commit `5eecb64`.
- R0-001 work is on branch `feat/R0-001-repository-toolchain`. Check `git log` and `gh pr list` for whether it is pushed, has a pull request, or is merged.
- Branch protection on `main` is not set yet (CONTRIBUTING.md says it should be once the repository exists).

## Current task
R0-001 [repository and toolchain](../../specs/R0/R0-001-repository-toolchain.md): done on the branch, report in [evidence/R0/R0-001/report.md](../../evidence/R0/R0-001/report.md). The next task is R0-002 (CI), then R0-003 (PostgreSQL row-level security). Order: [specs/R0/README.md](../../specs/R0/README.md).

The development controller (R0-011) and sandbox (R0-012) do not exist yet. Until they do, R0 tasks are built directly in a session that the operator starts and watches.

## Next step
1. If R0-001 is not merged: push the branch, open the pull request, owner reviews and merges.
2. Start a new session. Read this file, then [R0-002](../../specs/R0/R0-002-ci-environments.md), then build it. CI calls the `make` targets listed in [gates.md](../delivery/gates.md).

## How to work on the code
Machine setup and gate commands: [developer bootstrap](../runbooks/developer-bootstrap.md). Run `make check` before every commit; the pre-commit hook runs the secret scan and needs Docker.

## Blockers
None for R0.

## Owner decisions waiting
- Registrable domain for hosted client sites and previews (needed before anything tenant-generated goes online).
- Cloud storage target for the offsite backup copy (needed before the first client's production data).
- 24 questions for R2 and R3, listed in [ASSUMPTIONS_AND_OPEN_QUESTIONS.md](../ASSUMPTIONS_AND_OPEN_QUESTIONS.md) under "For the owner". None blocks R0 or R1.

## Known gaps
- The licence-check gate in [gates.md](../delivery/gates.md) has no owning R0 task. Proposal: add it to R0-002.
- `uv audit` is experimental in uv 0.13.10.
- Versions for later tools (Temporal, Redis, PostgreSQL 18 minor, Caddy, cloudflared) are still unchecked; each first-use task verifies them.
- R2 and R3 contracts are revision 1 with no second review; recheck before each release starts.

## Latest handoff
[log/2026-11-25-r0-001-repository-toolchain.md](log/2026-11-25-r0-001-repository-toolchain.md)
