# Notifications and Attention

Notifications are not the same as AttentionItems.

## AttentionItem

A product-level synthesized item with:
- priority;
- profile/tenant;
- source module;
- evidence;
- recommended action;
- expiry/freshness;
- status.

## Notification

A delivery attempt through:
- in-app;
- email;
- push later;
- voice/event later.

Notification policies should avoid nagging.

Deduplicate repeated findings and aggregate when possible.

Urgency comes from consequence/time sensitivity, not an LLM's dramatic wording.
