# ADR-0035 — CI Pipeline, Result Contract and Protected Paths
Status: Accepted (2026-11-25). Made during R0-002 under the owner's delegation in ADR-0032 and ADR-0033.

## Context
R0-002 needs ordered CI stages, a machine-readable result, test databases, protection against a worker hiding a failing gate, and branch protection. On 2026-11-25 GitHub refused the branch protection and rulesets APIs for this private repository: "Upgrade to GitHub Pro or make this repository public to enable this feature."

## Decision
1. **One CI job.** `.github/workflows/ci.yml` installs exact uv and pnpm versions and runs `tools/ci_run.py`, which runs the `make` gate targets in a fixed order and writes `reports/ci-result.json` (schema `contracts/schemas/ci-result.schema.json`). Every stage runs even after an earlier failure, so one run shows all problems. Reports are uploaded and kept 30 days. Job limit 20 minutes.
2. **No secrets in CI.** The workflow uses no repository secrets, has a read-only token, uses `pull_request` (never `pull_request_target`) and pins every action by commit. Test credentials are generated per run and masked. A test checks these rules.
3. **Test database.** PostgreSQL 18.7 from the same `compose.yaml` as local development (ADR-0033). The Django test runner creates `test_<name>`, migrates it from empty and drops it. Until R0-003 one role owns and uses the tables.
4. **Protected paths.** `.github/protected-paths` lists CI, gate, spec and agent-rule files. A pull request changing any of them fails the `protected-paths` stage until the owner adds the label `owner-approved-protected-change`. Workers must never add it.
5. **Branch protection.** Not available on the current plan. Until the owner decides (upgrade, public repository, or stay), the rule is: merge only when the CI check on the pull request is green.
6. **psycopg 3.3.9** (with `psycopg-binary`) is added. Licence LGPL-3.0-only. Review note required by ADR-0033 section 3: it is used unmodified as a separately distributed library through its public API; Presence OS is not distributed to third parties (ADR-0030); it is the PostgreSQL driver Django recommends; no permissive alternative is maintained to the same level. Accepted.
7. **`django.contrib.contenttypes`** is installed now: it is a framework app every later identity and permissions task needs, and it gives CI real migrations to run from empty.

## Alternatives considered
- One GitHub job per stage: clearer in the GitHub page, but the result contract would need a merge step and stage order would be spread across files.
- Required reviewers through CODEOWNERS: GitHub does not let the author approve their own pull request, and every commit is made as the owner, so it would block every merge.
- Third-party setup actions for uv and pnpm: more supply-chain surface than installing exact versions with pipx and npm.

## Consequences
- The label and "merge only when green" are rules, not enforced by GitHub. Until R0-012 removes the owner's GitHub login from the worker, a worker could break them; this is recorded in the worktree workflow.
- The CI job needs Docker on the runner (GitHub-hosted Ubuntu runners have it).

## Security impact
CI cannot leak a repository secret because it has none. Pull requests from forks run with a read-only token. Logs are redacted of credential-like environment values before they are stored.

## Cost/operational impact
GitHub Actions minutes for a private repository on the free plan are limited per month; one run takes a few minutes. Artifacts are kept 30 days.

## Migration / rollback
Revert the commit. The local PostgreSQL volume can be removed with `docker compose down -v`.

## Supersedes

## Superseded by
