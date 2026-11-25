# Implementation Report — R0-002 CI and Environments

Written 2026-11-25. Spec: [R0-002](../../../specs/R0/R0-002-ci-environments.md). Decisions: [ADR-0035](../../../docs/adrs/ADR-0035-ci-pipeline-and-protected-paths.md).

- Starting commit: `5286133` (docs(R0-001): add implementation report and handoff), the head of `feat/R0-001-repository-toolchain`.
- Resulting commit: the head of branch `feat/R0-002-ci-environments`. It contains this report, so it cannot name its own hash.
- Execution profile: an interactive session that the operator started and watched; no controller exists yet (R0-011).
- Harness: Claude Code, desktop app.
- Model: Claude Opus 5.5 (`claude-opus-5-5`).
- Reasoning: the session default.
- Task/spec hash: sha256 `99f3f5f63d92a0394fdd1d973fa4f5ff423a3effbb2c0fae0e52ce96acfd91f6` of `specs/R0/R0-002-ci-environments.md`.
- Changed files: see `git diff --stat 5286133..feat/R0-002-ci-environments`.
  - New: `.github/workflows/ci.yml`, `.github/protected-paths`, `compose.yaml`, `tools/ci_run.py`, `tools/tests/`, `contracts/schemas/ci-result.schema.json`, `apps/core/presence_core/migrations/`, `docs/delivery/worktree-workflow.md`, ADR-0035.
  - Changed: `Makefile`, `settings.py`, `tests.py`, `.env.example`, `.gitignore`, `pyproject.toml`, `uv.lock`, `tools/gate_selftest.sh`.
- Migrations: only Django's `contenttypes`. CI migrates every test database from empty.
- Rollback: revert the branch, then remove the local volume with `make services-down` followed by `docker volume rm` of `pgdata`. No deployed state.

## Versions (checked against official sources on 2026-11-25)
| Item | Pinned |
|---|---|
| PostgreSQL | 18.7, image `postgres:18.7-trixie@sha256:c6993038…1f0b6b` |
| psycopg[binary] | 3.3.9 |
| actions/checkout | v7.0.1 `3d3c42e5…b1` |
| actions/upload-artifact | v7.0.2 `cf430e03…d9` |
| Runner | `ubuntu-24.04` |

## Dependencies (review)
| Dependency | Licence | Maintenance | Why needed / duplication |
|---|---|---|---|
| psycopg[binary] | LGPL-3.0, used unmodified as a library (allowed; ADR-0035) | release 2026-10; the PostgreSQL adapter Django recommends | Django's PostgreSQL driver. No other driver is in the repository. |
| GitHub Actions above | MIT | official `actions/` organisation | Checkout and report upload. Pinned by commit SHA; a test enforces the pins. |

`uv audit` and `pnpm audit --audit-level high` report no known vulnerabilities.

## CI evidence
- **Run 1, red as designed:** <https://github.com/iamwaqargulzar/presence-os/actions/runs/45589488926>, merge commit `ebbc845`. Every gate passed. `protected-paths` failed because the PR changes `tools/ci_run.py`, `tools/gate_selftest.sh` and `tools/tests/*`, and the owner's label was not present. This is the expected behaviour.

  | Stage | Status | Exit | Seconds |
  |---|---|---|---|
  | static | passed | 0 | 3.2 |
  | unit | passed | 0 | 8.9 |
  | integration | passed | 0 | 19.4 |
  | security | passed | 0 | 5.8 |
  | protected-paths | **failed** | 1 | 0.0 |
  | gate-selftest | passed | 0 | 5.0 |

- **Run 2, green after the owner's label:** pending. The owner adds `owner-approved-protected-change` after review, and the run link is added here afterwards.

## Tests
- Gate self-test, in CI run 1 and locally. Each gate rejects a seeded violation:
  - format, lint and type errors (Python and TypeScript);
  - a failing unit test;
  - an invalid schema;
  - a broken migration (`test-integration`);
  - a known-vulnerable dependency (`django==4.2.0`, checked by `uv audit`);
  - a generated credential (pre-commit secret scan).
- `tools/tests/test_ci.py` covers:
  - redaction of credential-like environment values;
  - protected-path matching;
  - `ci-result.json` against its schema;
  - workflow policy: no `secrets.`, no `pull_request_target`, read-only permissions, and every `uses:` pinned by a 40-character SHA.
- Integration test: the test database name starts with `test_`, and migrations are applied.
- A full local `python3 tools/ci_run.py` passed every stage. No generated password appears in `reports/`.

## Security checks
- CI runs unreviewed pull-request code, so it has no repository secrets and read-only permissions, and never uses `pull_request_target`. Credentials are generated per run with `openssl rand`, masked, and redacted from stored logs.
- PostgreSQL binds to 127.0.0.1 only. Its password is required from the environment and has no default.
- Protected paths (`.github/protected-paths`) fail CI until the owner adds the label. A worker must never add it. That rule can't be enforced technically while the worker uses the owner's GitHub login; R0-012 removes that login.
- The repository is public (owner decision, 2026-11-25). `main` requires a pull request and a green `gates` check, also for administrators. Force pushes and deletion are off.

## Acceptance criteria
| Criterion | Result |
|---|---|
| Separate test database | yes, `test_*` per run; asserted by a test |
| Migrations executed in CI | yes, from empty, plus `makemigrations --check` |
| Unit, integration and security stages | yes |
| Secret scan | yes, gitleaks over the full history, plus the pre-commit hook |
| Dependency scan | yes, `uv audit`, `pnpm audit` |
| Report retention | yes, `ci-reports` artifact, 30 days |
| Branch protection documented | yes, ADR-0035; applied on `main` |
| Worktree workflow documented | yes, `docs/delivery/worktree-workflow.md`, linked from `AGENTS.md` |
| CI failure cannot be hidden by an agent | protected paths plus a required check. Limit: the worker still holds the owner's login until R0-012. |
| Green from a clean clone without production credentials | every gate is green in CI run 1. The full green run waits for the owner's label. |
| Environment rules written and checked | `docs/infrastructure/environments.md`; the localhost bind and the `test_` prefix are checked |

## Reviewer
No independent review. The owner reviews the protected files before adding the label.

## Cost/tokens/cache
Not measured. CI runs on free standard runners (public repository); one run takes about 2 minutes.

## Known limitations
- `uv audit` is experimental.
- The licence-check gate has no owning task.
- One database role owns and uses the tables; R0-003 splits it.

## Docs updated
`docs/infrastructure/environments.md`, `docs/delivery/testing-strategy.md`, `docs/delivery/worktree-workflow.md`, `docs/delivery/gates.md`, `AGENTS.md`, ADR-0035, `docs/DECISION_REGISTER.md`, `docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `CHANGELOG.md`, `apps/core/README.md`, `docs/runbooks/developer-bootstrap.md`, handoff files.
