# Concurrency, Idempotency and Consistency

## Optimistic concurrency

Mutable business resources should expose `version` / `base_version`.

A stale agent edit must return a conflict rather than overwrite another human/agent change.

## Idempotency

Every external side-effect request must carry an idempotency key derived from the action identity/attempt policy.

Retries must not duplicate:
- posts;
- emails/messages;
- payments/spend;
- CRM records;
- DNS changes;
- deployments;
- destructive operations.

## Artifact integrity

Artifact-bound approvals store a hash. Material edits invalidate the approval.

## Outbox

When a database change must reliably trigger async work:
- commit state + outbox event atomically;
- workers consume with idempotency;
- mark delivery separately.

Avoid distributed transactions.
