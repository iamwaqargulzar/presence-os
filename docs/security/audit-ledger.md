# Audit Ledger

Audit is append-oriented and human-readable. Audit records must help answer:
“Who or what did what, under whose authority, to which tenant, using which artifact, and what happened?”

Sensitive values are redacted or referenced, not dumped.

Built in R0-006 ([ADR-0038](../adrs/ADR-0038-audit-and-trace-correlation.md)). Code: `apps/core/presence_core/audit.py`.

## Storage
- Schema `audit`, owned by `presence_migrator`.
- `audit.tenant_event`: events about one tenant. FORCE row-level security on `tenant_id`, like every tenant table (ADR-0036). The runtime role `presence_app` may INSERT and SELECT, only inside the matching `tenant_context()`.
- `audit.platform_event`: events with no tenant (for example a failed sign-in before the tenant is known). `presence_app` may INSERT only; it cannot read them back.
- Neither table grants UPDATE, DELETE or TRUNCATE to `presence_app`. A test proves each is rejected.
- Retention is not decided; nothing deletes audit rows in R0.
- Expected row size: about 0.5–1 KB (mostly short text and a small `detail` object).
- Not built: tamper-evident hashing, external anchoring, a tenant-facing read API, an operator audit-reader role.

## Fields
Every row has `id`, `occurred_at` (UTC, set by the application) and the fields below. Only `action`, `result` and `actor` are required.

| Field | Meaning |
|---|---|
| `action` | Dotted event name from the catalogue below. |
| `result` | `success`, `denied` or `failure`. |
| `actor` | `user:<id>`, `service:<name>` or `operator:<id>`. An ID, never an email. |
| `tenant_id` | The tenant the event is about. Empty means a platform event. Never taken from context. |
| `profile_id` | Profile in that tenant (tenant events only). |
| `authority_source` | Where the authority came from: `session`, `grant:<id>`, `break_glass`. |
| `operator_context` | The managed operator acting for the tenant, if any. |
| `target` | What was acted on or where it went. |
| `policy_decision` | The policy result that allowed or denied it. |
| `connection_id` | The connection used. |
| `artifact_refs` | References to artifacts, never their content. |
| `rollback_ref` | Rollback or revocation reference. |
| `break_glass_reason` | Required reason when authority is break-glass. |
| `request_id`, `trace_id`, `workflow_id`, `task_id`, `action_id` | Correlation IDs. Filled from the current request or job when left empty. |
| `model`, `harness`, `reasoning_profile`, `execution_profile_id`, `development_run_id` | Reserved for AI and development-controller attribution. |
| `detail` | Small JSON object with event-specific facts. |

Every string and the whole `detail` object pass through the redaction layer before they are written ([observability](../infrastructure/observability.md#redaction)).

## Event catalogue
| Action | Emitted by | Result values |
|---|---|---|
| `auth.login` | Google sign-in (R0-004) | success |
| `auth.login_failed` | Google sign-in (R0-004); platform event when no tenant is known | failure, denied |
| `auth.logout` | sign-out (R0-004) | success |
| `auth.profile_switch` | profile switch (R0-004) | success, denied |
| `workflow.start` | workflow runner (R0-005) | success, failure |
| `workflow.complete` | workflow runner (R0-005) | success, failure |

The emitting tasks wire these events in; the names are fixed here so they stay stable. Add a row here before emitting a new action.

## How to emit an audit event
```python
from django.db import transaction
from presence_core.audit import AuditEvent, append_audit
from presence_core.tenancy import tenant_context

with tenant_context(tenant_id):            # opens the transaction and sets the tenant
    profile.switch_to(new_profile)         # the operation being recorded
    append_audit(AuditEvent(
        action="auth.profile_switch",
        result="success",
        actor=f"user:{user.id}",
        tenant_id=tenant_id,
        profile_id=str(new_profile.id),
        authority_source="session",
    ))
```

Rules:
1. Call `append_audit` inside the same transaction as the operation. It refuses to run outside one. If the write fails, it logs `audit_write_failed` and raises, so the operation rolls back instead of proceeding unaudited.
2. A tenant event needs `tenant_context()` for the same tenant; the database rejects any other tenant.
3. A platform event leaves `tenant_id` empty and runs in a plain `transaction.atomic()`.
4. Put IDs and references in the event, never secrets, tokens, passwords, emails or document content. Redaction is a safety net, not permission.
5. Leave correlation IDs empty; they come from `correlate()` (set by the request middleware and `tenant_context`). A job sets them with `with correlate(workflow_id=..., task_id=...):`.
