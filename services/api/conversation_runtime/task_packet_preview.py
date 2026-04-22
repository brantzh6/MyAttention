"""Task-packet preview bounded slice (controller-facing).

Generates normalized inspect-only task-packet previews for controller discussion.

This module is strictly inspect-only:
- no persistence
- no workflow execution
- no automatic delegation
- promotion_state is always inspect_only
"""

from typing import List

from conversation_runtime.contracts import (
    ConversationControllerPacket,
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