# Modular Monolith Boundaries

## Why

Presence OS has many eventual capabilities, but early microservices would increase development/operations cost, distributed-transaction complexity and autonomous-agent failure modes.

## Rule

Business modules live in one backend deployment where possible, but:
- expose explicit service/application interfaces;
- do not reach into another module's database tables ad hoc;
- publish domain events through an internal outbox where needed;
- keep schemas/migrations owned by modules;
- keep external effects behind Action Broker;
- keep privileged secrets access behind Secrets Broker.

## Processes that may be separate early

Separate processes/VMs are justified for:
- Edge Gateway;
- database/object storage;
- Temporal workers;
- browser/gVisor workers;
- public tenant runtime if needed;
- inference GPU server;
- secrets manager.

This is separation by operational/security boundary, not microservices fashion.
