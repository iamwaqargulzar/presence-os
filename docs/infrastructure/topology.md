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

## Allocations and names (R0-009)

Built by `infra/proxmox/vms.sh`. Sizes are a starting point (assumption; confirm against host A's real CPU, RAM and disks) and can be changed with `qm set`.

| VM | ID | Name | Bridge | Address | vCPU | RAM | Disk |
|---|---|---|---|---|---|---|---|
| Edge | 110 | `edge.presence.internal` | vmbr1 | 10.77.10.10 | 2 | 2 GB | 20 GB |
| Core | 120 | `core.presence.internal` | vmbr1 | 10.77.10.20 | 4 | 8 GB | 60 GB |
| Data | 130 | `data.presence.internal` | vmbr1 | 10.77.10.30 | 4 | 8 GB | 200 GB |
| Worker | 140 | `worker.presence.internal` | vmbr2 | 10.77.20.10 | 8 | 16 GB | 200 GB |
| Inference (host B) | — | `inference.presence.internal` | LAN | site-specific | — | — | — |

- `vmbr0`: the LAN and management network, as the Proxmox installer created it. Only the host has an address there.
- `vmbr1` (10.77.10.0/24, services) and `vmbr2` (10.77.20.0/24, worker sandbox): host-only bridges, NAT to the Internet through the host (`infra/proxmox/interfaces.presence`). Nothing on the LAN can open a connection to a VM.
- Names resolve from `infra/proxmox/presence.internal.hosts`; upstream DNS is public resolvers.
- SSH to a VM goes through the Proxmox host (`ssh -J`); the VM firewall accepts SSH only from the host's bridge address.

Allowed flows (Proxmox firewall, default drop both ways per VM; `infra/proxmox/firewall/`):

| From | To | Port | Why |
|---|---|---|---|
| Edge | Core | 3000 | Caddy to the console |
| Core | Data | 5432, 3900 | PostgreSQL, object storage |
| Core | Inference | 8443 | private inference gateway |
| Edge, Core, Worker | Internet | any | tunnel, providers, crawling (R0-012 narrows the Worker) |
| Data | Internet | 53, 123, 80, 443 | DNS, time, package updates |
| Management set | Proxmox host | 8006, 22 | administration |

Everything else between VMs, to the LAN, to the router, to the Proxmox host and to the inference host is dropped. Inference host B runs `infra/proxmox/inference-host.nft`: only the gateway port, only from host A.

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
