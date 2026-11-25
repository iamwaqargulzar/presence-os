# Assumptions and Open Questions

Current as of 2026-11-15. These do not block R0 unless marked blocking. Each task contract also lists its own open decisions under "Open decisions"; this file is the cross-cutting list.

## Decided on 2026-11-14 (no longer open)

- Operating model: operator-run, not sold (ADR-0030).
- Sign-in: Google only, by invitation.
- Operator access: console hostname through the Cloudflare Tunnel; Proxmox/SSH by local network or WireGuard.
- Inference: cloud-only default; GPU host optional.
- Social publishing: connectors built in-house (ADR-0031).
- Budgets are in money; no AI Compute Units.
- No payment processor, plan pricing or first commercial vertical is needed.
- Scheduled tasks (owner, 2026-11-15): the default is prepare and wait for the operator's approval. The operator may mark a specific low-risk task (a report, a watch, a check) as unattended; it then runs on an API profile. Any task that posts, sends, deploys or spends beyond its budget always waits for approval.
- Mobile surface (owner, 2026-11-15): the web console installed on the phone, with push notifications for approvals, failures and watch results. A notification opens the exact item. A chat channel may be added later for notifications only; approval stays in the signed-in console.
- Social platforms (owner, 2026-11-15): Meta first (Facebook Pages and Instagram through one app), then LinkedIn company pages. Others later. Start Meta business verification early; it needs no code. Recheck each platform's current approval rules before applying.
- Low-cost model (owner, 2026-11-15): for now DeepSeek V4.1 Flash, through DeepSeek's own service by default; a client can be switched to a US or EU host of the same model through its provider policy. The owner expects this choice to change often: the model is configuration, never code, and is replaced through the default-change procedure (R1-013). Default for a new client: only low-risk data (public website text, drafts of public posts, formatting, tagging, summaries of public pages). Customer lists, private messages, financial records, credentials and personal data about a client's customers are never sent to the low-cost profile.
- Clients without a Google account (owner, 2026-11-15): the client creates a free Google account on their existing email address. A client who declines gets no login; the operator shows drafts outside the system and records the client's approval as an operator-attested approval, with the evidence attached. Microsoft sign-in is not built now.
- Ending service (owner, 2026-11-15): clients have no control to revoke or pause the operator's access. The operator ends service from the console when a client asks. Clients can view the access and disconnect their own connected accounts.
- Budgets (owner, 2026-11-15): budgets, reservations and the ledger are kept in US dollars. The console also shows each amount in Pakistani rupees, converted at a rate the operator sets; the rupee figure is for reading only and never used for a limit check. Starting caps, changeable per tenant at any time: USD 20 per client per month, USD 30 per operator-owned company per month, USD 150 across all tenants per month, warning at 80%. Caps cover paid API usage; subscriptions are a fixed cost shown separately in the cost report.
- Console domain (owner, 2026-11-15): the operator console is `console.iamwaqargulzar.com` for the time being. This makes `iamwaqargulzar.com` the control-plane registrable domain: no client site, preview or other tenant-generated content may be served from any name under it. The console hostname is configuration and can be moved later. The second domain, for hosted client sites and previews, is not chosen yet.
- Backups (owner, 2026-11-15): the second backup copy is, for the time being, an encrypted USB drive attached to the server. This is an interim step and is not an offsite copy: it protects against a failed disk, not against fire, theft, a power surge or an attacker who controls the server. A cloud storage target replaces it later; Backblaze B2 is the leading candidate. The move to cloud storage must happen before the first client's data is held in production.
- Personal profile (owner, 2026-11-15): the operator's own personal presence is its own tenant, separate from every company, with its own accounts, brand voice and budget (the operator-owned cap). A personal site built by the system cannot be served under the control-plane domain.
- Model gateway (owner, 2026-11-15): built in-house, one adapter per provider; no gateway library (ADR-0033).
- Toolchain: newest stable versions that all dependencies support; uv and pnpm; private GitHub repository with GitHub Actions (ADR-0032).

## Blocking for R0-001

None. Resolved and built on 2026-11-25: versions and package managers (ADR-0032, ADR-0034), repository hosting (private GitHub repository created and pushed by the owner on 2026-11-25).

## R0 and R1 decisions

Decided in ADR-0033 (technical defaults), including the in-house model gateway, primary development worker, sign-in library, Cloudflare Access, Temporal, OpenBao, observability, object storage, sandbox limits, session boundary, data classes, hostname format and the contract gaps.

Still open:
- the licence-check gate has no owning R0 task (proposed: a small follow-up task after R0-002);
- the registrable domain for hosted client sites and previews (must not be `iamwaqargulzar.com`; needed before anything tenant-generated is put online);
- the cloud storage target for the offsite backup copy (needed before the first client's production data);
- left to the named task and recorded in its report: permission catalogue content, action-class and risk table, structure of `scope` and `constraints`, initial limit keys, governor per-class limits and weights, custom-domain and model-revision state names.

## R2/R3 decisions

The R2 and R3 task contracts were written on 2026-11-15 (`specs/R2/`, `specs/R3/`). Each lists its own open decisions with a proposed default. Nothing below is decided. The technical ones can be settled together in one ADR ("technical defaults for R2 and R3"), as ADR-0033 did for R0 and R1.

### For the owner

1. **Tenant-site domains (blocking for R3-002).** The registrable domain for client sites, and one for previews. Must not be `iamwaqargulzar.com`.
2. **Offsite backup target (blocking before the first client).** Backblaze B2 is the leading candidate (R3-014).
3. **Voice in R2.** Proposed default: text only in R2; voice later through the gateway (R2-005).
4. **Runtime profiles at R3 start.** Proposed default: static sites only; a Node/Next.js server profile only when a real client site needs it; no tenant databases or background jobs in R3 (R3-001).
5. **Static sites during a home outage.** Proposed default: serve production static sites from Cloudflare's cache (R3-002, E-085).
6. **Site generator.** Proposed default: in-house templates and content model; a permissive library only after dependency review; no CMS application deployed (R3-004).
7. **Contact forms on client sites.** Proposed default: one simple form type, submissions kept 180 days (R3-004).
8. **Google Business Profile connector.** Proposed default: not in R3; manual correction packs instead; first R4 contract if most clients are local businesses (R3-012).
9. **Google Search Console and analytics, read-only.** Proposed default: not in R2 or R3 (R2-011, R3-005).
10. **AI engines to measure, and money for it.** Proposed default: two engines with official APIs, about USD 2 per client per month (R2-014).
11. **Cloud image provider.** Proposed default: choose at task start by price and commercial-use terms; no local ComfyUI adapter in R3 (R3-007).
12. **Default client-approval policy.** Proposed default: for a client tenant with an Approver, every public post and every visible text change on a site needs the client's approval; none for operator-owned tenants (R2-007, R3-008).
13. **Urgent publication without client approval.** Proposed default: only a takedown or a factual correction, both flagged to the client (R3-008).
14. **One-tap approval of several items.** Proposed default: no (R2-007).
15. **What clients see.** Proposed defaults: component scores but not one overall number (R2-012); the competitor comparison after the operator has reviewed it (R2-013); no cost figures (R2-006, R3-013).
16. **Monthly client reports.** Proposed default: the operator reviews each one for the first three months per client (R3-013).
17. **Client or tenant name on the phone's lock screen in a push.** Proposed default: the name only (R2-008).
18. **AI-crawler policy for client sites.** Proposed default: allow, switchable per property (R3-005).
19. **Marking published content as AI-assisted.** Proposed default: follow each platform's rule; no extra label (R3-006).
20. **Posting to the operator's personal LinkedIn profile.** Proposed default: not in R3; company pages only (R3-011).
21. **Meta and LinkedIn applications (no code, start early).** Which legal business name and documents are used for Meta Business verification and the LinkedIn developer app; the public privacy policy text both require (R3-010, R3-011).
22. **Tenant export and offboarding.** Edge cases E-058, E-059, E-082 and E-086 are tagged "R1+", and no R0 to R3 contract builds the export. Proposed default: add one contract to R3 before the first client (R3-014).
23. **Pilot and outside review.** Proposed defaults: 30 days on the operator's own tenants before the first client; an external security test before the first client's account is connected (R2-017, R3-014).
24. **Recovery objectives stated to clients.** Proposed default: none in writing until restore drills give measured numbers (R3-014).

### Technical defaults proposed in the contracts

Per-run and per-skill limits and task-class routing (R2-001); embedding model and raw-archive retention (R2-002); fact promotion rules and freshness periods (R2-003); context token budgets and record retention (R2-004); conversation profile (R2-005); component library and console languages (R2-006); approval expiry periods and attested-approval evidence (R2-007); platform email provider, quiet hours and digest time (R2-008); lateness windows, overlap policy and schedule limits (R2-009); search provider, extraction library and cache freshness (R2-010); scan surface list and rescan period (R2-011); score formula version 1 (R2-012); competitor cap (R2-013); sample count and interval method (R2-014); ranking formula version 1 (R2-015); priority table version 1 (R2-016); where property source and builds live (R3-001); certificate method for custom domains and the Public Suffix List (R3-002); deploy risk rating and artifacts kept (R3-003); structured-data types (R3-005); similarity threshold and content languages (R3-006); risk rating of publishing (R3-008); post types, lateness window and post limits (R3-009); Instagram connection route (R3-010); LinkedIn reauthentication warning period (R3-011).

## Later

- final local voice model stack, if the GPU host is used;
- recovery objectives (RPO/RTO) to state to clients;
- design system and visual identity;
- legal entity, jurisdiction and compliance scope;
- static public IP timing; whether the tunnel remains a permanent fallback.

## Principle

When a choice is not architecturally important, choose a conservative stable default and record it in an ADR rather than delaying.
