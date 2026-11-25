# Runbook — Cloudflare Tunnel to Static Public IP

## Goal

Switch ingress without application changes.

## Preconditions

- dedicated static public IP confirmed;
- Edge Gateway is the target, not Proxmox management;
- current Tunnel path healthy;
- rollback window scheduled;
- Cloudflare DNS/origin configuration documented;
- firewall rules prepared and reviewed;
- monitoring and synthetic checks available.

## Procedure

1. Record current Cloudflare/Tunnel config.
2. Ensure Edge Gateway can terminate direct-origin HTTPS as designed.
3. Configure router explicit forwarding to Edge Gateway, preferably TCP 443 only.
4. Apply default-deny Edge firewall.
5. Restrict origin source to Cloudflare networks where practical.
6. Configure origin TLS / authenticated origin protection as selected.
7. Add/test temporary direct-origin route without changing production traffic if feasible.
8. Verify:
   - control plane;
   - random platform hostnames;
   - vanity hostnames;
   - custom domains;
   - previews;
   - webhooks/callbacks;
   - websocket/streaming voice paths;
   - health endpoints.
9. Change Cloudflare origin routing/DNS to static IP.
10. Monitor errors/latency/certificates/routing.
11. Keep Tunnel configuration intact during soak period.
12. If stable and operationally desired, disable Tunnel only after explicit decision.

## Rollback

Follow `static-origin-to-tunnel.md`.

## Non-goals

No application URL/schema/business-logic changes should be required.
