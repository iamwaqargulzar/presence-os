# Durable Workflows and Temporal

## Principle

Agents do bounded work. Temporal (or the durable workflow layer) owns long waits, retries, schedules and recoverability.

Use workflows for:
- approvals/waits;
- scheduled publication;
- domain verification;
- multi-stage research;
- onboarding;
- campaigns;
- long-running connection repair;
- deployment;
- offboarding;
- human-in-the-loop tasks.

## Workflow design

- Activity/tool calls must be idempotent.
- Checkpoint meaningful expensive stages.
- Retry from the failed stage, not from the beginning.
- Store large model/tool/research/media payloads in object storage/Postgres; workflow history carries artifact references.
- Use deterministic workflow code.
- Give long-lived workflows explicit versioning/upgrade policy.
- Support cancellation/revocation.
- Revalidate authorization and entitlements before delayed side effects.

## Worker upgrades

Use safe versioned deployments and rollback. Temporal Worker Versioning is treated as a capability to exploit, not a reason to deploy Kubernetes early.

## Eventing

Start with transaction outbox + internal event handling where needed. Do not introduce Kafka until event volume/independent consumers justify it.
