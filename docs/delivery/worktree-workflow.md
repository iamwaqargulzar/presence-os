# Coding-Agent Worktree Workflow

Current as of 2026-11-25 (R0-002). Applies to every development run, by a person or an agent. The R0-011 controller automates these steps later; until then the operator follows them.

## One run, one worktree
1. Start from the newest `main` (or the branch the task contract depends on):
   `git worktree add ../presence-os-<task-id> -b <type>/<task-id>-<slug> main`
2. Branch names follow [CONTRIBUTING.md](../../CONTRIBUTING.md): `<type>/<task-id>-<slug>`, for example `feat/R0-003-postgres-rls`. One task per branch.
3. Run `make bootstrap` inside the worktree. Each worktree has its own `.env`. Use a different `PRESENCE_DB_PORT` (and Compose project, `COMPOSE_PROJECT_NAME=presence-<task-id>`) when two worktrees run integration tests at the same time.
4. Record the start commit and the task contract's hash in the implementation report (ADR-0028).

## While working
- Run `make check` before every commit; the pre-commit hook runs the secret scan.
- A worker never edits its own task contract, the protected paths in `.github/protected-paths`, or the gates, unless the task says so. CI flags every such change.

## Finishing
1. Push the branch and open a pull request. CI is the only accepted gate result (E-039).
2. A pull request that touches a protected path stays red until the owner reviews it and adds the label `owner-approved-protected-change`. A worker never adds that label.
3. After merge or abandonment, clean up:
   `docker compose -p presence-<task-id> down -v` (if you started services), then `git worktree remove ../presence-os-<task-id>` and `git branch -d <branch>`.
4. `git worktree prune` removes records of worktrees deleted by hand.

## Known limit
Until the R0-012 sandbox exists, an agent works with the owner's GitHub login and could add the label itself. The rule above forbids it; the sandbox removes the ability.
