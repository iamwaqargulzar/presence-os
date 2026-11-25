# ADR-0001 — Modular Monolith First
Status: Accepted

## Decision
Build the initial backend as a modular monolith with explicit module boundaries.

## Rationale
The product has broad scope but early microservices would increase operational/distributed complexity and autonomous-development cost.

## Consequences
Separate processes/services are still allowed for real security/resource boundaries (Edge, DB, workers, inference, secrets). Kafka/service mesh/microservice extraction require later justification.
