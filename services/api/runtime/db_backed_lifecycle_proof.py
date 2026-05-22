"""
IKE Runtime v0 - DB-Backed Lifecycle Proof

Narrow helper for proving one lifecycle path through durable runtime truth:
- runtime_tasks
- runtime_task_events
- runtime_worker_leases

This helper is intentionally not a general task runner.
It exists to close the semantic gap between in-memory lifecycle proof and
PG-backed lifecycle fact path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select

from db.models import (
    RuntimeOwnerKind,
    RuntimeProject,
    RuntimeTask,
    RuntimeTaskEvent,
    RuntimeTaskStatus,
    RuntimeTaskType,
    RuntimeWorkerLease,
    RuntimeLeaseStatus,
)
from runtime.leases import (
    build_lease_release_update,
    claim_lease,
    release_lease,
)
from runtime.postgres_claim_verifier import PostgresClaimVerifier
from runtime.state_machine import ClaimType, OwnerKind, TaskStatus
from runtime.transitions import TransitionRequest, build_event_record, build_task_update, execute_transition


@dataclass
class DBBackedLifecycleProofResult:
    success: bool
    project_id: str
    task_id: str
    final_status: str
    lease_id: str | None = None
    event_ids: list[str] = field(default_factory=list)
    error: str | None = None
    persisted_event_count: int = 0

    def to_audit_dict(self) -> dict[str, object]:
        return {
            "success": self.success,
            "project_id": self.project_id,
            "task_id": self.task_id,
            "final_status": self.final_status,
            "lease_id": self.lease_id,
            "persisted_event_count": self.persisted_event_count,
            "error": self.error,
        }


def _parse_uuid(value: str) -> UUID:
    return UUID(str(value))


def _persist_event(db_session, event_dict: dict) -> RuntimeTaskEvent:
    row = RuntimeTaskEvent(
        event_id=_parse_uuid(event_dict["event_id"]),
        project_id=_parse_uuid(event_dict["project_id"]),
        task_id=_parse_uuid(event_dict["task_id"]),
        event_type=event_dict["event_type"],
        from_status=event_dict.get("from_status"),
        to_status=event_dict.get("to_status"),
        triggered_by_kind=event_dict["triggered_by_kind"],
        triggered_by_id=event_dict.get("triggered_by_id"),
        reason=event_dict.get("reason"),
        payload=event_dict.get("payload", {}),
        created_at=datetime.fromisoformat(event_dict["created_at"]),
    )
    db_session.add(row)
    db_session.commit()
    return row


def _apply_task_updates(task: RuntimeTask, updates: dict) -> None:
    for key, value in updates.items():
        if key == "status":
            task.status = RuntimeTaskStatus(value)
        elif key == "current_lease_id":
            task.current_lease_id = _parse_uuid(value) if value else None
        elif key == "waiting_reason":
            task.waiting_reason = value
        elif key == "waiting_detail":
            task.waiting_detail = value
        elif key == "result_summary":
            task.result_summary = value
        elif key == "next_action_summary":
            task.next_action_summary = value
        elif key == "started_at":
            task.started_at = value
        elif key == "ended_at":
            task.ended_at = value
        elif key == "updated_at":
            task.updated_at = value


def _load_persisted_failure_snapshot(
    db_session,
    task_id: str,
    fallback_status: str,
) -> tuple[str, int]:
    """Best-effort durable snapshot for failure reporting.

    The helper commits several lifecycle steps intentionally. If a later step
    fails, rollback only clears the current transaction; earlier committed rows
    remain durable truth. Failure summaries should therefore reflect persisted
    state when possible instead of stale in-memory state only.

    This is a failure-reporting helper, not a second truth source.
    """
    try:
        task_row = (
            db_session.execute(
                select(RuntimeTask).where(RuntimeTask.task_id == _parse_uuid(task_id))
            )
            .scalars()
            .one_or_none()
        )
        event_rows = (
            db_session.execute(
                select(RuntimeTaskEvent).where(RuntimeTaskEvent.task_id == _parse_uuid(task_id))
            )
            .scalars()
            .all()
        )
    except Exception:
        return fallback_status, 0

    durable_status = fallback_status
    if task_row is not None:
        durable_status = (
            task_row.status.value if hasattr(task_row.status, "value") else str(task_row.status)
        )
    return durable_status, len(event_rows)


def execute_db_backed_lifecycle_proof(
    db_session,
    project_key: str | None = None,
    title: str = "DB-backed lifecycle proof task",
    delegate_id: str = "delegate-001",
    controller_id: str = "controller-001",
) -> DBBackedLifecycleProofResult:
    now = datetime.now(timezone.utc)
    project = RuntimeProject(
        project_key=project_key or f"db-proof-{uuid4().hex[:8]}",
        title="DB-backed lifecycle proof project",
    )
    db_session.add(project)
    db_session.commit()
    project_id_str = str(project.project_id)

    task = RuntimeTask(
        project_id=project.project_id,
        task_type=RuntimeTaskType.IMPLEMENTATION,
        title=title,
        status=RuntimeTaskStatus.INBOX,
        priority=1,
    )
    db_session.add(task)
    db_session.commit()
    task_id_str = str(task.task_id)

    event_ids: list[str] = []
    lease_id: str | None = None

    try:
        req1 = TransitionRequest(
            task_id=task_id_str,
            project_id=project_id_str,
            from_status=TaskStatus.INBOX,
            to_status=TaskStatus.READY,
            role=OwnerKind.CONTROLLER,
            role_id=controller_id,
            reason="DB-backed triage complete",
        )
        result1 = execute_transition(req1)
        if not result1.success:
            raise ValueError(result1.error or "inbox->ready failed")
        _apply_task_updates(task, build_task_update(result1))
        task.owner_kind = RuntimeOwnerKind.DELEGATE
        task.owner_id = delegate_id
        db_session.add(task)
        db_session.commit()
        event1 = _persist_event(
            db_session,
            build_event_record(
                result1,
                project_id=project_id_str,
                triggered_by_kind=OwnerKind.CONTROLLER,
                triggered_by_id=controller_id,
            ),
        )
        event_ids.append(str(event1.event_id))

        lease_result = claim_lease(
            task_id=str(task.task_id),
            project_id=project_id_str,
            owner_kind=OwnerKind.DELEGATE,
            owner_id=delegate_id,
            ttl_seconds=3600,
            created_at=now,
        )
        if not lease_result.success or lease_result.lease is None:
            raise ValueError(lease_result.error or "claim_lease failed")
        lease_id = lease_result.lease.lease_id
        lease_row = RuntimeWorkerLease(
            lease_id=_parse_uuid(lease_result.lease.lease_id),
            task_id=task.task_id,
            owner_kind=RuntimeOwnerKind.DELEGATE,
            owner_id=delegate_id,
            lease_status=RuntimeLeaseStatus.ACTIVE,
            heartbeat_at=datetime.fromisoformat(lease_result.lease.metadata.get("claimed_at", lease_result.lease.created_at))
            if lease_result.lease.metadata.get("claimed_at")
            else datetime.fromisoformat(lease_result.lease.created_at),
            expires_at=datetime.fromisoformat(lease_result.lease.expires_at),
            created_at=datetime.fromisoformat(lease_result.lease.created_at),
            extra=lease_result.lease.metadata,
        )
        db_session.add(lease_row)
        db_session.commit()
        task.current_lease_id = _parse_uuid(lease_result.lease.lease_id)
        db_session.add(task)
        db_session.commit()
        if lease_result.event is not None:
            lease_event = _persist_event(db_session, lease_result.event.to_dict())
            event_ids.append(str(lease_event.event_id))

        verifier = PostgresClaimVerifier(db_session)
        verification = verifier.verify_and_build_context(
            claim_type=ClaimType.ACTIVE_LEASE,
            claim_ref=lease_result.lease.lease_id,
            delegate_id=delegate_id,
            task_id=task_id_str,
        )
        if not verification.valid or verification.claim_context is None:
            raise ValueError(verification.error or "lease verification failed")

        req2 = TransitionRequest(
            task_id=task_id_str,
            project_id=project_id_str,
            from_status=TaskStatus.READY,
            to_status=TaskStatus.ACTIVE,
            role=OwnerKind.DELEGATE,
            role_id=delegate_id,
            reason="DB-backed work started with verified lease",
            claim_context=verification.claim_context,
        )
        result2 = execute_transition(req2)
        if not result2.success:
            raise ValueError(result2.error or "ready->active failed")
        _apply_task_updates(task, build_task_update(result2, current_lease_id=lease_result.lease.lease_id))
        db_session.add(task)
        db_session.commit()
        event2 = _persist_event(
            db_session,
            build_event_record(
                result2,
                project_id=project_id_str,
                triggered_by_kind=OwnerKind.DELEGATE,
                triggered_by_id=delegate_id,
                extra_payload={"lease_id": lease_result.lease.lease_id},
            ),
        )
        event_ids.append(str(event2.event_id))

        release_event = release_lease(
            lease_id=lease_result.lease.lease_id,
            task_id=task_id_str,
            project_id=project_id_str,
            owner_kind=OwnerKind.DELEGATE,
            owner_id=delegate_id,
            reason="DB-backed lease released on review submission",
        )
        lease_row.lease_status = RuntimeLeaseStatus.RELEASED
        release_update = build_lease_release_update(now)
        lease_row.heartbeat_at = datetime.fromisoformat(release_update["heartbeat_at"])
        db_session.add(lease_row)
        task.current_lease_id = None
        db_session.add(task)
        db_session.commit()
        release_event_row = _persist_event(db_session, release_event.to_dict())
        event_ids.append(str(release_event_row.event_id))

        req3 = TransitionRequest(
            task_id=task_id_str,
            project_id=project_id_str,
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.REVIEW_PENDING,
            role=OwnerKind.DELEGATE,
            role_id=delegate_id,
            reason="DB-backed work complete; awaiting review",
        )
        result3 = execute_transition(req3)
        if not result3.success:
            raise ValueError(result3.error or "active->review_pending failed")
        _apply_task_updates(task, build_task_update(result3))
        db_session.add(task)
        db_session.commit()
        event3 = _persist_event(
            db_session,
            build_event_record(
                result3,
                project_id=project_id_str,
                triggered_by_kind=OwnerKind.DELEGATE,
                triggered_by_id=delegate_id,
            ),
        )
        event_ids.append(str(event3.event_id))

        req4 = TransitionRequest(
            task_id=task_id_str,
            project_id=project_id_str,
            from_status=TaskStatus.REVIEW_PENDING,
            to_status=TaskStatus.DONE,
            role=OwnerKind.CONTROLLER,
            role_id=controller_id,
            reason="DB-backed review passed; task accepted",
        )
        result4 = execute_transition(req4)
        if not result4.success:
            raise ValueError(result4.error or "review_pending->done failed")
        _apply_task_updates(task, build_task_update(result4, result_summary="DB-backed lifecycle proof complete"))
        db_session.add(task)
        db_session.commit()
        event4 = _persist_event(
            db_session,
            build_event_record(
                result4,
                project_id=project_id_str,
                triggered_by_kind=OwnerKind.CONTROLLER,
                triggered_by_id=controller_id,
                extra_payload={"review_passed": True},
            ),
        )
        event_ids.append(str(event4.event_id))

        refreshed_task = (
            db_session.execute(
                select(RuntimeTask).where(RuntimeTask.task_id == task.task_id)
            )
            .scalars()
            .one()
        )
        persisted_event_count = (
            db_session.execute(
                select(RuntimeTaskEvent).where(RuntimeTaskEvent.task_id == task.task_id)
            )
            .scalars()
            .all()
        )
        return DBBackedLifecycleProofResult(
            success=True,
            project_id=project_id_str,
            task_id=task_id_str,
            final_status=refreshed_task.status.value if hasattr(refreshed_task.status, "value") else str(refreshed_task.status),
            lease_id=lease_id,
            event_ids=event_ids,
            persisted_event_count=len(persisted_event_count),
        )
    except Exception as exc:
        db_session.rollback()
        # Avoid attribute access after rollback: SQLAlchemy may expire ORM state
        # and trigger unexpected IO. This fallback is only a conservative
        # placeholder until durable truth can be re-read from Postgres.
        fallback_status_obj = task.__dict__.get("status", RuntimeTaskStatus.INBOX)
        fallback_status = (
            fallback_status_obj.value
            if hasattr(fallback_status_obj, "value")
            else str(fallback_status_obj)
        )
        durable_status, persisted_event_count = _load_persisted_failure_snapshot(
            db_session,
            task_id_str,
            fallback_status,
        )
        return DBBackedLifecycleProofResult(
            success=False,
            project_id=project_id_str,
            task_id=task_id_str,
            final_status=durable_status,
            lease_id=lease_id,
            event_ids=event_ids,
            error=str(exc),
            persisted_event_count=persisted_event_count,
        )
