# Gates

Current as of 2026-11-25. A gate is a check that must pass before work moves on. A worker saying "done" is never a gate.

## 1. Every change (run by CI and by the development controller in a clean context)

| Gate | Fails when |
|---|---|
| Format | code is not formatted |
| Lint | a lint rule is broken |
| Type check | strict TypeScript or Python typing fails |
| Unit and integration tests | any test fails; flaky tests count as defects |
| Contract schemas | a file in `contracts/schemas/` does not validate |
| Tenant isolation suite | any cross-tenant SELECT/INSERT/UPDATE/DELETE or indirect access succeeds |
| Authorization tests | an action runs without a valid grant, or a client role starts AI work |
| Migrations | a migration has no tested reverse or documented rollback |
| Import boundary | a vendor AI SDK is imported outside the adapter layer |
| Secret scan | a credential pattern appears in code, fixtures, logs or artifacts |
| Dependency vulnerability scan | a known serious vulnerability is introduced |
| Licence check | a dependency licence is outside the allowed list |
| Lockfile change review | a dependency is added or changed without review |
| Protected paths | a worker changed its task contract, protected tests, gate or sandbox configuration |
| Provenance | spec hash, start commit, versions, diff and gate results are not recorded; or copied third-party code is found |
| Accessibility checks | a critical regression in a core journey |

Gate command names and exit codes are fixed in R0-001 and consumed by R0-002 and R0-011. Each is a target in the root `Makefile`; exit code 0 means pass, any other code means fail. Renaming a target or changing its meaning is a breaking change.

| Make target | Gates it runs |
|---|---|
| `make fmt-check` | Format (ruff, Biome) |
| `make lint` | Lint (ruff, Biome) |
| `make typecheck` | Type check (mypy strict, `tsc`) |
| `make test` | Unit tests, contract schemas, web build and smoke test |
| `make check` | All four above, in order |
| `make audit` | Dependency vulnerability scan (`uv audit`, `pnpm audit --audit-level high`) |
| `make scan-secrets` | Secret scan of the whole Git history (gitleaks) |
| `make scan-staged` | Secret scan of staged changes; run by the pre-commit hook |

`tools/gate_selftest.sh` proves each gate fails on a seeded violation. The other gates in the table above (tenant isolation, authorization, migrations, import boundary, licence check, lockfile review, protected paths, provenance, accessibility) are added by the tasks that introduce what they check.

## 2. Every task

- The task's acceptance criteria and tests pass.
- [Definition of done](definition-of-done.md) is met.
- An implementation report is stored (`templates/IMPLEMENTATION_REPORT_TEMPLATE.md`).
- Security-critical tasks have a recorded independent review.
- Open decisions the task needed are recorded in an ADR.

## 3. Development run (controller)

- Sandbox verified at run start, or the run does not start.
- A run on an `OPERATOR_SUBSCRIPTION` profile needs a recorded operator start or approval.
- Limits on time, tokens, calls, child agents and retries; hitting one ends the run as failed, never as success.

## 4. Release exit

- R0: `specs/R0/R0-010-exit-audit.md`.
- R1: `specs/R1/R1-010-kernel-exit.md`.
- Release blockers from the [testing strategy](testing-strategy.md): cross-tenant access, unauthorized side effect, broken rollback, secret exposure, duplicate destructive action on retry, critical accessibility regression, workflow determinism breakage.

## 5. Production

- Development agents can reach staging only.
- A production release is a separate action authorized by the operator.
- A restore drill has been recorded before client data is live.

## 6. Runtime (the product itself)

- Every external side effect passes the Action Broker with a valid AuthorizationGrant, a limit check and a budget reservation.
- A client request only creates a queue item.
- Publication of content that a tenant marks for approval waits for the client's artifact-bound approval.
