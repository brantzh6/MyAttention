from fastapi import APIRouter

from conversation_runtime.contracts import (
    ConversationSegmentPanelInspectRequest,
    ConversationSegmentPanelInspectResponse,
    ConversationSegmentInspectRequest,
    ConversationSegmentInspectResponse,
    FlywheelExecutionFeedbackInspectRequest,
    FlywheelExecutionFeedbackInspectResponse,
    FlywheelInspectRequest,
    FlywheelInspectResponse,
    TaskPacketPreviewRequest,
    TaskPacketPreviewResponse,
)
from conversation_runtime.p0 import (
    run_conversation_segment_panel_inspect,
    run_conversation_segment_inspect,
)
from conversation_runtime.flywheel import (
    run_execution_feedback_inspect,
    run_flywheel_inspect,
    run_task_packet_preview,
)


router = APIRouter()


@router.post(
    "/conversation-runtime/segments/inspect",
    response_model=ConversationSegmentInspectResponse,
)
async def inspect_conversation_segment(
    body: ConversationSegmentInspectRequest,
):
    """
    Convert one bounded conversation segment into reviewable candidate objects.

    This route is inspect-only:
    - it does not persist objects
    - it does not mutate source plans
    - it does not promote raw conversation into canonical truth
    """
    return await run_conversation_segment_inspect(body)


@router.post(
    "/conversation-runtime/segments/panel/inspect",
    response_model=ConversationSegmentPanelInspectResponse,
)
async def inspect_conversation_segment_panel(
    body: ConversationSegmentPanelInspectRequest,
):
    """
    Run a bounded dual-lane panel inspect over one conversation segment.

    This route is still inspect-only:
    - it exposes agreement and disagreement shape
    - it does not persist outcomes
    - it does not create a canonical merged decision
    """
    return await run_conversation_segment_panel_inspect(body)


@router.post(
    "/conversation-runtime/flywheel/inspect",
    response_model=FlywheelInspectResponse,
)
async def inspect_flywheel(
    body: FlywheelInspectRequest,
):
    """
    Extract flywheel candidates from one bounded conversation segment.

    Bridges manual input toward: information -> knowledge -> evolution.

    This route is strictly inspect-only:
    - it does not persist objects
    - it does not mutate source plans or knowledge bases
    - it does not promote any candidate into canonical truth
    - it does not trigger automated workflows
    """
    return await run_flywheel_inspect(body)


@router.post(
    "/conversation-runtime/flywheel/task-packet/preview",
    response_model=TaskPacketPreviewResponse,
)
def preview_task_packet(
    body: TaskPacketPreviewRequest,
):
    """
    Generate a normalized inspect-only task-packet preview for controller discussion.

    Accepts manual decision input and returns a preview that can be used
    for human/controller next-step discussion without persistence or workflow execution.

    This route is strictly inspect-only:
    - it does not persist objects
    - it does not mutate any state
    - it does not trigger automated workflows
    - it does not perform automatic delegation
    - promotion_state is always inspect_only
    """
    return run_task_packet_preview(body)


@router.post(
    "/conversation-runtime/flywheel/execution-feedback/inspect",
    response_model=FlywheelExecutionFeedbackInspectResponse,
)
async def inspect_execution_feedback(
    body: FlywheelExecutionFeedbackInspectRequest,
):
    """
    Reflect one bounded worker execution result back into the flywheel.

    This route is strictly inspect-only:
    - it does not persist worker results
    - it does not mutate knowledge state
    - it does not auto-trigger a new workflow
    - it does not promote reflected candidates into canonical truth
    """
    return await run_execution_feedback_inspect(body)
