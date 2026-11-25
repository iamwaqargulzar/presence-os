# R3-003 — Deploy, Health Check and Rollback

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 and R2 are built; recheck against their implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Put a verified release live for a property environment through the Action Broker, confirm it is healthy, and roll back to the previous release in one step when it is not, or when the operator asks.

## Why now
A deploy is the first real external side effect of the product. It must use the same authority, idempotency and audit path as every later one.

## Context / linked docs / ADRs
- [Digital properties and multi-property hosting](../../docs/product/digital-properties-and-hosting.md) (deployment lifecycle)
- [Authority, authorization and Action Broker](../../docs/security/authority-and-action-broker.md)
- [Concurrency, idempotency and consistency](../../docs/architecture/concurrency-idempotency.md)
- [Durable workflows and Temporal](../../docs/architecture/workflows-and-temporal.md)
- [Runbook: production deploy](../../docs/runbooks/production-deploy.md) (the platform's own deploys; tenant deploys follow the same discipline)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0002, ADR-0003, ADR-0005, ADR-0021

## Depends on
- R3-001, R3-002. Uses R1-003 (broker), R1-002 (grants), R1-011 (Deployment), R2-007 (approvals).

## Invariants
- a production deploy is an Action of class `property.deploy`. It needs a valid grant bound to the artifact hash and the target environment;
- a deploy always waits for approval when it comes from a schedule (owner decision); a direct "deploy this" from the operator is its own authority within scope;
- the deploy adapter is idempotent on (environment, artifact hash, action ID);
- every production deployment records its rollback target;
- a rollback is also an Action, with its own grant; it is pre-authorised for the operator as a low-friction control but still audited;
- only one deploy or rollback runs per environment at a time;
- an AI-written change never reaches production without passing a preview.

## In scope
- Deploy execution adapter for the Action Broker: prepare (check artifact is VERIFIED and present), execute (switch the environment's active deployment), query outcome, compensate (switch back).
- Deploy workflow: AUTHORIZED → DEPLOYING → health check → HEALTHY, or DEPLOY_FAILED, or UNHEALTHY → automatic rollback → ROLLED_BACK.
- Health check per runtime profile: for `static`, the canonical hostname returns the expected marker file and key pages return success.
- Per-environment deploy lock (lease with expiry).
- Promotion: preview → production uses the same artifact hash that was previewed and approved. A rebuild creates a new hash and needs a new approval.
- Rollback: one-step return to the recorded previous HEALTHY deployment; available from the console.
- Deployment history per environment with actor, authority source, hashes and health result.
- Scheduled go-live: "deploy at 09:00 tomorrow" is a delayed Action, revalidated at execution time.
- Client approval where the tenant policy requires it (enforced through R3-008).
- Post-deploy tasks: cache purge for the property's hosts, sitemap ping where applicable, change note for the progress report.
- Model for later runtimes, defined now and tested with a fake stateful profile: a migration lane (one schema-changing deploy per data boundary at a time), and worker or job revisions tied to the deployment revision so a rollback stops old jobs.

## Out of scope
- Real server-side runtimes with databases, workers or WebSockets. Their deploy rules are specified here; their implementation waits for a qualified profile.
- Canary and percentage rollouts.
- Deploys of the Presence platform itself (the production-deploy runbook).
- Property transfer between tenants (E-017).

## API / contract changes
- Action classes: `property.deploy`, `property.rollback`, with risk ratings recorded in the R1-002 table.
- Endpoints: request deploy (now or at a time), deployment history, rollback.
- Adapter contract documented against the R1-003 adapter interface.
- Deployment sketch: `rollback_target`, `health_result`, `approved_artifact_hash`.

## Data / migration
- Uses R1-011 Deployment. Adds DeployLock and DeploymentHealth (tenant-scoped, RLS).
- Reverse migrations tested.

## Security / privacy threat notes
- Artifact swapped between approval and deploy (E-048): hash bound in the grant and rechecked by the broker and by the adapter.
- Deploy to another tenant's environment: target validated against the acting tenant at grant time and execution time.
- A model-initiated deploy: impossible without a grant minted from a human interaction or approval record.
- Timeout after the switch happened (E-049): outcome queried from the registry state, never retried blindly; state `OUTCOME_UNKNOWN` until resolved.
- Stale grant used after the tenant was paused or the operator's access ended (E-047): revalidation at execution.
- Rollback to an artifact with a known vulnerability: the rollback view shows the artifact's last scan result.

## Edge cases covered
- E-018 schema migration while another deploy runs: lock and migration lane.
- E-019 background jobs survive a rollback: jobs are owned by the deployment revision.
- E-020 long-lived connections during deploy: recorded as a requirement for any future server profile; not applicable to `static`.
- E-047, E-048, E-049 on the deploy action.
- E-091 the system was down at a scheduled go-live: held for the operator inside a lateness window; never deployed late without a decision.
- E-092 a scheduled deploy has no shortcut.
- E-052 tenant paused during a deploy: a running switch finishes; queued ones are cancelled.

## Observability
- Audit: every deploy and rollback with actor, authority source, grant, artifact hash, environment, result.
- Metrics: deploy duration, failure and automatic-rollback rate, time to rollback.
- Trace from approval to the edge switch.

## Acceptance criteria
- a VERIFIED artifact goes live only with a grant bound to its hash and environment;
- the hash that was previewed and approved is the hash that goes live;
- an unhealthy deploy rolls back automatically and the site keeps serving the previous release;
- the operator can roll back from a phone in one confirmed step;
- two deploy requests for one environment never run together;
- a worker killed in the middle of a deploy leaves the environment on exactly one release, old or new, and the record says which;
- a scheduled deploy whose approval was withdrawn does not run.

## Tests
- Broker check chain for `property.deploy`: one negative test per check.
- Hash mismatch; other-tenant environment; expired, revoked and missing grant.
- Health failure → automatic rollback.
- Kill and restart at each workflow step; exactly-one-release assertion.
- Timeout-after-switch → `OUTCOME_UNKNOWN` → resolved by query.
- Lock contention.
- Fake stateful profile: migration lane serialisation; job revision reconciliation on rollback.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on DeployLock and DeploymentHealth across tenants; deploy history of tenant A not visible to tenant B.
- Client roles cannot request a deploy.

## Rollback / failure recovery
This task is the rollback mechanism. The switch is atomic at the registry. If the registry is unreachable, the edge keeps serving the last known mapping.

## Cost/resource budget
A deploy of a static site is a constant-time switch plus health requests. Proposed default: keep the last 10 artifacts per environment for rollback.

## Documentation updates
- `docs/product/digital-properties-and-hosting.md`, `docs/architecture/state-machines.md` (Deployment), a new runbook "tenant site rollback".

## Open decisions
- **Decision required:** risk rating of `property.deploy`. Proposed default: medium for a site with no custom domain, high for a production site on a client's own domain.
- **Decision required:** how many artifacts to keep for rollback. Proposed default: 10 per environment.
- **Decision required:** lateness window for a scheduled go-live. Proposed default: 30 minutes; after that it is held for the operator.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review recorded; a rollback drill on staging is recorded.
