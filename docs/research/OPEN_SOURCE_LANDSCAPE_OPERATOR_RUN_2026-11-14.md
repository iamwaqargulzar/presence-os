# Open-Source Landscape for the Operator-Run Model — 2026-11-14

Dated reference only. It does not change any ADR. It adds to [GITHUB_LANDSCAPE_2026-11-10.md](GITHUB_LANDSCAPE_2026-11-10.md), which was written before [ADR-0030](../adrs/ADR-0030-operator-run-agency-deployment.md).

**Question.** After ADR-0030, Presence OS is one operator managing their own companies and clients from a phone: reports, approvals, "do this task", scheduling, deploys, client requests, and social posting on a client's behalf. Does an open-source project already do this?

**Method.** 18 web searches on 2026-11-14. Results came from project pages, package registries and directory sites. **No repository was opened and no code was read, except AgenticOS (section 4a).** Star counts and licences below are second-hand; several sources disagreed. Check the `LICENSE` file of any project before reading its code closely.

**Labels** follow the build preference: **Study** means read for ideas, deploy nothing, copy nothing. **Library** means a candidate dependency, subject to dependency review. **Avoid reading code** marks copyleft or restricted licences where only the public documentation and behaviour should be studied.

## 1. Answer

**No open-source project covers the whole objective.** Nothing found combines tenant isolation per client, an authority-checked action path, a mobile operator console, client request and approval roles, websites, and social posting.

The objective is covered in five separate pieces by different projects. Each piece has at least one mature reference. That supports the current plan: build the product in-house, and use these projects as worked examples.

## 2. Remote control of coding agents from a phone

This is the "worker like T3 Code" part (ADR-0030 decision 6, R0-011).

| Project | Licence (reported) | Label | What to take from it |
|---|---|---|---|
| [pingdotgg/t3code](https://github.com/pingdotgg/t3code) | MIT | Study | The stated reference. Server runs on the machine with the code; web, desktop and mobile clients connect to it. Drives the official Claude Code and Codex harnesses rather than logging in itself. |
| [slopus/happy](https://github.com/slopus/happy) | MIT | Study | Mobile and web client for Claude Code and Codex. Push notification when the agent needs a permission or fails. |
| [happier-dev/happier](https://github.com/happier-dev/happier) | MIT | Study | Fork of Happy. Approvals are kept in a durable inbox; a notification opens the exact session. Self-hosted relay. Alpha quality. |
| [kzahel/yepanywhere](https://github.com/kzahel/yepanywhere) | MIT | Study | Mobile-first web UI for Claude Code and Codex. |
| Codeman | MIT | Study | Keeps agent sessions running all day in tmux and shows them from any device. |
| [siteboon/claudecodeui](https://github.com/siteboon/claudecodeui) (CloudCLI) | AGPL-3.0 | Avoid reading code | Web UI over Claude Code using the operator's own subscription. |
| [BloopAI/vibe-kanban](https://github.com/BloopAI/vibe-kanban) | Apache-2.0 | Study | Already listed on 2026-11-10. Task board, one worktree per task, review step. |
| [multica-ai/multica](https://github.com/multica-ai/multica) | Apache-2.0 plus extra conditions | Avoid reading code | Assign issues to coding agents like teammates. The licence forbids offering it as a managed service to others. |
| Claude Code Remote Control and cloud scheduled tasks | Not open source | Note | Anthropic's own feature now lets a phone watch and steer a session, and runs scheduled tasks. One project in this space (MobileCode) was archived when it launched. |

**What this means.**
- The pattern Presence OS chose is the common one: a server process next to the code, the official harness underneath, a thin client on the phone. No change needed.
- The two ideas worth copying as designs are Happier's **durable approval inbox with deep links** and Happy's **push on "needs permission" and on failure**. Both belong in the R2/R3 console specs.
- None of these has tenants, budgets, provider policy, or an authority check. They assume one trusted user and one machine. Presence OS still needs its own DevelopmentController and Action Broker.
- Anthropic's own Remote Control covers "check my coding agent from my phone" with no code written. It does not cover clients, tenants or social posting, so it does not replace the console. It is a useful fallback while the console is being built.
- Subscription and Agent SDK billing terms were not confirmed by today's searches. Recheck them at R0-007 and R0-011, as the specs already require.

## 3. Personal assistant with scheduling

This is the "schedule my daily tasks, ask it to do things" part.

| Project | Licence (reported) | Label | What to take from it |
|---|---|---|---|
| [openclaw/openclaw](https://github.com/openclaw/openclaw) | MIT (one source says Apache-2.0) | Study | The largest project of this kind. A gateway process that routes one or more agents across chat channels. Scheduler ("Automations", formerly cron) runs inside the gateway, not inside the model. Only an admin scope may add, edit or run a schedule. |
| Hermes Agent (Nous Research) | MIT | Study | CLI, messaging gateway, plugins. Skills written and refined by the agent itself. |
| NanoClaw | MIT | Study | Small codebase, one container per agent. Easier to read than OpenClaw. |

**What this means.**
- OpenClaw's rule that **the scheduler is deterministic code and a schedule change needs admin authority** matches Presence OS (Temporal schedules, operator authority, edge cases E-078 and E-079).
- One OpenClaw detail is a warning: its exec approvals **do not apply to commands run by a schedule**. In Presence OS a scheduled run must pass the same Action Broker checks as any other run. This is already an invariant; it is now recorded as edge case E-092.
- OpenClaw's 2026 security history is the main lesson. Reports describe about 1,800 instances exposed to the internet leaking keys, a one-click remote code execution through a stolen gateway token, and backdoored skills in its marketplace. Presence OS already answers most of this by design: no admin port is public and sign-in is Google-only by invitation. The remaining two are recorded as E-093 (stolen session) and E-094 (hostile skill pack).
- Hermes-style self-written skills conflict with the rule that a worker may not silently change its own instructions. Do not adopt that behaviour.

## 4. Multi-tenant agent platforms and "AI company" tools

| Project | Licence (reported) | Label | What to take from it |
|---|---|---|---|
| [paperclipai/paperclip](https://github.com/paperclipai/paperclip) | MIT | Study | Already listed. Org chart, budgets, governance, heartbeat for agents. |
| [vstorm-co/agenticos](https://github.com/vstorm-co/agenticos) | Apache-2.0 (confirmed from the licence file) | Study | Read directly; see section 4a. Organisations as tenants, a monthly budget checked **before** each model request, an approval gate around every tool, schedules, a phone app, and Claude Code or Codex as a coding worker. |
| [sarrazola/openlivery](https://github.com/sarrazola/openlivery) | MIT | Study | Closest to the agency shape: one installation, a separate workspace and branded portal per client. Scope is chat agents (WhatsApp, web widget) only. Very small. |
| [byteworthy/sovra](https://github.com/byteworthy/sovra) | not confirmed | Study | Multi-tenant agent application base aimed at agencies. |
| [crewform/crewform](https://github.com/crewform/crewform) | not confirmed | Study | Dispatch task, review result, ship to client. |

**What this means.** AgenticOS is the one to read before R1-003, R1-004 and R1-012 are implemented. Details follow.

### 4a. AgenticOS, read directly

Unlike the rest of this survey, this section is based on the repository itself, read on 2026-11-14 through the GitHub API: metadata, licence file, README, file tree, `docs/security.md`, `docs/architecture.md`, `docs/triggers.md`, the organisation model, and the design notes for the budget, approval and coding-agent capabilities. The code was not run and no security review was done.

**Corrections to what the web search said**
- Licence is plain Apache-2.0 (standard 202-line text, plus a NOTICE file). No open-core split was found in the repository. The name and logo are excluded.
- Tenant isolation is **not** at the database schema level. It is done in application code: each row has an `organization_id` and a service (`resolve_access`) refuses a mismatch. No PostgreSQL row-level security was found.
- About 270 stars and 52 forks, not about 100.

**Facts**

| Item | Finding |
|---|---|
| Age and pace | Created 2026-07-31. Release v1.74.0 on the day of reading; three releases in two days. About 10,500 files and over 320 database migrations. |
| People | One author has about 1,220 of roughly 1,500 commits. Maintained by the company Vstorm. |
| Stack | FastAPI, Pydantic AI, PostgreSQL with pgvector, Redis, Next.js, Docker Compose. Desktop and phone apps built with Tauri. |
| Purpose | An internal AI agent layer for **one company**: departments share agents in chat, Slack, Teams and similar. |
| Tenant unit | Organisation, with six roles (Owner, Admin, Builder, Operator, Member, Viewer). |
| Sign-in | Email and password, magic links, Google, OIDC, LDAP, Kerberos. No built-in multi-factor step. |
| Budgets | Monthly limit per agent, per group and per organisation. A new organisation starts with a default cap. |
| Approvals | A gate wraps tool execution. Approvals can be answered in the console, in chat channels and on the phone. |
| Scheduling | "Routines": schedules and event triggers (mail, calendar, GitHub, CRM). |
| Coding worker | Claude Code or Codex run headless inside a container. |
| Not present | Client websites and hosting, domains, social publishing, a client portal for outside customers. |

**Design ideas worth taking (ideas only, per the build preference)**
1. **Budget guard and spend ledger are two separate things.** One records, one refuses. The check runs before each request, because a check afterwards has already paid for the request that broke the limit. Same as R1-004.
2. **Every agent always has a budget guard and an approval gate.** Neither is an optional feature, so nobody can configure an agent without them by accident. Presence OS should state the same for the Action Broker.
3. **The gate wraps execution.** A tool is gated because the configuration says so, not because its author remembered to call a check.
4. **Approval is per tool, not per capability.** "Send email" is gated and "draft email" is not. A queue that asks about harmless reads teaches people to click through, and then the write is approved too.
5. **A bad approval setting is refused when the agent is published,** not found at run time. A typing mistake would otherwise produce a tool that silently never asks.
6. **An unattended run is stricter than an attended one.** Writes, delegation and external actions need approval unless the creator granted a narrow exception bound to that version and intent. Every waived call is still recorded with who consented.
7. **An unknown model price is recorded as zero with a flag,** so the total is marked incomplete instead of quietly under-reporting. Matches the "unavailable values not zeroed" test in R1-012.
8. **Prices come from a pinned package, not a live lookup.** Updating prices is a reviewed dependency change.
9. **A schedule whose previous run is still going** has defined behaviour. Presence OS should define it too.
10. **Its security document lists each control beside the test that proves it.** A good format for the R1-010 evidence.

**Where it does not meet Presence OS rules**
- **Isolation is application-level only.** One missed filter is a cross-tenant read. Presence OS requires PostgreSQL row-level security with a runtime role that cannot bypass it.
- **The subscription login is stored in the credential vault and handed to the worker** as an environment variable (the token from `claude setup-token`). Presence OS keeps the operator's login on the Worker VM only, outside the workspace.
- **The coding harness runs with its own permission prompts switched off,** relying on the container as the boundary. Presence OS adds gVisor, an egress allow list and path restrictions (E-087).
- **Password sign-in exists.** Presence OS is Google-only.
- **No durable workflow engine.** It uses its own worker queue; Presence OS uses Temporal.
- **Built for one company's staff,** not for an operator serving separate outside clients. Its own architecture document describes knowledge collections as shared by all users of a deployment.

**Should Presence OS be built on it instead?** No, and the reason is not licence. It would mean a different backend framework, no row-level security, no Temporal, and a codebase of about 10,000 files changing several times a week under one main author. The client-facing half of Presence OS (sites, domains, social, client roles) would still have to be written. It is the best single reference found for the agent-governance half, and its design notes explain the reasoning behind each choice, which is rare.

**Things to recheck later:** whether it adds row-level security; whether the pace settles; whether the single-author risk changes.

## 5. Agency and client portal

| Project | Licence (reported) | Label | What to take from it |
|---|---|---|---|
| [directus-labs/agency-os](https://github.com/directus-labs/agency-os) | MIT | Study | Agency website, CRM, projects and a client portal where clients see status, tasks and files. Tasks can be assigned to the client. One agency per installation. |
| [Vibra-Labs/Atrium](https://github.com/Vibra-Labs/Atrium) | Elastic Licence v2 | Avoid reading code | Self-hosted client portal with file sharing and branding. |
| [Worklenz/worklenz](https://github.com/Worklenz/worklenz) | AGPL-3.0 | Avoid reading code | Project management with a client portal. |
| OpenLevel | not confirmed | Study | A GoHighLevel-style tool with CRM, pipeline, booking and several client locations. No social planner found. |

**What this means.** No permissively licensed portal has a client **approval** flow with roles like Viewer, Requester and Approver. The R1-001 role design has no ready-made equivalent; AgencyOS is the reference for what a client expects to see (status, tasks waiting on them, files).

## 6. Social publishing

ADR-0031 already decides that connectors are written in-house. These are the references.

| Project | Licence (reported) | Label | What to take from it |
|---|---|---|---|
| [inovector/mixpost](https://github.com/inovector/mixpost) (Lite edition) | MIT | Study | The only permissively licensed scheduler of size. Workspaces, approval flow and white label are in the paid Pro edition, not in the MIT code. PHP/Laravel. |
| [gitroomhq/postiz-app](https://github.com/gitroomhq/postiz-app) | AGPL-3.0 | Avoid reading code | Already decided in ADR-0031. |
| [trypostit/trypost](https://github.com/trypostit/trypost) | AGPL-3.0 | Avoid reading code | Newer scheduler built for agencies and for AI agents: one workspace per client, team approvals, MCP server. |
| Socioboard | GPL-3.0 | Avoid reading code | Older multi-account tool. |
| [pendpost/pendpost](https://github.com/pendpost/pendpost) | MIT | Study | Tiny. An agent drafts and schedules; nothing is published until a person approves. |
| [langchain-ai/social-media-agent](https://github.com/langchain-ai/social-media-agent) | MIT | Study | Already listed. Draft, human review, schedule. |

**What this means.**
- There is still no permissively licensed scheduler with per-client workspaces and approvals. Building it in-house is not duplicating a free option.
- pendpost notes that Instagram, LinkedIn and X have **no scheduling on the platform side**: the scheduler itself must be running at the post time. For Presence OS that means a missed post during an outage must be detected and handled, not silently dropped. E-076 covers a failed token; the outage case is now recorded as E-091.
- TryPost and Mixpost Pro both sell "workspace per client plus approval" as the agency feature. That confirms the client Approver role is the feature clients expect.

## 7. Checks to make against existing specs

These are suggestions for the R2/R3 task contracts, not decisions. Items 3 to 6 were added to the [edge-case register](../PROJECT_REAUDIT_2026-08-10.md) as E-091 to E-094.

1. **Approval inbox.** Approvals are durable items, survive a lost notification, and each notification opens the exact item (from Happier).
2. **Push on two events.** "Needs your approval" and "run failed" (from Happy).
3. **Schedules go through the Action Broker.** A scheduled run gets no shortcut around approval (the OpenClaw gap).
4. **Missed scheduled post.** Defined behaviour when the system was down at post time (from pendpost).
5. **Console token theft.** A stolen session must not be enough to run commands on the Worker VM (the OpenClaw one-click incident). Compare with the Google sign-in and step-up rules in R0-004.
6. **Skill packs are supply chain.** Imported skill or prompt packs are reviewed and pinned like dependencies (the OpenClaw marketplace incident).
7. **Budget check before the model call**, not after (AgenticOS), which R1-004 already requires.
8. **Approval per tool, validated when configured**, and a stricter floor for unattended runs (AgenticOS, section 4a).
9. **Defined behaviour when a schedule fires while its previous run is still going** (AgenticOS).

## 8. Limits of this survey

- Web search only; no repository was opened.
- Licences and star counts are second-hand and sometimes conflicting.
- Small projects (OpenLivery, pendpost, AgenticOS) may be abandoned by the time they are read.
- Closed-source products were not searched.
- English-language results only.

## Sources

- https://github.com/pingdotgg/t3code · https://flaviocopes.com/t3-code · https://andrew.ooo/posts/t3-code-review-open-source-agent-control-surface/
- https://github.com/slopus/happy · https://happier.dev/ · https://docs.happier.dev/features/permissions
- https://github.com/siteboon/claudecodeui · https://github.com/skelpo/mobilecode · https://www.sourcepulse.org/projects/27224072
- https://github.com/multica-ai/multica · https://www.everydev.ai/tools/multica
- https://docs.openclaw.ai/automation/cron-jobs/how-it-works · https://docs.openclaw.ai/start/why-openclaw/openclaw-and-hermes-agent
- https://oecd.ai/en/incidents/2026-01-30-9567 · https://www.ilert.com/postmortems/openclaw-rce-token-exfiltration-2026-01
- https://composio.dev/blog/openclaw-alternatives · https://postfa.st/blog/hermes-agent-vs-openclaw
- https://www.everydev.ai/tools/agenticos · https://github.com/sarrazola/openlivery/wiki · https://github.com/byteworthy/sovra · https://github.com/crewform/crewform
- https://github.com/paperclipai/ · https://paperclip.ing/llms.txt
- https://directus.io/blog/announcing-agencyos · https://github.com/Vibra-Labs/Atrium · https://worklenz.com/open-source-client-portal/
- https://openalternative.co/compare/mixpost/vs/postiz · https://github.com/trypostit/trypost · https://mcpservers.org/servers/pendpost/pendpost
- https://makerkit.dev/blog/tutorials/claude-code-routines-guide · https://devops.com/claude-code-routines-anthropics-answer-to-unattended-dev-automation
