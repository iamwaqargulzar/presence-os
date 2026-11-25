"""Workflow definitions only: deterministic code, no I/O. Activities are called by name so this module never
imports activity code. See docs/architecture/how-to-write-a-workflow.md."""

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from presence_worker.contracts import (
        ArtifactRef,
        Decision,
        EffectInput,
        EffectResult,
        PrepareInput,
        ReferenceInput,
        ReferenceResult,
    )


@workflow.defn(name="Reference")
class ReferenceWorkflow:
    """Prepare a draft (checkpointed), wait for a human decision with a timeout, then apply one idempotent effect."""

    def __init__(self) -> None:
        self._decision: Decision | None = None

    @workflow.signal
    def decide(self, decision: Decision) -> None:
        # A signal only records the decision; apply_effect revalidates authority before acting (ADR-0003).
        if self._decision is None:
            self._decision = decision

    @workflow.run
    async def run(self, inp: ReferenceInput) -> ReferenceResult:
        # Checkpoint: the result is a reference in history, so a restarted worker never recomputes this stage.
        draft = await workflow.execute_activity(
            "prepare_draft",
            PrepareInput(inp.ctx, inp.request_key),
            result_type=ArtifactRef,
            start_to_close_timeout=timedelta(minutes=5),
        )
        try:
            await workflow.wait_condition(
                lambda: self._decision is not None, timeout=timedelta(seconds=inp.approval_timeout_s)
            )
        except TimeoutError:
            return ReferenceResult("timed_out", draft)
        if self._decision is None or not self._decision.approved:
            return ReferenceResult("rejected", draft)
        effect = await workflow.execute_activity(
            "apply_effect",
            EffectInput(inp.ctx, f"{workflow.info().workflow_id}/apply", draft),
            result_type=EffectResult,
            start_to_close_timeout=timedelta(minutes=1),
            retry_policy=RetryPolicy(initial_interval=timedelta(milliseconds=200), maximum_attempts=5),
            cancellation_type=workflow.ActivityCancellationType.WAIT_CANCELLATION_COMPLETED,
        )
        return ReferenceResult("completed", draft, effect)
