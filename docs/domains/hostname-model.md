# Platform Hostname Model


> **Presence OS engineering source of truth**
>
> Baseline date: **2026-08-08** (Asia/Karachi project context).
> Product architecture is intentionally model-, provider-, harness-, and ingress-neutral.
> Vendor capabilities, model names, prices, quotas, laws, and platform policies are time-sensitive reference facts and MUST be revalidated before implementation or purchase.
> When a focused document conflicts with an older discussion, the focused document plus the Decision Register and ADRs control.


## Rule

Every tenant/service receives an immutable randomized, collision-resistant platform hostname by default.

Examples:
- `k7m4q2.presence.site`
- actual format to be finalized by implementation/security review.

Do not derive infrastructure identity from person/company names.

Benefits:
- collision resistance;
- lower identity leakage;
- immutable routing despite rename;
- no sequential customer-count disclosure.

## Hostname types

- RANDOM_CANONICAL
- VANITY
- CUSTOM_DOMAIN
- PREVIEW

The random canonical route remains the infrastructure identity even when aliases are added.

## Vanity alias

Optional human-readable platform subdomain:
- availability checked;
- DB uniqueness authoritative;
- reserved/protected-name policy;
- abuse/homograph checks;
- assigned by the operator; the number per tenant is a tenant limit.

Do not rely on frontend availability check; claim atomically under uniqueness constraint.

## Preview

Preview identifiers should be randomized and noindex. Randomness is not authentication.

Sensitive previews require authentication/password/signed-share policy.

Avoid deeper subdomains if relying only on first-level Universal SSL coverage. Prefer a separate preview registrable domain/zone or first-level naming strategy.
