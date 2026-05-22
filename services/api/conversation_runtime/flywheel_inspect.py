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
    EvolutionTriggerCandidate,
    FlywheelInspectRequest,
    FlywheelInspectResponse,
    KnowledgeDeltaCandidate,
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
        notes.append("ready for task-packet preview after controller review")
    elif has_knowledge:
        next_step = "review_knowledge_deltas"
        notes.append("ready for task-packet preview after controller review")
    elif has_evolution:
        next_step = "review_evolution_triggers"
        notes.append("ready for task-packet preview after controller review")
    elif has_sources:
        next_step = "review_source_candidates"
        notes.append("no knowledge or evolution candidates; source-level candidates only")
        notes.append("controller review required; not ready for task-packet preview")
    elif has_corrections:
        next_step = "review_corrections"
        notes.append("no knowledge or evolution candidates; corrections only")
        notes.append("controller review required; not ready for task-packet preview")
    elif segment_intent == "other":
        next_step = "no_action"
        notes.append("segment classified as other; no flywheel candidates to promote")
        notes.append("insufficient inspect signal for flywheel action")
    else:
        next_step = "manual_review"
        notes.append("segment produced no actionable candidates")
        notes.append("controller review required; insufficient inspect signal")

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
    if actionable_knowledge or actionable_triggers:
        reason_tags.append("ready_for_task_packet_preview")
        reason_tags.append("needs_controller_review")
    elif operational_advice.suggested_next_step in {
        "review_source_candidates",
        "review_corrections",
        "manual_review",
    }:
        reason_tags.append("needs_controller_review")
    if operational_advice.suggested_next_step == "manual_review":
        reason_tags.append("manual_review_required")
    if not reason_tags:
        reason_tags.append("no_action")
        reason_tags.append("insufficient_signal")
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
    # Deferred import for test mock path compatibility
    # Tests patch "conversation_runtime.flywheel.LLMAdapter"
    from conversation_runtime.flywheel import LLMAdapter

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
