# ADR-0033 — Technical Defaults for R0 and R1
Status: Accepted (2026-11-15). The owner delegated technical choices to the development process and answered one point directly: the model gateway is built in-house.

## Context
The task contracts for R0 and R1 carried about sixty lines marked "Decision required". Most are not architecturally important. The project principle is to choose a conservative, stable default and record it rather than delay. This ADR records those defaults in one place. Each one can be changed later by a new ADR or, where noted, by configuration.

Product names and versions here were chosen from knowledge on 2026-11-15 without a fresh check of each project. Every named dependency still passes the dependency review (license, security, maintenance, duplication) in the task that first adds it. If a review fails, the task records the replacement.

## Decisions

### 1. Model gateway (owner decision)
- The model gateway is built in-house: a small module with one adapter per provider. No gateway library (for example LiteLLM) is used.
- Each adapter may use the provider's official client library.
- Provider policy, budget reservation, cost ledger and tenant separation live in the gateway's own code, not in an adapter.
- First adapters: Anthropic for the frontier profile, then DeepSeek for the low-cost profile. The gateway interface stays provider-neutral; a third adapter must need no change outside its own file and configuration.

### 2. Development workers (R0-011)
- Primary worker for R0 and R1: Claude Code through the Claude Agent SDK. Prime Agent is kept as the qualified second worker. Reason: the operator starts or approves these runs and already holds the subscription. This is a default the owner can reverse.
- OpenHands, Prime, Claude Code and Agent SDK versions: the newest stable release at the time R0-011 is implemented, pinned exactly (ADR-0032 rule).
- OpenHands Agent Canvas is not used as an operator interface. The operator interface is the Presence console.
- Parallelism at the start: 2 root workers, each with at most 2 child workers.

### 3. Sandbox and supply chain (R0-012)
- Boundary: each run is one non-root container under gVisor on the Worker VM, with a read-only root file system, no Docker socket, and outbound traffic only through an allow-list proxy. The Worker VM is the outer boundary and has no route to the management network.
- Registries allowed through the proxy: PyPI, the npm registry, the Debian archive, and container images from official publishers pinned by digest.
- License policy for code linked into the product: MIT, BSD, Apache-2.0, ISC, PSF and MPL-2.0 are allowed; LGPL needs a review note; GPL, AGPL, SSPL, Elastic License and Business Source License are refused. Unmodified infrastructure services under GPL or AGPL (run as separate processes) are allowed after review.
- Limits per run at the start: 2 hours wall clock, 4 virtual CPUs, 8 GB memory, 20 GB disk, USD 5 of API spend. The operator may raise a limit for a named run.
- Redacted session artifacts are kept 90 days.

### 4. CI (R0-002)
- CI provider: GitHub Actions (ADR-0032).
- Test services (PostgreSQL, later Redis and Temporal) start from the same Docker Compose file used locally.
- CI artifacts are kept 30 days. A vulnerability rated high or critical blocks a merge; an exception needs a written, dated waiver in the repository.

### 5. Database (R0-003)
- No external connection pooler at the start; Django persistent connections are used.
- Tenant context is carried as a transaction-scoped setting (`set_config(..., true)`) set at the start of every transaction. This stays correct if a pooler in transaction mode is added later. A session-scoped setting is never used.
- R0 enforces tenant at the database layer. Profile is enforced in the service layer until R1.

### 6. Identity (R0-004)
- Sign-in library: django-allauth, with only the Google provider enabled and password sign-in disabled.
- An individual profile is its own tenant (owner decision, 2026-11-15).

### 7. Temporal (R0-005)
- Newest stable Temporal server; workflows written with the Python SDK.
- Persistence: PostgreSQL, in a separate database with its own role on the Data VM. Temporal tables never share a database with tenant tables.

### 8. Audit and observability (R0-006)
- OpenTelemetry Collector feeding Prometheus (metrics), Loki (logs) and Tempo (traces), viewed in Grafana. All run unmodified, internal only.
- Platform-level audit events (not belonging to a tenant) live in an append-only table in a separate PostgreSQL schema, readable only by the operator role.

### 9. PresenceBench (R0-007)
- Evaluation artifacts go to the object store and are kept 180 days; the summary rows are kept without limit.

### 10. Security brokers (R0-008)
- Object storage: product code speaks only the S3 API. Target implementation: Garage, single node. SeaweedFS is the alternative if the review prefers it. The choice is rechecked when R0-008 starts because this field changes quickly.
- Secrets: OpenBao from the start, one node on the Platform VM with integrated storage. Unseal keys are split 2-of-3 and held by the operator outside the system. A daily encrypted snapshot goes into the normal backup. After a restart the operator unseals by hand; automatic unseal is reconsidered if restarts prove frequent.
- Malware scanner: ClamAV, run as a separate service.
- Default limits: outbound fetch 10 MB, 15 seconds, at most 3 redirects with each hop checked again; upload 25 MB.

### 11. Infrastructure (R0-009)
- Cloudflare Access is placed in front of the console hostname, with Google as the identity source and an allow list equal to the invitation list. The application still performs its own Google sign-in; Access is an extra layer, not a replacement.
- Base operating system: Debian stable (ADR-0032).
- Internal names use `presence.internal`. Separate Proxmox bridges with firewall rules are used for management, services and the worker sandbox. VLANs are added when a managed switch is in use.

### 12. Delegation and authorization (R1-001, R1-002)
- Permission names follow `resource.action` (for example `property.publish`). The catalogue itself is written in R1-001.
- Break-glass access lasts at most 60 minutes; the operator is notified by push and email and the event is audited.
- A grantee is a Person only in R1.
- Default grant lifetimes by risk: low 90 days; medium 30 days; high single use within 24 hours; critical single use within 15 minutes after a fresh sign-in.

### 13. Action Broker (R1-003)
- An uncertain outcome is the state `OUTCOME_UNKNOWN`. It is never retried automatically. It is resolved by checking the external platform, or by the operator (E-049).
- Every check in the chain is repeated at execution time.

### 14. Budgets (R1-004)
- When a tenant is paused, reserved actions that have not started are cancelled and their reservations released. An action already executing is allowed to finish, because a side effect cannot be safely cut in half.

### 15. Hostnames and domains (R1-005, R1-006)
- Random hostnames: 12 characters from lowercase letters and digits without look-alikes (no `0`, `1`, `i`, `l`, `o`), starting with a letter, passed through a blocked-word list. Randomness is naming only, never access control.
- A hostname binds to a property environment, not to a service.
- A preview expires after 14 days by default.
- A released vanity name is quarantined for 180 days.
- Vanity fee and downgrade grace period do not apply (ADR-0030: nothing is sold).
- Custom-domain ownership is rechecked daily.

### 16. Connection Broker (R1-007)
- OAuth client library: Authlib.
- Health is checked every 6 hours and before each use. One failure marks a connection DEGRADED; three failures in a row, or any revocation or authorization error from the platform, block it at once.
- A connection belongs to a tenant and may be narrowed to one property.

### 17. Artifacts (R1-008)
- Hash: SHA-256. Structured content is canonicalised with the JSON Canonicalization Scheme (RFC 8785) before hashing.
- Maximum object size 2 GB. All versions are kept in R1; a pruning policy is a later decision.

### 18. Resource Governor (R1-009)
- Slots and leases are held in Redis with expiry times.
- If Redis is down, no new heavy or AI work starts; it queues. Reading the console still works.
- Anti-starvation: a waiting job gains priority with age, and the lowest class always keeps at least one slot.

### 19. Digital properties (R1-011)
- An archived property is deleted after 30 days.
- Tenant roles apply to every property in R1; there are no property-level roles.
- A property with an active custom domain cannot be deleted until the domain is detached.

### 20. Tenant AI (R1-012)
- A "session" for model pinning is one task run. The model is pinned for the whole run; a new run takes the current default.
- Data classes: `public`, `business_internal`, `client_confidential`, `personal_data`, `financial`, `secret`. The class `secret` is never sent to any model.
- Initial providers: Anthropic and DeepSeek. Default policy for a new tenant: the frontier profile may receive every class except `secret`; the low-cost profile may receive `public` only.

### 21. Contract changes made with this ADR
- `action.schema.json`: state `OUTCOME_UNKNOWN` added.
- `authorization-grant.schema.json`: `created_at` added and required.
- `tenant-access-grant.schema.json`: `id` added and required.
- `hostname.schema.json` still names `service_id`. R1-005 replaces it with the property environment reference.

## Still open
- The registrable domain for client sites and previews; the cloud target for the offsite backup (owner).
- Left to the named task, to be recorded in its report: the permission catalogue content, the action-class and risk table, the structure of `scope` and `constraints`, the initial limit keys, per-class governor limits and weights, custom-domain state names and model-revision state names.

## Consequences
- R0 and R1 can start without waiting on a technical choice.
- Manual unseal means the system does not return to full service after a power cut until the operator acts.
- Cloudflare Access adds a second allow list that must match the invitation list.
- Several named tools (Garage, Loki, Tempo, Grafana, ClamAV) carry copyleft licenses. They run unmodified as separate services, which the license policy in section 3 allows after review.

## Alternatives considered
- A gateway library: refused; it is a wide dependency in the path of every credential and prompt, and the governing parts must be in-house either way.
- Prime Agent as primary worker: kept as second worker; can be swapped by the owner.
- A hosted secrets or observability service: refused for now; it would move secrets or logs outside the home system without need.
