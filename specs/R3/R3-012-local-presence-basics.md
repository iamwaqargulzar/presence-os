# R3-012 — Local Presence Basics

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 and R2 are built; recheck against their implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Keep a local business's name, address, phone, hours and services correct and the same everywhere. In R3 this is done without a new platform connector: the site carries the canonical details, the scan finds where listings differ, and Presence prepares exact corrections that a person applies on each listing.

## Why now
The release plan lists "local basics" in R3. Many of the operator's clients are local businesses, and wrong hours or phone numbers are the most common and most harmful presence gap.

## Context / linked docs / ADRs
- [Capability map](../../docs/product/capability-map.md) (search, AI and local presence)
- [Presence Graph and Digital Presence Passport](../../docs/data/presence-graph-passport.md)
- [Canonical knowledge, facts and memory](../../docs/data/knowledge-and-memory.md)
- [Social, community and browser automation policy](../../docs/integrations/social-browser-policy.md)
- [Trust, truth and attribution](../../docs/product/trust-and-attribution.md)
- [Do not build early](../../docs/delivery/do-not-build-early.md) (every social connector)
- [Research notes](../../docs/research/GITHUB_LANDSCAPE_2026-11-10.md) (no open project found for local listings)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0011, ADR-0031

## Depends on
- R3-005 (LocalBusiness structured data), R3-006 (drafting). Uses R2-003, R2-011, R2-015, R2-007, R2-009.

## Invariants
- the canonical facts are the single source for local details. A listing never overwrites a fact;
- Presence does not sign in to a listing site, does not automate a browser on it and does not bypass any verification step. A person makes the change on the platform;
- never create fake listings, fake reviews or review requests that pressure or reward customers;
- a listing is treated as the tenant's only after confirmation;
- review replies and review requests are not sent by the system in R3.

## In scope
- Location entity per tenant: one or more business locations, each with canonical name, address, phone, hours, special hours, categories, service area, map coordinates. Bound to canonical facts.
- Listing register: the tenant's confirmed listings (Google Business Profile, Bing Places, Apple Business Connect, Facebook Page details, and country-specific directories), each with URL, last checked values and state.
- Local consistency check: a scheduled, unattended, read-only task that reads each public listing page through R2-010 and compares it with the canonical details. Differences become gaps and opportunities.
- Correction pack: for each difference, an exact instruction for a person ("on listing X change the phone from A to B"), with the canonical value to copy, a link to the listing's edit page, and a place to mark it done. Shown to the operator; may be shared with the client as a request to act.
- Verification follow-up: after a pack is marked done, the next check confirms it or reopens it.
- Site side: location pages, embedded address and hours from facts, LocalBusiness structured data per location (through R3-005), a map link that needs no third-party script by default.
- Hours change flow: operator or client states new or holiday hours → fact update → site change proposal → correction pack for listings → optional social post draft.
- Facebook Page details: where the Meta connector's granted permissions allow reading Page details, compare them through the API instead of the public page. Writing Page details is not in R3.
- Review visibility: count and average rating read from public pages where visible, stored as measurements only.

## Out of scope
- A Google Business Profile API connector. **Decision required**; see open decisions.
- Posting to listings, replying to reviews, requesting reviews (R4).
- Paid listing-distribution services.
- Managed browser sessions to edit listings (R4, E-056).
- Creating new listings on the client's behalf.

## API / contract changes
- Internal: `local.check(tenant)`, `local.correction_pack(tenant)`.
- Endpoints: locations create and edit (with `base_version`), listings confirm, correction pack view, mark item done.
- New contract sketches: `location.schema.json`, `listing.schema.json`.
- Opportunity rule catalogue gains local finding types.

## Data / migration
- Tenant-scoped under RLS: Location, Listing, ListingObservation, CorrectionItem.
- Reverse migrations tested.

## Security / privacy threat notes
- An impostor or duplicate listing taken as the real one: confirmation step; duplicates are reported as findings, not edited.
- A listing page containing injected text: untrusted content rules of R2-010.
- A home-based business whose address should not be public: per-location flag "hide address"; site and structured data respect it.
- Automated edits against platform rules: none are made; the design removes the temptation.
- A client marking a correction "done" without doing it: the next check verifies.

## Edge cases covered
- E-046 a listing that disagrees with canonical facts creates a gap, and a conflict only if a person says the listing is right.
- E-074 wrong listing or account confirmed as the tenant's.
- E-061 the scheduled check never uses the subscription.
- E-083 no fabricated reviews or claims.
- E-013 several locations and several sites per tenant.

## Observability
- Audit: location and hours changes with source; listings confirmed; correction items marked done and verified.
- Metrics: consistency rate per tenant, open correction items and their age, time from hours change to all listings verified.

## Acceptance criteria
- a fixture business with three listings, one wrong phone and one wrong hours entry, gets a correction pack with exactly those two items and exact values;
- after the fixture listings are fixed, the next check closes the items without a person;
- a new holiday-hours statement produces a fact update, a site change proposal and a correction pack from one request;
- no code path signs in to, or submits a form on, a listing site;
- a location flagged "hide address" shows no street address on the site or in structured data.

## Tests
- Fixture listing pages: comparison logic for name variants, phone formats, hours formats and address formats.
- Correction pack generation and verification loop.
- Hours change flow end to end with fakes.
- Injection in a fixture listing page.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on the four tables across tenants.
- No external write: broker and connection fakes record zero calls from this module.
- Role tests: a Client Requester can mark a shared correction item done; a Viewer cannot.

## Rollback / failure recovery
All outputs are proposals and records. A wrong correction pack is regenerated from facts. Reverse migrations tested.

## Cost/resource budget
Proposed default: monthly check per tenant on the low-cost profile (`public` data), under USD 0.20 per tenant per month.

## Documentation updates
- `docs/product/capability-map.md` (what "local basics" covers in R3), `docs/data/core-entity-catalog.md`.

## Open decisions
- **Decision required (owner):** a Google Business Profile connector in R3. Proposed default: no. It is a third platform approval and would break "one platform at a time". R3 gives manual correction packs; the connector is proposed as the first R4 contract if local clients are the majority.
- **Decision required:** the directory list per country. Proposed default: decided per tenant by the operator, at most five beyond the main four.
- **Decision required:** whether correction packs are shared with clients by default. Proposed default: yes for tenants with a Requester or Approver; otherwise the operator applies them.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: the "no external write" test is part of the suite.
