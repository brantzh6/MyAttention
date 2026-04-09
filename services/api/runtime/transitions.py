"""
IKE Runtime v0 – Transition Execution

Orchestrates state transitions with validation, event recording,
and role-based guardrails. Integrates with the ORM models but does
not depend on any external service or API layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from .state_machine import (
    OwnerKind,
    TaskStatus,
    ClaimContext,
    validate_transition,
    TransitionError,
    InvalidTransitionError,
    RolePermissionError,
    GuardrailViolationError,
    ClaimRequiredError,
    ControlAction,
    ControlActionRecord,
    describe_transition,
    validate_waiting_reason,
    VALID_WAITING_REASONS,
)

# Roles authorized to use force=True as an escape hatch.
# Delegates must NOT bypass core transition rules via force.
FORCE_AUTHORIZED_ROLES: set[OwnerKind] = {
    OwnerKind.CONTROLLER,
    OwnerKind.RUNTIME,
}


@dataclass
class TransitionRequest:
    """Request to transition a task from one state to another."""
    task_id: str
    project_id: str
    from_status: TaskStatus
    to_status: TaskStatus
    role: OwnerKind
    role_id: str
    reason: str = ""
    allow_runtime_policy: bool = False
    allow_controller_gate: bool = False
    claim_context: ClaimContext | None = None
    extra_payload: dict = field(default_factory=dict)


@dataclass
class TransitionResult:
    """Result of a state transition attempt."""
    success: bool
    task_id: str
    from_status: TaskStatus
    to_status: TaskStatus
    event_type: str = ""
    event_reason: str = ""
    error: Optional[str] = None


def execute_transition(request: TransitionRequest) -> TransitionResult:
    """Execute a state transition with full validation.

    This is the primary entry point for transitioning tasks.
    It validates the transition against the v0 state machine and
    role permissions before producing a result.

    For CLAIM_REQUIRED transitions (e.g., delegate ready->active),
    the request must include a `claim_context` with verified claim proof.
    The legacy `allow_claim` flag has been removed (R1-C1 hardening).

    The caller is responsible for persisting the result:
    - Update runtime_tasks.status, updated_at, and any changed fields
    - Append a runtime_task_events row
    - Optionally write a runtime_outbox_events row for side effects

    Returns:
        TransitionResult with success=True and metadata if valid.
        TransitionResult with success=False and error message if invalid.
    """
    try:
        validate_transition(
            request.from_status,
            request.to_status,
            request.role,
            allow_runtime_policy=request.allow_runtime_policy,
            allow_controller_gate=request.allow_controller_gate,
            claim_context=request.claim_context,
        )
    except TransitionError as e:
        return TransitionResult(
            success=False,
            task_id=request.task_id,
            from_status=request.from_status,
            to_status=request.to_status,
            error=str(e),
        )

    return TransitionResult(
        success=True,
        task_id=request.task_id,
        from_status=request.from_status,
        to_status=request.to_status,
        event_type="state_transition",
        event_reason=request.reason or describe_transition(
            request.from_status, request.to_status
        ),
    )


def record_control_action(
    task_id: str,
    project_id: str,
    action: ControlAction,
    role: OwnerKind,
    role_id: str,
    reason: str,
    current_status: TaskStatus,
    extra_payload: dict | None = None,
) -> dict:
    """Record a control action (cancelled, dropped, deprioritized) as an event.

    Control actions do NOT change the durable task state.
    They produce an event with the action encoded in the payload/reason.

    The caller should:
    - Append a runtime_task_events row with event_type="control_action"
    - Optionally update task metadata with closure note
    - Optionally emit outbox event for notification

    Returns:
        Event record dict suitable for persistence.
    """
    return {
        "event_id": str(uuid4()),
        "project_id": project_id,
        "task_id": task_id,
        "event_type": "control_action",
        "from_status": current_status.value,
        "to_status": current_status.value,  # state does not change
        "triggered_by_kind": role.value,
        "triggered_by_id": role_id,
        "reason": reason,
        "payload": {
            "action": action.value,
            "control_action": True,
            **(extra_payload or {}),
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def build_event_record(
    result: TransitionResult,
    project_id: str,
    triggered_by_kind: OwnerKind,
    triggered_by_id: str,
    extra_payload: dict | None = None,
) -> dict:
    """Build an event record dict for persistence.

    Given a successful TransitionResult, produce a dict matching the
    runtime_task_events table schema.
    """
    if not result.success:
        raise ValueError("Cannot build event record for failed transition")

    return {
        "event_id": str(uuid4()),
        "project_id": project_id,
        "task_id": result.task_id,
        "event_type": result.event_type,
        "from_status": result.from_status.value,
        "to_status": result.to_status.value,
        "triggered_by_kind": triggered_by_kind.value,
        "triggered_by_id": triggered_by_id,
        "reason": result.event_reason,
        "payload": extra_payload or {},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def build_task_update(
    result: TransitionResult,
    waiting_reason: str | None = None,
    waiting_detail: str | None = None,
    result_summary: str | None = None,
    next_action_summary: str | None = None,
    current_lease_id: str | None = None,
    force: bool = False,
    role: OwnerKind | None = None,
) -> dict:
    """Build a task update dict for persistence after a successful transition.

    For transitions to WAITING, a valid waiting_reason is REQUIRED.
    Without it, a ValueError is raised (unless force=True is set by an
    authorized role – controller or runtime only).

    This prevents semantically incomplete waiting updates from reaching
    the database, which would violate the CHECK constraint requiring
    waiting_reason when status='waiting'.

    R1-A1 HARDENING: force=True is restricted to controller and runtime roles.
    Delegates cannot bypass core transition rules via the force escape hatch.

    R1-A5 ENFORCEMENT: role=None with force=True is REJECTED. The legacy
    bypass path is closed – role must be explicitly provided when force=True.

    Args:
        result: Successful TransitionResult.
        waiting_reason: Must be a valid v0 waiting reason for WAITING transitions.
        waiting_detail: Free-text explanation for the wait condition.
        result_summary: Set when transitioning to DONE or FAILED.
        next_action_summary: Optional next action text.
        current_lease_id: Lease ID to attach when entering ACTIVE.
        force: If True, skip waiting_reason validation. Restricted to
            controller and runtime roles only (R1-A1 hardening).
        role: The role attempting the transition. REQUIRED when force=True.
            R1-A5: legacy role=None bypass is closed.

    Returns:
        Dict of column updates for runtime_tasks.

    Raises:
        ValueError: If transitioning to WAITING without a valid waiting_reason,
            if force=True is used by an unauthorized role, or if force=True
            is used without providing role (R1-A5 enforcement).
    """
    if not result.success:
        raise ValueError("Cannot build task update for failed transition")

    updates: dict = {
        "status": result.to_status.value,
        "updated_at": datetime.now(timezone.utc),
    }

    # R1-A5 ENFORCEMENT: role=None with force=True is REJECTED.
    # The legacy bypass path is closed – role must be explicitly provided.
    if force and role is None:
        raise ValueError(
            "force=True requires explicit role parameter. "
            "Legacy role=None bypass is closed (R1-A5 enforcement). "
            "Provide role=OwnerKind.CONTROLLER or role=OwnerKind.RUNTIME if "
            "force=True is required, or provide a valid waiting_reason instead."
        )

    # R1-A1 HARDENING: force=True restricted to controller/runtime only.
    # Delegates must not bypass core transition rules via force.
    if force and role not in FORCE_AUTHORIZED_ROLES:
        raise ValueError(
            f"force=True is restricted to controller and runtime roles. "
            f"Role '{role.value}' is not authorized to bypass transition rules. "
            f"Provide a valid waiting_reason for WAITING transitions instead."
        )

    # When transitioning to WAITING, waiting_reason is REQUIRED
    if result.to_status == TaskStatus.WAITING:
        # R1-A5: role is always provided when force=True (see check above)
        effective_force = force and role in FORCE_AUTHORIZED_ROLES
        if not effective_force:
            if not validate_waiting_reason(waiting_reason):
                raise ValueError(
                    f"Transition to WAITING requires a valid waiting_reason. "
                    f"Got: {waiting_reason!r}. "
                    f"Valid reasons: {sorted(VALID_WAITING_REASONS)}"
                )
        updates["waiting_reason"] = waiting_reason
        if waiting_detail:
            updates["waiting_detail"] = waiting_detail
    else:
        # Clear waiting fields when leaving WAITING
        updates["waiting_reason"] = None
        updates["waiting_detail"] = None

    # When transitioning to DONE, set result_summary
    if result.to_status == TaskStatus.DONE:
        if result_summary:
            updates["result_summary"] = result_summary
        updates["ended_at"] = datetime.now(timezone.utc)

    # When transitioning to FAILED
    if result.to_status == TaskStatus.FAILED:
        if result_summary:
            updates["result_summary"] = result_summary
        updates["ended_at"] = datetime.now(timezone.utc)

    # When transitioning to ACTIVE from non-ACTIVE
    if result.to_status == TaskStatus.ACTIVE and result.from_status != TaskStatus.ACTIVE:
        updates["started_at"] = datetime.now(timezone.utc)
        if current_lease_id:
            updates["current_lease_id"] = current_lease_id

    # Update next_action_summary if provided
    if next_action_summary is not None:
        updates["next_action_summary"] = next_action_summary

    return updates
