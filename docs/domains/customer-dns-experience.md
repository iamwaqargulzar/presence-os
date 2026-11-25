# Customer DNS Experience

The customer should not need to understand or create a Cloudflare Tunnel.

For a customer-owned domain, the normal experience is:
- Presence provides exact DNS records;
- customer changes records at their registrar/DNS provider or authorizes supported provider automation;
- Presence validates and routes through its platform.

Prefer retaining customer DNS provider.

Cloudflare Tunnel is Presence's origin-ingress mechanism and should remain invisible to ordinary customers.
