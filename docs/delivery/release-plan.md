# Release Plan


> **Presence OS engineering source of truth**
>
> Baseline date: **2026-08-10** (Asia/Karachi project context).
> Product architecture is intentionally model-, provider-, harness-, and ingress-neutral.
> Vendor capabilities, model names, prices, quotas, laws, and platform policies are time-sensitive reference facts and MUST be revalidated before implementation or purchase.
> When a focused document conflicts with an older discussion, the focused document plus the Decision Register and ADRs control.


## R0 — Engineering Foundation

Deliver:
- repository/dev factory
- PresenceBench skeleton
- CI/test environments
- Proxmox baseline
- PostgreSQL baseline
- Temporal baseline
- secrets foundation
- audit foundations
- AI/model gateway skeleton
- security foundations
- coding-agent task/provenance workflow

Exit only when secure development and tenant-isolation foundations are testable.

## R1 — Presence Kernel

Deliver:
- users/persons
- tenants/profiles
- memberships/roles
- delegated access
- tenant limits, usage ledger and budgets
- Authorization Service
- Action Broker
- domains/random platform addresses
- preview routing
- connections
- audit
- budgets/resource controls foundations

## R2 — Presence Intelligence

Deliver:
- conversation shell
- operator mobile console: task requests, scheduling, reports, approvals
- client request/approve queue
- Context Compiler
- memory
- canonical knowledge
- research
- Presence Scan
- scoring/versioning
- competitors
- Opportunity Engine
- Attention synthesis

## R3 — Business Presence MVP

Deliver:
- website create/change
- preview/deploy/rollback
- SEO/AEO/GEO basics
- content/social/local basics
- image generation through the AI Capability Gateway
- approvals/actions
- reporting/progress

**R3 is the first release used for real client work.** Nothing is sold (ADR-0030).

Also in R3: social platform connectors built in-house, one platform at a time.

## R4 — Growth Operations

Deliver:
- CRM
- email/outreach
- lead discovery
- omnichannel
- managed-service workflows
- voice receptionist

## R5 — Expansion

Candidates:
- broader browser workflows
- ecommerce/feeds/commerce
- support
- PR/partnerships
- professional/career
- Platform Engineer
- marketplace/partner expansion.

Do not treat R5 as one giant release; split based on validated demand.

## 2026-08-10 release-plan amendments

### R0 additional foundation
- Claude Code worker adapter through the Agent SDK, with the operator start/approve gate (ADR-0030);
- Google sign-in only, by invitation;
- OpenHands-backed DevelopmentController + PrimeWorkerAdapter;
- autonomous-development sandbox/supply-chain controls;
- controller/worker/subagent telemetry separation;
- model/profile registry supports production tenant AI policy later.

### R1 additional kernel
- DigitalProperty and multi-property ownership/environments;
- TenantAIIdentity, AIModelProfile, TenantAIConfiguration, tenant provider policy;
- default model change with preview and rollback.

### R3 hosting scope
R3 may expose multiple sites/apps per tenant, but launches with a qualified set of runtime profiles. Do not promise arbitrary-language PaaS hosting before runtime/security/backup/resource profiles are qualified.
