from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select

from db.models import (
    RuntimeDecision,
    RuntimeDecisionOutcome,
    RuntimeDecisionStatus,
    RuntimeMemoryPacket,
    RuntimeOwnerKind,
    RuntimePacketStatus,
    RuntimeProject,
    RuntimeTask,
    RuntimeTaskStatus,
    RuntimeTaskType,
)
from runtime.db_backed_lifecycle_proof import execute_db_backed_lifecycle_proof
from runtime.operational_closure import (
    align_project_current_work_context,
    persist_reconstructed_work_context,
    reconstruct_runtime_work_context,
)
from runtime.project_surface import (
    bootstrap_runtime_project_surface,
    build_latest_project_runtime_read_surface,
    build_project_runtime_read_surface,
)


class TestProjectRuntimeReadSurface:
    def _make_project(self, db_session):
        project = RuntimeProject(
            project_key=f"project-surface-{uuid4().hex[:8]}",
            title="Project Surface Runtime",
        )
        db_session.add(project)
        db_session.commit()
        return (
            db_session.execute(
                select(RuntimeProject).where(RuntimeProject.project_id == project.project_id)
            )
            .scalars()
            .one()
        )

    def test_build_surface_follows_project_pointer_and_runtime_context(self, db_session):
        project = self._make_project(db_session)
        task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Align runtime surface",
            status=RuntimeTaskStatus.ACTIVE,
            priority=1,
            next_action_summary="Expose current runtime state",
        )
        db_session.add(task)
        db_session.commit()

        context = reconstruct_runtime_work_context(db_session, str(project.project_id))
        persisted = persist_reconstructed_work_context(db_session, context)
        align_project_current_work_context(db_session, str(project.project_id), str(persisted.work_context_id))

        surface = build_project_runtime_read_surface(db_session, str(project.project_id))
        assert surface is not None
        assert surface.current_work_context_id == str(persisted.work_context_id)
        assert surface.current_focus == context.current_focus
        assert surface.metadata["source"] == "runtime_truth_only"
        assert surface.metadata["has_current_context"] is True

    def test_surface_includes_active_waiting_decision_and_trusted_packets(self, db_session):
        project = self._make_project(db_session)
        task_done = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Completed upstream task",
            status=RuntimeTaskStatus.DONE,
            priority=1,
            result_summary="Upstream reviewed work completed",
            owner_kind=RuntimeOwnerKind.DELEGATE,
            owner_id="del-001",
        )
        task_active = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Current active task",
            status=RuntimeTaskStatus.ACTIVE,
            priority=0,
            next_action_summary="Do active work",
            owner_kind=RuntimeOwnerKind.DELEGATE,
            owner_id="del-001",
        )
        task_waiting = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.REVIEW,
            title="Waiting review task",
            status=RuntimeTaskStatus.WAITING,
            priority=2,
            waiting_reason="dependency_unmet",
            waiting_detail="Awaiting active task completion",
        )
        db_session.add_all([task_done, task_active, task_waiting])
        db_session.commit()

        decision = RuntimeDecision(
            project_id=project.project_id,
            task_id=task_active.task_id,
            decision_scope="runtime",
            title="Proceed",
            outcome=RuntimeDecisionOutcome.ADOPT,
            status=RuntimeDecisionStatus.FINAL,
            created_by_kind=RuntimeOwnerKind.CONTROLLER,
            created_by_id="ctrl-001",
            finalized_at=datetime.now(timezone.utc),
        )
        packet = RuntimeMemoryPacket(
            project_id=project.project_id,
            task_id=task_done.task_id,
            packet_type="study_result",
            status=RuntimePacketStatus.ACCEPTED,
            title="Trusted packet",
            summary="Upstream reviewed",
            created_by_kind=RuntimeOwnerKind.DELEGATE,
            created_by_id="del-001",
            accepted_at=datetime.now(timezone.utc),
            extra={
                "acceptance": {
                    "accepted_by": "controller",
                    "accepted_by_id": "ctrl-001",
                    "upstream_task_id": str(task_done.task_id),
                    "upstream_task_status": "done",
                }
            },
        )
        db_session.add_all([decision, packet])
        db_session.commit()

        context = reconstruct_runtime_work_context(db_session, str(project.project_id))
        persisted = persist_reconstructed_work_context(db_session, context)
        align_project_current_work_context(db_session, str(project.project_id), str(persisted.work_context_id))

        surface = build_project_runtime_read_surface(db_session, str(project.project_id))
        assert surface is not None
        assert len(surface.active_tasks) == 1
        assert surface.active_tasks[0].task_id == str(task_active.task_id)
        assert len(surface.waiting_tasks) == 1
        assert surface.waiting_tasks[0].task_id == str(task_waiting.task_id)
        assert surface.latest_decision is not None
        assert surface.latest_decision.decision_id == str(decision.decision_id)
        assert len(surface.trusted_packets) == 1
        assert surface.trusted_packets[0].memory_packet_id == str(packet.memory_packet_id)

    def test_surface_does_not_invent_absent_state(self, db_session):
        project = self._make_project(db_session)

        surface = build_project_runtime_read_surface(db_session, str(project.project_id))
        assert surface is not None
        assert surface.current_work_context_id is None
        assert surface.current_focus is None
        assert surface.latest_decision is None
        assert surface.trusted_packets == []
        assert surface.active_tasks == []
        assert surface.waiting_tasks == []
        assert surface.metadata["has_current_context"] is False

    def test_surface_excludes_untrusted_packets(self, db_session):
        project = self._make_project(db_session)
        task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Task with fake packet",
            status=RuntimeTaskStatus.ACTIVE,
            priority=1,
        )
        db_session.add(task)
        db_session.commit()

        fake_packet = RuntimeMemoryPacket(
            project_id=project.project_id,
            task_id=task.task_id,
            packet_type="study_result",
            status=RuntimePacketStatus.ACCEPTED,
            title="Fake packet",
            summary="No real upstream object",
            created_by_kind=RuntimeOwnerKind.DELEGATE,
            created_by_id="del-001",
            accepted_at=datetime.now(timezone.utc),
            extra={
                "acceptance": {
                    "accepted_by": "controller",
                    "accepted_by_id": "ctrl-001",
                    "upstream_task_id": str(uuid4()),
                    "upstream_task_status": "done",
                }
            },
        )
        db_session.add(fake_packet)
        db_session.commit()

        context = reconstruct_runtime_work_context(db_session, str(project.project_id))
        persisted = persist_reconstructed_work_context(db_session, context)
        align_project_current_work_context(db_session, str(project.project_id), str(persisted.work_context_id))

        surface = build_project_runtime_read_surface(db_session, str(project.project_id))
        assert surface is not None
        assert surface.trusted_packets == []

    def test_surface_excludes_packets_with_non_relevant_upstream_state(self, db_session):
        project = self._make_project(db_session)
        active_task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Still active upstream",
            status=RuntimeTaskStatus.ACTIVE,
            priority=1,
        )
        db_session.add(active_task)
        db_session.commit()

        packet = RuntimeMemoryPacket(
            project_id=project.project_id,
            task_id=active_task.task_id,
            packet_type="study_result",
            status=RuntimePacketStatus.ACCEPTED,
            title="Legacy accepted packet",
            summary="Accepted before read-path relevance hardening",
            created_by_kind=RuntimeOwnerKind.DELEGATE,
            created_by_id="del-001",
            accepted_at=datetime.now(timezone.utc),
            extra={
                "acceptance": {
                    "accepted_by": "controller",
                    "accepted_by_id": "ctrl-001",
                    "upstream_task_id": str(active_task.task_id),
                    "upstream_task_status": "active",
                }
            },
        )
        db_session.add(packet)
        db_session.commit()

        context = reconstruct_runtime_work_context(db_session, str(project.project_id))
        persisted = persist_reconstructed_work_context(db_session, context)
        align_project_current_work_context(
            db_session, str(project.project_id), str(persisted.work_context_id)
        )

        surface = build_project_runtime_read_surface(db_session, str(project.project_id))
        assert surface is not None
        assert surface.trusted_packets == []

    def test_build_latest_surface_returns_most_recent_project(self, db_session):
        older = RuntimeProject(
            project_key=f"project-surface-older-{uuid4().hex[:8]}",
            title="Older Runtime Project",
        )
        db_session.add(older)
        db_session.commit()

        newer = RuntimeProject(
            project_key=f"project-surface-newer-{uuid4().hex[:8]}",
            title="Newer Runtime Project",
        )
        db_session.add(newer)
        db_session.commit()

        latest_surface = build_latest_project_runtime_read_surface(db_session)
        assert latest_surface is not None
        assert latest_surface.project_id == str(newer.project_id)
        assert latest_surface.project_key == newer.project_key

    def test_build_latest_surface_can_target_project_key(self, db_session):
        project = self._make_project(db_session)
        task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Targeted runtime task",
            status=RuntimeTaskStatus.ACTIVE,
            priority=1,
        )
        db_session.add(task)
        db_session.commit()

        surface = build_latest_project_runtime_read_surface(
            db_session,
            project_key=project.project_key,
        )
        assert surface is not None
        assert surface.project_key == project.project_key
        assert len(surface.active_tasks) == 1

    def test_surface_aligns_with_db_backed_lifecycle_proof(self, db_session):
        proof = execute_db_backed_lifecycle_proof(
            db_session,
            title="DB-backed surface alignment proof",
        )
        assert proof.success is True

        context = reconstruct_runtime_work_context(db_session, proof.project_id)
        persisted = persist_reconstructed_work_context(db_session, context)
        align_project_current_work_context(db_session, proof.project_id, str(persisted.work_context_id))

        surface = build_project_runtime_read_surface(db_session, proof.project_id)
        assert surface is not None
        assert surface.project_id == proof.project_id
        assert surface.current_work_context_id == str(persisted.work_context_id)
        assert surface.metadata["has_current_context"] is True
        assert surface.metadata["active_task_count"] == 0
        assert surface.metadata["waiting_task_count"] == 0
        assert surface.active_tasks == []
        assert surface.waiting_tasks == []
        assert surface.current_focus == "No active work"
        assert surface.blockers_summary is None
        assert surface.next_steps_summary is None

    def test_bootstrap_runtime_project_surface_creates_project_explicitly(self, db_session):
        surface = bootstrap_runtime_project_surface(
            db_session,
            project_key=f"runtime-bootstrap-{uuid4().hex[:8]}",
            title="Runtime Bootstrap",
            current_phase="R2-D",
        )

        assert surface.project_key.startswith("runtime-bootstrap-")
        assert surface.title == "Runtime Bootstrap"
        assert surface.current_phase == "R2-D"
        assert surface.metadata["bootstrap_created"] is True
        assert surface.metadata["bootstrap_source"] == "explicit_request"

    def test_bootstrap_runtime_project_surface_reuses_existing_project(self, db_session):
        project = self._make_project(db_session)

        surface = bootstrap_runtime_project_surface(
            db_session,
            project_key=project.project_key,
            title="Ignored Replacement",
        )

        assert surface.project_id == str(project.project_id)
        assert surface.title == project.title
        assert surface.metadata["bootstrap_created"] is False
