# Runbook — Infrastructure Baseline (R0-009)

The operator applies `infra/` to the real hardware with these steps. Nothing here is run from a coding environment. Fill the placeholders (`192.0.2.x`, `198.51.100.x`, `REPLACE`) on the host, not in the repository: the repository is public.

## Before you start

- Proxmox VE installed on host A, Proxmox Backup Server on host C, both reachable only from the LAN.
- Record the installed versions (`pveversion`, `proxmox-backup-manager versions`) in the evidence file.
- Fixed LAN addresses for host A and host B on the router; WireGuard range known.
- A copy of this repository on host A (for example `git clone` into `/root/presence-os`).

## 1. Network and firewall on host A

1. Append `infra/proxmox/interfaces.presence` to `/etc/network/interfaces`; run `ifreload -a`; check `ip -br a` shows `vmbr1` and `vmbr2`.
2. Copy `infra/proxmox/firewall/*.fw` to `/etc/pve/firewall/`. Replace the placeholders in `cluster.fw` with the management LAN, the WireGuard range and the inference host address.
3. Before enabling, open a second SSH session from the management set; then `pve-firewall compile` and `pve-firewall status`. If you are locked out, use the console and `pve-firewall stop`.
4. Check the web UI still opens from the LAN and from the VPN, and not from any other address.

## 2. Backup storage

1. On host C, create a datastore and a user with the `DatastoreBackup` role only on that datastore.
2. On host A: Datacenter → Storage → Add → Proxmox Backup Server, ID `pbs`, with host C's fingerprint and the user above, and Encryption set to auto-generate a key.
3. Copy the generated key (`/etc/pve/priv/storage/pbs.enc`) to the offline place you keep recovery keys (paper or encrypted USB kept away from the server). Without it no backup can be restored.
4. On host C, add a sync job or `proxmox-backup-client` copy to the encrypted USB drive (interim second copy).

## 3. VMs

1. Download the Debian 13 generic cloud image and its `SHA512SUMS` from `https://cloud.debian.org/images/cloud/trixie/latest/`; check the sum (`sha512sum -c --ignore-missing SHA512SUMS`); save it as `/var/lib/vz/template/debian-13-genericcloud-amd64.qcow2`.
2. `SSH_KEYS=/root/operator.pub infra/proxmox/vms.sh`, then start the VMs.
3. On every VM: `apt install qemu-guest-agent`, append `infra/proxmox/presence.internal.hosts` to `/etc/hosts` (set the inference address), enable unattended security upgrades.
4. Data VM: install PostgreSQL, copy `infra/proxmox/scripts/pg-backup.sh` to `/usr/local/sbin/`, cron `30 1 * * * root /usr/local/sbin/pg-backup.sh`. Run it once by hand.

## 4. Edge and tunnel

Follow `infra/cloudflare/README.md`, then on the Edge VM: install Docker, copy `infra/compose` and `infra/cloudflare`, create `edge.env` from `edge.env.example`, `docker compose -f edge.compose.yaml --env-file edge.env up -d`. Check `ss -tlnp` shows only `127.0.0.1:8080` and SSH.

## 5. Inference host (only when used)

Install `infra/proxmox/inference-host.nft` as `/etc/nftables.conf` with the placeholders filled; `nft -c -f /etc/nftables.conf`, then `systemctl enable --now nftables`. Bind llama.cpp, ComfyUI and voice services to `127.0.0.1`.

## 6. Power, disks and alerts (E-085)

- UPS: install Network UPS Tools on host A; on low battery shut down the VMs (`onboot` brings them back) and the host. Test once by pulling mains power with the UPS attached.
- Disks: `zpool scrub` monthly (the Proxmox default cron), `smartd` enabled; mail or push notifications configured in Proxmox (Datacenter → Notifications) for backup failures, ZFS and SMART events.
- A lost phone with VPN access: revoke its WireGuard peer on the router and its Google session; nothing else to change.

## 7. Acceptance and evidence

Run `infra/proxmox/scripts/verify.sh` with the variables it lists:

1. `verify.sh worker` on the Worker VM.
2. `verify.sh core` on the Core VM, once with host B on and once with `INFERENCE_OFF=1` and host B off (E-062).
3. `verify.sh internet` from outside the site (a phone hotspot). Optionally an `nmap -Pn` of the public address from the same place.
4. One restore drill (`docs/runbooks/backup-restore-drill.md`), recorded in `evidence/R0/R0-009/restore-drill.md`.

Paste the outputs into `evidence/R0/R0-009/` with the hostnames and addresses redacted.

## Rollback

`pve-firewall stop`; remove the appended block from `/etc/network/interfaces` and `ifreload -a`; `qm destroy` the VMs; `pvesh delete /cluster/backup/presence-nightly`; `docker compose down` on the Edge VM and delete the tunnel in Cloudflare.
