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
