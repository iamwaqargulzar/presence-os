# Implementation Report — R0-001 Repository and Toolchain

Written 2026-11-25. Spec: [R0-001](../../../specs/R0/R0-001-repository-toolchain.md). Decisions: [ADR-0034](../../../docs/adrs/ADR-0034-r0-001-tooling-choices.md).

- Starting commit: `5eecb64` (docs: specification baseline), on `main`.
- Resulting commit: the head of branch `feat/R0-001-repository-toolchain`. It contains this report, so it cannot name its own hash.
- Execution profile: operator-started and operator-watched interactive session; no controller yet (R0-011).
- Harness: Claude Code, desktop app.
- Model: Claude Opus 5.5 (`claude-opus-5-5`).
- Reasoning: default for the session.
- Task/spec hash: sha256 `27970d434b8b48fcfe136499c8a80a96649ee3a4144b1ae79aef0c682d13d79b` of `specs/R0/R0-001-repository-toolchain.md` (revision 2).
- Changed files: see `git diff --stat 5eecb64..feat/R0-001-repository-toolchain`. New code: `apps/core/` (Django), `apps/web/` (Next.js), `contracts/tests/`, `Makefile`, `.githooks/pre-commit`, `.env.example`, `.python-version`, `pyproject.toml`, `uv.lock`, `apps/web/pnpm-lock.yaml`, `tools/gate_selftest.sh`. `tools/build_docs.py` reformatted by ruff, and it now skips build and cache folders.
- Migrations: none. No database in this task (ADR-0034 point 7).
- Rollback: revert the branch. No deployed state, no data.

## Versions (checked against official sources on 2026-11-25)
Sources: python.org release API, nodejs.org `dist/index.json`, PyPI JSON API, npm registry, GitHub releases.

| Item | Pinned | Rule applied |
|---|---|---|
| Python | 3.15.2 | newest stable; Django 6.1.3 lists 3.15; compiled dependency rpds-py has cp315 wheels. No fallback needed. |
| Node.js | 26.13.1 | newest LTS line ("Lithium"). |
| Django | 6.1.3 | newest stable. |
| Next.js, React | 16.4.6, 19.3.1 | newest stable. |
| TypeScript | 7.0.2 | newest stable; `next build` and `tsc` pass with it, so no fallback to 6.0.3. |
| uv, pnpm | 0.13.10, 12.23.0 | newest stable. The local uv was updated from 0.13.7. |
| Biome | 2.6.8 | 2.6.9 was under one day old; pnpm cooldown kept (ADR-0034). |
| @types/node, @types/react | 26.6.6, 19.3.0 | same cooldown reason. |
| gitleaks | v8.30.1, image digest `sha256:c00b6bd0…bbb7f` | newest release. |
| PostgreSQL | not pinned here | arrives with R0-003. |

## Dependencies (review)
All direct dependencies are allowed licences under ADR-0033 section 3. `uv audit` and `pnpm audit --audit-level high` report no known vulnerabilities on 2026-11-25.

| Dependency | Licence | Maintenance | Why needed / duplication |
|---|---|---|---|
| django | BSD-3-Clause | release 2026-11-03 | core framework (ADR-0001) |
| jsonschema (dev) | MIT | release 2026-01-07; standard Python validator | contract schema test; no other validator in the repo |
| ruff (dev) | MIT | release 2026-11-19 | Python format and lint in one tool |
| mypy, django-stubs (dev) | MIT | releases 2026-10 | strict Python typing |
| next, react, react-dom | MIT | releases 2026-10/11 | web framework (ADR-0032) |
| typescript (dev) | Apache-2.0 | release 2026-07-08 | strict typing |
| @biomejs/biome (dev) | MIT OR Apache-2.0 | release 2026-11-15 | format and lint in one tool, replacing ESLint and Prettier |
| @types/node, @types/react, @types/react-dom (dev) | MIT | DefinitelyTyped | types only |
| gitleaks (container, not a package) | MIT | release 2026-03-21 | secret scan; runs isolated in Docker with the repository mounted |

Transitive Python packages: 20 in total, all in `uv.lock`. Web lockfile: 92 entries, all passed pnpm's supply-chain policy check.

## Tests
- `make check` passes: format, lint, type check (mypy strict 7 files, `tsc`), 6 Django tests (health, request ID, log injection, JSON formatter), 2 contract schema tests (all 16 schemas valid against draft 2020-12), web build and 2 smoke tests (page and request ID through a running `next start`).
- `tools/gate_selftest.sh` passes: each gate fails on a seeded violation (Python and TypeScript for format, lint and type check; a failing test and an invalid schema for test; a generated credential-shaped value for the pre-commit secret scan). Each failure was checked to be for the seeded reason.
- Clean clone: on 2026-11-25 a fresh clone of the branch, following only `docs/runbooks/developer-bootstrap.md`, reached green `make check`, `make audit`, `make scan-secrets` and the self-test. `make dev-core` and `make dev-web` both started, bound to 127.0.0.1 only, and returned 200 with an `X-Request-ID` header and one JSON log line per request.

## Security checks
- `make scan-secrets`: gitleaks found no leaks in the full history. The pre-commit hook ran on the task commit.
- No secret in source: `PRESENCE_SECRET_KEY` comes only from the environment; tests use the fixed value `insecure-test-only`, which is not used for anything.
- Health endpoint returns only `{"status": "ok"}` and accepts only GET and HEAD.
- Incoming `X-Request-ID` values are untrusted; only `[A-Za-z0-9._-]{1,64}` is kept, which prevents forged log lines (tested in both apps).
- No environment value reaches the browser bundle; no `NEXT_PUBLIC_` variables exist.
- No vendor AI SDK is imported.

## Acceptance criteria
| Criterion | Result |
|---|---|
| Reproducible bootstrap documented | yes, runbook tested from a clean clone |
| Frontend and backend start locally | yes |
| Format, lint, type and test commands exist | yes, Makefile gate contract |
| Lockfiles committed | yes, `uv.lock`, `apps/web/pnpm-lock.yaml` |
| Security and dependency scanning baseline | yes, gitleaks, `uv audit`, `pnpm audit` |
| CI can run without production credentials | yes; no gate needs a credential. CI itself is R0-002. |
| `AGENTS.md` honoured by agent tooling | `CLAUDE.md` loads it; no other agent tooling exists yet |
| Clean clone reaches green gates from the bootstrap document alone | yes |
| Contract schemas validated by a test | yes |

## Reviewer
No independent review. R0-001 is not security-critical. The owner should review the pull request.

## Cost/tokens/cache
Not measured; the desktop session does not expose usage to the worker. No paid service used.

## Known limitations
- `uv audit` is experimental in uv 0.13.10; its output may change.
- Not built here: lockfile-change scanning (R0-002 owns it) and the import-boundary gate (R0-007 owns it). The licence-check gate in `docs/delivery/gates.md` has no owning R0 task; licences were checked by hand above. Recorded as a gap in `docs/handoff/STATUS.md`.
- The web smoke test uses fixed port 3199; it fails if that port is busy.
- The pre-commit hook needs Docker; without it, commits are blocked (fails closed on purpose).

## Docs updated
`README.md`, `00_START_HERE.md`, `CHANGELOG.md`, `apps/*/README.md`, `packages/README.md`, `docs/DECISION_REGISTER.md`, `docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `docs/delivery/gates.md`, `docs/runbooks/developer-bootstrap.md`, ADR-0034, handoff files.
