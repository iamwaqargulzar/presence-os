"""Tests against the Temporal service from compose.yaml. Run: make test-integration (needs Docker).

Timeouts are a few seconds of real time instead of the SDK's time-skipping server, because that server is a binary the
SDK downloads at run time without a checksum (ADR-0036)."""

import asyncio
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest import mock

from temporalio import activity
from temporalio.api.enums.v1 import EventType
from temporalio.api.history.v1 import HistoryEvent
from temporalio.client import WorkflowFailureError, WorkflowHandle
from temporalio.exceptions import ApplicationError, CancelledError
from temporalio.worker import Replayer, Worker

from presence_worker import activities, client
from presence_worker.contracts import (
    Decision,
    EffectInput,
    EffectResult,
    ReferenceInput,
    ReferenceResult,
    TenantContext,
)
from presence_worker.workflows import ReferenceWorkflow

HISTORY = Path(__file__).parent / "histories" / "reference_v1.json"
CTX = TenantContext("tenant-a", "profile-1", "trace-1")
WORKER_DIR = Path(__file__).resolve().parents[2]


def scheduled(history_events: list[HistoryEvent], activity_type: str) -> int:
    return sum(
        1
        for e in history_events
        if e.event_type == EventType.EVENT_TYPE_ACTIVITY_TASK_SCHEDULED
        and e.activity_task_scheduled_event_attributes.activity_type.name == activity_type
    )


def _key() -> str:
    # Under 10 characters so the recorded history does not trip the secret scanner's generic key rule.
    return f"r{time.time_ns() % 10**8:08d}"


class TemporalTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.artifacts = tmp.name
        patcher = mock.patch.dict("os.environ", {"PRESENCE_ARTIFACT_DIR": tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.queue = f"test-{uuid.uuid4().hex}"
        self.client = await client.connect()

    def worker(self, *acts: Callable[..., Any]) -> Worker:
        return Worker(
            self.client,
            task_queue=self.queue,
            workflows=[ReferenceWorkflow],
            activities=list(acts) or [activities.prepare_draft, activities.apply_effect],
        )

    async def start(self, timeout_s: float = 30) -> WorkflowHandle[ReferenceWorkflow, ReferenceResult]:
        with mock.patch.object(client, "TASK_QUEUE", self.queue):
            return await client.start_reference(self.client, ReferenceInput(CTX, _key(), timeout_s))

    async def test_approve_completes_and_history_holds_only_references(self) -> None:
        async with self.worker():
            handle = await self.start()
            await handle.signal(ReferenceWorkflow.decide, Decision(True, "operator"))
            result = await handle.result()
            history = await handle.fetch_history()
        self.assertEqual(result.outcome, "completed")
        assert result.effect is not None
        self.assertTrue(result.effect.first_time)
        self.assertGreater(result.draft.size, client.MAX_PAYLOAD_BYTES)
        self.assertLess(len(history.to_json()), client.MAX_PAYLOAD_BYTES)  # the 1 MiB draft is not in history
        await Replayer(workflows=[ReferenceWorkflow], data_converter=client.DATA_CONVERTER).replay_workflow(history)
        if os.environ.get("PRESENCE_RECORD_HISTORY") == "1":
            HISTORY.write_text(history.to_json())

    async def test_duplicate_start_returns_the_same_run(self) -> None:
        async with self.worker():
            inp = ReferenceInput(CTX, _key(), 30)
            with mock.patch.object(client, "TASK_QUEUE", self.queue):
                a = await client.start_reference(self.client, inp)
                b = await client.start_reference(self.client, inp)
            self.assertEqual(a.result_run_id, b.result_run_id)
            await a.signal(ReferenceWorkflow.decide, Decision(False, "operator"))
            self.assertEqual((await a.result()).outcome, "rejected")

    async def test_human_wait_times_out(self) -> None:
        async with self.worker():
            handle = await self.start(timeout_s=1)
            self.assertEqual((await handle.result()).outcome, "timed_out")

    async def test_cancel_during_human_wait(self) -> None:
        async with self.worker():
            handle = await self.start()
            await self.wait_for_activity_completed(handle, 1)
            await handle.cancel()
            with self.assertRaises(WorkflowFailureError) as err:
                await handle.result()
        self.assertIsInstance(err.exception.cause, CancelledError)

    async def test_cancel_during_activity(self) -> None:
        started, stopped = asyncio.Event(), asyncio.Event()

        @activity.defn(name="apply_effect")
        async def slow_effect(inp: EffectInput) -> EffectResult:
            started.set()
            try:
                while True:
                    activity.heartbeat()
                    await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                stopped.set()
                raise

        async with self.worker(activities.prepare_draft, slow_effect):
            handle = await self.start()
            await handle.signal(ReferenceWorkflow.decide, Decision(True, "operator"))
            await asyncio.wait_for(started.wait(), 10)
            await handle.cancel()
            with self.assertRaises(WorkflowFailureError) as err:
                await handle.result()
        self.assertIsInstance(err.exception.cause, CancelledError)
        self.assertTrue(stopped.is_set())

    async def test_retry_keeps_the_workflow_tenant(self) -> None:
        seen: list[tuple[int, TenantContext]] = []

        @activity.defn(name="apply_effect")
        async def flaky_effect(inp: EffectInput) -> EffectResult:
            seen.append((activity.info().attempt, inp.ctx))
            if activity.info().attempt == 1:
                raise ApplicationError("transient")
            return await activities.apply_effect(inp)

        async with self.worker(activities.prepare_draft, flaky_effect):
            handle = await self.start()
            await handle.signal(ReferenceWorkflow.decide, Decision(True, "operator"))
            self.assertEqual((await handle.result()).outcome, "completed")
        self.assertEqual([a for a, _ in seen], [1, 2])
        self.assertTrue(all(ctx == CTX for _, ctx in seen))

    async def test_killed_worker_resumes_without_repeating_checkpoint(self) -> None:
        """R0-010 recovery test: SIGKILL the worker process mid-workflow, start a new one, the run completes."""
        handle = await self.start()
        first = self.spawn_worker()
        try:
            await self.wait_for_activity_completed(handle, 1)
        finally:
            first.send_signal(signal.SIGKILL)
            first.wait()
        await handle.signal(ReferenceWorkflow.decide, Decision(True, "operator"))
        second = self.spawn_worker()
        try:
            result = await asyncio.wait_for(handle.result(), 60)
        finally:
            second.terminate()
            second.wait()
        self.assertEqual(result.outcome, "completed")
        events = [e async for e in handle.fetch_history_events()]
        self.assertEqual(scheduled(events, "prepare_draft"), 1)
        self.assertEqual(scheduled(events, "apply_effect"), 1)

    async def test_oversized_start_is_rejected_before_the_server(self) -> None:
        with self.assertRaises(client.PayloadTooLargeError):
            await client.start_reference(self.client, ReferenceInput(CTX, "x" * (client.MAX_PAYLOAD_BYTES + 1)))

    def spawn_worker(self) -> subprocess.Popen[bytes]:
        env = {**os.environ, "PRESENCE_TEMPORAL_TASK_QUEUE": self.queue, "PRESENCE_ARTIFACT_DIR": self.artifacts}
        return subprocess.Popen([sys.executable, "-m", "presence_worker"], cwd=WORKER_DIR, env=env)

    async def wait_for_activity_completed(self, handle: WorkflowHandle[Any, Any], count: int) -> None:
        for _ in range(200):
            events = [e async for e in handle.fetch_history_events()]
            if sum(1 for e in events if e.event_type == EventType.EVENT_TYPE_ACTIVITY_TASK_COMPLETED) >= count:
                return
            await asyncio.sleep(0.1)
        self.fail("activity did not complete in 20 s")
