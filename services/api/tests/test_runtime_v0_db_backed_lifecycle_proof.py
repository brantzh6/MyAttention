import asyncio
import threading
from unittest.mock import patch

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from db.models import RuntimeProject, RuntimeTask, RuntimeTaskEvent, RuntimeWorkerLease
from config import get_settings
from db.session import engine
from runtime.db_backed_lifecycle_proof import execute_db_backed_lifecycle_proof
from runtime.state_machine import TaskStatus
from tests.conftest import SyncAsyncSessionAdapter


class TestDBBackedLifecycleProof:
    def test_db_backed_lifecycle_proof_persists_truth_path(self, db_session):
        result = execute_db_backed_lifecycle_proof(db_session)

        assert result.success is True, result.error
        assert result.final_status == "done"
        assert result.persisted_event_count >= 6
        assert result.lease_id is not None

        project = (
            db_session.execute(
                select(RuntimeProject).where(RuntimeProject.project_id == result.project_id)
            )
            .scalars()
            .one_or_none()
        )
        assert project is not None

        task = (
            db_session.execute(
                select(RuntimeTask).where(RuntimeTask.task_id == result.task_id)
            )
            .scalars()
            .one_or_none()
        )
        assert task is not None
        assert task.status.value == "done"
        assert task.current_lease_id is None
        assert task.owner_id == "delegate-001"

        events = (
            db_session.execute(
                select(RuntimeTaskEvent).where(RuntimeTaskEvent.task_id == result.task_id)
            )
            .scalars()
            .all()
        )
        assert len(events) >= 6
        event_types = [event.event_type for event in events]
        assert "state_transition" in event_types
        assert "lease_claimed" in event_types
        assert "lease_released" in event_types

        lease = (
            db_session.execute(
                select(RuntimeWorkerLease).where(RuntimeWorkerLease.lease_id == result.lease_id)
            )
            .scalars()
            .one_or_none()
        )
        assert lease is not None
        assert lease.lease_status.value == "released"

    def test_db_backed_lifecycle_proof_uses_distinct_project_key(self, db_session):
        first = execute_db_backed_lifecycle_proof(db_session)
        second = execute_db_backed_lifecycle_proof(db_session)

        assert first.success is True, first.error
        assert second.success is True, second.error
        assert first.project_id != second.project_id
        assert first.task_id != second.task_id

    def test_db_backed_lifecycle_proof_repeated_runs_stay_isolated(self, db_session):
        first = execute_db_backed_lifecycle_proof(db_session)
        second = execute_db_backed_lifecycle_proof(db_session)

        assert first.success is True, first.error
        assert second.success is True, second.error
        assert first.project_id != second.project_id
        assert first.task_id != second.task_id
        assert first.lease_id != second.lease_id
        assert set(first.event_ids).isdisjoint(set(second.event_ids))

        projects = (
            db_session.execute(
                select(RuntimeProject).where(
                    RuntimeProject.project_id.in_([first.project_id, second.project_id])
                )
            )
            .scalars()
            .all()
        )
        tasks = (
            db_session.execute(
                select(RuntimeTask).where(
                    RuntimeTask.task_id.in_([first.task_id, second.task_id])
                )
            )
            .scalars()
            .all()
        )
        events = (
            db_session.execute(
                select(RuntimeTaskEvent).where(
                    RuntimeTaskEvent.task_id.in_([first.task_id, second.task_id])
                )
            )
            .scalars()
            .all()
        )
        leases = (
            db_session.execute(
                select(RuntimeWorkerLease).where(
                    RuntimeWorkerLease.lease_id.in_([first.lease_id, second.lease_id])
                )
            )
            .scalars()
            .all()
        )

        assert len(projects) == 2
        assert len(tasks) == 2
        assert len(leases) == 2
        assert len(events) == first.persisted_event_count + second.persisted_event_count

    def test_db_backed_lifecycle_proof_overlapping_runs_stay_isolated(self, db_session, async_runner):
        barrier = threading.Barrier(2)
        results = []
        errors = []
        lock = threading.Lock()

        settings = get_settings()

        def run_one():
            try:
                with asyncio.Runner() as runner:
                    local_engine = create_async_engine(
                        settings.database_url,
                        echo=False,
                        pool_pre_ping=True,
                        poolclass=NullPool,
                    )
                    local_session_maker = async_sessionmaker(
                        local_engine,
                        class_=AsyncSession,
                        expire_on_commit=False,
                        autocommit=False,
                        autoflush=False,
                    )
                    session = local_session_maker()
                    try:
                        adapter = SyncAsyncSessionAdapter(runner, session)
                        adapter.execute("SELECT 1")
                        try:
                            barrier.wait(timeout=5)
                            result = execute_db_backed_lifecycle_proof(adapter)
                            with lock:
                                results.append(result)
                        finally:
                            try:
                                adapter.rollback()
                            finally:
                                runner.run(session.close())
                    finally:
                        runner.run(local_engine.dispose())
            except Exception as exc:
                with lock:
                    errors.append(exc)

        t1 = threading.Thread(target=run_one, daemon=True)
        t2 = threading.Thread(target=run_one, daemon=True)
        t1.start()
        t2.start()
        t1.join(timeout=30)
        t2.join(timeout=30)

        assert not errors, errors
        assert len(results) == 2
        first, second = results
        assert first.success is True, first.error
        assert second.success is True, second.error
        assert first.project_id != second.project_id
        assert first.task_id != second.task_id
        assert first.lease_id != second.lease_id
        assert set(first.event_ids).isdisjoint(set(second.event_ids))

        tasks = (
            db_session.execute(
                select(RuntimeTask).where(
                    RuntimeTask.task_id.in_([first.task_id, second.task_id])
                )
            )
            .scalars()
            .all()
        )
        events = (
            db_session.execute(
                select(RuntimeTaskEvent).where(
                    RuntimeTaskEvent.task_id.in_([first.task_id, second.task_id])
                )
            )
            .scalars()
            .all()
        )
        leases = (
            db_session.execute(
                select(RuntimeWorkerLease).where(
                    RuntimeWorkerLease.lease_id.in_([first.lease_id, second.lease_id])
                )
            )
            .scalars()
            .all()
        )

        assert len(tasks) == 2
        assert len(leases) == 2
        assert len(events) == first.persisted_event_count + second.persisted_event_count

    def test_db_backed_lifecycle_proof_failure_reports_durable_partial_state(self, db_session):
        from runtime import db_backed_lifecycle_proof as proof_module

        original_execute_transition = proof_module.execute_transition

        def fail_on_ready_to_active(request):
            if request.from_status == TaskStatus.READY and request.to_status == TaskStatus.ACTIVE:
                raise ValueError("synthetic ready->active failure")
            return original_execute_transition(request)

        with patch.object(proof_module, "execute_transition", side_effect=fail_on_ready_to_active):
            result = execute_db_backed_lifecycle_proof(db_session)

        assert result.success is False
        assert "synthetic ready->active failure" in (result.error or "")
        assert result.final_status == "ready"
        assert result.persisted_event_count == 2

        task = (
            db_session.execute(
                select(RuntimeTask).where(RuntimeTask.task_id == result.task_id)
            )
            .scalars()
            .one_or_none()
        )
        assert task is not None
        assert task.status.value == "ready"

        events = (
            db_session.execute(
                select(RuntimeTaskEvent).where(RuntimeTaskEvent.task_id == result.task_id)
            )
            .scalars()
            .all()
        )
        event_types = [event.event_type for event in events]
        assert len(events) == 2
        assert "state_transition" in event_types
        assert "lease_claimed" in event_types
