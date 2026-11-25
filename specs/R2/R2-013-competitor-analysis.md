# R2-013 — Competitor Analysis

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 is built; recheck against the R1 implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
For each tenant, keep a short confirmed list of competitors and compare their public presence with the tenant's, from evidence. The result feeds the Opportunity Engine and the AI-visibility query sets.

## Why now
"Where are we weaker than the others?" is one of the two central questions of the Opportunity Engine. AI-visibility metrics such as share and win rate need a competitor set.

## Context / linked docs / ADRs
- [Attention, opportunities, presence health and AI visibility](../../docs/product/attention-opportunities-and-scoring.md)
- [Product vision and scope](../../docs/product/vision-and-scope.md)
- [Relationship graph](../../docs/architecture/relationship-and-conversation-graph.md) (Organization as competitor)
- [Trust, truth and attribution](../../docs/product/trust-and-attribution.md)
- [Communications, platform policy and jurisdiction](../../docs/compliance/communications-and-platform-policy.md)
- [Context, cache and AI economics](../../docs/ai/context-cache-economics.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0011

## Depends on
- R2-010 (research), R2-011 (surface checks reused on competitors).

## Invariants
- public information only. No sign-in, no bypass, no pretending to be a customer;
- a competitor's data is never stored as the tenant's fact;
- a suggested competitor is a candidate until a person confirms it;
- one tenant's competitor list and analysis are private to that tenant, even if another tenant is itself that competitor;
- claims about a competitor in any report are tied to evidence and stated as observations, not judgments;
- no cross-tenant data is used: tenant B's private data never informs tenant A's analysis.

## In scope
- Competitor entity: tenant, organisation name, site, surfaces, status (SUGGESTED, CONFIRMED, DISMISSED), why suggested, evidence.
- Discovery skill: suggest competitors from the tenant's services, location and search results; the operator confirms or dismisses.
- Limit on confirmed competitors per tenant.
- Competitor profile from the R2-011 surface checks, run in single-page mode: site basics, presence on platforms, listing presence, stated services and prices where public.
- Comparison artifact: a table of tenant against each competitor per surface and per measured component, with evidence links and dates.
- Change watch: a scheduled, unattended, read-only recheck that reports only changes (new service, new profile, changed pricing page).
- Reuse: competitor snapshots are cached for their freshness period (R2-010) and stored as structured artifacts.

## Out of scope
- Market, trend and pricing research beyond the competitor's own public pages.
- Paid competitive-intelligence data sources.
- Advertising and keyword spying tools.
- Any outreach to or interaction with a competitor.
- Sentiment and review analysis (R4).

## API / contract changes
- Internal: `suggest_competitors(tenant)`, `profile_competitor(id)`, `compare(tenant)`.
- Endpoints: list, confirm, dismiss, add by URL; get comparison.
- New contract sketch: `competitor.schema.json`.

## Data / migration
- Tenant-scoped under RLS: Competitor, CompetitorMeasurement, ComparisonReport.
- Reverse migrations tested.

## Security / privacy threat notes
- Two tenants that compete with each other: each one's analysis uses only public fetches made under its own tenant; no join ever crosses tenants; cache is per tenant. A test covers this exact case.
- A competitor's page crafted to inject instructions into analysts' tools: untrusted content rules of R2-010.
- Defamation risk: reports state what was observed, where and when; no generated judgments about a competitor's quality or honesty.
- Heavy crawling of a competitor's site: single-page checks, polite limits, robots rules.
- Personal data of a competitor's staff: not collected.

## Edge cases covered
- E-044 cache across tenants.
- E-046 the tenant's facts are not altered by what a competitor's page claims.
- E-083 defamation: wording rule for reports.
- E-021 crawl concurrency per tenant.

## Observability
- Audit: competitor confirmed or dismissed, by whom.
- Metrics: suggestions accepted, cost per comparison, changes detected per watch.

## Acceptance criteria
- a suggested competitor has no effect on scores, opportunities or query sets until confirmed;
- every cell of the comparison links to evidence with a date;
- with tenants A and B each listing the other as competitor, neither analysis contains anything from the other's private data, and neither can see that the other lists it;
- a change watch produces a notification only when something changed;
- the analysis performs no external write.

## Tests
- Fixture market: three fixture sites; expected suggestions, profiles and comparison.
- Mutual-competitor isolation test under the runtime role.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on all three tables across tenants.
- Wording check: report templates contain no judgment terms; a lint test on generated summaries against a deny-list.
- Limits: the per-tenant competitor cap and crawl limits.
- No external write: broker fake records zero calls.

## Rollback / failure recovery
Analyses are artifacts; a bad one is replaced by a new run. A competitor can be dismissed at any time, which removes it from later comparisons. Reverse migrations tested.

## Cost/resource budget
Proposed default: at most 5 confirmed competitors per tenant; USD 0.50 per full comparison; the watch runs monthly on the low-cost profile because all inputs are `public`.

## Documentation updates
- `docs/product/attention-opportunities-and-scoring.md`, `docs/data/core-entity-catalog.md`.

## Open decisions
- **Decision required:** competitor cap per tenant. Proposed default: 5.
- **Decision required:** watch period. Proposed default: monthly.
- **Decision required:** whether clients see the competitor comparison. Proposed default: yes, read-only, after the operator has reviewed it once.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: the mutual-competitor test joins the protected tenant-isolation suite.
