# ADR-0002 — Action Broker Is the Side-Effect Boundary
Status: Accepted

## Decision
All material external side effects pass through a privileged Action Broker.

## Consequences
Agents/skills cannot directly publish/send/spend/deploy/delete. Authorization, entitlements, risk, artifact/target, budget, idempotency and connection health are checked centrally.
