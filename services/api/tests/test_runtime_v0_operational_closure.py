from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import select

from db.models import (
    RuntimeContextStatus,
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
    RuntimeWorkContext,
)
from runtime.memory_packets import is_packet_trusted
from runtime.operational_closure import (
    ArchivedContextAlignmentError,
    NoActiveContextError,
    RuntimeContextAlignmentError,
    UpstreamRelevanceError,
    _packet_from_row,
    align_project_current_work_context,
    get_project_current_work_context,
    persist_reconstructed_work_context,
    promote_reviewed_memory_packet,
    reconstruct_runtime_work_context,
    transition_packet_to_review,
    verify_runtime_upstream_exists,
    verify_runtime_upstream_relevant,
)
from runtime.state_machine import OwnerKind


class TestOperationalClosure:
    def _make_project(self, db_session):
        project = RuntimeProject(
            project_key=f"operational-closure-{uuid4().hex[:8]}",
            title="Operational Closure Project",
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

    def test_reconstruct_runtime_work_context_from_canonical_truth(self, db_session):
        project = self._make_project(db_session)
        task_done = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Completed upstream work",
            status=RuntimeTaskStatus.DONE,
            priority=1,
            result_summary="Completed reviewed upstream work",
            owner_kind=RuntimeOwnerKind.DELEGATE,
            owner_id="del-001",
        )
        task_active = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Ship closure adapter",
            status=RuntimeTaskStatus.ACTIVE,
            priority=0,
            next_action_summary="Finish narrow service helper",
            owner_kind=RuntimeOwnerKind.DELEGATE,
            owner_id="del-001",
        )
        task_waiting = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Blocked follow-up",
            status=RuntimeTaskStatus.WAITING,
            priority=2,
            waiting_reason="dependency_unmet",
            waiting_detail="Awaiting reviewed artifact",
        )
        db_session.add(task_done)
        db_session.commit()
        db_session.add_all([task_active, task_waiting])
        db_session.commit()

        decision = RuntimeDecision(
            project_id=project.project_id,
            task_id=task_active.task_id,
            decision_scope="runtime",
            title="Proceed with R1-D",
            outcome=RuntimeDecisionOutcome.ADOPT,
            status=RuntimeDecisionStatus.FINAL,
            created_by_kind=RuntimeOwnerKind.CONTROLLER,
            created_by_id="ctrl-001",
            finalized_at=datetime.now(timezone.utc),
        )
        db_session.add(decision)
        db_session.commit()

        packet = RuntimeMemoryPacket(
            project_id=project.project_id,
            task_id=task_done.task_id,
            packet_type="study_result",
            status=RuntimePacketStatus.ACCEPTED,
            title="Reviewed closure result",
            summary="Trusted closure artifact",
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
        db_session.add(packet)
        db_session.commit()
        packet_row = (
            db_session.execute(
                select(RuntimeMemoryPacket).where(
                    RuntimeMemoryPacket.memory_packet_id == packet.memory_packet_id
                )
            )
            .scalars()
            .one()
        )
        assert verify_runtime_upstream_relevant(db_session, "task", str(task_done.task_id))[0]
        assert is_packet_trusted(
            _packet_from_row(packet_row),
            verify_upstream_exists=lambda t, oid: verify_runtime_upstream_relevant(
                db_session, t, oid
            )[0],
        )

        context = reconstruct_runtime_work_context(db_session, str(project.project_id))
        assert context.active_task_id == str(task_active.task_id)
        assert context.latest_decision_id == str(decision.decision_id)
        assert context.packet_ref_id == str(packet.memory_packet_id)
        assert "dependency_unmet" in (context.blockers_summary or "")
        assert context.metadata["reconstructed_from"] == "canonical_state"

    def test_reconstruct_excludes_untrusted_packet_from_context(self, db_session):
        project = self._make_project(db_session)
        packet = RuntimeMemoryPacket(
            project_id=project.project_id,
            packet_type="study_result",
            status=RuntimePacketStatus.ACCEPTED,
            title="Fake trusted packet",
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
        db_session.add(packet)
        db_session.commit()

        context = reconstruct_runtime_work_context(db_session, str(project.project_id))
        assert context.packet_ref_id is None

    def test_reconstruct_excludes_packet_with_non_relevant_upstream_state(self, db_session):
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
            summary="Accepted before stricter upstream relevance",
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
        assert context.packet_ref_id is None

    def test_persist_reconstructed_work_context_archives_previous_active(self, db_session):
        project = self._make_project(db_session)
        old_context = RuntimeWorkContext(
            project_id=project.project_id,
            status=RuntimeContextStatus.ACTIVE,
            current_focus="Old focus",
        )
        db_session.add(old_context)
        db_session.commit()

        task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Current active task",
            status=RuntimeTaskStatus.ACTIVE,
            priority=1,
            next_action_summary="Do the thing",
        )
        db_session.add(task)
        db_session.commit()

        context = reconstruct_runtime_work_context(db_session, str(project.project_id))
        persisted = persist_reconstructed_work_context(db_session, context)
        assert persisted.status == RuntimeContextStatus.ACTIVE
        archived = (
            db_session.execute(
                select(RuntimeWorkContext).where(
                    RuntimeWorkContext.work_context_id == old_context.work_context_id
                )
            )
            .scalars()
            .one()
        )
        assert archived.status == RuntimeContextStatus.ARCHIVED

    def test_align_project_pointer_to_active_reconstructed_context(self, db_session):
        project = self._make_project(db_session)
        task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Current active task",
            status=RuntimeTaskStatus.ACTIVE,
            priority=1,
            next_action_summary="Align project pointer",
        )
        db_session.add(task)
        db_session.commit()

        context = reconstruct_runtime_work_context(db_session, str(project.project_id))
        persisted = persist_reconstructed_work_context(db_session, context)
        aligned_project = align_project_current_work_context(
            db_session, str(project.project_id), str(persisted.work_context_id)
        )
        assert aligned_project.current_work_context_id == persisted.work_context_id

        visible_context = get_project_current_work_context(db_session, str(project.project_id))
        assert visible_context is not None
        assert visible_context.work_context_id == persisted.work_context_id
        assert visible_context.active_task_id == persisted.active_task_id

    def test_align_project_pointer_defaults_to_runtime_active_context(self, db_session):
        project = self._make_project(db_session)
        task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Auto align active context",
            status=RuntimeTaskStatus.ACTIVE,
            priority=1,
        )
        db_session.add(task)
        db_session.commit()

        context = reconstruct_runtime_work_context(db_session, str(project.project_id))
        persisted = persist_reconstructed_work_context(db_session, context)
        aligned_project = align_project_current_work_context(db_session, str(project.project_id))
        assert aligned_project.current_work_context_id == persisted.work_context_id

    def test_project_pointer_does_not_follow_archived_context(self, db_session):
        project = self._make_project(db_session)
        first_task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="First active task",
            status=RuntimeTaskStatus.ACTIVE,
            priority=2,
        )
        db_session.add(first_task)
        db_session.commit()

        ctx1 = reconstruct_runtime_work_context(db_session, str(project.project_id))
        persisted1 = persist_reconstructed_work_context(db_session, ctx1)
        align_project_current_work_context(db_session, str(project.project_id), str(persisted1.work_context_id))

        first_task.status = RuntimeTaskStatus.DONE
        first_task.result_summary = "First active task completed"
        second_task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Second active task",
            status=RuntimeTaskStatus.ACTIVE,
            priority=0,
        )
        db_session.add(second_task)
        db_session.commit()

        ctx2 = reconstruct_runtime_work_context(db_session, str(project.project_id))
        persisted2 = persist_reconstructed_work_context(db_session, ctx2)
        align_project_current_work_context(db_session, str(project.project_id))

        visible_context = get_project_current_work_context(db_session, str(project.project_id))
        assert visible_context is not None
        assert visible_context.work_context_id == persisted2.work_context_id
        assert visible_context.work_context_id != persisted1.work_context_id

    def test_promote_reviewed_memory_packet_to_trusted(self, db_session):
        project = self._make_project(db_session)
        task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Reviewed task",
            status=RuntimeTaskStatus.DONE,
            result_summary="Reviewed upstream work completed",
        )
        db_session.add(task)
        db_session.commit()

        packet = RuntimeMemoryPacket(
            project_id=project.project_id,
            task_id=task.task_id,
            packet_type="study_result",
            status=RuntimePacketStatus.DRAFT,
            title="Closure artifact",
            summary="Compact reviewed outcome",
            created_by_kind=RuntimeOwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        db_session.add(packet)
        db_session.commit()

        transition_packet_to_review(db_session, str(packet.memory_packet_id))
        promoted = promote_reviewed_memory_packet(
            db_session,
            str(packet.memory_packet_id),
            accepted_by_kind=OwnerKind.CONTROLLER,
            accepted_by_id="ctrl-001",
            upstream_task_id=str(task.task_id),
            upstream_task_status="done",
        )
        assert promoted.status == RuntimePacketStatus.ACCEPTED
        assert promoted.accepted_at is not None
        packet_model = RuntimeMemoryPacket(
            memory_packet_id=promoted.memory_packet_id,
            project_id=promoted.project_id,
            task_id=promoted.task_id,
            packet_type=promoted.packet_type,
            status=promoted.status,
            acceptance_trigger=promoted.acceptance_trigger,
            title=promoted.title,
            summary=promoted.summary or "",
            storage_ref=promoted.storage_ref,
            content_hash=promoted.content_hash,
            parent_packet_id=promoted.parent_packet_id,
            created_by_kind=promoted.created_by_kind,
            created_by_id=promoted.created_by_id,
            created_at=promoted.created_at,
            accepted_at=promoted.accepted_at,
            extra=promoted.extra,
        )
        # only use the helper's trust rule, not packet presence
        from runtime.operational_closure import _packet_from_row
        assert is_packet_trusted(
            _packet_from_row(packet_model),
            verify_upstream_exists=lambda t, oid: verify_runtime_upstream_exists(db_session, t, oid),
        ) is True

    def test_transition_packet_to_review_records_truthful_review_submission_provenance(self, db_session):
        project = self._make_project(db_session)
        packet = RuntimeMemoryPacket(
            project_id=project.project_id,
            packet_type="study_result",
            status=RuntimePacketStatus.DRAFT,
            title="Reviewer-created closure artifact",
            summary="Needs review provenance",
            created_by_kind=RuntimeOwnerKind.REVIEWER,
            created_by_id="rev-001",
        )
        db_session.add(packet)
        db_session.commit()

        transitioned = transition_packet_to_review(db_session, str(packet.memory_packet_id))
        assert transitioned.status == RuntimePacketStatus.PENDING_REVIEW
        assert transitioned.extra["review_submitted_by"] == "reviewer"
        assert transitioned.extra["review_submitted_by_id"] == "rev-001"
        submission = transitioned.extra["review_submission"]
        assert submission["submitted_by"] == "reviewer"
        assert submission["submitted_by_id"] == "rev-001"
        assert submission["reason"] == "Submitted for reviewed operational closure"

    def test_transition_packet_to_review_rejects_empty_created_by_id(self, db_session):
        project = self._make_project(db_session)
        packet = RuntimeMemoryPacket(
            project_id=project.project_id,
            packet_type="study_result",
            status=RuntimePacketStatus.DRAFT,
            title="Bad provenance artifact",
            summary="Missing creator id",
            created_by_kind=RuntimeOwnerKind.DELEGATE,
            created_by_id="",
        )
        db_session.add(packet)
        db_session.commit()

        with pytest.raises(Exception, match="non-empty triggered_by_id"):
            transition_packet_to_review(db_session, str(packet.memory_packet_id))

    def test_promote_reviewed_memory_packet_rejects_missing_upstream(self, db_session):
        project = self._make_project(db_session)
        packet = RuntimeMemoryPacket(
            project_id=project.project_id,
            packet_type="study_result",
            status=RuntimePacketStatus.DRAFT,
            title="Bad closure artifact",
            summary="No real upstream",
            created_by_kind=RuntimeOwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        db_session.add(packet)
        db_session.commit()

        transition_packet_to_review(db_session, str(packet.memory_packet_id))
        with pytest.raises(Exception):
            promote_reviewed_memory_packet(
                db_session,
                str(packet.memory_packet_id),
                accepted_by_kind=OwnerKind.CONTROLLER,
                accepted_by_id="ctrl-001",
                upstream_task_id=str(uuid4()),
                upstream_task_status="done",
            )

        refreshed = (
            db_session.execute(
                select(RuntimeMemoryPacket).where(
                    RuntimeMemoryPacket.memory_packet_id == packet.memory_packet_id
                )
            )
            .scalars()
            .one()
        )
        assert refreshed.status == RuntimePacketStatus.PENDING_REVIEW

    # ──────────────────────────────────────────────────────────────
    # R1-I1: Archived-context rejection guardrails
    # ──────────────────────────────────────────────────────────────

    def test_align_explicit_work_context_rejects_archived_context(self, db_session):
        """R1-I1: Explicit alignment must reject archived (non-active) contexts."""
        project = self._make_project(db_session)
        archived_context = RuntimeWorkContext(
            project_id=project.project_id,
            status=RuntimeContextStatus.ARCHIVED,
            current_focus="Old archived focus",
        )
        db_session.add(archived_context)
        db_session.commit()

        with pytest.raises(ArchivedContextAlignmentError, match="not ACTIVE"):
            align_project_current_work_context(
                db_session,
                str(project.project_id),
                str(archived_context.work_context_id),
            )

    def test_align_explicit_work_context_rejects_wrong_project_context(self, db_session):
        """R1-I1: Explicit alignment must reject context from different project."""
        project = self._make_project(db_session)
        other_project = RuntimeProject(
            project_key=f"other-project-{uuid4().hex[:8]}",
            title="Other Project",
        )
        db_session.add(other_project)
        db_session.commit()
        other_context = RuntimeWorkContext(
            project_id=other_project.project_id,
            status=RuntimeContextStatus.ACTIVE,
        )
        db_session.add(other_context)
        db_session.commit()

        with pytest.raises(RuntimeContextAlignmentError, match="does not exist for project"):
            align_project_current_work_context(
                db_session,
                str(project.project_id),
                str(other_context.work_context_id),
            )

    def test_align_implicit_raises_no_active_context_when_none_exists(self, db_session):
        """R1-I1: Implicit alignment raises explicit NoActiveContextError."""
        project = self._make_project(db_session)
        # No active context exists

        with pytest.raises(NoActiveContextError, match="no active RuntimeWorkContext"):
            align_project_current_work_context(db_session, str(project.project_id))

    def test_align_raises_explicit_error_for_missing_project(self, db_session):
        """R1-I1: Missing project raises explicit RuntimeContextAlignmentError."""
        fake_project_id = str(uuid4())

        with pytest.raises(RuntimeContextAlignmentError, match="does not exist"):
            align_project_current_work_context(db_session, fake_project_id)

    def test_align_raises_explicit_error_for_missing_explicit_context(self, db_session):
        """R1-I1: Missing explicit context raises explicit RuntimeContextAlignmentError."""
        project = self._make_project(db_session)
        fake_context_id = str(uuid4())

        with pytest.raises(RuntimeContextAlignmentError, match="does not exist"):
            align_project_current_work_context(
                db_session,
                str(project.project_id),
                fake_context_id,
            )

    def test_get_project_current_work_context_returns_none_for_archived_pointer(self, db_session):
        """R1-I1: Read helper returns None if pointer references archived context."""
        project = self._make_project(db_session)
        archived_context = RuntimeWorkContext(
            project_id=project.project_id,
            status=RuntimeContextStatus.ARCHIVED,
        )
        db_session.add(archived_context)
        db_session.commit()
        project.current_work_context_id = archived_context.work_context_id
        db_session.commit()

        # R1-I1: Read helper returns None for archived context
        result = get_project_current_work_context(db_session, str(project.project_id))
        assert result is None

    # ──────────────────────────────────────────────────────────────
    # R1-I1: Upstream relevance guardrails
    # ──────────────────────────────────────────────────────────────

    def test_verify_upstream_relevant_accepts_done_task(self, db_session):
        """R1-I1: DONE task is relevant for trusted upstream."""
        project = self._make_project(db_session)
        task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Completed task",
            status=RuntimeTaskStatus.DONE,
            result_summary="Task completed successfully",
        )
        db_session.add(task)
        db_session.commit()

        is_relevant, reason = verify_runtime_upstream_relevant(
            db_session, "task", str(task.task_id)
        )
        assert is_relevant is True
        assert "DONE" in reason

    def test_verify_upstream_relevant_accepts_review_pending_task(self, db_session):
        """R1-I1: REVIEW_PENDING task is relevant for trusted upstream."""
        project = self._make_project(db_session)
        task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Task awaiting review",
            status=RuntimeTaskStatus.REVIEW_PENDING,
        )
        db_session.add(task)
        db_session.commit()

        is_relevant, reason = verify_runtime_upstream_relevant(
            db_session, "task", str(task.task_id)
        )
        assert is_relevant is True
        assert "REVIEW_PENDING" in reason

    def test_verify_upstream_relevant_rejects_active_task(self, db_session):
        """R1-I1: ACTIVE task is NOT relevant for trusted upstream (not terminal)."""
        project = self._make_project(db_session)
        task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="In-progress task",
            status=RuntimeTaskStatus.ACTIVE,
        )
        db_session.add(task)
        db_session.commit()

        is_relevant, reason = verify_runtime_upstream_relevant(
            db_session, "task", str(task.task_id)
        )
        assert is_relevant is False
        assert "ACTIVE" in reason
        assert "DONE or REVIEW_PENDING" in reason

    def test_verify_upstream_relevant_accepts_final_decision(self, db_session):
        """R1-I1: FINAL decision with finalized_at is relevant."""
        project = self._make_project(db_session)
        decision = RuntimeDecision(
            project_id=project.project_id,
            decision_scope="runtime",
            title="Finalized decision",
            outcome=RuntimeDecisionOutcome.ADOPT,
            status=RuntimeDecisionStatus.FINAL,
            created_by_kind=RuntimeOwnerKind.CONTROLLER,
            created_by_id="ctrl-001",
            finalized_at=datetime.now(timezone.utc),
        )
        db_session.add(decision)
        db_session.commit()

        is_relevant, reason = verify_runtime_upstream_relevant(
            db_session, "decision", str(decision.decision_id)
        )
        assert is_relevant is True
        assert "finalized" in reason.lower()

    def test_verify_upstream_relevant_rejects_draft_decision(self, db_session):
        """R1-I1: DRAFT decision is NOT relevant (not finalized)."""
        project = self._make_project(db_session)
        decision = RuntimeDecision(
            project_id=project.project_id,
            decision_scope="runtime",
            title="Draft decision",
            outcome=RuntimeDecisionOutcome.ADOPT,
            status=RuntimeDecisionStatus.DRAFT,
            created_by_kind=RuntimeOwnerKind.CONTROLLER,
            created_by_id="ctrl-001",
        )
        db_session.add(decision)
        db_session.commit()

        is_relevant, reason = verify_runtime_upstream_relevant(
            db_session, "decision", str(decision.decision_id)
        )
        assert is_relevant is False
        assert "DRAFT" in reason
        assert "FINAL" in reason

    def test_promote_packet_rejects_active_task_upstream(self, db_session):
        """R1-I1: Packet promotion rejects non-terminal (ACTIVE) task upstream."""
        project = self._make_project(db_session)
        active_task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Still in progress",
            status=RuntimeTaskStatus.ACTIVE,
        )
        db_session.add(active_task)
        packet = RuntimeMemoryPacket(
            project_id=project.project_id,
            task_id=active_task.task_id,
            packet_type="study_result",
            status=RuntimePacketStatus.DRAFT,
            title="Premature closure",
            summary="Upstream not reviewed",
            created_by_kind=RuntimeOwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        db_session.add_all([active_task, packet])
        db_session.commit()

        transition_packet_to_review(db_session, str(packet.memory_packet_id))
        with pytest.raises(UpstreamRelevanceError, match="ACTIVE"):
            promote_reviewed_memory_packet(
                db_session,
                str(packet.memory_packet_id),
                accepted_by_kind=OwnerKind.CONTROLLER,
                accepted_by_id="ctrl-001",
                upstream_task_id=str(active_task.task_id),
                upstream_task_status="active",
            )

    def test_promote_packet_accepts_done_task_upstream(self, db_session):
        """R1-I1: Packet promotion accepts DONE (terminal) task upstream."""
        project = self._make_project(db_session)
        done_task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Completed",
            status=RuntimeTaskStatus.DONE,
            result_summary="Work completed",
        )
        db_session.add(done_task)
        packet = RuntimeMemoryPacket(
            project_id=project.project_id,
            task_id=done_task.task_id,
            packet_type="study_result",
            status=RuntimePacketStatus.DRAFT,
            title="Valid closure",
            summary="Trusted upstream",
            created_by_kind=RuntimeOwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        db_session.add_all([done_task, packet])
        db_session.commit()

        transition_packet_to_review(db_session, str(packet.memory_packet_id))
        promoted = promote_reviewed_memory_packet(
            db_session,
            str(packet.memory_packet_id),
            accepted_by_kind=OwnerKind.CONTROLLER,
            accepted_by_id="ctrl-001",
            upstream_task_id=str(done_task.task_id),
            upstream_task_status="done",
        )
        assert promoted.status == RuntimePacketStatus.ACCEPTED
        assert promoted.accepted_at is not None
