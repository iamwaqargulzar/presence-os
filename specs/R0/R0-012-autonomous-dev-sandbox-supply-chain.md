# R0-012 — Autonomous Development Sandbox and Supply-Chain Controls

> **Spec revision:** 3 — 2026-11-14. Amended by [ADR-0030](../../docs/adrs/ADR-0030-operator-run-agency-deployment.md); the "ADR-0030 amendments" section overrides any conflicting text below it. Revision 2 (2026-11-10): Expanded to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). Every revision 1 requirement is retained. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## ADR-0030 amendments (revision 3)
**Added to scope**
- The operator's subscription login used by the Claude Code worker is a **development credential confined to the Worker VM**. It is not a production credential, and the "no production credentials" invariant is unchanged.
- The login is stored outside the task workspace, readable only by the harness process account, never copied into worktrees, artifacts, logs or session records, and covered by the redaction scanner.
- Egress allow list gains the model providers' API endpoints required by the configured harnesses, and nothing broader.

**Changed acceptance criteria**
- The credential sweep exempts exactly one item, the harness login at its documented path, and fails on anything else.
- *(added)* a worker task cannot read the harness login through its allowed tools and paths (tested with a seeded attempt);
- *(added)* revoking and re-issuing the harness login is documented and performed once.

**Added threat notes**
- Prompt injection causing the worker to print or exfiltrate its own login: contained by path restrictions, egress allow list and redaction; residual risk recorded.

## Goal
Make OpenHands/Prime autonomous development safe enough for sustained R0/R1 implementation.

## Why now
Prime's worker lifecycle is not a security sandbox and OpenHands headless mode auto-approves actions. The surrounding environment is the only boundary, and it must be in place before autonomy is sustained across R1's security-critical tasks.

## Context / linked docs / ADRs
- Edge cases added 2026-11-14 that this task must cover: E-087, E-088 ([register](../../docs/PROJECT_REAUDIT_2026-08-10.md)).
- [Autonomous development security boundary](../../docs/security/autonomous-development-security.md)
- [Code provenance and dependency policy](../../docs/ai/code-provenance-and-dependencies.md)
- [Secure development lifecycle](../../docs/security/secure-development-lifecycle.md)
- [Network and service exposure](../../docs/security/network-and-service-exposure.md)
- [Re-audit edge cases E-025, E-026, E-030, E-031, E-034 to E-040](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0016 (gVisor), ADR-0027 (no production secrets), ADR-0028 (spec hash and start commit)

## Depends on
- R0-002
- R0-008
- R0-009
- R0-011

## Execution constraint
Network and host-level parts of this task are applied by the operator (see R0-009). A worker must not be asked to configure or weaken the sandbox that contains it; sandbox profile and gate policy files are protected paths.

## Invariants
- development agents receive no production credentials of any kind (database, Redis, Temporal, object store, Cloudflare/DNS, tenant OAuth, billing, SSH);
- no reachability from the agent workspace to Proxmox, the management LAN or production services;
- an unrestricted host Docker socket is never exposed to an agent-controlled process;
- an agent may not silently broaden dependency trust;
- hitting a limit means BUDGET_EXHAUSTED or TIMED_OUT, never success.

## In scope
- SandboxProfile: definition, versioning and automated provisioning of the development-worker environment (container/gVisor/VM composition on the Worker VM).
- Egress policy: allow required source and dependency registries through controlled egress; deny private LAN, metadata endpoints, Proxmox, inference-management ports and production control-plane addresses; web research off unless task policy enables it.
- GatePolicy wiring: lockfile-change visibility, package-source policy, vulnerability scan, secret scan, license check.
- Protected paths: task contracts, protected/hidden tests, gate and sandbox configuration.
- Redaction scanner for session and event artifacts before long-term storage.
- Hard limits: wall time, model calls/turns, tokens, tool calls, root/child agent count, child depth, retries, build/runtime resources.
- Orphan cleanup for processes and sessions.
- Provenance record per run: spec hash, start commit, versions, diff, gate results, reviewer.
- Kill drill: controller and worker each killed mid-run, then cleanup and recovery verified.

## Out of scope
- Tenant runtime sandboxing for hosted properties (R3).
- Full SLSA-level provenance and SBOM publication (progressive; required by release stage, not R0).
- A general-purpose secrets manager.
- Sandboxing for harnesses other than Prime beyond what the profile gives for free.

## API / contract changes
- SandboxProfile and GatePolicy definitions referenced by `development-run.schema.json` (`sandbox_profile_id`, `gate_policy_id`). Add contract sketches under `contracts/schemas/` if they cross module boundaries.
- Provenance record format.

## Data / migration
- SandboxProfile and GatePolicy revisions stored as versioned records or files; a run references an exact revision.
- Provenance and redacted session artifacts stored by reference with a retention period.

## Security / privacy threat notes
- Malicious dependency install script executing inside the sandbox (E-034): contained by egress and no-credential rules, caught by scans.
- Docker socket as host root (E-038).
- Agent reaching the LAN (E-037).
- Credentials in session JSONL (E-036).
- Test or spec tampering (E-030, E-031).
- Environment variables inherited from the operator's shell leaking credentials into the sandbox.
- Raw traces shared outside the project: never by default.

## Observability
- Denied egress attempts logged with run ID and destination.
- Limit hits, redaction hits, protected-path violations and scan findings recorded per run.
- Orphan detection count.

## Acceptance criteria
- dedicated development-worker sandbox profile documented and automated;
- agent workspace cannot reach Proxmox/management LAN/production services;
- no production credentials injected;
- unrestricted host Docker socket is not exposed to agent-controlled process;
- egress allow/deny policy tested;
- dependency lockfile/vulnerability/secret/license checks wired into gate policy;
- protected test/spec paths enforced for controlled tasks;
- session/event artifact redaction scanner;
- hard run limits for time/tokens/calls/children/retries/resources;
- orphaned process/session cleanup test;
- provenance includes spec hash, start commit, versions, diff, gates and reviewer;
- restore/cleanup drill succeeds after intentionally killed worker/controller;
- *(derived)* the sandbox environment contains no credential-bearing environment variable, file or SSH key, verified by an automated check at run start.

## Tests
Run from inside the sandbox, with results stored as evidence:
- connections to management network, Proxmox, Data VM, inference raw ports and metadata address all fail;
- an allowed registry is reachable; a non-allowed public host is not (when web research is off);
- Docker socket absent or unusable;
- credential sweep finds nothing.

Run by the controller:
- seeded vulnerable dependency, seeded secret and seeded disallowed license each fail the gate;
- write to a protected path fails the run;
- each limit type triggers the correct terminal state;
- killed worker and killed controller leave no orphan after cleanup;
- redaction scanner removes seeded token, cookie and key patterns.

## Rollback / failure recovery
SandboxProfile and GatePolicy are versioned; a bad revision is replaced by the previous one. If the sandbox cannot be verified at run start, the run does not start. A suspected escape is handled under the [security incident runbook](../../docs/runbooks/security-incident.md).

## Cost/resource budget
The sandbox adds build and startup overhead per run; measure it. Limits defined here are the cost control for all later autonomous work; record the initial values and the evidence used to change them.

## Documentation updates
- `docs/security/autonomous-development-security.md` (concrete profile, allow list, limits).
- `docs/ai/code-provenance-and-dependencies.md` (gate wiring).
- Operator guide for provisioning and verifying the sandbox.

## Open decisions
- **Decided (ADR-0033):** one non-root container per run under gVisor, read-only root file system, no Docker socket, outbound traffic only through an allow-list proxy; the Worker VM is the outer boundary.
- **Decided (ADR-0033):** registries and license policy are listed in ADR-0033 section 3.
- **Decided (ADR-0033):** 2 hours, 4 virtual CPUs, 8 GB memory, 20 GB disk, USD 5 API spend per run; the operator may raise a limit for a named run.
- **Decided (ADR-0033):** 90 days.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review recorded, and the in-sandbox reachability and credential-sweep evidence stored for R0-010.
