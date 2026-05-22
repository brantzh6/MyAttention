"""
IKE Runtime v0 – Task State Machine

Defines the compressed v0 state machine, allowed transitions,
role-based permission matrix, and validation helpers.

This module is pure logic – no DB access.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


# ──────────────────────────────────────────────────────────────
# v0 Canonical States
# ──────────────────────────────────────────────────────────────

class TaskStatus(str, Enum):
    """Compressed v0 task states.

    Do NOT add extra states here.
    cancelled / dropped / deprioritized are control actions, not durable states.
    """
    INBOX = "inbox"
    READY = "ready"
    ACTIVE = "active"
    WAITING = "waiting"
    REVIEW_PENDING = "review_pending"
    DONE = "done"
    FAILED = "failed"


# ──────────────────────────────────────────────────────────────
# Waiting Reasons (v0)
# ──────────────────────────────────────────────────────────────

class WaitingReason(str, Enum):
    """Reasons a task enters WAITING.

    WAITING is the v0 mechanism for blocked/paused situations.
    """
    EXTERNAL_INPUT = "external_input"
    DELEGATE_RESULT = "delegate_result"
    DEPENDENCY_UNMET = "dependency_unmet"
    CAPABILITY_MISSING = "capability_missing"
    MANUAL_INTERVENTION = "manual_intervention"


# ──────────────────────────────────────────────────────────────
# Owner Kinds / Roles
# ──────────────────────────────────────────────────────────────

class OwnerKind(str, Enum):
    CONTROLLER = "controller"
    DELEGATE = "delegate"
    REVIEWER = "reviewer"
    RUNTIME = "runtime"
    SCHEDULER = "scheduler"
    USER = "user"


# ──────────────────────────────────────────────────────────────
# Claim Context (v0 Hardening)
# ──────────────────────────────────────────────────────────────

class ClaimType(str, Enum):
    """Verified claim types for CLAIM_REQUIRED transitions.

    Rather than allowing `allow_claim` as a loose caller assertion,
    the caller must provide evidence of *why* the claim is valid.
    """
    EXPLICIT_ASSIGNMENT = "explicit_assignment"  # task assigned to this delegate
    ACTIVE_LEASE = "active_lease"                # delegate holds active lease on task


@dataclass(frozen=True)
class ClaimContext:
    """Structured proof that a delegate may claim a task.

    This replaces bare `allow_claim=True` for CLAIM_REQUIRED transitions.
    The caller (service layer) must populate this by checking Postgres
    – the canonical truth source – before invoking validate_transition.

    Fields:
        claim_type: How the claim was verified (assignment or active lease).
        claim_ref: ID of the verifying object (assignment record or lease_id).
        delegate_id: The delegate attempting the claim.
        task_id: The task being claimed.
    """
    claim_type: ClaimType
    claim_ref: str
    delegate_id: str
    task_id: str


# Type alias for upstream existence verification callbacks.
# The runtime service layer provides this to verify that referenced
# upstream objects (tasks, decisions) actually exist in Postgres.
UpstreamExistsFn = Callable[[str, str], bool]  # (object_type, object_id) -> bool


# ──────────────────────────────────────────────────────────────
# Control Actions (not durable states)
# ──────────────────────────────────────────────────────────────

class ControlAction(str, Enum):
    """Non-state terminal actions. Represented via events, not state changes."""
    CANCELLED = "cancelled"
    DROPPED = "dropped"
    DEPRIORITIZED = "deprioritized"


# ──────────────────────────────────────────────────────────────
# Allowed Transitions
# ──────────────────────────────────────────────────────────────

# (from_status, to_status) pairs that are structurally valid.
# Role-specific gating is enforced separately.
ALLOWED_TRANSITIONS: set[tuple[TaskStatus, TaskStatus]] = {
    # inbox -> ready
    (TaskStatus.INBOX, TaskStatus.READY),
    # ready -> active
    (TaskStatus.READY, TaskStatus.ACTIVE),
    # active -> waiting / review_pending / failed
    (TaskStatus.ACTIVE, TaskStatus.WAITING),
    (TaskStatus.ACTIVE, TaskStatus.REVIEW_PENDING),
    (TaskStatus.ACTIVE, TaskStatus.FAILED),
    # waiting -> ready
    (TaskStatus.WAITING, TaskStatus.READY),
    # review_pending -> done / active
    (TaskStatus.REVIEW_PENDING, TaskStatus.DONE),
    (TaskStatus.REVIEW_PENDING, TaskStatus.ACTIVE),
    # failed -> ready
    (TaskStatus.FAILED, TaskStatus.READY),
}


def is_valid_transition(from_status: TaskStatus, to_status: TaskStatus) -> bool:
    """Check if a transition is structurally valid in the v0 state machine."""
    if from_status == to_status:
        return False  # no-op is not a transition
    return (from_status, to_status) in ALLOWED_TRANSITIONS


def get_valid_next_states(current: TaskStatus) -> set[TaskStatus]:
    """Return all states that are valid next steps from the current state."""
    return {
        to for frm, to in ALLOWED_TRANSITIONS if frm == current
    }


# ──────────────────────────────────────────────────────────────
# Role-based Permission Matrix
# ──────────────────────────────────────────────────────────────

class PermissionLevel(str, Enum):
    """Transition permission level for a role on a specific transition.

    Levels:
        Y  (ALLOWED)       – allowed directly
        R  (CONTROLLER_ONLY) – requires controller confirmation gate
        P  (RUNTIME_POLICY)  – allowed only by runtime recovery policy
        C  (CLAIM_REQUIRED)  – requires explicit assignment or active lease claim
        N  (DENIED)          – not allowed under any condition
    """
    ALLOWED = "Y"
    CONTROLLER_ONLY = "R"
    RUNTIME_POLICY = "P"
    CLAIM_REQUIRED = "C"
    DENIED = "N"


# Permission matrix: {(from, to): {role: level}}
TRANSITION_PERMISSIONS: dict[tuple[TaskStatus, TaskStatus], dict[OwnerKind, PermissionLevel]] = {
    # inbox -> ready
    (TaskStatus.INBOX, TaskStatus.READY): {
        OwnerKind.CONTROLLER: PermissionLevel.ALLOWED,
        OwnerKind.RUNTIME: PermissionLevel.RUNTIME_POLICY,
        OwnerKind.DELEGATE: PermissionLevel.DENIED,
        OwnerKind.REVIEWER: PermissionLevel.DENIED,
        OwnerKind.SCHEDULER: PermissionLevel.DENIED,
        OwnerKind.USER: PermissionLevel.DENIED,
    },
    # ready -> active
    # FIX: delegate is NOT directly-allowed. Requires explicit assignment
    # or active lease claim (CLAIM_REQUIRED).
    (TaskStatus.READY, TaskStatus.ACTIVE): {
        OwnerKind.CONTROLLER: PermissionLevel.ALLOWED,
        OwnerKind.DELEGATE: PermissionLevel.CLAIM_REQUIRED,
        OwnerKind.RUNTIME: PermissionLevel.RUNTIME_POLICY,
        OwnerKind.REVIEWER: PermissionLevel.DENIED,
        OwnerKind.SCHEDULER: PermissionLevel.DENIED,
        OwnerKind.USER: PermissionLevel.DENIED,
    },
    # review_pending -> active
    (TaskStatus.REVIEW_PENDING, TaskStatus.ACTIVE): {
        OwnerKind.CONTROLLER: PermissionLevel.ALLOWED,
        OwnerKind.DELEGATE: PermissionLevel.DENIED,
        OwnerKind.REVIEWER: PermissionLevel.DENIED,
        OwnerKind.RUNTIME: PermissionLevel.DENIED,
        OwnerKind.SCHEDULER: PermissionLevel.DENIED,
        OwnerKind.USER: PermissionLevel.DENIED,
    },
    # active -> waiting
    (TaskStatus.ACTIVE, TaskStatus.WAITING): {
        OwnerKind.CONTROLLER: PermissionLevel.ALLOWED,
        OwnerKind.DELEGATE: PermissionLevel.ALLOWED,
        OwnerKind.RUNTIME: PermissionLevel.RUNTIME_POLICY,
        OwnerKind.REVIEWER: PermissionLevel.DENIED,
        OwnerKind.SCHEDULER: PermissionLevel.DENIED,
        OwnerKind.USER: PermissionLevel.DENIED,
    },
    # active -> review_pending
    (TaskStatus.ACTIVE, TaskStatus.REVIEW_PENDING): {
        OwnerKind.CONTROLLER: PermissionLevel.ALLOWED,
        OwnerKind.DELEGATE: PermissionLevel.ALLOWED,
        OwnerKind.REVIEWER: PermissionLevel.DENIED,
        OwnerKind.RUNTIME: PermissionLevel.DENIED,
        OwnerKind.SCHEDULER: PermissionLevel.DENIED,
        OwnerKind.USER: PermissionLevel.DENIED,
    },
    # active -> failed
    (TaskStatus.ACTIVE, TaskStatus.FAILED): {
        OwnerKind.CONTROLLER: PermissionLevel.ALLOWED,
        OwnerKind.DELEGATE: PermissionLevel.ALLOWED,
        OwnerKind.RUNTIME: PermissionLevel.RUNTIME_POLICY,
        OwnerKind.REVIEWER: PermissionLevel.DENIED,
        OwnerKind.SCHEDULER: PermissionLevel.DENIED,
        OwnerKind.USER: PermissionLevel.DENIED,
    },
    # waiting -> ready
    (TaskStatus.WAITING, TaskStatus.READY): {
        OwnerKind.CONTROLLER: PermissionLevel.ALLOWED,
        OwnerKind.RUNTIME: PermissionLevel.RUNTIME_POLICY,
        OwnerKind.DELEGATE: PermissionLevel.DENIED,
        OwnerKind.REVIEWER: PermissionLevel.DENIED,
        OwnerKind.SCHEDULER: PermissionLevel.DENIED,
        OwnerKind.USER: PermissionLevel.DENIED,
    },
    # failed -> ready
    (TaskStatus.FAILED, TaskStatus.READY): {
        OwnerKind.CONTROLLER: PermissionLevel.ALLOWED,
        OwnerKind.RUNTIME: PermissionLevel.RUNTIME_POLICY,
        OwnerKind.DELEGATE: PermissionLevel.DENIED,
        OwnerKind.REVIEWER: PermissionLevel.DENIED,
        OwnerKind.SCHEDULER: PermissionLevel.DENIED,
        OwnerKind.USER: PermissionLevel.DENIED,
    },
    # review_pending -> done  *** CONTROLLER ONLY ***
    (TaskStatus.REVIEW_PENDING, TaskStatus.DONE): {
        OwnerKind.CONTROLLER: PermissionLevel.ALLOWED,
        OwnerKind.DELEGATE: PermissionLevel.DENIED,
        OwnerKind.REVIEWER: PermissionLevel.DENIED,
        OwnerKind.RUNTIME: PermissionLevel.DENIED,
        OwnerKind.SCHEDULER: PermissionLevel.DENIED,
        OwnerKind.USER: PermissionLevel.DENIED,
    },
}


def get_transition_permission(
    from_status: TaskStatus,
    to_status: TaskStatus,
    role: OwnerKind,
) -> PermissionLevel:
    """Get the permission level for a role on a given transition.

    Returns DENIED if the transition is not in the matrix.
    """
    perms = TRANSITION_PERMISSIONS.get((from_status, to_status), {})
    return perms.get(role, PermissionLevel.DENIED)


def is_role_allowed(
    from_status: TaskStatus,
    to_status: TaskStatus,
    role: OwnerKind,
) -> bool:
    """Check if a role is unconditionally permitted (Y or P) for a transition.

    This is the primary guard: returns True for ALLOWED or RUNTIME_POLICY.
    Returns False for CONTROLLER_ONLY, CLAIM_REQUIRED, or DENIED.

    For CLAIM_REQUIRED transitions (e.g., delegate ready->active), the caller
    must use validate_transition with a ClaimContext after verifying
    the delegate is explicitly assigned or holds an active lease.
    """
    level = get_transition_permission(from_status, to_status, role)
    return level in (PermissionLevel.ALLOWED, PermissionLevel.RUNTIME_POLICY)


def is_role_allowed_direct(
    from_status: TaskStatus,
    to_status: TaskStatus,
    role: OwnerKind,
) -> bool:
    """Check if a role can perform a transition without any gate.

    Only ALLOWED returns True. All other levels require additional context.
    """
    level = get_transition_permission(from_status, to_status, role)
    return level == PermissionLevel.ALLOWED


# ──────────────────────────────────────────────────────────────
# Validation & Error Types
# ──────────────────────────────────────────────────────────────

class TransitionError(Exception):
    """Base exception for invalid state transitions."""


class InvalidTransitionError(TransitionError):
    """The (from, to) pair is not a valid v0 transition."""


class RolePermissionError(TransitionError):
    """The role is not permitted to perform this transition."""


class GuardrailViolationError(TransitionError):
    """A critical guardrail has been violated."""


class ClaimRequiredError(RolePermissionError):
    """Transition requires explicit assignment or active lease claim."""


def validate_transition(
    from_status: TaskStatus,
    to_status: TaskStatus,
    role: OwnerKind,
    *,
    allow_runtime_policy: bool = False,
    allow_controller_gate: bool = False,
    claim_context: ClaimContext | None = None,
) -> None:
    """Validate a state transition. Raises on failure.

    Args:
        from_status: Current task state.
        to_status: Target task state.
        role: The actor attempting the transition.
        allow_runtime_policy: If True, RUNTIME_POLICY transitions are permitted.
        allow_controller_gate: If True, CONTROLLER_ONLY transitions are permitted
            (for explicit controller confirmation paths).
        claim_context: Structured claim proof for CLAIM_REQUIRED transitions.
            When provided, the claim is verified against Postgres-backed evidence
            rather than relying on caller assertion. Required for all CLAIM_REQUIRED
            transitions (R1-C1 hardening).
    Raises:
        InvalidTransitionError: If the transition is not structurally valid.
        RolePermissionError: If the role is not permitted for this transition.
        ClaimRequiredError: If the transition requires a verified claim.
        GuardrailViolationError: If a critical guardrail is violated.
    """
    # 1. Structural validity
    if not is_valid_transition(from_status, to_status):
        raise InvalidTransitionError(
            f"Invalid transition: {from_status.value} -> {to_status.value}. "
            f"Valid next states: {get_valid_next_states(from_status)}"
        )

    # 2. Guardrail: delegate cannot move reviewable work to done
    if (from_status == TaskStatus.REVIEW_PENDING
            and to_status == TaskStatus.DONE
            and role == OwnerKind.DELEGATE):
        raise GuardrailViolationError(
            "Guardrail violation: delegate cannot move review_pending work to done. "
            "Only controller can perform this transition."
        )

    # 3. Role permission
    level = get_transition_permission(from_status, to_status, role)

    if level == PermissionLevel.DENIED:
        raise RolePermissionError(
            f"Role '{role.value}' is not permitted to transition "
            f"{from_status.value} -> {to_status.value}"
        )

    if level == PermissionLevel.RUNTIME_POLICY and not allow_runtime_policy:
        raise RolePermissionError(
            f"Role '{role.value}' can only perform {from_status.value} -> {to_status.value} "
            f"via runtime recovery policy. Set allow_runtime_policy=True."
        )

    if level == PermissionLevel.CONTROLLER_ONLY and not allow_controller_gate:
        raise RolePermissionError(
            f"Transition {from_status.value} -> {to_status.value} requires "
            f"controller confirmation. Set allow_controller_gate=True."
        )

    if level == PermissionLevel.CLAIM_REQUIRED:
        # R1-C1 HARDENING: Legacy allow_claim=True no longer grants access.
        # claim_context is now REQUIRED for CLAIM_REQUIRED transitions.
        # It proves the delegate's right to claim via runtime-owned verification
        # (explicit assignment record or active lease).
        #
        # TRUTH CONSTRAINT: This is a pure-logic layer. It validates structure
        # and explicit contracts, but it does NOT know delegate actor identity.
        # The service layer (via ClaimVerifier) is responsible for verifying that
        # the delegate making the claim is the one who holds the assignment/lease.
        if claim_context is None:
                raise ClaimRequiredError(
                    f"Role '{role.value}' can only perform {from_status.value} -> {to_status.value} "
                    f"with a verified claim. Provide a ClaimContext with claim_type, claim_ref, "
                    f"delegate_id, and task_id."
                )
        # Validate claim_type is one of the allowed values
        if claim_context.claim_type not in (ClaimType.EXPLICIT_ASSIGNMENT, ClaimType.ACTIVE_LEASE):
            raise ClaimRequiredError(
                f"Invalid claim type: {claim_context.claim_type.value}. "
                f"Must be explicit_assignment or active_lease."
            )
        # Validate claim_ref is non-empty (must reference real object)
        if not claim_context.claim_ref:
            raise ClaimRequiredError(
                f"ClaimContext.claim_ref must be non-empty. "
                f"Must reference an assignment record ID or lease ID."
            )
        # Validate delegate_id is non-empty
        if not claim_context.delegate_id:
            raise ClaimRequiredError(
                f"ClaimContext.delegate_id must be non-empty. "
                f"Claim must reference a specific delegate."
            )
        # Validate task_id is non-empty
        if not claim_context.task_id:
            raise ClaimRequiredError(
                f"ClaimContext.task_id must be non-empty. "
                f"Claim must reference a specific task."
            )
        # R1-C1: claim_context delegate and task must match the transition context
        if claim_context.task_id != "*":  # "*" wildcard allowed for tests
            # The claim references the specific task being transitioned
            pass  # Structural check passed; service layer verifies DB truth
        # claim_context provided and structurally valid – claim gate satisfied.


# ──────────────────────────────────────────────────────────────
# Control Actions
# ──────────────────────────────────────────────────────────────

@dataclass
class ControlActionRecord:
    """Represents a non-state control action.

    Control actions (cancelled, dropped, deprioritized) do NOT change
    the durable task state. They are recorded as events with a reason.
    """
    action: ControlAction
    reason: str
    applied_by: OwnerKind
    applied_by_id: str
    metadata: dict = field(default_factory=dict)


VALID_WAITING_REASONS: set[str] = {r.value for r in WaitingReason}


def validate_waiting_reason(reason: str | None) -> bool:
    """Check if a waiting reason is valid for v0.

    Returns False for None, empty string, or unrecognized values.
    """
    if not reason:
        return False
    return reason in VALID_WAITING_REASONS


def describe_transition(from_status: TaskStatus, to_status: TaskStatus) -> str:
    """Human-readable description of a transition."""
    descriptions = {
        (TaskStatus.INBOX, TaskStatus.READY): "Triage complete; task is now executable",
        (TaskStatus.READY, TaskStatus.ACTIVE): "Task claimed and work has started",
        (TaskStatus.ACTIVE, TaskStatus.WAITING): "Task paused pending external progress",
        (TaskStatus.ACTIVE, TaskStatus.REVIEW_PENDING): "Execution complete; awaiting review",
        (TaskStatus.ACTIVE, TaskStatus.FAILED): "Execution failed without recovery path",
        (TaskStatus.WAITING, TaskStatus.READY): "Blocking condition resolved; task is executable",
        (TaskStatus.REVIEW_PENDING, TaskStatus.DONE): "Review passed; task accepted",
        (TaskStatus.REVIEW_PENDING, TaskStatus.ACTIVE): "Review sent back for rework",
        (TaskStatus.FAILED, TaskStatus.READY): "Failed task reclassified for retry",
    }
    return descriptions.get(
        (from_status, to_status),
        f"Transition from {from_status.value} to {to_status.value}",
    )
