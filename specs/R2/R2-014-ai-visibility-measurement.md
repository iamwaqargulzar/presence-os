# R2-014 — AI Visibility Measurement

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 is built; recheck against the R1 implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Measure how often AI answer engines mention and cite a tenant, by asking a fixed set of questions many times and counting. Report rates with confidence, never a fixed rank. Keep every raw answer and the method.

## Why now
AI-search visibility is a named work area and a decided measurement rule. R3 (AEO and GEO work) needs a baseline taken before the work starts, or no improvement can be shown.

## Context / linked docs / ADRs
- [Attention, opportunities, presence health and AI visibility](../../docs/product/attention-opportunities-and-scoring.md)
- [Decision Register](../../docs/DECISION_REGISTER.md) (AI visibility measured stochastically)
- [Trust, truth and attribution](../../docs/product/trust-and-attribution.md)
- [AI Capability Gateway](../../docs/ai/capability-gateway.md)
- [Tenant Presence AI, model profiles and provider policy](../../docs/ai/tenant-ai-model-entitlements.md)
- [Research notes: AI visibility trackers](../../docs/research/GITHUB_LANDSCAPE_2026-11-10.md)
- [Core entity catalog](../../docs/data/core-entity-catalog.md) (AIVisibilityQuerySet, AIVisibilitySample)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0011, ADR-0013

## Depends on
- R2-011 (canonical identity and surfaces), R2-013 (competitor set). Uses R0-007 (gateway), R1-004 (budget), R2-009 (schedule).

## Invariants
- measure `Query Set × Location × Language × Provider × Repeated Samples`. Never state "rank #3 in ChatGPT";
- every metric is shown with its sample count and a confidence interval;
- raw sample answers and the method version are kept;
- measured providers are reached only through official APIs, through the gateway. No scraping of consumer chat sites, no bypass;
- the measurement targets are a separate list from the tenant's working models. A provider may be a measurement target for a tenant only with `public` data, because queries contain only public information;
- queries never contain confidential tenant data.

## In scope
- AIVisibilityQuerySet: tenant, versioned list of queries with intent tags, locations and languages. Drafted by a skill from the tenant's services and location; confirmed by the operator before first use.
- MeasurementTarget registry (platform-level): provider, model or product, whether web search grounding is on, API route, price, status. Distinct from AIModelProfile routing.
- Sampling workflow: for each query × location × language × target, take N samples with fixed settings; store each AIVisibilitySample (raw answer, citations, time, target revision, cost).
- Extraction per sample by deterministic matching first (tenant name, domains, known aliases; competitor names), then a low-cost model check for sentiment and factual accuracy against canonical facts.
- Metrics per target and overall: mention rate, citation rate, visibility share against confirmed competitors, sentiment, factual accuracy, competitor win rate, each with sample count and interval.
- Inaccuracy findings: an answer that contradicts a canonical fact becomes a finding with the raw answer as evidence.
- Runs: baseline on request; repeat on a schedule as an unattended read-only task on API profiles.
- Method version: sampling settings, N, extraction rules. A change makes a new version and marks the trend.
- Budget estimate shown before a run: queries × locations × languages × targets × N × price.
- Feed into R2-012 as the "AI visibility" component once a baseline exists.

## Out of scope
- Changing anything to improve visibility (R3-005).
- Measuring consumer chat products through a browser.
- Traditional search rank tracking. **Decision required**; see open decisions.
- Claims of cause between work done and a metric change (R3-013).

## API / contract changes
- Internal: `draft_query_set`, `estimate(run)`, `start_measurement`, `get_metrics(tenant, period)`.
- Endpoints: query set review and confirm; run, status; metrics; sample browser.
- Gateway: a `measure()` path that calls a MeasurementTarget with fixed settings and no tenant context beyond the query, still recorded in the usage ledger.
- New contract sketches: `ai-visibility-query-set.schema.json`, `ai-visibility-sample.schema.json`.

## Data / migration
- Platform table: MeasurementTarget (versioned).
- Tenant-scoped under RLS: AIVisibilityQuerySet, AIVisibilityRun, AIVisibilitySample, AIVisibilityMetric.
- Raw answers in object storage when large.
- Reverse migrations tested.

## Security / privacy threat notes
- Query leakage: a query that names a client's private plan or customer. Queries are built from `public` class facts only and are confirmed by the operator.
- Provider policy: a tenant's policy can exclude a provider entirely; that target is then skipped and reported as "not measured by policy" (E-063).
- Answers are untrusted content. An answer containing instructions is data.
- Cost run-away: the product of the five dimensions grows fast; the estimate and a hard reservation come before the first call.
- Misleading numbers: small N shown as certainty. Intervals and minimum N are enforced in the display.

## Edge cases covered
- E-063 provider excluded by tenant policy.
- E-008 costs in money with price snapshots.
- E-009 budget exhausted mid-run: completed samples are kept, the run is PARTIAL and metrics show the lower N.
- E-003 a target model is retired: the target gets a new revision; trends mark the change.
- E-061 scheduled measurement never uses the subscription.

## Observability
- Audit: query set confirmed, run started, target revisions used.
- Metrics: samples per run, cost per run and per tenant, extraction disagreements between rule and model.

## Acceptance criteria
- no screen or report shows a rank position; every metric shows N and an interval;
- every metric can be opened down to the raw samples behind it;
- the same samples and method version always give the same metrics;
- a target excluded by the tenant's provider policy receives no call;
- a run that would exceed its budget is refused before the first call, with the estimate shown;
- an answer contradicting a canonical fact appears as an inaccuracy finding with evidence.

## Tests
- Fake targets with seeded answer distributions: computed rates fall inside expected intervals.
- Determinism of metric computation from stored samples.
- Extraction: name variants, competitor names, false matches (a different company with a similar name).
- Provider-policy skip.
- Budget: estimate accuracy, refusal, partial run.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on all tenant tables across tenants; samples of tenant A not readable by tenant B.
- Injection: a seeded answer with instructions changes nothing.
- No live provider calls in CI.

## Rollback / failure recovery
Samples are append-only. A flawed method version is retired; its metrics stay marked with that version. Reverse migrations tested.

## Cost/resource budget
Proposed default for a baseline: 15 queries × 1 location × 1 language × 2 targets × 5 samples = 150 calls, with a cap of USD 2.00 per run and one scheduled run per month. This is a visible part of the USD 20 client cap; the operator sees it before enabling the schedule.

## Documentation updates
- `docs/product/attention-opportunities-and-scoring.md` (method, N, intervals), `docs/ai/capability-gateway.md` (measurement path), `docs/ai/model-harness-registry.md` (MeasurementTarget).

## Open decisions
- **Decision required (owner):** which AI engines to measure first, and the monthly money for it per tenant. Proposed default: two targets with official APIs that support web-grounded answers, chosen at task start; USD 2 per tenant per month.
- **Decision required:** N per cell and the interval method. Proposed default: N = 5 for the baseline, Wilson interval, "insufficient data" below 20 samples per metric.
- **Decision required:** traditional search rank tracking in R2. Proposed default: not in R2; R2-011 records only whether the tenant is found for its own name.
- **Decision required:** whether an API answer is a fair stand-in for what the consumer product shows. Proposed default: state this limit in every report.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: the method is written in the focused document so a client can be told how the numbers are computed.
