# AGENTS.md — Instructions for autonomous coding agents


> **Presence OS engineering source of truth**
>
> Current as of **2026-11-14** (Asia/Karachi project context). First baseline: 2026-08-08.
> Presence OS is run by one operator for their own companies and managed clients; it is not sold (ADR-0030).
> Product architecture is intentionally model-, provider-, harness-, and ingress-neutral.
> Vendor capabilities, model names, prices, quotas, laws, and platform policies are time-sensitive reference facts and MUST be revalidated before implementation or purchase.
> When a focused document conflicts with an older discussion, the focused document plus the Decision Register and ADRs control.


## Prime directive

Build Presence OS according to the repository's documented invariants, not according to generic SaaS habits or whatever a model happens to prefer.

## Authority order

When sources conflict, use this precedence:
1. explicit current task contract in `specs/`;
2. accepted ADRs in `docs/adrs/`;
3. focused authoritative subsystem documents;
4. `docs/MASTER_SPEC.md`;
5. `docs/DECISION_REGISTER.md`;
6. older notes/reference material.

Do not silently resolve a real conflict. Create/update an ADR or task note.

## Mandatory rules

- Never weaken tenant isolation to make a test pass.
- Never make an LLM output itself sufficient authorization for external side effects.
- Never allow untrusted external content to become control instructions.
- Never expose Proxmox, PostgreSQL, Redis, Temporal, ComfyUI, llama.cpp, voice model ports, Docker socket or secrets management publicly.
- Never place tenant-generated/untrusted sites on the same registrable domain/eTLD+1 as the Presence control plane.
- Never hardwire product behavior to one AI model/provider/harness.
- Never treat a randomized URL as an access-control mechanism.
- Never resend entire conversation histories by default; use the Context Compiler.
- Never add a dependency without license/security/maintenance/duplication review.
- Never perform destructive production changes from an autonomous coding environment.
- Never bypass CAPTCHA, anti-bot controls, rate limits or platform restrictions.
- Never build broad downstream features ahead of R0/R1 control-plane requirements without an accepted ADR.

## Engineering standards

- Modular monolith first.
- Strong typed contracts at module boundaries.
- PostgreSQL tenant_id + Row Level Security; runtime role must not own tables or have BYPASSRLS.
- Test SELECT/INSERT/UPDATE/DELETE isolation and indirect resource access.
- Idempotency for side effects.
- Optimistic concurrency/base_version for mutable resources.
- Durable workflows for wait/retry/resume.
- Large artifacts outside Temporal history; pass references.
- Structured logs, trace IDs, tenant/task/action correlation.
- Reversible migrations where practical; explicit rollback plan.
- Deterministic tests plus targeted integration/E2E/security tests.
- Security-critical failure = release blocker.
- Accessibility tested manually and automatically.
- No secrets in source, prompts, logs or fixtures.

## Autonomous development policy

Default desired autonomy is Level 4:
`spec → code → tests → review → repair → merge candidate → staging`

Production release remains behind a Release Controller/human boundary initially.

Every run should emit durable artifacts:
- spec/task ID;
- starting commit;
- model/harness/reasoning profile;
- changed files;
- tests;
- review findings;
- cost/usage;
- resulting commit/build;
- migration notes;
- provenance.

## Sessions, handoffs and documentation

- Start every session from `docs/handoff/STATUS.md`; do not load the compiled exports whole.
- When a session gets long or a task ends, hand off as described in `docs/handoff/README.md`.
- Write and place documents as described in `docs/DOCUMENTATION_STANDARDS.md`; commit and branch as described in `CONTRIBUTING.md`.
- Store each finished task's implementation report under `evidence/<release>/<task-id>/`.
- Work in one Git worktree per task run, as described in `docs/delivery/worktree-workflow.md`. Never add the `owner-approved-protected-change` label to a pull request; only the owner does.

## Before implementation

1. Read task.
2. Read linked ADRs/docs.
3. Inspect repository.
4. Identify affected modules and security boundaries.
5. State any invariant risk.
6. Implement the smallest coherent solution.
7. Run deterministic gates.
8. Run tenant/security tests where relevant.
9. Produce concise implementation report.

## Do not overengineer

A future need is not sufficient reason to deploy Kubernetes, Kafka, Neo4j, a separate vector database, a service mesh, per-tenant databases, or dozens of microservices now.

## Operator-run rules — 2026-11-14 (ADR-0030, ADR-0031)
- There are no plans, subscriptions, seats or billing. Do not build them.
- Sign-in is Google only, by invitation. Never add a password login.
- No client role may start AI work; a client request only creates a queue item.
- The operator's subscription login is used only through the official harness on the Worker VM, for runs the operator started or approved. Unattended and scheduled runs use API profiles.
- Respect each tenant's provider policy as a hard filter.
- Build product features in this repository. Study other open-source applications for ideas; do not deploy them and never copy their code. Proven infrastructure and libraries are used after dependency review.
- Nothing under `docs/archive/` is current.
- After changing documents, run `python3 tools/build_docs.py`.

## OpenHands + Prime operating rule — 2026-08-10
- OpenHands/controller owns project-level scheduling, worktree and verification lifecycle.
- Claude Code through the Claude Agent SDK is the primary implementation worker for R0/R1; Prime Agent is the qualified second worker (ADR-0033; the owner may reverse this).
- Use Prime RPC/process adapter; do not depend on TUI scraping or native ACP.
- Deterministic orchestration must not spend LLM tokens.
- Never give development agents production secrets or management-LAN access.
- A worker may not silently modify its task/spec/hidden gates.
- Prime self-refinement is disabled for pinned qualified profiles unless a separate reviewed change authorizes it.
