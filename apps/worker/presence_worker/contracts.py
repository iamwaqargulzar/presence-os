"""Small typed values that cross the workflow/activity boundary. Large data travels as an ArtifactRef, never inline."""

import re
from dataclasses import dataclass

_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


@dataclass(frozen=True)
class TenantContext:
    """Who a workflow runs for. Passed explicitly in every workflow and activity input, so a retry on any worker
    sees the same tenant. R0-003 turns it into the database tenant setting (see activities.tenant_scope)."""

    tenant_id: str
    profile_id: str
    trace_id: str

    def __post_init__(self) -> None:
        for name in ("tenant_id", "profile_id", "trace_id"):
            if not _SAFE_ID.match(getattr(self, name)):
                raise ValueError(f"{name} must match {_SAFE_ID.pattern}")


@dataclass(frozen=True)
class ArtifactRef:
    sha256: str
    size: int


@dataclass(frozen=True)
class ReferenceInput:
    ctx: TenantContext
    request_key: str
    approval_timeout_s: float = 7 * 24 * 3600


@dataclass(frozen=True)
class PrepareInput:
    ctx: TenantContext
    request_key: str


@dataclass(frozen=True)
class EffectInput:
    ctx: TenantContext
    idempotency_key: str
    draft: ArtifactRef


@dataclass(frozen=True)
class EffectResult:
    idempotency_key: str
    first_time: bool


@dataclass(frozen=True)
class Decision:
    approved: bool
    decided_by: str


@dataclass(frozen=True)
class ReferenceResult:
    outcome: str  # completed | rejected | timed_out
    draft: ArtifactRef
    effect: EffectResult | None = None
