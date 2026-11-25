# ADR-0032 — Toolchain Versions, Package Managers and Repository
Status: Accepted (2026-11-14). The owner delegated the choice: "using the latest of whatever is needed."

## Context
R0-001 was blocked by three decisions: repository hosting and CI, the supported Python, Node and PostgreSQL versions, and the package managers. The owner asked for the latest versions and left the detail to the development process.

## Decision

### 1. Version rule
Use **the newest stable release that every required dependency supports**. This is "latest" with one safety condition:
- stable releases only: no beta, release candidate or preview;
- where a project has long-term-support lines (Node.js), use the newest LTS line;
- if one required dependency does not yet support the newest release, use the newest release it does support, and record the reason in the R0-001 implementation report;
- exact versions are pinned in the repository (version files and lockfiles) and change only through a reviewed commit.

### 2. Targets on 2026-11-14
Versions were checked by web search on this date. R0-001 confirms each one against the official site before pinning.

| Component | Target | Note |
|---|---|---|
| Python | 3.15.x | Released 2026-10-09. Fall back to 3.14 only if a required package (for example the Temporal SDK or the PostgreSQL driver) has no 3.15 build yet. |
| Django | 6.1.x | Supports Python 3.12 to 3.15 and PostgreSQL 15 and higher. Move to 6.2 (the next long-term-support release) when it is out. |
| Node.js | newest LTS line | Expected to be 26. If 26 is not yet marked LTS, use 24. |
| Next.js | 16.x | The current stable major. |
| TypeScript | newest stable, strict mode | |
| PostgreSQL | 18.x | 19 was still a release candidate. Move to 19 after its first minor update and after pgvector supports it. |
| pgvector | newest stable for the PostgreSQL version | |
| Redis, Temporal server, Caddy, cloudflared | newest stable | Container images pinned by digest. |
| VM operating system | Debian stable | Unattended security updates on. |
| Container base images | official slim images, pinned by digest | |

### 3. Package managers
- **Python: uv.** One lockfile (`uv.lock`), fast, and it also installs the pinned Python version.
- **Node: pnpm,** enabled through Corepack with the version pinned in `package.json`.
- **No monorepo task runner.** A plain `Makefile` (or `just`) holds the gate commands. Add a task runner only if build times justify it later.

### 4. Repository and CI
- **Private GitHub repository** under the owner's account, with **GitHub Actions** for CI. Chosen because the owner's Git identity is already a GitHub account.
- CI holds no production secrets and has no route to the management network.
- This point was not stated by the owner. It is the default and can be changed before the first push without affecting anything else in this ADR.

### 5. Keeping versions current
- An automated update tool (Dependabot or Renovate) opens update proposals; each one passes the normal gates.
- Security patches are applied promptly. Major version upgrades are a reviewed change with a rollback note.
- Every new dependency still passes the licence, security, maintenance and duplication review required by `AGENTS.md`.

## Consequences
- R0-001 has no blocking decisions left.
- Python 3.15 is five weeks old on the decision date, so the fallback rule in point 1 may apply to it.
- Django 6.1 is not a long-term-support release; an upgrade to 6.2 is expected in 2027.

## Alternatives considered
- **Always the newest release, with no condition.** Rejected: one unsupported dependency would block the build.
- **Only long-term-support versions everywhere.** Rejected: the owner asked for the latest, and the update process above keeps the risk low.
- **Self-hosted Git (Forgejo/Gitea) on Proxmox.** Possible later; it is another service to maintain, which conflicts with the wish to manage fewer projects.
