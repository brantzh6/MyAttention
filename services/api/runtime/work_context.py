"""
IKE Runtime v0 – Work Context

Narrow snapshot carrier for the current restorable working set of a project.
WorkContext is NOT a second truth source – it is a derived view over canonical
task/decision state and accepted packet references.

This module provides:
- WorkContext dataclass matching runtime_work_contexts schema
- One-active-context-per-project discipline
- Reconstruction from canonical state (tasks + decisions + packets)
- No hidden mutable truth – context fields are derivable
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


# ──────────────────────────────────────────────────────────────
# Context Status
# ──────────────────────────────────────────────────────────────

class ContextStatus:
    """Work context lifecycle states."""
    ACTIVE = "active"
    ARCHIVED = "archived"


# ──────────────────────────────────────────────────────────────
# WorkContext Dataclass
# ──────────────────────────────────────────────────────────────

@dataclass
class WorkContext:
    """Narrow snapshot of the current working set for a project.

    This is a convenience carrier – the canonical truth lives in:
    - runtime_tasks (canonical task state)
    - runtime_decisions (canonical decision state)
    - runtime_memory_packets (accepted packet references)

    WorkContext fields are DERIVABLE from canonical state.
    They should not be treated as an independent truth source.

    Matches runtime_work_contexts table schema.
    """
    work_context_id: str
    project_id: str
    status: str
    active_task_id: str | None
    latest_decision_id: str | None
    current_focus: str
    blockers_summary: str | None
    next_steps_summary: str | None
    packet_ref_id: str | None
    updated_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for persistence into runtime_work_contexts."""
        return {
            "work_context_id": self.work_context_id,
            "project_id": self.project_id,
            "status": self.status,
            "active_task_id": self.active_task_id,
            "latest_decision_id": self.latest_decision_id,
            "current_focus": self.current_focus,
            "blockers_summary": self.blockers_summary,
            "next_steps_summary": self.next_steps_summary,
            "packet_ref_id": self.packet_ref_id,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkContext":
        """Reconstruct from a persistence dict."""
        return cls(
            work_context_id=data["work_context_id"],
            project_id=data["project_id"],
            status=data["status"],
            active_task_id=data.get("active_task_id"),
            latest_decision_id=data.get("latest_decision_id"),
            current_focus=data.get("current_focus", ""),
            blockers_summary=data.get("blockers_summary"),
            next_steps_summary=data.get("next_steps_summary"),
            packet_ref_id=data.get("packet_ref_id"),
            updated_at=data["updated_at"],
            metadata=data.get("metadata", {}),
        )


# ──────────────────────────────────────────────────────────────
# Canonical State Snapshots (Input for Reconstruction)
# ──────────────────────────────────────────────────────────────

@dataclass
class TaskSnapshot:
    """Minimal task data needed for work context reconstruction."""
    task_id: str
    title: str
    status: str
    task_type: str
    priority: int
    next_action_summary: str | None
    waiting_reason: str | None
    waiting_detail: str | None


@dataclass
class DecisionSnapshot:
    """Minimal decision data needed for work context reconstruction."""
    decision_id: str
    title: str
    outcome: str | None
    status: str
    finalized_at: str | None


@dataclass
class AcceptedPacketRef:
    """Reference to an accepted memory packet."""
    memory_packet_id: str
    title: str
    packet_type: str
    accepted_at: str


# ──────────────────────────────────────────────────────────────
# Reconstruction from Canonical State
# ──────────────────────────────────────────────────────────────

def reconstruct_work_context(
    project_id: str,
    active_tasks: list[TaskSnapshot],
    waiting_tasks: list[TaskSnapshot],
    latest_decisions: list[DecisionSnapshot],
    accepted_packets: list[AcceptedPacketRef],
    current_focus: str | None = None,
    existing_context_id: str | None = None,
) -> WorkContext:
    """Rebuild a WorkContext from canonical runtime state.

    This is the truthfulness-enforcing function. It derives all
    WorkContext fields from canonical task/decision/packet state,
    ensuring the context cannot drift into a second truth source.

    Reconstruction rules:
    - active_task_id: highest-priority active task (or first if equal)
    - latest_decision_id: most recently finalized decision
    - current_focus: from active task title, or explicit override
    - blockers_summary: derived from waiting tasks
    - next_steps_summary: derived from active/ready tasks
    - packet_ref_id: most recently accepted packet

    Args:
        project_id: The project this context belongs to.
        active_tasks: Tasks in active state.
        waiting_tasks: Tasks in waiting state (potential blockers).
        latest_decisions: Recent decisions for the project.
        accepted_packets: Accepted memory packet references.
        current_focus: Optional explicit override for focus text.
        existing_context_id: If provided, reuse this context ID.

    Returns:
        A WorkContext derived entirely from canonical state.
    """
    now = datetime.now(timezone.utc).isoformat()
    context_id = existing_context_id or str(uuid4())

    # Active task: highest priority (lowest number), then first
    active_task_id = None
    active_task_title = None
    if active_tasks:
        sorted_active = sorted(active_tasks, key=lambda t: t.priority)
        top_task = sorted_active[0]
        active_task_id = top_task.task_id
        active_task_title = top_task.title

    # Latest decision: most recently finalized
    latest_decision_id = None
    finalized = [d for d in latest_decisions if d.finalized_at is not None]
    if finalized:
        finalized.sort(key=lambda d: d.finalized_at or "", reverse=True)
        latest_decision_id = finalized[0].decision_id

    # Current focus: explicit override, or active task title, or project summary
    if current_focus:
        focus = current_focus
    elif active_task_title:
        focus = f"Working on: {active_task_title}"
    elif waiting_tasks:
        focus = f"Waiting: {len(waiting_tasks)} task(s) blocked"
    else:
        focus = "No active work"

    # Blockers summary: derived from waiting tasks
    blockers = _derive_blockers_summary(waiting_tasks)

    # Next steps: derived from active tasks
    next_steps = _derive_next_steps_summary(active_tasks)

    # Packet ref: most recently accepted
    packet_ref_id = None
    if accepted_packets:
        sorted_packets = sorted(
            accepted_packets,
            key=lambda p: p.accepted_at or "",
            reverse=True,
        )
        packet_ref_id = sorted_packets[0].memory_packet_id

    return WorkContext(
        work_context_id=context_id,
        project_id=project_id,
        status=ContextStatus.ACTIVE,
        active_task_id=active_task_id,
        latest_decision_id=latest_decision_id,
        current_focus=focus,
        blockers_summary=blockers,
        next_steps_summary=next_steps,
        packet_ref_id=packet_ref_id,
        updated_at=now,
        metadata={
            "reconstructed_from": "canonical_state",
            "active_task_count": len(active_tasks),
            "waiting_task_count": len(waiting_tasks),
            "decision_count": len(latest_decisions),
            "packet_count": len(accepted_packets),
        },
    )


def _derive_blockers_summary(waiting_tasks: list[TaskSnapshot]) -> str | None:
    """Derive blockers summary from waiting tasks."""
    if not waiting_tasks:
        return None

    reasons: dict[str, int] = {}
    for task in waiting_tasks:
        reason = task.waiting_reason or "unspecified"
        reasons[reason] = reasons.get(reason, 0) + 1

    parts = [f"{count}x {reason}" for reason, count in sorted(reasons.items())]
    return f"Waiting on: {', '.join(parts)}"


def _derive_next_steps_summary(active_tasks: list[TaskSnapshot]) -> str | None:
    """Derive next steps summary from active tasks."""
    if not active_tasks:
        return None

    # Collect next_action_summary from active tasks
    summaries = [
        t.next_action_summary
        for t in active_tasks
        if t.next_action_summary
    ]

    if summaries:
        return f"Active: {len(active_tasks)} task(s). " + "; ".join(summaries[:3])
    return f"Active: {len(active_tasks)} task(s) in progress"


# ──────────────────────────────────────────────────────────────
# Context Lifecycle Operations
# ──────────────────────────────────────────────────────────────

def create_work_context(
    project_id: str,
    current_focus: str = "",
    active_task_id: str | None = None,
    latest_decision_id: str | None = None,
    packet_ref_id: str | None = None,
) -> WorkContext:
    """Create a new active work context for a project.

    Args:
        project_id: The project this context belongs to.
        current_focus: Description of current focus area.
        active_task_id: Optional reference to the active task.
        latest_decision_id: Optional reference to latest decision.
        packet_ref_id: Optional reference to a memory packet.

    Returns:
        New WorkContext with ACTIVE status.
    """
    now = datetime.now(timezone.utc).isoformat()
    return WorkContext(
        work_context_id=str(uuid4()),
        project_id=project_id,
        status=ContextStatus.ACTIVE,
        active_task_id=active_task_id,
        latest_decision_id=latest_decision_id,
        current_focus=current_focus,
        blockers_summary=None,
        next_steps_summary=None,
        packet_ref_id=packet_ref_id,
        updated_at=now,
        metadata={"created": True},
    )


def archive_work_context(
    context: WorkContext,
    reason: str = "Context archived",
) -> dict[str, Any]:
    """Archive a work context.

    Returns a dict of updates to apply to the database.
    The context object itself is NOT mutated (immutability discipline).
    """
    now = datetime.now(timezone.utc).isoformat()
    return {
        "work_context_id": context.work_context_id,
        "status": ContextStatus.ARCHIVED,
        "updated_at": now,
        "metadata": {
            **context.metadata,
            "archived_reason": reason,
            "archived_at": now,
        },
    }


def update_work_context(
    context: WorkContext,
    current_focus: str | None = None,
    active_task_id: str | None = None,
    latest_decision_id: str | None = None,
    blockers_summary: str | None = None,
    next_steps_summary: str | None = None,
    packet_ref_id: str | None = None,
) -> dict[str, Any]:
    """Build an update dict for a work context.

    Only provided fields are included in the update.
    The context object itself is NOT mutated.
    """
    now = datetime.now(timezone.utc).isoformat()
    updates: dict[str, Any] = {
        "work_context_id": context.work_context_id,
        "updated_at": now,
    }
    if current_focus is not None:
        updates["current_focus"] = current_focus
    if active_task_id is not None:
        updates["active_task_id"] = active_task_id
    if latest_decision_id is not None:
        updates["latest_decision_id"] = latest_decision_id
    if blockers_summary is not None:
        updates["blockers_summary"] = blockers_summary
    if next_steps_summary is not None:
        updates["next_steps_summary"] = next_steps_summary
    if packet_ref_id is not None:
        updates["packet_ref_id"] = packet_ref_id

    return updates
