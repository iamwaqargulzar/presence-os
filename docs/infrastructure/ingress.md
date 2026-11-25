# Ingress Strategy

## Default

Cloudflare Tunnel is the initial/default path.

`Internet → Cloudflare → Cloudflare Tunnel → Edge Gateway/Caddy → internal routing`

Benefits:
- outbound-only origin connection;
- no public IP required;
- no inbound router ports required;
- origin hidden from direct Internet traffic.

## Architectural requirement

Everything after the Edge Gateway must be identical whether ingress is Tunnel or future static-IP origin.

Application code must not care.

## Future direct origin

`Internet → Cloudflare proxy → static public IP:443 → router/firewall → same Edge Gateway → same routing`

The migration is infrastructure/DNS/firewall work, not an application rewrite.

See runbooks:
- `docs/runbooks/tunnel-to-static-origin.md`
- `docs/runbooks/static-origin-to-tunnel.md`
