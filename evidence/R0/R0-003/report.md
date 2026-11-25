# Implementation Report — R0-003 PostgreSQL Tenancy and Row Level Security

Written 2026-11-25. Spec: [R0-003](../../../specs/R0/R0-003-postgres-rls.md). Decisions: [ADR-0036](../../../docs/adrs/ADR-0036-postgres-roles-and-tenant-context.md). Design: [database tenancy and RLS](../../../docs/security/database-tenancy-rls.md).

- Starting commit: `00d2b03` (fix(docs): skip agent worktrees when building the context export), branch based on R0-002; R0-002's worktree secret-scan fix (`f208a1c`) merged in afterwards.
- Resulting commit: the head of branch `feat/R0-003-postgres-rls`. It contains this report, so it cannot name its own hash.
- Execution profile: autonomous side session started by the operator's coordinating session; the owner was away.
- Harness: Claude Code, desktop app.
- Model: Claude Opus 5.5 (`claude-opus-5-5`).
- Reasoning: default for the session.
- Task/spec hash: sha256 `5f902b7eebfc43156836b5fd55d7656a67c9f619de1ddb888ae0b3399b099c94` of `specs/R0/R0-003-postgres-rls.md` (revision 2).
- Changed files: see `git diff --stat 00d2b03..feat/R0-003-postgres-rls`. New: `infra/postgres/roles.sh`, `apps/core/presence_core/{tenancy,rls_testing,models}.py`, migration `0001_tenant_rls_fixtures.py`. Changed: `settings.py`, `tests.py`, `Makefile` (one line), `.env.example`, `.github/workflows/ci.yml` (two new generated credentials), `pyproject.toml` (RUF012 ignore for Django class attributes).
- Migrations: `presence_core` 0001 — default privileges for `presence_app`, two fixture tables, forced RLS and policies, composite foreign key. Reverse tested in the integration suite (`migrate presence_core zero` and forward again).
- Rollback: revert the branch; locally `docker compose down -v` removes the roles and data.

## What was built
- Roles `presence_migrator` (owns the schema) and `presence_app` (runtime), created idempotently by `infra/postgres/roles.sh` on `make services-up`.
- Two Django aliases; a router allows migrations only on `migrator`.
- `tenant_context()`: transaction-scoped `presence.tenant_id`, nested use restores the outer tenant; RLS write denials logged as `rls_denied` with tenant and SQLSTATE only.
- `protect_tenant_table()`: one migration operation for ENABLE + FORCE + policy, with a reverse.
- `unprotected_tenant_tables()` and a test that fails on any unprotected tenant table.
- `TenantIsolationTestCase.assert_crud_isolated()`: reusable SELECT/INSERT/UPDATE/DELETE/no-context checks for later modules.

## Dependencies
None added.

## Tests
- `make test-integration`: 12 tests pass against PostgreSQL 18.7, queries as `presence_app`:
  - role attributes: not superuser, no BYPASSRLS, no CREATEROLE/CREATEDB, owns no relation, not a member of the owner role, no TRUNCATE;
  - parent and child: cross-tenant SELECT hidden, UPDATE and DELETE affect 0 rows, INSERT into and moving a row to another tenant rejected, other tenant's row unchanged;
  - no tenant context: zero rows, deletes nothing, insert rejected;
  - joins and reverse relations show only own rows; a child cannot reference another tenant's parent;
  - same backend connection used for tenant A then B shows no leak; nested context restores; context cleared after an exception;
  - every tenant table protected; a seeded table without a policy, and one with a policy but no FORCE, are detected;
  - migration 0001 reverses and reapplies;
  - an RLS denial is logged without row contents.
- `make check` passes (format, lint, mypy strict, unit tests, web build and tests).
- `python3 tools/ci_run.py`: static, unit, integration, security and protected-paths pass.
- After merging `f208a1c`, rerun in this worktree: `make check`, `make scan-secrets` (9 commits scanned, no leaks), `make test-integration` (12 tests) and `tools/gate_selftest.sh` (all gates reject seeded violations, including the pre-commit secret scan) all pass.
- The first commit (`4634b15`) ran the pre-commit hook (no `--no-verify`), but before `f208a1c` the hook's gitleaks scanned nothing in a worktree; its diff was checked for secrets by hand, and `make scan-secrets` now covers it.

## Security checks
- Isolation is enforced by the database for both roles (FORCE), so the owner role cannot cross tenants by accident either.
- Foreign-key checks bypass RLS; the composite `(tenant_id, parent_id)` key prevents cross-tenant references and existence probing.
- Passwords come only from `.env` (generated as the bootstrap runbook says) or per-run generated CI values; none in source, fixtures or logs. `roles.sh` reads them with `\getenv`, not on the command line.
- PostgreSQL stays bound to 127.0.0.1 (unchanged `compose.yaml`).

## Acceptance criteria
| Criterion | Result |
|---|---|
| runtime role is not table owner | yes, tested |
| runtime role has no BYPASSRLS | yes, tested |
| tenant A cannot SELECT/INSERT/UPDATE/DELETE tenant B | yes, tested on both tables |
| pooled connection cannot leak tenant context | yes, same-connection test |
| missing tenant context fails closed | yes, tested |
| FORCE RLS used where selected by design | yes, on every tenant table (ADR-0036), tested by detection |
| RLS helper/test framework reusable | yes, `tenancy.py` and `rls_testing.py`; guide in the design doc |
| table without a policy detected automatically | yes, tested with a seeded table |
| isolation holds through joins and relationships | yes, tested |

## Reviewer
**Independent review of the role and policy migrations is still pending.** The spec's definition of done requires it for this security-sensitive task. Items for the reviewer: `infra/postgres/roles.sh`, migration `0001_tenant_rls_fixtures.py`, `tenancy.py`.

## Cost/tokens/cache
Not measured; the desktop session does not expose usage to the worker. No paid service used.

## Known limitations
- `presence_migrator` has CREATEDB for test databases; production provisioning must omit it.
- `django_migrations` and `django_content_type` were created before the default privileges and are not granted to `presence_app`.
- `.github/workflows/ci.yml` and `Makefile` are protected paths; the pull request needs the owner's label.

## Docs updated
`docs/security/database-tenancy-rls.md`, ADR-0036, `docs/DECISION_REGISTER.md`, `docs/runbooks/developer-bootstrap.md`, `CHANGELOG.md`, compiled exports.
