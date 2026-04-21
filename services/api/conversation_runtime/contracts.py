from typing import List, Optional

from pydantic import BaseModel, Field

from feeds.ai_judgment import (
    SourceCandidateJudgment,
    SourceDiscoveryJudgePanelInsights,
    SourceJudgmentSelectiveAbsorptionAdvice,
)
from feeds.source_contracts import (
    SourceDiscoveryCandidate,
    SourceDiscoveryFocus,
    SourceDiscoveryInterestBias,
)


class ConversationSegmentInspectRequest(BaseModel):
    conversation_text: str = Field(..., min_length=2)
    speaker_role: str = Field("user")
    topic: str = Field(..., min_length=2)
    task_intent: str = Field("")
    focus: SourceDiscoveryFocus = Field(SourceDiscoveryFocus.AUTHORITATIVE)
    interest_bias: Optional[SourceDiscoveryInterestBias] = Field(None)
    thread_id: str = Field("")
    provider: str = Field("qwen")
    model: str = Field("")
    max_source_candidates: int = Field(4, ge=0, le=8)


class CorrectionEventProposal(BaseModel):
    target_scope: str
    target_ref: str
    correction_content: str
    provenance_note: str = ""
    trust_state: str = "candidate"
    proposal_state: str = "proposed"
    review_gate: str = "controller_review_required"
    absorption_state: str = "not_absorbed"


class CorrectionEventJudgment(BaseModel):
    target_scope: str
    target_ref: str
    correction_content: str
    verdict: str
    rationale: str
    confidence: float


class ConversationOperationalAdvice(BaseModel):
    suggested_next_step: str = "no_action"
    controller_notes: List[str] = []


class ConversationControllerPacket(BaseModel):
    review_mode: str = "inspect_only"
    actionable_source_object_keys: List[str] = []
    actionable_correction_targets: List[str] = []
    reason_tags: List[str] = []
    advisory_scope: str = "inspect_compression_only"
    truth_status: str = "non_canonical"


class ConversationIntentTrace(BaseModel):
    raw_segment_intent: str = "other"
    source_candidates_before_compression: int = 0
    source_candidates_after_compression: int = 0
    dropped_source_object_keys: List[str] = []
    correction_events_extracted: int = 0
    conversation_window_truncated: bool = False
    trace_scope: str = "inspect_precompression_context"


class ConversationPanelIntentTrace(BaseModel):
    primary_raw_intent: str = "other"
    secondary_raw_intent: str = "other"
    merged_segment_intent: str = "other"
    source_candidates_before_compression: int = 0
    source_candidates_after_compression: int = 0
    dropped_source_object_keys: List[str] = []
    correction_events_before_merge: int = 0
    correction_events_after_merge: int = 0
    conversation_window_truncated: bool = False
    trace_scope: str = "panel_inspect_precompression_context"


class ConversationSegmentInspectResponse(BaseModel):
    topic: str
    task_intent: str = ""
    focus: SourceDiscoveryFocus
    interest_bias: SourceDiscoveryInterestBias = SourceDiscoveryInterestBias.AUTHORITY
    provider: str
    model: str
    segment_intent: str
    source_candidates: List[SourceDiscoveryCandidate] = []
    source_judgments: List[SourceCandidateJudgment] = []
    source_summary: str = ""
    correction_events: List[CorrectionEventProposal] = []
    correction_judgments: List[CorrectionEventJudgment] = []
    correction_summary: str = ""
    operational_advice: ConversationOperationalAdvice = ConversationOperationalAdvice()
    controller_packet: ConversationControllerPacket = ConversationControllerPacket()
    intent_trace: ConversationIntentTrace = ConversationIntentTrace()
    notes: List[str] = []
    truth_boundary: List[str] = []
    promotion_state: str = "inspect_only"


class ConversationSegmentPanelInspectRequest(BaseModel):
    conversation_text: str = Field(..., min_length=2)
    speaker_role: str = Field("user")
    topic: str = Field(..., min_length=2)
    task_intent: str = Field("")
    focus: SourceDiscoveryFocus = Field(SourceDiscoveryFocus.AUTHORITATIVE)
    interest_bias: Optional[SourceDiscoveryInterestBias] = Field(None)
    thread_id: str = Field("")
    primary_provider: str = Field("qwen")
    primary_model: str = Field("")
    secondary_provider: str = Field("anthropic")
    secondary_model: str = Field("")
    max_source_candidates: int = Field(4, ge=0, le=8)


class ConversationSegmentPanelInspectResponse(BaseModel):
    topic: str
    task_intent: str = ""
    focus: SourceDiscoveryFocus
    interest_bias: SourceDiscoveryInterestBias = SourceDiscoveryInterestBias.AUTHORITY
    primary_provider: str
    primary_model: str
    secondary_provider: str
    secondary_model: str
    segment_intent: str
    source_candidates: List[SourceDiscoveryCandidate] = []
    primary_judgments: List[SourceCandidateJudgment] = []
    secondary_judgments: List[SourceCandidateJudgment] = []
    primary_summary: str = ""
    secondary_summary: str = ""
    extraction_summary: dict[str, object] = {}
    panel_summary: dict[str, object] = {}
    panel_insights: SourceDiscoveryJudgePanelInsights = SourceDiscoveryJudgePanelInsights()
    selective_absorption: SourceJudgmentSelectiveAbsorptionAdvice = (
        SourceJudgmentSelectiveAbsorptionAdvice()
    )
    correction_events: List[CorrectionEventProposal] = []
    primary_correction_judgments: List[CorrectionEventJudgment] = []
    secondary_correction_judgments: List[CorrectionEventJudgment] = []
    primary_correction_summary: str = ""
    secondary_correction_summary: str = ""
    correction_panel_summary: dict[str, object] = {}
    operational_advice: ConversationOperationalAdvice = ConversationOperationalAdvice()
    controller_packet: ConversationControllerPacket = ConversationControllerPacket()
    intent_trace: ConversationPanelIntentTrace = ConversationPanelIntentTrace()
    notes: List[str] = []
    truth_boundary: List[str] = []
    promotion_state: str = "inspect_only"


# ---------------------------------------------------------------------------
# Flywheel inspect bounded object families
# ---------------------------------------------------------------------------


class KnowledgeDeltaCandidate(BaseModel):
    """Bounded proposal for a knowledge-layer delta extracted from conversation."""

    delta_type: str = Field(
        ...,
        description="Kind of knowledge delta: claim, concept, boundary, or relation",
    )
    label: str = Field(..., min_length=1, description="Short human-readable label")
    content: str = Field(..., min_length=1, description="Proposed delta content")
    provenance_note: str = "conversation-flywheel-inspect"
    trust_state: str = "candidate"
    proposal_state: str = "proposed"
    review_gate: str = "controller_review_required"
    absorption_state: str = "not_absorbed"


class EvolutionTriggerCandidate(BaseModel):
    """Bounded proposal for an evolution-layer trigger extracted from conversation."""

    trigger_type: str = Field(
        ...,
        description="Kind of evolution trigger: study, prototype, review, or source-strategy",
    )
    label: str = Field(..., min_length=1, description="Short human-readable label")
    rationale: str = Field("", description="Why this trigger is worth considering")
    provenance_note: str = "conversation-flywheel-inspect"
    trust_state: str = "candidate"
    proposal_state: str = "proposed"
    review_gate: str = "controller_review_required"
    absorption_state: str = "not_absorbed"


class FlywheelInspectRequest(BaseModel):
    """Request body for the flywheel inspect route."""

    conversation_text: str = Field(..., min_length=2)
    speaker_role: str = Field("user")
    topic: str = Field(..., min_length=2)
    task_intent: str = Field("")
    thread_id: str = Field("")
    provider: str = Field("qwen")
    model: str = Field("")


class FlywheelInspectResponse(BaseModel):
    """Response for the flywheel inspect route. Strictly inspect-only."""

    topic: str
    task_intent: str = ""
    provider: str
    model: str
    segment_intent: str = "other"
    source_candidates: List[SourceDiscoveryCandidate] = []
    correction_events: List[CorrectionEventProposal] = []
    knowledge_delta_candidates: List[KnowledgeDeltaCandidate] = []
    evolution_trigger_candidates: List[EvolutionTriggerCandidate] = []
    extraction_summary: str = ""
    operational_advice: ConversationOperationalAdvice = ConversationOperationalAdvice()
    controller_packet: ConversationControllerPacket = ConversationControllerPacket()
    notes: List[str] = []
    truth_boundary: List[str] = []
    promotion_state: str = "inspect_only"


# ---------------------------------------------------------------------------
# Task-packet preview bounded object families (controller-facing)
# ---------------------------------------------------------------------------


class SelectedLabelGroup(BaseModel):
    """Normalized representation of a selected label group."""

    label_type: str = Field(
        ..., description="Type of label: knowledge, evolution, or source"
    )
    labels: List[str] = Field(default_factory=list, description="Selected labels")
    count: int = Field(0, ge=0, description="Number of labels selected")


class TaskPacketPreviewRequest(BaseModel):
    """Request body for the task-packet preview route.

    Accepts manual decision input from controller and returns
    a normalized inspect-only task-packet preview.
    """

    topic: str = Field(..., min_length=1)
    task_intent: str = Field(..., min_length=1)
    selected_knowledge_labels: List[str] = Field(default_factory=list)
    selected_evolution_labels: List[str] = Field(default_factory=list)
    selected_source_labels: List[str] = Field(default_factory=list)
    reviewer_note: str = Field("")
    explicit_non_canonical: bool = Field(
        False, description="Explicitly mark this packet as non-canonical boundary"
    )


class TaskPacketPreviewResponse(BaseModel):
    """Response for the task-packet preview route.

    Returns a normalized inspect-only preview that can be used
    for human/controller next-step discussion.
    """

    task_packet_summary: str
    packet_intent: str = Field(
        ..., description="Derived intent: knowledge_driven, evolution_driven, source_driven, mixed, no_action, or manual_review"
    )
    suggested_lane: str = Field(
        ..., description="Suggested processing lane: knowledge_review, evolution_review, source_review, mixed_review, or no_action"
    )
    suggested_next_step: str
    selected_label_groups: List[SelectedLabelGroup] = []
    controller_packet: ConversationControllerPacket = ConversationControllerPacket()
    truth_boundary: List[str] = []
    promotion_state: str = "inspect_only"
    notes: List[str] = []


class FlywheelExecutionFeedbackInspectRequest(BaseModel):
    """Request body for worker-result feedback inspect."""

    topic: str = Field(..., min_length=1)
    task_intent: str = Field(..., min_length=1)
    worker_lane: str = Field(..., min_length=1)
    task_packet_summary: str = Field(..., min_length=1)
    execution_feedback_text: str = Field(..., min_length=2)
    execution_status_hint: str = Field("neutral")
    provider: str = Field("qwen")
    model: str = Field("")
    # Caller-provided provenance (inspect-only, not verified)
    worker_run_id: str = Field("", description="Caller-provided worker run ID (not verified)")
    worker_provider: str = Field("", description="Caller-provided worker provider (not verified)")
    worker_model: str = Field("", description="Caller-provided worker model (not verified)")
    worker_artifact_ref: str = Field("", description="Caller-provided artifact reference (not verified)")


class WorkerProvenance(BaseModel):
    """Inspect-only provenance context for worker execution feedback.

    This provenance is caller-provided and explicitly NOT verified
    by this endpoint. It is included for human/controller reference
    only and does not affect truth state or promotion semantics.
    """

    worker_run_id: str = ""
    worker_provider: str = ""
    worker_model: str = ""
    worker_artifact_ref: str = ""
    provenance_source: str = "caller_provided"
    verified: bool = False


class FlywheelExecutionFeedbackInspectResponse(BaseModel):
    """Inspect-only execution feedback reflection surface."""

    topic: str
    task_intent: str
    worker_lane: str
    execution_status_hint: str
    provider: str
    model: str
    feedback_intent: str = "other"
    feedback_summary: str = ""
    knowledge_delta_candidates: List[KnowledgeDeltaCandidate] = []
    evolution_trigger_candidates: List[EvolutionTriggerCandidate] = []
    operational_advice: ConversationOperationalAdvice = ConversationOperationalAdvice()
    controller_packet: ConversationControllerPacket = ConversationControllerPacket()
    notes: List[str] = []
    truth_boundary: List[str] = []
    promotion_state: str = "inspect_only"
    provenance: WorkerProvenance = WorkerProvenance()
