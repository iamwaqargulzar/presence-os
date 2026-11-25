# Session Handoff — 2026-11-25 — R0-002 CI and environments

- Date: 2026-11-25
- Phase / release: R0
- Task contract(s): [`specs/R0/R0-002-ci-environments.md`](../../../specs/R0/R0-002-ci-environments.md)
- Starting commit: `5286133` (head of `feat/R0-001-repository-toolchain`)
- Ending commit: head of branch `feat/R0-002-ci-environments`
- Worker / model: Claude Code (desktop app), Claude Opus 5.5

## Done
- R0-001 pushed as PR #1. R0-002 built and pushed as PR #2, stacked on #1:
  - CI workflow and `tools/ci_run.py` with the result contract;
  - PostgreSQL 18.7 through compose;
  - protected paths;
  - a stronger gate self-test.

  Report: [evidence/R0/R0-002/report.md](../../../evidence/R0/R0-002/report.md).
- The first CI run failed as designed: every gate passed, and only `protected-paths` failed, waiting for the owner's label.
- On the owner's instruction, the repository was made public after a full-history secret scan found nothing. `main` is protected: pull request plus green `gates` check, also for administrators.
- Three parallel sessions started, each in its own worktree cut from R0-002's tip. Each opens a draft PR against `feat/R0-002-ci-environments`:
  - R0-003 (RLS);
  - R0-005 (Temporal);
  - R0-009 (infrastructure, repository-only, nothing applied to hardware).

## Decided
- CI design, protected paths, psycopg, public repository and branch protection → [ADR-0035](../../adrs/ADR-0035-ci-pipeline-and-protected-paths.md) and the Decision Register.

## Not finished
- The green CI run after the owner adds `owner-approved-protected-change` to PR #2. Add its link to the R0-002 report.
- PR #1 has no `gates` check, because the workflow arrives in PR #2, so branch protection blocks it. Proposal: retarget PR #2 to `main`, merge it (it contains R0-001), and close PR #1.

## Not checked
- No independent review of R0-002.
- The parallel sessions' results: check each draft PR's diff and CI before trusting its report.

## Next step
Owner: review PR #2 and add the label. Then merge as proposed above, and rebase the three draft PRs onto `main`.

## Owner decisions waiting
See [STATUS.md](../STATUS.md).
