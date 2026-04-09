"""
IKE Runtime v0 - Controller Runtime Read Surface

Narrow controller-facing read helpers assembled strictly from runtime truth:
- RuntimeProject
- aligned RuntimeWorkContext
- current active/waiting tasks
- latest finalized decision
- latest trusted memory packet refs

This module must not create or persist duplicate summary state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy import select

from db.models import (
    RuntimeDecision,
    RuntimeMemoryPacket,
    RuntimeProject,
    RuntimeTask,
    RuntimeTaskStatus,
)
from runtime.operational_closure import (
    _packet_from_row,
    _parse_uuid,
    get_project_current_work_context,
    verify_runtime_upstream_relevant,
)
from runtime.memory_packets import is_packet_trusted


@dataclass
class RuntimeTaskRef:
    task_id: str
    title: str
    status: str
    task_type: str
    priority: int
    next_action_summary: str | None
    waiting_reason: str | None
    waiting_detail: str | None


@dataclass
class RuntimeDecisionRef:
    decision_id: str
    title: str
    outcome: str | None
    status: str
    finalized_at: str | None


@dataclass
class RuntimePacketRef:
    memory_packet_id: str
    title: str
    packet_type: str
    accepted_at: str


@dataclass
class ProjectRuntimeReadSurface:
    project_id: str
    project_key: str
    title: str
    status: str
    current_phase: str | None
    priority: int
    current_work_context_id: str | None
    current_focus: str | None
    blockers_summary: str | None
    next_steps_summary: str | None
    active_tasks: list[RuntimeTaskRef] = field(default_factory=list)
    waiting_tasks: list[RuntimeTaskRef] = field(default_factory=list)
    latest_decision: RuntimeDecisionRef | None = None
    trusted_packets: list[RuntimePacketRef] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def _task_ref_from_row(row: RuntimeTask) -> RuntimeTaskRef:
    return RuntimeTaskRef(
        task_id=str(row.task_id),
        title=row.title,
        status=row.status.value if hasattr(row.status, "value") else str(row.status),
        task_type=(
            row.task_type.value if hasattr(row.task_type, "value") else str(row.task_type)
        ),
        priority=row.priority,
        next_action_summary=row.next_action_summary,
        waiting_reason=row.waiting_reason,
        waiting_detail=row.waiting_detail,
    )


def _decision_ref_from_row(row: RuntimeDecision) -> RuntimeDecisionRef:
    return RuntimeDecisionRef(
        decision_id=str(row.decision_id),
        title=row.title,
        outcome=row.outcome.value if getattr(row, "outcome", None) else None,
        status=row.status.value if hasattr(row.status, "value") else str(row.status),
        finalized_at=row.finalized_at.isoformat() if row.finalized_at else None,
    )


def build_project_runtime_read_surface(
    db_session,
    project_id: str | UUID,
    max_trusted_packets: int = 3,
) -> ProjectRuntimeReadSurface | None:
    """Build a narrow controller-facing read model from runtime truth only."""
    project_uuid = _parse_uuid(project_id, "project_id")
    project = (
        db_session.execute(
            select(RuntimeProject).where(RuntimeProject.project_id == project_uuid)
        )
        .scalars()
        .one_or_none()
    )
    if project is None:
        return None

    current_context = get_project_current_work_context(db_session, str(project_uuid))

    active_rows = (
        db_session.execute(
            select(RuntimeTask).where(
                RuntimeTask.project_id == project_uuid,
                RuntimeTask.status == RuntimeTaskStatus.ACTIVE,
            )
        )
        .scalars()
        .all()
    )
    waiting_rows = (
        db_session.execute(
            select(RuntimeTask).where(
                RuntimeTask.project_id == project_uuid,
                RuntimeTask.status == RuntimeTaskStatus.WAITING,
            )
        )
        .scalars()
        .all()
    )
    decision_row = (
        db_session.execute(
            select(RuntimeDecision)
            .where(
                RuntimeDecision.project_id == project_uuid,
                RuntimeDecision.finalized_at.is_not(None),
            )
            .order_by(RuntimeDecision.finalized_at.desc())
            .limit(1)
        )
        .scalars()
        .one_or_none()
    )
    packet_rows = (
        db_session.execute(
            select(RuntimeMemoryPacket).where(
                RuntimeMemoryPacket.project_id == project_uuid
            )
        )
        .scalars()
        .all()
    )

    trusted_packets: list[RuntimePacketRef] = []
    for row in packet_rows:
        packet = _packet_from_row(row)
        if is_packet_trusted(
            packet,
            verify_upstream_exists=lambda t, oid: verify_runtime_upstream_relevant(
                db_session, t, oid
            )[0],
        ):
            trusted_packets.append(
                RuntimePacketRef(
                    memory_packet_id=packet.memory_packet_id,
                    title=packet.title,
                    packet_type=packet.packet_type,
                    accepted_at=packet.accepted_at or packet.created_at,
                )
            )
    trusted_packets.sort(key=lambda p: p.accepted_at, reverse=True)

    return ProjectRuntimeReadSurface(
        project_id=str(project.project_id),
        project_key=project.project_key,
        title=project.title,
        status=project.status.value if hasattr(project.status, "value") else str(project.status),
        current_phase=project.current_phase,
        priority=project.priority,
        current_work_context_id=(
            str(project.current_work_context_id) if project.current_work_context_id else None
        ),
        current_focus=current_context.current_focus if current_context else None,
        blockers_summary=current_context.blockers_summary if current_context else None,
        next_steps_summary=current_context.next_steps_summary if current_context else None,
        active_tasks=[_task_ref_from_row(row) for row in sorted(active_rows, key=lambda r: r.priority)],
        waiting_tasks=[_task_ref_from_row(row) for row in sorted(waiting_rows, key=lambda r: r.priority)],
        latest_decision=_decision_ref_from_row(decision_row) if decision_row else None,
        trusted_packets=trusted_packets[:max_trusted_packets],
        metadata={
            "source": "runtime_truth_only",
            "active_task_count": len(active_rows),
            "waiting_task_count": len(waiting_rows),
            "trusted_packet_count": len(trusted_packets),
            "has_current_context": current_context is not None,
        },
    )


def build_latest_project_runtime_read_surface(
    db_session,
    project_key: str | None = None,
    max_trusted_packets: int = 3,
) -> ProjectRuntimeReadSurface | None:
    """Resolve one latest runtime project surface for narrow visible integration.

    If project_key is provided, the surface is built for that exact project.
    Otherwise the most recently created runtime project is used.

    RuntimeProject.updated_at is not yet runtime-managed truth, so this helper
    deliberately avoids implying "most recently updated" semantics.
    """
    query = select(RuntimeProject)
    if project_key:
        query = query.where(RuntimeProject.project_key == project_key)
    else:
        query = query.order_by(
            RuntimeProject.created_at.desc(),
            RuntimeProject.project_key.desc(),
        ).limit(1)

    project = db_session.execute(query).scalars().one_or_none()
    if project is None:
        return None
    return build_project_runtime_read_surface(
        db_session,
        str(project.project_id),
        max_trusted_packets=max_trusted_packets,
    )


def bootstrap_runtime_project_surface(
    db_session,
    project_key: str,
    title: str,
    current_phase: str | None = None,
    priority: int = 1,
    max_trusted_packets: int = 3,
) -> ProjectRuntimeReadSurface:
    """Explicitly bootstrap one runtime project and return its read surface."""
    project = (
        db_session.execute(
            select(RuntimeProject).where(RuntimeProject.project_key == project_key)
        )
        .scalars()
        .one_or_none()
    )
    created = False
    if project is None:
        project = RuntimeProject(
            project_key=project_key,
            title=title,
            current_phase=current_phase,
            priority=priority,
        )
        db_session.add(project)
        db_session.commit()
        project = (
            db_session.execute(
                select(RuntimeProject).where(RuntimeProject.project_id == project.project_id)
            )
            .scalars()
            .one()
        )
        created = True

    surface = build_project_runtime_read_surface(
        db_session,
        str(project.project_id),
        max_trusted_packets=max_trusted_packets,
    )
    assert surface is not None
    surface.metadata = {
        **(surface.metadata or {}),
        "bootstrap_created": created,
        "bootstrap_source": "explicit_request",
    }
    return surface
