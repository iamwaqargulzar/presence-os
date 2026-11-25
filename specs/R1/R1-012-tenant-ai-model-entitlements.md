# R1-012 — Tenant Presence AI, Model Profiles and Provider Policy

> **Spec revision:** 4 — 2026-11-14. Rewritten as clean text after [ADR-0030](../../docs/adrs/ADR-0030-operator-run-agency-deployment.md): package entitlements, AI tiers sold in plans, entitlement exceptions and AI Compute Units are removed. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## Goal
Give every tenant one stable Presence AI identity, resolve which model profile each run uses, pin it for the run, and never send a tenant's data to a provider that tenant's policy forbids.

## Why now
R2 starts the conversation shell. Before the first tenant run, the system must know which model profile it uses, pin it, respect the tenant's provider policy, and record usage in a way that survives the next model change.

## Context / linked docs / ADRs
- [Tenant Presence AI, model profiles and provider policy](../../docs/ai/tenant-ai-model-entitlements.md)
- [AI Capability Gateway](../../docs/ai/capability-gateway.md)
- [Tenant limits, budgets and usage](../../docs/commercial/plans-entitlements-billing.md)
- [Context and cache economics](../../docs/ai/context-cache-economics.md)
- [Edge cases E-001, E-003, E-004, E-006, E-007, E-009 to E-012, E-044, E-061 to E-063, E-066](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- Contracts: [ai-model-profile.schema.json](../../contracts/schemas/ai-model-profile.schema.json), [tenant-ai-configuration.schema.json](../../contracts/schemas/tenant-ai-configuration.schema.json)
- ADR-0013, ADR-0022, ADR-0024, ADR-0029, ADR-0030

## Depends on
- R0-007 AI capability/profile registry (task-class routing, credential class)
- R1-001 RBAC
- R1-004 limits and budgets

## Invariants
- one stable logical Presence AI per tenant; identity, memory and authority never live in the model instance;
- model IDs are versioned configuration, never code;
- the effective AIModelProfile revision is pinned for a run/session; a change never swaps the model mid-run;
- privacy, data-residency and the tenant provider policy are hard filters, not ranking preferences;
- resolution fails closed when no profile satisfies the required capabilities and policy;
- a run that the operator did not start or approve never resolves to an `OPERATOR_SUBSCRIPTION` profile;
- the Platform Admin AI has its own configuration and no tenant memory or inherited tenant authority.

## In scope
- TenantAIIdentity entity (stable, one per tenant).
- AIModelProfile with revisions, status (DRAFT, ACTIVE, DEPRECATED, DISABLED), privacy class, capability metadata, credential class and fallback list.
- TenantAIConfiguration: mode (PINNED or PLATFORM_DEFAULT), override profile, privacy mode, monthly AI budget reference.
- **Tenant provider policy:** per tenant, which providers and regions may receive which data classes.
- Resolver: authorised run override → tenant override → platform default. The platform default comes from the task-class routing in R0-007 (frontier profile or low-cost profile). Returns the profile revision and a human-readable reason.
- Pin record per run/session.
- Fallback selection filtered by provider policy, privacy, capability, budget reservation, credential class and provider health; otherwise checkpoint/pause with a reason.
- Usage accounting in raw tokens (input, cache write, cache read, output, reasoning) and money cost, with provenance grade.
- Operator inspection of the effective profile and reason.
- PlatformAIConfiguration placeholder.

## Out of scope
- Changing the platform default safely across tenants (R1-013).
- Conversation, memory and the Context Compiler (R2).
- Automatic quality-based escalation between profiles.
- Client-facing model settings: clients do not choose models.

## API / contract changes
- Internal: `resolve(tenant, task_class, required_capabilities, run_context, run_override?) → pinned profile revision + reason | paused(reason)`; `pin(run)`; `fallback(run)`.
- Operator endpoints: set tenant override, set tenant provider policy, inspect effective profile.
- `tenant-ai-configuration.schema.json` and `ai-model-profile.schema.json` refined; add TenantAIIdentity and tenant-provider-policy sketches.

## Data / migration
- Platform-level tables: AIModelProfile (+revisions).
- Tenant-scoped tables under RLS: TenantAIIdentity, TenantAIConfiguration, tenant provider policy, run/session pin, AI usage records.
- Reverse migrations tested.

## Security / privacy threat notes
- Fallback sending tenant data to a provider or region its policy forbids (E-007).
- Low-cost provider receiving a data class the tenant did not allow (E-063).
- Subscription-backed profile used by an unattended or client-triggered run (E-061).
- Platform Admin AI reading tenant data by default (E-012).
- Prompt/result cache keyed without tenant, profile, property or policy revision (E-044).
- Model switched invisibly (E-010) or mid-conversation (E-001).
- Provider credentials exposed through profile records: store references only.
- A run override requested by a model rather than the operator: overrides require authority like any other privileged change.

## Observability
- Audit: configuration change, provider-policy change, every resolution with reason and pinned revision, every fallback or pause.
- Per-run usage with provenance grade, attributable to tenant, task and provider/model.

## Acceptance criteria
- TenantAIIdentity entity boundary;
- AIModelProfile versioning and capability metadata;
- TenantAIConfiguration with PINNED/PLATFORM_DEFAULT;
- resolution order platform default → tenant override → bounded run override;
- effective profile revision pinned per run/session;
- fallback filtered by provider policy, privacy, capability and budget;
- the operator can inspect the effective profile and resolution reason;
- RLS/audit/negative tests;
- *(derived)* a profile lacking a required capability is rejected before the run starts;
- *(derived)* PINNED mode with an unavailable profile pauses unless a fallback is explicitly configured;
- a tenant whose policy excludes a provider never resolves or falls back to that provider, for any task class;
- an unattended run never resolves to a subscription-backed profile;
- with the inference host off, a request for a local-only profile pauses with a reason (E-062).

## Tests
- Resolver matrix across the three levels, including an invalid override.
- Pinning: default changed mid-session → same revision until the boundary; new session → new revision.
- Provider-policy matrix across task classes and fallback.
- Credential-class matrix: operator-started, operator-approved, scheduled, client-requested.
- Capability mismatch fails closed.
- Budget exhausted mid-task (E-009) with the fake gateway.
- Usage: unavailable values not zeroed.
- Cross-tenant RLS suite; a client role cannot read or change AI configuration.
- All tests use the fake gateway adapter and spend nothing.

## Rollback / failure recovery
Profiles are revisioned: a bad mapping is superseded by a new revision. Resolution fails closed to "paused with reason". Reverse migrations tested.

## Cost/resource budget
Resolution runs once per run/session and is cacheable by tenant plus policy revision. AI spend is bounded by R1-004 reservations and the tenant's monthly AI budget.

## Documentation updates
- `docs/ai/tenant-ai-model-entitlements.md` (concrete fields, resolver rules).
- Contract schemas and `docs/data/core-entity-catalog.md`.

## Open decisions
- **Decided (ADR-0033):** one task run; the model is pinned for the run.
- **Decided (ADR-0033):** `public`, `business_internal`, `client_confidential`, `personal_data`, `financial`, `secret`; `secret` never goes to any model.
- **Decided (ADR-0033):** Anthropic and DeepSeek. New tenant: frontier may receive every class except `secret`; low-cost may receive `public` only.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent review of the provider-policy and fallback filter is recorded.
