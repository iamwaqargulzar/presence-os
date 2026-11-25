# Compose / Local Runtime

Initial local/self-hosted orchestration should be simple and reproducible. Do not introduce Kubernetes before an accepted ADR.

- `edge.compose.yaml`, `Caddyfile`, `edge.env.example`: the Edge VM (cloudflared and Caddy, ADR-0006). Host networking, no published ports; Caddy listens on `127.0.0.1:8080` and routes by hostname, answering 404 for unknown hosts.
- Check locally: `docker compose -f infra/compose/edge.compose.yaml --env-file <filled env> config -q` and `caddy validate`.
- Images are pinned by tag and digest. To update, check the upstream release, then replace both.
- The repository-root `compose.yaml` is the developer database for tests (R0-002), not production.
