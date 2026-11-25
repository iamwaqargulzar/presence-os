# R0-002 — Local/CI Environments and Quality Gates

> **Spec revision:** 2 — 2026-11-10. Expanded to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). Every revision 1 requirement is retained. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## Goal
Create isolated local/test/staging conventions and deterministic CI.

## Why now
Autonomous work is only trustworthy if gates run independently of the agent that wrote the code (E-039). Every later task's acceptance is proven through this pipeline.

## Context / linked docs / ADRs
- [Environments and release boundaries](../../docs/infrastructure/environments.md)
- [Testing strategy](../../docs/delivery/testing-strategy.md)
- [Secure development lifecycle](../../docs/security/secure-development-lifecycle.md)
- [Autonomous development security](../../docs/security/autonomous-development-security.md)
- [Re-audit edge cases E-030, E-039](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0026 (deterministic orchestration), ADR-0027 (no production secrets), ADR-0028 (spec hash and start commit)

## Depends on
- R0-001 (gate command contract).

## Invariants
- CI holds no production credentials and cannot reach production or the management network;
- gate results come from CI, never from an agent's own report;
- test data is synthetic;
- a flaky test is a defect: quarantine only with an owner, an expiry and a repair task.

## In scope
- Environment conventions for local, test/CI and staging: distinct databases, distinct credentials, distinct configuration.
- CI pipeline with ordered stages: format/lint/type, unit, integration (with database and migrations), security.
- Secret scan and dependency/vulnerability scan as blocking stages.
- Test report and build artifact retention.
- Branch protection expectations, documented and applied where the host supports it.
- Coding-agent worktree workflow: one worktree per task run, branch naming, cleanup.

## Out of scope
- Production deployment and release controller.
- Staging infrastructure itself (R0-009 provides the hosts).
- Sandbox enforcement for agents (R0-012).
- Canary environment.

## API / contract changes
- **CI result contract:** per-stage status, exit code, report location and commit SHA, in a machine-readable form the R0-011 gate runner can read.
- Extends the R0-001 gate command contract with integration and security stage commands.

## Data / migration
- A dedicated test database, created and destroyed per CI run.
- Migrations are executed from empty in CI on every run.
- From R0-003 onward, CI applies migrations as the migration role and runs tests as the runtime role.

## Security / privacy threat notes
- Agent hides a failing gate: required status checks come from CI, and CI configuration is a protected path a worker cannot edit in the same run (E-030, E-031).
- CI secret exfiltration: CI credentials are least-privilege and scoped to the repository and test resources.
- Untrusted pull-request code running with secrets: jobs that run unreviewed code get no secrets.
- Supply chain: lockfile changes are visible in the diff and scanned.

## Observability
- Each CI run records commit SHA, stage results, durations and report links.
- Retained artifacts are redacted of credentials before storage.

## Acceptance criteria
- separate test database;
- migrations executed in CI;
- unit/integration/security test stages;
- secret scan;
- dependency scan;
- artifact/test report retention;
- branch protection expectations documented;
- coding-agent worktree workflow documented;
- CI failure cannot be hidden by autonomous agent;
- *(derived)* CI is green from a clean clone with no production credential present;
- *(derived)* environment separation rules from `environments.md` are written down and checked where automatable.

## Tests
- Seeded failing unit test fails the pipeline.
- Seeded fake credential fails the secret scan.
- Seeded vulnerable dependency fails the dependency scan (or is reported per the documented severity policy).
- Migrations from empty succeed; a seeded broken migration fails the pipeline.
- A change to protected CI configuration from a worker branch is rejected or flagged.

## Rollback / failure recovery
Pipeline definitions are versioned; revert the commit. If the CI provider is unavailable, the same gate commands run locally and merges wait: no merge without recorded gate evidence.

## Cost/resource budget
CI minutes and storage depend on the provider chosen. Set a retention period for artifacts and a per-run time limit. No paid tier is assumed.

## Documentation updates
- `docs/infrastructure/environments.md` (concrete conventions).
- `docs/delivery/testing-strategy.md` (stage mapping).
- Worktree workflow document, referenced from `AGENTS.md`.
- `docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`.

## Open decisions
- **Decided (ADR-0033):** CI provider is GitHub Actions (ADR-0032).
- **Decided (ADR-0033):** test services start from the same Docker Compose file used locally.
- **Decided (ADR-0033):** CI artifacts are kept 30 days; a high or critical vulnerability blocks a merge unless a written, dated waiver exists.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: a recorded CI run from a clean clone, and recorded evidence of each seeded negative test failing the pipeline.
