"""Execution feedback inspect bounded slice.

Reflects bounded worker execution results back into the flywheel.

This module is strictly inspect-only:
- no persistence
- no knowledge state mutation
- no workflow auto-trigger
- no canonical truth promotion
"""

from typing import List

from conversation_runtime.contracts import (
    ConversationControllerPacket,
    ConversationOperationalAdvice,
    FlywheelExecutionFeedbackInspectRequest,
    FlywheelExecutionFeedbackInspectResponse,
    KnowledgeDeltaCandidate,
    EvolutionTriggerCandidate,
    WorkerProvenance,
)
from conversation_runtime.flywheel_inspect import (
    flywheel_truth_boundary,
    _normalize_knowledge_delta_candidates,
    _normalize_evolution_trigger_candidates,
)
from feeds.ai_judgment import (
    default_model_for_provider,
    parse_ai_judgment_payload,
)


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
    # Deferred import for test mock path compatibility
    # Tests patch "conversation_runtime.flywheel.LLMAdapter"
    from conversation_runtime.flywheel import LLMAdapter

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