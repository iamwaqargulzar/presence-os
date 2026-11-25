# R3-007 — Image Generation through the Gateway

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 and R2 are built; recheck against their implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Produce images for posts and sites through the AI Capability Gateway's `image()` operation, under the same provider policy, budget and audit as text. An image is a draft artifact with provenance; it is published only through approval.

## Why now
Posts and pages need images. The release plan names "image generation through the AI Capability Gateway" for R3.

## Context / linked docs / ADRs
- [AI Capability Gateway](../../docs/ai/capability-gateway.md)
- [Local inference, media and voice](../../docs/ai/local-inference-media-voice.md)
- [Tenant Presence AI, model profiles and provider policy](../../docs/ai/tenant-ai-model-entitlements.md)
- [Cost and resource governance](../../docs/architecture/cost-resource-governance.md)
- [Trust, truth and attribution](../../docs/product/trust-and-attribution.md)
- [File ingestion security](../../docs/security/file-ingestion.md)
- [Release plan](../../docs/delivery/release-plan.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0010, ADR-0013, ADR-0023, ADR-0030, ADR-0033

## Depends on
- R3-006 (content items that images attach to). Uses R0-007 (gateway), R1-004, R1-008, R1-009, R1-012.

## Invariants
- image generation goes through the gateway. No module calls an image provider or a local ComfyUI port directly;
- routing is CLOUD_ONLY by default. Local generation is used only when the GPU host is on and a local image profile is ACTIVE; nothing depends on it;
- the tenant's provider policy applies to prompts and to reference images sent out;
- model and provider names are configuration;
- budget is reserved before the call;
- never generate an image that presents an invented person as a real customer, employee or endorser, or that imitates a real person or a third party's brand;
- a generated image is a draft until approved.

## In scope
- Image model profiles in the registry (capability `image_generation`), with price reference per image and size, and the credential class `API`.
- An adapter for one cloud image provider behind the gateway. An adapter for the local ComfyUI service is specified but optional.
- ImageRequest: tenant, purpose, prompt, size and aspect, style reference from brand settings, optional reference images (the tenant's own, through quarantine), count.
- Prompt building by a skill from the content item and brand settings; the prompt contains `public` class information unless policy allows more.
- Output handling: result stored as an artifact with hash; passed through file validation; metadata stripped or set; resized variants for each channel.
- Provenance: model profile, prompt, seed where available, time; and a content-credential mark where the provider supplies one.
- Selection flow: several candidates → operator picks → the chosen image is attached to the content item, which changes the item's hash.
- Alternative text drafted for every image and editable.
- Safety checks: provider-side moderation result recorded; a deny list for real-person names, competitor brands and protected marks in prompts.
- Reuse: a tenant media library of approved images.
- Budget and Resource Governor: media queue class; per-tenant monthly image count limit.

## Out of scope
- Video, audio and animation.
- Photo editing tools and a design editor.
- Logo and brand identity design as a finished service.
- Training or fine-tuning on a client's images.
- Stock photo licensing integrations.

## API / contract changes
- Gateway: concrete request and result shape for `image()`; usage recorded per image.
- Internal skill: `media.generate_image`.
- Endpoints: request images, list candidates, select, media library.
- New contract sketch: `media-asset.schema.json`.

## Data / migration
- Tenant-scoped under RLS: ImageRequest, MediaAsset (artifact reference, hash, provenance), MediaVariant.
- Reverse migrations tested.

## Security / privacy threat notes
- Prompt or reference image leaking confidential data to a provider: data-class check on the prompt and on each reference image; the default for a new tenant is `public` only.
- Likeness, trademark and copyright risk (E-083): deny list, human selection and approval, provenance; the takedown path in R3-008 covers images.
- Misleading imagery (fake product, fake premises, fake team): flagged at selection with a required confirmation "this is illustrative"; never used in testimonial or team sections.
- Returned files: treated as untrusted files; type-validated and re-encoded before use.
- Cost run-away through large batches: count limits and reservation.
- Local path: the ComfyUI port stays private; reached only by the gateway (AGENTS.md).

## Edge cases covered
- E-062 GPU host off and a local-only image profile requested: pause with a reason; default route is cloud.
- E-063 provider policy for prompts and reference images.
- E-083 infringing content.
- E-009 budget exhausted mid-batch: finished images kept, rest cancelled.
- E-003 image model retired: profile revision change through the R1-013 procedure.
- E-048 attaching a different image after approval invalidates the approval.

## Observability
- Audit: request, profile used, images produced, selection, attachment.
- Metrics: images per tenant, cost per image, rejection rate at selection, moderation blocks.

## Acceptance criteria
- an image is produced only through the gateway, with a reservation and a ledger record;
- a tenant whose policy excludes the image provider gets a clear "not allowed by policy" result and no call is made;
- with the GPU host off, generation works by cloud and no error mentions the local host;
- every stored image has a hash, provenance and alternative text;
- replacing the image on an approved content item removes the approval;
- a prompt naming a real person or a competitor's brand is refused before the call.

## Tests
- Fake image adapter: success, moderation block, timeout, partial batch.
- Provider-policy matrix for prompt and reference image classes.
- Routing: host off, host on with and without an ACTIVE local profile.
- Deny list.
- File validation of returned bytes (wrong type, oversized, malformed).
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on the three tables across tenants; media library and artifact ID substitution.
- Import boundary: an image SDK imported outside the adapter layer fails the gate.
- No paid calls in CI.

## Rollback / failure recovery
The image profile can be disabled by configuration; drafts then proceed without images. Stored images are artifacts and are unaffected by a provider change.

## Cost/resource budget
Proposed default: at most 40 generated images per client per month and USD 3 of the client cap; 4 candidates per request.

## Documentation updates
- `docs/ai/capability-gateway.md` (image operation), `docs/ai/local-inference-media-voice.md` (local image path is optional), `docs/ai/model-harness-registry.md`.

## Open decisions
- **Decision required (owner):** the cloud image provider and model. Proposed default: choose at task start by price, licence terms for commercial use and a small PresenceBench comparison; record it as configuration.
- **Decision required:** build the local ComfyUI adapter in R3. Proposed default: no; cloud only, because the GPU host may stay off (ADR-0030). The older documents that say "local image generation" are superseded by the release plan.
- **Decision required:** monthly image limit and money share. Proposed default above.
- **Decision required:** whether images of people are allowed at all. Proposed default: no realistic people unless the operator confirms per image.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: the provider's commercial-use terms are checked and the date recorded.
