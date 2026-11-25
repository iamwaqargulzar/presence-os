# Authority, Authorization and Action Broker


> **Presence OS engineering source of truth**
>
> Baseline date: **2026-08-08** (Asia/Karachi project context).
> Product architecture is intentionally model-, provider-, harness-, and ingress-neutral.
> Vendor capabilities, model names, prices, quotas, laws, and platform policies are time-sensitive reference facts and MUST be revalidated before implementation or purchase.
> When a focused document conflicts with an older discussion, the focused document plus the Decision Register and ADRs control.


This is one of the highest-priority architectural documents.

## Core rule

**LLMs may infer intent but cannot mint authority.**

Authority comes from:
1. explicit command from an authorized human;
2. valid prior tenant automation/delegation policy;
3. human approval of an agent proposal.

The Authorization Service converts those real sources into a machine-enforced `AuthorizationGrant`.

## Intent modes

- DISCUSS / QUESTION
- RESEARCH / PLAN
- PREPARE / PREVIEW
- IMPLEMENT / PUBLISH / SCHEDULE / SEND / DEPLOY etc.

An explicit implementation request from an authorized user counts as approval for that scoped action. Do not ask for duplicate approval.

If implementation intent is materially ambiguous, ask one natural clarification.

## High-risk confirmation

Even direct requests require consequence-specific confirmation for high-risk/irreversible actions such as:
- destructive deletes;
- major bulk sends;
- large spend;
- DNS/domain transfer;
- security/access changes;
- production destruction;
- legal/financial commitments.

## Authorization modes

### Outcome-bound
Example: “Create and publish an announcement about X.”
Allows a bounded outcome within constraints.

### Artifact-bound
Example: “Publish post v82 to LinkedIn company account tomorrow at 9.”
Grant binds to:
- artifact hash;
- destination/account;
- schedule/audience;
- material parameters.

Material changes invalidate grant.

## AuthorizationGrant

At minimum:
- id
- tenant/profile
- actor
- authority_source
- action_class
- scope
- constraints
- artifact hash if applicable
- target
- expiry
- risk
- created_at
- revoked_at

## Action Broker

Only privileged service crossing the external side-effect boundary.

Action state machine:
DRAFT → PREPARED → AUTHORIZED → QUEUED → EXECUTING → SUCCEEDED

Additional terminal/interruption states:
FAILED / CANCELLED / REVOKED / EXPIRED

Before execution check:
- tenant/profile active;
- entitlement/quota;
- actor/skill permissions;
- valid AuthorizationGrant;
- risk/confirmation;
- exact artifact/target;
- budget reservation;
- credential/connection health;
- policy;
- idempotency.

For delayed work, revalidate immediately before side effect.

## Visible UI controls

A deliberate `Publish`, `Deploy`, `Send`, etc. button from an authorized user may itself be the authority source. Record the interaction and scope.
