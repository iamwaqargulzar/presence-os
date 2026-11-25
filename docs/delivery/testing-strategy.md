# Testing Strategy

## Pyramid

- unit tests for domain logic;
- contract/schema tests;
- integration tests for database/workflows/connectors;
- RLS/tenant security tests;
- Action Broker authorization tests;
- browser/E2E for critical journeys;
- accessibility checks;
- migration/replay tests;
- security/fuzz/red-team tests;
- PresenceBench for AI coding/runtime profiles.

## Release blockers

- cross-tenant access;
- unauthorized side effect;
- broken rollback/migration;
- secret exposure;
- destructive duplicate action due retry;
- critical accessibility regressions in core journeys;
- deterministic workflow breakage.

## Test data

Synthetic fixtures by default.
Do not casually use production customer data in development.

## Flakiness

Flaky tests are defects; quarantine only with owner/expiry and a repair task.

## CI stages (R0-002, 2026-11-25)

`tools/ci_run.py` runs these in order, records each one in `reports/ci-result.json` (schema: `contracts/schemas/ci-result.schema.json`), and fails the run if any stage fails.

| Stage | Command | Covers |
|---|---|---|
| static | `make fmt-check lint typecheck` | format, lint, strict typing |
| unit | `make test` | Django unit tests, contract schemas, CI tool tests, web build and smoke test |
| integration | `make test-integration` | PostgreSQL from `compose.yaml`; migrations from empty; database tests (tag `integration`) |
| security | `make audit scan-secrets` | dependency vulnerabilities, secret scan of the whole history |
| protected-paths | `tools/ci_run.py protected-paths` | pull requests that change CI, gates, specs or agent rules need the owner's label |
| gate-selftest | `tools/gate_selftest.sh` | every gate still fails on a seeded violation |

Mark a Django test that needs the database with `@tag("integration")`; `make test` excludes it.

## Flaky tests

A flaky test is a defect. It may be quarantined only by the owner, with all three of these written in the pull request that quarantines it: the owner's name, an expiry date at most 14 days away, and the repair task. Quarantine means `@unittest.skip("quarantined until YYYY-MM-DD: <task>")`; a skip without that text is refused in review.
