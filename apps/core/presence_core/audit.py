"""Audit append path (R0-006, docs/security/audit-ledger.md). This is a long-lived internal contract.

Call `append_audit()` inside the transaction of the operation it records. If the write fails the exception
propagates, so the operation rolls back instead of proceeding unaudited. Tenant events need the matching
`tenant_context()`; the database rejects any other tenant. The runtime role can insert and (tenant events
only, under RLS) select, never update or delete.
"""

import logging
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID

from django.db import DEFAULT_DB_ALIAS, connections
from psycopg.types.json import Jsonb

from presence_core.observability import correlation, redact

logger = logging.getLogger("presence.audit")

Result = Literal["success", "denied", "failure"]


@dataclass(frozen=True, kw_only=True)
class AuditEvent:
    """Who or what did what, under whose authority, to which tenant, using which artifact, and what happened.

    Only `action`, `result` and `actor` are required. Correlation IDs left empty are taken from the current
    request or job (`observability.correlate`). Never put secrets or personal data here; strings and
    `detail` are redacted anyway.
    """

    action: str  # dotted event name from the catalogue, e.g. "auth.login"
    result: Result
    actor: str  # "user:<id>", "service:<name>" or "operator:<id>"; an ID, never an email
    tenant_id: UUID | None = None  # None: a platform event with no tenant
    profile_id: str | None = None
    authority_source: str | None = None  # e.g. "session", "grant:<id>", "break_glass"
    operator_context: str | None = None  # managed-operator acting for the tenant
    target: str | None = None
    policy_decision: str | None = None
    connection_id: str | None = None
    artifact_refs: Sequence[str] = ()
    rollback_ref: str | None = None
    break_glass_reason: str | None = None
    request_id: str | None = None
    trace_id: str | None = None
    workflow_id: str | None = None
    task_id: str | None = None
    action_id: str | None = None
    # Reserved attribution fields: filled once AI runs and the development controller exist.
    model: str | None = None
    harness: str | None = None
    reasoning_profile: str | None = None
    execution_profile_id: str | None = None
    development_run_id: str | None = None
    detail: Mapping[str, Any] = field(default_factory=dict)


def append_audit(event: AuditEvent, using: str = DEFAULT_DB_ALIAS) -> UUID:
    """Store `event` in the caller's transaction and return its ID. Raises if it cannot be stored."""
    connection = connections[using]
    if not connection.in_atomic_block:
        raise RuntimeError("append_audit must run inside the transaction of the operation it records")
    ids = correlation()
    # The tenant is never taken from context: a tenant event names its tenant explicitly.
    row: dict[str, Any] = {
        key: ids.get(key) if value is None and key != "tenant_id" else value for key, value in asdict(event).items()
    }
    row, _ = redact(row)  # keys and the tenant UUID come back unchanged; strings and detail are redacted
    row["detail"] = Jsonb(row["detail"])
    if event.tenant_id is None:
        table = "audit.platform_event"
        del row["tenant_id"], row["profile_id"]
    else:
        table = "audit.tenant_event"
    event_id = uuid.uuid4()
    row |= {"id": event_id, "occurred_at": datetime.now(UTC)}
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO {table} ({', '.join(row)}) VALUES ({', '.join(['%s'] * len(row))})",  # noqa: S608 (column names come from AuditEvent)
                list(row.values()),
            )
    except Exception:
        # Health signal; never log the event itself.
        logger.error("audit_write_failed", extra={"fields": {"action": event.action, "table": table}})
        raise
    return event_id
