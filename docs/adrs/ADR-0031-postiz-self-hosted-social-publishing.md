# ADR-0031 — Postiz as a Self-Hosted Social Publishing Service
Status: Withdrawn (2026-11-14, by the owner, the same day it was accepted)

## Replacement decision
Social platform connectors are **built inside Presence OS** as connectors behind the Connection Broker (R1-007) and the Action Broker. No separate scheduling product is deployed.
- Reasons: one system to operate instead of two; one place for tokens, tenant isolation and audit; no third-party licence obligations.
- Postiz and similar projects may be read to learn how platforms behave. **No code is copied from them.** Postiz is AGPL-3.0, and copied code would bring that licence into Presence OS.
- Platforms are added one at a time, starting with the few the operator's clients use. Each still needs its own developer app and, for most, the platform's approval.
- Each connector is a task contract of its own, written with the R3 specs.

The text below is the withdrawn proposal, kept for the record.

## Context
ADR-0030 makes Presence OS an operator-run agency tool. The operator manages social media for clients, who connect their own accounts (R1-007). Each social platform needs its own connector, token handling and scheduling. Postiz (`gitroomhq/postiz-app`, AGPL-3.0, actively maintained as of 2026-11-13) already provides these, a public API, and uses PostgreSQL and Temporal, which Presence OS also runs.

## Decision
1. Social publishing is done by a self-hosted, **unmodified** Postiz instance running as a separate service. Presence OS does not copy or link Postiz code.
2. Presence OS talks to Postiz only through its public API, behind a Presence-owned connector adapter, so Postiz stays replaceable.
3. Every post still goes through the Presence Action Broker first. Postiz executes; it does not decide. Nobody except the operator and the adapter can reach the Postiz API.
4. Postiz is not exposed publicly except for the pages a client must reach to connect an account, and only if evaluation shows that is necessary.
5. Postiz gets its own database and its own Temporal namespace or instance. It does not share Presence tables.

## Alternatives
- Build each platform connector in Presence OS: full control, months of work per platform set, and the same platform approvals are needed either way.
- A hosted scheduling service: no hosting work, but client tokens live with a third party and there is a recurring fee.

## Evaluation gate (before deployment)
- Licence: confirm AGPL-3.0 obligations for an unmodified, separately run service, and that no Postiz code enters the Presence repository.
- Isolation: confirm how Postiz separates one client's accounts from another's, and map one Presence tenant to one Postiz workspace (or equivalent). If Postiz cannot keep clients apart, this ADR is reopened.
- Connect flow: decide whether the client connects accounts on a Postiz page or on a Presence page that hands off to Postiz, and how that fits the R1-007 rule that Presence holds connection state and health.
- Token custody: tokens will be stored by Postiz. Record where, how they are encrypted, and how a client's disconnect in Presence removes them in Postiz.
- Security and maintenance review as required by AGENTS.md; pin a release.
- Platform developer apps and approvals are still required for each social platform when self-hosting.

## Consequences
- R1-007 keeps its broker contract and gains Postiz as the first social connector behind it.
- The landscape research's caution stands: AGPL projects are used only unmodified and as separate services.
- A second Temporal user and a second database add operating work on the Core/Data VMs; resource headroom must be checked in R0-009.
