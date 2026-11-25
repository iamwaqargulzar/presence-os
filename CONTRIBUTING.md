# Contributing

Current as of 2026-11-25. Presence OS has one owner and operator. "Contributor" here means the owner and the development workers (AI agents) acting for the owner.

## Before any change
Read [`AGENTS.md`](AGENTS.md), [`docs/handoff/STATUS.md`](docs/handoff/STATUS.md) and the task contract in `specs/`. Work without a task contract is limited to documentation and housekeeping.

## Identity
- Every commit and push is made as the owner, with the global Git identity. Never set a per-repository `user.name` or `user.email`.
- Never commit as an agent or tool name, and never add `Co-authored-by` or other agent attribution lines.

## Branches
- `main` is always releasable to staging and protected once the GitHub repository exists.
- Work branches: `<type>/<task-id>-<slug>`, for example `feat/R0-003-postgres-rls` or `docs/handoff-2026-11-25`.
- One task contract per branch and pull request.

## Commit messages
[Conventional Commits](https://www.conventionalcommits.org/): `<type>(<scope>): <summary>`.
- Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore`, `security`.
- Scope: the task id or area, for example `feat(R0-003): add tenant isolation policies`.
- Summary in the imperative, at most 72 characters. The body says why, and links the task or ADR.

## Pull requests
Use the [pull request template](.github/pull_request_template.md). A pull request merges only when:
- every gate in [`docs/delivery/gates.md`](docs/delivery/gates.md) passes in CI;
- the task's acceptance criteria are met and its implementation report is in `evidence/`;
- security-critical work has a recorded independent review;
- documentation is updated and `python3 tools/build_docs.py` prints `links: ok`.

## Dependencies
No dependency is added without the license, security, maintenance and duplication review in [`AGENTS.md`](AGENTS.md) and ADR-0033 section 3. Record the review in the pull request.

## Documentation
Follow [`docs/DOCUMENTATION_STANDARDS.md`](docs/DOCUMENTATION_STANDARDS.md).
