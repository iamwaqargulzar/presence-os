# Runbook — Static Public IP Back to Cloudflare Tunnel

1. Confirm Tunnel/cloudflared version/config and credentials.
2. Establish outbound tunnel from Edge VM.
3. Validate tunnel health.
4. Route a test hostname if feasible.
5. Switch Cloudflare origin to Tunnel.
6. Verify control, tenant, preview and custom-domain traffic.
7. Verify webhooks/streaming.
8. Close public router forwarding if direct origin is no longer required.
9. Preserve static-origin documentation for future recovery.
10. Record incident/reason and metrics.

Application/internal Caddy routing remains unchanged.
