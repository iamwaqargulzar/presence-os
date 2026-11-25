# Decision Register

> **Presence OS engineering source of truth**
>
> Current as of **2026-11-14** (Asia/Karachi project context). First baseline: 2026-08-08.
> This register lists decisions in force. Accepted ADRs contain rationale and consequences. Decisions that were reversed are not listed here; see the ADRs and `docs/archive/`.

## Operating model (ADR-0030)
- Presence OS is run by one operator for their own companies and managed clients. It is not sold as a product.
- No signup, plans, subscriptions, seats, invoices or payment processing.
- Each company or client is a tenant. The operator creates tenants.
- R3 is the first release used for real client work.

## Product
- Business presence first; individual/professional later.
- Conversation/voice-first, not voice-only.
- Agent Home default after login.
- The operator console is mobile-first: task requests, scheduling, reports, approvals, deploy/modify.
- UI visual style remains revisable; avoid stereotypical AI-slop aesthetics.

## Identity/tenancy
- Login belongs to a Person. Sign-in is Google sign-in only, by invitation; no passwords are stored.
- Platform authority and tenant authority are separate.
- The operator acts in each tenant through an explicit, audited `MANAGED_SERVICE` TenantAccessGrant.
- Client roles: viewer, requester, approver. No client role can start AI work; a client request creates a queue item.
- Clients connect their own external accounts on the platforms' official consent pages and can disconnect them.

## Authority/security
- LLM cannot mint authority.
- Action Broker is the sole external side-effect boundary.
- Explicit implementation request by an authorized user counts as approval within scope.
- High-risk actions still require consequence-specific confirmation.
- Outcome-bound and artifact-bound authorization supported; client approval is artifact-bound.
- External content is untrusted data, not control.
- Fetch Broker and file quarantine are first-class.
- OpenBao/equivalent secrets boundary before client data is live.

## Data
- PostgreSQL shared DB + tenant_id + RLS.
- runtime DB role does not own tables / BYPASSRLS.
- external observations become Candidate Facts before canonical truth.
- FACT/PREFERENCE/DECISION/CONVERSATION_SUMMARY/TASK_STATE are distinct.
- score formulas versioned.
- AI visibility measured stochastically over repeated query/provider/location/language samples.

## Limits and budgets
- Versioned per-tenant limits set by the operator.
- Tenant budget and global budget, in money; reserve then settle, atomically.
- Append-only usage ledger; cost report per tenant.
- Cost Governor and Resource Governor are separate.

## Infrastructure
- Proxmox on the Presence host; 4-VM layout: Edge/Core/Data/Worker.
- Backup server runs Proxmox Backup Server.
- The inference GPU server is optional and may stay off.
- Cloudflare Tunnel is the default ingress; a tested migration to a static public IP is kept.
- Operator console on its own control-plane hostname through the tunnel.
- Proxmox and SSH: local network or the operator's WireGuard VPN on the router; never published. The VPN is managed outside this project.
- No HA cluster; invest in UPS, backups and restore drills.

## Domains
- control plane and client-generated content use different registrable domains.
- randomized collision-resistant canonical platform hostname for every property.
- optional vanity hostname, assigned by the operator, availability/reserved-name checked.
- custom domain optional.
- wildcard platform DNS preferred so random/vanity creation is mostly database routing.
- random preview identifiers; noindex; authentication when sensitive.

## Stack
- Next.js/TypeScript, Django/Python, PostgreSQL/pgvector, Temporal, Redis, S3-compatible object storage, Docker/Compose, Playwright, gVisor, Cloudflare Tunnel/Caddy, OpenTelemetry.
- modular monolith; no Kubernetes/Kafka/graph DB/separate vector DB initially.

## AI
- AI Capability Gateway; no module imports a vendor SDK directly.
- Routing is CLOUD_ONLY by default; local modes only when the GPU host is on.
- Task-class routing: frontier profile for planning, architecture, security-sensitive work and review; low-cost API profile (intended: DeepSeek) for high-volume, machine-checkable work.
- Credential class on every profile: `OPERATOR_SUBSCRIPTION` only for operator-started or approved runs through an official harness on the Worker VM; `API` for scheduled and unattended runs.
- Each tenant has one stable logical Presence AI identity, independent of the model.
- Tenant provider policy is a hard filter.
- Model resolution: bounded run override → tenant override → platform default; the profile revision is pinned per run/session.
- A default model change is versioned, previewed, audited and can be rolled back; tenant overrides are preserved.
- Context Compiler prevents full-history resend.

## Build preference
- Product features are written in Presence OS for full control.
- Other open-source applications are studied for ideas, not deployed, and nothing is copied from them.
- Proven infrastructure and libraries are used as they are, each after the dependency review in AGENTS.md.
- Social platform connectors are built in-house, one platform at a time (ADR-0031).
- Connector order: Meta (Facebook Pages and Instagram), then LinkedIn company pages.

## Hosting
- A tenant can own multiple DigitalProperties (websites, apps, portals, landing properties).
- DigitalProperty owns environments/deployments/hostname attachments/resource attribution; one-tenant-one-site is forbidden as a data-model assumption.

## Autonomous development
- Execution Profile = model × harness × reasoning × context/cache strategy.
- OpenHands-backed DevelopmentController is the initial control plane; deterministic orchestration uses zero LLM calls by default.
- Workers: Prime Agent (Presence-owned RPC/process adapter) and Claude Code through the Claude Agent SDK. Primary worker is an open decision. Codex/OpenCode/Oh My Pi/ReasoniX remain replaceable fallback entries.
- Controller, worker parent, worker children/reviewer and build/tool usage are metered separately.
- Development agents have no production secrets or management-network reachability.
- task/spec hash + start commit + execution/sandbox/gate profile revisions are pinned per DevelopmentRun.
- PresenceBench qualifies profiles on real tasks; current models are candidates, never permanent.
- development autonomy to staging; the operator authorizes production.

## Domains
- Operator console: `console.iamwaqargulzar.com`, for the time being. The hostname is configuration and can be moved.
- `iamwaqargulzar.com` is therefore the control-plane registrable domain; nothing tenant-generated is served under it (ADR-0008).
- The domain for hosted client sites and previews is a different registrable domain, not chosen yet.

## Backups
- Interim second copy: an encrypted USB drive attached to the server. It is not an offsite copy.
- A cloud storage target replaces it before the first client's data is held in production.
- The drive is encrypted, and a restore from it is tested like any other backup.

## Personal profile
- The operator's personal presence is its own tenant, separate from every company.
- It uses the operator-owned budget cap and its own brand voice and connected accounts.

## Technical defaults
- The model gateway is built in-house with one adapter per provider (owner decision).
- All other R0 and R1 technical defaults are in ADR-0033: workers, sandbox limits, database context, sign-in library, Temporal, observability, object storage, secrets, Cloudflare Access, grant lifetimes, hostname format, connection health, data classes.

## Clients without a Google account
- The client creates a Google account on their existing email address.
- Otherwise the client has no login; the operator records the client's approval on their behalf, marked as operator-attested, with evidence (for example the client's email) attached.
- No second sign-in provider for now.

## Ending service
- A client cannot revoke or pause the operator's access; the operator ends service from the console at the client's request.
- A client can view the operator's access and disconnect their own connected accounts.

## Budgets
- Accounting currency: US dollars. Rupee amounts are shown beside them for reading only, at an operator-set rate.
- Starting caps: USD 20 per client, USD 30 per operator-owned company, USD 150 across all tenants, per month; warning at 80%.
- Subscriptions are a fixed cost, reported separately and not counted against caps.

## Low-cost model
- Current choice: DeepSeek V4.1 Flash. It is a dated choice, not a commitment; models change every few weeks and are swapped by configuration (R1-013).
- Default provider is DeepSeek's own service; a client's provider policy can require a US or EU host instead.
- A new client's default policy allows only low-risk public material to reach the low-cost profile.

## Scheduling
- A scheduled task prepares its work and waits for the operator's approval by default.
- The operator may mark a specific low-risk task as unattended; it runs on an API profile, never on the subscription (E-061, E-078).
- A task that posts, sends or deploys always waits for approval (E-092).

## Mobile
- The operator console is a web app installable on the phone, with push notifications.
- Notifications carry a short summary and a link to the exact item; approval happens only inside the signed-in console.
- A chat channel is a possible later addition for notifications only.

## Toolchain
- Versions: the newest stable release that every required dependency supports; pinned in the repository (ADR-0032).
- Package managers: uv (Python), pnpm (Node). No monorepo task runner.
- Repository: private GitHub with GitHub Actions (default; the owner may change it before the first push).
- Pinned on 2026-11-25 (R0-001): Python 3.15.2, Node 26.13.1 LTS, Django 6.1.3, Next.js 16.4.6, TypeScript 7.0.2, uv 0.13.10, pnpm 12.23.0. Exact pins live in `.python-version`, `pyproject.toml`, `uv.lock`, `apps/web/package.json` and `apps/web/pnpm-lock.yaml`.
- Node and pnpm are pinned through `packageManager` and `devEngines`, without Corepack; pnpm's one-day release cooldown stays on (ADR-0034).
- Gate tools: ruff, mypy, Biome, `tsc`, Django test runner, `unittest`, `node:test`, gitleaks, `uv audit`, `pnpm audit`. Gate commands are `make` targets (ADR-0034, `docs/delivery/gates.md`).

## Delivery
- R0 Foundation → R1 Kernel → R2 Intelligence → R3 Business Presence → R4 Growth Ops → R5 Expansion.
- Gates are listed in `docs/delivery/gates.md`.
