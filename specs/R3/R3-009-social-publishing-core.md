# R3-009 — Social Publishing Core

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 and R2 are built; recheck against their implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Build everything social posting needs that is the same for every platform: the post model, the calendar, the connector contract, safe scheduled execution, reconciliation after an unknown result, and handling of missed and held posts. No platform-specific code is in this task; it is proven against a fake platform.

## Why now
ADR-0031: social connectors are built in-house, one platform at a time. The shared part must exist first so that the Meta and LinkedIn connectors are thin adapters.

## Context / linked docs / ADRs
- [ADR-0031 (replacement decision: in-house connectors)](../../docs/adrs/ADR-0031-postiz-self-hosted-social-publishing.md)
- [Connector framework](../../docs/integrations/connector-framework.md)
- [Social, community and browser automation policy](../../docs/integrations/social-browser-policy.md)
- [OAuth, connections and browser identity](../../docs/security/oauth-connections-browser.md)
- [Concurrency, idempotency and consistency](../../docs/architecture/concurrency-idempotency.md)
- [Runbook: external API / connector change](../../docs/runbooks/connector-api-change.md)
- [Research: social publishing](../../docs/research/OPEN_SOURCE_LANDSCAPE_OPERATOR_RUN_2026-11-14.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0002, ADR-0005, ADR-0018, ADR-0030

## Depends on
- R3-008 (publication flow). Uses R1-003 (broker, delayed actions), R1-007 (connections), R3-006 (content), R3-007 (media), R2-008, R2-016.

## Invariants
- every post is a `content.publish` Action through the Action Broker. Connectors are execution adapters; they decide nothing;
- official APIs only. No browser automation, no password, cookie or one-time code handling, no bypass of limits;
- no code is copied from any third-party scheduler (ADR-0031);
- a post has one idempotency key per destination; after an unknown result the platform is checked before any retry (E-077);
- never claim exactly-once delivery;
- most platforms have no scheduling on their side: Presence must be running at post time, and a post missed during downtime is held for a decision, never published late by itself and never dropped (E-091);
- a connection belongs to one tenant; a post can go only to an account connected by that tenant.

## In scope
- SocialPost: tenant, content item version, destination (connection, account, surface type), platform variant fields, media, scheduled local time and timezone, resolved instant, state mirrored from its Action, external post reference, permalink.
- Connector contract (versioned interface): `capabilities()`, `validate(post) → problems`, `publish(post, idempotency_key)`, `lookup(idempotency_key or reference) → outcome`, `delete(reference)`, `health()`, `rate_limit_state()`, `account_identity()`.
- Capability matrix per connector: supported post types, limits (length, media count, sizes, formats), required scopes, restrictions, policy status, last verified date. Stored as data and shown in the console.
- Pre-publication validation against the matrix, at draft time and again at execution.
- Scheduling: a scheduled post is a delayed Action; revalidated in full immediately before posting (grant, approval, connection health, limits, tenant state).
- Timezone rules as in R2-009 (local intent stored; daylight-saving safe).
- Execution outcomes: SUCCEEDED with reference; FAILED with a platform reason; `OUTCOME_UNKNOWN` → reconcile by `lookup` on a backoff; only a confirmed "not published" allows a retry.
- Rate-limit handling: respect the platform's stated limits; queue inside the window; never burst.
- Held posts: when a connection is not healthy (reauthentication needed, permission lost, platform outage, app approval withdrawn), queued posts move to HELD with the reason; the operator and client are told; after repair the operator releases or reschedules them.
- Missed posts: on restart, posts whose time passed during downtime are listed; inside the lateness window the operator chooses "post now", "reschedule" or "cancel"; outside it they are marked MISSED.
- Calendar view per tenant: drafts, awaiting approval, scheduled, published, held, missed.
- Account confirmation: before the first post to a newly connected account, show the account's name and picture for confirmation (E-074).
- Post-publication record: permalink stored for the progress report; basic public counts read later where the API allows.
- A fake platform (local service) implementing the connector contract with scriptable behaviour, used by all tests.
- Connector health items feeding Attention; the connector API-change runbook wired to them.

## Out of scope
- Any real platform (R3-010, R3-011).
- Comments, replies, direct messages, follows and engagement (R4).
- Analytics dashboards beyond the stored basic counts.
- Bulk import of post lists; automatic reposting or recycling.
- Paid promotion of posts.

## API / contract changes
- The connector contract above, documented as the guide "how to write a social connector".
- Endpoints: create post from an approved content item, schedule, reschedule, cancel, calendar, resolve held or missed post, confirm account.
- New contract sketches: `social-post.schema.json`, `connector-capability.schema.json`.

## Data / migration
- Tenant-scoped under RLS: SocialPost, SocialPostAttempt (if not covered by ActionAttempt), AccountConfirmation.
- Platform table: ConnectorCapability (versioned).
- Reverse migrations tested.

## Security / privacy threat notes
- Double post after a timeout (E-077): reconcile before retry; test with "succeeds then times out".
- Post to the wrong account or wrong tenant's account: destination bound in the grant; account confirmation; cross-tenant test.
- Token exposure: adapters receive a short-lived capability from the Connection Broker, never the stored token; nothing is logged.
- Queued post after disconnect or revoked approval (E-047): execution-time revalidation.
- Platform policy breach by volume: rate limits in the governor per connection.
- Webhook replay from a platform (E-050): not used in this task; if a connector adds webhooks it must verify signature, time window and event idempotency.

## Edge cases covered
- E-047, E-048, E-049 on posts.
- E-051 daylight-saving shifts of scheduled posts.
- E-074 wrong or personal account.
- E-075 a platform withdraws the app's approval or API access.
- E-076 token refresh fails overnight before scheduled posts.
- E-077 retry after unknown result posts twice.
- E-091 system down at post time.
- E-092 scheduled post has no shortcut.

## Observability
- Audit: every post Action transition; held, released, missed decisions; account confirmations.
- Metrics: posts by state and connector, unknown outcomes and time to reconcile, held and missed counts, rate-limit waits.
- Trace from approval to the adapter call.

## Acceptance criteria
- against the fake platform, a scheduled approved post publishes once at its time, and its permalink is stored;
- "succeeds then times out" never produces a second post;
- a post whose connection became unhealthy is HELD with a reason and both the operator and the client are told;
- after simulated downtime across a post time, the post is not published until the operator decides;
- a post that breaks a capability limit is refused at draft time with the exact problem;
- a post cannot target an account of another tenant;
- adding a second fake connector needs no change outside its adapter and its capability data.

## Tests
- Broker check chain for a post: one negative test per check.
- Idempotency and reconciliation: kill worker mid-publish; timeout after success; platform returns duplicate error.
- Held and missed flows; lateness window boundaries.
- Daylight-saving and timezone tests.
- Rate limit: bursts are spread, not dropped.
- Capability validation matrix.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on SocialPost and AccountConfirmation across tenants; connection ID substitution.
- Secrets: seeded token never appears in logs, traces, audit or model context.
- Boundary: a connector called outside the broker fails the gate.

## Rollback / failure recovery
A connector can be disabled by configuration; its queued posts become HELD. Nothing retries blindly against a platform. Reverse migrations tested.

## Cost/resource budget
No model calls. Proposed default limits: 60 scheduled posts per tenant per month; per-connection rate limits from the capability matrix.

## Documentation updates
- `docs/integrations/connector-framework.md` (the concrete contract and matrix), `docs/integrations/social-browser-policy.md`, `docs/runbooks/connector-api-change.md`, a new runbook "held and missed posts".

## Open decisions
- **Decision required:** lateness window for a missed post. Proposed default: 60 minutes for "post now" to be offered; after that only reschedule or cancel.
- **Decision required:** whether a post may be auto-released when a connection recovers within a short time. Proposed default: no; the operator releases held posts.
- **Decision required:** post types in the first version. Proposed default: text, link, single image, multiple images. Video and stories later.
- **Decision required:** monthly post limit per tenant. Proposed default above.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: independent security review recorded; the double-post and E-091 tests are protected tests; provenance review confirms no third-party scheduler code.
