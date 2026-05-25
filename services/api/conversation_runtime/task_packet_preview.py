"""Task-packet preview bounded slice (controller-facing).

Generates normalized inspect-only task-packet previews for controller discussion.

This module is strictly inspect-only:
- no persistence
- no workflow execution
- no automatic delegation
- promotion_state is always inspect_only
"""

import re
from typing import List

from conversation_runtime.contracts import (
    CandidatePacket,
    ConversationControllerPacket,
    ExecutionHandoffPreview,
    SelectedLabelGroup,
    TaskPacketPreviewRequest,
    TaskPacketPreviewResponse,
)


def _task_packet_preview_truth_boundary() -> List[str]:
    return [
        "task-packet preview is inspect-only, not a workflow contract",
        "suggested lane and next step are advisory, not automated decisions",
        "selected label groups are normalized inputs, not persisted state",
        "controller packet is compression for human review, not execution",
        "promotion state is fixed to inspect_only; no automatic promotion",
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


def _safe_task_id_fragment(value: str, max_length: int = 30) -> str:
    """Normalize user-controlled text before it is used in artifact paths."""
    normalized = re.sub(r"[^a-z0-9_-]+", "_", str(value).strip().lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_-")
    if not normalized:
        return "untitled"
    return normalized[:max_length].strip("_-") or "untitled"


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


def _contains_flywheel_signal(text: str) -> bool:
    """Check if text contains mainline flywheel progression signals.

    Note: 'evolution' alone is NOT a flywheel signal - generic evolution context
    (e.g. "Evolution focus", "prototype:new-feature") should not trigger candidate
    generation. Only explicit flywheel/mainline/controller/runtime signals qualify.
    """
    if not text:
        return False
    text_lower = text.lower()
    mainline_signals = [
        "flywheel",
        "preview",
        "packet",
        "controller",
        "runtime",
        "feedback collector",
        "execution feedback",
        "evidence impact",
        "handoff",
        "delegate",
        "inspect",
        "absorption",
        "mainline",
    ]
    return any(sig in text_lower for sig in mainline_signals)


def _derive_candidate_packet(
    packet_intent: str,
    suggested_lane: str,
    evolution_labels: List[str],
    reviewer_note: str,
    topic: str,
    task_intent: str,
) -> CandidatePacket | None:
    """Generate a controller-ready candidate packet for mainline flywheel progression.

    Returns None if conditions for a candidate packet are not met.
    Generates a candidate when:
    1. packet_intent is mixed or evolution_driven
    2. at least one evolution label is selected
    3. combined context (topic, task_intent, reviewer_note, evolution labels)
       contains a mainline flywheel signal
    """
    # Only generate candidate packet for mixed/evolution-driven cases with evolution labels
    if packet_intent not in ("mixed", "evolution_driven"):
        return None

    if not evolution_labels:
        return None

    # Check for mainline flywheel progression signals in combined context
    # Topic, task_intent, reviewer_note, and evolution labels are all considered
    combined_context = [
        topic,
        task_intent,
        reviewer_note,
    ] + evolution_labels

    has_flywheel_signal = any(_contains_flywheel_signal(ctx) for ctx in combined_context)

    if not has_flywheel_signal:
        return None

    # Generate candidate packet for mainline flywheel progression
    # Build a clear goal based on the topic and evolution labels
    goal = (
        f"Improve Flywheel task-packet preview so selected inspect labels "
        f"become a single controller-ready next packet candidate for '{topic}'"
    )

    if reviewer_note:
        goal += f" (reviewer note: {reviewer_note[:80]})"

    # Build allowed files based on the flywheel context
    allowed_files = [
        "services/api/conversation_runtime/contracts.py",
        "services/api/conversation_runtime/task_packet_preview.py",
        "services/api/tests/test_flywheel_inspect_route.py",
        "services/web/lib/api-client.ts",
        "services/web/components/evolution/task-preview-section.tsx",
        "services/web/components/evolution/flywheel-packet-builders.ts",
    ]

    # Build validation commands
    validation_commands = [
        "python -m pytest services/api/tests/test_flywheel_inspect_route.py",
        "python -m py_compile services/api/conversation_runtime/contracts.py services/api/conversation_runtime/task_packet_preview.py",
    ]

    # Build non-goals (from packet requirements)
    non_goals = [
        "no persistence",
        "no scheduler changes",
        "no runtime operator changes",
        "no GitHub/Codex review trigger",
        "no automatic worker execution",
        "no promotion or acceptance record",
    ]

    # Build stop conditions
    stop_conditions = [
        "schema change requires broad frontend/backend contract refactor",
        "implementation would require persistence or scheduler semantics",
        "runtime services become unavailable",
        "validation cannot run for reasons unrelated to this task",
    ]

    # Generate path-safe task ID.
    candidate_task_id = f"flywheel_candidate_{_safe_task_id_fragment(topic)}"

    return CandidatePacket(
        candidate_task_id=candidate_task_id,
        candidate_lane="mainline_flywheel",
        candidate_goal=goal,
        allowed_files=allowed_files,
        non_goals=non_goals,
        validation_commands=validation_commands,
        review_gate="local_delegated_L1_review_then_controller_absorption",
        stop_conditions=stop_conditions,
        delegation_target="local_coding_delegate",
        truth_status="non_canonical",
    )


def _derive_result_artifact_path(task_id: str) -> str:
    """Derive the expected result artifact path from task_id."""
    if not task_id:
        return ""
    return f"tasks/codex/{task_id}_result.md"


def _derive_sdlc_stage(packet_intent: str) -> str:
    """Derive SDLC stage from packet intent."""
    # Most flywheel packets are code_implementation by default
    if packet_intent in ("mixed", "evolution_driven"):
        return "code_implementation"
    if packet_intent == "knowledge_driven":
        return "design"
    if packet_intent == "source_driven":
        return "design"
    return "code_implementation"


def _derive_risk_level(task_id: str, allowed_files: List[str]) -> str:
    """Derive risk level from task context."""
    # R3 if touches runtime contracts, persistence, or worker dispatch
    high_risk_patterns = [
        "contracts.py",
        "session.py",
        "worker",
        "dispatch",
        "scheduler",
        "harness",
        "persistence",
    ]
    for file in allowed_files:
        for pattern in high_risk_patterns:
            if pattern in file.lower():
                return "R3"
    # R2 is default for bounded implementation tasks
    return "R2"


def _derive_write_policy(allowed_files: List[str], non_goals: List[str]) -> str:
    """Derive write policy from allowed files and non_goals."""
    if not allowed_files:
        return "result_only"
    return "bounded_patch"


def _generate_handoff_markdown(
    task_id: str,
    owner_lane: str,
    objective: str,
    current_evidence: List[str],
    allowed_files: List[str],
    non_goals: List[str],
    validation_commands: List[str],
    review_gate: str,
    expected_result_format: List[str],
    stop_conditions: List[str],
    delegation_target: str,
    truth_status: str,
    promotion_state: str,
    sdlc_stage: str,
    risk_level: str,
    result_artifact_path: str,
    write_policy: str,
) -> str:
    """Generate a full markdown delegate packet body from existing typed fields."""
    lines = []

    lines.append(f"# Delegate Packet: {task_id}")
    lines.append("")
    lines.append("Date: controller-provided-at-dispatch")
    lines.append("")
    lines.append(f"Task id: `{task_id}`")
    lines.append("")
    lines.append(f"Owner lane: {owner_lane}")
    lines.append("")
    lines.append("Controller: Controller owns scope, review absorption, and promotion decision.")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append(objective)
    lines.append("")

    lines.append("## Scope")
    lines.append("")
    if allowed_files:
        lines.append("Make the smallest bounded patch within the allowed files below.")
    else:
        lines.append("Result-only task. Do not modify source files unless the controller re-scopes the packet.")
    lines.append("")

    if current_evidence:
        lines.append("## Current Evidence")
        lines.append("")
        for item in current_evidence:
            lines.append(f"- {item}")
        lines.append("")

    if allowed_files:
        lines.append("## Allowed Files")
        lines.append("")
        lines.append("Use the narrowest patch possible:")
        lines.append("")
        for file in allowed_files:
            lines.append(f"- `{file}`")
        lines.append("")

    if non_goals:
        lines.append("## Non-Goals")
        lines.append("")
        for non_goal in non_goals:
            lines.append(f"- {non_goal}")
        lines.append("")

    lines.append("## Acceptance Criteria")
    lines.append("")
    lines.append("- The bounded objective is satisfied without expanding scope.")
    lines.append("- The result remains inspect-only until controller absorption.")
    lines.append("- The delegate result uses the expected result format below.")
    lines.append("")

    if validation_commands:
        lines.append("## Validation Commands")
        lines.append("")
        lines.append("Required:")
        lines.append("")
        lines.append("```powershell")
        for command in validation_commands:
            lines.append(command)
        lines.append("```")
        lines.append("")

    lines.append("## Review Gate")
    lines.append("")
    lines.append(f"Default gate: `{review_gate}`")
    lines.append("")
    lines.append("GitHub/Codex review is not required unless this becomes a promotion-ready PR")
    lines.append("or the controller explicitly requests cloud review.")
    lines.append("")

    lines.append("## Expected Result Format")
    lines.append("")
    lines.append("Return:")
    lines.append("")
    for field in expected_result_format:
        lines.append(f"1. `{field}`")
    lines.append("")
    lines.append(f"Write the result to: `{result_artifact_path}`")
    lines.append("")

    if stop_conditions:
        lines.append("## Stop Conditions")
        lines.append("")
        lines.append("Stop and report if:")
        lines.append("")
        for condition in stop_conditions:
            lines.append(f"- {condition}")
        lines.append("")

    lines.append("## Truth Boundary / Promotion State")
    lines.append("")
    lines.append(f"- truth_status: `{truth_status}`")
    lines.append(f"- promotion_state: `{promotion_state}`")
    lines.append(f"- sdlc_stage: `{sdlc_stage}`")
    lines.append(f"- risk_level: `{risk_level}`")
    lines.append(f"- write_policy: `{write_policy}`")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("This handoff is inspect-only and advisory. It does not trigger execution,")
    lines.append("persistence, scheduling, or promotion.")
    lines.append("")

    return "\n".join(lines)


def _derive_handoff_preview(
    candidate_packet: CandidatePacket | None,
    task_packet_summary: str,
    packet_intent: str,
    suggested_lane: str,
    suggested_next_step: str,
) -> ExecutionHandoffPreview | None:
    """Build an inspect-only delegate handoff preview from a candidate packet."""
    if candidate_packet is None:
        return None

    current_evidence = [
        task_packet_summary,
        f"packet_intent={packet_intent}",
        f"suggested_lane={suggested_lane}",
        f"suggested_next_step={suggested_next_step}",
        "candidate_packet_generated=true",
        "promotion_state=inspect_only",
    ]

    expected_result_format = [
        "summary",
        "files_changed",
        "why_this_solution",
        "validation_run",
        "known_risks",
        "recommendation",
        "stop_condition",
    ]

    # Derive new metadata fields
    result_artifact_path = _derive_result_artifact_path(candidate_packet.candidate_task_id)
    sdlc_stage = _derive_sdlc_stage(packet_intent)
    risk_level = _derive_risk_level(candidate_packet.candidate_task_id, candidate_packet.allowed_files)
    write_policy = _derive_write_policy(candidate_packet.allowed_files, candidate_packet.non_goals)

    handoff_markdown = _generate_handoff_markdown(
        task_id=candidate_packet.candidate_task_id,
        owner_lane=candidate_packet.candidate_lane,
        objective=candidate_packet.candidate_goal,
        current_evidence=current_evidence,
        allowed_files=candidate_packet.allowed_files,
        non_goals=candidate_packet.non_goals,
        validation_commands=candidate_packet.validation_commands,
        review_gate=candidate_packet.review_gate,
        expected_result_format=expected_result_format,
        stop_conditions=candidate_packet.stop_conditions,
        delegation_target=candidate_packet.delegation_target,
        truth_status="non_canonical",
        promotion_state="inspect_only",
        sdlc_stage=sdlc_stage,
        risk_level=risk_level,
        result_artifact_path=result_artifact_path,
        write_policy=write_policy,
    )

    return ExecutionHandoffPreview(
        task_id=candidate_packet.candidate_task_id,
        owner_lane=candidate_packet.candidate_lane,
        objective=candidate_packet.candidate_goal,
        current_evidence=current_evidence,
        allowed_files=candidate_packet.allowed_files,
        non_goals=candidate_packet.non_goals,
        validation_commands=candidate_packet.validation_commands,
        review_gate=candidate_packet.review_gate,
        expected_result_format=expected_result_format,
        stop_conditions=candidate_packet.stop_conditions,
        delegation_target=candidate_packet.delegation_target,
        truth_status="non_canonical",
        promotion_state="inspect_only",
        sdlc_stage=sdlc_stage,
        risk_level=risk_level,
        result_artifact_path=result_artifact_path,
        write_policy=write_policy,
        handoff_markdown=handoff_markdown,
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

    # Get evolution labels for candidate packet generation
    evolution_labels = body.selected_evolution_labels

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

    # Derive candidate packet if conditions are met
    candidate_packet = _derive_candidate_packet(
        packet_intent=packet_intent,
        suggested_lane=suggested_lane,
        evolution_labels=evolution_labels,
        reviewer_note=body.reviewer_note,
        topic=body.topic,
        task_intent=body.task_intent,
    )

    if candidate_packet:
        notes.append(f"candidate_packet_generated=true")
        notes.append(f"candidate_lane={candidate_packet.candidate_lane}")
        notes.append(f"delegation_target={candidate_packet.delegation_target}")

    handoff_preview = _derive_handoff_preview(
        candidate_packet=candidate_packet,
        task_packet_summary=task_packet_summary,
        packet_intent=packet_intent,
        suggested_lane=suggested_lane,
        suggested_next_step=suggested_next_step,
    )

    if handoff_preview:
        notes.append("handoff_preview_generated=true")
        notes.append(f"handoff_owner_lane={handoff_preview.owner_lane}")

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
        candidate_packet=candidate_packet,
        handoff_preview=handoff_preview,
    )
