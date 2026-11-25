# Canonical Knowledge, Facts and Memory


> **Presence OS engineering source of truth**
>
> Baseline date: **2026-08-08** (Asia/Karachi project context).
> Product architecture is intentionally model-, provider-, harness-, and ingress-neutral.
> Vendor capabilities, model names, prices, quotas, laws, and platform policies are time-sensitive reference facts and MUST be revalidated before implementation or purchase.
> When a focused document conflicts with an older discussion, the focused document plus the Decision Register and ADRs control.


## Canonical truth

Company facts may include:
- identity;
- locations;
- services/products;
- pricing;
- founders/team;
- credentials;
- reviews;
- customers where evidenced;
- contacts;
- values;
- claims;
- achievements.

Individual facts may include:
- skills;
- employment;
- education;
- projects;
- achievements;
- portfolio;
- career history;
- expertise;
- public work.

## External observation pipeline

External observations never automatically become canonical truth.

`External Observation → Candidate Fact → confidence/evidence evaluation → Canonical Fact`

Conflicting credible sources produce `CONFLICTED_FACT`, not silent last-write-wins.

## Fact metadata

- value
- source/evidence
- timestamp
- confidence
- owner
- freshness/expiry
- original language
- status
- supersedes/superseded_by where relevant

## Memory taxonomy

Keep separate:
- FACT
- PREFERENCE
- DECISION
- CONVERSATION_SUMMARY
- TASK_STATE

A conversation summary does not outrank a verified fact.

## User control

Provide:
- correction;
- deletion where applicable;
- supersession;
- provenance visibility;
- export.

Do not lose original evidence merely because a normalized fact exists.
