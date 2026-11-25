# R2-011 — Presence Scan and Presence Graph

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 is built; recheck against the R1 implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Measure where a tenant appears online today and how correctly. The scan produces measurements with evidence, a Presence Graph that links the tenant's canonical facts to each surface, and a Presence Snapshot that states what is known, uncertain and missing.

## Why now
The onboarding target is useful work within 10 to 15 minutes of creating a tenant, without DNS or connected accounts. Scores, competitors and opportunities all read the scan.

## Context / linked docs / ADRs
- [Presence Graph and Digital Presence Passport](../../docs/data/presence-graph-passport.md)
- [Client onboarding and time-to-value](../../docs/product/onboarding-and-first-value.md)
- [Runbook: new tenant first 15 minutes](../../docs/runbooks/new-tenant-first-15-minutes.md)
- [Attention, opportunities, presence health and AI visibility](../../docs/product/attention-opportunities-and-scoring.md)
- [Trust, truth and attribution](../../docs/product/trust-and-attribution.md)
- [Core entity catalog](../../docs/data/core-entity-catalog.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0011, ADR-0021

## Depends on
- R2-010 (research), R2-003 (facts). Uses R2-001, R1-011 (properties).

## Invariants
- the scan is read-only and uses only public information, or data from the tenant's own connected accounts when a connection exists and allows reading;
- every measurement keeps its evidence and its method version;
- a scan finding is an Observation. It never changes a canonical fact by itself;
- report honestly: "not found" and "could not check" are different results;
- no relational shortcut: the graph is tables in PostgreSQL, tenant-scoped.

## In scope
- PresenceSurface catalogue (platform-level): website, search listing, AI search, maps/local listing, social profile per platform, review site, directory. Each has a check definition and version.
- TenantSurface: a tenant's instance of a surface (for example its Facebook page URL), found by the scan or entered by the operator, with status FOUND, NOT_FOUND, UNVERIFIED, NOT_CHECKED.
- PresenceMeasurement: surface, check, value, evidence, method version, time.
- Scan workflow: take minimal profile input; find the tenant's surfaces by research; run checks per surface; write Observations and Candidate Facts; build the snapshot. Checkpointed per surface.
- Checks in R2 (public data only): site reachable and basics (title, description, HTTPS, mobile viewport, structured data present, `robots.txt`, sitemap, `llms.txt`); name, address, phone and hours as shown on each found surface; presence or absence of a profile on the main social platforms; listing presence on a short list of directories.
- Consistency check: compare what each surface shows with canonical facts; produce gap findings: MISSING, INCORRECT, STALE, WEAK.
- Presence Graph: edges fact → surface with state (matches, differs, absent, unknown) and evidence.
- Presence Snapshot artifact: known, uncertain, missing; gaps by surface; the questions the operator must answer to settle facts.
- Rescan: on request or on a schedule (through R2-009); results are compared with the previous scan.
- Scan of an existing site owned by the tenant uses the bounded crawl from R2-010.

## Out of scope
- Scores (R2-012), competitors (R2-013), AI visibility sampling (R2-014).
- Fixing anything found (R3).
- Review content analysis and reputation scoring (R4).
- Private analytics data. **Decision required**; see open decisions.
- The Digital Presence Passport export.

## API / contract changes
- Internal: `start_scan(tenant, scope)`, `get_snapshot(tenant, version)`, `list_gaps(tenant)`.
- Endpoints: start scan, scan status, snapshot, gaps, confirm or correct a found surface.
- New contract sketches: `presence-surface.schema.json`, `presence-measurement.schema.json`, `presence-gap.schema.json`.

## Data / migration
- Platform table: PresenceSurface, SurfaceCheck (versioned).
- Tenant-scoped under RLS: TenantSurface, PresenceMeasurement, PresenceGap, PresenceGraphEdge, PresenceScan.
- Reverse migrations tested.

## Security / privacy threat notes
- A look-alike or impostor profile taken as the tenant's own: found surfaces are UNVERIFIED until the operator or client confirms them.
- Scan content with injected instructions: same rules as R2-010.
- Personal data about staff or customers found on public pages: stored only when it is a fact kind the tenant needs; classed `personal_data`.
- Scanning a site the tenant does not own at crawl depth: full crawl only for surfaces confirmed as the tenant's; others get a single-page check.
- Platform terms: profile checks use public pages or official APIs only; no sign-in, no bypass.

## Edge cases covered
- E-046 contradictory facts across surfaces become conflicts, not overwrites.
- E-074 wrong account: a surface must be confirmed before it is treated as the tenant's.
- E-009 budget exhausted mid-scan: checkpoint per surface, resume.
- E-013 a tenant with many properties: one scan covers each property's site as its own surface.

## Observability
- Audit: scan started and by whom, surfaces confirmed or rejected.
- Metrics: scan duration, surfaces found, checks failed to run, cost per scan, gap counts by kind.

## Acceptance criteria
- a new tenant with only a name, city and site URL gets a snapshot inside the time target on fixture data;
- every gap links to the evidence and to the fact it compares against;
- an unconfirmed surface never feeds a canonical fact;
- a rescan shows what changed since the last one;
- a check that could not run is reported as NOT_CHECKED, not as a failure of the tenant;
- the scan performs no write to any external system.

## Tests
- Fixture tenant with a fixture site and fixture profile pages: expected surfaces, measurements and gaps.
- Consistency: each gap kind produced by a prepared mismatch.
- Impostor profile fixture stays UNVERIFIED.
- Resume after a killed worker repeats no completed surface.
- Method versioning: changing a check creates a new version; old measurements keep the old one.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on all tenant tables across tenants; snapshot artifact of tenant A not readable by tenant B.
- No external write: broker and connection fakes record zero calls.

## Rollback / failure recovery
A scan is a workflow; a failed surface is retried alone. A bad check version is superseded. Reverse migrations tested.

## Cost/resource budget
Proposed default per scan: USD 1.00 and 15 minutes, in the "internal scans" class. Extraction runs on the low-cost profile; the snapshot summary on the frontier profile when the operator started the scan.

## Documentation updates
- `docs/data/presence-graph-passport.md`, `docs/product/onboarding-and-first-value.md`, `docs/runbooks/new-tenant-first-15-minutes.md`, `docs/data/core-entity-catalog.md`.

## Open decisions
- **Decision required:** the first list of directories and social platforms the scan checks. Proposed default: the tenant's site, Google search listing presence, Google Maps listing presence, Facebook, Instagram, LinkedIn, and up to five directories chosen per country.
- **Decision required:** whether R2 reads private analytics (Google Search Console, Google Analytics) through a read-only connection. Proposed default: no; public data only in R2, a read-only connector is proposed for R3 or R4.
- **Decision required:** default rescan period. Proposed default: monthly, as an unattended read-only schedule.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: the first-15-minutes runbook is run once on a fixture tenant and the timing is recorded.
