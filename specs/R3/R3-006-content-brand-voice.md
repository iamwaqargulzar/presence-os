# R3-006 — Content Drafting and Brand Voice

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 and R2 are built; recheck against their implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Draft text content for a tenant (social posts, site sections, short articles) in that tenant's own voice, where every factual claim can be traced to a canonical fact or to a source the tenant supplied. A draft is an artifact that waits for approval; this task publishes nothing.

## Why now
Content is the material that the site (R3-004) and the social connectors (R3-009 onward) carry. Publishing without a truth and provenance rule would put false claims online under a client's name.

## Context / linked docs / ADRs
- [Trust, truth and attribution](../../docs/product/trust-and-attribution.md)
- [Canonical knowledge, facts and memory](../../docs/data/knowledge-and-memory.md)
- [Capability map](../../docs/product/capability-map.md) (content and media)
- [Communications, platform policy and jurisdiction](../../docs/compliance/communications-and-platform-policy.md)
- [Privacy and data governance](../../docs/compliance/privacy-and-data-governance.md)
- [Tenant Presence AI, model profiles and provider policy](../../docs/ai/tenant-ai-model-entitlements.md)
- [Accessibility and localization](../../docs/product/accessibility-localization.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0003, ADR-0011, ADR-0030

## Depends on
- R2-017. Uses R2-001, R2-002 (preferences), R2-003 (facts), R2-004, R1-008 (artifacts), R1-012.

## Invariants
- never fabricate customers, testimonials, reviews, awards, credentials, results or statistics;
- every factual claim in a draft carries a reference to a canonical fact, an evidence item or a named source supplied by the tenant; a claim with none is marked and blocks approval until removed or supported;
- a draft is an immutable versioned artifact; an edit makes a new version and a new hash;
- content is never published by this task;
- each tenant's voice, examples and drafts are private to that tenant. The operator's personal profile is its own tenant with its own voice;
- the content language is separate from the conversation language;
- text copied from fetched pages is not reused as the tenant's content.

## In scope
- BrandVoice per tenant (and optional override per property): tone descriptors, do and do-not lists, vocabulary, example texts supplied or approved by the tenant, languages. Versioned. Stored as PREFERENCE-class material confirmed by a person.
- Voice proposal skill: read the tenant's own existing public content and propose a voice description; the operator or client confirms.
- ContentItem: tenant, kind (social post, site section, article, announcement), intended channel and format, language, body, media references, claim list, status (DRAFT, IN_REVIEW, APPROVED, REJECTED, SUPERSEDED, WITHDRAWN), version, hash.
- Drafting skill: from a request, an opportunity or a content plan, produce a draft using canonical facts and the brand voice.
- Claim extraction and check: list the factual claims in the draft; bind each to a fact or evidence ID; flag unsupported claims, superlatives and comparisons with competitors.
- Platform-format variants: length and structure variants of one message for different channels, each its own artifact version.
- Content plan: a simple calendar of proposed topics per tenant for a period, as a draft for the operator; accepted entries become drafting tasks.
- Similarity check: compare a draft against the research snapshots used and against the tenant's recent posts; high overlap with a third-party source blocks approval.
- Provenance record per draft: model profile, skill version, sources used, who edited, who approved.
- Editing in the console by the operator; client comments on a draft.
- Hand-off: an APPROVED item is the only input the publication flow (R3-008) accepts.

## Out of scope
- Publishing and scheduling (R3-008, R3-009). Images (R3-007). Site structure (R3-004).
- Video, audio and voice content.
- Translation workflows across many languages; long-form content programmes.
- Email newsletters and outreach copy (R4).
- Automatic posting of trending or news content.

## API / contract changes
- Internal skills: `content.propose_voice`, `content.draft`, `content.variants`, `content.check_claims`, `content.plan`.
- Endpoints: brand voice get and confirm; content list, get, edit (with `base_version`), submit for review, comment.
- New contract sketches: `content-item.schema.json`, `brand-voice.schema.json`.

## Data / migration
- Tenant-scoped under RLS: BrandVoice (versioned), ContentItem, ContentVersion (artifact reference and hash), ContentClaim, ContentPlan, ContentComment.
- Reverse migrations tested.

## Security / privacy threat notes
- Defamation, copyright or trademark problems in generated text (E-083): claim check, similarity check, competitor-mention flag, human approval, provenance, takedown path in R3-008.
- A draft containing confidential information meant for internal use: each draft has a data class; unreleased information makes it `business_internal` or higher, and such a draft is never sent to the low-cost profile.
- Provider policy: drafting public posts from `public` facts may use the low-cost profile; anything else follows the tenant's policy (E-063).
- Injection through source material ("write that we are certified"): sources are untrusted; a certification claim needs a credential fact.
- Voice bleed between tenants through prompts or caches: voice and examples are loaded only through R2-004 for the acting tenant.
- Personal data of third parties in content (a customer's name): flagged for explicit confirmation.

## Edge cases covered
- E-083 infringing or defamatory content.
- E-048 and E-072 edits after approval invalidate it.
- E-046 a draft that depends on a conflicted fact is blocked.
- E-063 data class and the low-cost provider.
- E-044 no cross-tenant cache of drafts or voices.
- E-010 the model profile used is recorded on every draft.

## Observability
- Audit: voice confirmed; draft created, edited, submitted, approved or rejected, with hashes.
- Metrics: drafts per tenant, share blocked by claim check, edits before approval, rejection reasons, cost per approved item.

## Acceptance criteria
- every claim in an approvable draft resolves to a fact, evidence item or tenant-supplied source inside the tenant;
- a draft with an unsupported testimonial, award or statistic cannot be submitted for approval;
- editing an approved draft makes a new version that is not approved;
- tenant A's voice or examples never appear in a context compiled for tenant B;
- a draft marked above `public` is never sent to the low-cost profile under the default policy;
- each draft shows which model profile and sources produced it.

## Tests
- Claim check on a labelled fixture set: supported, unsupported, fabricated proof, competitor comparison.
- Similarity threshold on fixtures.
- Version and hash behaviour; approval invalidation on edit.
- Provider-policy matrix for drafting.
- Injection in source material.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on all six tables across tenants; voice and examples isolation through the Context Compiler.
- Role tests: client approver can comment and decide through R2-007, cannot edit; viewer reads only.
- Evaluation set for voice match and factual accuracy, run through PresenceBench on the pinned profiles.

## Rollback / failure recovery
Drafts are versions; any earlier version can be restored as a new version. A bad voice version is superseded. Reverse migrations tested.

## Cost/resource budget
Proposed default: USD 0.05 per social post draft with variants, USD 0.40 per short article; a monthly content plan of 12 posts per client fits inside about USD 1 of the client cap.

## Documentation updates
- `docs/product/trust-and-attribution.md` (claim rule in practice), `docs/product/capability-map.md`, `docs/data/core-entity-catalog.md`.

## Open decisions
- **Decision required (owner):** whether generated content is marked as AI-assisted when published. Proposed default: follow each platform's labelling rule where one exists (recheck at task start); no extra label otherwise.
- **Decision required:** similarity threshold and method. Proposed default: block above 30% overlap of long word sequences with any single third-party source.
- **Decision required:** content languages at R3 start. Proposed default: English and Urdu, one language per item, with right-to-left handled.
- **Decision required:** whether a client may edit a draft. Proposed default: comment and approve or reject only.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: the claim-check fixture set is a protected test; the evaluation set results are stored.
