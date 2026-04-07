"""
Tests for IKE Runtime v0 task state semantics.

Validates:
- Legal transitions per v0 state machine
- Illegal transition blocking
- Role-based permission guardrails
- Delegate claim boundary for ready -> active (CORRECTED)
- Waiting transition requires explicit waiting reason (CORRECTED)
- Control actions (non-state events)
- Guardrail: delegate cannot move review_pending -> done
"""

import pytest
from uuid import uuid4

from runtime.state_machine import (
    TaskStatus,
    OwnerKind,
    PermissionLevel,
    ControlAction,
    WaitingReason,
    is_valid_transition,
    get_valid_next_states,
    get_transition_permission,
    is_role_allowed,
    is_role_allowed_direct,
    validate_transition,
    TransitionError,
    InvalidTransitionError,
    RolePermissionError,
    GuardrailViolationError,
    ClaimRequiredError,
    validate_waiting_reason,
    VALID_WAITING_REASONS,
    describe_transition,
)

from runtime.transitions import (
    TransitionRequest,
    TransitionResult,
    execute_transition,
    record_control_action,
    build_event_record,
    build_task_update,
)


# ──────────────────────────────────────────────────────────────
# State Enum Sanity
# ──────────────────────────────────────────────────────────────

class TestStateEnumSanity:
    """Ensure the v0 state enum matches design exactly."""

    def test_exactly_seven_states(self):
        expected = {"inbox", "ready", "active", "waiting",
                     "review_pending", "done", "failed"}
        actual = {s.value for s in TaskStatus}
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test_no_cancelled_state(self):
        """cancelled is a control action, not a durable state."""
        assert "cancelled" not in {s.value for s in TaskStatus}

    def test_no_blocked_state(self):
        """blocked is modelled via waiting_reason, not a state."""
        assert "blocked" not in {s.value for s in TaskStatus}

    def test_no_dropped_state(self):
        assert "dropped" not in {s.value for s in TaskStatus}

    def test_no_deprioritized_state(self):
        assert "deprioritized" not in {s.value for s in TaskStatus}

    def test_all_owner_kinds_present(self):
        expected = {"controller", "delegate", "reviewer",
                     "runtime", "scheduler", "user"}
        actual = {k.value for k in OwnerKind}
        assert actual == expected

    def test_control_actions_are_not_states(self):
        """Control actions must not appear as TaskStatus values."""
        control_values = {a.value for a in ControlAction}
        state_values = {s.value for s in TaskStatus}
        assert not (control_values & state_values)


# ──────────────────────────────────────────────────────────────
# Legal Transitions
# ──────────────────────────────────────────────────────────────

class TestLegalTransitions:
    """Verify all design-specified legal transitions are valid."""

    LEGAL = [
        (TaskStatus.INBOX, TaskStatus.READY),
        (TaskStatus.READY, TaskStatus.ACTIVE),
        (TaskStatus.ACTIVE, TaskStatus.WAITING),
        (TaskStatus.ACTIVE, TaskStatus.REVIEW_PENDING),
        (TaskStatus.ACTIVE, TaskStatus.FAILED),
        (TaskStatus.WAITING, TaskStatus.READY),
        (TaskStatus.REVIEW_PENDING, TaskStatus.DONE),
        (TaskStatus.REVIEW_PENDING, TaskStatus.ACTIVE),
        (TaskStatus.FAILED, TaskStatus.READY),
    ]

    @pytest.mark.parametrize("from_status,to_status", LEGAL)
    def test_legal_transition_is_valid(self, from_status, to_status):
        assert is_valid_transition(from_status, to_status) is True

    def test_noop_is_not_valid(self):
        for s in TaskStatus:
            assert is_valid_transition(s, s) is False

    def test_get_valid_next_states_from_inbox(self):
        assert get_valid_next_states(TaskStatus.INBOX) == {TaskStatus.READY}

    def test_get_valid_next_states_from_ready(self):
        assert get_valid_next_states(TaskStatus.READY) == {TaskStatus.ACTIVE}

    def test_get_valid_next_states_from_active(self):
        assert get_valid_next_states(TaskStatus.ACTIVE) == {
            TaskStatus.WAITING,
            TaskStatus.REVIEW_PENDING,
            TaskStatus.FAILED,
        }

    def test_get_valid_next_states_from_waiting(self):
        assert get_valid_next_states(TaskStatus.WAITING) == {TaskStatus.READY}

    def test_get_valid_next_states_from_review_pending(self):
        assert get_valid_next_states(TaskStatus.REVIEW_PENDING) == {
            TaskStatus.DONE,
            TaskStatus.ACTIVE,
        }

    def test_get_valid_next_states_from_failed(self):
        assert get_valid_next_states(TaskStatus.FAILED) == {TaskStatus.READY}

    def test_get_valid_next_states_from_done(self):
        """done is terminal – no valid next states."""
        assert get_valid_next_states(TaskStatus.DONE) == set()


# ──────────────────────────────────────────────────────────────
# Illegal Transitions
# ──────────────────────────────────────────────────────────────

class TestIllegalTransitions:
    """Verify transitions not in the design are blocked."""

    ILLEGAL = [
        (TaskStatus.INBOX, TaskStatus.ACTIVE),
        (TaskStatus.INBOX, TaskStatus.DONE),
        (TaskStatus.INBOX, TaskStatus.FAILED),
        (TaskStatus.INBOX, TaskStatus.WAITING),
        (TaskStatus.INBOX, TaskStatus.REVIEW_PENDING),
        (TaskStatus.READY, TaskStatus.WAITING),
        (TaskStatus.READY, TaskStatus.DONE),
        (TaskStatus.READY, TaskStatus.FAILED),
        (TaskStatus.READY, TaskStatus.REVIEW_PENDING),
        (TaskStatus.ACTIVE, TaskStatus.DONE),
        (TaskStatus.ACTIVE, TaskStatus.READY),
        (TaskStatus.DONE, TaskStatus.READY),
        (TaskStatus.DONE, TaskStatus.ACTIVE),
        (TaskStatus.DONE, TaskStatus.INBOX),
        (TaskStatus.DONE, TaskStatus.WAITING),
        (TaskStatus.DONE, TaskStatus.REVIEW_PENDING),
        (TaskStatus.DONE, TaskStatus.FAILED),
        (TaskStatus.FAILED, TaskStatus.ACTIVE),
        (TaskStatus.FAILED, TaskStatus.DONE),
        (TaskStatus.FAILED, TaskStatus.WAITING),
        (TaskStatus.WAITING, TaskStatus.ACTIVE),
        (TaskStatus.WAITING, TaskStatus.DONE),
        (TaskStatus.WAITING, TaskStatus.FAILED),
        (TaskStatus.REVIEW_PENDING, TaskStatus.FAILED),
        (TaskStatus.REVIEW_PENDING, TaskStatus.WAITING),
        (TaskStatus.REVIEW_PENDING, TaskStatus.READY),
        (TaskStatus.REVIEW_PENDING, TaskStatus.INBOX),
    ]

    @pytest.mark.parametrize("from_status,to_status", ILLEGAL)
    def test_illegal_transition_is_invalid(self, from_status, to_status):
        assert is_valid_transition(from_status, to_status) is False

    def test_validate_transition_raises_on_illegal(self):
        with pytest.raises(InvalidTransitionError):
            validate_transition(
                TaskStatus.ACTIVE,
                TaskStatus.DONE,
                OwnerKind.CONTROLLER,
            )


# ──────────────────────────────────────────────────────────────
# Role Permissions – Allowed
# ──────────────────────────────────────────────────────────────

class TestRolePermissionsAllowed:
    """Verify role permissions that should be ALLOWED."""

    def test_controller_can_triage_inbox_to_ready(self):
        assert is_role_allowed(
            TaskStatus.INBOX, TaskStatus.READY, OwnerKind.CONTROLLER
        ) is True

    def test_controller_can_claim_ready_to_active(self):
        assert is_role_allowed(
            TaskStatus.READY, TaskStatus.ACTIVE, OwnerKind.CONTROLLER
        ) is True

    def test_controller_can_move_active_to_waiting(self):
        assert is_role_allowed(
            TaskStatus.ACTIVE, TaskStatus.WAITING, OwnerKind.CONTROLLER
        ) is True

    def test_delegate_can_move_active_to_waiting(self):
        assert is_role_allowed(
            TaskStatus.ACTIVE, TaskStatus.WAITING, OwnerKind.DELEGATE
        ) is True

    def test_controller_can_move_active_to_review_pending(self):
        assert is_role_allowed(
            TaskStatus.ACTIVE, TaskStatus.REVIEW_PENDING, OwnerKind.CONTROLLER
        ) is True

    def test_delegate_can_move_active_to_review_pending(self):
        assert is_role_allowed(
            TaskStatus.ACTIVE, TaskStatus.REVIEW_PENDING, OwnerKind.DELEGATE
        ) is True

    def test_controller_can_accept_review_to_done(self):
        assert is_role_allowed(
            TaskStatus.REVIEW_PENDING, TaskStatus.DONE, OwnerKind.CONTROLLER
        ) is True

    def test_controller_can_send_back_review_to_active(self):
        assert is_role_allowed(
            TaskStatus.REVIEW_PENDING, TaskStatus.ACTIVE, OwnerKind.CONTROLLER
        ) is True

    def test_controller_can_recover_failed_to_ready(self):
        assert is_role_allowed(
            TaskStatus.FAILED, TaskStatus.READY, OwnerKind.CONTROLLER
        ) is True

    def test_controller_can_recover_waiting_to_ready(self):
        assert is_role_allowed(
            TaskStatus.WAITING, TaskStatus.READY, OwnerKind.CONTROLLER
        ) is True

    def test_delegate_can_move_active_to_failed(self):
        assert is_role_allowed(
            TaskStatus.ACTIVE, TaskStatus.FAILED, OwnerKind.DELEGATE
        ) is True


# ──────────────────────────────────────────────────────────────
# CORRECTED: Delegate Claim Boundary for ready -> active
# ──────────────────────────────────────────────────────────────

class TestDelegateClaimBoundary:
    """FIX: delegate ready -> active must NOT be globally direct-allowed.

    Design rule: delegate may move ready -> active only when explicitly
    assigned or when lease claim succeeds under policy.
    """

    def test_delegate_ready_to_active_is_claim_required(self):
        """The permission level must be CLAIM_REQUIRED, not ALLOWED."""
        level = get_transition_permission(
            TaskStatus.READY, TaskStatus.ACTIVE, OwnerKind.DELEGATE
        )
        assert level == PermissionLevel.CLAIM_REQUIRED, \
            f"Expected CLAIM_REQUIRED, got {level}"

    def test_delegate_ready_to_active_is_not_is_role_allowed(self):
        """is_role_allowed should return False for claim-required transitions.

        The caller must use validate_transition with allow_claim=True
        after verifying assignment or lease claim.
        """
        assert is_role_allowed(
            TaskStatus.READY, TaskStatus.ACTIVE, OwnerKind.DELEGATE
        ) is False

    def test_delegate_ready_to_active_is_not_direct_allowed(self):
        """Direct allowed must be False for delegate ready->active."""
        assert is_role_allowed_direct(
            TaskStatus.READY, TaskStatus.ACTIVE, OwnerKind.DELEGATE
        ) is False

    def test_delegate_validate_fails_without_claim(self):
        """validate_transition must raise ClaimRequiredError without claim flag."""
        with pytest.raises(ClaimRequiredError):
            validate_transition(
                TaskStatus.READY, TaskStatus.ACTIVE, OwnerKind.DELEGATE
            )

    def test_delegate_validate_passes_with_claim_flag(self):
        """validate_transition passes when claim is verified."""
        validate_transition(
            TaskStatus.READY, TaskStatus.ACTIVE, OwnerKind.DELEGATE,
            allow_claim=True,
        )

    def test_controller_still_allowed_ready_to_active(self):
        """Controller should not be affected by the delegate fix."""
        level = get_transition_permission(
            TaskStatus.READY, TaskStatus.ACTIVE, OwnerKind.CONTROLLER
        )
        assert level == PermissionLevel.ALLOWED
        validate_transition(
            TaskStatus.READY, TaskStatus.ACTIVE, OwnerKind.CONTROLLER
        )

    def test_runtime_still_policy_ready_to_active(self):
        """Runtime should still need policy flag for ready->active."""
        level = get_transition_permission(
            TaskStatus.READY, TaskStatus.ACTIVE, OwnerKind.RUNTIME
        )
        assert level == PermissionLevel.RUNTIME_POLICY
        with pytest.raises(RolePermissionError):
            validate_transition(
                TaskStatus.READY, TaskStatus.ACTIVE, OwnerKind.RUNTIME
            )
        validate_transition(
            TaskStatus.READY, TaskStatus.ACTIVE, OwnerKind.RUNTIME,
            allow_runtime_policy=True,
        )

    def test_delegate_claim_error_message_is_actionable(self):
        """Error message should guide the caller to set allow_claim."""
        with pytest.raises(ClaimRequiredError) as exc_info:
            validate_transition(
                TaskStatus.READY, TaskStatus.ACTIVE, OwnerKind.DELEGATE
            )
        msg = str(exc_info.value).lower()
        assert "allow_claim" in msg
        assert "assignment" in msg or "lease" in msg

    def test_execute_transition_delegate_claim_without_flag(self):
        """execute_transition returns error for delegate ready->active without claim."""
        req = TransitionRequest(
            task_id=str(uuid4()),
            project_id=str(uuid4()),
            from_status=TaskStatus.READY,
            to_status=TaskStatus.ACTIVE,
            role=OwnerKind.DELEGATE,
            role_id="del-001",
        )
        result = execute_transition(req)
        assert result.success is False
        assert result.error is not None
        assert "claim" in result.error.lower()

    def test_execute_transition_delegate_claim_with_flag(self):
        """execute_transition succeeds when claim flag is set."""
        req = TransitionRequest(
            task_id=str(uuid4()),
            project_id=str(uuid4()),
            from_status=TaskStatus.READY,
            to_status=TaskStatus.ACTIVE,
            role=OwnerKind.DELEGATE,
            role_id="del-001",
            allow_claim=True,
        )
        result = execute_transition(req)
        assert result.success is True
        assert result.error is None


# ──────────────────────────────────────────────────────────────
# Role Permissions – Denied
# ──────────────────────────────────────────────────────────────

class TestRolePermissionsDenied:
    """Verify role permissions that should be DENIED."""

    def test_delegate_cannot_triage_inbox(self):
        assert is_role_allowed(
            TaskStatus.INBOX, TaskStatus.READY, OwnerKind.DELEGATE
        ) is False

    def test_delegate_cannot_accept_review_to_done(self):
        """Critical guardrail: delegate cannot move review_pending -> done."""
        assert is_role_allowed(
            TaskStatus.REVIEW_PENDING, TaskStatus.DONE, OwnerKind.DELEGATE
        ) is False

    def test_reviewer_cannot_transition_tasks(self):
        """Reviewer has no direct task transition rights."""
        transitions = [
            (TaskStatus.INBOX, TaskStatus.READY),
            (TaskStatus.READY, TaskStatus.ACTIVE),
            (TaskStatus.ACTIVE, TaskStatus.WAITING),
            (TaskStatus.ACTIVE, TaskStatus.REVIEW_PENDING),
            (TaskStatus.ACTIVE, TaskStatus.FAILED),
            (TaskStatus.WAITING, TaskStatus.READY),
            (TaskStatus.REVIEW_PENDING, TaskStatus.DONE),
            (TaskStatus.REVIEW_PENDING, TaskStatus.ACTIVE),
            (TaskStatus.FAILED, TaskStatus.READY),
        ]
        for frm, to in transitions:
            assert is_role_allowed(frm, to, OwnerKind.REVIEWER) is False, \
                f"Reviewer should not be allowed {frm.value} -> {to.value}"

    def test_scheduler_cannot_transition_tasks(self):
        for frm, to in [
            (TaskStatus.INBOX, TaskStatus.READY),
            (TaskStatus.READY, TaskStatus.ACTIVE),
            (TaskStatus.ACTIVE, TaskStatus.WAITING),
        ]:
            assert is_role_allowed(frm, to, OwnerKind.SCHEDULER) is False

    def test_user_cannot_transition_tasks(self):
        for frm, to in [
            (TaskStatus.INBOX, TaskStatus.READY),
            (TaskStatus.READY, TaskStatus.ACTIVE),
            (TaskStatus.REVIEW_PENDING, TaskStatus.DONE),
        ]:
            assert is_role_allowed(frm, to, OwnerKind.USER) is False


# ──────────────────────────────────────────────────────────────
# Guardrail: Delegate Cannot Accept
# ──────────────────────────────────────────────────────────────

class TestDelegateAcceptanceGuardrail:
    """The most critical guardrail: delegate cannot move reviewable work to done."""

    def test_delegate_denied_review_pending_to_done(self):
        level = get_transition_permission(
            TaskStatus.REVIEW_PENDING, TaskStatus.DONE, OwnerKind.DELEGATE
        )
        assert level == PermissionLevel.DENIED

    def test_delegate_validate_raises_guardrail_violation(self):
        with pytest.raises(GuardrailViolationError):
            validate_transition(
                TaskStatus.REVIEW_PENDING,
                TaskStatus.DONE,
                OwnerKind.DELEGATE,
            )

    def test_reviewer_denied_review_pending_to_done(self):
        level = get_transition_permission(
            TaskStatus.REVIEW_PENDING, TaskStatus.DONE, OwnerKind.REVIEWER
        )
        assert level == PermissionLevel.DENIED

    def test_runtime_denied_review_pending_to_done(self):
        level = get_transition_permission(
            TaskStatus.REVIEW_PENDING, TaskStatus.DONE, OwnerKind.RUNTIME
        )
        assert level == PermissionLevel.DENIED

    def test_controller_allowed_review_pending_to_done(self):
        level = get_transition_permission(
            TaskStatus.REVIEW_PENDING, TaskStatus.DONE, OwnerKind.CONTROLLER
        )
        assert level == PermissionLevel.ALLOWED


# ──────────────────────────────────────────────────────────────
# Runtime Policy Transitions
# ──────────────────────────────────────────────────────────────

class TestRuntimePolicyTransitions:
    """Runtime can perform recovery transitions only with policy flag."""

    def test_runtime_denied_without_policy_flag(self):
        with pytest.raises(RolePermissionError, match="runtime recovery policy"):
            validate_transition(
                TaskStatus.ACTIVE, TaskStatus.WAITING, OwnerKind.RUNTIME
            )

    def test_runtime_allowed_with_policy_flag(self):
        validate_transition(
            TaskStatus.ACTIVE, TaskStatus.WAITING, OwnerKind.RUNTIME,
            allow_runtime_policy=True,
        )

    def test_runtime_denied_inbox_to_ready_without_flag(self):
        with pytest.raises(RolePermissionError):
            validate_transition(
                TaskStatus.INBOX, TaskStatus.READY, OwnerKind.RUNTIME
            )

    def test_runtime_allowed_inbox_to_ready_with_flag(self):
        validate_transition(
            TaskStatus.INBOX, TaskStatus.READY, OwnerKind.RUNTIME,
            allow_runtime_policy=True,
        )


# ──────────────────────────────────────────────────────────────
# CORRECTED: Waiting Reason Validation
# ──────────────────────────────────────────────────────────────

class TestWaitingReasonValidation:
    """FIX: validate_waiting_reason rejects None and empty strings."""

    def test_valid_waiting_reasons(self):
        for reason in WaitingReason:
            assert validate_waiting_reason(reason.value) is True

    def test_none_is_not_valid(self):
        """FIX: None should be rejected."""
        assert validate_waiting_reason(None) is False

    def test_empty_string_is_not_valid(self):
        """FIX: empty string should be rejected."""
        assert validate_waiting_reason("") is False

    def test_invalid_waiting_reason(self):
        assert validate_waiting_reason("blocked") is False
        assert validate_waiting_reason("cancelled") is False
        assert validate_waiting_reason("on_hold") is False

    def test_all_valid_reasons_covered(self):
        expected = {
            "external_input", "delegate_result", "dependency_unmet",
            "capability_missing", "manual_intervention",
        }
        assert VALID_WAITING_REASONS == expected


# ──────────────────────────────────────────────────────────────
# CORRECTED: build_task_update requires waiting_reason
# ──────────────────────────────────────────────────────────────

class TestWaitingUpdateSemantics:
    """FIX: build_task_update must require valid waiting_reason for WAITING."""

    def test_waiting_transition_requires_reason(self):
        """FIX: transitioning to WAITING without waiting_reason raises ValueError."""
        result = TransitionResult(
            success=True,
            task_id=str(uuid4()),
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.WAITING,
            event_type="state_transition",
            event_reason="",
        )
        with pytest.raises(ValueError, match="waiting_reason"):
            build_task_update(result)

    def test_waiting_transition_with_valid_reason_succeeds(self):
        """With a valid waiting_reason, the update succeeds."""
        result = TransitionResult(
            success=True,
            task_id=str(uuid4()),
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.WAITING,
            event_type="state_transition",
            event_reason="",
        )
        updates = build_task_update(
            result,
            waiting_reason="dependency_unmet",
            waiting_detail="Waiting on external API",
        )
        assert updates["status"] == "waiting"
        assert updates["waiting_reason"] == "dependency_unmet"
        assert updates["waiting_detail"] == "Waiting on external API"

    def test_waiting_transition_with_invalid_reason_fails(self):
        """Invalid waiting reasons are rejected."""
        result = TransitionResult(
            success=True,
            task_id=str(uuid4()),
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.WAITING,
            event_type="state_transition",
            event_reason="",
        )
        with pytest.raises(ValueError):
            build_task_update(result, waiting_reason="blocked")

    def test_waiting_transition_with_none_reason_fails(self):
        """None as waiting_reason is rejected."""
        result = TransitionResult(
            success=True,
            task_id=str(uuid4()),
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.WAITING,
            event_type="state_transition",
            event_reason="",
        )
        with pytest.raises(ValueError):
            build_task_update(result, waiting_reason=None)

    def test_waiting_transition_with_empty_string_fails(self):
        """Empty string as waiting_reason is rejected."""
        result = TransitionResult(
            success=True,
            task_id=str(uuid4()),
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.WAITING,
            event_type="state_transition",
            event_reason="",
        )
        with pytest.raises(ValueError):
            build_task_update(result, waiting_reason="")

    def test_force_bypasses_waiting_reason_check(self):
        """force=True bypasses the validation as an escape hatch.
        
        R1-A5 ENFORCEMENT: force=True now requires explicit role parameter.
        Only controller and runtime roles are authorized to use force=True.
        """
        result = TransitionResult(
            success=True,
            task_id=str(uuid4()),
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.WAITING,
            event_type="state_transition",
            event_reason="",
        )
        # R1-A5: role must be provided when force=True
        updates = build_task_update(
            result,
            waiting_reason=None,
            force=True,
            role=OwnerKind.CONTROLLER,
        )
        assert updates["status"] == "waiting"
        assert updates["waiting_reason"] is None

    def test_non_waiting_transitions_not_affected(self):
        """Non-WAITING transitions work normally."""
        result = TransitionResult(
            success=True,
            task_id=str(uuid4()),
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.REVIEW_PENDING,
            event_type="state_transition",
            event_reason="",
        )
        updates = build_task_update(result)
        assert updates["status"] == "review_pending"
        assert updates["waiting_reason"] is None
        assert updates["waiting_detail"] is None

    def test_waiting_error_message_is_actionable(self):
        """Error message should list valid reasons."""
        result = TransitionResult(
            success=True,
            task_id=str(uuid4()),
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.WAITING,
            event_type="state_transition",
            event_reason="",
        )
        with pytest.raises(ValueError) as exc_info:
            build_task_update(result, waiting_reason=None)
        msg = str(exc_info.value).lower()
        assert "waiting_reason" in msg
        assert "dependency_unmet" in msg


# ──────────────────────────────────────────────────────────────
# Control Actions
# ──────────────────────────────────────────────────────────────

class TestControlActions:
    """Control actions are events, not state changes."""

    def test_control_action_values(self):
        expected = {"cancelled", "dropped", "deprioritized"}
        actual = {a.value for a in ControlAction}
        assert actual == expected

    def test_control_action_not_in_states(self):
        state_values = {s.value for s in TaskStatus}
        control_values = {a.value for a in ControlAction}
        assert not (state_values & control_values)

    def test_record_control_action_preserves_state(self):
        event = record_control_action(
            task_id=str(uuid4()),
            project_id=str(uuid4()),
            action=ControlAction.CANCELLED,
            role=OwnerKind.CONTROLLER,
            role_id="ctrl-001",
            reason="Project cancelled",
            current_status=TaskStatus.ACTIVE,
        )
        assert event["from_status"] == "active"
        assert event["to_status"] == "active"  # state unchanged
        assert event["payload"]["action"] == "cancelled"
        assert event["payload"]["control_action"] is True
        assert event["event_type"] == "control_action"


# ──────────────────────────────────────────────────────────────
# Transition Execution
# ──────────────────────────────────────────────────────────────

class TestExecuteTransition:
    """Integration tests for the execute_transition function."""

    def test_successful_transition(self):
        req = TransitionRequest(
            task_id=str(uuid4()),
            project_id=str(uuid4()),
            from_status=TaskStatus.READY,
            to_status=TaskStatus.ACTIVE,
            role=OwnerKind.CONTROLLER,
            role_id="ctrl-001",
            reason="Starting work",
        )
        result = execute_transition(req)
        assert result.success is True
        assert result.error is None
        assert result.event_type == "state_transition"

    def test_failed_illegal_transition(self):
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
        assert result.error is not None
        assert "Invalid transition" in result.error

    def test_failed_delegate_acceptance(self):
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
        assert result.error is not None
        assert "Guardrail violation" in result.error

    def test_failed_delegate_denied_transition(self):
        req = TransitionRequest(
            task_id=str(uuid4()),
            project_id=str(uuid4()),
            from_status=TaskStatus.INBOX,
            to_status=TaskStatus.READY,
            role=OwnerKind.DELEGATE,
            role_id="del-001",
        )
        result = execute_transition(req)
        assert result.success is False
        assert result.error is not None
        assert "not permitted" in result.error

    def test_runtime_policy_transition_success(self):
        req = TransitionRequest(
            task_id=str(uuid4()),
            project_id=str(uuid4()),
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.WAITING,
            role=OwnerKind.RUNTIME,
            role_id="runtime",
            reason="Lease expired",
            allow_runtime_policy=True,
        )
        result = execute_transition(req)
        assert result.success is True

    def test_runtime_policy_transition_without_flag_fails(self):
        req = TransitionRequest(
            task_id=str(uuid4()),
            project_id=str(uuid4()),
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.WAITING,
            role=OwnerKind.RUNTIME,
            role_id="runtime",
        )
        result = execute_transition(req)
        assert result.success is False
        assert "runtime recovery policy" in result.error


# ──────────────────────────────────────────────────────────────
# Event & Task Update Builders
# ──────────────────────────────────────────────────────────────

class TestEventBuilder:
    def test_build_event_record_from_result(self):
        result = TransitionResult(
            success=True,
            task_id=str(uuid4()),
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.REVIEW_PENDING,
            event_type="state_transition",
            event_reason="Work complete, awaiting review",
        )
        event = build_event_record(
            result,
            project_id=str(uuid4()),
            triggered_by_kind=OwnerKind.DELEGATE,
            triggered_by_id="del-001",
            extra_payload={"artifact_ref": "art-123"},
        )
        assert event["from_status"] == "active"
        assert event["to_status"] == "review_pending"
        assert event["triggered_by_kind"] == "delegate"
        assert event["payload"]["artifact_ref"] == "art-123"

    def test_build_event_fails_on_failed_result(self):
        result = TransitionResult(
            success=False,
            task_id=str(uuid4()),
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.DONE,
            error="Invalid transition",
        )
        with pytest.raises(ValueError):
            build_event_record(
                result,
                project_id=str(uuid4()),
                triggered_by_kind=OwnerKind.CONTROLLER,
                triggered_by_id="ctrl-001",
            )


class TestTaskUpdateBuilder:
    def test_update_for_done_transition(self):
        result = TransitionResult(
            success=True,
            task_id=str(uuid4()),
            from_status=TaskStatus.REVIEW_PENDING,
            to_status=TaskStatus.DONE,
            event_type="state_transition",
            event_reason="Review passed",
        )
        updates = build_task_update(
            result,
            result_summary="All checks passed",
        )
        assert updates["status"] == "done"
        assert updates["result_summary"] == "All checks passed"
        assert "ended_at" in updates

    def test_update_clears_waiting_when_leaving_waiting(self):
        result = TransitionResult(
            success=True,
            task_id=str(uuid4()),
            from_status=TaskStatus.WAITING,
            to_status=TaskStatus.READY,
            event_type="state_transition",
            event_reason="",
        )
        updates = build_task_update(
            result,
            waiting_reason="dependency_unmet",
        )
        assert updates["status"] == "ready"
        assert updates["waiting_reason"] is None
        assert updates["waiting_detail"] is None

    def test_update_sets_started_at_when_entering_active(self):
        result = TransitionResult(
            success=True,
            task_id=str(uuid4()),
            from_status=TaskStatus.READY,
            to_status=TaskStatus.ACTIVE,
            event_type="state_transition",
            event_reason="",
        )
        updates = build_task_update(result, current_lease_id="lease-001")
        assert "started_at" in updates
        assert updates["current_lease_id"] == "lease-001"

    def test_update_does_not_set_started_at_when_already_active(self):
        result = TransitionResult(
            success=True,
            task_id=str(uuid4()),
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.WAITING,
            event_type="state_transition",
            event_reason="",
        )
        updates = build_task_update(
            result,
            waiting_reason="dependency_unmet",
        )
        assert "started_at" not in updates


# ──────────────────────────────────────────────────────────────
# Transition Descriptions
# ──────────────────────────────────────────────────────────────

class TestTransitionDescriptions:
    def test_describe_known_transitions(self):
        assert "Triage" in describe_transition(
            TaskStatus.INBOX, TaskStatus.READY
        )
        assert "claimed" in describe_transition(
            TaskStatus.READY, TaskStatus.ACTIVE
        ).lower()
        assert "accepted" in describe_transition(
            TaskStatus.REVIEW_PENDING, TaskStatus.DONE
        )

    def test_describe_unknown_transition(self):
        desc = describe_transition(TaskStatus.INBOX, TaskStatus.DONE)
        assert "inbox" in desc
        assert "done" in desc


# ──────────────────────────────────────────────────────────────
# Machine-distinguishability Checks
# ──────────────────────────────────────────────────────────────

class TestStateDistinguishability:
    """Verify states that must be machine-distinguishable are distinct."""

    def test_waiting_not_equivalent_to_blocked(self):
        assert TaskStatus.WAITING.value != "blocked"

    def test_review_pending_not_equivalent_to_done(self):
        assert TaskStatus.REVIEW_PENDING != TaskStatus.DONE
        assert TaskStatus.REVIEW_PENDING.value != TaskStatus.DONE.value

    def test_failed_not_equivalent_to_cancelled(self):
        assert TaskStatus.FAILED.value != "cancelled"

    def test_review_pending_has_different_transitions_than_done(self):
        """review_pending has outgoing transitions; done does not."""
        rp_next = get_valid_next_states(TaskStatus.REVIEW_PENDING)
        done_next = get_valid_next_states(TaskStatus.DONE)
        assert len(rp_next) > 0
        assert len(done_next) == 0

    def test_waiting_has_different_transitions_than_failed(self):
        waiting_next = get_valid_next_states(TaskStatus.WAITING)
        failed_next = get_valid_next_states(TaskStatus.FAILED)
        assert waiting_next == {TaskStatus.READY}
        assert failed_next == {TaskStatus.READY}
        assert TaskStatus.WAITING != TaskStatus.FAILED


# ──────────────────────────────────────────────────────────────
# Permission Level Coverage
# ──────────────────────────────────────────────────────────────

class TestPermissionLevelCoverage:
    """Ensure all allowed transitions have permission entries."""

    def test_all_transitions_have_permissions(self):
        from runtime.state_machine import (
            ALLOWED_TRANSITIONS,
            TRANSITION_PERMISSIONS,
        )
        for transition in ALLOWED_TRANSITIONS:
            assert transition in TRANSITION_PERMISSIONS, \
                f"Missing permission entry for {transition}"

    def test_all_permissions_have_all_roles(self):
        from runtime.state_machine import TRANSITION_PERMISSIONS
        for transition, role_perms in TRANSITION_PERMISSIONS.items():
            for role in OwnerKind:
                assert role in role_perms, \
                    f"Missing role {role.value} for {transition}"

    def test_permission_level_enum_has_claim_required(self):
        """CLAIM_REQUIRED must exist as a distinct level."""
        assert PermissionLevel.CLAIM_REQUIRED is not None
        assert PermissionLevel.CLAIM_REQUIRED.value == "C"
        # It must be distinct from all other levels
        levels = {p for p in PermissionLevel}
        assert len(levels) == 5  # Y, R, P, C, N
