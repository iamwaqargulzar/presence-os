"""Deterministic tests that need no Temporal server. Run: make test."""

import ast
import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from temporalio.api.common.v1 import Payload
from temporalio.client import WorkflowHistory
from temporalio.testing import ActivityEnvironment
from temporalio.worker import Replayer

from presence_worker import activities, workflows
from presence_worker.client import (
    DATA_CONVERTER,
    MAX_PAYLOAD_BYTES,
    PayloadLimitCodec,
    PayloadTooLargeError,
    workflow_id,
)
from presence_worker.contracts import ArtifactRef, EffectInput, PrepareInput, TenantContext

HISTORY = Path(__file__).parent / "histories" / "reference_v1.json"
CTX = TenantContext("tenant-a", "profile-1", "trace-1")


class ArtifactDirMixin(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        patcher = mock.patch.dict("os.environ", {"PRESENCE_ARTIFACT_DIR": tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.root = Path(tmp.name)


class ActivityTests(ArtifactDirMixin):
    def test_same_idempotency_key_gives_one_effect(self) -> None:
        env = ActivityEnvironment()
        inp = EffectInput(CTX, "reference/tenant-a/req-1/apply", ArtifactRef("ab" * 32, 1))
        first = asyncio.run(env.run(activities.apply_effect, inp))
        second = asyncio.run(env.run(activities.apply_effect, inp))
        self.assertTrue(first.first_time)
        self.assertFalse(second.first_time)
        self.assertEqual(len(list((self.root / "effects").rglob("*"))), 2)  # tenant dir + one record

    def test_checkpointed_stage_is_not_recomputed_on_retry(self) -> None:
        env = ActivityEnvironment()
        inp = PrepareInput(CTX, "req-1")
        with mock.patch.object(activities, "build_draft", wraps=activities.build_draft) as build:
            first = asyncio.run(env.run(activities.prepare_draft, inp))
            second = asyncio.run(env.run(activities.prepare_draft, inp))
        self.assertEqual(build.call_count, 1)
        self.assertEqual(first, second)
        self.assertGreater(first.size, MAX_PAYLOAD_BYTES)  # content is large; only the reference travels
        self.assertEqual(len(activities.read_artifact(first)), first.size)

    def test_tenants_do_not_share_effect_records(self) -> None:
        env = ActivityEnvironment()
        ref = ArtifactRef("ab" * 32, 1)
        a = asyncio.run(env.run(activities.apply_effect, EffectInput(CTX, "same-key", ref)))
        other = TenantContext("tenant-b", "profile-1", "trace-1")
        b = asyncio.run(env.run(activities.apply_effect, EffectInput(other, "same-key", ref)))
        self.assertTrue(a.first_time and b.first_time)


class ContractTests(unittest.TestCase):
    def test_oversized_payload_is_rejected(self) -> None:
        codec = PayloadLimitCodec()
        with self.assertRaises(PayloadTooLargeError):
            asyncio.run(codec.encode([Payload(data=b"x" * (MAX_PAYLOAD_BYTES + 1))]))
        self.assertEqual(len(asyncio.run(codec.encode([Payload(data=b"x" * 100)]))), 1)

    def test_tenant_context_rejects_unsafe_ids(self) -> None:
        for bad in ("", "a/b", "x" * 65, "a\nb"):
            with self.assertRaises(ValueError):
                TenantContext(bad, "p", "t")
        self.assertEqual(workflow_id("reference", CTX, "req-1"), "reference/tenant-a/req-1")

    def test_workflow_module_does_not_import_activities(self) -> None:
        tree = ast.parse(Path(workflows.__file__).read_text())
        imported = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        imported |= {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        self.assertFalse({m for m in imported if m and "activities" in m})
        self.assertFalse(imported & {"os", "time", "random", "pathlib", "uuid"})


class ReplayTests(unittest.TestCase):
    def test_recorded_history_replays_against_current_code(self) -> None:
        """Fails if a code change would break workflows already running (E-081). Regenerate only for a new version."""
        history = WorkflowHistory.from_json("reference-v1", HISTORY.read_text())
        replayer = Replayer(workflows=[workflows.ReferenceWorkflow], data_converter=DATA_CONVERTER)
        asyncio.run(replayer.replay_workflow(history))
