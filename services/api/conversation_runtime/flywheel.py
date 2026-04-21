"""Bounded AI-entry flywheel inspect slice.

Bridges manual conversation input toward the short-term IKE flywheel:
    information -> knowledge -> evolution

This module is strictly inspect-only:
- no persistence
- no source-plan mutation
- no canonical truth promotion
- no workflow automation
"""

from typing import Any, List

from conversation_runtime.contracts import (
    ConversationControllerPacket,
    ConversationOperationalAdvice,
    CorrectionEventProposal,
    EvolutionTriggerCandidate,
    FlywheelExecutionFeedbackInspectRequest,
    FlywheelExecutionFeedbackInspectResponse,
    FlywheelInspectRequest,
    FlywheelInspectResponse,
    KnowledgeDeltaCandidate,
    SelectedLabelGroup,
    TaskPacketPreviewRequest,
    TaskPacketPreviewResponse,
    WorkerProvenance,
)
from conversation_runtime.p0 import (
    _build_conversation_sample_snippet,
    _normalize_correction_events,
    _prepare_conversation_window,
    conversation_truth_boundary,
)
from feeds.ai_judgment import (
    default_model_for_provider,
    parse_ai_judgment_payload,
)
from feeds.source_semantics import ai_judgment_truth_boundary
from llm.adapter import LLMAdapter


_ALLOWED_KNOWLEDGE_DELTA_TYPES = {"claim", "concept", "boundary", "relation"}
_ALLOWED_EVOLUTION_TRIGGER_TYPES = {"study", "prototype", "review", "source-strategy"}
_MAX_KNOWLEDGE_DELTAS = 6
_MAX_EVOLUTION_TRIGGERS = 4


def flywheel_truth_boundary() -> List[str]:
    return [
        "flywheel inspect output is candidate material only, not canonical knowledge",
        "knowledge delta candidates are bounded proposals, not accepted knowledge state",
        "evolution trigger candidates are bounded suggestions, not scheduled actions",
        "flywheel inspect does not auto-promote any candidate into canonical truth",
        "controller packet is advisory compression, not a workflow contract",
    ]


def _build_flywheel_extraction_prompt(body: FlywheelInspectRequest) -> str:
    conversation_window, truncated = _prepare_conversation_window(body.conversation_text)
    return (
        "You are extracting flywheel candidates from one bounded conversation segment for IKE.\n"
        "Return valid JSON only.\n"
        "The flywheel has three layers: information -> knowledge -> evolution.\n\n"
        "Extract:\n"
        "1. source_candidates: URLs or references worth tracking (same as segment inspect).\n"
        "   Each has url and context_note.\n"
        "2. correction_events: bounded source corrections with target_scope (source_authority, "
        "source_status, source_plan_item), target_ref, correction_content.\n"
        "3. knowledge_delta_candidates: knowledge-layer deltas.\n"
        "   Each has delta_type (claim|concept|boundary|relation), label, content.\n"
        "   Use claim for factual assertions. concept for named ideas. boundary for scope/edge "
        "clarifications. relation for connections between entities.\n"
        "4. evolution_trigger_candidates: evolution-layer triggers.\n"
        "   Each has trigger_type (study|prototype|review|source-strategy), label, rationale.\n"
        "   Use study for things worth investigating. prototype for small experiments to try. "
        "review for areas needing deeper review. source-strategy for source monitoring changes.\n"
        "5. intent: flywheel_signal if any knowledge or evolution candidates exist, "
        "otherwise source_hint, correction, or other.\n"
        "6. summary: one-line summary of what was extracted.\n\n"
        "Schema:\n"
        "{\n"
        '  "intent": "flywheel_signal|source_hint|correction|other",\n'
        '  "summary": "...",\n'
        '  "source_candidates": [{"url": "...", "context_note": "..."}],\n'
        '  "correction_events": [{"target_scope": "...", "target_ref": "...", '
        '"correction_content": "..."}],\n'
        '  "knowledge_delta_candidates": [{"delta_type": "claim|concept|boundary|relation", '
        '"label": "...", "content": "..."}],\n'
        '  "evolution_trigger_candidates": [{"trigger_type": "study|prototype|review|source-strategy", '
        '"label": "...", "rationale": "..."}]\n'
        "}\n\n"
        f"Topic: {body.topic}\n"
        f"Task intent: {body.task_intent}\n"
        f"Speaker role: {body.speaker_role}\n"
        f"Conversation window truncated: {'yes' if truncated else 'no'}\n"
        f"Conversation:\n{conversation_window}\n"
    )


def _normalize_knowledge_delta_candidates(
    payload: dict[str, Any],
) -> List[KnowledgeDeltaCandidate]:
    candidates: List[KnowledgeDeltaCandidate] = []
    raw_items = list(payload.get("knowledge_delta_candidates", []))
    for raw in raw_items[:_MAX_KNOWLEDGE_DELTAS]:
        if not isinstance(raw, dict):
            continue
        delta_type = str(raw.get("delta_type", "")).strip().lower()
        label = str(raw.get("label", "")).strip()
        content = str(raw.get("content", "")).strip()
        if delta_type not in _ALLOWED_KNOWLEDGE_DELTA_TYPES:
            continue
        if not label or not content:
            continue
        candidates.append(
            KnowledgeDeltaCandidate(
                delta_type=delta_type,
                label=label,
                content=content,
            )
        )
    return candidates


def _normalize_evolution_trigger_candidates(
    payload: dict[str, Any],
) -> List[EvolutionTriggerCandidate]:
    candidates: List[EvolutionTriggerCandidate] = []
    raw_items = list(payload.get("evolution_trigger_candidates", []))
    for raw in raw_items[:_MAX_EVOLUTION_TRIGGERS]:
        if not isinstance(raw, dict):
            continue
        trigger_type = str(raw.get("trigger_type", "")).strip().lower()
        label = str(raw.get("label", "")).strip()
        rationale = str(raw.get("rationale", "")).strip()
        if trigger_type not in _ALLOWED_EVOLUTION_TRIGGER_TYPES:
            continue
        if not label:
            continue
        candidates.append(
            EvolutionTriggerCandidate(
                trigger_type=trigger_type,
                label=label,
                rationale=rationale,
            )
        )
    return candidates


def _derive_flywheel_operational_advice(
    knowledge_deltas: List[KnowledgeDeltaCandidate],
    evolution_triggers: List[EvolutionTriggerCandidate],
    source_candidates_count: int,
    correction_events_count: int,
    segment_intent: str,
) -> ConversationOperationalAdvice:
    notes: List[str] = []

    if knowledge_deltas:
        notes.append(
            f"{len(knowledge_deltas)} knowledge delta candidate(s) extracted for review"
        )
    if evolution_triggers:
        notes.append(
            f"{len(evolution_triggers)} evolution trigger candidate(s) extracted for review"
        )

    has_knowledge = bool(knowledge_deltas)
    has_evolution = bool(evolution_triggers)
    has_sources = source_candidates_count > 0
    has_corrections = correction_events_count > 0

    if has_knowledge and has_evolution:
        next_step = "review_flywheel_candidates"
    elif has_knowledge:
        next_step = "review_knowledge_deltas"
    elif has_evolution:
        next_step = "review_evolution_triggers"
    elif has_sources:
        next_step = "review_source_candidates"
        notes.append("no knowledge or evolution candidates; source-level candidates only")
    elif has_corrections:
        next_step = "review_corrections"
        notes.append("no knowledge or evolution candidates; corrections only")
    elif segment_intent == "other":
        next_step = "no_action"
        notes.append("segment classified as other; no flywheel candidates to promote")
    else:
        next_step = "manual_review"
        notes.append("segment produced no actionable candidates")

    return ConversationOperationalAdvice(
        suggested_next_step=next_step,
        controller_notes=notes,
    )


def _build_flywheel_controller_packet(
    knowledge_deltas: List[KnowledgeDeltaCandidate],
    evolution_triggers: List[EvolutionTriggerCandidate],
    operational_advice: ConversationOperationalAdvice,
) -> ConversationControllerPacket:
    actionable_knowledge = [
        f"{d.delta_type}:{d.label}" for d in knowledge_deltas
    ]
    actionable_triggers = [
        f"{t.trigger_type}:{t.label}" for t in evolution_triggers
    ]
    reason_tags: List[str] = []
    if actionable_knowledge:
        reason_tags.append("knowledge_delta_review")
    if actionable_triggers:
        reason_tags.append("evolution_trigger_review")
    if operational_advice.suggested_next_step == "manual_review":
        reason_tags.append("manual_review_required")
    if not reason_tags:
        reason_tags.append("no_action")
    return ConversationControllerPacket(
        review_mode=operational_advice.suggested_next_step,
        actionable_source_object_keys=[],
        actionable_correction_targets=actionable_knowledge + actionable_triggers,
        reason_tags=reason_tags,
        advisory_scope="flywheel_inspect_only",
        truth_status="non_canonical",
    )


async def run_flywheel_inspect(
    body: FlywheelInspectRequest,
) -> FlywheelInspectResponse:
    adapter = LLMAdapter()
    model = body.model.strip() or default_model_for_provider(body.provider)
    _, conversation_window_truncated = _prepare_conversation_window(body.conversation_text)

    raw = await adapter.chat(
        message=_build_flywheel_extraction_prompt(body),
        provider=body.provider,
        model=model,
        system_prompt="Return valid JSON only.",
    )
    payload, parse_status = parse_ai_judgment_payload(raw)

    allowed_intents = {"flywheel_signal", "source_hint", "correction", "other"}
    segment_intent = str(payload.get("intent", "")).strip().lower()
    if segment_intent not in allowed_intents:
        segment_intent = "other"

    # Reuse P0 normalization for source-level objects
    source_candidates_raw = list(payload.get("source_candidates", []))
    correction_events, discarded_corrections = _normalize_correction_events(payload)

    # Build source candidates using P0 helper pattern (lightweight, no authority classifier)
    from feeds.source_contracts import SourceDiscoveryCandidate, SourceDiscoveryFocus
    from feeds.source_semantics import candidate_identity, focus_category

    source_candidates: List[SourceDiscoveryCandidate] = []
    for raw_candidate in source_candidates_raw[:4]:
        if not isinstance(raw_candidate, dict):
            continue
        url = str(raw_candidate.get("url", "")).strip()
        context_note = str(raw_candidate.get("context_note", "")).strip()
        if not url:
            continue
        item_type, object_key, display_name, canonical_url, source_domain = candidate_identity(
            url, SourceDiscoveryFocus.AUTHORITATIVE
        )
        source_candidates.append(
            SourceDiscoveryCandidate(
                item_type=item_type,
                object_key=object_key,
                domain=source_domain,
                name=display_name,
                url=canonical_url,
                authority_tier="B",
                authority_score=0.5,
                recommendation="review",
                recommendation_reason="flywheel-inspect-derived",
                evidence_count=1,
                matched_queries=[body.topic],
                sample_titles=[context_note or display_name],
                sample_snippets=[_build_conversation_sample_snippet(body.conversation_text)],
                source_nature="conversation_hint",
                temperature="medium",
                recommended_mode="inspect",
                recommended_execution_strategy="review_first",
                why_relevant=context_note or "derived from bounded conversation segment",
                confidence_note="flywheel-inspect single-segment extraction",
                canonical_ref=object_key,
                candidate_endpoints=[canonical_url],
            )
        )

    # Extract knowledge and evolution candidates
    knowledge_deltas = _normalize_knowledge_delta_candidates(payload)
    evolution_triggers = _normalize_evolution_trigger_candidates(payload)
    extraction_summary = str(payload.get("summary", "")).strip()

    # Build operational advice and controller packet
    operational_advice = _derive_flywheel_operational_advice(
        knowledge_deltas=knowledge_deltas,
        evolution_triggers=evolution_triggers,
        source_candidates_count=len(source_candidates),
        correction_events_count=len(correction_events),
        segment_intent=segment_intent,
    )
    controller_packet = _build_flywheel_controller_packet(
        knowledge_deltas=knowledge_deltas,
        evolution_triggers=evolution_triggers,
        operational_advice=operational_advice,
    )

    notes = [
        f"conversation_parse_status={parse_status}",
        f"segment_intent={segment_intent}",
        f"source_candidates={len(source_candidates)}",
        f"correction_events={len(correction_events)}",
        f"discarded_corrections={discarded_corrections}",
        f"knowledge_delta_candidates={len(knowledge_deltas)}",
        f"evolution_trigger_candidates={len(evolution_triggers)}",
        f"conversation_window_truncated={str(conversation_window_truncated).lower()}",
    ]

    truth_boundary = conversation_truth_boundary()
    truth_boundary.extend(ai_judgment_truth_boundary())
    truth_boundary.extend(flywheel_truth_boundary())

    return FlywheelInspectResponse(
        topic=body.topic,
        task_intent=body.task_intent,
        provider=body.provider,
        model=model,
        segment_intent=segment_intent,
        source_candidates=source_candidates,
        correction_events=correction_events,
        knowledge_delta_candidates=knowledge_deltas,
        evolution_trigger_candidates=evolution_triggers,
        extraction_summary=extraction_summary,
        operational_advice=operational_advice,
        controller_packet=controller_packet,
        notes=notes,
        truth_boundary=truth_boundary,
    )


# ---------------------------------------------------------------------------
# Task-packet preview bounded slice (controller-facing)
# ---------------------------------------------------------------------------


def _task_packet_preview_truth_boundary() -> List[str]:
    return [
        "task-packet preview is inspect-only, not a workflow contract",
        "suggested lane and next step are advisory, not automated decisions",
        "selected label groups are normalized inputs, not persisted state",
        "controller packet is compression for human review, not execution",
        "promotion state is fixed to inspect_only; no automatic promotion",
    ]


def _execution_feedback_truth_boundary() -> List[str]:
    return [
        "execution feedback inspect is candidate reflection only, not accepted outcome state",
        "execution feedback does not auto-absorb worker results into canonical knowledge",
        "execution feedback does not auto-trigger new workflow execution",
        "execution feedback controller packet is advisory compression, not a promotion contract",
        "promotion state is fixed to inspect_only; no automatic promotion",
        "worker provenance is caller-provided and not verified by this endpoint",
        "provenance fields (worker_run_id, worker_provider, worker_model, worker_artifact_ref) are inspect-only context",
    ]


def _normalize_selected_labels(
    knowledge_labels: List[str],
    evolution_labels: List[str],
    source_labels: List[str],
) -> List[SelectedLabelGroup]:
    """Normalize selected label inputs into structured groups."""
    groups: List[SelectedLabelGroup] = []

    if knowledge_labels:
        normalized = [str(label).strip() for label in knowledge_labels if str(label).strip()]
        if normalized:
            groups.append(
                SelectedLabelGroup(
                    label_type="knowledge",
                    labels=normalized,
                    count=len(normalized),
                )
            )

    if evolution_labels:
        normalized = [str(label).strip() for label in evolution_labels if str(label).strip()]
        if normalized:
            groups.append(
                SelectedLabelGroup(
                    label_type="evolution",
                    labels=normalized,
                    count=len(normalized),
                )
            )

    if source_labels:
        normalized = [str(label).strip() for label in source_labels if str(label).strip()]
        if normalized:
            groups.append(
                SelectedLabelGroup(
                    label_type="source",
                    labels=normalized,
                    count=len(normalized),
                )
            )

    return groups


def _derive_packet_intent(
    knowledge_count: int,
    evolution_count: int,
    source_count: int,
) -> str:
    """Derive packet intent from label counts using bounded heuristic."""
    has_knowledge = knowledge_count > 0
    has_evolution = evolution_count > 0
    has_sources = source_count > 0

    if has_knowledge and has_evolution:
        return "mixed"
    if has_knowledge:
        return "knowledge_driven"
    if has_evolution:
        return "evolution_driven"
    if has_sources:
        return "source_driven"
    return "no_action"


def _derive_suggested_lane(packet_intent: str) -> str:
    """Map packet intent to suggested processing lane."""
    lane_map = {
        "knowledge_driven": "knowledge_review",
        "evolution_driven": "evolution_review",
        "source_driven": "source_review",
        "mixed": "mixed_review",
        "no_action": "no_action",
        "manual_review": "manual_review",
    }
    return lane_map.get(packet_intent, "manual_review")


def _derive_suggested_next_step(
    packet_intent: str,
    reviewer_note: str,
) -> str:
    """Derive suggested next step for controller discussion."""
    if packet_intent == "no_action":
        if reviewer_note:
            return "manual_review_with_note"
        return "no_action"
    if packet_intent == "mixed":
        return "prioritize_and_sequence"
    if packet_intent == "knowledge_driven":
        return "review_knowledge_candidates"
    if packet_intent == "evolution_driven":
        return "review_evolution_candidates"
    if packet_intent == "source_driven":
        return "review_source_candidates"
    return "manual_review"


def _build_task_packet_summary(
    topic: str,
    task_intent: str,
    packet_intent: str,
    label_groups: List[SelectedLabelGroup],
) -> str:
    """Build a one-line summary for the task packet."""
    total_labels = sum(g.count for g in label_groups)
    if packet_intent == "no_action":
        return f"Topic '{topic}' intent '{task_intent}' has no actionable labels"
    group_desc = ", ".join(f"{g.label_type}:{g.count}" for g in label_groups)
    return f"Topic '{topic}' intent '{task_intent}' has {total_labels} labels ({group_desc})"


def _build_preview_controller_packet(
    packet_intent: str,
    label_groups: List[SelectedLabelGroup],
    suggested_next_step: str,
    explicit_non_canonical: bool,
) -> ConversationControllerPacket:
    """Build controller packet for task-packet preview."""
    actionable_targets: List[str] = []
    reason_tags: List[str] = []

    for group in label_groups:
        for label in group.labels:
            actionable_targets.append(f"{group.label_type}:{label}")

    if packet_intent != "no_action":
        reason_tags.append(packet_intent)
    else:
        reason_tags.append("no_action")

    if explicit_non_canonical:
        reason_tags.append("explicit_non_canonical_boundary")

    truth_status = "explicit_non_canonical" if explicit_non_canonical else "non_canonical"

    return ConversationControllerPacket(
        review_mode="inspect_only",
        actionable_source_object_keys=[],
        actionable_correction_targets=actionable_targets,
        reason_tags=reason_tags,
        advisory_scope="task_packet_preview",
        truth_status=truth_status,
    )


def run_task_packet_preview(
    body: TaskPacketPreviewRequest,
) -> TaskPacketPreviewResponse:
    """Bounded inspect-only function for task-packet preview.

    Accepts manual decision input and returns a normalized preview
    without persistence, workflow execution, or automatic delegation.
    """
    # Normalize selected labels
    label_groups = _normalize_selected_labels(
        knowledge_labels=body.selected_knowledge_labels,
        evolution_labels=body.selected_evolution_labels,
        source_labels=body.selected_source_labels,
    )

    # Count labels per type
    knowledge_count = sum(g.count for g in label_groups if g.label_type == "knowledge")
    evolution_count = sum(g.count for g in label_groups if g.label_type == "evolution")
    source_count = sum(g.count for g in label_groups if g.label_type == "source")

    # Derive packet intent
    packet_intent = _derive_packet_intent(
        knowledge_count=knowledge_count,
        evolution_count=evolution_count,
        source_count=source_count,
    )

    # Derive suggested lane and next step
    suggested_lane = _derive_suggested_lane(packet_intent)
    suggested_next_step = _derive_suggested_next_step(
        packet_intent=packet_intent,
        reviewer_note=body.reviewer_note,
    )

    # Build summary and controller packet
    task_packet_summary = _build_task_packet_summary(
        topic=body.topic,
        task_intent=body.task_intent,
        packet_intent=packet_intent,
        label_groups=label_groups,
    )
    controller_packet = _build_preview_controller_packet(
        packet_intent=packet_intent,
        label_groups=label_groups,
        suggested_next_step=suggested_next_step,
        explicit_non_canonical=body.explicit_non_canonical,
    )

    # Build notes
    notes: List[str] = [
        f"knowledge_labels_selected={knowledge_count}",
        f"evolution_labels_selected={evolution_count}",
        f"source_labels_selected={source_count}",
        f"packet_intent={packet_intent}",
        f"suggested_lane={suggested_lane}",
        f"explicit_non_canonical={body.explicit_non_canonical}",
    ]
    if body.reviewer_note:
        notes.append(f"reviewer_note_present=true")

    # Build truth boundary
    truth_boundary = _task_packet_preview_truth_boundary()

    return TaskPacketPreviewResponse(
        task_packet_summary=task_packet_summary,
        packet_intent=packet_intent,
        suggested_lane=suggested_lane,
        suggested_next_step=suggested_next_step,
        selected_label_groups=label_groups,
        controller_packet=controller_packet,
        truth_boundary=truth_boundary,
        promotion_state="inspect_only",
        notes=notes,
    )


def _build_execution_feedback_prompt(
    body: FlywheelExecutionFeedbackInspectRequest,
) -> str:
    # Build provenance context section if any provenance fields are provided
    provenance_section = ""
    if body.worker_run_id or body.worker_provider or body.worker_model or body.worker_artifact_ref:
        provenance_lines = [
            "--- Worker Provenance Context (caller-provided, not verified) ---",
        ]
        if body.worker_run_id:
            provenance_lines.append(f"worker_run_id: {body.worker_run_id}")
        if body.worker_provider:
            provenance_lines.append(f"worker_provider: {body.worker_provider}")
        if body.worker_model:
            provenance_lines.append(f"worker_model: {body.worker_model}")
        if body.worker_artifact_ref:
            provenance_lines.append(f"worker_artifact_ref: {body.worker_artifact_ref}")
        provenance_lines.append("Note: Provenance is caller-provided and not verified by this endpoint.")
        provenance_section = "\n" + "\n".join(provenance_lines) + "\n"

    return (
        "You are reflecting on one bounded worker execution result for IKE.\n"
        "Return valid JSON only.\n"
        "This route is inspect-only and non-canonical.\n\n"
        "Extract:\n"
        "1. intent: execution_feedback if the feedback suggests useful knowledge or evolution reflection, otherwise other.\n"
        "2. summary: one concise line describing what the worker result means.\n"
        "3. knowledge_delta_candidates: bounded knowledge deltas implied by the execution result.\n"
        "   Each item has delta_type (claim|concept|boundary|relation), label, content.\n"
        "4. evolution_trigger_candidates: bounded next-step evolution triggers implied by the execution result.\n"
        "   Each item has trigger_type (study|prototype|review|source-strategy), label, rationale.\n\n"
        "Schema:\n"
        "{\n"
        '  "intent": "execution_feedback|other",\n'
        '  "summary": "...",\n'
        '  "knowledge_delta_candidates": [{"delta_type": "claim|concept|boundary|relation", "label": "...", "content": "..."}],\n'
        '  "evolution_trigger_candidates": [{"trigger_type": "study|prototype|review|source-strategy", "label": "...", "rationale": "..."}]\n'
        "}\n\n"
        f"Topic: {body.topic}\n"
        f"Task intent: {body.task_intent}\n"
        f"Worker lane: {body.worker_lane}\n"
        f"Execution status hint: {body.execution_status_hint}\n"
        f"Task packet summary:\n{body.task_packet_summary}\n\n"
        f"{provenance_section}"
        f"Execution feedback text:\n{body.execution_feedback_text}\n"
    )


def _derive_execution_feedback_operational_advice(
    knowledge_deltas: List[KnowledgeDeltaCandidate],
    evolution_triggers: List[EvolutionTriggerCandidate],
    feedback_intent: str,
) -> ConversationOperationalAdvice:
    notes: List[str] = []

    if knowledge_deltas:
        notes.append(
            f"{len(knowledge_deltas)} execution-feedback knowledge candidate(s) extracted"
        )
    if evolution_triggers:
        notes.append(
            f"{len(evolution_triggers)} execution-feedback evolution trigger(s) extracted"
        )

    if knowledge_deltas and evolution_triggers:
        next_step = "review_execution_feedback"
    elif knowledge_deltas:
        next_step = "review_feedback_knowledge"
    elif evolution_triggers:
        next_step = "review_feedback_evolution"
    elif feedback_intent == "other":
        next_step = "no_action"
        notes.append("execution feedback produced no actionable reflection candidates")
    else:
        next_step = "manual_review"
        notes.append("execution feedback is ambiguous and should be reviewed manually")

    return ConversationOperationalAdvice(
        suggested_next_step=next_step,
        controller_notes=notes,
    )


def _build_execution_feedback_controller_packet(
    knowledge_deltas: List[KnowledgeDeltaCandidate],
    evolution_triggers: List[EvolutionTriggerCandidate],
    operational_advice: ConversationOperationalAdvice,
) -> ConversationControllerPacket:
    reason_tags: List[str] = []
    if knowledge_deltas:
        reason_tags.append("execution_feedback_knowledge")
    if evolution_triggers:
        reason_tags.append("execution_feedback_evolution")
    if operational_advice.suggested_next_step == "manual_review":
        reason_tags.append("manual_review_required")
    if not reason_tags:
        reason_tags.append("no_action")
    return ConversationControllerPacket(
        review_mode=operational_advice.suggested_next_step,
        actionable_source_object_keys=[],
        actionable_correction_targets=[],
        reason_tags=reason_tags,
        advisory_scope="execution_feedback_inspect_only",
        truth_status="non_canonical",
    )


async def run_execution_feedback_inspect(
    body: FlywheelExecutionFeedbackInspectRequest,
) -> FlywheelExecutionFeedbackInspectResponse:
    adapter = LLMAdapter()
    model = body.model.strip() or default_model_for_provider(body.provider)

    raw = await adapter.chat(
        message=_build_execution_feedback_prompt(body),
        provider=body.provider,
        model=model,
        system_prompt="Return valid JSON only.",
    )
    payload, parse_status = parse_ai_judgment_payload(raw)

    allowed_intents = {"execution_feedback", "other"}
    feedback_intent = str(payload.get("intent", "")).strip().lower()
    if feedback_intent not in allowed_intents:
        feedback_intent = "other"

    knowledge_deltas = _normalize_knowledge_delta_candidates(payload)
    evolution_triggers = _normalize_evolution_trigger_candidates(payload)
    feedback_summary = str(payload.get("summary", "")).strip()

    operational_advice = _derive_execution_feedback_operational_advice(
        knowledge_deltas=knowledge_deltas,
        evolution_triggers=evolution_triggers,
        feedback_intent=feedback_intent,
    )
    controller_packet = _build_execution_feedback_controller_packet(
        knowledge_deltas=knowledge_deltas,
        evolution_triggers=evolution_triggers,
        operational_advice=operational_advice,
    )

    # Build caller-provided provenance (inspect-only, not verified)
    provenance = WorkerProvenance(
        worker_run_id=body.worker_run_id,
        worker_provider=body.worker_provider,
        worker_model=body.worker_model,
        worker_artifact_ref=body.worker_artifact_ref,
        provenance_source="caller_provided",
        verified=False,
    )

    notes = [
        f"execution_feedback_parse_status={parse_status}",
        f"feedback_intent={feedback_intent}",
        f"worker_lane={body.worker_lane}",
        f"execution_status_hint={body.execution_status_hint}",
        f"knowledge_delta_candidates={len(knowledge_deltas)}",
        f"evolution_trigger_candidates={len(evolution_triggers)}",
        f"provenance_source=caller_provided",
        f"provenance_verified=false",
    ]

    truth_boundary = flywheel_truth_boundary()
    truth_boundary.extend(_execution_feedback_truth_boundary())

    return FlywheelExecutionFeedbackInspectResponse(
        topic=body.topic,
        task_intent=body.task_intent,
        worker_lane=body.worker_lane,
        execution_status_hint=body.execution_status_hint,
        provider=body.provider,
        model=model,
        feedback_intent=feedback_intent,
        feedback_summary=feedback_summary,
        knowledge_delta_candidates=knowledge_deltas,
        evolution_trigger_candidates=evolution_triggers,
        operational_advice=operational_advice,
        controller_packet=controller_packet,
        notes=notes,
        truth_boundary=truth_boundary,
        promotion_state="inspect_only",
        provenance=provenance,
    )
