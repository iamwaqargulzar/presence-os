# R3-008 — Publication Policy, Approval Execution and Takedown

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 and R2 are built; recheck against their implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
One rule set for when a piece of content may become public, on any channel. It joins the operator's authority, the tenant's client-approval policy and the Action Broker into one publication flow, and it gives a fast way to take published content back.

## Why now
R3 has several ways to publish (site deploy, social post, later others). If each one checks approval in its own way, one of them will be wrong. The runtime gate "publication waits for the client's artifact-bound approval" needs one owner.

## Context / linked docs / ADRs
- [Authority, authorization and Action Broker](../../docs/security/authority-and-action-broker.md)
- [Gates](../../docs/delivery/gates.md) (section 6, runtime)
- [Operator and managed-service experience](../../docs/product/admin-and-managed-service.md)
- [Communications, platform policy and jurisdiction](../../docs/compliance/communications-and-platform-policy.md)
- [Trust, truth and attribution](../../docs/product/trust-and-attribution.md)
- [Incident management](../../docs/operations/incident-management.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0002, ADR-0003, ADR-0018, ADR-0030

## Depends on
- R3-006 (approved content items). Uses R2-007 (approval items and tenant approval policy), R1-002, R1-003, R1-008.

## Invariants
- nothing becomes public except as an Action through the Action Broker with a valid grant;
- a publication is always artifact-bound: exact content hash, exact destination, exact time window and audience;
- where the tenant's policy requires client approval, the Action cannot be AUTHORIZED without a client approval (or an operator-attested one with evidence) for that exact hash;
- the client's approval satisfies the tenant's requirement. The operator's authority to act is still needed. Neither replaces the other;
- any material change after approval invalidates it;
- a publication requested by a schedule always waits for approval;
- a takedown is always possible for the operator and is never blocked by an approval requirement.

## In scope
- Publication request: content item version (or site content version), destination (a property environment, or a connection and account), time (now or scheduled), audience parameters.
- Policy evaluation, deterministic: given tenant policy revision, content kind, destination and requester, return which approvals are required.
- Flow: request → required approvals created in R2-007 → on completion the Authorization Service mints the artifact-bound grant → Action AUTHORIZED → QUEUED → broker executes through the channel's adapter.
- "Material change" definition: any change to the content hash, attached media, destination account, or scheduled time beyond a tolerance. Each invalidates approvals.
- Pre-publication checks added to the broker's policy step for the class `content.publish`: content item is APPROVED and unblocked by the claim check (R3-006); destination belongs to the tenant; platform policy flags from the connector's capability matrix; tenant state.
- Publication record: what was published, where, when, by which Action, under which approvals, with the external reference returned by the channel.
- Takedown: an Action of class `content.unpublish` that removes or hides the item on its channel (site: redeploy without it or roll back; social: delete where the platform allows). One control in the console. Records reason and who asked.
- Client takedown request: a Client Requester or Approver can ask for takedown; it is a queue item flagged URGENT.
- Correction flow: publish a corrected version as a new artifact with new approval, linked to the withdrawn one.
- Withdrawal before publication: operator or client approver can withdraw an approval while the Action is queued; the broker then moves it to REVOKED.
- Emergency hold: the operator can hold all queued publications for a tenant or for all tenants with one control.

## Out of scope
- Channel adapters themselves (R3-003 for sites, R3-009 to R3-011 for social).
- Legal assessment of content. The system escalates; it does not decide law.
- Multi-step client approval chains (several approvers in order).
- Moderation of third-party comments (R4).

## API / contract changes
- Action classes: `content.publish`, `content.unpublish`, with risk ratings in the R1-002 table.
- Internal: `request_publication(...)`, `required_approvals(...)`, `takedown(publication, reason)`, `hold(scope)`.
- Endpoints: request publication, publication list and detail, takedown, client takedown request, hold and release.
- New contract sketches: `publication.schema.json`, `tenant-approval-policy.schema.json` (refining the R2-007 record).

## Data / migration
- Tenant-scoped under RLS: Publication, PublicationHold, TakedownRecord. TenantApprovalPolicy comes from R2-007.
- Reverse migrations tested.

## Security / privacy threat notes
- A path that publishes without passing this flow: the broker refuses `content.publish` without a Publication record and matching approvals; a boundary test seeds a direct adapter call.
- Approval for version A used to publish version B (E-048, E-072): hash binding checked at grant time, at execution time and by the adapter.
- Destination swapped (the personal account instead of the business page, E-074): destination identity is part of the bound parameters and is shown in the approval view.
- Operator-attested approval abused: evidence required, flagged in every record, listed in the client's view.
- A takedown request used to silence content by someone without the right: only tenant roles of that tenant and the operator can request; every takedown is audited.
- Queued publication after service ends or the client disconnects (E-047): revalidation at execution.

## Edge cases covered
- E-047, E-048, E-072 on publication.
- E-074 wrong account.
- E-083 infringing or defamatory content: approval, provenance, fast takedown.
- E-092 scheduled publication has no shortcut.
- E-052 tenant paused: queued publications are cancelled per ADR-0033 point 14.
- E-079 approvals not given in time: the publication expires; nothing publishes late by itself.

## Observability
- Audit: publication requested, approvals satisfied, grant minted, executed, taken down, held.
- Metrics: time from draft to publication, approvals by type, expired publications, takedowns and time to takedown.

## Acceptance criteria
- with a client-approval policy on, a post cannot be published on the operator's authority alone;
- with the policy off, the operator's explicit "publish this" publishes without a second question;
- a one-character edit after approval stops the publication;
- a takedown from the console removes a published fixture item through the fake adapter within one minute and records the reason;
- the hold control stops every queued publication in scope and releases them only by the operator;
- a direct adapter call outside the broker fails the boundary gate.

## Tests
- Policy matrix: tenant policy × content kind × requester role × attested or not.
- Hash, destination and time-change invalidation.
- Withdrawal while queued → REVOKED, no adapter call.
- Takedown: success, platform refuses deletion (item marked "could not remove", attention item raised).
- Hold and release.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on the three tables across tenants; a client of tenant A cannot request takedown for tenant B.
- Boundary test for direct publishing.
- All with fake adapters.

## Rollback / failure recovery
Publications are records plus Actions; a wrong publication is handled by takedown and correction. Policy revisions are versioned and can be rolled back for new requests.

## Cost/resource budget
No model calls. Each publication is one Action with the broker's normal cost.

## Documentation updates
- `docs/security/authority-and-action-broker.md` (publication flow), `docs/delivery/gates.md` (runtime gate reference), a new runbook "content takedown".

## Open decisions
- **Decision required:** risk rating of `content.publish`. Proposed default: medium; high when the audience is paid or the destination has more than a set follower count.
- **Decision required:** tolerance for a schedule change before approval is invalidated. Proposed default: any change of more than 60 minutes, or any change of date.
- **Decision required (owner):** may the operator publish for a client tenant without client approval in an urgent case? Proposed default: only a takedown or a correction of a factual error; both are flagged to the client.
- **Decision required:** who is told about a takedown. Proposed default: the operator and all Approvers of the tenant.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review recorded; the policy matrix test joins the protected authorization tests.
