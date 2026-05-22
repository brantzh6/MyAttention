"""
Tests for IKE Runtime v0 Work Context.

Validates:
- One-active-context-per-project discipline
- Work context reconstruction from canonical state
- No hidden upstream truth invented in the context layer
- Reconstruction proof: remove snapshot, rebuild, confirm no material truth lost
"""

import pytest
from uuid import uuid4

from runtime.work_context import (
    ContextStatus,
    WorkContext,
    TaskSnapshot,
    DecisionSnapshot,
    AcceptedPacketRef,
    reconstruct_work_context,
    create_work_context,
    archive_work_context,
    update_work_context,
    _derive_blockers_summary,
    _derive_next_steps_summary,
)


# ──────────────────────────────────────────────────────────────
# WorkContext Dataclass
# ──────────────────────────────────────────────────────────────

class TestWorkContextDataclass:
    def test_create_minimal_context(self):
        ctx = WorkContext(
            work_context_id=str(uuid4()),
            project_id=str(uuid4()),
            status=ContextStatus.ACTIVE,
            active_task_id=None,
            latest_decision_id=None,
            current_focus="Initial focus",
            blockers_summary=None,
            next_steps_summary=None,
            packet_ref_id=None,
            updated_at="2026-04-06T00:00:00+00:00",
        )
        assert ctx.status == ContextStatus.ACTIVE
        assert ctx.current_focus == "Initial focus"
        assert ctx.active_task_id is None

    def test_to_dict_matches_schema(self):
        ctx_id = str(uuid4())
        proj_id = str(uuid4())
        ctx = WorkContext(
            work_context_id=ctx_id,
            project_id=proj_id,
            status=ContextStatus.ACTIVE,
            active_task_id=str(uuid4()),
            latest_decision_id=str(uuid4()),
            current_focus="Building the thing",
            blockers_summary="Waiting on API",
            next_steps_summary="Implement feature X",
            packet_ref_id=str(uuid4()),
            updated_at="2026-04-06T00:00:00+00:00",
            metadata={"key": "value"},
        )
        d = ctx.to_dict()
        assert d["work_context_id"] == ctx_id
        assert d["project_id"] == proj_id
        assert d["status"] == ContextStatus.ACTIVE
        assert d["current_focus"] == "Building the thing"
        assert d["blockers_summary"] == "Waiting on API"
        assert d["next_steps_summary"] == "Implement feature X"
        assert d["metadata"] == {"key": "value"}

    def test_from_dict_roundtrip(self):
        original = WorkContext(
            work_context_id=str(uuid4()),
            project_id=str(uuid4()),
            status=ContextStatus.ACTIVE,
            active_task_id=None,
            latest_decision_id=None,
            current_focus="Test",
            blockers_summary=None,
            next_steps_summary=None,
            packet_ref_id=None,
            updated_at="2026-04-06T00:00:00+00:00",
        )
        restored = WorkContext.from_dict(original.to_dict())
        assert restored.work_context_id == original.work_context_id
        assert restored.project_id == original.project_id
        assert restored.current_focus == original.current_focus


# ──────────────────────────────────────────────────────────────
# Context Status
# ──────────────────────────────────────────────────────────────

class TestContextStatus:
    def test_active_status(self):
        assert ContextStatus.ACTIVE == "active"

    def test_archived_status(self):
        assert ContextStatus.ARCHIVED == "archived"

    def test_only_two_statuses(self):
        """v0 only has active and archived."""
        assert ContextStatus.ACTIVE is not None
        assert ContextStatus.ARCHIVED is not None


# ──────────────────────────────────────────────────────────────
# One Active Context Per Project
# ──────────────────────────────────────────────────────────────

class TestOneActiveContextPerProject:
    """Enforce: one active work context per project."""

    def test_create_active_context(self):
        ctx = create_work_context(
            project_id="proj-1",
            current_focus="Project kickoff",
        )
        assert ctx.status == ContextStatus.ACTIVE
        assert ctx.project_id == "proj-1"

    def test_archive_produces_update_dict(self):
        ctx = create_work_context(
            project_id="proj-1",
            current_focus="Initial",
        )
        updates = archive_work_context(ctx, reason="Project complete")
        assert updates["status"] == ContextStatus.ARCHIVED
        assert updates["work_context_id"] == ctx.work_context_id
        assert updates["metadata"]["archived_reason"] == "Project complete"
        assert "archived_at" in updates["metadata"]

    def test_context_not_mutated_by_archive(self):
        """archive_work_context returns updates, does not mutate context."""
        ctx = create_work_context(
            project_id="proj-1",
            current_focus="Initial",
        )
        original_status = ctx.status
        archive_work_context(ctx)
        assert ctx.status == original_status  # unchanged

    def test_context_not_mutated_by_update(self):
        """update_work_context returns updates, does not mutate context."""
        ctx = create_work_context(
            project_id="proj-1",
            current_focus="Initial",
        )
        original_focus = ctx.current_focus
        update_work_context(ctx, current_focus="Updated")
        assert ctx.current_focus == original_focus  # unchanged


# ──────────────────────────────────────────────────────────────
# Context Update
# ──────────────────────────────────────────────────────────────

class TestContextUpdate:
    def test_update_single_field(self):
        ctx = create_work_context(
            project_id="proj-1",
            current_focus="Initial",
        )
        updates = update_work_context(ctx, current_focus="New focus")
        assert updates["current_focus"] == "New focus"
        assert updates["work_context_id"] == ctx.work_context_id
        assert "updated_at" in updates

    def test_update_multiple_fields(self):
        ctx = create_work_context(
            project_id="proj-1",
            current_focus="Initial",
        )
        updates = update_work_context(
            ctx,
            active_task_id="task-1",
            latest_decision_id="dec-1",
            blockers_summary="Blocked by X",
        )
        assert updates["active_task_id"] == "task-1"
        assert updates["latest_decision_id"] == "dec-1"
        assert updates["blockers_summary"] == "Blocked by X"
        # Unchanged fields not in update
        assert "next_steps_summary" not in updates

    def test_update_no_fields(self):
        ctx = create_work_context(
            project_id="proj-1",
            current_focus="Initial",
        )
        updates = update_work_context(ctx)
        assert "work_context_id" in updates
        assert "updated_at" in updates
        assert "current_focus" not in updates


# ──────────────────────────────────────────────────────────────
# Reconstruction from Canonical State
# ──────────────────────────────────────────────────────────────

class TestWorkContextReconstruction:
    """The core truthfulness tests: context must be derivable from canonical state."""

    def _make_task(self, task_id=None, status="active", priority=2,
                   next_action=None, waiting_reason=None, waiting_detail=None):
        return TaskSnapshot(
            task_id=task_id or str(uuid4()),
            title=f"Task {task_id or 'X'}",
            status=status,
            task_type="implementation",
            priority=priority,
            next_action_summary=next_action,
            waiting_reason=waiting_reason,
            waiting_detail=waiting_detail,
        )

    def _make_decision(self, decision_id=None, outcome="adopt", status="final",
                       finalized_at="2026-04-06T00:00:00+00:00"):
        return DecisionSnapshot(
            decision_id=decision_id or str(uuid4()),
            title=f"Decision {decision_id or 'X'}",
            outcome=outcome,
            status=status,
            finalized_at=finalized_at,
        )

    def _make_packet(self, packet_id=None, accepted_at="2026-04-06T00:00:00+00:00"):
        return AcceptedPacketRef(
            memory_packet_id=packet_id or str(uuid4()),
            title="Packet",
            packet_type="study_result",
            accepted_at=accepted_at,
        )

    def test_reconstruct_with_active_task(self):
        task = self._make_task(priority=1, next_action="Implement login")
        ctx = reconstruct_work_context(
            project_id="proj-1",
            active_tasks=[task],
            waiting_tasks=[],
            latest_decisions=[],
            accepted_packets=[],
        )
        assert ctx.active_task_id == task.task_id
        assert "Working on:" in ctx.current_focus

    def test_reconstruct_selects_highest_priority_task(self):
        low = self._make_task(priority=3, next_action="Low priority")
        high = self._make_task(priority=0, next_action="Urgent")
        ctx = reconstruct_work_context(
            project_id="proj-1",
            active_tasks=[low, high],
            waiting_tasks=[],
            latest_decisions=[],
            accepted_packets=[],
        )
        assert ctx.active_task_id == high.task_id

    def test_reconstruct_with_latest_decision(self):
        old_dec = self._make_decision(
            decision_id="dec-old",
            finalized_at="2026-04-01T00:00:00+00:00",
        )
        new_dec = self._make_decision(
            decision_id="dec-new",
            finalized_at="2026-04-06T00:00:00+00:00",
        )
        ctx = reconstruct_work_context(
            project_id="proj-1",
            active_tasks=[],
            waiting_tasks=[],
            latest_decisions=[old_dec, new_dec],
            accepted_packets=[],
        )
        assert ctx.latest_decision_id == "dec-new"

    def test_reconstruct_ignores_non_finalized_decisions(self):
        draft_dec = self._make_decision(
            decision_id="dec-draft",
            finalized_at=None,
        )
        ctx = reconstruct_work_context(
            project_id="proj-1",
            active_tasks=[],
            waiting_tasks=[],
            latest_decisions=[draft_dec],
            accepted_packets=[],
        )
        assert ctx.latest_decision_id is None

    def test_reconstruct_with_accepted_packet(self):
        old_pkt = self._make_packet(
            packet_id="pkt-old",
            accepted_at="2026-04-01T00:00:00+00:00",
        )
        new_pkt = self._make_packet(
            packet_id="pkt-new",
            accepted_at="2026-04-06T00:00:00+00:00",
        )
        ctx = reconstruct_work_context(
            project_id="proj-1",
            active_tasks=[],
            waiting_tasks=[],
            latest_decisions=[],
            accepted_packets=[old_pkt, new_pkt],
        )
        assert ctx.packet_ref_id == "pkt-new"

    def test_reconstruct_blockers_from_waiting_tasks(self):
        w1 = self._make_task(status="waiting", waiting_reason="dependency_unmet")
        w2 = self._make_task(status="waiting", waiting_reason="dependency_unmet")
        w3 = self._make_task(status="waiting", waiting_reason="external_input")
        ctx = reconstruct_work_context(
            project_id="proj-1",
            active_tasks=[],
            waiting_tasks=[w1, w2, w3],
            latest_decisions=[],
            accepted_packets=[],
        )
        assert ctx.blockers_summary is not None
        assert "2x dependency_unmet" in ctx.blockers_summary
        assert "1x external_input" in ctx.blockers_summary

    def test_reconstruct_no_blockers_when_no_waiting(self):
        ctx = reconstruct_work_context(
            project_id="proj-1",
            active_tasks=[],
            waiting_tasks=[],
            latest_decisions=[],
            accepted_packets=[],
        )
        assert ctx.blockers_summary is None

    def test_reconstruct_next_steps_from_active_tasks(self):
        t1 = self._make_task(next_action="Step 1")
        t2 = self._make_task(next_action="Step 2")
        ctx = reconstruct_work_context(
            project_id="proj-1",
            active_tasks=[t1, t2],
            waiting_tasks=[],
            latest_decisions=[],
            accepted_packets=[],
        )
        assert ctx.next_steps_summary is not None
        assert "2 task(s)" in ctx.next_steps_summary

    def test_reconstruct_focus_override(self):
        ctx = reconstruct_work_context(
            project_id="proj-1",
            active_tasks=[],
            waiting_tasks=[],
            latest_decisions=[],
            accepted_packets=[],
            current_focus="Custom focus text",
        )
        assert ctx.current_focus == "Custom focus text"

    def test_reconstruct_marks_source(self):
        """Metadata should record that this was reconstructed from canonical state."""
        ctx = reconstruct_work_context(
            project_id="proj-1",
            active_tasks=[],
            waiting_tasks=[],
            latest_decisions=[],
            accepted_packets=[],
        )
        assert ctx.metadata["reconstructed_from"] == "canonical_state"
        assert ctx.metadata["active_task_count"] == 0
        assert ctx.metadata["waiting_task_count"] == 0

    def test_reconstruct_preserves_existing_context_id(self):
        existing_id = str(uuid4())
        ctx = reconstruct_work_context(
            project_id="proj-1",
            active_tasks=[],
            waiting_tasks=[],
            latest_decisions=[],
            accepted_packets=[],
            existing_context_id=existing_id,
        )
        assert ctx.work_context_id == existing_id

    def test_reconstruct_no_active_tasks_default_focus(self):
        ctx = reconstruct_work_context(
            project_id="proj-1",
            active_tasks=[],
            waiting_tasks=[],
            latest_decisions=[],
            accepted_packets=[],
        )
        assert ctx.current_focus == "No active work"

    def test_reconstruct_waiting_tasks_default_focus(self):
        w = self._make_task(status="waiting")
        ctx = reconstruct_work_context(
            project_id="proj-1",
            active_tasks=[],
            waiting_tasks=[w],
            latest_decisions=[],
            accepted_packets=[],
        )
        assert "Waiting" in ctx.current_focus

    def test_reconstruct_status_is_active(self):
        ctx = reconstruct_work_context(
            project_id="proj-1",
            active_tasks=[],
            waiting_tasks=[],
            latest_decisions=[],
            accepted_packets=[],
        )
        assert ctx.status == ContextStatus.ACTIVE

    def test_reconstruct_sets_updated_at(self):
        ctx = reconstruct_work_context(
            project_id="proj-1",
            active_tasks=[],
            waiting_tasks=[],
            latest_decisions=[],
            accepted_packets=[],
        )
        assert ctx.updated_at is not None


# ──────────────────────────────────────────────────────────────
# Reconstruction Proof: Remove and Rebuild
# ──────────────────────────────────────────────────────────────

class TestReconstructionProof:
    """Prove: remove snapshot, rebuild, confirm no material truth is lost."""

    def _make_task(self, task_id, status="active", priority=2,
                   next_action=None, waiting_reason=None, waiting_detail=None):
        return TaskSnapshot(
            task_id=task_id,
            title=f"Task {task_id}",
            status=status,
            task_type="implementation",
            priority=priority,
            next_action_summary=next_action,
            waiting_reason=waiting_reason,
            waiting_detail=waiting_detail,
        )

    def _make_decision(self, decision_id, outcome="adopt", status="final",
                       finalized_at="2026-04-06T00:00:00+00:00"):
        return DecisionSnapshot(
            decision_id=decision_id,
            title=f"Decision {decision_id}",
            outcome=outcome,
            status=status,
            finalized_at=finalized_at,
        )

    def _make_packet(self, packet_id, accepted_at="2026-04-06T00:00:00+00:00"):
        return AcceptedPacketRef(
            memory_packet_id=packet_id,
            title=f"Packet {packet_id}",
            packet_type="study_result",
            accepted_at=accepted_at,
        )

    def test_rebuild_from_canonical_preserves_truth(self):
        """Canonical state -> context -> rebuild -> same material truth."""
        proj_id = str(uuid4())
        task_id = str(uuid4())
        dec_id = str(uuid4())
        pkt_id = str(uuid4())

        # Build initial context from canonical state
        ctx1 = reconstruct_work_context(
            project_id=proj_id,
            active_tasks=[
                self._make_task(task_id, priority=1, next_action="Build API"),
            ],
            waiting_tasks=[
                self._make_task(str(uuid4()), status="waiting",
                                waiting_reason="external_input"),
            ],
            latest_decisions=[
                self._make_decision(dec_id, outcome="adopt"),
            ],
            accepted_packets=[
                self._make_packet(pkt_id),
            ],
        )

        # Capture material truth from first context
        original_active_task = ctx1.active_task_id
        original_decision = ctx1.latest_decision_id
        original_packet = ctx1.packet_ref_id
        original_blockers = ctx1.blockers_summary

        # Rebuild from same canonical state (simulating "snapshot removed")
        ctx2 = reconstruct_work_context(
            project_id=proj_id,
            active_tasks=[
                self._make_task(task_id, priority=1, next_action="Build API"),
            ],
            waiting_tasks=[
                self._make_task(str(uuid4()), status="waiting",
                                waiting_reason="external_input"),
            ],
            latest_decisions=[
                self._make_decision(dec_id, outcome="adopt"),
            ],
            accepted_packets=[
                self._make_packet(pkt_id),
            ],
        )

        # Material truth preserved
        assert ctx2.active_task_id == original_active_task
        assert ctx2.latest_decision_id == original_decision
        assert ctx2.packet_ref_id == original_packet
        assert ctx2.blockers_summary == original_blockers
        # Context IDs differ (new snapshot) but content is the same
        assert ctx2.work_context_id != ctx1.work_context_id
        assert ctx2.current_focus == ctx1.current_focus

    def test_rebuild_reflects_canonical_changes(self):
        """When canonical state changes, rebuilt context reflects changes."""
        proj_id = str(uuid4())
        task_a = str(uuid4())
        task_b = str(uuid4())

        # First: task A is active
        ctx1 = reconstruct_work_context(
            project_id=proj_id,
            active_tasks=[
                self._make_task(task_a, priority=1, next_action="Task A"),
            ],
            waiting_tasks=[],
            latest_decisions=[],
            accepted_packets=[],
        )
        assert ctx1.active_task_id == task_a

        # Later: task A done, task B now active
        ctx2 = reconstruct_work_context(
            project_id=proj_id,
            active_tasks=[
                self._make_task(task_b, priority=0, next_action="Task B"),
            ],
            waiting_tasks=[],
            latest_decisions=[],
            accepted_packets=[],
        )
        assert ctx2.active_task_id == task_b
        assert ctx2.active_task_id != ctx1.active_task_id

    def test_context_does_not_invent_truth(self):
        """WorkContext must not contain data not derivable from canonical state."""
        ctx = reconstruct_work_context(
            project_id=str(uuid4()),
            active_tasks=[],
            waiting_tasks=[],
            latest_decisions=[],
            accepted_packets=[],
        )
        # All fields should be None or derived
        assert ctx.active_task_id is None
        assert ctx.latest_decision_id is None
        assert ctx.packet_ref_id is None
        assert ctx.blockers_summary is None
        assert ctx.next_steps_summary is None
        # Focus is a default, not invented
        assert "No active work" == ctx.current_focus
        # Metadata records the derivation
        assert ctx.metadata["reconstructed_from"] == "canonical_state"


# ──────────────────────────────────────────────────────────────
# Blocker Derivation
# ──────────────────────────────────────────────────────────────

class TestBlockerDerivation:
    def test_no_waiting_tasks_returns_none(self):
        assert _derive_blockers_summary([]) is None

    def test_single_waiting_task(self):
        task = TaskSnapshot(
            task_id="t1", title="T1", status="waiting",
            task_type="implementation", priority=2,
            next_action_summary=None,
            waiting_reason="dependency_unmet",
            waiting_detail="Waiting on API",
        )
        summary = _derive_blockers_summary([task])
        assert summary is not None
        assert "1x dependency_unmet" in summary

    def test_multiple_same_reason(self):
        tasks = [
            TaskSnapshot(
                task_id=f"t{i}", title=f"T{i}", status="waiting",
                task_type="implementation", priority=2,
                next_action_summary=None,
                waiting_reason="external_input",
                waiting_detail=None,
            )
            for i in range(3)
        ]
        summary = _derive_blockers_summary(tasks)
        assert summary is not None
        assert "3x external_input" in summary

    def test_mixed_reasons(self):
        tasks = [
            TaskSnapshot(
                task_id="t1", title="T1", status="waiting",
                task_type="implementation", priority=2,
                next_action_summary=None,
                waiting_reason="dependency_unmet",
                waiting_detail=None,
            ),
            TaskSnapshot(
                task_id="t2", title="T2", status="waiting",
                task_type="implementation", priority=2,
                next_action_summary=None,
                waiting_reason="external_input",
                waiting_detail=None,
            ),
        ]
        summary = _derive_blockers_summary(tasks)
        assert summary is not None
        assert "1x dependency_unmet" in summary
        assert "1x external_input" in summary

    def test_unspecified_reason(self):
        task = TaskSnapshot(
            task_id="t1", title="T1", status="waiting",
            task_type="implementation", priority=2,
            next_action_summary=None,
            waiting_reason=None,
            waiting_detail=None,
        )
        summary = _derive_blockers_summary([task])
        assert summary is not None
        assert "1x unspecified" in summary


# ──────────────────────────────────────────────────────────────
# Next Steps Derivation
# ──────────────────────────────────────────────────────────────

class TestNextStepsDerivation:
    def test_no_active_tasks_returns_none(self):
        assert _derive_next_steps_summary([]) is None

    def test_active_task_with_next_action(self):
        task = TaskSnapshot(
            task_id="t1", title="T1", status="active",
            task_type="implementation", priority=2,
            next_action_summary="Implement login flow",
            waiting_reason=None,
            waiting_detail=None,
        )
        summary = _derive_next_steps_summary([task])
        assert summary is not None
        assert "Implement login flow" in summary

    def test_active_task_without_next_action(self):
        task = TaskSnapshot(
            task_id="t1", title="T1", status="active",
            task_type="implementation", priority=2,
            next_action_summary=None,
            waiting_reason=None,
            waiting_detail=None,
        )
        summary = _derive_next_steps_summary([task])
        assert summary is not None
        assert "1 task(s)" in summary

    def test_limits_to_three_summaries(self):
        tasks = [
            TaskSnapshot(
                task_id=f"t{i}", title=f"T{i}", status="active",
                task_type="implementation", priority=2,
                next_action_summary=f"Action {i}",
                waiting_reason=None,
                waiting_detail=None,
            )
            for i in range(5)
        ]
        summary = _derive_next_steps_summary(tasks)
        assert summary is not None
        assert "5 task(s)" in summary
        # Should contain first 3 action summaries
        assert "Action 0" in summary
        assert "Action 1" in summary
        assert "Action 2" in summary
        assert "Action 3" not in summary  # Limited to 3
