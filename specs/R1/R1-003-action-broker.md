# R1-003 — Action Broker

> **Spec revision:** 2 — 2026-11-10. Expanded from a one-paragraph summary to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). The revision 1 summary is kept verbatim under Goal. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## Goal
Implement action state machine, authorization revalidation, tenant limit/risk/target/artifact checks, idempotency and execution adapter interface. Include delayed-action revalidation and cancellation/revocation.

## Why now
The Action Broker is the only component allowed to cross the external side-effect boundary. No connector, publisher, sender or deployer may be written before it exists, or the boundary will be bypassed from day one.

## Context / linked docs / ADRs
- [Authority, authorization and Action Broker](../../docs/security/authority-and-action-broker.md)
- [State machines](../../docs/architecture/state-machines.md)
- [Concurrency, idempotency and consistency](../../docs/architecture/concurrency-idempotency.md)
- [Durable workflows and Temporal](../../docs/architecture/workflows-and-temporal.md)
- [Tenant lifecycle](../../docs/operations/tenant-lifecycle.md)
- [Re-audit edge cases E-002, E-047 to E-050](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- Contract: [action.schema.json](../../contracts/schemas/action.schema.json)
- ADR-0002, ADR-0003, ADR-0005

## Depends on
- R1-002 (grant validation), R0-005 (durable delayed execution), R0-006 (audit).
- The broker also checks tenant limits/budget (R1-004), connection health (R1-007) and artifacts (R1-008), which are later in the task order. *(Derived)* Define these as narrow check interfaces in this task with implementations that deny by default; each later task supplies the real implementation and removes its stub.

## Invariants
- the Action Broker is the sole external side-effect boundary; no module calls a provider directly;
- no execution without a currently valid AuthorizationGrant;
- delayed work is revalidated immediately before the side effect;
- every side-effect request carries an idempotency key; retries never duplicate posts, messages, spend, records, DNS changes, deployments or destructive operations;
- never claim exactly-once delivery to an external provider;
- suspension of a tenant blocks new external actions.

## In scope
- Action entity and state machine: DRAFT → PREPARED → AUTHORIZED → QUEUED → EXECUTING → SUCCEEDED, with FAILED, CANCELLED, REVOKED, EXPIRED.
- ActionAttempt records per execution try.
- Pre-execution check chain, in a defined order, each producing an audited decision: tenant/profile active; tenant limit/quota; actor/skill permission; valid grant; risk/confirmation; exact artifact and target; budget reservation; connection health; policy; idempotency.
- Delayed and scheduled actions as durable workflows that re-run the full check chain at execution time.
- Cancellation by an authorised human and revocation when the grant or connection is withdrawn or a limit is lowered.
- Execution adapter interface: prepare, execute(idempotency key), query outcome, compensate where supported.
- A fake/test adapter with controllable outcomes (success, failure, timeout-after-success, duplicate detection).
- Optimistic concurrency on Action via `base_version`.
- Outbox-based handoff from committed state to execution.

## Out of scope
- Real provider adapters (R3 onward).
- Webhook ingestion (edge case E-050 is recorded for R1/R4; only the idempotency-key convention is established here).
- Approval UI.
- Compensation/rollback of real external effects.

## API / contract changes
- Internal: create/prepare/authorize/queue/cancel action; adapter interface; the four check interfaces (tenant limit, budget, connection, artifact).
- `action.schema.json`: **the schema has no state for an uncertain outcome**, but edge case E-049 requires "provider/request idempotency + uncertain-outcome state" when a provider times out after a possibly successful side effect. This is a real conflict between the contract and the re-audit; resolve it through an ADR (add a state, or model it on ActionAttempt) and do not resolve it silently.
- Idempotency key derivation rule documented as a contract for adapters.

## Data / migration
- Tables: Action, ActionAttempt, outbox (if not delivered by R0-005). Tenant-scoped under RLS.
- State transitions are enforced in the service layer inside a transaction and recorded in audit.
- Reverse migrations tested.

## Security / privacy threat notes
- Bypass: a module performing a side effect without the broker. Mitigate with an import/egress boundary test similar to R0-007's.
- Stale authority: queued action executes after grant or connection was revoked or a limit was lowered (E-047, E-002).
- Approved content changed after approval (E-048).
- Duplicate execution on retry or worker restart.
- Timeout after success reported as failure and retried (E-049).
- Cross-tenant action: target or connection belonging to another tenant.
- Model-generated destination or parameters accepted without deterministic validation.

## Observability
- Audit: every state transition and every check decision with actor, authority source, grant ID, artifact hash, target, connection, result.
- Metrics: actions by state and class, check-chain denials by reason, attempt count, time in queue.
- Trace: one trace from request through workflow to adapter call.

## Acceptance criteria
- *(revision 1)* action state machine;
- *(revision 1)* authorization revalidation;
- *(revision 1)* tenant limit, risk, target and artifact checks;
- *(revision 1)* idempotency;
- *(revision 1)* execution adapter interface;
- *(revision 1)* delayed-action revalidation;
- *(revision 1)* cancellation and revocation;
- *(derived)* no code path reaches an adapter without passing the full check chain;
- *(derived)* a suspended tenant cannot start a new external action;
- *(derived)* timeout-after-success does not produce a duplicate side effect and is not reported as a clean failure.

## Tests
- State machine: all valid and invalid transitions.
- Check chain: one negative test per check (inactive tenant, limit exceeded, no permission, no/expired/revoked grant, missing confirmation, artifact hash mismatch, target mismatch, no budget, unhealthy connection, policy block).
- Delayed action: grant revoked while queued → REVOKED, no adapter call; grant expired → EXPIRED.
- Idempotency: worker killed mid-execution and restarted → exactly one adapter effect recorded by the fake.
- Uncertain outcome: fake adapter succeeds then times out.
- Concurrency: two edits with the same `base_version` → one conflict.
- Cross-tenant: action referencing another tenant's grant, artifact or connection denied.
- Boundary: seeded direct provider call outside the broker fails a gate.

## Rollback / failure recovery
Fails closed at every check. A stuck EXECUTING action is resolved by querying the adapter outcome, not by blind retry. Reverse migrations tested. Compensation is adapter-specific and out of scope beyond the interface.

## Cost/resource budget
Each action costs a constant number of checks plus one workflow. Budget reservation happens before execution and is settled or released afterwards (R1-004). Admission is subject to the Resource Governor once R1-009 exists.

## Documentation updates
- `docs/security/authority-and-action-broker.md`, `docs/architecture/state-machines.md` (uncertain-outcome resolution).
- Contract schema.
- Guide: "how to write an execution adapter".
- ADR for the uncertain-outcome decision.

## Open decisions
- **Decided (ADR-0033):** the state `OUTCOME_UNKNOWN`, now in `action.schema.json`; never retried automatically.
- **Decided (ADR-0033):** every check is repeated at execution time. The fixed order is written in this task's implementation.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review recorded; all default-deny stubs are tracked so R1-010 can confirm none remain.
