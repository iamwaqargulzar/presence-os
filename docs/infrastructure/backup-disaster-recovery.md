# Backup, Disaster Recovery, RPO/RTO

## Minimum backup layers

1. PostgreSQL logical/physical strategy appropriate to scale.
2. VM/config backups to Proxmox Backup Server.
3. Object storage replication/backup.
4. OpenBao/secrets recovery procedure and keys handled separately.
5. Encrypted offsite copy.
6. Git/source + infrastructure-as-code remote repository.

## Backups are not proven until restored

Run restore drills.

Record:
- restore date;
- backup set;
- elapsed time;
- data loss window;
- failures;
- remediation.

## Initial target philosophy

Do not invent contractual enterprise RPO/RTO numbers before measuring restore capability.

R0 should define internal recovery objectives, then validate them with drills before publishing commitments.

## R0 strategy and internal objectives (R0-009)

- PostgreSQL: nightly `pg_dump -Fc` per database plus globals at 01:30 on the Data VM (`infra/proxmox/scripts/pg-backup.sh`), kept 7 days on the VM.
- VMs: nightly Proxmox Backup Server snapshot of all four VMs at 02:30, with the guest agent freezing file systems; keep 7 daily, 4 weekly, 6 monthly. PBS client-side encryption is on; the key is kept offline by the operator, not on host A or C.
- Second copy: PBS sync to the encrypted USB drive (interim, not offsite; see the Decision Register). Replaced by the cloud target before the first client's production data.
- Object storage is inside the Data VM snapshot until R0-011 sets a separate policy.

Internal objectives, not commitments; compare each restore drill against them:

| Scope | RPO | RTO |
|---|---|---|
| Data VM (database and objects) | 24 h | 4 h |
| Whole host A rebuilt on replacement hardware | 24 h | 1 working day |
| Inference host | none (no state) | none (cloud-only fallback) |

Upgrade before the first client's production data: WAL archiving for point-in-time recovery (RPO minutes) and the offsite copy.

On site loss (E-084) the offsite copy, this repository and the PBS encryption key are enough to rebuild: install Proxmox, apply `infra/`, restore the VMs from PBS. On power loss (E-085) the UPS signals a clean shutdown of the VMs and the host (`docs/runbooks/infrastructure-baseline.md`).

## Failure cases

Document recovery from:
- Presence host loss;
- Data VM corruption;
- accidental tenant deletion;
- bad migration;
- ransomware;
- secrets-store loss;
- inference host loss;
- Cloudflare/Tunnel failure;
- backup server loss.

Inference outage should degrade local AI/media capability and permit configured cloud fallback, not corrupt tenant truth.
