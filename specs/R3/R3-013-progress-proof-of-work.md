# R3-013 — Progress Reporting and Proof of Work

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 and R2 are built; recheck against their implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Show the operator and each client what Presence did, with evidence, and what changed, with honest attribution. A report is built from records the system already holds; a model may word it, but may not add a claim.

## Why now
R3 is the first release used for real client work. A client must be able to see what was done for them. The operator needs a per-client record of work and cost.

## Context / linked docs / ADRs
- [Trust, truth and attribution](../../docs/product/trust-and-attribution.md)
- [Client onboarding and time-to-value](../../docs/product/onboarding-and-first-value.md) (what the client sees)
- [Conversation Shell and Agent Home](../../docs/product/conversation-and-home.md) (recent improvements, recent progress)
- [Tenant limits, budgets and usage](../../docs/commercial/plans-entitlements-billing.md) (cost report)
- [Audit ledger](../../docs/security/audit-ledger.md)
- [Attention, opportunities, presence health and AI visibility](../../docs/product/attention-opportunities-and-scoring.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0011, ADR-0018, ADR-0030

## Depends on
- R3-003 (deployments), R3-009 (posts). Uses R2-011, R2-012, R2-014 (measurements), R2-015, R1-004 (ledger), R0-006 (audit).

## Invariants
- every statement in a report links to a record: an Action, a publication, a deployment, a measurement or a fact change;
- impact is labelled as one of three: CAUSED BY (supported by a credible path or experiment), CORRELATED WITH (same period, cause not shown), OBSERVED (raw fact). The default is OBSERVED;
- prefer honest uncertainty over dramatic numbers; a score change across a formula change is marked as a method change;
- a client's report contains only that client's tenant;
- money figures are in USD from the ledger; the rupee figure is for reading only;
- report text is `GENERATED` content; it can be worded by a model, never extended by one.

## In scope
- ProofOfWork entry: one per completed unit of work (site change deployed, post published, correction verified, fact corrected, scan run), with what, when, who authorised it, evidence links (permalink, deployment record, before and after artifact), and cost.
- Entries are created by deterministic handlers on domain events through the outbox, not by a model.
- Before and after: for site changes, the two content versions and previews; for presence, the measurements taken before and after.
- Progress report for a period per tenant: work done; what waits for the client; presence measurements and their change with labels; opportunities opened and closed; what is planned next.
- Report assembly: structured data first; then a model writes short summary paragraphs from that data only; a faithfulness check rejects any number or claim not in the data.
- Attribution rules, deterministic: a change is CAUSED BY only where a direct path exists (for example "the phone number on listing X now matches because correction item Y was verified"); metric movements are CORRELATED WITH by default.
- Views: operator view per tenant with cost; client view without internal cost unless the operator turns it on.
- Delivery: in the console; monthly report notification with a link (R2-008); export as a PDF or HTML file artifact for clients without a login.
- Feeds for Agent Home: "recent improvements" and "recent progress".
- Operator cost report per tenant and global for a period, from the ledger alone: API spend by task class and provider, with subscriptions shown separately as fixed cost.
- Schedule: monthly report prepared as an unattended read-only task; sending it to a client waits for the operator's approval at the start. See open decisions.

## Out of scope
- Web analytics, conversions and revenue attribution (R4, needs analytics and CRM data).
- Invoices and billing (ADR-0030: none).
- Custom report builders and white-label branding.
- Benchmarks against other tenants.

## API / contract changes
- Internal: event handlers `on_action_succeeded`, `on_deployment_healthy`, `on_measurement`; `build_report(tenant, period)`.
- Endpoints: proof-of-work list, report list and detail, export, cost report.
- New contract sketches: `proof-of-work.schema.json`, `progress-report.schema.json`.

## Data / migration
- Tenant-scoped under RLS: ProofOfWork (append-only), ProgressReport (artifact reference, hash, data snapshot), ReportDelivery.
- Reverse migrations tested.

## Security / privacy threat notes
- A report that overstates results: faithfulness check, labels, and links for every figure.
- Cross-tenant leak in a report or export: built under the tenant's context only; export links are signed, short-lived and tied to the tenant.
- Internal cost, model names or other clients' names in a client view: field-level visibility; a test scans client views for operator-only fields.
- An exported file sent to the wrong person: export for a no-login client is an operator action with a recorded recipient.
- Sending a report by email is a platform notification through the broker (R2-008); the report body is not in the email.

## Edge cases covered
- E-072 a report shows the exact approved version that was published.
- E-058 the proof-of-work record is part of what a client export must include (noted for the export task that does not exist yet).
- E-008 costs in money from the ledger with price snapshots.
- E-086 if the operator is unavailable, a client's report history remains readable to them.
- E-010 the model profile used for each piece of work is in the operator view.

## Observability
- Audit: report built, approved for sending, delivered, exported.
- Metrics: reports sent on time, faithfulness-check rejections, client report open rate.

## Acceptance criteria
- every proof-of-work entry opens its evidence;
- a report contains no number that is not in its data snapshot;
- a metric change is labelled CORRELATED WITH unless a deterministic rule marks it CAUSED BY;
- a formula change inside the period is shown as a method change, not as a gain or loss;
- a client sees only their tenant and no operator-only field;
- the cost report for a period equals the ledger totals for that period.

## Tests
- Event-to-entry tests for each event type; idempotent on event replay.
- Faithfulness check on fixtures with seeded extra claims.
- Attribution rule table tests.
- Formula-change boundary in a period.
- Field-visibility scan for client views and exports.
- Cost report reconciliation against the ledger.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on the three tables across tenants; UPDATE and DELETE on ProofOfWork refused; export link of tenant A refused for tenant B.

## Rollback / failure recovery
Entries and reports are append-only; a wrong report is superseded by a corrected one that links to it. If wording fails, the structured report is delivered without summary text.

## Cost/resource budget
One wording call per report. Proposed default: frontier profile, because the report names the client and its plans; under USD 0.20 per report.

## Documentation updates
- `docs/product/trust-and-attribution.md` (attribution rules in practice), `docs/product/onboarding-and-first-value.md`, `docs/commercial/plans-entitlements-billing.md` (cost report fields).

## Open decisions
- **Decision required (owner):** are monthly reports sent to clients automatically, or after the operator reviews each one? Proposed default: operator reviews each report for the first three months per client, then may switch that client to automatic.
- **Decision required (owner):** do clients see cost? Proposed default: no.
- **Decision required:** report period and day. Proposed default: calendar month, prepared on the 2nd.
- **Decision required:** export format for clients without a login. Proposed default: a PDF rendered from the same HTML.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: the faithfulness and field-visibility tests are protected tests.
