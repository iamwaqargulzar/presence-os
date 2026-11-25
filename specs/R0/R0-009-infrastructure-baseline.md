# R0-009 — Proxmox, Network and Backup Baseline

> **Spec revision:** 3 — 2026-11-14. Amended by [ADR-0030](../../docs/adrs/ADR-0030-operator-run-agency-deployment.md); the "ADR-0030 amendments" section overrides any conflicting text below it. Revision 2 (2026-11-10): Expanded to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). Every revision 1 requirement is retained. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## ADR-0030 amendments (revision 3)

**Added to scope**
- A dedicated hostname for the operator console on the control-plane domain, published through the Cloudflare Tunnel and Caddy like the test control hostname. No VPN is part of this task.
- The private inference host is **optional**. The baseline must be complete and pass with that host powered off.

**Changed acceptance criteria**
- "inference reached over private hostname" and "raw GPU model ports not public" apply only when the inference host is deployed; otherwise record it as not deployed.
- *(added)* the console hostname answers only through the tunnel, and an unauthenticated request receives nothing but the sign-in redirect;
- *(added)* Proxmox, SSH and every internal service remain unreachable from the Internet with the console published;
- *(added)* all four VMs and the restore drill pass with the inference host powered off.

**Added invariants**
- the console hostname is on the control-plane registrable domain, never on the domain used for tenant content;
- publishing the console never publishes an administrative service: Proxmox and SSH are reached from the local management network, or remotely through the operator's WireGuard VPN on the router, and by no other path.

**Added threat notes**
- The console is visible on the public Internet. Sign-in is delegated to Google (R0-004), rate limiting applies at the edge, and Cloudflare Access in front of the console is an open decision.
- A lost or stolen operator phone: session revocation in Presence OS and sign-out of the Google account are documented and tested once.

**Open decisions added**
- **Decided (ADR-0033):** yes; Cloudflare Access sits in front of the console hostname with an allow list equal to the invitation list. The application still does its own Google sign-in.
- Decided 2026-11-14: remote Proxmox/SSH access is through the operator's WireGuard VPN on the router only. The VPN is managed by the operator outside this project and is not part of this task.

## Goal
Document and reproducibly configure Edge/Core/Data/Worker VMs and PBS backup, with private inference reachability only if the optional inference host is deployed.

## Why now
Staging needs somewhere to run, the development worker needs an isolated host (R0-012), and backups are not proven until one restore has been performed.

## Context / linked docs / ADRs
- Edge cases added 2026-11-14 that this task must cover: E-062, E-084, E-085 ([register](../../docs/PROJECT_REAUDIT_2026-08-10.md)).
- [Physical and logical topology](../../docs/infrastructure/topology.md)
- [Ingress strategy](../../docs/infrastructure/ingress.md)
- [Internal networking and inference](../../docs/infrastructure/internal-networking-and-inference.md)
- [Network and service exposure](../../docs/security/network-and-service-exposure.md)
- [Backup and disaster recovery](../../docs/infrastructure/backup-disaster-recovery.md)
- Runbooks: [backup restore drill](../../docs/runbooks/backup-restore-drill.md), [tunnel to static origin](../../docs/runbooks/tunnel-to-static-origin.md), [static origin to tunnel](../../docs/runbooks/static-origin-to-tunnel.md)
- ADR-0006, ADR-0008, ADR-0009, ADR-0010, ADR-0027

## Depends on
- R0-001 (repository for infrastructure-as-code).

## Execution constraint
**This task is operator-executed.** Autonomous development agents never receive Proxmox, management-LAN or production credentials (ADR-0027, AGENTS.md). An agent may author infrastructure-as-code, configuration templates, checklists and verification scripts in the repository. A human applies them to the hosts and records the evidence.

## Invariants
- never publicly expose Proxmox, PostgreSQL, Redis, Temporal, OpenBao, the Docker API, ComfyUI, llama.cpp, voice model ports or worker debug ports;
- Cloudflare Tunnel is the default ingress; everything behind the Edge Gateway is identical under a future static-IP origin;
- control plane and tenant content use different registrable domains;
- no HA cluster; invest in UPS, backups and restore drills;
- prefer internal DNS names over hard-coded LAN addresses.

## In scope
- Four VMs on the Presence host: Edge (cloudflared, Caddy), Core, Data (PostgreSQL + pgvector, object storage), Worker.
- Network policy between VMs, the management network and the inference host, default-deny where practical.
- Cloudflare Tunnel terminating at Edge; Caddy routing one test control hostname.
- Private hostname for inference reachability from Core.
- Proxmox Backup Server on the backup host; scheduled VM backups; one recorded restore drill.
- Reproducible configuration in `infra/proxmox`, `infra/compose`, `infra/cloudflare`.
- UPS/clean-shutdown and disk-health monitoring noted as done or as a dated follow-up.

## Out of scope
- Encrypted offsite backup automation (design and owner recorded; implementation may follow).
- Static public IP migration (runbook exists; not executed).
- Private Inference/Voice Gateway service itself; R0 proves reachability only.
- Tenant wildcard zones and custom hostnames (R1-005, R1-006).
- Production OpenBao.

## API / contract changes
None at application level. Records the internal service names and ports that application configuration will reference.

## Data / migration
- No schema. Backup scope and schedule for the Data VM are defined.
- The PostgreSQL backup strategy (logical/physical) is chosen and written down.

## Security / privacy threat notes
- Management interface reachable from Worker or Edge.
- Tunnel credential or Cloudflare API token over-scoped: use narrowly scoped tokens, never a global key.
- Worker VM reaching private ranges: this is the host that runs untrusted code and development agents.
- Backup server holds everything: restrict access and keep recovery keys separate.
- Raw GPU model ports reachable from the LAN at large.

## Observability
- Host and VM health, disk/SMART/ZFS status, backup job success, tunnel status.
- Backup and restore results recorded with date, backup set, elapsed time, data-loss window, failures and remediation.

## Acceptance criteria
- Proxmox management private;
- Cloudflare Tunnel terminates at Edge;
- Caddy routes test control hostname;
- inference reached over private hostname;
- raw GPU model ports not public;
- Worker cannot reach management/private ranges unless explicitly allowed;
- PBS backup executes;
- one restore drill recorded;
- *(derived)* internal recovery objectives are written down and compared against the drill result;
- *(derived)* an external scan of the public surface shows no listening service other than what the tunnel publishes.

## Tests
Verification scripts, run by the operator, with output stored as evidence:
- from Worker: connection attempts to the management network, Proxmox, the Data VM database port and the inference host's raw ports all fail;
- from Core: inference private hostname resolves and responds;
- from the Internet: only the test control hostname responds;
- restore drill: a VM or database restored to a scratch target and verified.

## Rollback / failure recovery
VM snapshots before each configuration change. Tunnel and Caddy configuration versioned in the repository. Recovery from loss of the Presence host, the Data VM and the backup server is documented, even if only the Data VM restore is drilled in R0.

## Cost/resource budget
Existing hardware only. Record VM CPU/RAM/disk allocations and remaining headroom. Cloudflare usage stays within the plan confirmed at implementation time (pricing must be revalidated).

## Documentation updates
- `infra/*/README.md`, `docs/infrastructure/topology.md` (actual allocations and names).
- Restore drill record under `evidence/`.
- `docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`.

## Open decisions
- **Decided (ADR-0033):** Debian stable (ADR-0032).
- **Decided (ADR-0033):** internal names use `presence.internal`; separate Proxmox bridges with firewall rules for management, services and worker sandbox; VLANs when a managed switch is in use.
- **Decided (owner, 2026-11-15):** the console is `console.iamwaqargulzar.com` for the time being, so `iamwaqargulzar.com` is the control-plane registrable domain. The hostname is configuration.
- **Decision required:** the registrable domain for tenant content and previews; it must differ from `iamwaqargulzar.com`. Not needed for the test control hostname.
- **Decided (owner, 2026-11-15):** the interim second copy is an encrypted USB drive attached to the server. It does not count as offsite.
- **Decision required:** the cloud storage target for the offsite copy; required before the first client's data is held in production.

## Definition of done
Everything applicable in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: operator-signed evidence for each acceptance item, stored for R0-010.
