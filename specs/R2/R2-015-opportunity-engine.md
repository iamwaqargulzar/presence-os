# R2-015 — Opportunity Engine

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 is built; recheck against the R1 implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Answer two questions for each tenant: where is it underrepresented, incorrect, stale or invisible, and what is the most valuable next action. Produce ranked Opportunities with evidence, and draft the first 30-day plan for a new tenant.

## Why now
Scan, scores, competitors and AI visibility produce findings. Without ranking, the operator gets a long list and no direction. The onboarding flow ends with a prioritised plan.

## Context / linked docs / ADRs
- [Attention, opportunities, presence health and AI visibility](../../docs/product/attention-opportunities-and-scoring.md)
- [Client onboarding and time-to-value](../../docs/product/onboarding-and-first-value.md)
- [Trust, truth and attribution](../../docs/product/trust-and-attribution.md)
- [Authority, authorization and Action Broker](../../docs/security/authority-and-action-broker.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- Contract: [opportunity.schema.json](../../contracts/schemas/opportunity.schema.json)
- ADR-0003, ADR-0011

## Depends on
- R2-012, R2-013, R2-014. Uses R2-001, R2-003, R2-004.

## Invariants
- an Opportunity is a proposal. It is never authority and starts nothing by itself;
- every Opportunity cites evidence (a gap, measurement, comparison or sample);
- the ranking formula is versioned, like score formulas;
- candidate generation is rules first; a model may word and combine, but may not invent a finding with no evidence ID;
- expected benefit is stated as an estimate with its basis, never as a promise;
- accepting an Opportunity creates a task request under the accepting person's authority, through the normal path.

## In scope
- Opportunity entity per the schema: title, evidence IDs, impact, confidence, effort, estimated cost, expected benefit, relevant skills, tenant goal, freshness, status (NEW, REVIEWED, ACCEPTED, IN_PROGRESS, DONE, DISMISSED, STALE).
- Goal entity: the tenant's stated goals, entered by the operator or confirmed from the client; used for relevance.
- Rule catalogue (versioned): each rule maps a finding type to an opportunity template, for example "phone number differs on a listing" → "correct the listing".
- Generation pipeline: collect findings since the last run; apply rules; merge duplicates; a model call writes the plain-language title and benefit text using only the cited evidence; validate that every evidence ID exists in the tenant.
- Scoring: `priority = f(impact, confidence, effort, cost, goal relevance, freshness)`, deterministic, versioned.
- Feasibility mark: whether the skills needed exist in the current release. In R2 most actions are "available in R3"; this is shown, not hidden.
- Lifecycle: review, accept, dismiss with a reason; a dismissed opportunity is not proposed again while its evidence is unchanged; an opportunity whose evidence is gone becomes STALE.
- First 30-day plan: an artifact that orders the top opportunities into weeks with effort and cost estimates. It is a draft for the operator, and can be shown to the client.
- Console list for the Agent Home "opportunities" area.

## Out of scope
- Doing the work (R3).
- Inputs that do not exist yet: analytics, CRM, sales, support, calls (R4). The input interface is open for them.
- Learned ranking from outcomes.
- Automatic acceptance.

## API / contract changes
- Internal: `generate(tenant)`, `rank(tenant)`, `accept(opportunity, actor) → task request`, `dismiss`.
- Endpoints: list, get with evidence, accept, dismiss; goals create and edit; plan get.
- `opportunity.schema.json` refined: add `rule_id`, `ranking_version`, `feasibility`, `dismiss_reason`, `freshness`. New sketch: `goal.schema.json`.

## Data / migration
- Platform tables: OpportunityRule (versioned), RankingVersion.
- Tenant-scoped under RLS: Opportunity, Goal, PlanDraft.
- Reverse migrations tested.

## Security / privacy threat notes
- A model inventing an opportunity from injected page text ("your site is hacked, install this plugin"): generation is rule-driven from typed findings; free text from pages never becomes a template input except as quoted evidence.
- Opportunity mistaken for approval: accept only records intent and creates a task request; the Authority Resolver and Action Broker still decide.
- Opportunities that would mean fabricating reviews, testimonials or credentials: the rule catalogue has no such template and a deny check rejects generated text proposing them.
- Client sees an internal cost estimate: per-field visibility by role.

## Edge cases covered
- E-046 an opportunity built on a conflicted fact is marked low confidence and asks for the conflict to be settled first.
- E-060 a rule or ranking change is a platform change with preview; it creates no tenant side effect.
- E-071 a client accepting an opportunity creates a client request, not a task.
- E-009 generation stops cleanly on budget exhaustion.

## Observability
- Audit: generated, accepted, dismissed, with rule and ranking versions.
- Metrics: opportunities per tenant by status, acceptance rate by rule, duplicates merged, stale rate.

## Acceptance criteria
- every Opportunity has at least one evidence ID that resolves inside the tenant;
- the same findings and versions give the same ranking;
- a dismissed opportunity does not return while its evidence is unchanged;
- accepting creates a task request and no run, grant or action by itself;
- a Client Requester's "I want this" creates a ClientRequest;
- a new fixture tenant gets a 30-day plan draft at the end of onboarding;
- no generated text proposes fabricated proof.

## Tests
- Rule tests: each finding type → expected template.
- Ranking determinism and ordering properties (higher impact with equal other inputs ranks higher).
- Evidence validation: unknown or other-tenant evidence ID rejected.
- Dedupe and re-proposal rules.
- Injection: hostile text in evidence does not create or alter an opportunity type.
- Fabrication deny-list test on generated text.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on Opportunity, Goal, PlanDraft across tenants.
- Role tests: client roles see permitted fields only; accept by client becomes a request.

## Rollback / failure recovery
Rule and ranking versions can be rolled back. If the wording model is unavailable, opportunities are shown with their template text. Reverse migrations tested.

## Cost/resource budget
One wording call per new opportunity batch, on the low-cost profile when all evidence is `public`, otherwise frontier. Proposed default: at most 20 open opportunities per tenant; lower-ranked ones are held back.

## Documentation updates
- `docs/product/attention-opportunities-and-scoring.md` (rules, ranking version 1), `docs/product/onboarding-and-first-value.md`, contract schema.

## Open decisions
- **Decision required:** ranking formula version 1. Proposed default: `impact × confidence × goal relevance ÷ (effort + cost weight)`, with freshness as a decay.
- **Decision required:** who enters goals. Proposed default: the operator; a client can propose a goal as a request.
- **Decision required:** whether the plan is shown to clients automatically. Proposed default: only after the operator marks it as shared.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: rule catalogue version 1 is listed in the focused document.
