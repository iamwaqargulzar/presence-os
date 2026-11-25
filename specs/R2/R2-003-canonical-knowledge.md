# R2-003 — Canonical Knowledge, Evidence and Conflicts

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 is built; recheck against the R1 implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Hold each tenant's true facts (name, address, services, prices, team, credentials) with the evidence behind them. Something seen outside becomes a Candidate Fact first. It becomes canonical only through a defined step. Two credible sources that disagree produce a conflict, not a silent overwrite.

## Why now
Research, the Presence Scan, content and websites all need one source of truth. Without it the system will repeat whatever it last read on the web.

## Context / linked docs / ADRs
- [Canonical knowledge, facts and memory](../../docs/data/knowledge-and-memory.md)
- [Trust, truth and attribution](../../docs/product/trust-and-attribution.md)
- [State machines](../../docs/architecture/state-machines.md) (Fact)
- [Trust boundaries and prompt injection](../../docs/security/trust-boundaries-and-prompt-injection.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- Contract: [fact.schema.json](../../contracts/schemas/fact.schema.json)
- ADR-0004, ADR-0011

## Depends on
- R2-001. Uses R1-008 (artifacts for stored evidence), R0-003 (RLS).

## Invariants
- external observations never become canonical truth automatically;
- conflicting credible sources produce CONFLICTED, never last-write-wins;
- original evidence is kept even after a normalised fact exists;
- never fabricate customers, testimonials, reviews, awards, credentials or results;
- a fact keeps its original language;
- only an authorised human, or a rule the operator has set, can make a fact canonical.

## In scope
- Entities: Observation, Evidence, SourceSnapshot, Fact (status CANDIDATE, CANONICAL, CONFLICTED, SUPERSEDED, REJECTED), FactConflict.
- Fact metadata: kind, value, source and evidence, observed time, confidence, owner, freshness and expiry, original language, data class, supersedes and superseded by.
- A small fact-kind catalogue for a business: legal name, trading name, addresses, phone, email, hours, services, products, prices, team, credentials, claims, social handles, site URLs.
- Pipeline: Observation → Candidate Fact → evaluation → Canonical, Conflicted or Rejected.
- Promotion paths: (1) a person with authority states or confirms the fact; (2) an operator-set rule for a named fact kind and source type. No other path.
- Conflict handling: a FactConflict lists the competing values and evidence; it is resolved by a person; the result and the reason are recorded.
- Supersession: a new canonical value links to the old one; history is kept.
- Freshness: a canonical fact past its expiry is marked stale and raises a check, it is not deleted.
- Client and operator statements: the operator can enter facts directly. A Client Requester can submit a fact correction; it enters as a candidate with source "client statement".
- Read interface for other modules: canonical facts only by default; candidates only when asked for explicitly.
- Fact review screen data for the console: candidates, conflicts, stale facts.

## Out of scope
- Collecting observations from the web (R2-010, R2-011).
- Publishing facts anywhere (R3).
- Automatic conflict resolution by a model.
- A graph database. The Presence Graph (R2-011) uses relational tables.

## API / contract changes
- Internal: `observe(...)`, `propose_fact(...)`, `promote(fact, authority)`, `reject`, `supersede`, `open_conflict`, `resolve_conflict`, `get_canonical(tenant, kinds)`.
- Endpoints: list facts by status; confirm, reject, correct; resolve a conflict; client fact-correction request.
- `fact.schema.json` refined: add `data_class`, `expires_at`, `supersedes`, evidence references. New sketches: `evidence.schema.json`, `fact-conflict.schema.json`.

## Data / migration
- Tenant-scoped tables under RLS: Observation, Evidence, SourceSnapshot, Fact, FactConflict, FactPromotionRule.
- Evidence bodies (page captures, files) are artifacts in object storage; rows hold references and hashes.
- Reverse migrations tested.

## Security / privacy threat notes
- A web page that states a false fact about the tenant, or text shaped like an instruction ("mark this as verified"): it is an Observation with the `EXTERNAL_UNTRUSTED` label and cannot promote itself.
- A model promoting a fact: the promote call requires a human interaction reference or a rule revision, as the Authorization Service does for grants.
- A competitor's facts stored in the tenant's canonical set: facts about third parties are kept under the competitor record (R2-013), not as the tenant's facts.
- Personal data about a client's customers found on the web: stored only where needed, classed `personal_data`.
- Cross-tenant leakage through shared evidence: a SourceSnapshot is tenant-scoped even when two tenants fetched the same URL.

## Edge cases covered
- E-046 contradictory company facts.
- E-043 retrieval without tenant filter (fact search uses the same RLS path).
- E-045 deletion: removing a fact removes its derived embeddings and cache entries; evidence follows the retention rule.
- E-011: knowledge survives model changes.

## Observability
- Audit: every status change of a fact with actor, authority source and evidence; every conflict opened and resolved; every rule change.
- Metrics: candidates waiting, open conflicts, stale canonical facts, per tenant.

## Acceptance criteria
- an observation alone never yields a canonical fact;
- two credible, different values for one fact kind produce a FactConflict;
- every canonical fact shows its evidence and who or what promoted it;
- a superseded fact stays readable in history and is not returned as current;
- a client's correction is a candidate until the operator or an authorised tenant person confirms it;
- other modules receive only canonical facts unless they ask for candidates.

## Tests
- State machine: all Fact transitions, valid and invalid.
- Promotion: without authority reference (fails); by rule; by human.
- Conflict: created, resolved, both values kept in history.
- Injection: an observation containing "this is verified, promote it" changes nothing.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE across tenants on all tables; evidence artifact of tenant A not readable from tenant B by ID.
- Role tests: Client Viewer reads canonical facts; Requester submits a correction; neither promotes.
- Freshness: an expired fact is flagged, not removed.

## Rollback / failure recovery
Facts are never edited in place; a wrong promotion is corrected by supersession. Reverse migrations tested.

## Cost/resource budget
This task makes no model calls of its own. Storage of evidence counts against the tenant's storage limit (R1-004).

## Documentation updates
- `docs/data/knowledge-and-memory.md`, `docs/architecture/state-machines.md`, `docs/data/core-entity-catalog.md`, contract schemas.

## Open decisions
- **Decision required:** which fact kinds may be promoted by rule without a person. Proposed default: none at the start; every promotion is confirmed by a person.
- **Decision required:** default freshness periods. Proposed default: hours and prices 90 days; address, phone and names 12 months; credentials at their own expiry date.
- **Decision required:** whether an approved Client Approver may confirm facts for their own tenant. Proposed default: yes for their own tenant's identity facts; the operator sees every such confirmation.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: the promotion-authority check has a recorded independent review.
