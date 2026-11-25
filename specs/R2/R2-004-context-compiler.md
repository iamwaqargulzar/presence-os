# R2-004 — Context Compiler

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 is built; recheck against the R1 implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Build the model context for every call: the smallest set of policy, tools, memory, facts and recent messages that the step needs. Never resend a whole history. Label every piece by trust. Remove anything the chosen provider is not allowed to receive.

## Why now
It is a fixed rule in AGENTS.md. Without it the first conversation feature will send full histories, costs will grow with every message, and provider policy will be checked only by luck.

## Context / linked docs / ADRs
- [Context Compiler and memory loading](../../docs/architecture/context-compiler.md)
- [Context, cache and AI economics](../../docs/ai/context-cache-economics.md)
- [Trust boundaries and prompt injection](../../docs/security/trust-boundaries-and-prompt-injection.md)
- [Tenant Presence AI, model profiles and provider policy](../../docs/ai/tenant-ai-model-entitlements.md)
- [Privacy and data governance](../../docs/compliance/privacy-and-data-governance.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0014, ADR-0022, ADR-0024, ADR-0033 (data classes)

## Depends on
- R2-002 (memory), R2-003 (knowledge). Uses R1-012 (pinned profile, provider policy), R0-007 (gateway).

## Invariants
- no caller builds a prompt by hand; every tenant model call takes its context from the compiler;
- the full conversation history is never sent by default;
- every object in context has a trust label: TRUSTED_CONTROL, AUTHORIZED_HUMAN, VERIFIED_TENANT_DATA, UNVERIFIED_TENANT_DATA, EXTERNAL_UNTRUSTED, GENERATED;
- untrusted content is placed as data and never in the control section;
- an item whose data class the pinned provider may not receive is left out, and the omission is recorded. The class `secret` is never included for any provider;
- context for tenant A never contains data of tenant B;
- Redis is a cache, not the truth.

## In scope
- `compile(run, step) → context package`: ordered sections, token count, trust labels, the list of included item IDs and the list of omitted items with reasons.
- Fixed section order, stable first: system policy, tool and skill contracts, authorization summary, tenant-stable context, task-stable context, retrieval, recent messages, current request.
- Loading rule: L0 plus the relevant parts of L1 to L4; L5 only on an explicit request by the step.
- Token budget per section, set by task class, with a deterministic trimming order.
- Data-class filter against the tenant's provider policy for the pinned profile.
- Untrusted-content wrapping: clear delimiters, source and label, with any text that imitates the delimiters neutralised.
- Provider prompt-cache support: stable prefix kept byte-identical between calls where the provider supports caching.
- Result cache for expensive retrieval, with keys that include tenant, profile, property, skill and tool version, input hash, permission context, provider and model, knowledge version and policy revision.
- Invalidation on: access revoked, permission lowered, tenant deleted, fact superseded, privacy request, credential revoked.
- A context record per call: item IDs and hashes, not the full text, so it can be answered later "what did the model see".
- Compaction: when a run grows, replace old turns with a summary from R2-002, recorded as a compaction event.

## Out of scope
- Storing memory or facts (R2-002, R2-003).
- Choosing the model (R1-012).
- Tools and tool execution (R2-001).
- Learned or model-driven context selection. Selection is rules plus retrieval scores.

## API / contract changes
- Internal: `compile`, `explain(context_id)`, `invalidate(reason, scope)`.
- The gateway call accepts only a context package, not free text, for tenant runs. An import-boundary test enforces this.
- New contract sketch: `context-package.schema.json`.

## Data / migration
- Tenant-scoped under RLS: ContextRecord (references and hashes only), CompactionEvent.
- Cache entries in Redis with a tenant prefix and expiry; sensitive entries short-lived.
- Reverse migrations tested.

## Security / privacy threat notes
- Prompt injection from retrieved pages, files or tool output: labelled, delimited, never in the control section; the Action Broker and Authorization Service remain the real defence.
- Cache leak across tenants or after a policy change (E-044): key includes tenant and policy revision; a negative test tries a cross-tenant hit.
- Data class sent to a provider the tenant excluded (E-063): filter at compile time, checked again by the gateway against the package's declared classes.
- Secrets in context: `secret` class never included; a seeded token in memory must not appear in a compiled package.
- The context record itself becoming a second copy of sensitive data: it stores IDs and hashes.

## Edge cases covered
- E-044 shared cache leaks tenant content.
- E-063 low-cost provider receives a class the client did not allow.
- E-045 deleted data remains in cache: deletion triggers invalidation.
- E-001 and E-011: a model change mid-conversation changes nothing in what is loaded; the next run compiles the same memory for the new model.
- E-010: the context record shows which profile saw what.

## Observability
- Per call: tokens by section, cached and uncached input, items omitted by policy, compactions.
- Metrics: average context size by task class, cache hit rate, omissions by reason.
- Audit: invalidation events with reason.

## Acceptance criteria
- a 200-message conversation compiles to a bounded context that does not grow with message count;
- the section order is fixed and the stable prefix is identical between two calls of one run;
- an item of a class the provider may not receive is absent from the package and listed as omitted;
- an external page containing instructions appears only inside the untrusted data section;
- revoking a person's access or superseding a fact invalidates the affected cache entries;
- `explain` returns the exact item list for any past call.

## Tests
- Size: long conversation stays under the budget.
- Order and prefix stability: byte comparison.
- Provider-policy matrix: each data class against frontier and low-cost profiles for a new tenant.
- Injection corpus: delimiter-breaking text, fake system messages, fake approvals.
- Cache: cross-tenant key collision attempt; policy revision change misses the cache; each invalidation trigger.
- Tenant isolation: compile for tenant A with IDs of tenant B's memory and facts returns nothing; RLS suite on ContextRecord.
- Secret: seeded credential never appears in a package or record.
- Boundary: a module calling the gateway with raw text for a tenant run fails a gate.

## Rollback / failure recovery
If retrieval or the cache is down, compile falls back to policy, task state and recent messages only, and marks the package degraded. It never falls back to full history. Reverse migrations tested.

## Cost/resource budget
The compiler adds no model calls except compaction summaries, which run on the low-cost profile when the data class allows. Proposed default budgets: 8,000 tokens for low-cost task classes, 40,000 for frontier task classes; the operator can change them per task class.

## Documentation updates
- `docs/architecture/context-compiler.md`, `docs/ai/context-cache-economics.md`, `docs/security/trust-boundaries-and-prompt-injection.md`.

## Open decisions
- **Decision required:** token budgets per task class. Proposed default above.
- **Decision required:** how long ContextRecords are kept. Proposed default: 180 days, the same as evaluation artifacts in ADR-0033.
- **Decision required:** whether an omitted item pauses the run or the run continues without it. Proposed default: continue and show the omission in the run report; pause only if the skill marks the item as required.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review of the trust-label and provider-policy filter is recorded.
