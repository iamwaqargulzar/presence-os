# R2-006 — Console Shell, Agent Home and Client Home

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 is built; recheck against the R1 implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Build the web console the operator uses from a phone: installable, mobile-first, with Agent Home as the landing page. From it the operator switches tenant, asks for a task, follows runs, reads reports and sees cost. Build the limited home a signed-in client sees for their own tenant.

## Why now
R0 and R1 delivered endpoints with no interface. The operator works mainly from a phone (ADR-0030). Approvals, notifications and scheduling in the next tasks all need this shell.

## Context / linked docs / ADRs
- [Operator and managed-service experience](../../docs/product/admin-and-managed-service.md)
- [Conversation Shell and Agent Home](../../docs/product/conversation-and-home.md)
- [Information architecture](../../docs/ux/information-architecture.md)
- [UI / visual design direction](../../docs/ux/design-direction.md)
- [Accessibility and localization](../../docs/product/accessibility-localization.md)
- [Person, profile and tenant model](../../docs/product/person-profile-tenant-model.md)
- [Registrable-domain separation](../../docs/domains/domain-separation.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0008, ADR-0030, ADR-0033

## Depends on
- R2-005. Uses R0-004 (Google sign-in, sessions), R1-001 (roles), R1-004 (cost report), R0-011 (development-run endpoints).

## Invariants
- the console is served only on the control-plane hostname (`console.iamwaqargulzar.com` today); nothing tenant-generated is rendered from that origin as active content;
- sign-in is Google only, by invitation; there is no password form anywhere;
- the acting tenant and "Acting as Managed Operator" are always visible while the operator is inside a tenant;
- a client sees only their own tenant and has no control that starts AI work;
- the browser never talks to the Worker VM; it talks to the Core API only (E-093);
- WCAG 2.2 AA; nothing depends on motion or on drag;
- visual style is built from semantic tokens so it can be changed later.

## In scope
- Next.js application shell: sign-in handoff, session handling, tenant selector, navigation, error and offline states.
- Installable web app: manifest, icons, service worker for the app shell only. No tenant data is cached offline in R2.
- Agent Home for the operator: conversation input, short synthesis line, and four areas fed by later tasks: needs attention, opportunities, recent improvements, recent progress.
- Cross-tenant operator overview: every tenant with its state, open approvals, failing runs, budget use.
- Task request: by conversation, or by a short structured form when the operator prefers it.
- Task and run pages: status, steps, report, artifacts, usage and cost, model profile used, cancel and resume.
- Reports list: run reports per tenant, newest first.
- Cost page: per tenant and global, in USD with the rupee figure beside it for reading only, budget bars and the 80% warning.
- Knowledge and memory review pages (data from R2-002 and R2-003).
- Development runs page: list runs, start or approve a run that uses the operator's subscription, cancel. It calls the R0-011 endpoints.
- Client Home: tenant name, what is done, what waits for the client, their connections (from R1-007) with disconnect, the operator's access shown read-only, usage summary. No conversation box.
- Preview frames: tenant-generated previews are opened on the tenant-site domain in a new context, never framed with console cookies.
- Design tokens and base components: colour roles, spacing, type, radius, focus, status priority; light and dark themes.

## Out of scope
- Approval inbox and client request queue (R2-007). Push notifications (R2-008). Scheduling screens (R2-009).
- A native mobile app (do-not-build-early).
- The voice-reactive form.
- Final visual identity. **Decision required**, later.
- Platform administration beyond what R1 exposed (tenants, limits, model policy pages are thin forms over the R1 endpoints).

## API / contract changes
- No new domain contracts. A backend-for-frontend layer in the Django API: endpoints shaped for the console pages, all passing the R1-001 permission check.
- Security headers contract for the console origin: strict Content-Security-Policy, no third-party scripts, cookies `Secure`, `HttpOnly`, `SameSite=Lax` or stricter, host-only (no parent-domain cookie).

## Data / migration
- OperatorPreference (console settings) per person. No tenant data model changes.

## Security / privacy threat notes
- Tenant-generated HTML or a client-submitted request text rendered in the console: always escaped; rich previews only on the other registrable domain.
- Cross-site request forgery and clickjacking on approval and start buttons: anti-forgery tokens, `frame-ancestors 'none'`.
- Stolen session used to start a development run (E-093): starting or approving a subscription run needs the step-up confirmation; the worker accepts only signed controller requests.
- Wrong-tenant action by the operator: the tenant name is in the header and in every confirmation text.
- A client guessing another tenant's URL: every endpoint checks membership; IDs are not authority.
- Service worker caching private data: app shell only; cache cleared on sign-out.

## Edge cases covered
- E-010 the effective model profile is shown.
- E-012 the platform view shows tenant summaries only through the operator's access grant.
- E-064 global and tenant budget shown together with the warning threshold.
- E-070, E-090, E-093: session list and revoke are reachable from the console; step-up on high-risk controls.
- E-073 invitation revoked: the next request ends the client's session.
- E-074 the client sees which account is connected and can disconnect.

## Observability
- Front-end errors and web-vitals to the existing telemetry, without message content.
- Audit: tenant switch, every start, approve, cancel and resume control used, with the session reference.

## Acceptance criteria
- the console installs on Android and iOS home screens and opens without browser chrome;
- the operator can go from sign-in to a running task for a chosen tenant in under one minute on a phone;
- every page works at 360 px width, with keyboard only, and with a screen reader;
- a Client Viewer sees their own tenant's home and gets a refusal on every operator endpoint and every other tenant's ID;
- no page asks for a password or a social platform credential;
- the rupee figure is never used in a limit check.

## Tests
- End-to-end (Playwright) for the core journeys: sign in, switch tenant, ask for a task, read the report, read cost.
- Role matrix against every console endpoint: operator, tenant admin, client viewer, requester, approver, uninvited.
- Tenant isolation: ID substitution on every endpoint that takes an ID; indirect access through run, artifact and report links.
- Security headers and cookie attributes checked by test.
- Stored cross-site scripting: hostile text in task requests, facts and client requests renders as text.
- Accessibility: automated checks in CI plus a recorded manual pass (keyboard, VoiceOver or NVDA, right-to-left).

## Rollback / failure recovery
The front end is deployed as a versioned build; rollback is the previous build. If the conversation backend is down, structured forms still work.

## Cost/resource budget
No model calls of its own. Page weight budget, proposed default: under 300 KB of script on first load on a mobile connection.

## Documentation updates
- `docs/product/admin-and-managed-service.md`, `docs/ux/information-architecture.md`, `docs/ux/design-direction.md` (tokens), `docs/product/conversation-and-home.md`.

## Open decisions
- **Decision required:** component library. Proposed default: a small set of in-house components on headless accessible primitives (for example Radix), after dependency review; no full design kit.
- **Decision required:** what a client sees of cost. Proposed default: the usage summary only (R1-004 already allows it), no money figures unless the operator turns them on per tenant.
- **Decision required:** console languages. Proposed default: English only in R2, with all strings externalised and right-to-left layout tested.
- **Decision required (owner, later):** visual identity and design system.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: the manual accessibility pass is recorded; the role-matrix test is added to the protected authorization tests.
