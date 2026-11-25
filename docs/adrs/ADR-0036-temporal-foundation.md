# ADR-0036 — Temporal Foundation: Pins, Development Server and Payload Rules
Status: Accepted (2026-11-25). Made during R0-005 under the owner's delegation in ADR-0032 and ADR-0033.

## Context
R0-005 needs a Temporal service for local and CI use, a Python client and worker, and tests for determinism, cancellation, retries and worker restarts. ADR-0005 chose Temporal; ADR-0033 section 7 chose the newest stable server, the Python SDK and a separate PostgreSQL database in production. Versions below were checked against PyPI, GitHub releases and Docker Hub on 2026-11-25 and must be rechecked before the next upgrade.

## Decision
1. **Python SDK `temporalio==1.36.1`.** 1.37.0 was released on 2026-11-24, less than one day before; the one-day release cooldown (ADR-0034) applies to Python packages too. Licence MIT. It ships `abi3` wheels for CPython 3.11 and later and works on the pinned Python 3.15.2: imports, unit tests and integration tests pass. No toolchain change is needed.
2. **Development server: Temporal CLI image `temporalio/temporal:1.10.1`, pinned by digest** in `compose.yaml`. It runs `temporal server start-dev` (embedded server, SQLite in memory). Its port binds only to `127.0.0.1` (default 17233, `PRESENCE_TEMPORAL_PORT`); the web UI is off (`--headless`). History is lost when the container stops. This server is for development and CI only. Production uses the newest stable server (v1.32.2 on 2026-11-02) with PostgreSQL in its own database and role; R0-009 deploys it.
3. **No time-skipping test server.** The SDK's time-skipping environment downloads a test-server binary at run time without a pinned checksum. Instead: unit tests use the SDK `Replayer` against a committed history (no server) and run activities in the SDK `ActivityEnvironment`; integration tests run against the compose server with timeouts of one or two seconds. Revisit if the SDK can verify a pinned binary.
4. **Payload limit.** The client and worker share one data converter whose codec rejects any single payload over 64 KiB (`PayloadTooLargeError`). Larger data goes to the artifact store and history carries an `ArtifactRef` (sha256 and size). Temporal's own limits are much higher; 64 KiB keeps history small and makes "data in history" fail loudly in tests.
5. **Workflow IDs** are `{kind}/{tenant_id}/{business_key}`. A start uses conflict policy "use existing" and reuse policy "reject duplicate", so a repeated start returns the same run and a finished business key cannot start again.
6. **Package layout.** `presence_worker.workflows` never imports activity code; workflows call activities by name. A unit test checks the imports.

## Alternatives considered
- `temporalio/auto-setup` or a full server with PostgreSQL locally: closer to production, but more containers and memory for every developer. The production database setup belongs to R0-009.
- SDK time-skipping environment: faster timeout tests, but an unverified binary download (rejected above).
- Temporal's default payload limits only: oversized payloads would still be accepted until about 2 MiB, so tests would not catch the mistake.

## Consequences
- Dependency review (ADR-0033 section 3): `temporalio` (MIT) brings `nexus-rpc` 1.5.0 (MIT), `protobuf` 7.36.2 (BSD-3-Clause), `types-protobuf` (Apache-2.0) and `typing-extensions` (PSF-2.0). No duplication: no other workflow engine or protobuf library is in the repository. `uv audit` reports no known vulnerabilities on 2026-11-25. The SDK contains a compiled Rust core; its source is public in the same repository.
- `make services-up` now also starts Temporal; `make test-integration` runs the worker integration tests; `make test` runs the worker unit and replay tests.
- Shortcuts until other tasks land are listed in `evidence/R0/R0-005/report.md` (tenant context from R0-003, structured logs from R0-006, object store, authorization recheck from R1-003, outbox table).

## Security impact
Temporal is reachable only on the loopback interface. No secret is stored in workflow inputs or history; the codec limit and a history-size test guard against large tenant data in history. Signals carry no authority (ADR-0003): the reference workflow calls a revalidation step before its side effect.

## Cost/operational impact
Measured on 2026-11-25 on the development machine: see the report for the dev server's memory use. No paid service.

## Migration / rollback
Revert the commit and run `docker compose rm -sf temporal`. No business data is stored.

## Supersedes

## Superseded by
