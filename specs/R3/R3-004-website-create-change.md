# R3-004 — Website Create and Change

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 and R2 are built; recheck against their implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Let the operator create a website for a tenant, or change an existing one, by asking in plain language. The AI edits structured site content and a controlled set of templates. Every change is shown as a preview and a diff before anything goes live.

## Why now
Website creation and improvement with hosting is the first named work area of the product, and the first R3 deliverable in the release plan.

## Context / linked docs / ADRs
- [Product vision and scope](../../docs/product/vision-and-scope.md)
- [Digital properties and multi-property hosting](../../docs/product/digital-properties-and-hosting.md)
- [Trust, truth and attribution](../../docs/product/trust-and-attribution.md)
- [Accessibility and localization](../../docs/product/accessibility-localization.md)
- [UI / visual design direction](../../docs/ux/design-direction.md)
- [Canonical knowledge, facts and memory](../../docs/data/knowledge-and-memory.md)
- [Research notes: website generation](../../docs/research/GITHUB_LANDSCAPE_2026-11-10.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0011, ADR-0021, ADR-0030

## Depends on
- R3-003 (deploy path). Uses R3-001 (build), R3-002 (preview), R2-001, R2-003 (facts), R2-005, R2-007, R1-008.

## Invariants
- site content is a versioned, hashable artifact; an approval binds to its hash;
- every public statement about the business comes from a canonical fact or from text a person supplied and approved. Never fabricate customers, testimonials, reviews, awards or results;
- the AI changes a site only inside the property's source tree, through the build pipeline. It has no deploy permission;
- no change reaches production without a preview;
- generated sites meet WCAG 2.2 AA on the template level;
- a tenant can have several sites; nothing assumes one;
- no code is copied from other projects' templates or builders (ADR-0030, E-088).

## In scope
- Site content model: site settings, navigation, pages, sections (typed blocks with fields), media references, per-language variants. Stored as structured JSON, canonicalised and hashed.
- An in-house template and component set for the `static` profile: a small number of page layouts and section types, built on semantic tokens so brand colours and type can be set per property.
- Brand settings per property: colours, type, logo, tone reference; entered by the operator or proposed from the client's existing site and confirmed.
- Create flow: from tenant facts, goals and the Presence Snapshot, propose a site outline → operator confirms → generate content → build → preview.
- Change flow: a plain request ("add our new service", "change the phone number") → the Director creates a task → the web skill edits content or, when needed, template code inside the property source → build → preview → diff.
- Diff view: content changes as before and after text; visual change as two preview links; list of changed pages.
- Existing site improvement: read the tenant's current public site with R2-010, propose a rebuilt version in the content model, and list what was kept, changed and dropped. Nothing is copied from a site the tenant does not own.
- Fact binding: fields such as phone, address and hours reference canonical facts; when a fact is superseded, affected pages are listed as a proposed change.
- Contact form on static sites: posts to a small Presence-run endpoint on the tenant-site domain, with spam protection, storing submissions for the tenant and notifying the operator. See open decisions.
- Media: uploads through file quarantine; images optimised at build; alternative text required.
- Manual edit: the operator can edit a text field directly in the console; it follows the same version, preview and approval path.
- Client flow: a client request for a site change is a queue item; a client approves the diff where policy requires.

## Out of scope
- SEO and AI-search specifics (R3-005). Image generation (R3-007). Long-form content strategy (R3-006).
- A drag-and-drop visual page builder for clients.
- WordPress or other external CMS integration; ecommerce, booking systems, portals with logins (later releases).
- Free-form application code generation for server runtimes.
- Importing a site by copying another party's design.

## API / contract changes
- Internal skills: `site.outline`, `site.generate`, `site.change`, `site.import_own_site`.
- Endpoints: site content read; propose change; get diff; edit field (with `base_version`); form submissions list.
- New contract sketches: `site-content.schema.json`, `site-change.schema.json`.

## Data / migration
- Tenant-scoped under RLS: SiteContentVersion (artifact reference and hash), SiteChange, BrandSettings, FormSubmission.
- Template source lives in the platform repository; a property pins a template version.
- Reverse migrations tested.

## Security / privacy threat notes
- Generated HTML or script carrying an attack (cross-site scripting, hidden links, cryptominer): content fields are typed and escaped by the templates; free HTML blocks are not offered; the verify step scans output.
- Injection through the client's existing site during import: fetched text is untrusted data and can only fill content fields after review.
- Fabricated proof: a deny check blocks testimonial, review, award and client-logo sections unless each item links to evidence.
- Form endpoint abuse (spam, data harvesting, personal data intake): rate limits, challenge that does not block assistive technology, submissions classed `personal_data`, retention rule.
- Wrong-tenant content: facts and media are resolved only inside the acting tenant.
- Model-written template code: goes through build verification and, for template changes, review before merge into the property source.

## Edge cases covered
- E-048 and E-072 content changed after approval.
- E-046 a conflicted fact cannot be published; the page shows the gap in preview.
- E-083 infringing or defamatory content: approval, provenance and the takedown path in R3-008.
- E-088 no copied code or templates.
- E-013 many properties per tenant.
- E-063 site text is `public` class once approved; drafts with unreleased information are `business_internal`.

## Observability
- Audit: each change with requester, authority source, content hashes before and after, model profile used.
- Metrics: time from request to preview, changes rejected at review, build failures caused by generated code, cost per change.

## Acceptance criteria
- from a fixture tenant with facts and goals, the operator gets a previewable multi-page site without writing code;
- "change the phone number" produces a diff that touches only the bound fact fields;
- every testimonial-type block without evidence is refused;
- the approved hash equals the deployed hash;
- generated pages pass the automated accessibility checks and keyboard navigation;
- a client can view the preview and approve or reject, and cannot edit or deploy;
- two sites for one tenant are independent in content, brand and history.

## Tests
- Golden generation tests on fixtures (structure, not wording).
- Schema validation of content; hostile content fields rendered inert.
- Fact binding and supersession proposal.
- Fabrication deny check.
- Import of a fixture "own site" containing injected instructions.
- Concurrency: two edits on one `base_version` → one conflict.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on all four tables across tenants; form submissions of tenant A not readable by tenant B; media ID substitution.
- Accessibility checks on every template; right-to-left layout check.
- Form endpoint: rate limit, oversized input, script input.

## Rollback / failure recovery
Content is versioned; any earlier version can be rebuilt and deployed through R3-003. A failed generation leaves the current version untouched.

## Cost/resource budget
Proposed default: USD 1.50 for a new site draft, USD 0.20 for a simple change; frontier profile for outline and template code, low-cost profile for formatting `public` text.

## Documentation updates
- `docs/product/digital-properties-and-hosting.md`, `docs/product/vision-and-scope.md`, a guide "how a site change flows".

## Open decisions
- **Decision required (owner):** build the site generator and templates fully in-house, or use a permissively licensed library for the editor or content layer (the research notes name Puck, MIT). Proposed default: in-house templates and content model; no CMS application deployed; a library only after dependency review.
- **Decision required (owner):** contact forms in R3. Proposed default: yes, one simple form type, submissions kept 180 days and shown to the operator and the client.
- **Decision required:** languages of generated sites. Proposed default: one language per site in R3, chosen per property, with right-to-left supported by the templates.
- **Decision required:** whether a client may edit text directly. Proposed default: no; clients request and approve.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: provenance review confirms no third-party template code; a manual accessibility pass on each template is recorded.
