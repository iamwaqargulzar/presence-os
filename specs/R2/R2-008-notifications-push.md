# R2-008 — Notifications and Push

> **Spec revision:** 1 — 2026-11-15. Written to `templates/TASK_SPEC_TEMPLATE.md` before R1 is built; recheck against the R1 implementation reports before starting. **Decision required** marks a point that is not decided. A **proposed default** is a suggestion until an ADR records it.

## Goal
Deliver notifications to the operator's phone and to clients: in the console, by web push and by email. A notification is short, carries no sensitive content, and opens the exact item. Approval never happens inside a notification.

## Why now
Owner decision of 2026-11-15: the mobile surface is the installed web console with push notifications for approvals, failures and watch results. Scheduling (R2-009) is not useful if the operator does not learn that something waits.

## Context / linked docs / ADRs
- [Notifications and attention](../../docs/architecture/notifications-and-attention.md)
- [Assumptions and open questions](../../docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md) (mobile surface decision)
- [Decision Register](../../docs/DECISION_REGISTER.md) (Mobile)
- [Email and outreach infrastructure](../../docs/integrations/email-outreach.md) (platform mail kept apart from tenant mail)
- [Research: push on two events](../../docs/research/OPEN_SOURCE_LANDSCAPE_OPERATOR_RUN_2026-11-14.md)
- [Edge-case register](../../docs/PROJECT_REAUDIT_2026-08-10.md)
- ADR-0002, ADR-0030, ADR-0033

## Depends on
- R2-006 (service worker, console), R2-007 (approval items). Uses R1-003 (a push or email is an external side effect).

## Invariants
- a Notification is a delivery attempt. It is not the AttentionItem and not the ApprovalItem; losing it loses nothing;
- sending a push or an email is an external side effect and passes the Action Broker, under a standing platform policy grant for the class "platform notification to a signed-in member";
- a notification body carries a short summary and a link. No draft text, no client data, no token;
- the link requires sign-in and then the normal permission check. The link alone grants nothing;
- urgency comes from consequence and time, by rule, not from a model's wording;
- no nagging: repeated findings are deduplicated and grouped.

## In scope
- Notification entity: recipient, tenant, source item, event type, channel, state (PENDING, SENT, FAILED, SUPPRESSED), dedupe key.
- Event types in R2: approval needed, run failed, run finished (opt-in), watch result, budget threshold reached, connection needs reauthentication, client request received, break-glass used. For clients: a draft waits for your approval; your request was answered.
- Channels: in-app list with unread count; Web Push (standard VAPID, through the browser vendors' push services); email for the daily digest and for clients.
- Push subscription management per device: subscribe after an explicit tap, list devices, remove a device. Subscriptions die with the session's person when the invitation is revoked.
- Deep links: every notification resolves to one item URL in the console.
- Preferences per person: per event type and channel, quiet hours with a timezone, digest time.
- Digest: when more than a set number of items would be sent in a period, or during quiet hours, send one digest (E-079).
- Dedupe and rate limit per recipient.
- Platform email sending adapter behind the Action Broker, for the control-plane sender only.
- Retry with backoff; a subscription that the push service reports as gone is removed.

## Out of scope
- A chat channel (possible later, notifications only; owner decision).
- SMS, voice.
- Email to anyone who is not an invited member. Tenant marketing email is R4.
- Deciding what is important (R2-016).
- Approve or reject buttons inside a notification.

## API / contract changes
- Endpoints: subscribe device, list and remove devices, get and set preferences, list notifications, mark read.
- Internal: `notify(event, item, recipients)`; an action class `platform.notify` in the Action Broker's table with a low risk rating.
- New contract sketch: `notification.schema.json`.

## Data / migration
- Tenant-scoped under RLS where the event belongs to a tenant: Notification. Person-scoped: PushSubscription, NotificationPreference.
- Push subscription keys are stored as secrets by reference.
- Reverse migrations tested.

## Security / privacy threat notes
- Notification text on a locked screen exposes client data: bodies are generic ("1 draft waits for approval — Client B"). **Decision required** whether the tenant name appears; see open decisions.
- The push service (Google, Apple, Mozilla) sees metadata and the encrypted payload: payloads are encrypted by the Web Push standard and kept minimal.
- A crafted link in an email leading to a look-alike page: links use only the console hostname; the email says so; sign-in is Google with Cloudflare Access in front.
- A lost phone (E-090): revoking sessions also removes that device's push subscription.
- Email bounce or reply content treated as instruction: inbound mail is not processed in R2.
- Cross-tenant: a client's notification list shows only their tenant's events.

## Edge cases covered
- E-079 approvals pile up: one digest, expiry visible, nothing auto-approves.
- E-078 a prepared task waits: the operator is notified once.
- E-076 token refresh failed: reauthentication notification to the client and the operator.
- E-090 lost phone.
- E-069 Google unavailable: notifications still send; links work after sign-in returns.
- E-064 budget threshold.

## Observability
- Audit: each send through the broker with event type and recipient, never the body of a sensitive item.
- Metrics: sent, failed, suppressed, digest size, time from event to delivery, tap-through rate.

## Acceptance criteria
- an approval request reaches a subscribed phone as a push and opens the exact item after sign-in;
- a failed run produces exactly one push, not one per retry;
- no notification payload contains draft text, facts, tokens or personal data;
- with 20 pending approvals the operator receives one digest;
- nothing is sent during quiet hours except events the operator marked as always-send;
- removing a device stops push to it at once;
- every send appears as an Action with a grant reference.

## Tests
- Web Push against a local fake push service: subscribe, send, expired subscription removed.
- Payload scan: seeded sensitive strings never appear in any channel.
- Dedupe, grouping and digest thresholds.
- Quiet hours across a daylight-saving change (E-051).
- Deep link: unauthenticated, wrong role, other tenant.
- Tenant isolation: SELECT, INSERT, UPDATE, DELETE on Notification across tenants; a client cannot list another tenant's notifications.
- Broker: a send without the policy grant is refused; a paused tenant's client notifications are held.

## Rollback / failure recovery
Delivery failure never blocks the source workflow. Items remain in the inbox. Reverse migrations tested.

## Cost/resource budget
No model calls. Proposed default limits: 30 pushes and 5 emails per person per day before forced digest.

## Documentation updates
- `docs/architecture/notifications-and-attention.md`: it still says "push later"; update to the owner decision.
- `docs/security/network-and-service-exposure.md` (outbound to push services and the mail provider).

## Open decisions
- **Decision required (owner):** may the tenant or client name appear in a push on the lock screen? Proposed default: yes for the name, nothing else.
- **Decision required:** email provider for platform mail. Proposed default: one transactional provider chosen by dependency review at task start, on a sending subdomain of the control-plane domain with SPF, DKIM and DMARC.
- **Decision required:** quiet hours and digest time defaults. Proposed default: quiet 22:00 to 07:00 Asia/Karachi, digest at 08:00.
- **Decision required:** iOS support depends on the web app being installed to the home screen; confirm current Apple rules at task start.

## Definition of done
Everything in [definition-of-done.md](../../docs/delivery/definition-of-done.md), plus: the payload scan test is a protected test; a real push is received on the operator's phone in staging and recorded.
