"""
IKE Runtime v0 – Lifecycle Proof Test

Proves the complete task lifecycle path:
  inbox -> ready -> active -> review_pending -> done

This is a truth-constrained proof:
- State changes and event history must align
- Review boundary must stay explicit (delegate cannot move review_pending -> done)
- Only controller can accept review_pending work to done

This test validates the narrowest possible lifecycle proof using the
existing runtime kernel without adding new first-class objects.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from runtime.state_machine import (
    TaskStatus,
    OwnerKind,
    PermissionLevel,
    get_transition_permission,
    validate_transition,
    is_valid_transition,
    describe_transition,
    TransitionError,
    InvalidTransitionError,
    GuardrailViolationError,
    ClaimRequiredError,
    ClaimContext,
    ClaimType,
)
from runtime.transitions import (
    TransitionRequest,
    TransitionResult,
    execute_transition,
    build_event_record,
    build_task_update,
)
from runtime.events import (
    EventType,
    TaskEvent,
    make_state_transition_event,
    EventSequence,
)
from runtime.leases import (
    claim_lease,
    TASK_TYPE_RECOVERY,
)


# ──────────────────────────────────────────────────────────────
# Lifecycle Path Definition
# ──────────────────────────────────────────────────────────────

# The canonical lifecycle path to prove
LIFECYCLE_PATH = [
    (TaskStatus.INBOX, TaskStatus.READY),
    (TaskStatus.READY, TaskStatus.ACTIVE),
    (TaskStatus.ACTIVE, TaskStatus.REVIEW_PENDING),
    (TaskStatus.REVIEW_PENDING, TaskStatus.DONE),
]

# Expected actors for each transition in the lifecycle
LIFECYCLE_ACTORS = [
    OwnerKind.CONTROLLER,  # inbox -> ready (triage)
    OwnerKind.DELEGATE,    # ready -> active (claim & start)
    OwnerKind.DELEGATE,    # active -> review_pending (submit for review)
    OwnerKind.CONTROLLER,  # review_pending -> done (accept)
]


# ──────────────────────────────────────────────────────────────
# Lifecycle Proof Test
# ──────────────────────────────────────────────────────────────

class TestLifecycleProof:
    """Prove the complete v0 task lifecycle with aligned state and events."""

    def test_lifecycle_path_is_valid(self):
        """Every transition in the lifecycle path must be structurally valid."""
        for from_status, to_status in LIFECYCLE_PATH:
            assert is_valid_transition(from_status, to_status), \
                f"Invalid transition: {from_status.value} -> {to_status.value}"

    def test_lifecycle_actors_are_permitted(self):
        """Each actor must be permitted for their lifecycle transition."""
        for (from_status, to_status), actor in zip(LIFECYCLE_PATH, LIFECYCLE_ACTORS):
            level = get_transition_permission(from_status, to_status, actor)
            assert level in (PermissionLevel.ALLOWED, PermissionLevel.CLAIM_REQUIRED), \
                f"{actor.value} not permitted for {from_status.value} -> {to_status.value}"

    def test_full_lifecycle_execution(self):
        """Execute the complete lifecycle path with proper actors."""
        task_id = str(uuid4())
        project_id = str(uuid4())
        event_log = EventSequence()

        # Step 1: inbox -> ready (controller triage)
        req1 = TransitionRequest(
            task_id=task_id,
            project_id=project_id,
            from_status=TaskStatus.INBOX,
            to_status=TaskStatus.READY,
            role=OwnerKind.CONTROLLER,
            role_id="ctrl-001",
            reason="Triage complete; task is executable",
        )
        result1 = execute_transition(req1)
        assert result1.success is True, f"Step 1 failed: {result1.error}"
        
        event1 = build_event_record(
            result1,
            project_id=project_id,
            triggered_by_kind=OwnerKind.CONTROLLER,
            triggered_by_id="ctrl-001",
        )
        event_log.append(TaskEvent(**event1))

        # Step 2: ready -> active (delegate claim with structured claim context)
        claim_ctx = ClaimContext(
            claim_type=ClaimType.ACTIVE_LEASE,
            claim_ref="lease-001",
            delegate_id="del-001",
            task_id=task_id,
        )
        req2 = TransitionRequest(
            task_id=task_id,
            project_id=project_id,
            from_status=TaskStatus.READY,
            to_status=TaskStatus.ACTIVE,
            role=OwnerKind.DELEGATE,
            role_id="del-001",
            reason="Work started",
        )
        # Validate with structured claim context
        validate_transition(
            TaskStatus.READY,
            TaskStatus.ACTIVE,
            OwnerKind.DELEGATE,
            claim_context=claim_ctx,
        )
        result2 = execute_transition(req2)
        # Note: execute_transition doesn't pass claim_context, so we validated separately
        # For the proof, we use allow_claim=True to simulate verified claim
        req2_allow = TransitionRequest(
            task_id=task_id,
            project_id=project_id,
            from_status=TaskStatus.READY,
            to_status=TaskStatus.ACTIVE,
            role=OwnerKind.DELEGATE,
            role_id="del-001",
            reason="Work started",
            allow_claim=True,
        )
        result2 = execute_transition(req2_allow)
        assert result2.success is True, f"Step 2 failed: {result2.error}"

        event2 = build_event_record(
            result2,
            project_id=project_id,
            triggered_by_kind=OwnerKind.DELEGATE,
            triggered_by_id="del-001",
        )
        event_log.append(TaskEvent(**event2))

        # Step 3: active -> review_pending (delegate submits for review)
        req3 = TransitionRequest(
            task_id=task_id,
            project_id=project_id,
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.REVIEW_PENDING,
            role=OwnerKind.DELEGATE,
            role_id="del-001",
            reason="Work complete; awaiting review",
        )
        result3 = execute_transition(req3)
        assert result3.success is True, f"Step 3 failed: {result3.error}"

        event3 = build_event_record(
            result3,
            project_id=project_id,
            triggered_by_kind=OwnerKind.DELEGATE,
            triggered_by_id="del-001",
        )
        event_log.append(TaskEvent(**event3))

        # Step 4: review_pending -> done (controller accepts)
        req4 = TransitionRequest(
            task_id=task_id,
            project_id=project_id,
            from_status=TaskStatus.REVIEW_PENDING,
            to_status=TaskStatus.DONE,
            role=OwnerKind.CONTROLLER,
            role_id="ctrl-001",
            reason="Review passed; task accepted",
        )
        result4 = execute_transition(req4)
        assert result4.success is True, f"Step 4 failed: {result4.error}"

        event4 = build_event_record(
            result4,
            project_id=project_id,
            triggered_by_kind=OwnerKind.CONTROLLER,
            triggered_by_id="ctrl-001",
            extra_payload={"review_passed": True},
        )
        event_log.append(TaskEvent(**event4))

        # Verify event log has all 4 transitions
        assert event_log.count == 4
        assert event_log.events[0].from_status == "inbox"
        assert event_log.events[0].to_status == "ready"
        assert event_log.events[1].from_status == "ready"
        assert event_log.events[1].to_status == "active"
        assert event_log.events[2].from_status == "active"
        assert event_log.events[2].to_status == "review_pending"
        assert event_log.events[3].from_status == "review_pending"
        assert event_log.events[3].to_status == "done"

    def test_review_boundary_is_enforced(self):
        """Delegate cannot bypass review by moving review_pending -> done."""
        # This is the critical guardrail
        level = get_transition_permission(
            TaskStatus.REVIEW_PENDING, TaskStatus.DONE, OwnerKind.DELEGATE
        )
        assert level == PermissionLevel.DENIED

        # validate_transition must raise GuardrailViolationError
        with pytest.raises(GuardrailViolationError):
            validate_transition(
                TaskStatus.REVIEW_PENDING,
                TaskStatus.DONE,
                OwnerKind.DELEGATE,
            )

        # execute_transition must fail
        req = TransitionRequest(
            task_id=str(uuid4()),
            project_id=str(uuid4()),
            from_status=TaskStatus.REVIEW_PENDING,
            to_status=TaskStatus.DONE,
            role=OwnerKind.DELEGATE,
            role_id="del-001",
        )
        result = execute_transition(req)
        assert result.success is False
        assert "Guardrail violation" in result.error

    def test_controller_can_accept_review(self):
        """Only controller can move review_pending -> done."""
        level = get_transition_permission(
            TaskStatus.REVIEW_PENDING, TaskStatus.DONE, OwnerKind.CONTROLLER
        )
        assert level == PermissionLevel.ALLOWED

        # validate_transition succeeds
        validate_transition(
            TaskStatus.REVIEW_PENDING,
            TaskStatus.DONE,
            OwnerKind.CONTROLLER,
        )

        # execute_transition succeeds
        req = TransitionRequest(
            task_id=str(uuid4()),
            project_id=str(uuid4()),
            from_status=TaskStatus.REVIEW_PENDING,
            to_status=TaskStatus.DONE,
            role=OwnerKind.CONTROLLER,
            role_id="ctrl-001",
            reason="Review passed",
        )
        result = execute_transition(req)
        assert result.success is True

    def test_delegate_claim_requires_proof(self):
        """Delegate ready -> active requires explicit claim proof."""
        # Without claim, must fail
        with pytest.raises(ClaimRequiredError):
            validate_transition(
                TaskStatus.READY,
                TaskStatus.ACTIVE,
                OwnerKind.DELEGATE,
            )

        # With structured claim context, succeeds
        claim_ctx = ClaimContext(
            claim_type=ClaimType.ACTIVE_LEASE,
            claim_ref="lease-123",
            delegate_id="del-001",
            task_id="task-123",
        )
        validate_transition(
            TaskStatus.READY,
            TaskStatus.ACTIVE,
            OwnerKind.DELEGATE,
            claim_context=claim_ctx,
        )

        # With explicit assignment claim, also succeeds
        claim_ctx2 = ClaimContext(
            claim_type=ClaimType.EXPLICIT_ASSIGNMENT,
            claim_ref="assignment-456",
            delegate_id="del-001",
            task_id="task-123",
        )
        validate_transition(
            TaskStatus.READY,
            TaskStatus.ACTIVE,
            OwnerKind.DELEGATE,
            claim_context=claim_ctx2,
        )

    def test_state_event_alignment(self):
        """State changes must produce aligned event records."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        # Single transition
        req = TransitionRequest(
            task_id=task_id,
            project_id=project_id,
            from_status=TaskStatus.INBOX,
            to_status=TaskStatus.READY,
            role=OwnerKind.CONTROLLER,
            role_id="ctrl-001",
        )
        result = execute_transition(req)
        assert result.success is True

        event = build_event_record(
            result,
            project_id=project_id,
            triggered_by_kind=OwnerKind.CONTROLLER,
            triggered_by_id="ctrl-001",
        )

        # Event must match the transition
        assert event["from_status"] == "inbox"
        assert event["to_status"] == "ready"
        assert event["task_id"] == task_id
        assert event["event_type"] == "state_transition"

    def test_lifecycle_cannot_skip_review_pending(self):
        """active -> done is NOT a valid transition (must go through review)."""
        assert is_valid_transition(TaskStatus.ACTIVE, TaskStatus.DONE) is False

        with pytest.raises(InvalidTransitionError):
            validate_transition(
                TaskStatus.ACTIVE,
                TaskStatus.DONE,
                OwnerKind.CONTROLLER,
            )

        req = TransitionRequest(
            task_id=str(uuid4()),
            project_id=str(uuid4()),
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.DONE,
            role=OwnerKind.CONTROLLER,
            role_id="ctrl-001",
        )
        result = execute_transition(req)
        assert result.success is False
        assert "Invalid transition" in result.error

    def test_lifecycle_descriptions_are_meaningful(self):
        """Each lifecycle transition has a meaningful description."""
        descriptions = [
            describe_transition(TaskStatus.INBOX, TaskStatus.READY),
            describe_transition(TaskStatus.READY, TaskStatus.ACTIVE),
            describe_transition(TaskStatus.ACTIVE, TaskStatus.REVIEW_PENDING),
            describe_transition(TaskStatus.REVIEW_PENDING, TaskStatus.DONE),
        ]
        for desc in descriptions:
            assert len(desc) > 10  # Non-trivial description
            assert "transition" not in desc.lower() or len(desc) > 30


# ──────────────────────────────────────────────────────────────
# Ordered Task-Event History Proof
# ──────────────────────────────────────────────────────────────

class TestOrderedEventHistory:
    """Prove that event history is ordered and immutable."""

    def test_events_are_appended_in_order(self):
        """Events must be appended in lifecycle order."""
        seq = EventSequence()
        task_id = str(uuid4())
        project_id = str(uuid4())

        # Simulate lifecycle events in order
        for i, ((from_s, to_s), actor) in enumerate(zip(LIFECYCLE_PATH, LIFECYCLE_ACTORS)):
            if i == 1 and actor == OwnerKind.DELEGATE:
                # Skip claim validation for event ordering test
                pass
            
            event = make_state_transition_event(
                project_id=project_id,
                task_id=task_id,
                from_status=from_s,
                to_status=to_s,
                triggered_by_kind=actor,
                triggered_by_id=f"{actor.value}-001",
                reason=f"Lifecycle step {i+1}",
            )
            seq.append(event)

        # Verify order matches lifecycle
        assert seq.count == 4
        assert seq.events[0].from_status == "inbox"
        assert seq.events[0].to_status == "ready"
        assert seq.events[1].from_status == "ready"
        assert seq.events[1].to_status == "active"
        assert seq.events[2].from_status == "active"
        assert seq.events[2].to_status == "review_pending"
        assert seq.events[3].from_status == "review_pending"
        assert seq.events[3].to_status == "done"

    def test_events_are_immutable(self):
        """Once appended, events cannot be modified."""
        seq = EventSequence()
        event = make_state_transition_event(
            project_id="p",
            task_id="t",
            from_status=TaskStatus.INBOX,
            to_status=TaskStatus.READY,
            triggered_by_kind=OwnerKind.CONTROLLER,
            triggered_by_id="ctrl-001",
            reason="Triage",
        )
        seq.append(event)
        
        # Event is frozen
        with pytest.raises(AttributeError):
            seq.events[0].task_id = "tampered"

    def test_event_sequence_produces_persistable_dicts(self):
        """EventSequence.to_dicts() produces valid persistence dicts."""
        seq = EventSequence()
        for from_s, to_s in LIFECYCLE_PATH[:2]:  # Just first two for brevity
            event = make_state_transition_event(
                project_id="proj-1",
                task_id="task-1",
                from_status=from_s,
                to_status=to_s,
                triggered_by_kind=OwnerKind.CONTROLLER,
                triggered_by_id="ctrl-001",
                reason="Test",
            )
            seq.append(event)

        dicts = seq.to_dicts()
        assert len(dicts) == 2
        for d in dicts:
            assert "event_id" in d
            assert "project_id" in d
            assert "task_id" in d
            assert "event_type" in d
            assert "from_status" in d
            assert "to_status" in d
            assert "created_at" in d


# ──────────────────────────────────────────────────────────────
# Integration with Lease System
# ──────────────────────────────────────────────────────────────

class TestLifecycleWithLeases:
    """Prove lifecycle works with lease-based claim system."""

    def test_lease_claim_aligns_with_active_transition(self):
        """Lease claim should align with ready -> active transition."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        # Claim lease
        lease_result = claim_lease(
            task_id=task_id,
            project_id=project_id,
            owner_kind=OwnerKind.DELEGATE,
            owner_id="del-001",
            ttl_seconds=3600,
        )
        assert lease_result.success is True
        lease_id = lease_result.lease.lease_id

        # Transition to active (simulating with allow_claim)
        req = TransitionRequest(
            task_id=task_id,
            project_id=project_id,
            from_status=TaskStatus.READY,
            to_status=TaskStatus.ACTIVE,
            role=OwnerKind.DELEGATE,
            role_id="del-001",
            allow_claim=True,
        )
        result = execute_transition(req)
        assert result.success is True

        # Lease event should exist
        assert lease_result.event is not None
        assert lease_result.event.event_type == "lease_claimed"
        assert lease_result.event.payload["lease_id"] == lease_id

    def test_recovery_never_produces_done(self):
        """Lease expiry recovery must never produce done status."""
        for task_type, recovery_status in TASK_TYPE_RECOVERY.items():
            assert recovery_status != TaskStatus.DONE, \
                f"{task_type} recovery must not go to done"

        # This ensures the lifecycle proof is truthful:
        # done can only be reached via explicit controller acceptance,
        # never via automatic recovery.


# ──────────────────────────────────────────────────────────────
# Truth Constraints Validation
# ──────────────────────────────────────────────────────────────

class TestTruthConstraints:
    """Validate that the lifecycle proof meets truth constraints."""

    def test_state_and_event_history_align(self):
        """State changes must produce matching event records."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        # Perform transition
        req = TransitionRequest(
            task_id=task_id,
            project_id=project_id,
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.REVIEW_PENDING,
            role=OwnerKind.DELEGATE,
            role_id="del-001",
        )
        result = execute_transition(req)
        assert result.success is True

        # Build event
        event = build_event_record(
            result,
            project_id=project_id,
            triggered_by_kind=OwnerKind.DELEGATE,
            triggered_by_id="del-001",
        )

        # Verify alignment
        assert event["from_status"] == result.from_status.value
        assert event["to_status"] == result.to_status.value
        assert event["task_id"] == result.task_id

    def test_review_boundary_is_explicit(self):
        """review_pending state must exist and be distinct."""
        # review_pending is a canonical state
        assert TaskStatus.REVIEW_PENDING in TaskStatus

        # review_pending has different transitions than done
        review_next = {TaskStatus.DONE, TaskStatus.ACTIVE}
        done_next = set()
        
        from runtime.state_machine import get_valid_next_states
        assert get_valid_next_states(TaskStatus.REVIEW_PENDING) == review_next
        assert get_valid_next_states(TaskStatus.DONE) == done_next

        # review_pending is not equivalent to done
        assert TaskStatus.REVIEW_PENDING.value != TaskStatus.DONE.value

    def test_done_is_terminal_state(self):
        """done must be a terminal state with no outgoing transitions."""
        from runtime.state_machine import get_valid_next_states
        assert get_valid_next_states(TaskStatus.DONE) == set()

    def test_no_silent_promotion_to_done(self):
        """No automatic process can promote work to done."""
        # Recovery cannot produce done
        for task_type in TASK_TYPE_RECOVERY:
            assert TASK_TYPE_RECOVERY[task_type] != TaskStatus.DONE

        # Only explicit controller action can reach done
        level = get_transition_permission(
            TaskStatus.REVIEW_PENDING, TaskStatus.DONE, OwnerKind.CONTROLLER
        )
        assert level == PermissionLevel.ALLOWED

        # All other roles are denied
        for role in [OwnerKind.DELEGATE, OwnerKind.REVIEWER, OwnerKind.RUNTIME,
                     OwnerKind.SCHEDULER, OwnerKind.USER]:
            level = get_transition_permission(
                TaskStatus.REVIEW_PENDING, TaskStatus.DONE, role
            )
            assert level == PermissionLevel.DENIED, \
                f"{role.value} should not be able to move to done"
