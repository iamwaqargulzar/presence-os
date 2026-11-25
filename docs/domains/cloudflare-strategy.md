# Cloudflare Strategy

## Platform-owned zones

Use Cloudflare-managed zones for control/tenant/preview domains.

For platform-hosted first-level tenant hostnames, prefer wildcard DNS such as:
`*.presence.site → Presence Edge`

Then tenant hostname provisioning is a Hostname Registry/database operation, not a DNS API call per customer.

## Custom customer domains

Use Cloudflare for SaaS/custom hostnames when appropriate.

Do not architect the product around Enterprise-only features unless a concrete requirement needs them.

## Certificates

Be aware that Universal SSL on a full setup covers the apex and first-level subdomains, not arbitrary deeper subdomains.

## API

Use narrowly scoped Cloudflare API tokens. Avoid global API keys.

Current Cloudflare pricing/limits are reference data and must be rechecked before commercial decisions.
