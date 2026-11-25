# R3-011 — LinkedIn Company Pages Connector

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 and R2 are built; recheck against their implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.
>
> Platform details in this file (product names, permission names, token lifetimes) are what was understood on 2026-11-15. They are time-sensitive. Confirm each against LinkedIn's official documentation at task start and record the date.

## Goal
Publish approved posts to a client's LinkedIn company page through LinkedIn's official API, behind the Connection Broker and the Action Broker, reusing the R3-009 core without changing it.

## Why now
Owner decision of 2026-11-15: LinkedIn company pages are the second platform. Doing a second connector also proves that the connector contract is truly platform-neutral.

## Context / linked docs / ADRs
- [ADR-0031 (in-house connectors)](../../docs/adrs/ADR-0031-postiz-self-hosted-social-publishing.md)
- [Decision Register](../../docs/DECISION_REGISTER.md) (connector order)
- [Connector framework](../../docs/integrations/connector-framework.md)
- [OAuth, connections and browser identity](../../docs/security/oauth-connections-browser.md)
- [Social, community and browser automation policy](../../docs/integrations/social-browser-policy.md)
- [Communications, platform policy and jurisdiction](../../docs/compliance/communications-and-platform-policy.md)
- [Runbook: external API / connector change](../../docs/runbooks/connector-api-change.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0002, ADR-0015, ADR-0018, ADR-0030

## Depends on
- R3-010 (done first; one platform at a time). Uses R3-009, R1-007, R0-008.

## Invariants
- official LinkedIn API only, with consent on LinkedIn's own pages; no password, cookie or one-time code is ever handled;
- company pages only. No automation of personal profiles, connection requests or messages;
- least permissions: publish to and read posts of organisations the person administers;
- tokens only in the Secrets Broker store; short-lived capability for the adapter;
- one tenant's organisation token is never usable from another tenant;
- every publish is a broker Action;
- no code copied from any other scheduler's LinkedIn integration; no work-around of LinkedIn limits or access programmes.

## In scope
- Non-code track, started early: LinkedIn developer app tied to the operator's company page; application for the API product that allows posting on behalf of organisations; the use-case description LinkedIn asks for.
- Provider registry entry for LinkedIn: endpoints, scopes, token and refresh lifetimes, required version header.
- Connect flow: start → LinkedIn consent → callback → list organisations where the person has a posting role → pick those that belong to this tenant → store by reference.
- Account identity display (company name, logo, vanity name) for confirmation.
- Connector adapter implementing the R3-009 contract for one surface: organisation feed.
- Post types: text, link (article share), single image, multiple images. Image upload through LinkedIn's upload step, tracked so a retry does not duplicate.
- Idempotency and lookup: store the returned post identifier; for an unknown outcome, list recent organisation posts and match before any retry.
- Versioned API handling: the adapter pins a LinkedIn API version, records its end date, and raises an attention item well before it ends.
- Token health: access token expiry, refresh where LinkedIn grants refresh tokens, otherwise a reauthentication request to the client before expiry; role removed from the page; app access withdrawn.
- Rate-limit handling per LinkedIn's application and member limits.
- Disconnect and delete post for takedown.
- Capability matrix data with last-verified date.
- Staging test on the operator's own company page.

## Out of scope
- Personal profile posting. The operator's personal tenant may want it; it is a different permission and policy question. See open decisions.
- Comments, reactions, messages, connection requests, lead forms, ads, analytics dashboards, video and documents.
- Any browser automation of LinkedIn.

## API / contract changes
- Connector `linkedin` registered with capabilities. No change to the R3-009 contract; a needed change is a spec revision of R3-009.
- OAuth callback endpoint on the control-plane domain.

## Data / migration
- No new tenant tables. Provider registry and ConnectorCapability rows.

## Security / privacy threat notes
- Token leak: same controls as R3-010; seeded-value secret scan.
- A person who administers several companies attaching the wrong one to a tenant (E-074): explicit pick, identity shown, confirmation before the first post.
- Reauthentication prompts used for phishing: the request is shown inside the signed-in console and by a notification that links only to the console; it never asks for a password.
- Access programme withdrawn (E-075): posts HELD, attention item, runbook.
- Tokens that expire without refresh: clients would be asked to reconnect on a regular cycle; a missed reconnect holds posts, it does not drop them (E-076).
- Development agents never receive the live client secret or tokens.

## Edge cases covered
- E-074, E-075, E-076, E-077 for LinkedIn.
- E-047 disconnect or role removal while posts are queued.
- E-049 timeout after success.
- E-051 scheduled time handling is inherited from R3-009.

## Observability
- Audit: connect, organisations picked, every publish and delete with LinkedIn's reference.
- Metrics: publish results by reason, token expiry horizon per connection, API version end date, rate-limit state.

## Acceptance criteria
- a client connects a company page without the operator and without Presence seeing a password;
- an approved post publishes once and its permalink is stored;
- a connection whose token expires within the warning period raises a reauthentication request before posts are affected;
- an unknown outcome is reconciled by lookup and never posted twice;
- the R3-009 contract and core code are unchanged by this task, or the change is recorded as an R3-009 spec revision;
- a seeded token never appears outside the secrets store.

## Tests
- Contract test suite of R3-009 against this adapter with a local LinkedIn-shaped fake built from the official documentation.
- Error mapping: expired token, insufficient role, rate limit, version retired, media rejected, access withdrawn.
- Image upload step failure and retry without duplicate.
- Token expiry horizon and reauthentication request timing.
- Tenant isolation: organisation of tenant A cannot be posted to from tenant B through any ID; RLS suite with LinkedIn rows.
- Secret scan with seeded values.
- Manual staging run on the operator's company page, recorded.

## Rollback / failure recovery
Disable by configuration; posts become HELD. Adapter versions follow LinkedIn's API versions; the previous adapter is kept until the new one is proven.

## Cost/resource budget
No model calls. API access cost as understood today is none for this use; recheck. Calendar time for LinkedIn's access approval is the main cost.

## Documentation updates
- `docs/integrations/connector-framework.md` (LinkedIn matrix row), `docs/SOURCE_REGISTRY.md` (LinkedIn documentation links and check date), a short client guide "how to connect a LinkedIn company page".

## Open decisions
- **Decision required (owner, non-code):** which company page and legal entity the LinkedIn developer app is registered under, and when to apply.
- **Decision required (owner):** posting to the operator's own personal LinkedIn profile from the personal tenant. Proposed default: not in R3; company pages only, as the Decision Register states.
- **Decision required:** behaviour if LinkedIn does not grant the organisation-posting product. Proposed default: LinkedIn stays "draft and remind": Presence prepares the post and the operator or client posts it by hand; nothing is automated around the refusal.
- **Decision required:** reauthentication warning period. Proposed default: 14 days before token expiry, repeated at 3 days.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review recorded; access approval obtained, or the limitation written in the R3 exit report; documentation check date recorded.
