# R3-005 — SEO, AEO and GEO Basics

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 and R2 are built; recheck against their implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Make every site Presence hosts easy for search engines and AI answer engines to read, understand and cite. The basics are produced by deterministic code from site content and canonical facts. An audit turns what is missing into proposed site changes.

## Why now
Search and AI-search visibility is a named work area. R2 measured the baseline (R2-011, R2-014); R3 must be able to act on it, or the measurements lead nowhere.

## Context / linked docs / ADRs
- [Attention, opportunities, presence health and AI visibility](../../docs/product/attention-opportunities-and-scoring.md)
- [Capability map](../../docs/product/capability-map.md) (web and conversion; search, AI and local presence)
- [Trust, truth and attribution](../../docs/product/trust-and-attribution.md)
- [Communications, platform policy and jurisdiction](../../docs/compliance/communications-and-platform-policy.md)
- [Research notes: SEO, AEO/GEO](../../docs/research/GITHUB_LANDSCAPE_2026-11-10.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0011, ADR-0030

## Depends on
- R3-004 (site content and templates). Uses R2-003 (facts), R2-011 (site checks), R2-014 (baseline), R2-015 (opportunities).

## Invariants
- structured data and meta content are generated from canonical facts and approved content only. Nothing is invented to rank;
- no deceptive technique: no hidden text, cloaking, doorway pages, fake reviews in markup, or keyword stuffing;
- no promise of a rank or of being cited. Results are reported as measured rates (R2-014);
- technical outputs (sitemap, robots, canonical tags, structured data) are deterministic code, not model output;
- a change proposed by the audit is a normal site change: preview, diff, approval, deploy;
- previews are never indexable.

## In scope
- Generated for every hosted site at build time: title and description per page, canonical URL, language tags, Open Graph and social card tags, XML sitemap, `robots.txt`, structured data (JSON-LD) for Organization or LocalBusiness, WebSite, breadcrumb, and FAQ or Service where the content has them.
- `llms.txt` generated from the site outline and canonical facts.
- A machine-readable facts page section (name, address, phone, hours, services) matching canonical facts exactly, so answer engines read one consistent source.
- Heading structure, image alternative text and internal link checks in the verify step.
- Performance basics in templates: image sizing, lazy loading, no render-blocking third-party script by default.
- Redirect map per property: when a page is renamed or a site is rebuilt from an older one, old URLs redirect; managed as content, deployed with the site.
- On-page audit skill for a hosted site: uses the R2-011 checks plus the items above; output is a list of findings mapped to Opportunity rules.
- Content suggestions for answer engines: questions customers ask (from the R2-014 query set and research), with a proposed FAQ or service section drafted from canonical facts. Each is a proposed site change.
- AI-crawler policy per property in `robots.txt`: allow or disallow known AI crawlers. See open decisions.
- Before and after record: the R2-014 and R2-011 measurements taken before a change set, for R3-013.

## Out of scope
- Keyword rank tracking and paid keyword tools.
- Link building, outreach and guest posting (R4 or later).
- Google Search Console, Bing Webmaster and analytics connectors. **Decision required**; see open decisions.
- Auditing or changing sites that Presence does not host (findings for those are reported as advice only).
- Advertising.

## API / contract changes
- Build step contract: `seo_outputs(site_content, facts) → files`.
- Internal skill: `seo.audit(property) → findings`.
- Site content schema: per-page `seo` fields (title, description, canonical override, index flag), `redirects`.
- Opportunity rule catalogue gains SEO and AEO finding types.

## Data / migration
- Tenant-scoped under RLS: SeoAudit, SeoFinding. Redirects and SEO fields live in SiteContentVersion.
- Reverse migrations tested.

## Security / privacy threat notes
- Structured data that states something false (a rating with no reviews): generated only from typed facts with evidence; review and rating markup is disabled until a verified source exists.
- A model writing meta text that makes claims not on the page: meta text is derived from approved page content and passes the same approval.
- Open redirect through the redirect map: redirects only to paths on the same property.
- Preview indexed by a search engine: `noindex` header, robots rule and no sitemap on preview hosts; tested.
- `llms.txt` or facts section exposing something private: built from `public` class facts only.

## Edge cases covered
- E-023 preview leak through indexing.
- E-046 a conflicted fact is left out of structured data and flagged.
- E-083 deceptive or infringing content: blocked by rule and by approval.
- E-016 old URLs after a rebuild or delete: redirect map and holding response.

## Observability
- Audit: audit runs; SEO-affecting changes with before and after values.
- Metrics: findings per property by type, share of pages with valid structured data, build-time validation failures.

## Acceptance criteria
- every production site built by Presence has a valid sitemap, `robots.txt`, canonical tags, structured data and `llms.txt`, all consistent with canonical facts;
- structured data validates against the schema.org types used;
- no preview host is indexable;
- changing a canonical fact (for example hours) changes the structured data in the next build, and the diff shows it;
- the audit of a fixture site lists the seeded defects and each maps to an opportunity;
- no generated markup contains a rating, review or award without evidence.

## Tests
- Golden tests for each generated file from fixture content and facts.
- Structured-data validation against a local schema validator.
- Preview indexability test.
- Redirect map: same-site only; loops and chains rejected.
- Deceptive-pattern lint on generated output (hidden text, stuffed keywords).
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on SeoAudit and SeoFinding across tenants; facts of tenant A never appear in tenant B's generated files.
- Fact supersession → next build output changes.

## Rollback / failure recovery
All outputs are part of the site artifact; rollback of the site rolls them back. A validation failure blocks VERIFIED and leaves the live site as it is.

## Cost/resource budget
Generation is code and costs nothing in model spend. The audit and content suggestions use the low-cost profile on `public` data. Proposed default: USD 0.30 per audit.

## Documentation updates
- `docs/product/attention-opportunities-and-scoring.md`, `docs/product/capability-map.md` (what "basics" covers), a method note for clients on what is and is not promised.

## Open decisions
- **Decision required (owner):** default AI-crawler policy for client sites. Proposed default: allow search and answer-engine crawlers so the business can be cited; the operator can switch it per property.
- **Decision required (owner):** a read-only Google Search Console connector in R3. Proposed default: not in R3; it would be a third connector and needs Google's app verification. Raise it when Meta and LinkedIn are done.
- **Decision required:** which structured-data types are in the first set. Proposed default: Organization, LocalBusiness, WebSite, BreadcrumbList, FAQPage, Service.
- **Decision required:** use of third-party SEO skill packs named in the research notes. Proposed default: read for ideas only; if a pack is imported it follows the pack rule in R2-001 (review, hash pin).

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: one fixture site passes an external structured-data validator by hand and the result is recorded.
