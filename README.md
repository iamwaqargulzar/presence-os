# Presence OS

Presence OS is a private, multi-tenant system that one operator uses to manage the online presence of their own companies and of clients, with most of the work done by supervised AI. It is not sold as a product.

> **Presence OS engineering source of truth**
>
> Current as of **2026-11-14** (Asia/Karachi project context). First baseline: 2026-08-10.
> Presence OS is run by one operator for their own companies and managed clients. It is not sold as a product ([ADR-0030](docs/adrs/ADR-0030-operator-run-agency-deployment.md)).
> Vendor capabilities, model names, prices, quotas, provider terms, laws and platform policies are time-sensitive and MUST be rechecked before implementation or purchase.

## Start here

1. Read [`00_START_HERE.md`](00_START_HERE.md).
2. Read [`AGENTS.md`](AGENTS.md) before editing anything.
3. Read [`docs/DECISION_REGISTER.md`](docs/DECISION_REGISTER.md) and [`docs/adrs/`](docs/adrs/) for locked decisions.
4. Read [`docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`](docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md) for what is still undecided.
5. Begin implementation only from a task contract in [`specs/`](specs/).

## What this repository is

An **engineering specification and implementation-control repository**. It contains:
- product scope and UX principles;
- architecture and data/control boundaries;
- security and threat model;
- infrastructure and deployment topology;
- domain/ingress strategy and runbooks;
- AI gateway, model routing, context and cost architecture;
- the development factory and PresenceBench;
- tenant limits, budgets and offboarding;
- release sequence and gates;
- ADRs, contract schemas, templates and the R0 to R3 task contracts;
- the edge-case register (E-001 to E-094).

## Project status

Specification complete for R0 and R1; R2 and R3 task contracts written (revision 1). R0-001 (repository and toolchain) built on 2026-11-25: Django and Next.js skeletons with pinned toolchain and gate commands. Set up a machine with [`docs/runbooks/developer-bootstrap.md`](docs/runbooks/developer-bootstrap.md). The live status is in [`docs/handoff/STATUS.md`](docs/handoff/STATUS.md).

## Repository layout

| Path | Contents |
|---|---|
| `00_START_HERE.md`, `AGENTS.md`, `CLAUDE.md` | Entry point and rules for people and coding agents |
| `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md` | Workflow, security policy, history of changes |
| `specs/R0` … `specs/R3` | Task contracts, one per implementable task |
| `docs/adrs/` | Architecture decision records |
| `docs/handoff/` | Live status and session handoffs |
| `docs/<area>/` | Focused documents per subsystem; rules in [`docs/DOCUMENTATION_STANDARDS.md`](docs/DOCUMENTATION_STANDARDS.md) |
| `contracts/schemas/` | Machine-checked interface schemas |
| `templates/` | Templates for tasks, ADRs, reports, handoffs and incidents |
| `evidence/` | Implementation reports, reviews, audits and drills |
| `apps/`, `packages/`, `infra/`, `benchmarks/`, `evals/` | Code locations, filled from R0 onward |
| `tools/` | Repository tools, including `build_docs.py` |

## Maintenance

After editing any document, run `python3 tools/build_docs.py` to rebuild the compiled files and check links.
