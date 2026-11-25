# System Architecture Overview


> **Presence OS engineering source of truth**
>
> Baseline date: **2026-08-08** (Asia/Karachi project context).
> Product architecture is intentionally model-, provider-, harness-, and ingress-neutral.
> Vendor capabilities, model names, prices, quotas, laws, and platform policies are time-sensitive reference facts and MUST be revalidated before implementation or purchase.
> When a focused document conflicts with an older discussion, the focused document plus the Decision Register and ADRs control.


## Master abstraction

`GOAL → WORKFLOW → AGENT → SKILL → TOOL → CONNECTOR → PROVIDER`

Runtime flow:

`Human → Voice/Text/UI → Conversation Shell → Intent Resolver → Authority Resolver → Director Agent → Memory/Knowledge/Opportunity → Temporal Workflows → Skill Runtime → Capability Resolver → AI/Tools/Media → Action Broker → Policy/Authorization/Risk/Entitlement → Connector/Provider → External World`

Cross-cutting:
- Tenant Isolation
- Cost Governor
- Resource Governor
- Secrets Broker
- Context Compiler
- Cache
- Audit Ledger
- Observability
- Security Policy
- Evaluation System

## Architectural style

**Modular monolith first** with strongly separated modules and processes where the threat/resource boundary justifies it.

Initial conceptual modules:
- accounts
- tenancy
- profiles
- identity
- authorization
- conversation
- context
- knowledge
- presence
- opportunities
- tasks
- workflows
- approvals
- actions
- skills
- connectors
- providers
- tenant limits
- entitlements
- usage
- limits and budgets
- notifications
- audit
- domains
- deployments
- files
- browser
- inference
- evaluations

Extract services only when scaling, isolation, operational independence or security creates a real need.

## External side-effect boundary

Agents and business modules do not directly publish, send, spend, delete, deploy, change DNS, mutate CRM or perform equivalent external effects. They submit an action through the Action Broker.

## Trust boundary

External web/email/social/file/tool content never receives authority merely because it appears in model context.

## Data boundary

Tenant/profile-scoped records carry tenant_id/profile_id as appropriate, with RLS and application checks.

## Infrastructure boundary

Control plane, tenant-generated sites, untrusted workers and GPU inference are separate zones even if initially deployed on a small number of VMs.
