# R3-001 — Property Runtime Profiles and Build Pipeline

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 and R2 are built; recheck against their implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Turn a property's source into an immutable, hashed release artifact, inside a sandbox, for a small set of qualified runtime profiles. A tenant can have several properties; each builds apart from the others.

## Why now
Nothing can be previewed or deployed until there is a release artifact. Building runs code that an AI wrote for a tenant; it is untrusted code and must be contained from the first build.

## Context / linked docs / ADRs
- [Digital properties and multi-property hosting](../../docs/product/digital-properties-and-hosting.md)
- [Release plan](../../docs/delivery/release-plan.md) (R3 hosting scope)
- [Topology](../../docs/infrastructure/topology.md)
- [Secrets management](../../docs/security/secrets.md)
- [Capacity and noisy neighbours](../../docs/operations/capacity-and-noisy-neighbor.md)
- [Research notes: hosting](../../docs/research/GITHUB_LANDSCAPE_2026-11-10.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0008, ADR-0016, ADR-0021, ADR-0030, ADR-0033

## Depends on
- R2-017 (R2 exit). Uses R1-011 (property, environment, deployment records), R1-008 (artifacts), R1-009 (governor), R1-004 (limits), R0-008 (secrets), R0-012 (sandbox pattern).

## Invariants
- tenant code is untrusted. It is built and run only inside gVisor sandboxes on the Worker VM or the tenant runtime, never on the Core or Data VM;
- a build has no route to the management network, the control plane's database, or any other tenant's files;
- a release artifact is immutable and identified by its SHA-256 hash;
- only qualified runtime profiles are offered. No arbitrary-language hosting;
- secrets are namespaced by tenant + property + environment and are never baked into an artifact;
- "same tenant" is not a reason to share a build workspace, cache or secret between two properties;
- property hosting limits are separate from AI budgets.

## In scope
- RuntimeProfile registry (platform-level, versioned): name, base image digest, build command, output type, health check, resource class, status (CANDIDATE, QUALIFIED, RETIRED).
- Qualification procedure for a profile: security review, build and run test, backup and restore of its data, resource measurement. Recorded as evidence.
- First profiles: see open decisions. The contract is written so that a profile is data plus a qualification record.
- Property source store: one Git-like versioned source tree per property, held by Presence (object storage or an internal bare repository), tenant-scoped.
- Build workflow (Temporal): fetch source revision → sandboxed dependency install through the allow-list proxy → build → static checks → package artifact → record hash, source revision, profile revision, build log reference. States DRAFT → BUILT, or BUILD_FAILED.
- Verify step: artifact scan (secrets, size, forbidden files), link check, accessibility and basic performance checks on the built output. States BUILT → VERIFIED, or VERIFY_FAILED.
- Build cache per property, never shared across properties or tenants.
- Limits: build minutes, concurrency, artifact size, per tenant and per property, through R1-004 and R1-009.
- Build logs stored as artifacts after the redaction scan.
- Operator view: builds per property, status, log, artifact hash.

## Out of scope
- Serving and previews (R3-002). Deploy and rollback (R3-003). Generating the source (R3-004).
- Databases for tenant apps, background workers and scheduled jobs of tenant apps. **Decision required**; see open decisions.
- Importing a client's existing repository from GitHub.
- Buildpacks or a general PaaS. Deploying an existing PaaS product is against the build-in-house rule (ADR-0030).

## API / contract changes
- Internal: `build(property, source_revision, profile) → deployment record in BUILT/VERIFIED`, `get_build_log`.
- Endpoints: start build, status, log, list artifacts.
- New contract sketches: `runtime-profile.schema.json`, `release-artifact.schema.json`. The Deployment sketch from R1-011 gains `profile_revision`, `source_revision`, `verify_result`.

## Data / migration
- Platform table: RuntimeProfile.
- Tenant-scoped under RLS: PropertySource, Build, BuildLog reference. Uses R1-011 Deployment.
- Reverse migrations tested.

## Security / privacy threat notes
- Malicious or model-written build scripts: sandbox, non-root, read-only base, no Docker socket, time and resource limits.
- Dependency confusion or a hostile package installed at build: registry allow-list, lockfile required, vulnerability scan on the lockfile; high or critical findings block VERIFIED.
- Secret in the artifact or log (E-022, E-036 pattern): build receives only build-time public configuration; runtime secrets are injected at serve time; scan blocks an artifact containing a credential pattern.
- Cross-property cache poisoning: cache key includes tenant and property; no shared layer is writable.
- Build used for crypto-mining or as an outbound relay: egress allow-list, CPU and time caps.

## Edge cases covered
- E-013 a tenant with 20 properties: limits and governor bound count and concurrency.
- E-021 one property takes all build slots: per-tenant and per-property fair queue.
- E-022 secret reused across apps.
- E-034-style dependency risk applied to tenant builds.
- E-081 workflow change while builds are in flight.

## Observability
- Audit: build started (by whom, which source revision), profile revision, result, artifact hash.
- Metrics: build duration, failures by stage, queue wait, minutes per tenant and property.

## Acceptance criteria
- the same source revision and profile revision produce an artifact with the same recorded inputs, and the hash is stored;
- a build cannot reach the control-plane database, the management network or another property's workspace;
- a source tree with a credential pattern does not reach VERIFIED;
- two properties of one tenant never share a workspace, cache or secret;
- a tenant at its build limit is queued or refused with a reason, and other tenants are not slowed;
- a profile that is not QUALIFIED cannot be selected.

## Tests
- Sandbox escape attempts from a hostile build fixture: network, file system, process limits.
- Secret scan and vulnerability gate.
- Fairness: one tenant submits 20 builds; a second tenant's build still starts within the bound.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on PropertySource and Build across tenants; artifact and log of tenant A not readable by tenant B; property A's cache not readable by property B of the same tenant.
- Crash and resume of the build workflow.
- Profile qualification record required.

## Rollback / failure recovery
A failed build leaves the previous artifact and the live site untouched. Artifacts are kept per the R1-008 rule. A profile can be retired; properties on it keep serving their last artifact and are flagged.

## Cost/resource budget
Proposed default per build: 10 minutes, 2 virtual CPUs, 4 GB memory, 500 MB artifact; 2 concurrent builds on the host, 1 per tenant.

## Documentation updates
- `docs/product/digital-properties-and-hosting.md` (profile list, qualification), `docs/infrastructure/topology.md` (where builds run), `docs/runbooks/` (new: qualify a runtime profile).

## Open decisions
- **Decision required (owner):** runtime profiles at R3 start. Proposed default: `static` only (pre-rendered HTML, CSS, JavaScript, images, built with one in-house site generator). A Node/Next.js server profile is the second, qualified later in R3 only if a real client site needs server code.
- **Decision required:** tenant app databases, workers and scheduled jobs. Proposed default: none in R3; forms on static sites post to a small Presence-run endpoint (see R3-004).
- **Decision required:** where property source lives. Proposed default: an internal bare Git repository per property on the Data VM, backed up with the rest.
- **Decision required:** which VM runs builds and the tenant runtime. Proposed default: builds on the Worker VM; serving on the Edge VM for static files.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review of the build sandbox; the `static` profile has a recorded qualification.
