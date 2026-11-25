# ADR-0030 — Operator-Run Agency Deployment, Not a Sold Product
Status: Accepted (2026-11-14, by the owner)

## Context
The baseline specifies a multi-tenant product sold to customers, with plans, billing, AI tiers and an optional private GPU host. The owner has decided to run Presence OS as a private tool for their own companies and for clients they manage as an agency. Nothing is sold as software. Electricity cost and use of existing AI subscriptions are the main operating constraints.

## Decision
1. **Scope.** Presence OS is operated by one owner (the operator). Each owned company or managed client is a tenant. There is no self-service signup, plan catalogue, invoicing or reseller mode.
2. **Client access.** A client may be given a login scoped to their own tenant with one of three levels: view, request changes, approve drafts. Clients cannot start AI work; their requests queue for the operator.
3. **Isolation stays at full strength.** Because clients can log in, tenant_id + RLS and the full cross-tenant test suite remain mandatory. The Action Broker, authority model and audit trail are unchanged.
4. **Inference is cloud-first; the GPU host is optional.** The default routing mode is CLOUD_ONLY. The private inference host may be powered off indefinitely. LOCAL_ONLY is not offered to any tenant while it is off.
5. **Model split.** A frontier model does planning, architecture, security-sensitive work and review. A low-cost API model (currently intended: DeepSeek) does high-volume, low-risk, machine-checkable work. The split is configuration in the registries and is qualified with PresenceBench on real tasks, not fixed in code.
6. **Subscription-backed worker.** A harness adapter runs the official Claude Code on the isolated Worker VM through the Claude Agent SDK, using the operator's own subscription. Other subscriptions (for example Codex) are used only through their own official tools in the same way. Subscription-backed runs are started or approved by the operator.
7. **Unattended and scheduled runs use API credentials**, not subscriptions, through the AI Capability Gateway.
8. **Operator access is mobile-first on a dedicated console domain with Google sign-in only.** The operator's console (task requests, scheduling, reports, approvals, deploy/modify actions) is served on its own hostname on the control-plane domain through the existing Cloudflare Tunnel. Sign-in for the operator and for clients is Google sign-in (OpenID Connect) only. Presence OS stores no passwords and has no password login, reset or signup form. Only email addresses the operator has invited can sign in. Proxmox, SSH and the other internal services are never published this way: remote administration is only through the operator's private WireGuard VPN on their router.

## Relationship to existing ADRs
- **ADR-0029** is narrowed, not reversed: subscription credentials remain barred from unattended and client-triggered work. This ADR permits them for operator-started runs through an official harness on the Worker VM.
- **ADR-0027** stands: the worker holds no production secrets. The subscription login is itself a secret confined to the Worker VM.
- **ADR-0013, ADR-0022 to ADR-0024** stand: models remain replaceable and pinned per run.
- **ADR-0025** (OpenHands + Prime factory): Claude Code via the Agent SDK is added as a harness entry. Whether it replaces Prime Agent as the primary worker is a separate decision.

## Consequences for task contracts
| Spec | Effect |
|---|---|
| R0-007 | Add a Claude Code (Agent SDK) harness entry and a low-cost API model entry. |
| R0-004 | Google sign-in only, invitation allow-list, no password login. |
| R0-009 | Console hostname through the Cloudflare Tunnel; GPU host becomes optional in the deployment. |
| R0-011 / R0-012 | Adapter for the subscription-backed worker; operator start/approval gate. |
| R1-001 | Add the three client access levels and the operator role. |
| R1-004 | Shrink: remove plans and billing; keep per-tenant budgets as operator spending caps. |
| R1-012 | Shrink: per-tenant model choice and run pinning; remove package entitlements and exceptions. |
| R1-013 | Drop or reduce to a single audited "change default model" action. |
| R1-002, 003, 005 to 011 | Unchanged. |
| R2 / R3 | Add the operator mobile console, task scheduling and the client request/approve queue to the task contracts when they are written. |

## Risks and open points
- Provider terms change. Anthropic has said Agent SDK usage may move from subscription limits to paid credit; the adapter must work with either. Terms for every subscription used must be rechecked before reliance.
- Subscription rate limits cap throughput; heavy batches fall back to the API model.
- Client data sent to the low-cost provider: decide per tenant which data classes may leave to which provider.
- Decision required: whether scheduled daily tasks run fully unattended on API models, or only prepare work and notify the operator for approval.
- The operator's Google account becomes the single key to the console: it must use two-step verification, preferably a passkey or hardware key. A Google outage or account lock blocks sign-in until it is resolved.
- Decision required: whether Cloudflare Access is also placed in front of the operator console so the application is not directly reachable by strangers (recommended).
- Decided 2026-11-14: remote Proxmox and SSH access is only through the operator's WireGuard VPN on the router. The VPN is managed by the operator outside this project.
- Decision required: mobile surface: responsive web console only, or also push notifications/chat channel.
