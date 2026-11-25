# R3-010 — Meta Connector (Facebook Pages and Instagram)

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 and R2 are built; recheck against their implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.
>
> Platform details in this file (permission names, review steps, limits) are what was understood on 2026-11-15. They are time-sensitive. Confirm each against Meta's official documentation at task start and record the date.

## Goal
Publish approved posts to a client's Facebook Page and Instagram professional account through Meta's official API, with one Meta developer app, behind the Connection Broker and the Action Broker.

## Why now
Owner decision of 2026-11-15: Meta first, then LinkedIn. Meta business verification and app review take calendar time and need no code, so they start early.

## Context / linked docs / ADRs
- [ADR-0031 (in-house connectors)](../../docs/adrs/ADR-0031-postiz-self-hosted-social-publishing.md)
- [Decision Register](../../docs/DECISION_REGISTER.md) (connector order)
- [Connector framework](../../docs/integrations/connector-framework.md)
- [OAuth, connections and browser identity](../../docs/security/oauth-connections-browser.md)
- [Social, community and browser automation policy](../../docs/integrations/social-browser-policy.md)
- [Communications, platform policy and jurisdiction](../../docs/compliance/communications-and-platform-policy.md)
- [Secrets management](../../docs/security/secrets.md)
- [Runbook: external API / connector change](../../docs/runbooks/connector-api-change.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0002, ADR-0015, ADR-0018, ADR-0030

## Depends on
- R3-009 (connector contract, fake platform tests). Uses R1-007 (OAuth flow, token storage), R0-008 (secrets, Fetch Broker allow-list).

## Invariants
- official Meta API only, with the client's consent given on Meta's own pages. Presence never sees a Facebook or Instagram password;
- least permissions: only those needed to list the client's Pages, publish, read the published post and delete it;
- tokens live only in the Secrets Broker store; adapters get a short-lived capability;
- one tenant's Page token is never usable from another tenant;
- every publish is a broker Action; the connector decides nothing;
- no code copied from any other scheduler's Meta integration;
- never work around a Meta limit, review requirement or restriction.

## In scope
- Non-code track, started as soon as this contract is accepted: Meta Business verification of the operator's business; creation of the developer app; privacy policy and data-deletion pages required by Meta, served on the control-plane domain; app review submission for the needed permissions, with the screen recordings Meta asks for.
- Provider registry entry for Meta in the Connection Broker: endpoints, scopes, token lifetimes, capabilities.
- Connect flow: client or operator starts "Connect Facebook/Instagram" → Meta consent → callback → list the Pages and linked Instagram accounts the person granted → the person picks which ones belong to this tenant → store Page-level credentials by reference.
- Account identity display (name, picture, handle) for the confirmation step of R3-009.
- Connector adapter implementing the R3-009 contract for two surfaces: Facebook Page feed; Instagram professional account feed.
- Post types: text, link, single image and multiple images for Facebook Pages; single image and carousel for Instagram. Instagram media is fetched by Meta from a URL: serve it from a short-lived signed URL on the tenant-site domain, never from the control-plane domain.
- Idempotency and lookup: store Meta's returned ID; for an unknown outcome, look the post up before any retry. Instagram's two-step publish (create container, then publish) is tracked per step.
- Capability matrix data for both surfaces, with last-verified date.
- Rate-limit handling from Meta's response headers and documented publishing limits.
- Token refresh and health: detect expired or invalidated tokens, removed permissions, a Page the person no longer manages, and an app restriction; map each to a connection status.
- Disconnect: remove stored credentials and revoke the grant at Meta where the API allows.
- Meta's data-deletion callback and deauthorisation callback: verified by signature, idempotent, and they remove the connection.
- Delete post for takedown (R3-008).
- Staging test with a test Page and test Instagram account owned by the operator.

## Out of scope
- Comments, messages, mentions, ads, insights dashboards, stories, reels and video (later contracts).
- Personal Facebook profiles (not supported by the platform for this use).
- Using Facebook's own scheduled-post feature. See open decisions.
- WhatsApp and Messenger (R4).

## API / contract changes
- Connector `meta` registered with capabilities; no change to the R3-009 contract. If the contract proves too narrow, the change is made in R3-009 by a spec revision, not here.
- Callback endpoints for OAuth, deauthorisation and data deletion on the control-plane domain.

## Data / migration
- No new tenant tables beyond R1-007 and R3-009. Provider registry row and ConnectorCapability rows.
- App secret and tokens in the Secrets Broker only.

## Security / privacy threat notes
- App secret or Page token leak: never in logs, model context, error messages or the repository; secret scan with seeded values.
- A person granting Pages of several businesses, and one being attached to the wrong tenant: explicit pick per tenant, identity shown, confirmation before the first post (E-074).
- Forged callbacks (deauthorise, data deletion) or replay (E-050): signature check, time window, event idempotency.
- Media URL exposure: signed, short-lived, single asset, on the tenant-site domain.
- App-level risk: one developer app serves every client; if Meta restricts it, all Meta posting stops. Mitigation: strict policy compliance, held posts, attention item, runbook (E-075).
- Development agents never receive the live app secret or any client token (ADR-0027); connector tests use the fake platform and recorded fixtures.

## Edge cases covered
- E-074 wrong or personal account connected.
- E-075 Meta withdraws app approval or API access.
- E-076 token invalid before scheduled posts: posts HELD, reauthentication request.
- E-077 unknown outcome and double post, including the Instagram two-step case.
- E-047 disconnect while posts are queued.
- E-050 callback replay.
- E-049 timeout after success.

## Observability
- Audit: connect, accounts picked, permissions granted, every publish and delete with Meta's reference, callbacks received.
- Metrics: publish success and failure by reason, rate-limit state, token health, API version in use and its end date.

## Acceptance criteria
- a client connects a Page and an Instagram account without the operator, and without Presence seeing a password;
- an approved post publishes once to each chosen surface and its permalink is stored;
- revoking Presence in the person's Facebook settings is detected and moves the connection to a blocked status; queued posts are HELD;
- an unknown outcome is reconciled by lookup and never posted twice;
- the takedown control deletes the post where Meta allows, and reports clearly where it does not;
- a seeded token never appears outside the secrets store;
- the connector uses only permissions that passed app review.

## Tests
- Contract test suite of R3-009 run against this adapter with a local Meta-shaped fake built from the official documentation.
- Error mapping: expired token, missing permission, rate limit, Page access lost, media rejected, app restricted.
- Instagram two-step: failure between container and publish; retry without duplicate.
- Callback signature, replay and idempotency.
- Tenant isolation: a token of tenant A cannot be selected by tenant B through any ID; RLS suite on the connection and post tables with Meta rows.
- Secret scan with seeded values.
- Manual staging run on the operator's test Page and account, recorded.

## Rollback / failure recovery
Disable the connector by configuration; posts become HELD. The adapter is versioned with Meta's API version; the previous adapter version is kept until the new one is proven (connector API-change runbook).

## Cost/resource budget
No model calls. The API is free at this use level as understood today; recheck. Engineering cost is mostly waiting for review.

## Documentation updates
- `docs/integrations/connector-framework.md` (Meta matrix row), `docs/SOURCE_REGISTRY.md` (Meta documentation links and check date), a short client guide "how to connect Facebook and Instagram".

## Open decisions
- **Decision required (owner, non-code, start now):** the legal business name and documents used for Meta Business verification, and the public privacy policy text Meta requires.
- **Decision required:** Facebook's own scheduling against Presence scheduling. Proposed default: Presence schedules everything, so approval revalidation and takedown work the same on every platform.
- **Decision required:** which Instagram connection route to use (through a Facebook Page or Instagram's direct business login). Proposed default: the route that needs the fewest permissions for publishing; decide from current documentation.
- **Decision required:** operating in development mode with only the operator's own accounts before app review completes. Proposed default: yes, for operator-owned tenants only.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review recorded; app review approved for the permissions used, or the limitation is written in the R3 exit report; documentation check date recorded.
