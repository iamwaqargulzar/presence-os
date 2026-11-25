# Implementation Report — R0-005 Temporal Durable Workflow Foundation

Written 2026-11-25. Spec: [R0-005](../../../specs/R0/R0-005-temporal-foundation.md). Decisions: [ADR-0036](../../../docs/adrs/ADR-0036-temporal-foundation.md).

- Starting commit: `1f5d8a4` (docs(R0-002): record public repository and branch protection on main), on branch `feat/R0-002-ci-environments`.
- Resulting commit: the head of branch `feat/R0-005-temporal-foundation`. It contains this report, so it cannot name its own hash.
- Execution profile: autonomous side session started by the operator's coordinating session; operator away. No controller yet (R0-011).
- Harness: Claude Code, desktop app. Model: Claude Opus 5.5 (`claude-opus-5-5`). Reasoning: default for the session.
- Task/spec hash: sha256 `25be7fc4987814afb96b70652643026e0fc26cd628d7cedad88f2eab018ced95` of `specs/R0/R0-005-temporal-foundation.md`.
- Changed files: `apps/worker/presence_worker/` (new), `apps/worker/README.md`, `compose.yaml`, `Makefile`, `pyproject.toml`, `uv.lock`, `.env.example`, `.gitignore`, docs listed below.
- Migrations: none. The development server keeps history in memory.
- Rollback: revert the branch; `docker compose rm -sf temporal`. No business data.

## Versions (checked against official sources on 2026-11-25)
Sources: PyPI JSON API, GitHub releases of `temporalio/temporal`, `temporalio/cli` and `temporalio/sdk-python`, Docker Hub.

| Item | Pinned | Rule applied |
|---|---|---|
| `temporalio` (Python SDK) | 1.36.1 | 1.37.0 released 2026-11-24, under one day old: cooldown (ADR-0034). abi3 wheels work on Python 3.15.2. |
| Temporal CLI image (dev server) | `temporalio/temporal:1.10.1`, digest `sha256:b228dadf…41225` | newest CLI release (2026-11-13). |
| Temporal server (production) | not deployed here | newest stable is v1.32.2 (2026-11-02); R0-009 deploys it with PostgreSQL. |

## Dependencies (review)
`uv audit` reports no known vulnerabilities across 25 packages on 2026-11-25. No duplication: there is no other workflow engine or protobuf library in the repository.

| Dependency | Licence | Maintenance | Why needed / duplication |
|---|---|---|---|
| temporalio 1.36.1 | MIT | official Temporal SDK; frequent releases (latest 2026-11-24) | workflow engine client and worker (ADR-0005, ADR-0033) |
| nexus-rpc 1.5.0 (transitive) | MIT | Temporal project | required by the SDK |
| protobuf 7.36.2 (transitive) | BSD-3-Clause | Google | wire format used by the SDK |
| types-protobuf (transitive) | Apache-2.0 | typeshed | type stubs |
| typing-extensions 4.16.0 (transitive) | PSF-2.0 | Python core developers | typing backports |
| Temporal CLI container (not a package) | MIT | Temporal project | development and CI server only |

## Tests
- `make check` passes: format, lint, mypy strict (now includes `apps/worker`), Django and web tests, and 7 worker unit tests: one effect per idempotency key, checkpointed stage not recomputed, tenants do not share effect records, oversized payload rejected, unsafe tenant IDs rejected, workflow module does not import activities, and **replay of the committed history** (`tests/histories/reference_v1.json`) against current code.
- `make test-integration` passes (8 worker integration tests against the compose server, about 45 s): approve path (history under 64 KiB while the draft is above it, history replays), duplicate start returns the same run, human-wait timeout, cancel during the human wait, cancel during the activity (activity sees the cancel and cleans up), retry keeps the same tenant context (attempts 1 and 2 both log the workflow's tenant), oversized start rejected, worker killed and restarted.
- **Recovery test for R0-010** (`test_killed_worker_resumes_without_repeating_checkpoint`): a worker process (`python -m presence_worker`) completed `prepare_draft`, then was killed with SIGKILL while the workflow waited for a human decision. A new worker process started, the decision was signalled, and the workflow completed. History shows `prepare_draft` and `apply_effect` each scheduled exactly once. Result: pass, 2026-11-25.
- `python3 tools/ci_run.py`: static, unit, integration, security and protected-paths stages pass. `gate-selftest` fails on one line, "secret hook passed a seeded credential". Cause, not from this task: in a Git worktree, `.git` is a file pointing outside the folder mounted into the gitleaks container, so gitleaks prints "not a git repository", scans 0 commits and exits 0. The same happens without any R0-005 change. CI uses a normal checkout and is not affected. Follow-up below.

## Security checks
- Temporal binds only to `127.0.0.1` (`PRESENCE_TEMPORAL_PORT`, default 17233); the web UI is off.
- Payloads above 64 KiB are rejected by the shared codec; the integration test checks that a larger draft stays out of history.
- Signals carry no authority: the decision is recorded and `revalidate()` runs before the effect (ADR-0003).
- Tenant and profile IDs are validated (`[A-Za-z0-9._-]`, 1 to 64 characters) because they become part of workflow IDs and file paths.
- No secret in source, history or fixtures; the committed history holds only test IDs and generated text.
- The SDK time-skipping server is not used because it downloads an unpinned binary (ADR-0036).

## Acceptance criteria
| Criterion | Evidence |
|---|---|
| workflow/activity packages separated | `workflows.py` calls activities by name; unit test checks it imports no activity code |
| deterministic workflow test | replay unit test on the committed history; integration approve test replays a fresh history |
| idempotent activity example | `apply_effect` with key `{workflow_id}/apply`; unit test |
| cancellation | two integration tests (during wait, during activity) |
| checkpoint/artifact-reference pattern | `prepare_draft` stores the draft by sha256 and returns `ArtifactRef`; unit and restart tests |
| versioning/deployment policy documented | `docs/architecture/workflows-and-temporal.md` |
| large payload not stored in history | codec limit, unit and integration tests |
| worker killed mid-workflow resumes (R0-010) | recovery test above |
| tenant context matches after retry | integration retry test |

## Cost/resource budget
Development server baseline on 2026-11-25, idle after the test run: about 134 MiB memory (`docker stats`), image 180 MB, no volume (history in memory). Production with PostgreSQL will need more; R0-009 should measure there.

## Reviewer
No independent review. The owner should review the pull request; it touches protected paths (`compose.yaml`, `Makefile`), which need the owner's label.

## Cost/tokens/cache
Not measured; the desktop session does not expose usage. No paid service used.

## Shortcuts (marked `shortcut:` in code)
- `tenant_scope()` only logs the tenant; R0-003 plugs in the transaction and `set_config` there. The interface (`TenantContext` in every input) does not change.
- `revalidate()` allows everything until the Action Broker (R1-003).
- Artifacts and effect records are local files under `var/`; object store and PostgreSQL in R0-009/R1.
- Worker logs are plain text with the correlation fields; JSON logs and OpenTelemetry in R0-006.
- Outbox: design only (in the workflows doc), because the table needs row-level security from R0-003.

## Known limitations
- Metrics from the spec's Observability section (queue backlog, failures and retries, workflow duration) and spans are not built; R0-006 owns telemetry.
- ADR number 0036 was free on 2026-11-25, but parallel sessions (R0-003, R0-009) may also pick it; renumber at merge if they collide.
- `temporalio` 1.37.0 was skipped for the cooldown; upgrade in a later change.
- Integration tests use real one- or two-second timeouts and take about 45 s.
- Follow-up: `make scan-staged` silently passes inside Git worktrees (see Tests). Needs a fix in the protected `Makefile`, for example mounting the common Git directory, or failing when gitleaks reports an error.

## Docs updated
`docs/architecture/workflows-and-temporal.md`, new `docs/architecture/how-to-write-a-workflow.md`, `apps/worker/README.md`, `docs/DECISION_REGISTER.md`, `CHANGELOG.md`, ADR-0036; compiled exports rebuilt with `tools/build_docs.py`.
