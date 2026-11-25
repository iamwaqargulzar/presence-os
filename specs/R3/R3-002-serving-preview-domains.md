# R3-002 — Tenant Site Serving, Preview and Custom Domain Go-Live

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 and R2 are built; recheck against their implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Serve tenant sites and previews to the internet from the Edge VM, on a registrable domain that is not the control plane's. Each property gets its random hostname at once, optional vanity and custom domains, and private previews that expire.

## Why now
The kernel can register hostnames and verify domains (R1-005, R1-006) but serves nothing. This is the first time tenant-generated content is online, so domain separation must be real, not planned.

## Context / linked docs / ADRs
- [Registrable-domain security separation](../../docs/domains/domain-separation.md)
- [Platform hostname model](../../docs/domains/hostname-model.md)
- [Customer custom domains](../../docs/domains/custom-domains.md)
- [Cloudflare strategy](../../docs/domains/cloudflare-strategy.md)
- [Ingress](../../docs/infrastructure/ingress.md)
- [Network and service exposure](../../docs/security/network-and-service-exposure.md)
- [Runbook: custom domain onboarding](../../docs/runbooks/custom-domain-onboarding.md)
- [Digital properties and multi-property hosting](../../docs/product/digital-properties-and-hosting.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0006, ADR-0007, ADR-0008, ADR-0021, ADR-0033

## Depends on
- R3-001 (artifacts). Uses R1-005, R1-006, R1-011, R0-009 (tunnel, Caddy).

## Invariants
- nothing tenant-generated is served under the control-plane registrable domain (`iamwaqargulzar.com` today), including previews, error pages for tenant hosts and uploaded files;
- a random hostname or preview URL is naming, never access control;
- a sensitive preview needs authentication, is `noindex`, and expires;
- one hostname maps to one property environment. No path sharing between properties (E-015);
- the edge serves only what the Hostname Registry says. An unknown or released host gets a safe holding response, never another tenant's site;
- a custom domain stays the client's property; losing it suspends that hostname only, the random hostname remains;
- Proxmox, PostgreSQL, Redis, Temporal and the secrets store are never reachable through the tenant ingress.

## In scope
- Tenant-site zone setup on the second registrable domain: wildcard DNS and certificate for production, and a separate zone or first-level naming for previews.
- Edge routing: Caddy on the Edge VM resolves the request host through the registry's read interface (cached, with explicit invalidation) to a property environment and its current artifact.
- Static serving of the artifact pinned to the environment's active deployment. Atomic switch between artifacts.
- Security headers for tenant sites; no cookies shared with any other tenant host; the public-suffix question is recorded (see open decisions).
- Preview environments: random preview hostname, `noindex` header and robots rule, expiry (14 days by default, ADR-0033), and for sensitive previews a signed-in viewer check or a signed share link with expiry.
- Client preview access: a Client Approver opens the preview from the approval item; the preview domain checks a short-lived signed token issued by the console.
- Vanity hostname go-live: an operator-assigned alias routes like the canonical name.
- Custom domain go-live: after R1-006 verification, issue the certificate, attach, health-check, optionally make it primary with a redirect from the canonical name. Follows the runbook.
- Daily ownership recheck result handling: on failure, suspend that hostname with a neutral holding page and raise an attention item.
- Holding responses: unknown host, suspended property, archived property, released hostname. No tenant content, no platform branding that helps phishing.
- Delete path: hostname attachment and DNS records removed in the delete workflow; dangling-record scan run on a schedule.
- Outage visibility: an external check tells the operator when tenant sites are unreachable.
- Bandwidth and request metrics per property for limits.

## Out of scope
- Building (R3-001) and deploying (R3-003).
- Server-side runtimes; only the `static` profile is served unless another profile is qualified.
- Automatic DNS provider setup (Domain Connect) and DNS migration with mail records.
- A content delivery network product beyond what Cloudflare gives by default. Edge cache during a home outage is an open decision.
- Web application firewall rule tuning per tenant.

## API / contract changes
- Edge-facing: `resolve(host) → environment, artifact, flags (noindex, auth required, suspended)`.
- Endpoints: create preview, share preview (signed link), expire preview; go-live for vanity and custom domains; set primary.
- `hostname.schema.json`: confirm the environment binding (ADR-0033 point 21) and add `serving_state`.

## Data / migration
- Uses R1 tables. Adds PreviewShare (tenant-scoped, RLS) and ServingEvent for suspensions.
- Reverse migrations tested.

## Security / privacy threat notes
- Cookie or origin attack from a tenant site on the console: different registrable domain; the console sets host-only cookies; test that no tenant host can set a cookie the console reads.
- Tenant sites attacking each other through shared-domain cookies: tenant sites are static with no platform session; the tenant-site domain is submitted to the Public Suffix List if the decision below says so.
- Subdomain takeover through a DNS record left behind (E-016, E-080): delete workflow plus scheduled scan.
- Host-header tricks reaching another tenant's site or an internal service: strict registry match, no default site, internal names refused.
- Preview leak (E-023): authentication for sensitive previews, expiry, `noindex`, no listing.
- Phishing hosted on a tenant site: only the operator deploys; content passes R3-008; a takedown path exists.
- Signed link forwarded to others: short expiry, single property, revocable.

## Edge cases covered
- E-014 two properties claim one hostname (registry is authoritative at the edge).
- E-015 path sharing: refused.
- E-016 and E-080 deleted property with DNS still pointing.
- E-023 preview leaks a private site.
- E-054 custom domain expires or is reassigned.
- E-055 vanity name quarantine respected at the edge.
- E-085 home outage takes sites offline.

## Observability
- Audit: go-live, primary change, suspension, preview share created and used.
- Metrics: requests and bytes per property, certificate expiry, resolve latency, holding responses by reason, external reachability.

## Acceptance criteria
- a property is reachable on its random hostname within one minute of its first deployment, with no DNS work;
- no response for any tenant host carries a cookie for, or content from, the control-plane domain;
- an unknown host, a released vanity name and a suspended property each return the holding response;
- a sensitive preview cannot be read without a valid sign-in or signed link, and stops working at expiry;
- a custom domain goes live without rebuilding the property and can be detached without affecting the random hostname;
- deleting a property removes its routes and DNS records; the scan finds none left.

## Tests
- Routing matrix: canonical, vanity, custom, preview, unknown, suspended, quarantined.
- Cookie and origin isolation test between the console origin and a tenant host.
- Preview: unauthenticated, expired, wrong tenant's signed link, revoked link.
- Tenant isolation: a host of tenant A never resolves to an artifact of tenant B, including after cache invalidation races; RLS suite on PreviewShare.
- Host-header fuzzing; internal hostnames refused.
- Domain loss simulation: verification fails → hostname suspended, canonical still works.
- Dangling-record scan on a seeded leftover record.

## Rollback / failure recovery
Routing changes are data changes with audit and can be reverted. Certificates renew before expiry with an alert on failure. The tunnel-to-static-origin runbooks remain valid.

## Cost/resource budget
Static serving is cheap. Proposed default limits per tenant: 10 properties, 20 GB transfer per month, 5 live previews per property; all changeable by the operator.

## Documentation updates
- `docs/domains/domain-separation.md` (the chosen tenant-site domain), `docs/domains/hostname-model.md`, `docs/infrastructure/ingress.md`, `docs/runbooks/custom-domain-onboarding.md`.

## Open decisions
- **Decision required (owner, blocking for this task):** the registrable domain for client sites and previews. It must not be `iamwaqargulzar.com`. Proposed default: buy one neutral domain for production sites and use a second for previews.
- **Decision required (owner):** whether static sites are also served from an edge cache or a small cloud host during a home outage (E-085). Proposed default: yes for production static sites, through Cloudflare caching with "serve stale" where the plan allows; recheck current Cloudflare terms and price.
- **Decision required:** custom-domain certificates: Cloudflare for SaaS, or Caddy on-demand TLS with an ask endpoint. Proposed default: Caddy on-demand TLS, because it needs no paid add-on; revisit if the tunnel makes it impractical.
- **Decision required:** submit the tenant-site domain to the Public Suffix List. Proposed default: yes, before the first client site.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review of domain separation and preview access; the cookie-isolation test joins the protected tests.
