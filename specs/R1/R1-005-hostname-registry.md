# R1-005 — Hostname Registry and Random Platform Addresses

> **Spec revision:** 2 — 2026-11-10. Expanded from a one-paragraph summary to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). The revision 1 summary is kept verbatim under Goal. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## Goal
Generate secure random canonical hostnames, route through wildcard platform DNS/Edge, enforce uniqueness and service binding, and preserve immutable routing across profile/company rename.

## Why now
Every hosted property, preview and tenant service needs an address that does not depend on a name, a DNS API call or a manual step. Vanity and custom domains (R1-006) and DigitalProperties (R1-011) attach to this registry.

## Context / linked docs / ADRs
- Edge cases added 2026-11-14 that this task must cover: E-080 ([register](../../docs/PROJECT_REAUDIT_2026-08-10.md)).
- [Platform hostname model](../../docs/domains/hostname-model.md)
- [Domain separation](../../docs/domains/domain-separation.md)
- [Cloudflare strategy](../../docs/domains/cloudflare-strategy.md)
- [Ingress strategy](../../docs/infrastructure/ingress.md)
- [State machines](../../docs/architecture/state-machines.md)
- [Re-audit edge cases E-014, E-016, E-023](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- Contract: [hostname.schema.json](../../contracts/schemas/hostname.schema.json)
- ADR-0006, ADR-0007, ADR-0008

## Depends on
- R0-003, R0-004, R0-006.
- R0-009 (Edge VM, Caddy, a wildcard tenant zone) for the routing part *(derived)*.

## Invariants
- tenant-generated content never shares a registrable domain with the control plane;
- a randomized URL is not an access-control mechanism;
- infrastructure identity is never derived from a person or company name;
- the random canonical hostname is immutable and remains the infrastructure identity when aliases are added;
- database uniqueness is authoritative; never rely on a frontend availability check;
- provisioning a platform hostname is a database operation, not a per-customer DNS API call.

## In scope
- Hostname entity with type (RANDOM_CANONICAL, VANITY, CUSTOM_DOMAIN, PREVIEW) and status (PENDING, ACTIVE, REDIRECT, RELEASE_PENDING, QUARANTINED, DISABLED, FAILED). This task implements RANDOM_CANONICAL and PREVIEW; other types are reserved for R1-006.
- Secure random label generation from a cryptographic source, with collision retry under a uniqueness constraint.
- Atomic claim and binding of a hostname to exactly one route target.
- Edge routing lookup: host header → registry → target, with a safe default response for unknown, disabled or tombstoned hostnames.
- Preview hostnames: random, `noindex`, expiry, on the preview zone.
- Tombstone behaviour when a target is removed while the hostname still resolves (E-016).
- Rename safety: changing a profile or company name changes no hostname.

## Out of scope
- Vanity hostnames and custom domains (R1-006).
- Preview authentication itself (the registry marks a preview as sensitive; enforcement arrives with property environments in R1-011).
- Certificates beyond what the wildcard zone already provides.
- Path-based routing between properties.

## API / contract changes
- Internal: allocate canonical hostname, allocate preview hostname, bind/unbind, resolve.
- Edge-facing resolve interface (read-only, low latency, cacheable with explicit invalidation).
- `hostname.schema.json`: the schema binds a hostname to `service_id`, while the 2026-08-10 property model routes through `HostnameAttachment → PropertyEnvironment/ServiceUnit`. Decide the binding target now so R1-011 does not need a breaking change, and record it. The state-machine document ends in `AVAILABLE/removed`, which the schema does not have; align them.

## Data / migration
- Hostname table, tenant-scoped under RLS, with a **global** uniqueness constraint on the hostname string. Global uniqueness under per-tenant RLS needs care: the constraint must hold across tenants without the runtime role being able to read other tenants' rows.
- The Edge resolver needs a cross-tenant read of routing data only: provide a dedicated narrow role or a routing projection, not BYPASSRLS on the runtime role.
- Reverse migrations tested.

## Security / privacy threat notes
- Hostname takeover: a released or dangling hostname served to a new owner too early.
- Two targets claiming one hostname (E-014).
- Enumeration: predictable or sequential labels disclose customer count.
- Uniqueness check leaking the existence of another tenant's hostname beyond "taken".
- Preview leak (E-023): random plus noindex is not authentication.
- Cookie scope: nothing set on the tenant zone may be valid for the control-plane domain.
- Offensive or misleading random labels: filter the alphabet or reject by list.

## Observability
- Audit: allocation, binding change, status change.
- Metrics: resolve latency and miss rate at the Edge, collisions on allocation, hostnames by status.
- Domain/certificate state metrics reserved.

## Acceptance criteria
- *(revision 1)* secure random canonical hostnames generated;
- *(revision 1)* routed through wildcard platform DNS and the Edge;
- *(revision 1)* uniqueness and service binding enforced;
- *(revision 1)* routing immutable across profile/company rename;
- *(derived)* concurrent allocation of the same label yields exactly one owner;
- *(derived)* unknown, disabled and tombstoned hostnames get a safe response and never another tenant's content;
- *(derived)* previews are noindex and expire;
- *(derived)* the Edge resolver has no general cross-tenant data access.

## Tests
- Unit: label generation alphabet/length, collision retry.
- Concurrency: parallel claims of one hostname.
- Integration: request through Caddy to a test target by canonical hostname; rename then re-request.
- Security: cross-tenant RLS suite; resolver role cannot read non-routing columns or other tables; unknown host does not fall through to a default tenant.
- Preview: expiry enforced, noindex header present.

## Rollback / failure recovery
Routing fails closed to the safe default response. Registry changes are transactional. If the resolver cache is stale, explicit invalidation plus a short TTL bound the exposure. Reverse migrations tested.

## Cost/resource budget
One resolve per request at the Edge: must be cached. Stay within Cloudflare's first-level wildcard coverage; deeper subdomains need extra certificate capability and are avoided. Revalidate Cloudflare limits before relying on them.

## Documentation updates
- `docs/domains/hostname-model.md` (final format, binding target).
- `docs/architecture/state-machines.md`.
- Contract schema.
- `infra/cloudflare/README.md` (zone and wildcard records).

## Open decisions
- **Decision required:** registrable domains for tenant production and preview zones. They must differ from the control-plane domain `iamwaqargulzar.com` (owner, 2026-11-15).
- **Decided (ADR-0033):** 12 characters, lowercase letters and digits without `0 1 i l o`, starting with a letter, with a blocked-word list.
- **Decided (ADR-0033):** a property environment. This task replaces `service_id` in `hostname.schema.json`.
- **Decided (ADR-0033):** 14 days.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent review of the resolver's database access is recorded.
