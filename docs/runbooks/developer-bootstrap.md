# Developer Bootstrap

Current as of 2026-11-25 (R0-002). Takes a new Linux machine from a clean clone to green gates. Tested from a clean clone on 2026-11-25 (R0-001).

## 1. Install once per machine
| Tool | Why | How |
|---|---|---|
| Git, GNU Make | clone and gate commands | system package manager |
| uv 0.13.10 | installs Python 3.15.2 and the Python packages | [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/); then `uv self update 0.13.10` |
| pnpm (any 10.x or newer) | installs Node 26.13.1 and the web packages | [pnpm installation guide](https://pnpm.io/installation) |
| Docker with Compose | runs PostgreSQL for integration tests and the pinned gitleaks secret scanner | Docker Engine; your user must be able to run `docker` |

You do not install Python or Node yourself. uv reads `.python-version`; pnpm reads `packageManager` and `devEngines` in `apps/web/package.json` and downloads the exact pinned versions. Node 26 no longer ships Corepack (ADR-0034).

## 2. Set up the clone
```bash
git clone https://github.com/iamwaqargulzar/presence-os.git
cd presence-os
make bootstrap
cp .env.example .env
```
`make bootstrap` installs both lockfiles exactly (`--locked`, `--frozen-lockfile`) and turns on the pre-commit secret scan (`git config core.hooksPath .githooks`).

Edit `.env` and set `PRESENCE_SECRET_KEY`, `PRESENCE_DB_PASSWORD`, `PRESENCE_DB_MIGRATOR_PASSWORD` and `PRESENCE_DB_APP_PASSWORD`, each to its own output of:
```bash
uv run python -c "import secrets; print(secrets.token_urlsafe(50))"
```
`.env` is ignored by Git. Never commit it.

Django connects as two roles ([database tenancy](../security/database-tenancy-rls.md)): `make services-up` creates them. Run migrations as the owner role: `uv run python apps/core/manage.py migrate --database migrator`. If your PostgreSQL volume predates R0-003, run `make services-up` once more, or reset it with `docker compose down -v`.

## 3. Check everything
```bash
make check
make test-integration
make audit
make scan-secrets
tools/gate_selftest.sh
```
All five must exit 0. `make test-integration` starts PostgreSQL from `compose.yaml` on 127.0.0.1:15432 (change `PRESENCE_DB_PORT` in `.env` if that port is taken); `make services-down` stops it. `python3 tools/ci_run.py` runs everything exactly as CI does and writes `reports/ci-result.json`. The gate names are listed in [gates.md](../delivery/gates.md).

## 4. Start the apps
- `make dev-core`: Django on http://127.0.0.1:8000/healthz returns `{"status": "ok"}`.
- `make dev-web`: Next.js on http://127.0.0.1:3000/ shows the placeholder page.

Both bind to 127.0.0.1 only. Both print one JSON log line per request with a `request_id`, and return it in the `X-Request-ID` header.

## Troubleshooting
- `Required uv version ... does not match`: run `uv self update 0.13.10`.
- pnpm refuses a package "within the minimumReleaseAge cutoff": the package is less than a day old. Pin the previous release; do not add an exception without a review (ADR-0034).
- `make scan-staged` or a commit fails with a Docker error: Docker is not running or your user cannot use it. The hook fails closed on purpose.
