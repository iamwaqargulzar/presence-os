# Cloudflare Infrastructure

Cloudflare Tunnel is the default ingress (ADR-0006); the static-IP path is in `docs/runbooks/tunnel-to-static-origin.md`. Platform DNS, tenant domains and custom hostnames come in R1/R3.

`cloudflared.yml` sends every tunnel hostname to Caddy on the Edge VM; Caddy decides what each hostname serves.

## Set up (operator, once)

1. Create a locally managed tunnel on the Edge VM: `cloudflared tunnel login`, `cloudflared tunnel create presence`. Move the credentials JSON to `/etc/presence/cloudflared-credentials.json` (root only, mode 600). It never enters the repository; delete `cert.pem` from the VM afterwards.
2. DNS: `cloudflared tunnel route dns presence edge-test.iamwaqargulzar.com` and the same for `console.iamwaqargulzar.com`. Only these two hostnames point at the tunnel in R0.
3. Cloudflare Access (ADR-0033 section 11): a self-hosted application on `console.iamwaqargulzar.com`, Google as the identity provider, a policy allowing only the invited email addresses, session length 24 h. The test hostname stays public.
4. A rate-limiting rule on the console hostname (Security → WAF), and "Always use HTTPS" on the zone.
5. If a Cloudflare API token is ever needed for automation, scope it to this zone's DNS and tunnel edit only and keep it out of the repository.

Check from outside the site with `infra/proxmox/scripts/verify.sh internet`.
