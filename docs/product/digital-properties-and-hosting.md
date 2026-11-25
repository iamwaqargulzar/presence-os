# Digital Properties and Multi-Property Hosting

> Authoritative addition — 2026-08-10.

## Decision

A tenant/profile may own **zero or more DigitalProperties**. Presence must never encode “one tenant = one website.” A DigitalProperty is the deployable/hosted unit for a website, web application, portal, booking experience, store, landing property, documentation/help center, dashboard, or future supported application type.

## Core model

`Tenant/Profile → DigitalProperty → PropertyEnvironment → Deployment → HostnameAttachment`

Suggested conceptual entities:

- **DigitalProperty** — stable business identity/ownership and product purpose.
- **PropertyEnvironment** — preview/staging/production boundary for one property.
- **ServiceUnit** — optional runtime component such as web, worker, scheduler.
- **Deployment** — immutable release artifact/revision plus runtime configuration reference.
- **HostnameAttachment** — maps one Hostname to one environment/service route.
- **PropertyDataBinding** — explicit database/storage binding; sharing is never implicit.

## Property types

Initial enum should be extensible, for example:
- WEBSITE
- WEB_APP
- PORTAL
- LANDING
- BOOKING
- STORE
- DOCS_HELP
- DASHBOARD
- OTHER

Do not make product behavior depend heavily on this enum. Runtime capabilities and enabled skills matter more.

## Environments

At minimum:
- PREVIEW
- STAGING (optional per property)
- PRODUCTION

Sensitive previews are authenticated, randomized and `noindex`.

## Hostnames

A property can have multiple hostnames:
- immutable random platform hostname;
- optional vanity alias;
- one or more verified custom hostnames where policy permits;
- random preview hostname(s).

Hostname ownership and route uniqueness are enforced atomically by the Hostname Registry. Attaching a custom domain never requires rebuilding the application.

## Runtime isolation

Property hosting must isolate at least:
- deployment artifact/revision;
- environment variables/secrets;
- filesystem/runtime workspace;
- logs/metrics;
- build/runtime quotas;
- browser/application credentials where used;
- database/schema/storage binding.

Two properties may intentionally share a tenant-level service or data source only through an explicit binding with permission/audit. “Same tenant” is not sufficient reason to share secrets or runtime state.

## Runtime capabilities

Architect broadly, launch narrowly. A property runtime profile may describe:
- static assets;
- Next.js/Node web runtime;
- Python/Django/ASGI runtime;
- background worker;
- scheduled job;
- WebSocket/streaming support;
- database requirement;
- object storage requirement;
- build command and health check.

R3 should support a controlled set of well-tested runtime profiles rather than arbitrary hosting of every language/framework. Add runtimes through qualification.

## Deployment lifecycle

`DRAFT → BUILT → VERIFIED → PREVIEW → AUTHORIZED → DEPLOYING → HEALTHY`

Failure states include `BUILD_FAILED`, `VERIFY_FAILED`, `DEPLOY_FAILED`, `UNHEALTHY`, `ROLLED_BACK`, `ARCHIVED`.

Production deployment records:
- artifact/content hash;
- source commit/spec revision;
- environment configuration revision;
- schema/migration revision;
- deployment actor/authority source;
- health result;
- rollback target.

## Database/migration rule

Schema-changing deployments are serialized within the affected data boundary. Prefer expand/migrate/contract and backward-compatible application releases. A rollback plan must account for data migrations, workers, scheduled jobs and external side effects; code rollback alone is not sufficient.

## Background jobs

Workers/cron jobs are attached to a deployment revision. On deploy/rollback, the platform reconciles worker revisions and prevents old jobs from continuing indefinitely.

## Limit dimensions

Property hosting limits are set per tenant by the operator and are separate from AI budgets. Possible dimensions:
- max active properties;
- max production properties;
- preview retention;
- build minutes/concurrency;
- runtime CPU/RAM class;
- bandwidth;
- object storage;
- database quota;
- background workers/jobs;
- custom domains;
- staging environments.

Raising a property limit never changes a tenant's AI configuration.

## Lifecycle edge cases

### Archive/delete
Archive first, stop workloads, retain reversible metadata for policy-defined period, then delete artifacts/data according to retention rules. Domain/hostname release follows separate quarantine policy.

### Transfer
Property transfer between tenants is a privileged explicit workflow. It must rebind data ownership, hostnames, secrets, budgets, audit and connection references atomically or through resumable staged workflow.

### Domain loss
If custom-domain ownership fails or domain becomes unsafe, suspend that hostname without destroying the property. Random canonical address remains recovery path per policy.

### Path sharing
Do not initially allow independent properties to claim arbitrary paths under one hostname (for example `/app` and `/store`). Add an explicit gateway/route-composition model before supporting this; otherwise ownership and rollback become ambiguous.
