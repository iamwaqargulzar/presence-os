# R1-006 — Vanity and Custom Domain Foundations

> **Spec revision:** 2 — 2026-11-10. Expanded from a one-paragraph summary to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). The revision 1 summary is kept verbatim under Goal. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## Goal
Implement vanity syntax/reserved-name/atomic-claim lifecycle and Cloudflare custom-domain state machine. Control plane and tenant content must remain on separate registrable domains.

## Why now
A business will not share a random address with customers. Vanity names are assigned by the operator and custom domains are expected for the R3 website product; their lifecycle and takeover protections belong in the kernel.

## Context / linked docs / ADRs
- Edge cases added 2026-11-14 that this task must cover: E-080 ([register](../../docs/PROJECT_REAUDIT_2026-08-10.md)).
- [Vanity hostname policy](../../docs/domains/vanity-policy.md)
- [Customer custom domains](../../docs/domains/custom-domains.md)
- [Customer DNS experience](../../docs/domains/customer-dns-experience.md)
- [Cloudflare strategy](../../docs/domains/cloudflare-strategy.md)
- [Domain separation](../../docs/domains/domain-separation.md)
- Runbooks: [vanity hostname](../../docs/runbooks/vanity-hostname.md), [custom domain onboarding](../../docs/runbooks/custom-domain-onboarding.md)
- [Re-audit edge cases E-016, E-054, E-055](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0007, ADR-0008, ADR-0018

## Depends on
- R1-005 (registry), R1-004 (tenant limit for vanity and custom domains), R0-005 (verification workflow).

## Invariants
- control plane and tenant content stay on separate registrable domains;
- the random canonical hostname is retained under every alias and remains the recovery path;
- a vanity name is claimed atomically under a uniqueness constraint;
- a previously public vanity hostname is never recycled immediately;
- the customer keeps ownership of their domain; prefer keeping their existing DNS provider;
- no Enterprise-only Cloudflare feature is assumed;
- Cloudflare API tokens are narrowly scoped and held by the Secrets Broker; the DNS/domain change is an external side effect and goes through the Action Broker.

## In scope
**Vanity**
- Syntax validation: ASCII lowercase letters, digits, hyphen; 3–32 characters; no leading/trailing hyphen; no Unicode/homograph names.
- Reserved-name list (admin, api, app, auth, billing, cdn, docs, help, login, mail, portal, preview, status, support, www, and extensions) plus an impersonation-pattern check hook.
- Atomic claim tied to a tenant limit.
- Lifecycle: ACTIVE → RELEASE_PENDING → QUARANTINED → AVAILABLE, with manual-release flag for high-risk names.
- Downgrade behaviour: grace period, keep serving, offer retention or release.

**Custom domain**
- State machine for: domain entered → ownership/routing validation → hostname validation → certificate validation → attached → health-checked → optionally primary; with failure, suspended and removed states.
- DomainVerification and CertificateState records.
- Verification as a durable workflow with manual CNAME/TXT instructions.
- Periodic ownership/DNS health re-check; suspend the hostname (not the property) when evidence fails.
- Cloudflare for SaaS custom-hostname adapter behind an interface, exercised against a fake in tests.

## Out of scope
- Automatic provider OAuth / Domain Connect setup.
- Full DNS migration to platform-managed DNS, including MX/SPF/DKIM/DMARC preservation.
- Internationalised (IDN) vanity names.
- Any purchase or checkout flow: vanity names are assigned by the operator (ADR-0030).
- Trademark dispute handling beyond manual release.

## API / contract changes
- Endpoints: check and claim vanity; release; add custom domain; get verification instructions and status; set primary; remove.
- `hostname.schema.json` used for VANITY and CUSTOM_DOMAIN types; add verification and certificate state references if they cross module boundaries.
- Adapter interface for the custom-hostname provider.

## Data / migration
- Extends the R1-005 Hostname table usage; adds reserved-name table (platform-level), DomainVerification, CertificateState, quarantine timestamps.
- Reverse migrations tested.

## Security / privacy threat notes
- Subdomain/hostname takeover after release or after the customer's domain expires or is reassigned (E-054, E-055).
- Impersonation through look-alike vanity names.
- Race on claim; availability check used as an oracle.
- Attaching a domain the tenant does not control: verification must prove control, and must be re-proven periodically.
- Property deleted while the custom domain still points at the platform (E-016).
- Over-scoped Cloudflare token.

## Observability
- Audit: claim, release, quarantine transitions, domain added, verification result, certificate state change, primary change, suspension.
- Metrics: domains by state, verification failures, certificate expiry horizon, health-check failures.

## Acceptance criteria
- *(revision 1)* vanity syntax validation;
- *(revision 1)* reserved-name policy;
- *(revision 1)* atomic claim and lifecycle;
- *(revision 1)* Cloudflare custom-domain state machine;
- *(revision 1)* control plane and tenant content on separate registrable domains;
- *(derived)* a released vanity name cannot be claimed during quarantine;
- *(derived)* failed ownership re-check suspends the custom hostname while the canonical hostname keeps working;
- *(derived)* the provider call is made only through the Action Broker with a valid grant.

## Tests
- Unit: syntax matrix, reserved names, homograph rejection.
- Concurrency: parallel claims of one vanity name.
- Lifecycle: release → quarantine → available at boundary times; downgrade grace.
- Custom domain: full happy path against the fake provider; each failure state; ownership lost after activation.
- Security: cross-tenant RLS suite; attach attempt for a domain verified by another tenant denied; tenant limit missing denied.
- No test calls the real Cloudflare API.

## Rollback / failure recovery
Verification is a resumable workflow. A failed attach leaves the canonical hostname untouched. Removing a custom domain detaches routing first, then releases provider resources. Reverse migrations tested.

## Cost/resource budget
Cloudflare for SaaS has per-hostname pricing above an included amount; treat the figures in the source registry as reference data to be revalidated, and expose the count as a per-tenant limit.

## Documentation updates
- `docs/domains/vanity-policy.md`, `docs/domains/custom-domains.md`, both runbooks.
- `docs/architecture/state-machines.md` (custom-domain states).
- Contract schema.

## Open decisions
- **Decided (ADR-0033):** 180 days.
- **Decided (ADR-0033):** not applicable; nothing is sold (ADR-0030).
- **Decision required:** exact custom-domain state names.
- **Decided (ADR-0033):** daily.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review of the takeover protections is recorded.
