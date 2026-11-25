# R1-002 — Authorization Service

> **Spec revision:** 2 — 2026-11-10. Expanded from a one-paragraph summary to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). The revision 1 summary is kept verbatim under Goal. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## Goal
Implement deterministic AuthorizationGrant minting from explicit human command, delegation policy or approved proposal. Support outcome-bound/artifact-bound modes, scope/constraints/expiry/revocation and high-risk confirmation requirements.

## Why now
"LLMs may infer intent but cannot mint authority" is only true if something else mints it. This service is that something; the Action Broker (R1-003) will refuse to act without its output.

## Context / linked docs / ADRs
- Edge cases added 2026-11-14 that this task must cover: E-072 ([register](../../docs/PROJECT_REAUDIT_2026-08-10.md)).
- [Authority, authorization and Action Broker](../../docs/security/authority-and-action-broker.md)
- [Trust boundaries and prompt injection](../../docs/security/trust-boundaries-and-prompt-injection.md)
- [Delegation and break glass](../../docs/security/delegation-and-break-glass.md)
- [Concurrency and idempotency](../../docs/architecture/concurrency-idempotency.md)
- [Re-audit edge cases E-047, E-048](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- Contract: [authorization-grant.schema.json](../../contracts/schemas/authorization-grant.schema.json)
- ADR-0002, ADR-0003

## Depends on
- R1-001 (permission check, acting context).
- R0-006 (audit).

## Invariants
- an LLM output is never itself sufficient authorization for an external side effect;
- authority has exactly these sources: explicit command from an authorized human, a valid tenant delegation/automation policy, human approval of a proposal, or a deliberate visible UI control used by an authorized human;
- external or untrusted content can never grant, widen or approve anything;
- minting is deterministic code: same inputs, same decision;
- an explicit implementation request from an authorized user counts as approval within its scope; do not ask twice;
- high-risk and irreversible actions always need consequence-specific confirmation.

## In scope
- AuthorizationGrant entity: id, tenant/profile, actor, authority_source (EXPLICIT_HUMAN, DELEGATION_POLICY, APPROVED_PROPOSAL, VISIBLE_UI_ACTION), authorization_mode (OUTCOME_BOUND, ARTIFACT_BOUND), action_class, scope, constraints, artifact hash, target, risk (LOW, MEDIUM, HIGH, CRITICAL), expires_at, created_at, revoked_at.
- Minting paths, one per authority source, each recording the evidence it relied on (the human message or UI interaction reference, the policy revision, the approval record).
- Risk classification by action class from a versioned table.
- High-risk confirmation: a separate, consequence-specific confirmation record required before a HIGH/CRITICAL grant becomes usable.
- Validation interface for the Action Broker: is this grant valid now, for this action, target and artifact?
- Revocation and expiry.
- Proposal/approval record sufficient to back APPROVED_PROPOSAL.
- Delegation policy minimal form: tenant-defined rule allowing an action class within constraints.

## Out of scope
- Intent resolution from conversation (R2). This task accepts a structured intent and the reference to the human input behind it; it does not parse language.
- Executing actions (R1-003).
- Rich policy language or policy UI.
- Approval inbox UI.

## API / contract changes
- `mint(request) → grant | confirmation_required | denied(reason)`.
- `confirm(grant, confirmation)`; `validate(grant, action) → valid | invalid(reason)`; `revoke(grant)`.
- `authorization-grant.schema.json`: add `created_at`; define the structure of `scope`, `constraints` and `target` instead of open objects; add the confirmation reference. The focused document lists `created_at` but the schema omits it. Changes are reviewed.

## Data / migration
- Tables: AuthorizationGrant, confirmation record, proposal/approval record, delegation policy, risk classification table (platform-level, versioned). Tenant-scoped ones under RLS.
- Grants are immutable after minting except for `revoked_at`; a change of scope is a new grant.
- Reverse migrations tested.

## Security / privacy threat notes
- Prompt injection causing a model to claim approval was given: the service requires a reference to an authenticated human interaction, which the model cannot fabricate.
- Scope creep: an outcome-bound grant used for a broader action.
- Artifact swapped after approval (E-048): hash binding.
- Grant used after the actor lost permission (E-047): validation re-checks R1-001.
- Replay of a confirmation for a different grant.
- Managed operator minting outside their approval categories.

## Observability
- Audit: every mint attempt (granted, confirmation required, denied) with authority source and evidence reference; confirmation; revocation; every failed validation with reason.
- Metric: grants by source and risk; denials by reason.

## Acceptance criteria
- *(revision 1)* deterministic AuthorizationGrant minting from explicit human command, delegation policy or approved proposal;
- *(revision 1)* outcome-bound and artifact-bound modes;
- *(revision 1)* scope, constraints, expiry and revocation enforced;
- *(revision 1)* high-risk confirmation requirements enforced;
- *(derived)* visible UI action supported as an authority source with the interaction recorded;
- *(derived)* a mint request with no authenticated human or policy evidence is denied regardless of the text supplied;
- *(derived)* a material change to artifact, destination, schedule or audience invalidates an artifact-bound grant.

## Tests
- Unit: each minting path; risk classification; expiry boundaries.
- Authorization suite: unauthorised actor, wrong tenant, wrong capacity, expired, revoked, scope exceeded, artifact hash mismatch, target mismatch, missing confirmation, replayed confirmation.
- Injection tests: untrusted content containing approval-like text produces no grant.
- Determinism: repeated identical requests give identical decisions.
- RLS suite on new tables.

## Rollback / failure recovery
Fails closed: if the service cannot decide, no grant. Revocation is the recovery tool for a wrongly minted grant, together with an incident record. Reverse migrations tested.

## Cost/resource budget
Negligible compute. No model calls are made by this service.

## Documentation updates
- `docs/security/authority-and-action-broker.md` (concrete risk table, scope structure).
- Contract schema.
- Guide: "how a module requests authorization".

## Open decisions
- **Decision required:** the initial action-class catalogue and risk table.
- **Decided (ADR-0033):** low 90 days; medium 30 days; high single use within 24 hours; critical single use within 15 minutes after a fresh sign-in.
- **Decision required:** the structure of `scope` and `constraints`.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review recorded; zero unauthorised-grant findings in the authorization suite.
