"""Worker process: python -m presence_worker (needs a running Temporal service, see compose.yaml)."""

import asyncio
import logging

from temporalio.worker import Worker

from presence_worker.activities import apply_effect, prepare_draft
from presence_worker.client import TASK_QUEUE, connect
from presence_worker.workflows import ReferenceWorkflow


async def main() -> None:
    # shortcut: plain-text logs; R0-006 moves the worker to the shared JSON log format and OpenTelemetry metrics.
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    client = await connect()
    worker = Worker(
        client, task_queue=TASK_QUEUE, workflows=[ReferenceWorkflow], activities=[prepare_draft, apply_effect]
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
