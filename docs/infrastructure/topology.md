# Physical and Logical Topology


> **Presence OS engineering source of truth**
>
> Baseline date: **2026-08-08** (Asia/Karachi project context).
> Product architecture is intentionally model-, provider-, harness-, and ingress-neutral.
> Vendor capabilities, model names, prices, quotas, laws, and platform policies are time-sensitive reference facts and MUST be revalidated before implementation or purchase.
> When a focused document conflicts with an older discussion, the focused document plus the Decision Register and ADRs control.


## Physical hosts

### Host A — Presence Server
- Proxmox VE bare metal.
- Primary Presence workloads.
- No direct exposure of Proxmox management to Internet.

### Host B — Inference GPU Server (optional)
This host may stay powered off. Presence OS runs cloud-only by default (ADR-0030) and must work fully without it. When it is on:
- AMD Ryzen 7 8700G
- 32 GB RAM
- NVIDIA RTX 3090
- llama.cpp
- ComfyUI
- voice services
- video model loaded on demand
- private LAN/VLAN access only

### Host C — Backup/Storage
- former Coolify server repurposed
- Proxmox Backup Server/storage target
- local backup target; encrypted offsite copy still required

## Initial VM layout — intentionally lean

### Edge VM
- cloudflared
- Caddy
- public ingress termination, including the operator console hostname
- hostname routing edge
- no business database

### Core VM
- Next.js
- Django
- Temporal app/workers as appropriate
- Redis/workers may initially coexist
- business/control plane

### Data VM
- PostgreSQL + pgvector
- S3-compatible object storage
- backup agents

### Worker VM
- Playwright
- gVisor/untrusted coding/build sandboxes
- crawling/browser tasks
- development workers, including the official Claude Code harness signed in with the operator's subscription

Split further only when scale/security/operations justify it.

## Administrative access

Proxmox and SSH are reached from the local management network, or remotely through the operator's WireGuard VPN on the router. The VPN is managed by the operator outside this project. Nothing administrative is published through the Cloudflare Tunnel.

## Conceptual future network zones

- MGMT
- EDGE
- CONTROL
- WORKERS
- PRODUCTION
- GPU

These can initially map to simpler LAN arrangements while preserving service boundaries in configuration.

## Home-hosting reliability

Do now:
- UPS + clean shutdown;
- SMART/ZFS monitoring and scrubs;
- PBS;
- encrypted offsite backup;
- infrastructure-as-code/reproducible config;
- restore drills;
- documented RPO/RTO.

Do not market enterprise-grade uptime until topology actually supports it.
