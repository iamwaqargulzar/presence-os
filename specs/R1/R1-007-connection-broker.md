# R1-007 — Connection Broker

> **Spec revision:** 3 — 2026-11-14. Amended by [ADR-0030](../../docs/adrs/ADR-0030-operator-run-agency-deployment.md); the "ADR-0030 amendments" section overrides any conflicting text below it. Revision 2 (2026-11-10): Expanded from a one-paragraph summary to the full task template (`templates/TASK_SPEC_TEMPLATE.md`). The revision 1 summary is kept verbatim under Goal. Items marked *(derived)* come from the linked focused documents. Items marked **Decision required** are not locked and must be recorded in an ADR before or during the task.

## ADR-0030 amendments (revision 3)
**Added to scope**
- **Client-initiated connection.** A signed-in client can open "Connect account" in their own tenant, is sent to the social platform's own sign-in and consent page, and returns with the connection stored for that tenant. The client types their platform password only on the platform's page; Presence OS never sees or stores it.
- The operator can send a client a connect request (a link that requires the client's own Presence sign-in; the link alone grants nothing).
- The client can see every connection on their tenant, which permissions it holds and when it was last used, and can disconnect it at any time.
- Posting on a connected account is an operator action in the managed-operator capacity through the Action Broker. Where the client has the Approver role and the tenant requires it, the post waits for the client's approval.

**Added acceptance criteria**
- a client can connect and disconnect an account without operator involvement, within their own tenant only;
- a connection made by a client of tenant A is unusable from tenant B;
- after a client disconnects, a queued post for that account does not publish (E-047);
- no page of Presence OS asks for a social platform password, cookie or one-time code.

**Unchanged**
- Managed browser profiles, where a person signs in inside a hosted browser and the system keeps the session, stay out of scope (R4, E-056). Official platform connections are the supported route.

**Open decisions added**
- **Decided (ADR-0033):** (owner, 2026-11-15) Meta first (Facebook Pages and Instagram), then LinkedIn company pages. Recheck each platform's approval rules before applying.
- Decided 2026-11-14 ([ADR-0031](../../docs/adrs/ADR-0031-postiz-self-hosted-social-publishing.md), replacement decision): social platform connectors are built inside Presence OS behind this broker, one platform at a time, with no code copied from third-party schedulers. Presence stores the tokens under this task's credential rules. Each platform connector is its own later task.

## Goal
Implement provider/account/scopes/credential-ref/health states and OAuth Code+PKCE reference flow. Credentials remain outside model context and business-table sprawl.

## Why now
Every real action in R3 (publishing, posting, analytics) runs on a tenant's own account at a third party. The Action Broker checks connection health before acting, and credentials must have exactly one home before the first connector is written.

## Context / linked docs / ADRs
- Edge cases added 2026-11-14 that this task must cover: E-074, E-075, E-076 ([register](../../docs/PROJECT_REAUDIT_2026-08-10.md)).
- [OAuth, connections and browser identity](../../docs/security/oauth-connections-browser.md)
- [Connector framework](../../docs/integrations/connector-framework.md)
- [Secrets management](../../docs/security/secrets.md)
- [Communications and platform policy](../../docs/compliance/communications-and-platform-policy.md)
- [State machines](../../docs/architecture/state-machines.md)
- [OAuth references](../../docs/SOURCE_REGISTRY.md)
- [Re-audit edge cases E-047, E-056](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- Contract: [connection.schema.json](../../contracts/schemas/connection.schema.json)
- ADR-0015, ADR-0018

## Depends on
- R0-008 (Secrets Broker), R1-001 (permission to connect/disconnect), R0-006.
- Supplies the connection-health check implementation for R1-003.

## Invariants
- raw credentials never enter model context, logs, traces or business tables; modules hold a `credential_ref` only;
- clients enter their own credentials and one-time codes; Presence avoids storing passwords;
- least scopes; exact redirect URIs; state/CSRF protection; Authorization Code with PKCE;
- never bypass CAPTCHA, rate limits, anti-bot systems or platform restrictions; pause and ask for human takeover;
- a connection belongs to one tenant/profile and is never shared implicitly, even between properties of the same tenant.

## In scope
- Connection entity: provider, account_ref, credential_ref, scopes, status, expires_at, refresh_state, last_verified, health, capabilities.
- Status machine: CONNECTED ↔ DEGRADED → REAUTH_REQUIRED / PERMISSION_LOST / RATE_LIMITED / PROVIDER_OUTAGE / POLICY_BLOCKED → DISCONNECTED.
- Provider registry entry describing endpoints, scopes and capabilities.
- OAuth Authorization Code + PKCE reference flow, implemented against a local fake identity provider.
- Token storage through the Secrets Broker; refresh with rotation handling; revocation on disconnect.
- Health verification job and the health-check interface for the Action Broker.
- Capability-scoped credential use: an adapter obtains a short-lived capability for one call, not the stored token.

## Out of scope
- Real provider integrations.
- Managed browser profiles and browser identity states (R4; E-056 recorded).
- Connection repair workflows beyond state transitions and a reauth prompt hook.
- Webhook subscriptions.

## API / contract changes
- Endpoints: start connect, OAuth callback, list connections, disconnect.
- Internal: `health(connection)`, `use(connection, purpose) → capability`.
- `connection.schema.json` confirmed or refined; provider registry shape added if it crosses module boundaries.

## Data / migration
- Tables: Connection (tenant-scoped, RLS), provider registry (platform-level), OAuth transaction state (short-lived).
- No token columns anywhere outside the Secrets Broker's store.
- Reverse migrations tested.

## Security / privacy threat notes
- Authorization-code interception and CSRF on the callback: PKCE and state.
- Open redirect through a loosely matched redirect URI.
- Token leakage through logs, error messages or prompts.
- Account confusion: connecting an account to the wrong tenant when a person operates several profiles; the callback binds to the acting context captured at start.
- Refresh-token reuse after rotation; provider-side revocation not detected.
- Queued action executing on a revoked connection (E-047): health checked at execution time.
- Scope escalation by a later reconnect.

## Observability
- Audit: connect started/completed/failed, scopes granted, refresh failure, status change, disconnect, every credential use with action ID.
- Metrics: connections by provider and status, refresh failures, time since last verified.

## Acceptance criteria
- *(revision 1)* provider/account/scopes/credential-ref/health states implemented;
- *(revision 1)* OAuth Code + PKCE reference flow;
- *(revision 1)* credentials outside model context and outside business tables;
- *(derived)* all eight connection statuses reachable and enforced by the health check;
- *(derived)* disconnect revokes at the provider where supported and removes the stored secret;
- *(derived)* a connection cannot be used by another tenant or by a module without a stated purpose.

## Tests
- OAuth: happy path; missing/incorrect state; wrong PKCE verifier; mismatched redirect URI; replayed code. All against the fake provider.
- Refresh: success with rotation; failure moves to REAUTH_REQUIRED.
- Health: each status blocks or permits the Action Broker as specified.
- Secrets: seeded token never appears in logs, traces, audit, database business tables or a captured prompt.
- Cross-tenant RLS suite; callback started under tenant A cannot complete under tenant B.

## Rollback / failure recovery
On any uncertainty the connection degrades and actions pause; nothing retries blindly against a provider. Disconnect is idempotent. Reverse migrations tested.

## Cost/resource budget
Health verification is periodic work per connection: schedule it under the Resource Governor's background class and respect provider rate limits.

## Documentation updates
- `docs/security/oauth-connections-browser.md`, `docs/integrations/connector-framework.md`.
- `docs/architecture/state-machines.md` if transitions are refined.
- Guide: "how to add a provider".

## Open decisions
- **Decided (ADR-0033):** Authlib, subject to dependency review.
- **Decided (ADR-0033):** every 6 hours and before each use; one failure is DEGRADED; three in a row, or any revocation or authorization error, blocks at once.
- **Decided (ADR-0033):** a connection belongs to a tenant and may be narrowed to one property.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review recorded; the R1-003 connection-health stub is replaced.
