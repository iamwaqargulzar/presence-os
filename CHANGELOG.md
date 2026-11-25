# Changelog

## 2026-11-25 — R0-005 Temporal foundation

- Temporal worker package `apps/worker/presence_worker`: typed contracts, reference workflow (checkpointed draft, human wait with timeout, revalidated idempotent effect), client with 64 KiB payload limit and workflow ID convention; `make dev-worker`.
- `temporalio` 1.36.1 added (MIT, review in ADR-0036). Temporal development server 1.10.1 in `compose.yaml`, bound to 127.0.0.1.
- Unit and replay tests run in `make test`; integration tests (timeout, cancel, retry, duplicate start, oversized payload, worker kill and restart) run in `make test-integration`.
- Workflow conventions, versioning and worker deployment policy, outbox design: `docs/architecture/workflows-and-temporal.md`; new guide `docs/architecture/how-to-write-a-workflow.md`. ADR-0036.

## 2026-11-25 — R0-002 CI and environments

- GitHub Actions workflow `.github/workflows/ci.yml` runs `tools/ci_run.py`: static, unit, integration, security, protected-paths and gate-selftest stages; result contract `contracts/schemas/ci-result.schema.json`; reports kept 30 days.
- PostgreSQL 18.7 from `compose.yaml` for local and CI integration tests; psycopg 3.3.9 added (LGPL-3.0, review note in ADR-0035); `django.contrib.contenttypes` so migrations run from empty.
- New gate targets: `test-integration`, `services-up`, `services-down`. Gate self-test now also covers a broken migration and a known-vulnerable dependency.
- Protected paths listed in `.github/protected-paths`; changes need the owner's label.
- Added `docs/delivery/worktree-workflow.md` (linked from `AGENTS.md`), concrete environment conventions, CI stage mapping and the flaky-test rule. ADR-0035.

## 2026-11-25 — R0-001 repository and toolchain

- Pinned toolchain: Python 3.15.2 (uv 0.13.10), Node 26.13.1 LTS (pnpm 12.23.0), Django 6.1.3, Next.js 16.4.6, React 19.3.1, TypeScript 7.0.2. Lockfiles committed.
- `apps/core`: Django skeleton with `/healthz`, request-ID middleware and JSON logs. `apps/web`: Next.js placeholder page with a request-ID proxy.
- Root `Makefile` holds the gate command contract; `tools/gate_selftest.sh` proves each gate fails on a seeded violation.
- Pre-commit secret scan (gitleaks, digest-pinned image), `.env.example`, contract schema test.
- ADR-0034: tooling choices; Node pinned without Corepack; pnpm release cooldown kept.
- Added `docs/runbooks/developer-bootstrap.md`; gate targets listed in `docs/delivery/gates.md`.
- `tools/build_docs.py` reformatted by ruff (no behaviour change).

## 2026-11-25 — repository baseline

- Git initialised on `main`; the specification package is the baseline. `TREE.txt` and `MANIFEST.sha256` retired; Git history is the integrity record.
- Ponytail plugin (5.3.3) installed by the owner; `CLAUDE.md` says project rules win over its minimal-change style.
- Added: `CLAUDE.md`, `CONTRIBUTING.md`, `SECURITY.md`, `.gitattributes`, `.github/CODEOWNERS`, `.github/pull_request_template.md`, `docs/DOCUMENTATION_STANDARDS.md`, `evidence/README.md`.
- Added the session handoff system: `docs/handoff/README.md` (protocol), `docs/handoff/STATUS.md` (living status), `docs/handoff/log/` (session handoffs), `templates/SESSION_HANDOFF_TEMPLATE.md`.
- Moved: `OPENHANDS_START_HERE.md` → `docs/ai/openhands-controller-start.md`; `PRIME_WORKER_TASK_TEMPLATE.md` → `templates/`; `BOOTSTRAP_CHECKLIST.md` → `docs/archive/BOOTSTRAP_CHECKLIST_v2.md` (replaced by `STATUS.md`).
- Fixed stale text saying the primary development worker was undecided (ADR-0033 decided it).

## 2026-11-15 — R2 and R3 task contracts

- R2 (Presence Intelligence): 17 task contracts written, `specs/R2/R2-001` to `R2-017`, with the task list and dependency order in `specs/R2/README.md`.
- R3 (Business Presence): 14 task contracts written, `specs/R3/R3-001` to `R3-014`, with the task list and dependency order in `specs/R3/README.md`.
- All are revision 1, written to the full template before R1 is built. Each must be rechecked against the R1 (and for R3 also the R2) implementation reports before its task starts. This is earlier than `specs/R1/R1-010-kernel-exit.md` and the old R2 README intended ("only after R1 reality is known"); the recheck rule is the answer to that.
- Every R2- and R3-tagged edge case in the register is assigned to a contract. The exit contracts (R2-017, R3-014) list them.
- No owner decision was invented. Undecided points are marked "Decision required" with a proposed default, and collected in `docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md` (R2/R3 section).
- Where sources differed, the newer or higher source was followed: image generation goes through the AI Capability Gateway, cloud by default (release plan, ADR-0030), not "local image generation"; R3 is built in-house (ADR-0030, ADR-0031), not as an integration of third-party applications as the 2026-11-10 research note suggested; push notifications are in R2 (owner decision), although `docs/architecture/notifications-and-attention.md` still says "push later".
- Gap found: tenant export and offboarding (E-058, E-059, E-082, E-086, tagged "R1+") has no contract in R0 to R3. Recorded as an open decision in R3-014.
- `00_START_HERE.md`, `README.md`, `PROJECT_MANIFEST.yaml`, `specs/README.md` updated to list the new contracts.

## 2026-11-15

- Owner decision: scheduled tasks prepare and wait by default; unattended only per task for low-risk work.
- Owner decision: mobile surface is the installable web console with push notifications.
- Owner decision: social connector order is Meta (Facebook and Instagram), then LinkedIn.
- Owner decision: low-cost model is DeepSeek V4.1 Flash for now, replaceable by configuration; default data limits for new clients recorded.
- Owner decision: budgets in US dollars with rupees shown for reading; starting caps recorded.
- Owner decision: clients cannot revoke or pause the operator's access; the operator ends service from the console.
- Owner decision: the operator console is `console.iamwaqargulzar.com` for the time being; the domain for client sites and previews is still to be chosen.
- Owner decision: the second backup copy is an encrypted USB drive on the server for the time being; cloud storage replaces it before the first client's production data.
- Owner decision: the operator's personal profile is its own tenant.
- Owner decision: the model gateway is built in-house.
- ADR-0033 added: technical defaults for R0 and R1. The "Decision required" lines it settles in the task contracts are replaced with the decision. AGENTS.md: Claude Code is the primary development worker, Prime second.
- Contracts: `OUTCOME_UNKNOWN` added to the Action states; `created_at` added to the authorization grant; `id` added to the tenant access grant.
- Owner decision: clients without a Google account create one on their own email, or have no login and the operator records their approval.

## 2026-11-14 — operator-run model

- ADR-0030 accepted: Presence OS is run by one operator for their own companies and managed clients; it is not sold. Plans, subscriptions, seats, billing, AI tiers sold in plans and AI Compute Units removed.
- Client roles (viewer, requester, approver); no client role can start AI work.
- Google sign-in only, by invitation.
- Operator console on its own hostname through the Cloudflare Tunnel; Proxmox/SSH by local network or the operator's WireGuard VPN.
- Cloud-only inference by default; GPU host optional.
- Task-class model routing (frontier and low-cost API), credential classes, tenant provider policy.
- Claude Code through the Claude Agent SDK added as a worker harness, with an operator start/approve gate.
- ADR-0031: social platform connectors are built in-house; the same-day proposal to self-host Postiz was withdrawn.
- Build preference recorded: features built in-house; other applications studied, not deployed or copied.
- Specs: R0-004, R0-007, R0-009, R0-011, R0-012, R1-001, R1-007 amended (revision 3); R1-004, R1-012, R1-013 rewritten (revision 4); small wording fixes in R1-006, R1-010, R1-011.
- Edge-case register extended from E-060 to E-090; E-002, E-004, E-005, E-008, E-052 reworded for the new model.
- New: `docs/delivery/gates.md`, `tools/build_docs.py`, `docs/archive/`.
- Rewritten: `00_START_HERE.md`, `README.md`, `PROJECT_MANIFEST.yaml`, `docs/DECISION_REGISTER.md`, `docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, and the focused documents on limits/budgets, tenant AI, model changes, tenant lifecycle, roles, onboarding, operator experience and vision.
- Archived: go-to-market and competitive documents, `plan-ai-entitlement.schema.json`, the legacy Codex handoff prompt, the August audit and changelog.
- Research: `docs/research/OPEN_SOURCE_LANDSCAPE_OPERATOR_RUN_2026-11-14.md` added (survey for the operator-run model). Edge cases E-091 to E-094 added from it. AgenticOS was read directly and its section corrected.
- ADR-0032 added: toolchain versions, package managers and repository. R0-001 has no blocking decisions left.

## 2026-11-10

- All R0 and R1 task contracts expanded to the full template (revision 2).
- `docs/research/GITHUB_LANDSCAPE_2026-11-10.md` added.

## 2026-08-10

- First v2 specification baseline. See `docs/archive/CHANGELOG_2026-08-10.md`.
