"""
Tests for IKE Runtime v0 events and leases.

Validates:
- Append-only event behavior (immutability)
- Event type correctness
- Lease claim / heartbeat / expiry semantics
- Task-type recovery destination correctness
- Recovery must NOT finalize work as done
- Recovery emits explicit events
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from runtime.state_machine import TaskStatus, OwnerKind, WaitingReason
from runtime.events import (
    EventType,
    TaskEvent,
    make_event,
    make_state_transition_event,
    make_lease_claimed_event,
    make_lease_expired_event,
    make_recovery_event,
    EventSequence,
)
from runtime.leases import (
    TASK_TYPE_RECOVERY,
    get_recovery_status,
    get_all_task_types_with_recovery,
    LeaseRecord,
    LeaseClaimResult,
    LeaseExpiryResult,
    claim_lease,
    heartbeat_lease,
    release_lease,
    expire_lease,
    recover_stale_active_task,
    build_lease_heartbeat_update,
    build_lease_release_update,
    build_lease_expired_update,
)


# ──────────────────────────────────────────────────────────────
# Event Immutability (Append-Only Discipline)
# ──────────────────────────────────────────────────────────────

class TestEventImmutability:
    """Events must be immutable after creation – append-only guarantee."""

    def test_event_is_frozen(self):
        """TaskEvent must be a frozen dataclass."""
        event = make_event(
            project_id=str(uuid4()),
            task_id=str(uuid4()),
            event_type=EventType.STATE_TRANSITION,
            triggered_by_kind=OwnerKind.CONTROLLER,
            triggered_by_id="ctrl-001",
            reason="Test",
            from_status=TaskStatus.INBOX,
            to_status=TaskStatus.READY,
        )
        with pytest.raises(AttributeError):  # frozen=True
            event.event_id = "tampered"

    def test_event_has_unique_id(self):
        e1 = make_event(
            project_id="p", task_id="t",
            event_type=EventType.STATE_TRANSITION,
            triggered_by_kind=OwnerKind.CONTROLLER,
            triggered_by_id="c",
            reason="r",
        )
        e2 = make_event(
            project_id="p", task_id="t",
            event_type=EventType.STATE_TRANSITION,
            triggered_by_kind=OwnerKind.CONTROLLER,
            triggered_by_id="c",
            reason="r",
        )
        assert e1.event_id != e2.event_id

    def test_event_created_at_is_set(self):
        event = make_event(
            project_id="p", task_id="t",
            event_type=EventType.STATE_TRANSITION,
            triggered_by_kind=OwnerKind.CONTROLLER,
            triggered_by_id="c",
            reason="r",
        )
        assert event.created_at is not None
        # Should be valid ISO format
        datetime.fromisoformat(event.created_at)

    def test_event_to_dict_matches_schema(self):
        event = make_event(
            project_id=str(uuid4()),
            task_id=str(uuid4()),
            event_type=EventType.STATE_TRANSITION,
            triggered_by_kind=OwnerKind.CONTROLLER,
            triggered_by_id="ctrl-001",
            reason="Triaged",
            from_status=TaskStatus.INBOX,
            to_status=TaskStatus.READY,
            payload={"source": "triage"},
        )
        d = event.to_dict()
        assert d["event_id"] == event.event_id
        assert d["project_id"] == event.project_id
        assert d["task_id"] == event.task_id
        assert d["event_type"] == event.event_type
        assert d["from_status"] == "inbox"
        assert d["to_status"] == "ready"
        assert d["triggered_by_kind"] == "controller"
        assert d["triggered_by_id"] == "ctrl-001"
        assert d["reason"] == "Triaged"
        assert d["payload"] == {"source": "triage"}
        assert d["created_at"] is not None


# ──────────────────────────────────────────────────────────────
# Event Types
# ──────────────────────────────────────────────────────────────

class TestEventTypes:
    """Verify all canonical event types exist."""

    def test_state_transition_type(self):
        assert EventType.STATE_TRANSITION == "state_transition"

    def test_lease_event_types(self):
        assert EventType.LEASE_CLAIMED == "lease_claimed"
        assert EventType.LEASE_HEARTBEAT == "lease_heartbeat"
        assert EventType.LEASE_RELEASED == "lease_released"
        assert EventType.LEASE_EXPIRED == "lease_expired"

    def test_recovery_event_types(self):
        assert EventType.RECOVERY_LEASE_EXPIRY == "recovery_lease_expiry"
        assert EventType.RECOVERY_STALE_ACTIVE == "recovery_stale_active"

    def test_control_action_type(self):
        assert EventType.CONTROL_ACTION == "control_action"

    def test_lifecycle_event_types(self):
        assert EventType.TASK_CREATED == "task_created"
        assert EventType.CHECKPOINT_SAVED == "checkpoint_saved"


# ──────────────────────────────────────────────────────────────
# Event Builders
# ──────────────────────────────────────────────────────────────

class TestEventBuilders:
    def test_make_state_transition_event(self):
        event = make_state_transition_event(
            project_id="proj-1",
            task_id="task-1",
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.REVIEW_PENDING,
            triggered_by_kind=OwnerKind.DELEGATE,
            triggered_by_id="del-001",
            reason="Work complete",
        )
        assert event.event_type == EventType.STATE_TRANSITION
        assert event.from_status == "active"
        assert event.to_status == "review_pending"
        assert event.triggered_by_kind == "delegate"

    def test_make_lease_claimed_event(self):
        event = make_lease_claimed_event(
            project_id="proj-1",
            task_id="task-1",
            lease_id="lease-1",
            owner_kind=OwnerKind.DELEGATE,
            owner_id="del-001",
        )
        assert event.event_type == EventType.LEASE_CLAIMED
        assert event.payload["lease_id"] == "lease-1"

    def test_make_lease_expired_event(self):
        event = make_lease_expired_event(
            project_id="proj-1",
            task_id="task-1",
            lease_id="lease-1",
            expired_owner_kind="delegate",
            expired_owner_id="del-001",
        )
        assert event.event_type == EventType.LEASE_EXPIRED
        assert event.triggered_by_kind == "runtime"  # runtime detects expiry
        assert event.payload["lease_id"] == "lease-1"

    def test_make_recovery_event(self):
        event = make_recovery_event(
            project_id="proj-1",
            task_id="task-1",
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.WAITING,
            task_type="implementation",
            reason="Lease expired",
            lease_id="lease-1",
        )
        assert event.event_type == EventType.RECOVERY_LEASE_EXPIRY
        assert event.payload["recovery"] is True
        assert event.payload["task_type"] == "implementation"
        assert event.payload["lease_id"] == "lease-1"

    def test_recovery_event_does_not_set_done(self):
        """Recovery events must never produce 'done' as to_status."""
        for task_type in TASK_TYPE_RECOVERY:
            status = TASK_TYPE_RECOVERY[task_type]
            assert status != TaskStatus.DONE, \
                f"Recovery for {task_type} must not go to done"


# ──────────────────────────────────────────────────────────────
# Event Sequence
# ──────────────────────────────────────────────────────────────

class TestEventSequence:
    """Test append-only event sequence behavior."""

    def test_append_events(self):
        seq = EventSequence()
        e1 = make_event(
            project_id="p", task_id="t",
            event_type=EventType.STATE_TRANSITION,
            triggered_by_kind=OwnerKind.CONTROLLER,
            triggered_by_id="c",
            reason="r",
        )
        e2 = make_event(
            project_id="p", task_id="t",
            event_type=EventType.LEASE_CLAIMED,
            triggered_by_kind=OwnerKind.DELEGATE,
            triggered_by_id="d",
            reason="claimed",
        )
        seq.append(e1)
        seq.append(e2)
        assert seq.count == 2
        assert seq.events[0].event_id == e1.event_id
        assert seq.events[1].event_id == e2.event_id

    def test_to_dicts(self):
        seq = EventSequence()
        seq.append(make_event(
            project_id="p", task_id="t",
            event_type=EventType.STATE_TRANSITION,
            triggered_by_kind=OwnerKind.CONTROLLER,
            triggered_by_id="c",
            reason="r",
        ))
        dicts = seq.to_dicts()
        assert len(dicts) == 1
        assert dicts[0]["event_type"] == "state_transition"

    def test_events_cannot_be_removed(self):
        """EventSequence has no remove/pop/clear methods."""
        seq = EventSequence()
        seq.append(make_event(
            project_id="p", task_id="t",
            event_type=EventType.STATE_TRANSITION,
            triggered_by_kind=OwnerKind.CONTROLLER,
            triggered_by_id="c",
            reason="r",
        ))
        # The underlying list is accessible but the API doesn't expose mutation
        # This test documents the design intent
        assert seq.count == 1
        # If someone mutates seq.events directly, that's their problem,
        # but the public API doesn't support it
        assert not hasattr(seq, "remove")
        assert not hasattr(seq, "pop")
        assert not hasattr(seq, "clear")


# ──────────────────────────────────────────────────────────────
# Task-Type Recovery Policy
# ──────────────────────────────────────────────────────────────

class TestTaskTypeRecoveryPolicy:
    """Verify task-type recovery destinations per the design spec."""

    def test_implementation_recovers_to_waiting(self):
        assert TASK_TYPE_RECOVERY["implementation"] == TaskStatus.WAITING

    def test_review_recovers_to_review_pending(self):
        assert TASK_TYPE_RECOVERY["review"] == TaskStatus.REVIEW_PENDING

    def test_study_recovers_to_failed(self):
        assert TASK_TYPE_RECOVERY["study"] == TaskStatus.FAILED

    def test_daemon_recovers_to_ready(self):
        assert TASK_TYPE_RECOVERY["daemon"] == TaskStatus.READY

    def test_workflow_recovers_to_waiting(self):
        assert TASK_TYPE_RECOVERY["workflow"] == TaskStatus.WAITING

    def test_maintenance_recovers_to_ready(self):
        assert TASK_TYPE_RECOVERY["maintenance"] == TaskStatus.READY

    def test_no_recovery_to_done(self):
        """Critical: no task type recovers to done on lease expiry."""
        for task_type, status in TASK_TYPE_RECOVERY.items():
            assert status != TaskStatus.DONE, \
                f"{task_type} must not recover to done"

    def test_no_recovery_to_review_pending_except_review(self):
        """Only review tasks recover to review_pending."""
        for task_type, status in TASK_TYPE_RECOVERY.items():
            if task_type != "review":
                assert status != TaskStatus.REVIEW_PENDING, \
                    f"{task_type} must not recover to review_pending"

    def test_get_recovery_status_known_type(self):
        assert get_recovery_status("implementation") == TaskStatus.WAITING

    def test_get_recovery_status_unknown_type(self):
        assert get_recovery_status("unknown_type") is None

    def test_get_all_task_types_with_recovery(self):
        types = get_all_task_types_with_recovery()
        expected = {"implementation", "review", "study", "daemon", "workflow", "maintenance"}
        assert types == expected


# ──────────────────────────────────────────────────────────────
# Lease Claim
# ──────────────────────────────────────────────────────────────

class TestLeaseClaim:
    def test_claim_lease_success(self):
        result = claim_lease(
            task_id="task-1",
            project_id="proj-1",
            owner_kind=OwnerKind.DELEGATE,
            owner_id="del-001",
            ttl_seconds=1800,
        )
        assert result.success is True
        assert result.lease is not None
        assert result.event is not None

    def test_claimed_lease_is_active(self):
        result = claim_lease(
            task_id="task-1",
            project_id="proj-1",
            owner_kind=OwnerKind.DELEGATE,
            owner_id="del-001",
        )
        assert result.lease.lease_status == "active"

    def test_claimed_lease_has_heartbeat(self):
        result = claim_lease(
            task_id="task-1",
            project_id="proj-1",
            owner_kind=OwnerKind.DELEGATE,
            owner_id="del-001",
        )
        assert result.lease.heartbeat_at is not None

    def test_claimed_lease_has_expires_at(self):
        result = claim_lease(
            task_id="task-1",
            project_id="proj-1",
            owner_kind=OwnerKind.DELEGATE,
            owner_id="del-001",
            ttl_seconds=3600,
        )
        expires = datetime.fromisoformat(result.lease.expires_at)
        created = datetime.fromisoformat(result.lease.created_at)
        delta = expires - created
        assert delta.total_seconds() == pytest.approx(3600, abs=1)

    def test_claim_produces_event(self):
        result = claim_lease(
            task_id="task-1",
            project_id="proj-1",
            owner_kind=OwnerKind.DELEGATE,
            owner_id="del-001",
        )
        assert result.event.event_type == EventType.LEASE_CLAIMED
        assert result.event.payload["lease_id"] == result.lease.lease_id

    def test_lease_record_to_dict(self):
        result = claim_lease(
            task_id="task-1",
            project_id="proj-1",
            owner_kind=OwnerKind.DELEGATE,
            owner_id="del-001",
        )
        d = result.lease.to_dict()
        assert d["lease_id"] == result.lease.lease_id
        assert d["lease_status"] == "active"
        assert d["owner_kind"] == "delegate"


# ──────────────────────────────────────────────────────────────
# Lease Heartbeat
# ──────────────────────────────────────────────────────────────

class TestLeaseHeartbeat:
    def test_heartbeat_produces_event(self):
        event = heartbeat_lease(
            lease_id="lease-1",
            task_id="task-1",
            project_id="proj-1",
            owner_kind=OwnerKind.DELEGATE,
            owner_id="del-001",
        )
        assert event.event_type == EventType.LEASE_HEARTBEAT
        assert event.payload["lease_id"] == "lease-1"

    def test_heartbeat_with_custom_time(self):
        now = datetime(2026, 4, 6, 12, 0, 0, tzinfo=timezone.utc)
        event = heartbeat_lease(
            lease_id="lease-1",
            task_id="task-1",
            project_id="proj-1",
            owner_kind=OwnerKind.DELEGATE,
            owner_id="del-001",
            heartbeat_at=now,
        )
        assert event.payload["heartbeat_at"] == now.isoformat()


# ──────────────────────────────────────────────────────────────
# Lease Release
# ──────────────────────────────────────────────────────────────

class TestLeaseRelease:
    def test_release_produces_event(self):
        event = release_lease(
            lease_id="lease-1",
            task_id="task-1",
            project_id="proj-1",
            owner_kind=OwnerKind.DELEGATE,
            owner_id="del-001",
        )
        assert event.event_type == EventType.LEASE_RELEASED
        assert event.payload["lease_id"] == "lease-1"


# ──────────────────────────────────────────────────────────────
# Lease Expiry and Recovery
# ──────────────────────────────────────────────────────────────

class TestLeaseExpiry:
    """The core recovery tests."""

    def test_implementation_expiry_recovers_to_waiting(self):
        result = expire_lease(
            lease_id="lease-1",
            task_id="task-1",
            project_id="proj-1",
            expired_owner_kind="delegate",
            expired_owner_id="del-001",
            task_type="implementation",
        )
        assert result.success is True
        assert result.recovery_status == TaskStatus.WAITING
        assert result.task_update["status"] == "waiting"

    def test_review_expiry_recovers_to_review_pending(self):
        result = expire_lease(
            lease_id="lease-1",
            task_id="task-1",
            project_id="proj-1",
            expired_owner_kind="delegate",
            expired_owner_id="del-001",
            task_type="review",
        )
        assert result.success is True
        assert result.recovery_status == TaskStatus.REVIEW_PENDING

    def test_study_expiry_recovers_to_failed(self):
        result = expire_lease(
            lease_id="lease-1",
            task_id="task-1",
            project_id="proj-1",
            expired_owner_kind="delegate",
            expired_owner_id="del-001",
            task_type="study",
        )
        assert result.success is True
        assert result.recovery_status == TaskStatus.FAILED

    def test_daemon_expiry_recovers_to_ready(self):
        result = expire_lease(
            lease_id="lease-1",
            task_id="task-1",
            project_id="proj-1",
            expired_owner_kind="runtime",
            expired_owner_id="runtime",
            task_type="daemon",
        )
        assert result.success is True
        assert result.recovery_status == TaskStatus.READY

    def test_workflow_expiry_recovers_to_waiting(self):
        result = expire_lease(
            lease_id="lease-1",
            task_id="task-1",
            project_id="proj-1",
            expired_owner_kind="delegate",
            expired_owner_id="del-001",
            task_type="workflow",
        )
        assert result.success is True
        assert result.recovery_status == TaskStatus.WAITING

    def test_maintenance_expiry_recovers_to_ready(self):
        result = expire_lease(
            lease_id="lease-1",
            task_id="task-1",
            project_id="proj-1",
            expired_owner_kind="runtime",
            expired_owner_id="runtime",
            task_type="maintenance",
        )
        assert result.success is True
        assert result.recovery_status == TaskStatus.READY

    def test_no_task_recovers_to_done(self):
        """Critical: lease expiry must NEVER promote work to done."""
        for task_type in TASK_TYPE_RECOVERY:
            result = expire_lease(
                lease_id="lease-1",
                task_id="task-1",
                project_id="proj-1",
                expired_owner_kind="delegate",
                expired_owner_id="del-001",
                task_type=task_type,
            )
            assert result.recovery_status != TaskStatus.DONE, \
                f"{task_type} must not recover to done"

    def test_expiry_produces_two_events(self):
        """Expiry must produce both expired event and recovery event."""
        result = expire_lease(
            lease_id="lease-1",
            task_id="task-1",
            project_id="proj-1",
            expired_owner_kind="delegate",
            expired_owner_id="del-001",
            task_type="implementation",
        )
        assert result.expired_event is not None
        assert result.recovery_event is not None
        assert result.expired_event.event_type == EventType.LEASE_EXPIRED
        assert result.recovery_event.event_type == EventType.RECOVERY_LEASE_EXPIRY

    def test_recovery_event_is_auditable(self):
        """Recovery event must capture task_type and both statuses."""
        result = expire_lease(
            lease_id="lease-1",
            task_id="task-1",
            project_id="proj-1",
            expired_owner_kind="delegate",
            expired_owner_id="del-001",
            task_type="implementation",
        )
        payload = result.recovery_event.payload
        assert payload["recovery"] is True
        assert payload["task_type"] == "implementation"
        assert payload["from_status"] == "active"
        assert payload["to_status"] == "waiting"
        assert payload["lease_id"] == "lease-1"

    def test_recovery_clears_lease_pointer(self):
        """Task update must clear current_lease_id after expiry."""
        result = expire_lease(
            lease_id="lease-1",
            task_id="task-1",
            project_id="proj-1",
            expired_owner_kind="delegate",
            expired_owner_id="del-001",
            task_type="implementation",
        )
        assert result.task_update["current_lease_id"] is None

    def test_waiting_recovery_sets_waiting_reason(self):
        """Tasks recovering to WAITING must have waiting_reason set."""
        result = expire_lease(
            lease_id="lease-1",
            task_id="task-1",
            project_id="proj-1",
            expired_owner_kind="delegate",
            expired_owner_id="del-001",
            task_type="implementation",
        )
        assert result.task_update["waiting_reason"] == "delegate_result"
        assert "waiting_detail" in result.task_update

    def test_non_waiting_recovery_does_not_set_waiting_reason(self):
        """Tasks not recovering to WAITING should not set waiting_reason."""
        result = expire_lease(
            lease_id="lease-1",
            task_id="task-1",
            project_id="proj-1",
            expired_owner_kind="runtime",
            expired_owner_id="runtime",
            task_type="daemon",
        )
        assert "waiting_reason" not in result.task_update

    def test_unknown_task_type_fails(self):
        """Unknown task types must fail with an error."""
        result = expire_lease(
            lease_id="lease-1",
            task_id="task-1",
            project_id="proj-1",
            expired_owner_kind="delegate",
            expired_owner_id="del-001",
            task_type="nonexistent",
        )
        assert result.success is False
        assert result.error is not None
        assert "nonexistent" in result.error

    def test_recovery_event_triggered_by_runtime(self):
        """Recovery events must be triggered by runtime, not the expired owner."""
        result = expire_lease(
            lease_id="lease-1",
            task_id="task-1",
            project_id="proj-1",
            expired_owner_kind="delegate",
            expired_owner_id="del-001",
            task_type="implementation",
        )
        assert result.recovery_event.triggered_by_kind == "runtime"
        assert result.recovery_event.triggered_by_id == "runtime"


# ──────────────────────────────────────────────────────────────
# Stale Active Task Recovery
# ──────────────────────────────────────────────────────────────

class TestStaleActiveRecovery:
    """Recover tasks stuck in active with no valid lease."""

    def test_stale_active_implementation_recovers_to_waiting(self):
        result = recover_stale_active_task(
            task_id="task-1",
            project_id="proj-1",
            task_type="implementation",
            reason="No active lease found",
        )
        assert result.success is True
        assert result.recovery_status == TaskStatus.WAITING

    def test_stale_active_study_recovers_to_failed(self):
        result = recover_stale_active_task(
            task_id="task-1",
            project_id="proj-1",
            task_type="study",
            reason="No active lease found",
        )
        assert result.success is True
        assert result.recovery_status == TaskStatus.FAILED

    def test_stale_active_recovery_emits_event(self):
        result = recover_stale_active_task(
            task_id="task-1",
            project_id="proj-1",
            task_type="daemon",
        )
        assert result.recovery_event is not None
        assert result.recovery_event.event_type == EventType.RECOVERY_STALE_ACTIVE

    def test_stale_active_unknown_type_fails(self):
        result = recover_stale_active_task(
            task_id="task-1",
            project_id="proj-1",
            task_type="unknown_type",
        )
        assert result.success is False
        assert result.error is not None


# ──────────────────────────────────────────────────────────────
# Lease Update Helpers
# ──────────────────────────────────────────────────────────────

class TestLeaseUpdateHelpers:
    def test_heartbeat_update(self):
        update = build_lease_heartbeat_update(extends_seconds=7200)
        assert "heartbeat_at" in update
        assert "expires_at" in update

    def test_release_update(self):
        update = build_lease_release_update()
        assert update["lease_status"] == "released"

    def test_expired_update(self):
        update = build_lease_expired_update()
        assert update["lease_status"] == "expired"
