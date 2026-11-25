# Incident Management

Severity should be based on user/security/business impact.

Example classes:
- SEV0: active cross-tenant/security compromise, destructive widespread action
- SEV1: major production outage/data integrity risk
- SEV2: significant degraded capability
- SEV3: limited defect/workaround exists

## Initial response

1. stop/contain harmful automation;
2. preserve evidence/audit;
3. revoke credentials/grants if relevant;
4. isolate affected tenant/service;
5. communicate internally;
6. restore safe service;
7. validate integrity;
8. post-incident review.

For agent-caused incidents, capture execution profile, prompts/context references, tools, authority grant and action trace.

## Postmortem

Blameless about people, precise about systems.
Include:
- timeline;
- impact;
- root/contributing causes;
- detection;
- response;
- missed safeguards;
- action items with owners/dates;
- PresenceBench regression case where applicable.
