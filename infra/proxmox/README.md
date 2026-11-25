# Proxmox Infrastructure

Configuration for host A (Proxmox VE), the optional inference host B and the backups to host C (R0-009). Applied by the operator with `docs/runbooks/infrastructure-baseline.md`; layout and allowed flows in `docs/infrastructure/topology.md`. Proxmox management is never exposed publicly.

| File | Goes to |
|---|---|
| `interfaces.presence` | appended to `/etc/network/interfaces` on host A |
| `firewall/*.fw` | `/etc/pve/firewall/` on host A |
| `vms.sh` | run once as root on host A |
| `presence.internal.hosts` | appended to `/etc/hosts` on each VM |
| `inference-host.nft` | `/etc/nftables.conf` on host B |
| `scripts/pg-backup.sh` | `/usr/local/sbin/` on the Data VM, cron 01:30 |
| `scripts/verify.sh` | acceptance checks, run per role |

Addresses in `192.0.2.0/24` and `198.51.100.0/24` are documentation placeholders; real values are filled in on the host and never committed. `make test` runs the offline checks in `infra/tests/`.
