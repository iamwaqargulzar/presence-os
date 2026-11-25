"""Audit events emitted by the identity kernel (R0-004).

Field names match R0-006's `presence_core.audit.AuditEvent`, so the swap is one import.
"""

import logging
from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import UUID

logger = logging.getLogger("presence.audit")


@dataclass(frozen=True, kw_only=True)
class AuditEvent:
    action: str  # auth.login, auth.login_failed, auth.logout, auth.profile_switch, tenant.created, membership.changed
    result: str  # success | denied | failure
    actor: str  # "user:<person id>" or "anonymous"
    tenant_id: UUID | None = None
    profile_id: UUID | None = None
    detail: dict[str, Any] = field(default_factory=dict)  # never emails, tokens or names


def emit_audit(event: AuditEvent) -> None:
    # shortcut: logs a structured line until R0-006 merges; then call presence_core.audit.append_audit(event)
    # inside the operation's transaction, so a failed audit write rolls the operation back.
    logger.info("audit", extra={"fields": {"audit": asdict(event)}})
