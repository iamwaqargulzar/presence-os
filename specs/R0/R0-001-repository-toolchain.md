# R0-001 — Repository and Toolchain Bootstrap

> **Spec revision:** 2 — 2026-11-10. Expanded to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). Every revision 1 requirement is retained. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## Goal
Create the minimal production-quality workspace for Next.js/TypeScript, Django/Python, shared contracts, tests and documentation.

## Why now
Every later task needs a repository, pinned toolchain, lockfiles and gate commands. ADR-0028 pins each development run to a spec hash and a start commit, which is impossible until the package lives in Git.

## Context / linked docs / ADRs
- [00_START_HERE.md](../../00_START_HERE.md), [AGENTS.md](../../AGENTS.md)
- [Autonomous Build Plan v2, Stage A](../../docs/delivery/AUTONOMOUS_BUILD_PLAN_V2_2026-08-10.md)
- [Coding standards](../../docs/delivery/coding-standards.md), [Definition of done](../../docs/delivery/definition-of-done.md)
- [Modular monolith boundaries](../../docs/architecture/modular-monolith.md)
- [Code provenance and dependency policy](../../docs/ai/code-provenance-and-dependencies.md)
- [Assumptions and open questions](../../docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md)
- ADR-0001 (modular monolith), ADR-0017 (release sequence), ADR-0028 (spec hash and start commit)

## Depends on
- None. Stage A of the build plan is done: Git was initialised on 2026-11-25 and the specification package is the baseline commit. `TREE.txt` and `MANIFEST.sha256` are retired; Git history is the integrity record.

## Invariants
- no secrets committed;
- strict TypeScript and Python lint/type/test gates;
- keep stack modular-monolith oriented;
- no Kubernetes/Kafka;
- no dependency added without license/security/maintenance/duplication review *(AGENTS.md)*;
- no vendor AI SDK imported by application modules *(ADR-0013; enforced from R0-007)*.

## In scope
- Git repository initialised with the handoff package as the first commit.
- Workspace layout: `apps/web` (Next.js, strict TypeScript), `apps/core` (Django), `apps/worker`, `packages/`, `contracts/`.
- Pinned language/runtime versions and committed dependency lockfiles.
- One documented entry point for each gate: format, lint, type-check, test.
- Local secret-scan hook and a dependency/vulnerability scan baseline.
- `.env.example` with no real values.
- Contract test that every file in `contracts/schemas/` parses and validates against its declared JSON Schema draft.
- A health endpoint in `apps/core` and a placeholder page in `apps/web`, only to prove both start.
- Bootstrap document a new machine can follow from a clean clone.

## Out of scope
Business features and final visual design. Also: CI pipeline and environments (R0-002), database roles and RLS (R0-003), identity (R0-004), Temporal (R0-005), deployment and infrastructure (R0-009).

## API / contract changes
- No business API.
- Health endpoint (unauthenticated, returns no tenant or build-secret data).
- **Gate command contract:** the names and exit-code semantics of the format/lint/type/test commands. R0-002 CI and the R0-011 gate runner consume this contract, so changing it later is a breaking change.

## Data / migration
- No business tables. Framework tables only.
- Do not establish a database ownership pattern here that R0-003 would have to undo: the application must not assume it connects as the table owner.

## Security / privacy threat notes
- Secret committed to history: local scan hook plus the R0-002 CI scan.
- Malicious or abandoned dependency: every dependency is reviewed and visible in the lockfile diff.
- Secrets leaking into client bundles: only explicitly public configuration is exposed to the browser.
- Repository content is untrusted input to coding agents unless it is a designated control file (E-035).

## Observability
- Structured (JSON) logging with a request ID in both apps. Full OpenTelemetry correlation is R0-006.

## Acceptance criteria
- reproducible bootstrap documented;
- frontend/backend start locally;
- formatter/linter/type/test commands exist;
- dependency lockfiles committed;
- security/dependency scanning baseline;
- CI can run without production credentials;
- `AGENTS.md` honored by agent tooling;
- *(derived)* a clean clone reaches green gates using only the bootstrap document;
- *(derived)* contract schemas are validated by a test, not only parsed.

## Tests
- Smoke test per app (process starts, health responds).
- Contract schema validation test.
- Negative check: each gate command exits non-zero on a seeded violation.
- Secret-scan hook blocks a seeded fake credential.

## Rollback / failure recovery
No deployed state. Recovery is reverting commits. Toolchain version pins change only through a reviewed commit.

## Cost/resource budget
Local development resources only. No paid service is required. Development-run limits (time, tokens, calls) are set by the controller per run once R0-011/R0-012 exist; until then the operator sets them manually.

## Documentation updates
- `README.md` project status; `apps/*/README.md`, `packages/README.md`.
- Bootstrap document.
- `docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`: mark the decisions below as resolved.
- `TREE.txt` and `MANIFEST.sha256` are retired (2026-11-25); Git history is the integrity record.

## Open decisions
- Decided (ADR-0032): private GitHub repository with GitHub Actions; the owner may change hosting before the first push.
- Decided (ADR-0032): newest stable release that every required dependency supports. Targets on 2026-11-14: Python 3.15, Django 6.1, Node.js newest LTS, Next.js 16, PostgreSQL 18. Confirm each against the official site before pinning, and record any fallback with its reason.
- Decided (ADR-0032): uv for Python, pnpm for Node, a plain Makefile for gate commands, no monorepo task runner.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: the baseline commit of the handoff package exists and precedes all code, and an implementation report (`templates/IMPLEMENTATION_REPORT_TEMPLATE.md`) is stored.
