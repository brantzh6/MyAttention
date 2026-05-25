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
    candidate_packet: Optional["CandidatePacket"] = Field(
        None, description="Optional controller-ready candidate packet for mainline flywheel progression"
    )
    handoff_preview: Optional["ExecutionHandoffPreview"] = Field(
        None,
        description="Optional delegate-ready inspect-only handoff preview derived from candidate_packet",
    )


class CandidatePacket(BaseModel):
    """Controller-ready candidate packet for mainline flywheel progression.

    This is an inspect-only advisory shape that helps the controller
    hand off the next bounded implementation task without manual reinterpretation.
    """

    candidate_task_id: str = Field(
        "", description="Generated task ID for the candidate packet (non-canonical)"
    )
    candidate_lane: str = Field(
        "", description="Target lane for delegation: mainline_flywheel, knowledge_review, etc."
    )
    candidate_goal: str = Field(
        "", description="Clear goal statement for the candidate task"
    )
    allowed_files: List[str] = Field(
        default_factory=list, description="Bounded list of files the delegate may touch"
    )
    non_goals: List[str] = Field(
        default_factory=list, description="Explicit scope boundaries"
    )
    validation_commands: List[str] = Field(
        default_factory=list, description="Required validation commands"
    )
    review_gate: str = Field(
        "", description="Review gate requirement: local_delegated_L1, controller_absorption, etc."
    )
    stop_conditions: List[str] = Field(
        default_factory=list, description="Conditions that should halt the task"
    )
    delegation_target: str = Field(
        "", description="Target delegate lane: local coding delegate, etc."
    )
    truth_status: str = Field(
        "non_canonical", description="Always non_canonical; for advisory purposes only"
    )


class ExecutionHandoffPreview(BaseModel):
    """Delegate-ready handoff preview derived from a candidate packet.

    This remains inspect-only and advisory. It does not trigger execution,
    persistence, scheduling, or promotion.
    """

    task_id: str = Field("", description="Candidate task id to hand off")
    owner_lane: str = Field("", description="Target owner lane for the handoff")
    objective: str = Field("", description="Delegate-facing objective")
    current_evidence: List[str] = Field(
        default_factory=list,
        description="Evidence the delegate should treat as input context",
    )
    allowed_files: List[str] = Field(
        default_factory=list,
        description="Bounded file set for implementation",
    )
    non_goals: List[str] = Field(
        default_factory=list,
        description="Explicit non-goals for the handoff",
    )
    validation_commands: List[str] = Field(
        default_factory=list,
        description="Commands required before returning the result",
    )
    review_gate: str = Field("", description="Required review gate")
    expected_result_format: List[str] = Field(
        default_factory=list,
        description="Required fields the delegate must return",
    )
    stop_conditions: List[str] = Field(
        default_factory=list,
        description="Conditions requiring the delegate to stop and report",
    )
    delegation_target: str = Field("", description="Target delegate type")
    truth_status: str = Field("non_canonical", description="Advisory truth status")
    promotion_state: str = Field("inspect_only", description="Always inspect_only")
    # New metadata fields for delegate packet readiness
    sdlc_stage: str = Field(
        "code_implementation",
        description="SDLC stage: design, design_review, code_implementation, code_review, testing, promotion_decision, runtime_monitoring",
    )
    risk_level: str = Field(
        "R2",
        description="Risk level: R1 (low), R2 (default), R3 (high-risk escalation)",
    )
    result_artifact_path: str = Field(
        "",
        description="Expected path for the result artifact markdown file",
    )
    write_policy: str = Field(
        "result_only",
        description="Write policy: result_only (no persistence), bounded_patch (limited changes), full_implementation (requires controller approval)",
    )
    handoff_markdown: str = Field(
        "",
        description="Generated markdown body for controller inspection and delegate handoff",
    )


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
    completeness_status: str = "missing"
    provided_fields: List[str] = []
    missing_fields: List[str] = []


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
