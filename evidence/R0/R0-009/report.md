# Implementation Report — R0-009 Proxmox, Network and Backup Baseline

Written 2026-11-25. Spec: [R0-009](../../../specs/R0/R0-009-infrastructure-baseline.md). Runbook: [infrastructure baseline](../../../docs/runbooks/infrastructure-baseline.md).

- Starting commit: `1f5d8a4` (docs(R0-002): record public repository and branch protection on main), on `feat/R0-002-ci-environments`.
- Resulting commit: the head of branch `feat/R0-009-infrastructure-baseline`. It contains this report, so it cannot name its own hash.
- Execution profile: side session started by the operator's main session while the owner was away; no controller yet (R0-011).
- Harness: Claude Code, desktop app.
- Model: Claude Opus 5.5 (`claude-opus-5-5`).
- Reasoning: default for the session.
- Task/spec hash: sha256 `8627aa86830baefba99e2c359e91672de9a2c480ab9a627b4e30847d7aab8ac8` of `specs/R0/R0-009-infrastructure-baseline.md` (revision 3).
- Changed files: new `infra/proxmox/` (firewall files, bridges, hosts, `vms.sh`, `inference-host.nft`, `scripts/pg-backup.sh`, `scripts/verify.sh`), `infra/compose/` (edge compose, Caddyfile, env example), `infra/cloudflare/cloudflared.yml`, `infra/tests/test_infra.py`, the three `infra/*/README.md`, `docs/runbooks/infrastructure-baseline.md`, this folder. One line added to the `Makefile` `test` target.
- Migrations: none.
- Rollback: revert the branch. Nothing was applied to any host; the runbook has its own rollback section for when the owner applies it.

## Versions (checked against official sources on 2026-11-25)
Sources: GitHub releases API for the projects, `docker buildx imagetools inspect` for digests, Debian release page.

| Item | Pinned | Note |
|---|---|---|
| cloudflared | 2026.11.2, digest `sha256:55c7e3e8…3af6` | newest release (2026-11-23) |
| Caddy | 2.11.9-alpine, digest `sha256:003a9780…f0` | newest release (2026-11-05) |
| Debian (VM image) | 13 "trixie" (13.8 current) | image checksum checked by the operator at download (runbook step 3) |
| Proxmox VE, PBS | not pinned | the installed version is recorded by the owner (assumption: VE 9, PBS 4) |

## Dependencies (review)
No package dependency added. Two container images are used on the Edge VM only.

| Item | Licence | Maintenance | Why needed / duplication |
|---|---|---|---|
| cloudflared (image) | Apache-2.0 | Cloudflare, releases monthly | the tunnel ingress chosen in ADR-0006; nothing else in the repo does this |
| Caddy (image) | Apache-2.0 | active, release 2026-11-05 | the origin router named in ADR-0006 |

Both run with host networking because Caddy must reach `core.presence.internal` and cloudflared must reach Caddy on 127.0.0.1; neither publishes a port or mounts the Docker socket. Caddy's admin API is off.

## Tests
- `make check` passes, including 12 new offline tests in `infra/tests/test_infra.py`: default-drop policies on every VM and the cluster, every inbound accept names a source, SSH only from the Proxmox host, private ranges dropped before general egress, the Worker's first outbound rule drops all private ranges, only Core reaches Data and the inference host, every VM NIC has the firewall on, the inference host drops by default and never opens the raw model ports, the edge publishes no ports and pins images by digest, Caddy binds to 127.0.0.1 with the admin API off and a 404 catch-all, the tunnel sends everything to Caddy.
- Validated with the real tools: `docker compose config -q` (edge compose), `caddy validate` 2.11.9 (Caddyfile), `cloudflared tunnel ingress validate` and `ingress rule` 2026.11.2, `nft -c` in an unprivileged namespace (inference host rules), `bash -n` on all scripts. Not wired into `make`: they need Docker and the images; the offline tests guard the exposure rules.
- `python3 tools/build_docs.py`: `links: ok`.

## Security checks
- No real address, hostname or key in the repository: LAN values are documentation ranges (`192.0.2.0/24`, `198.51.100.0/24`) to be replaced on the host; the internal 10.77.x ranges are private. The only real names are the already public `console.iamwaqargulzar.com` and the proposed `edge-test.iamwaqargulzar.com`.
- Tunnel credentials stay in a root-only file on the Edge VM; `edge.env` is ignored by `.gitignore`.
- Proxmox (8006, SSH) open only to the management set; PostgreSQL and object storage only to Core; inference raw ports bound to localhost and closed in nftables; no Docker socket mounted; nothing listens on the Edge VM's LAN side.
- The Worker cannot reach the management LAN, the router, the Proxmox host, the Data VM or the inference host.
- Nothing was connected to or applied on a real host.
- Secret scan: none of this branch's commits used `--no-verify`. The pre-commit hook ran on commits `1bc2536` and `d8f5b24`, but its gitleaks container could not read the worktree's `.git`. It printed "not a git repository", scanned 0 commits and still passed, so those two commits were not really scanned. After merging the R0-002 fix (`f208a1c`), which mounts the shared `.git`, `make scan-secrets` scanned all 9 commits of HEAD's history and found no leaks. `make check` and `tools/gate_selftest.sh` also pass. The self-test confirms that `scan-staged` rejects a seeded credential in this worktree. This report's commit was the first one the hook really scanned.

## Acceptance criteria
| Criterion | Result |
|---|---|
| Worker cannot reach management, Proxmox, Data database port, inference raw ports | rules written and tested offline; `verify.sh worker` on hardware: **owner** |
| Core resolves and reaches the inference hostname | rules and hosts file written; `verify.sh core`: **owner** |
| From the Internet only the test hostname answers; console gives only the sign-in redirect | edge config validated; Access set-up in `infra/cloudflare/README.md`; `verify.sh internet`: **owner** |
| One restore drill recorded | template `restore-drill.md`; drill: **owner** |
| Recovery objectives written and compared with the drill | objectives in `docs/infrastructure/backup-disaster-recovery.md`; comparison after the drill: **owner** |
| External scan shows nothing else listening | `verify.sh internet` port loop, optional `nmap`: **owner** |
| All of the above with the inference host off (E-062) | `verify.sh core` with `INFERENCE_OFF=1`: **owner** |
| Site loss (E-084), outage (E-085) | rebuild path and UPS/clean shutdown in the backup doc and runbook; UPS test: **owner** |

## Still needs the owner on real hardware
1. Fill the placeholders and apply runbook steps 1–6 on hosts A, B (optional) and C.
2. Store the PBS encryption key offline.
3. Create the tunnel, DNS records and the Cloudflare Access application.
4. Run `verify.sh worker`, `core` (inference on and off) and `internet`; paste redacted output here.
5. Run one restore drill and fill `restore-drill.md`; compare with the objectives.
6. Pull mains power once to test the UPS shutdown.
7. Confirm or correct the assumptions in `docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md` (R0-009 section), especially the VM sizes and address ranges.

## Reviewer
No independent review yet. This change defines the network boundary, so the owner should review the firewall files and the topology table before applying them.

## Cost/tokens/cache
Not measured; the desktop session does not expose usage to the worker. No paid service used.

## Known limitations
- `shortcut:` nightly dump gives RPO 24 h; WAL archiving is needed before the first client's production data.
- `shortcut:` internal names come from a hosts file; move to router DNS when more hosts need names.
- The Worker's egress to the Internet is open; R0-012 narrows it.
- The inference gateway port (8443) is a placeholder until the gateway is built.
- No ADR added, to avoid a number clash with sessions running in parallel; the decisions are in the Decision Register under Infrastructure and Backups.

## Docs updated
`infra/*/README.md`, `docs/infrastructure/topology.md`, `docs/infrastructure/backup-disaster-recovery.md`, `docs/runbooks/backup-restore-drill.md`, new `docs/runbooks/infrastructure-baseline.md`, `docs/DECISION_REGISTER.md`, `docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`, `CHANGELOG.md`.
