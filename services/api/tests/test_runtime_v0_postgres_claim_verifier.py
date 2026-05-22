from datetime import datetime, timedelta, timezone
from uuid import uuid4

from db.models import (
    RuntimeProject,
    RuntimeTask,
    RuntimeWorkerLease,
    RuntimeTaskType,
    RuntimeTaskStatus,
    RuntimeOwnerKind,
    RuntimeLeaseStatus,
)
from runtime.postgres_claim_verifier import PostgresClaimVerifier
from runtime.state_machine import ClaimType, OwnerKind, TaskStatus
from runtime.transitions import TransitionRequest, execute_transition


class TestPostgresClaimVerifier:
    def _make_project(self, db_session):
        project = RuntimeProject(
            project_key=f"claim-verifier-{uuid4().hex[:8]}",
            title="Claim Verifier Project",
        )
        db_session.add(project)
        db_session.commit()
        return project

    def test_explicit_assignment_claim_succeeds_via_task_owner_truth(self, db_session):
        project = self._make_project(db_session)
        task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Assigned task",
            status=RuntimeTaskStatus.READY,
            owner_kind=RuntimeOwnerKind.DELEGATE,
            owner_id="del-001",
        )
        db_session.add(task)
        db_session.commit()

        verifier = PostgresClaimVerifier(db_session)
        verification = verifier.verify_and_build_context(
            claim_type=ClaimType.EXPLICIT_ASSIGNMENT,
            claim_ref=str(task.task_id),
            delegate_id="del-001",
            task_id=str(task.task_id),
        )
        assert verification.valid is True
        assert verification.claim_context is not None

        result = execute_transition(
            TransitionRequest(
                task_id=str(task.task_id),
                project_id=str(project.project_id),
                from_status=TaskStatus.READY,
                to_status=TaskStatus.ACTIVE,
                role=OwnerKind.DELEGATE,
                role_id="del-001",
                claim_context=verification.claim_context,
            )
        )
        assert result.success is True

    def test_explicit_assignment_claim_rejects_wrong_delegate(self, db_session):
        project = self._make_project(db_session)
        task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Assigned task",
            status=RuntimeTaskStatus.READY,
            owner_kind=RuntimeOwnerKind.DELEGATE,
            owner_id="del-001",
        )
        db_session.add(task)
        db_session.commit()

        verifier = PostgresClaimVerifier(db_session)
        verification = verifier.verify_and_build_context(
            claim_type=ClaimType.EXPLICIT_ASSIGNMENT,
            claim_ref=str(task.task_id),
            delegate_id="del-999",
            task_id=str(task.task_id),
        )
        assert verification.valid is False
        assert verification.claim_context is None

    def test_active_lease_claim_succeeds_via_runtime_truth(self, db_session):
        project = self._make_project(db_session)
        lease_id = uuid4()
        heartbeat_at = datetime.now(timezone.utc)
        task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Leased task",
            status=RuntimeTaskStatus.READY,
            owner_kind=RuntimeOwnerKind.DELEGATE,
            owner_id="del-001",
        )
        db_session.add(task)
        db_session.commit()

        lease = RuntimeWorkerLease(
            lease_id=lease_id,
            task_id=task.task_id,
            owner_kind=RuntimeOwnerKind.DELEGATE,
            owner_id="del-001",
            lease_status=RuntimeLeaseStatus.ACTIVE,
            heartbeat_at=heartbeat_at,
            expires_at=heartbeat_at + timedelta(minutes=5),
        )
        db_session.add(lease)
        db_session.commit()
        task.current_lease_id = lease_id
        db_session.commit()

        verifier = PostgresClaimVerifier(db_session)
        verification = verifier.verify_and_build_context(
            claim_type=ClaimType.ACTIVE_LEASE,
            claim_ref=str(lease_id),
            delegate_id="del-001",
            task_id=str(task.task_id),
        )
        assert verification.valid is True
        assert verification.claim_context is not None

    def test_active_lease_claim_rejects_wrong_delegate(self, db_session):
        project = self._make_project(db_session)
        lease_id = uuid4()
        heartbeat_at = datetime.now(timezone.utc)
        task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Leased task",
            status=RuntimeTaskStatus.READY,
            owner_kind=RuntimeOwnerKind.DELEGATE,
            owner_id="del-001",
        )
        db_session.add(task)
        db_session.commit()

        lease = RuntimeWorkerLease(
            lease_id=lease_id,
            task_id=task.task_id,
            owner_kind=RuntimeOwnerKind.DELEGATE,
            owner_id="del-001",
            lease_status=RuntimeLeaseStatus.ACTIVE,
            heartbeat_at=heartbeat_at,
            expires_at=heartbeat_at + timedelta(minutes=5),
        )
        db_session.add(lease)
        db_session.commit()
        task.current_lease_id = lease_id
        db_session.commit()

        verifier = PostgresClaimVerifier(db_session)
        verification = verifier.verify_and_build_context(
            claim_type=ClaimType.ACTIVE_LEASE,
            claim_ref=str(lease_id),
            delegate_id="del-999",
            task_id=str(task.task_id),
        )
        assert verification.valid is False
        assert verification.claim_context is None
