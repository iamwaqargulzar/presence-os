# R2-007 — Approval Inbox and Client Request Queue

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 is built; recheck against the R1 implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Give the operator one durable inbox for everything that waits for a decision. Give clients two things: a way to ask for a change, which only creates a queue item, and a way to approve or reject the exact draft shown to them.

## Why now
Scheduled tasks prepare and wait (owner decision). Client roles exist since R1 but have no screen. In R3 nothing can be published without this.

## Context / linked docs / ADRs
- [Operator and managed-service experience](../../docs/product/admin-and-managed-service.md)
- [Authority, authorization and Action Broker](../../docs/security/authority-and-action-broker.md)
- [Delegation and break glass](../../docs/security/delegation-and-break-glass.md)
- [Person, profile and tenant model](../../docs/product/person-profile-tenant-model.md)
- [Gates](../../docs/delivery/gates.md) (runtime gates)
- [Research: approval inbox](../../docs/research/OPEN_SOURCE_LANDSCAPE_OPERATOR_RUN_2026-11-14.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0002, ADR-0003, ADR-0030

## Depends on
- R2-006. Uses R1-002 (proposal and approval record, grants), R1-003 (actions), R1-008 (artifact hash), R1-001 (roles).

## Invariants
- an approval is a durable record, not a notification. Losing a notification loses nothing;
- an approval covers only the exact artifact, target and parameters shown (artifact-bound). A changed draft needs a new approval (E-072);
- nothing approves itself. An expired item is expired, never approved;
- a client request creates a queue item and nothing else: no run, no model call, no action (E-071);
- a client approval can satisfy a tenant's approval requirement; it never widens authority and never replaces the operator's own authority to act;
- an operator-attested approval is marked as such and must carry evidence.

## In scope
- ApprovalItem: tenant, kind (action, run start, plan, draft), what is to be approved (artifact reference and hash, target, parameters, schedule), who may decide, state (PENDING, APPROVED, REJECTED, EXPIRED, WITHDRAWN, SUPERSEDED), expiry, decision record.
- Operator inbox: all pending items across tenants, grouped by tenant, with a direct link per item. Approve, reject with a reason, or open the draft.
- Decision view: shows exactly what will happen, where, when, as whom, and the cost estimate. For high-risk classes it shows the consequence-specific confirmation.
- On approval the Authorization Service mints the grant from the approval record. The inbox mints nothing itself.
- Supersession: if the artifact changes while pending, the item becomes SUPERSEDED and a new one is created.
- Expiry: every item has an expiry. Proposed default: 7 days for drafts, 24 hours for anything time-bound, never beyond the scheduled time.
- Client request queue: ClientRequest with text, optional attachment (through file quarantine), state (NEW, ACCEPTED, DECLINED, DONE). The operator accepts it (and then starts a task under their own authority), declines it with a note, or answers.
- Client approval: where the tenant's policy requires it, a draft is shown to Client Approvers; they approve or reject with a comment.
- Tenant approval policy: per tenant, which content kinds need a client approval before publication. Stored and versioned here; enforced by R3-008.
- Operator-attested approval: for a client with no login, the operator records the client's approval with evidence attached (for example the client's email as a file). Marked `OPERATOR_ATTESTED` everywhere it is shown.
- Run-start approvals: a prepared run that needs the frontier profile or the subscription waits here (E-078).
- Bulk view, not bulk approve: the operator can step quickly through items; each is decided on its own. See open decisions.

## Out of scope
- Push and digest delivery (R2-008).
- Executing the approved action against a real platform (R3).
- Comment threads and collaborative editing of drafts.
- A client approving anything outside drafts shown to them (no spend, no deploy, no connection change by approval).

## API / contract changes
- Endpoints: list inbox; get item; approve; reject; client request create, list, accept, decline; client approve, reject; record attested approval.
- Internal: `request_approval(...) → item`, `on_decision` event through the outbox.
- New contract sketches: `approval-item.schema.json`, `client-request.schema.json`. `OperatorApproval` in the entity catalogue becomes the decision record of an ApprovalItem.

## Data / migration
- Tenant-scoped under RLS: ApprovalItem, ApprovalDecision, ClientRequest, TenantApprovalPolicy (versioned).
- Reverse migrations tested.

## Security / privacy threat notes
- Draft changed after approval (E-048, E-072): the grant binds to the hash; the broker checks it again at execution.
- A client approving for another tenant, or an item not addressed to their role: membership and role check on every decision.
- Client request text containing instructions for the AI: it is `UNVERIFIED_TENANT_DATA`, shown to the operator as text, and never enters a run until the operator accepts the request; even then it is data.
- Forged attested approval: only the operator can record one; evidence is required; it is prominently audited and visible to the client if they later get a login.
- Approval by a stolen session: step-up confirmation for high-risk classes.
- Approval fatigue leading to blind approval: digest and grouping (R2-008), clear diffs, no "approve all".

## Edge cases covered
- E-048 and E-072 content changed after approval.
- E-071 client request starts work.
- E-078 scheduled task needs the frontier profile and nobody is present: it waits here.
- E-079 approvals pile up: items expire; nothing auto-approves.
- E-047 authority revoked while an approved action is queued: the broker revalidates; the inbox shows the action as REVOKED.
- E-073 invitation revoked: pending items addressed to that client return to the operator.

## Observability
- Audit: item created, shown, decided, expired, superseded; every attested approval with its evidence reference.
- Metrics: pending count and age per tenant, expiry rate, time to decision, client approval turnaround.

## Acceptance criteria
- every item has a stable link that opens the exact item after sign-in;
- approving mints a grant bound to the shown hash, target and parameters, and nothing wider;
- editing a pending draft supersedes its item;
- an expired item cannot be approved;
- a client request produces a queue item and, verifiably, zero runs, model calls and actions;
- a client with the Approver role can decide only items addressed to their tenant's approvers;
- an attested approval without evidence is refused.

## Tests
- State machine of ApprovalItem and ClientRequest.
- Hash binding: change one byte after approval; execution is refused.
- Expiry at the boundary; approve after expiry refused.
- Zero-work proof for client requests: counters on the run, gateway and broker fakes stay at zero.
- Role matrix: viewer, requester, approver, operator, another tenant's approver.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE across tenants on all four tables; ID substitution on decide endpoints.
- Injection: hostile text in a client request does not reach a model before acceptance.
- Concurrency: two decisions on one item; one wins, one conflicts.

## Rollback / failure recovery
Decisions are append-only. A wrong approval is undone by revoking the grant or cancelling the action, both existing kernel operations. Reverse migrations tested.

## Cost/resource budget
No model calls. Attachments count against tenant storage.

## Documentation updates
- `docs/product/admin-and-managed-service.md`, `docs/security/authority-and-action-broker.md`, `docs/data/core-entity-catalog.md`, `docs/architecture/state-machines.md`.

## Open decisions
- **Decision required:** expiry periods. Proposed default above.
- **Decision required (owner):** whether the operator may approve several low-risk items with one tap. Proposed default: no; one decision per item.
- **Decision required:** default tenant approval policy. Proposed default: for a client tenant, every public post and every site change that alters visible text needs a client approval if the tenant has an Approver; for operator-owned tenants, none.
- **Decision required:** what evidence is accepted for an attested approval. Proposed default: an uploaded email, message screenshot or signed document; free text alone is refused.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review recorded; the zero-work test for client requests joins the protected authorization tests.
