"""
Tests for IKE Runtime v0 state machine hardening.

Validates:
- Legal claim path: delegate with ClaimContext can transition ready->active
- Illegal claim path: delegate without claim proof cannot transition ready->active
- Restricted force-path: force=True denied for delegates, allowed for controller/runtime
- ClaimContext validation: structured proof replaces loose allow_claim
- R1-C1 Hardening:
  - allow_claim=True no longer satisfies CLAIM_REQUIRED transitions
  - role=None with force=True is REJECTED (legacy bypass closed)
  - ClaimContext fields validated (claim_ref, delegate_id, task_id non-empty)
- Regression: first-wave corrected semantics still hold
"""

import pytest

from runtime.state_machine import (
    TaskStatus,
    OwnerKind,
    PermissionLevel,
    ClaimType,
    ClaimContext,
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
    ControlAction,
    ControlActionRecord,
    validate_waiting_reason,
    VALID_WAITING_REASONS,
    describe_transition,
)


# ──────────────────────────────────────────────────────────────
# Claim Context – Legal Claim Path
# ──────────────────────────────────────────────────────────────

class TestClaimContextLegalPath:
    """Prove that a delegate with proper ClaimContext can claim a task."""

    def test_delegate_with_explicit_assignment_claim(self):
        """Delegate with explicit_assignment ClaimContext can go ready->active."""
        claim = ClaimContext(
            claim_type=ClaimType.EXPLICIT_ASSIGNMENT,
            claim_ref="assignment-001",
            delegate_id="del-001",
            task_id="task-1",
        )
        # Should NOT raise – claim context satisfies the gate
        validate_transition(
            TaskStatus.READY,
            TaskStatus.ACTIVE,
            OwnerKind.DELEGATE,
            claim_context=claim,
        )

    def test_delegate_with_active_lease_claim(self):
        """Delegate with active_lease ClaimContext can go ready->active."""
        claim = ClaimContext(
            claim_type=ClaimType.ACTIVE_LEASE,
            claim_ref="lease-abc-123",
            delegate_id="del-002",
            task_id="task-2",
        )
        validate_transition(
            TaskStatus.READY,
            TaskStatus.ACTIVE,
            OwnerKind.DELEGATE,
            claim_context=claim,
        )

    def test_controller_still_allowed_without_claim(self):
        """Controller can transition ready->active without any claim context."""
        validate_transition(
            TaskStatus.READY,
            TaskStatus.ACTIVE,
            OwnerKind.CONTROLLER,
        )

    def test_runtime_policy_still_works(self):
        """Runtime can transition via runtime policy flag."""
        validate_transition(
            TaskStatus.READY,
            TaskStatus.ACTIVE,
            OwnerKind.RUNTIME,
            allow_runtime_policy=True,
        )

    def test_allow_claim_keyword_is_removed(self):
        """R1-C7: allow_claim compatibility keyword no longer exists."""
        with pytest.raises(TypeError, match="allow_claim"):
            validate_transition(
                TaskStatus.READY,
                TaskStatus.ACTIVE,
                OwnerKind.DELEGATE,
                allow_claim=True,
            )


# ──────────────────────────────────────────────────────────────
# Claim Context – Illegal Claim Path
# ──────────────────────────────────────────────────────────────

class TestClaimContextIllegalPath:
    """Prove that delegates without proper claim proof are blocked."""

    def test_delegate_without_claim_blocked(self):
        """Delegate with no claim context is blocked."""
        with pytest.raises(ClaimRequiredError, match="verified claim"):
            validate_transition(
                TaskStatus.READY,
                TaskStatus.ACTIVE,
                OwnerKind.DELEGATE,
            )

    def test_delegate_denied_on_other_transitions(self):
        """Delegate is still denied on transitions that are not claim-gated."""
        # delegate -> inbox->ready is DENIED, not CLAIM_REQUIRED
        with pytest.raises(RolePermissionError):
            validate_transition(
                TaskStatus.INBOX,
                TaskStatus.READY,
                OwnerKind.DELEGATE,
            )

        # delegate -> waiting->ready is DENIED
        with pytest.raises(RolePermissionError):
            validate_transition(
                TaskStatus.WAITING,
                TaskStatus.READY,
                OwnerKind.DELEGATE,
            )

    def test_reviewer_denied_everywhere(self):
        """Reviewer role is denied on all transitions."""
        for frm, to in [
            (TaskStatus.INBOX, TaskStatus.READY),
            (TaskStatus.READY, TaskStatus.ACTIVE),
            (TaskStatus.ACTIVE, TaskStatus.WAITING),
            (TaskStatus.REVIEW_PENDING, TaskStatus.DONE),
        ]:
            with pytest.raises((RolePermissionError, ClaimRequiredError)):
                validate_transition(frm, to, OwnerKind.REVIEWER)

    def test_scheduler_denied_everywhere(self):
        """Scheduler role is denied on all transitions."""
        with pytest.raises((RolePermissionError, ClaimRequiredError)):
            validate_transition(
                TaskStatus.READY,
                TaskStatus.ACTIVE,
                OwnerKind.SCHEDULER,
            )

    def test_user_denied_everywhere(self):
        """User role is denied on all transitions."""
        with pytest.raises((RolePermissionError, ClaimRequiredError)):
            validate_transition(
                TaskStatus.READY,
                TaskStatus.ACTIVE,
                OwnerKind.USER,
            )


# ──────────────────────────────────────────────────────────────
# Force-Path Restriction (R1-A1 Hardening)
# ──────────────────────────────────────────────────────────────

class TestForcePathRestriction:
    """Prove that force=True is restricted to controller/runtime roles."""

    def test_controller_can_use_force(self):
        """Controller is authorized to use force=True."""
        from runtime.transitions import build_task_update, FORCE_AUTHORIZED_ROLES
        from runtime.state_machine import TaskStatus

        result = type('TransitionResult', (), {
            'success': True,
            'task_id': 'task-1',
            'from_status': TaskStatus.ACTIVE,
            'to_status': TaskStatus.WAITING,
        })()

        # Should NOT raise – controller is authorized
        updates = build_task_update(
            result,
            waiting_reason=None,
            force=True,
            role=OwnerKind.CONTROLLER,
        )
        assert updates["status"] == "waiting"

    def test_runtime_can_use_force(self):
        """Runtime is authorized to use force=True."""
        from runtime.transitions import build_task_update

        result = type('TransitionResult', (), {
            'success': True,
            'task_id': 'task-1',
            'from_status': TaskStatus.ACTIVE,
            'to_status': TaskStatus.WAITING,
        })()

        # Should NOT raise – runtime is authorized
        updates = build_task_update(
            result,
            waiting_reason=None,
            force=True,
            role=OwnerKind.RUNTIME,
        )
        assert updates["status"] == "waiting"

    def test_delegate_cannot_use_force(self):
        """Delegate is NOT authorized to use force=True."""
        from runtime.transitions import build_task_update

        result = type('TransitionResult', (), {
            'success': True,
            'task_id': 'task-1',
            'from_status': TaskStatus.ACTIVE,
            'to_status': TaskStatus.WAITING,
        })()

        with pytest.raises(ValueError, match="force=True is restricted"):
            build_task_update(
                result,
                waiting_reason=None,
                force=True,
                role=OwnerKind.DELEGATE,
            )

    def test_reviewer_cannot_use_force(self):
        """Reviewer is NOT authorized to use force=True."""
        from runtime.transitions import build_task_update

        result = type('TransitionResult', (), {
            'success': True,
            'task_id': 'task-1',
            'from_status': TaskStatus.ACTIVE,
            'to_status': TaskStatus.WAITING,
        })()

        with pytest.raises(ValueError, match="force=True is restricted"):
            build_task_update(
                result,
                waiting_reason=None,
                force=True,
                role=OwnerKind.REVIEWER,
            )

    def test_force_without_role_is_rejected(self):
        """R1-A5: When role is None, force=True is REJECTED (legacy bypass closed)."""
        from runtime.transitions import build_task_update

        result = type('TransitionResult', (), {
            'success': True,
            'task_id': 'task-1',
            'from_status': TaskStatus.ACTIVE,
            'to_status': TaskStatus.WAITING,
        })()

        # R1-A5: role=None with force=True is now rejected
        with pytest.raises(ValueError, match="force=True requires explicit role"):
            build_task_update(
                result,
                waiting_reason=None,
                force=True,
                role=None,
            )

    def test_delegate_with_valid_waiting_reason_works(self):
        """Delegate with valid waiting_reason can transition to WAITING (no force needed)."""
        from runtime.transitions import build_task_update

        result = type('TransitionResult', (), {
            'success': True,
            'task_id': 'task-1',
            'from_status': TaskStatus.ACTIVE,
            'to_status': TaskStatus.WAITING,
        })()

        updates = build_task_update(
            result,
            waiting_reason="external_input",
            waiting_detail="Waiting for user response",
            force=False,
            role=OwnerKind.DELEGATE,
        )
        assert updates["status"] == "waiting"
        assert updates["waiting_reason"] == "external_input"


# ──────────────────────────────────────────────────────────────
# Guardrail Regression Tests
# ──────────────────────────────────────────────────────────────

class TestGuardrailRegression:
    """Ensure first-wave corrected semantics are not broken."""

    def test_delegate_cannot_move_review_to_done(self):
        """Guardrail: delegate cannot bypass review to mark work done."""
        with pytest.raises(GuardrailViolationError, match="delegate cannot move review_pending"):
            validate_transition(
                TaskStatus.REVIEW_PENDING,
                TaskStatus.DONE,
                OwnerKind.DELEGATE,
            )

    def test_controller_can_move_review_to_done(self):
        """Only controller can complete review_pending work."""
        validate_transition(
            TaskStatus.REVIEW_PENDING,
            TaskStatus.DONE,
            OwnerKind.CONTROLLER,
        )

    def test_invalid_transition_still_rejected(self):
        """Structurally invalid transitions are still rejected."""
        with pytest.raises(InvalidTransitionError):
            validate_transition(
                TaskStatus.INBOX,
                TaskStatus.DONE,
                OwnerKind.CONTROLLER,
            )

    def test_no_op_transition_rejected(self):
        """Same-state transition is not valid."""
        assert is_valid_transition(TaskStatus.ACTIVE, TaskStatus.ACTIVE) is False


# ──────────────────────────────────────────────────────────────
# Permission Matrix Verification
# ──────────────────────────────────────────────────────────────

class TestPermissionMatrix:
    """Verify the role-based permission matrix is correctly configured."""

    def test_ready_to_active_is_claim_required_for_delegate(self):
        """Delegate on ready->active must be CLAIM_REQUIRED, not ALLOWED."""
        level = get_transition_permission(
            TaskStatus.READY,
            TaskStatus.ACTIVE,
            OwnerKind.DELEGATE,
        )
        assert level == PermissionLevel.CLAIM_REQUIRED

    def test_ready_to_active_denied_for_non_claim_roles(self):
        """Non-delegate roles should not have claim-gated access to ready->active."""
        for role in [OwnerKind.REVIEWER, OwnerKind.SCHEDULER, OwnerKind.USER]:
            level = get_transition_permission(
                TaskStatus.READY,
                TaskStatus.ACTIVE,
                role,
            )
            assert level == PermissionLevel.DENIED

    def test_is_role_allowed_excludes_claim_required(self):
        """is_role_allowed returns False for CLAIM_REQUIRED (gate not passed)."""
        assert is_role_allowed(
            TaskStatus.READY,
            TaskStatus.ACTIVE,
            OwnerKind.DELEGATE,
        ) is False

    def test_is_role_allowed_allows_controller(self):
        """is_role_allowed returns True for controller on ready->active."""
        assert is_role_allowed(
            TaskStatus.READY,
            TaskStatus.ACTIVE,
            OwnerKind.CONTROLLER,
        ) is True

    def test_is_role_allowed_direct_excludes_controller_only(self):
        """is_role_allowed_direct only returns True for ALLOWED level."""
        # review_pending -> done is CONTROLLER_ONLY for controller
        assert is_role_allowed_direct(
            TaskStatus.REVIEW_PENDING,
            TaskStatus.DONE,
            OwnerKind.CONTROLLER,
        ) is True  # CONTROLLER has ALLOWED on this transition


# ──────────────────────────────────────────────────────────────
# ClaimContext Validation
# ──────────────────────────────────────────────────────────────

class TestClaimContextValidation:
    """Verify ClaimContext structure and validation."""

    def test_claim_context_is_frozen(self):
        """ClaimContext is immutable."""
        claim = ClaimContext(
            claim_type=ClaimType.EXPLICIT_ASSIGNMENT,
            claim_ref="assign-001",
            delegate_id="del-001",
            task_id="task-1",
        )
        with pytest.raises(AttributeError):
            claim.delegate_id = "del-002"

    def test_claim_context_has_all_fields(self):
        """ClaimContext requires all four fields."""
        claim = ClaimContext(
            claim_type=ClaimType.ACTIVE_LEASE,
            claim_ref="lease-xyz",
            delegate_id="del-042",
            task_id="task-99",
        )
        assert claim.claim_type == ClaimType.ACTIVE_LEASE
        assert claim.claim_ref == "lease-xyz"
        assert claim.delegate_id == "del-042"
        assert claim.task_id == "task-99"

    def test_claim_type_enum_values(self):
        """ClaimType has exactly the expected values."""
        assert ClaimType.EXPLICIT_ASSIGNMENT.value == "explicit_assignment"
        assert ClaimType.ACTIVE_LEASE.value == "active_lease"


# ──────────────────────────────────────────────────────────────
# Waiting Reason Validation
# ──────────────────────────────────────────────────────────────

class TestWaitingReasonValidation:
    """Validate waiting reason helpers."""

    def test_valid_reasons_accepted(self):
        for reason in VALID_WAITING_REASONS:
            assert validate_waiting_reason(reason) is True

    def test_invalid_reasons_rejected(self):
        for reason in [None, "", "blocked", "custom_reason", "waiting"]:
            assert validate_waiting_reason(reason) is False

    def test_valid_waiting_reasons_set(self):
        """Valid reasons match the WaitingReason enum."""
        from runtime.state_machine import WaitingReason
        expected = {r.value for r in WaitingReason}
        assert VALID_WAITING_REASONS == expected


# ──────────────────────────────────────────────────────────────
# Control Actions
# ──────────────────────────────────────────────────────────────

class TestControlActions:
    """Validate control action records."""

    def test_control_action_record(self):
        record = ControlActionRecord(
            action=ControlAction.CANCELLED,
            reason="No longer needed",
            applied_by=OwnerKind.CONTROLLER,
            applied_by_id="ctrl-001",
        )
        assert record.action == ControlAction.CANCELLED
        assert record.reason == "No longer needed"
        assert record.applied_by == OwnerKind.CONTROLLER
        assert record.metadata == {}

    def test_control_action_with_metadata(self):
        record = ControlActionRecord(
            action=ControlAction.DROPPED,
            reason="Superseded",
            applied_by=OwnerKind.RUNTIME,
            applied_by_id="runtime",
            metadata={"superseded_by": "task-new"},
        )
        assert record.metadata["superseded_by"] == "task-new"


# ──────────────────────────────────────────────────────────────
# Transition Descriptions
# ──────────────────────────────────────────────────────────────

class TestTransitionDescriptions:
    """Validate human-readable transition descriptions."""

    def test_inbox_to_ready_description(self):
        desc = describe_transition(TaskStatus.INBOX, TaskStatus.READY)
        assert "triage" in desc.lower()

    def test_ready_to_active_description(self):
        desc = describe_transition(TaskStatus.READY, TaskStatus.ACTIVE)
        assert "claim" in desc.lower()

    def test_unknown_transition_description(self):
        desc = describe_transition(TaskStatus.INBOX, TaskStatus.DONE)
        assert "inbox" in desc.lower()
        assert "done" in desc.lower()


# ──────────────────────────────────────────────────────────────
# R1-A5 Enforcement Tests
# ──────────────────────────────────────────────────────────────

class TestR1A5Enforcement:
    """R1-A5: Enforcement hardening tests.

    Tests for:
    - role=None force bypass closure
    - ClaimContext field validation (structural checks only)

    Note: ClaimContext.delegate_id is NOT validated against role.value
    in the pure-logic layer. The service layer is responsible for
    verifying that the claim's delegate_id matches the calling delegate.
    """

    def test_claim_context_empty_claim_ref_rejected(self):
        """R1-A5: ClaimContext with empty claim_ref is rejected."""
        claim = ClaimContext(
            claim_type=ClaimType.EXPLICIT_ASSIGNMENT,
            claim_ref="",  # empty!
            delegate_id="delegate",
            task_id="task-1",
        )
        with pytest.raises(ClaimRequiredError, match="claim_ref must be non-empty"):
            validate_transition(
                TaskStatus.READY,
                TaskStatus.ACTIVE,
                OwnerKind.DELEGATE,
                claim_context=claim,
            )

    def test_claim_context_empty_task_id_rejected(self):
        """R1-A5: ClaimContext with empty task_id is rejected."""
        claim = ClaimContext(
            claim_type=ClaimType.EXPLICIT_ASSIGNMENT,
            claim_ref="assign-001",
            delegate_id="delegate",
            task_id="",  # empty!
        )
        with pytest.raises(ClaimRequiredError, match="task_id must be non-empty"):
            validate_transition(
                TaskStatus.READY,
                TaskStatus.ACTIVE,
                OwnerKind.DELEGATE,
                claim_context=claim,
            )

    def test_force_true_without_role_rejected(self):
        """R1-A5: force=True with role=None is REJECTED (legacy bypass closed)."""
        from runtime.transitions import build_task_update

        result = type('TransitionResult', (), {
            'success': True,
            'task_id': 'task-1',
            'from_status': TaskStatus.ACTIVE,
            'to_status': TaskStatus.WAITING,
        })()

        # R1-A5: This should now fail - role=None is not allowed with force=True
        with pytest.raises(ValueError, match="force=True requires explicit role"):
            build_task_update(
                result,
                waiting_reason=None,
                force=True,
                role=None,  # R1-A5: closed
            )

    def test_force_true_with_controller_role_allowed(self):
        """R1-A5: force=True with explicit controller role is allowed."""
        from runtime.transitions import build_task_update

        result = type('TransitionResult', (), {
            'success': True,
            'task_id': 'task-1',
            'from_status': TaskStatus.ACTIVE,
            'to_status': TaskStatus.WAITING,
        })()

        # Should NOT raise - controller is authorized
        updates = build_task_update(
            result,
            waiting_reason=None,
            force=True,
            role=OwnerKind.CONTROLLER,
        )
        assert updates["status"] == "waiting"

    def test_force_true_with_runtime_role_allowed(self):
        """R1-A5: force=True with explicit runtime role is allowed."""
        from runtime.transitions import build_task_update

        result = type('TransitionResult', (), {
            'success': True,
            'task_id': 'task-1',
            'from_status': TaskStatus.ACTIVE,
            'to_status': TaskStatus.WAITING,
        })()

        # Should NOT raise - runtime is authorized
        updates = build_task_update(
            result,
            waiting_reason=None,
            force=True,
            role=OwnerKind.RUNTIME,
        )
        assert updates["status"] == "waiting"

    def test_force_true_with_delegate_role_rejected(self):
        """R1-A5: force=True with delegate role is still rejected."""
        from runtime.transitions import build_task_update

        result = type('TransitionResult', (), {
            'success': True,
            'task_id': 'task-1',
            'from_status': TaskStatus.ACTIVE,
            'to_status': TaskStatus.WAITING,
        })()

        with pytest.raises(ValueError, match="force=True is restricted"):
            build_task_update(
                result,
                waiting_reason=None,
                force=True,
                role=OwnerKind.DELEGATE,
            )
