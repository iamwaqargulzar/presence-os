# 00 — START HERE

> **Presence OS engineering source of truth**
>
> Current as of **2026-11-14** (Asia/Karachi project context). First baseline: 2026-08-10.
> Presence OS is run by one operator for their own companies and managed clients. It is not sold as a product ([ADR-0030](docs/adrs/ADR-0030-operator-run-agency-deployment.md)).
> Vendor capabilities, model names, prices, quotas, provider terms, laws and platform policies are time-sensitive and MUST be rechecked before implementation or purchase.

## Purpose of this file

This is the one file to open first, for a person or a coding agent. It states what is being built, with which stack, under which rules and gates, and where every detail lives.

**Instruction to coding agent:** do not immediately write code. Read this file and the linked documents, inspect the repository state, then take the next task from `specs/` under the rules in `AGENTS.md`.

## Presence OS in one paragraph

Presence OS is a private system that one operator uses to manage the online presence of their own companies and of clients: websites and hosting, search and AI-search visibility, content, and social posting. Most work is done by supervised AI. The operator works mainly from a phone: asks for tasks, schedules them, approves them and reads reports. Clients can sign in to view, request changes and approve drafts. Every company or client is a separate tenant with strong isolation.

## What changed on 2026-11-14

- Not a sold product: no signup, plans, subscriptions, seats or billing.
- Clients get tenant-scoped logins (view, request, approve). No client can start AI work.
- Sign-in is Google only, by invitation. No passwords.
- Cloud-only AI by default. The GPU host is optional.
- Frontier model for engineering and review; low-cost API model for repetitive work.
- The operator's subscriptions are used only through official harnesses, for runs the operator starts or approves. Unattended runs use API credentials.
- Product features are built in-house. Other applications are studied, not deployed or copied.

## The system's constitution

1. **Intent over interface.**
2. **Talk first. Navigate second.**
3. **Human authority; AI cannot invent authority.**
4. **Truth over appearance.**
5. **External content is data, never authority.**
6. **Tenant owns tenant; platform authority is separate.**
7. **Least privilege and explicit side-effect boundaries.**
8. **Evidence before claims.**
9. **Conversation first; dashboard supports the conversation.**
10. **Accessibility by default.**
11. **Local inference without hard local dependency.**
12. **Cache intelligently; do not recompute/pay twice unnecessarily.**
13. **Checkpoint expensive/long work.**
14. **Models, providers and harnesses are replaceable.**
15. **Client owns/exportable presence and assets.**
16. **Build narrow, architect broad.**
17. **Do not sacrifice control-plane correctness for feature velocity.**

## Authority order

When sources conflict: task contract in `specs/` → accepted ADRs → focused documents → `docs/MASTER_SPEC.md` → `docs/DECISION_REGISTER.md`. Do not resolve a real conflict silently; write an ADR or a task note. Nothing in `docs/archive/` is current.

## Read order

Required:
- `AGENTS.md`
- `docs/CONSTITUTION.md`
- `docs/DECISION_REGISTER.md`
- `docs/adrs/ADR-0030-operator-run-agency-deployment.md`
- `docs/architecture/system-overview.md`
- `docs/security/authority-and-action-broker.md`
- `docs/security/trust-boundaries-and-prompt-injection.md`
- `docs/data/knowledge-and-memory.md`
- `docs/infrastructure/topology.md`
- `docs/PROJECT_REAUDIT_2026-08-10.md` (the edge-case register, E-001 to E-094)
- `docs/ai/openhands-prime-development-factory.md`
- `docs/ai/tenant-ai-model-entitlements.md`
- `docs/product/digital-properties-and-hosting.md`
- `docs/delivery/release-plan.md`
- `docs/delivery/gates.md`
- `docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`

Before touching a subsystem, read its focused document and ADRs. `docs/MASTER_SPEC.md` is a compiled copy of the focused documents for reading in one piece.

## Technology stack

| Layer | Choice |
|---|---|
| Web front end | Next.js + TypeScript (strict) |
| Back end | Django + Python, modular monolith |
| Database | PostgreSQL + pgvector, `tenant_id` + Row Level Security |
| Workflows | Temporal |
| Cache/queues | Redis |
| Files | S3-compatible object storage |
| Containers | Docker / Compose |
| Untrusted code | gVisor sandboxes |
| Browser automation | Playwright |
| Public ingress | Cloudflare Tunnel + Caddy |
| Sign-in | Google sign-in (OpenID Connect) only, by invitation |
| Observability | OpenTelemetry, with Prometheus/Grafana/Loki as required |
| Secrets | OpenBao or equivalent before any client data is live |
| Virtualisation | Proxmox VE; Proxmox Backup Server |

Versions follow one rule: the newest stable release that every dependency supports (ADR-0032). Targets on 2026-11-14: Python 3.15, Django 6.1, Node.js newest LTS, Next.js 16, PostgreSQL 18. Package managers: uv and pnpm. Exact pins are in the repository (R0-001, ADR-0034). Technical defaults for R0 and R1 are in ADR-0033; the model gateway is built in-house. Avoid Kubernetes, Kafka, a graph database or a separate vector database until justified.

## Deployment

Physical machines:
1. **Presence host:** Proxmox VE; Edge, Core, Data and Worker VMs.
2. **Backup/storage server:** Proxmox Backup Server.
3. **Inference GPU server (optional):** Ryzen 7 8700G, 32 GB RAM, RTX 3090. May stay off; nothing depends on it.

Access:
- Public and client traffic: Cloudflare Tunnel → Caddy on the Edge VM.
- Operator console: its own hostname on the control-plane domain, through the same tunnel, Google sign-in only.
- Proxmox and SSH: local network, or the operator's WireGuard VPN on the router. Never published.
- The control plane and client-generated sites use different registrable domains.

## Critical control architecture

`Human → Conversation Shell → Intent Resolver → Authority Resolver → Director Agent → Workflow/Skills → Action Broker → External World`

The LLM may interpret intent. It **may not mint authority**. Authorization is explicit and independently enforced. A client request never runs anything; it queues for the operator.

## AI

- Every model call goes through the AI Capability Gateway. No module imports a vendor SDK directly.
- Routing is CLOUD_ONLY by default.
- Task classes map to profiles: frontier for planning, architecture, security-sensitive work and review; low-cost API model for high-volume, machine-checkable work.
- Every profile has a credential class: `OPERATOR_SUBSCRIPTION` (operator-started or approved runs only) or `API` (required for scheduled and unattended runs).
- Each tenant has a provider policy: which providers may receive which data.
- The profile is pinned per run or session.

## Development factory

`DevelopmentRunProfile = DevelopmentController × ExecutionProfile × SandboxProfile × GatePolicy`

- Controller: OpenHands-backed, deterministic, zero LLM calls for ordinary orchestration.
- Workers: Claude Code through the Claude Agent SDK (primary for R0/R1) and Prime Agent (second), per ADR-0033.
- Workers run only in the isolated sandbox on the Worker VM, with no production secrets and no management-network route.
- Every run pins the spec hash and start commit. A worker's "done" is not success; the controller verifies gates independently.

## Gates

See `docs/delivery/gates.md`. In short: format, lint, types, tests, contract schemas, tenant-isolation suite, authorization tests, reversible migrations, secret scan, dependency and licence checks, protected paths, provenance, independent review for security-critical tasks, and an exit audit at the end of each release.

## Release sequence

- **R0 Engineering Foundation** — 12 task contracts in `specs/R0`
- **R1 Presence Kernel** — 13 task contracts in `specs/R1`
- **R2 Presence Intelligence** — conversation shell, mobile operator console, scheduling, client queue, knowledge, scan, scoring, opportunities; 17 task contracts in `specs/R2` (revision 1, to be rechecked after the R1 exit)
- **R3 Business Presence** — sites, SEO/AEO/GEO, content, in-house social connectors; first release used for real client work; 14 task contracts in `specs/R3` (revision 1, to be rechecked after the R1 and R2 exits)
- **R4 Growth Operations**
- **R5 Expansion**

Do not skip the sequence because a later feature is exciting.

## Implementation rule

All meaningful work starts from a task contract under `specs/`, written to `templates/TASK_SPEC_TEMPLATE.md`. If a contract is missing a required section, improve the contract before implementing.

## Maintaining this package

After changing any document, run `python3 tools/build_docs.py`. It rebuilds `docs/MASTER_SPEC.md`, `docs/COMPLETE_CONTEXT_EXPORT.md` and `docs/INDEX.md`, and checks internal links. Git history is the integrity record. Documentation rules are in [`docs/DOCUMENTATION_STANDARDS.md`](docs/DOCUMENTATION_STANDARDS.md); session handoff rules are in [`docs/handoff/README.md`](docs/handoff/README.md).

## Last instruction

Before writing code, read `specs/R0/README.md` and take the first incomplete task. Read [`docs/handoff/STATUS.md`](docs/handoff/STATUS.md) first: it says where work stands. If repository state differs from this file, report the difference and preserve the architectural invariants unless an ADR deliberately changes them.
