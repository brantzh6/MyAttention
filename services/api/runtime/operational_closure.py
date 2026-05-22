"""
IKE Runtime v0 - Operational Closure Helpers

Narrow DB-backed helpers for the first truthful closure loop after R1-C:
- reconstruct WorkContext from canonical runtime truth
- promote reviewed upstream work into trusted MemoryPacket records

These helpers must not create a second truth source. WorkContext remains
derivative, and trusted memory remains explicitly linked to reviewed upstream
task/decision truth.

R1-I1 HARDENING: Explicit guardrails for:
- Archived-context rejection in project-pointer alignment
- No-active-context handling with bounded runtime-domain errors
- Upstream relevance checks beyond mere existence
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm.exc import NoResultFound

from db.models import (
    RuntimeContextStatus,
    RuntimeDecision,
    RuntimeDecisionStatus,
    RuntimeMemoryPacket,
    RuntimePacketStatus,
    RuntimeProject,
    RuntimeTask,
    RuntimeTaskStatus,
    RuntimeWorkContext,
)
from runtime.memory_packets import (
    MemoryPacket,
    accept_packet,
    is_packet_trusted,
    transition_to_review,
)
from runtime.state_machine import OwnerKind
from runtime.work_context import (
    AcceptedPacketRef,
    DecisionSnapshot,
    TaskSnapshot,
    WorkContext,
    reconstruct_work_context,
)


# ──────────────────────────────────────────────────────────────
# R1-I1: Explicit Runtime-Domain Exceptions
# ──────────────────────────────────────────────────────────────

class RuntimeContextAlignmentError(Exception):
    """Explicit bounded error when project-pointer alignment fails.

    Replaces raw ORM/lookup errors with runtime-domain messaging.
    """


class NoActiveContextError(RuntimeContextAlignmentError):
    """Project has no active runtime work context for alignment.

    This is an expected condition, not a failure – call sites should
    handle this explicitly rather than catching raw ORM errors.
    """


class ArchivedContextAlignmentError(RuntimeContextAlignmentError):
    """Attempted alignment to an archived (non-active) work context.

    Explicit project-pointer alignment must target ACTIVE contexts only.
    """


class UpstreamRelevanceError(Exception):
    """Referenced upstream object exists but lacks required relevance.

    R1-I1 hardening: for trusted closure/memory paths, mere existence
    is insufficient – upstream objects must be in relevant terminal states.
    """


def _parse_uuid(value: str | UUID, field_name: str) -> UUID:
    try:
        return UUID(str(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value}") from exc


def _as_datetime(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


def verify_runtime_upstream_exists(db_session, object_type: str, object_id: str) -> bool:
    """Check whether a referenced runtime upstream object exists in Postgres.

    R1-I1 HARDENING: Mere existence is insufficient for trusted paths.
    This function verifies existence but NOT relevance. Use
    verify_runtime_upstream_relevant() for trust gate checks.
    """
    try:
        object_uuid = _parse_uuid(object_id, object_type)
    except ValueError:
        return False

    if object_type == "task":
        result = db_session.execute(
            select(RuntimeTask.task_id).where(RuntimeTask.task_id == object_uuid)
        )
        return result.one_or_none() is not None

    if object_type == "decision":
        result = db_session.execute(
            select(RuntimeDecision.decision_id).where(
                RuntimeDecision.decision_id == object_uuid
            )
        )
        return result.one_or_none() is not None

    return False


def verify_runtime_upstream_relevant(
    db_session, object_type: str, object_id: str
) -> tuple[bool, str]:
    """Check whether upstream object exists AND is in a relevant state for trust.

    R1-I1 HARDENING: For trusted closure/memory paths, mere existence is too weak.
    Upstream objects must be in terminal/reviewable states:
    - Tasks: DONE or REVIEW_PENDING (completed work awaiting/accepted review)
    - Decisions: FINAL status with finalized_at set

    Returns:
        (is_relevant, reason) tuple explaining relevance status.

    This is the trust-gate verifier – use it for acceptance promotion.
    """
    try:
        object_uuid = _parse_uuid(object_id, object_type)
    except ValueError:
        return False, f"Invalid {object_type} id: {object_id}"

    if object_type == "task":
        result = db_session.execute(
            select(RuntimeTask).where(RuntimeTask.task_id == object_uuid)
        )
        row = result.scalars().one_or_none()
        if row is None:
            return False, f"Task '{object_id}' does not exist"
        status_label = row.status.name if hasattr(row.status, "name") else str(row.status)
        # R1-I1: Task must be in a terminal/reviewable state
        # DONE = completed work, REVIEW_PENDING = awaiting controller acceptance
        if row.status not in (RuntimeTaskStatus.DONE, RuntimeTaskStatus.REVIEW_PENDING):
            return False, (
                f"Task '{object_id}' exists but is in '{status_label}' status. "
                f"Trusted upstream requires DONE or REVIEW_PENDING."
            )
        return True, f"Task '{object_id}' is in relevant state '{status_label}'"

    if object_type == "decision":
        result = db_session.execute(
            select(RuntimeDecision).where(RuntimeDecision.decision_id == object_uuid)
        )
        row = result.scalars().one_or_none()
        if row is None:
            return False, f"Decision '{object_id}' does not exist"
        status_label = row.status.name if hasattr(row.status, "name") else str(row.status)
        # R1-I1: Decision must be finalized
        if row.status != RuntimeDecisionStatus.FINAL:
            return False, (
                f"Decision '{object_id}' exists but is in '{status_label}' status. "
                f"Trusted upstream requires FINAL status."
            )
        if row.finalized_at is None:
            return False, (
                f"Decision '{object_id}' has FINAL status but no finalized_at timestamp. "
                f"Trusted upstream requires finalized_at."
            )
        return True, f"Decision '{object_id}' is finalized"

    return False, f"Unknown upstream object type: {object_type}"


def _packet_from_row(row: RuntimeMemoryPacket) -> MemoryPacket:
    return MemoryPacket(
        memory_packet_id=str(row.memory_packet_id),
        project_id=str(row.project_id),
        task_id=str(row.task_id) if row.task_id is not None else None,
        packet_type=row.packet_type,
        status=row.status.value if hasattr(row.status, "value") else str(row.status),
        acceptance_trigger=row.acceptance_trigger,
        title=row.title,
        summary=row.summary or "",
        storage_ref=row.storage_ref,
        content_hash=row.content_hash,
        parent_packet_id=(
            str(row.parent_packet_id) if row.parent_packet_id is not None else None
        ),
        created_by_kind=(
            row.created_by_kind.value
            if hasattr(row.created_by_kind, "value")
            else str(row.created_by_kind)
        ),
        created_by_id=row.created_by_id or "",
        created_at=row.created_at.isoformat(),
        accepted_at=row.accepted_at.isoformat() if row.accepted_at else None,
        metadata=row.extra or {},
    )


def reconstruct_runtime_work_context(
    db_session,
    project_id: str,
    current_focus: str | None = None,
    existing_context_id: str | None = None,
) -> WorkContext:
    """Reconstruct a WorkContext from canonical runtime truth in Postgres."""
    project_uuid = _parse_uuid(project_id, "project_id")

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
    decision_rows = (
        db_session.execute(
            select(RuntimeDecision).where(
                RuntimeDecision.project_id == project_uuid,
                RuntimeDecision.finalized_at.is_not(None),
            )
        )
        .scalars()
        .all()
    )
    packet_rows = (
        db_session.execute(
            select(RuntimeMemoryPacket).where(
                RuntimeMemoryPacket.project_id == project_uuid,
                RuntimeMemoryPacket.status == RuntimePacketStatus.ACCEPTED,
            )
        )
        .scalars()
        .all()
    )

    active_tasks = [
        TaskSnapshot(
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
        for row in active_rows
    ]
    waiting_tasks = [
        TaskSnapshot(
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
        for row in waiting_rows
    ]
    decisions = [
        DecisionSnapshot(
            decision_id=str(row.decision_id),
            title=row.title,
            outcome=row.outcome.value if getattr(row, "outcome", None) else None,
            status=row.status.value if hasattr(row.status, "value") else str(row.status),
            finalized_at=row.finalized_at.isoformat() if row.finalized_at else None,
        )
        for row in decision_rows
    ]

    accepted_packets: list[AcceptedPacketRef] = []
    for row in packet_rows:
        packet = _packet_from_row(row)
        if is_packet_trusted(
            packet,
            verify_upstream_exists=lambda t, oid: verify_runtime_upstream_relevant(
                db_session, t, oid
            )[0],
        ):
            accepted_packets.append(
                AcceptedPacketRef(
                    memory_packet_id=packet.memory_packet_id,
                    title=packet.title,
                    packet_type=packet.packet_type,
                    accepted_at=packet.accepted_at or packet.created_at,
                )
            )

    return reconstruct_work_context(
        project_id=str(project_uuid),
        active_tasks=active_tasks,
        waiting_tasks=waiting_tasks,
        latest_decisions=decisions,
        accepted_packets=accepted_packets,
        current_focus=current_focus,
        existing_context_id=existing_context_id,
    )


def persist_reconstructed_work_context(db_session, context: WorkContext) -> RuntimeWorkContext:
    """Persist a reconstructed active WorkContext while archiving older active ones."""
    project_uuid = _parse_uuid(context.project_id, "project_id")
    context_uuid = _parse_uuid(context.work_context_id, "work_context_id")
    project = (
        db_session.execute(
            select(RuntimeProject).where(RuntimeProject.project_id == project_uuid)
        )
        .scalars()
        .one_or_none()
    )
    if project is None:
        raise RuntimeContextAlignmentError(
            f"Project '{context.project_id}' does not exist. "
            "Cannot persist reconstructed work context without runtime project truth."
        )

    active_rows = (
        db_session.execute(
            select(RuntimeWorkContext).where(
                RuntimeWorkContext.project_id == project_uuid,
                RuntimeWorkContext.status == RuntimeContextStatus.ACTIVE,
            )
        )
        .scalars()
        .all()
    )
    for row in active_rows:
        if row.work_context_id != context_uuid:
            row.status = RuntimeContextStatus.ARCHIVED
            row.updated_at = _as_datetime(context.updated_at)
            row.extra = {
                **(row.extra or {}),
                "archived_by": "runtime_reconstruction",
            }

    existing = (
        db_session.execute(
            select(RuntimeWorkContext).where(RuntimeWorkContext.work_context_id == context_uuid)
        )
        .scalars()
        .one_or_none()
    )
    if existing is None:
        existing = RuntimeWorkContext(
            work_context_id=context_uuid,
            project_id=project_uuid,
        )
        db_session.add(existing)

    existing.status = RuntimeContextStatus.ACTIVE
    existing.active_task_id = (
        _parse_uuid(context.active_task_id, "active_task_id")
        if context.active_task_id
        else None
    )
    existing.latest_decision_id = (
        _parse_uuid(context.latest_decision_id, "latest_decision_id")
        if context.latest_decision_id
        else None
    )
    existing.current_focus = context.current_focus
    existing.blockers_summary = context.blockers_summary
    existing.next_steps_summary = context.next_steps_summary
    existing.packet_ref_id = (
        _parse_uuid(context.packet_ref_id, "packet_ref_id")
        if context.packet_ref_id
        else None
    )
    existing.updated_at = _as_datetime(context.updated_at)
    existing.extra = context.metadata
    db_session.commit()
    return existing


def align_project_current_work_context(
    db_session,
    project_id: str,
    work_context_id: str | None = None,
) -> RuntimeProject:
    """Align RuntimeProject.current_work_context_id to the active runtime truth.

    If work_context_id is omitted, the helper resolves the currently active
    RuntimeWorkContext for the project. This keeps the project-facing pointer
    derivative of runtime truth instead of becoming a separate source.

    R1-I1 HARDENING:
    - Explicit work_context_id must reference an ACTIVE context (reject ARCHIVED)
    - No-active-context is handled with explicit bounded error, not raw ORM
    - Missing project is handled with explicit bounded error

    Raises:
        RuntimeContextAlignmentError: If project does not exist.
        ArchivedContextAlignmentError: If explicit work_context_id is not ACTIVE.
        NoActiveContextError: If implicit alignment finds no active context.
        ValueError: If context does not belong to the project.
    """
    project_uuid = _parse_uuid(project_id, "project_id")
    project = (
        db_session.execute(
            select(RuntimeProject).where(RuntimeProject.project_id == project_uuid)
        )
        .scalars()
        .one_or_none()
    )
    if project is None:
        raise RuntimeContextAlignmentError(
            f"Project '{project_id}' does not exist. "
            f"Cannot align work context pointer for non-existent project."
        )

    if work_context_id is not None:
        context_uuid = _parse_uuid(work_context_id, "work_context_id")
        context = (
            db_session.execute(
                select(RuntimeWorkContext).where(
                    RuntimeWorkContext.work_context_id == context_uuid,
                    RuntimeWorkContext.project_id == project_uuid,
                )
            )
            .scalars()
            .one_or_none()
        )
        if context is None:
            raise RuntimeContextAlignmentError(
                f"WorkContext '{work_context_id}' does not exist for project '{project_id}'. "
                f"Cannot align to non-existent context."
            )
        # R1-I1: Reject alignment to archived (non-active) contexts
        if context.status != RuntimeContextStatus.ACTIVE:
            raise ArchivedContextAlignmentError(
                f"WorkContext '{work_context_id}' is '{context.status.value}', not ACTIVE. "
                f"Explicit project-pointer alignment must target active contexts only."
            )
    else:
        # Implicit alignment: find the currently active context
        context = (
            db_session.execute(
                select(RuntimeWorkContext).where(
                    RuntimeWorkContext.project_id == project_uuid,
                    RuntimeWorkContext.status == RuntimeContextStatus.ACTIVE,
                )
            )
            .scalars()
            .one_or_none()
        )
        if context is None:
            raise NoActiveContextError(
                f"Project '{project_id}' has no active RuntimeWorkContext. "
                f"Cannot implicitly align without an active context. "
                f"Reconstruct and persist a context first, or provide explicit work_context_id."
            )

    project.current_work_context_id = context.work_context_id
    project.updated_at = _as_datetime(context.updated_at)
    aligned_at = _as_datetime(context.updated_at).isoformat()
    project.extra = {
        **(project.extra or {}),
        "current_work_context_alignment": {
            "source": "runtime_work_contexts",
            "aligned_at": aligned_at,
            "work_context_id": str(context.work_context_id),
        },
    }
    db_session.commit()
    return project


def get_project_current_work_context(db_session, project_id: str) -> RuntimeWorkContext | None:
    """Return the current active project WorkContext from the project pointer.

    This helper is project-facing but still runtime-derived: it trusts only the
    project pointer plus the referenced runtime_work_context row.

    R1-I1 HARDENING: Returns None for bounded no-context conditions:
    - Project does not exist
    - Project has no current_work_context_id pointer
    - Referenced context does not exist or project mismatch

    This is a read helper, so None is appropriate for expected absence.
    Callers needing explicit error handling for write paths should use
    align_project_current_work_context which raises explicit exceptions.
    """
    project_uuid = _parse_uuid(project_id, "project_id")
    project = (
        db_session.execute(
            select(RuntimeProject).where(RuntimeProject.project_id == project_uuid)
        )
        .scalars()
        .one_or_none()
    )
    if project is None or project.current_work_context_id is None:
        return None

    context = (
        db_session.execute(
            select(RuntimeWorkContext).where(
                RuntimeWorkContext.work_context_id == project.current_work_context_id,
                RuntimeWorkContext.project_id == project_uuid,
            )
        )
        .scalars()
        .one_or_none()
    )
    # R1-I1: Also check context is ACTIVE for read-path consistency
    # The context may have been archived since pointer was set
    if context is None or context.status != RuntimeContextStatus.ACTIVE:
        return None
    return context


def transition_packet_to_review(db_session, memory_packet_id: str) -> RuntimeMemoryPacket:
    """Move a draft runtime packet to pending_review using runtime packet rules.

    R1-I1 HARDENING: Explicit error handling for missing packet.
    """
    packet_uuid = _parse_uuid(memory_packet_id, "memory_packet_id")
    row = (
        db_session.execute(
            select(RuntimeMemoryPacket).where(RuntimeMemoryPacket.memory_packet_id == packet_uuid)
        )
        .scalars()
        .one_or_none()
    )
    if row is None:
        raise ValueError(
            f"Memory packet '{memory_packet_id}' does not exist. "
            f"Cannot transition non-existent packet to review."
        )
    packet = _packet_from_row(row)
    try:
        triggered_by_kind = OwnerKind(packet.created_by_kind)
    except ValueError as exc:
        raise ValueError(
            f"Runtime packet {packet.memory_packet_id} has invalid created_by_kind "
            f"for review provenance: {packet.created_by_kind}"
        ) from exc
    updates = transition_to_review(
        packet,
        triggered_by_kind=triggered_by_kind,
        triggered_by_id=packet.created_by_id,
        trigger_reason="Submitted for reviewed operational closure",
    )
    row.status = RuntimePacketStatus.PENDING_REVIEW
    row.extra = updates["metadata"]
    db_session.commit()
    return row


def promote_reviewed_memory_packet(
    db_session,
    memory_packet_id: str,
    accepted_by_kind: OwnerKind,
    accepted_by_id: str,
    upstream_task_id: str | None = None,
    upstream_task_status: str | None = None,
    upstream_decision_id: str | None = None,
    acceptance_reason: str = "Operational closure accepted after review",
) -> RuntimeMemoryPacket:
    """Promote a pending_review packet to trusted accepted runtime memory.

    R1-I1 HARDENING: Uses relevance-based upstream verification, not just existence.
    Upstream objects must be in terminal/reviewable states for trust promotion:
    - Tasks: DONE or REVIEW_PENDING
    - Decisions: FINAL with finalized_at

    Raises:
        UpstreamRelevanceError: If upstream object exists but is not in relevant state.
        PacketTransitionError: If packet transition rules violated.
    """
    packet_uuid = _parse_uuid(memory_packet_id, "memory_packet_id")
    row = (
        db_session.execute(
            select(RuntimeMemoryPacket).where(RuntimeMemoryPacket.memory_packet_id == packet_uuid)
        )
        .scalars()
        .one_or_none()
    )
    if row is None:
        raise ValueError(
            f"Memory packet '{memory_packet_id}' does not exist. "
            f"Cannot promote non-existent packet."
        )
    packet = _packet_from_row(row)

    # R1-I1: Create relevance verifier that raises on non-relevant upstream
    def verify_upstream_relevant_for_promotion(object_type: str, object_id: str) -> bool:
        is_relevant, reason = verify_runtime_upstream_relevant(db_session, object_type, object_id)
        if not is_relevant:
            raise UpstreamRelevanceError(
                f"Packet '{memory_packet_id}' cannot be accepted: {reason}. "
                f"Trusted packets require upstream objects in relevant states."
            )
        return True

    updates = accept_packet(
        packet,
        accepted_by_kind=accepted_by_kind,
        accepted_by_id=accepted_by_id,
        upstream_task_id=upstream_task_id,
        upstream_task_status=upstream_task_status,
        upstream_decision_id=upstream_decision_id,
        acceptance_reason=acceptance_reason,
        verify_upstream_exists=verify_upstream_relevant_for_promotion,
    )
    row.status = RuntimePacketStatus.ACCEPTED
    row.accepted_at = datetime.fromisoformat(updates["accepted_at"])
    row.extra = updates["metadata"]
    db_session.commit()
    return row
