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
