"""Activities: every side effect lives here, is idempotent, and runs inside tenant_scope."""

import hashlib
import json
import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from temporalio import activity

from presence_worker.contracts import ArtifactRef, EffectInput, EffectResult, PrepareInput, TenantContext

logger = logging.getLogger("presence.worker")


def _root() -> Path:
    # shortcut: artifacts and effect records are local files; move to the object store and Postgres in R0-009/R1.
    return Path(os.environ.get("PRESENCE_ARTIFACT_DIR", "var/artifacts"))


def _key_path(kind: str, ctx: TenantContext, key: str) -> Path:
    return _root() / kind / ctx.tenant_id / hashlib.sha256(key.encode()).hexdigest()


def put_artifact(data: bytes) -> ArtifactRef:
    """Content-addressed store: the same bytes always give the same reference."""
    sha = hashlib.sha256(data).hexdigest()
    path = _root() / "blobs" / sha
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_bytes(data)
        tmp.replace(path)
    return ArtifactRef(sha, len(data))


def read_artifact(ref: ArtifactRef) -> bytes:
    return (_root() / "blobs" / ref.sha256).read_bytes()


@contextmanager
def tenant_scope(ctx: TenantContext) -> Iterator[None]:
    """Everything an activity does for a tenant runs inside this scope."""
    # shortcut: only logs the context; R0-003 opens a transaction here and sets the tenant with set_config(..., true).
    info = activity.info()
    fields = {
        "workflow_id": info.workflow_id,
        "run_id": info.workflow_run_id,
        "activity": info.activity_type,
        "attempt": info.attempt,
        "tenant_id": ctx.tenant_id,
        "profile_id": ctx.profile_id,
        "trace_id": ctx.trace_id,
    }
    logger.info("activity start %s", json.dumps(fields), extra={"fields": fields})
    yield


def revalidate(ctx: TenantContext, action: str) -> None:
    """Called before every delayed side effect, because authority may have changed while the workflow waited."""
    # shortcut: allows everything; the Action Broker (R1-003) checks authorization and tenant limits here.


def build_draft(request_key: str) -> bytes:
    """Stands in for an expensive stage (model call, research, rendering). Output is deliberately large."""
    return (request_key.encode() + b"\n") * ((1 << 20) // (len(request_key) + 1))


@activity.defn
async def prepare_draft(inp: PrepareInput) -> ArtifactRef:
    with tenant_scope(inp.ctx):
        marker = _key_path("checkpoints", inp.ctx, f"{activity.info().workflow_id}/{inp.request_key}")
        if marker.exists():  # an earlier attempt finished the work; do not recompute it
            return ArtifactRef(**json.loads(marker.read_text()))
        ref = put_artifact(build_draft(inp.request_key))
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(json.dumps({"sha256": ref.sha256, "size": ref.size}))
        return ref


@activity.defn
async def apply_effect(inp: EffectInput) -> EffectResult:
    with tenant_scope(inp.ctx):
        revalidate(inp.ctx, "reference.apply")
        path = _key_path("effects", inp.ctx, inp.idempotency_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:  # creating the record is the effect; O_EXCL makes a second attempt with the same key a no-op
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            return EffectResult(inp.idempotency_key, first_time=False)
        with os.fdopen(fd, "w") as f:
            f.write(inp.draft.sha256)
        return EffectResult(inp.idempotency_key, first_time=True)
