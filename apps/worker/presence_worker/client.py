"""Client side: connection, payload limit and the workflow start interface."""

import dataclasses
import os
from collections.abc import Sequence

import temporalio.converter
from temporalio.api.common.v1 import Payload
from temporalio.client import Client, WorkflowHandle
from temporalio.common import WorkflowIDConflictPolicy, WorkflowIDReusePolicy

from presence_worker.contracts import ReferenceInput, ReferenceResult, TenantContext
from presence_worker.workflows import ReferenceWorkflow

TASK_QUEUE = os.environ.get("PRESENCE_TEMPORAL_TASK_QUEUE", "presence-default")
# History must carry references, not content. Anything bigger than this is rejected before it reaches the server.
MAX_PAYLOAD_BYTES = 64 * 1024


class PayloadTooLargeError(ValueError):
    pass


class PayloadLimitCodec(temporalio.converter.PayloadCodec):
    async def encode(self, payloads: Sequence[Payload]) -> list[Payload]:
        for p in payloads:
            if p.ByteSize() > MAX_PAYLOAD_BYTES:
                raise PayloadTooLargeError(
                    f"payload {p.ByteSize()} bytes > {MAX_PAYLOAD_BYTES}; store it as an artifact"
                )
        return list(payloads)

    async def decode(self, payloads: Sequence[Payload]) -> list[Payload]:
        return list(payloads)


DATA_CONVERTER = dataclasses.replace(temporalio.converter.default(), payload_codec=PayloadLimitCodec())


async def connect() -> Client:
    address = os.environ.get(
        "PRESENCE_TEMPORAL_ADDRESS", f"127.0.0.1:{os.environ.get('PRESENCE_TEMPORAL_PORT', '17233')}"
    )
    return await Client.connect(address, namespace="default", data_converter=DATA_CONVERTER)


def workflow_id(kind: str, ctx: TenantContext, business_key: str) -> str:
    """Same business request, same ID: a repeated start returns the existing run instead of starting a second one."""
    return f"{kind}/{ctx.tenant_id}/{business_key}"


async def start_reference(client: Client, inp: ReferenceInput) -> WorkflowHandle[ReferenceWorkflow, ReferenceResult]:
    return await client.start_workflow(
        ReferenceWorkflow.run,
        inp,
        id=workflow_id("reference", inp.ctx, inp.request_key),
        task_queue=TASK_QUEUE,
        id_conflict_policy=WorkflowIDConflictPolicy.USE_EXISTING,
        id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
    )
