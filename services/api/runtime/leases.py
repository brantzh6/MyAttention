"""
IKE Runtime v0 – Worker Lease Semantics

Durable worker-lease claim, heartbeat, expiry, and recovery helpers.
No DB access. Callers persist returned dicts into runtime_worker_leases
and runtime_task_events.

R1-C1: This module also owns the ClaimVerifier adapter – the runtime-owned
truth rule for whether a delegate may claim or continue work on a task.
The ClaimVerifier is a protocol that the service layer implements to
perform Postgres-backed verification of delegate assignment and lease linkage.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from .state_machine import (
    TaskStatus,
    OwnerKind,
    ClaimContext,
    ClaimType,
)
from .events import (
    EventType,
    TaskEvent,
    make_event,
    make_lease_claimed_event,
    make_lease_expired_event,
    make_recovery_event,
)


# ──────────────────────────────────────────────────────────────
# Task-Type Lease Expiry Recovery Defaults
# ──────────────────────────────────────────────────────────────

# Per the design: when a lease expires, the task is recovered
# to this status depending on its type.
# Recovery must NOT silently finalize work as done.
TASK_TYPE_RECOVERY: dict[str, TaskStatus] = {
    "implementation": TaskStatus.WAITING,
    "review": TaskStatus.REVIEW_PENDING,
    "study": TaskStatus.FAILED,
    "daemon": TaskStatus.READY,
    "workflow": TaskStatus.WAITING,
    "maintenance": TaskStatus.READY,
}


def get_recovery_status(task_type: str) -> TaskStatus | None:
    """Get the recovery target status for a task type on lease expiry.

    Returns None if the task type has no defined recovery policy.
    """
    return TASK_TYPE_RECOVERY.get(task_type)


def get_all_task_types_with_recovery() -> set[str]:
    """Return all task types that have a recovery policy."""
    return set(TASK_TYPE_RECOVERY.keys())


# ──────────────────────────────────────────────────────────────
# R1-C1: ClaimVerifier – Runtime-Owned Truth Adapter
# ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ClaimVerificationResult:
    """Result of a runtime-owned claim verification.

    Fields:
        valid: Whether the claim is verified.
        claim_context: The structured claim context if valid.
        error: Error message if invalid.
    """
    valid: bool
    claim_context: ClaimContext | None = None
    error: str | None = None


class ClaimVerifier(ABC):
    """Abstract adapter for runtime-owned claim verification.

    The service layer implements this to verify delegate claims against
    Postgres-backed truth (assignment records, active leases).

    This is the runtime's truth rule for whether a delegate may claim
    or continue work on a task. It replaces the legacy pattern where
    the caller simply asserted `allow_claim=True`.

    Implementations must verify:
    1. The delegate_id matches the actual calling delegate's identity.
    2. For EXPLICIT_ASSIGNMENT: an assignment record exists linking
       the delegate to the task.
    3. For ACTIVE_LEASE: an active lease exists on the task owned by
       the delegate, and the claim_ref matches the lease_id.
    """

    @abstractmethod
    def verify_claim(
        self,
        claim_type: ClaimType,
        claim_ref: str,
        delegate_id: str,
        task_id: str,
    ) -> ClaimVerificationResult:
        """Verify a delegate's claim to work on a task.

        Args:
            claim_type: How the claim was made (assignment or lease).
            claim_ref: ID of the verifying object (assignment ID or lease ID).
            delegate_id: The delegate attempting the claim.
            task_id: The task being claimed.

        Returns:
            ClaimVerificationResult with validity status.
        """
        ...

    def verify_and_build_context(
        self,
        claim_type: ClaimType,
        claim_ref: str,
        delegate_id: str,
        task_id: str,
    ) -> ClaimVerificationResult:
        """Verify a claim and return a ready-to-use ClaimContext.

        Convenience method that calls verify_claim and, if valid,
        returns a ClaimContext suitable for validate_transition.
        """
        result = self.verify_claim(claim_type, claim_ref, delegate_id, task_id)
        if result.valid:
            return ClaimVerificationResult(
                valid=True,
                claim_context=ClaimContext(
                    claim_type=claim_type,
                    claim_ref=claim_ref,
                    delegate_id=delegate_id,
                    task_id=task_id,
                ),
            )
        return result


# ──────────────────────────────────────────────────────────────
# In-Memory ClaimVerifier for Testing
# ──────────────────────────────────────────────────────────────

class InMemoryClaimVerifier(ClaimVerifier):
    """In-memory ClaimVerifier for unit tests.

    Pre-register known-good delegate→task assignments and leases.
    Any unregistered claim fails.
    """

    def __init__(self) -> None:
        # {(delegate_id, task_id): set of claim_refs}
        self._assignments: dict[tuple[str, str], set[str]] = {}
        # {lease_id: (delegate_id, task_id)}
        self._leases: dict[str, tuple[str, str]] = {}

    def register_assignment(
        self, delegate_id: str, task_id: str, assignment_id: str
    ) -> None:
        """Register a known delegate→task assignment."""
        key = (delegate_id, task_id)
        self._assignments.setdefault(key, set()).add(assignment_id)

    def register_lease(
        self, lease_id: str, delegate_id: str, task_id: str
    ) -> None:
        """Register a known active lease."""
        self._leases[lease_id] = (delegate_id, task_id)

    def verify_claim(
        self,
        claim_type: ClaimType,
        claim_ref: str,
        delegate_id: str,
        task_id: str,
    ) -> ClaimVerificationResult:
        if claim_type == ClaimType.EXPLICIT_ASSIGNMENT:
            key = (delegate_id, task_id)
            if claim_ref in self._assignments.get(key, set()):
                return ClaimVerificationResult(valid=True)
            return ClaimVerificationResult(
                valid=False,
                error=f"No assignment record found for delegate={delegate_id}, "
                f"task={task_id}, assignment_id={claim_ref}",
            )
        elif claim_type == ClaimType.ACTIVE_LEASE:
            owner = self._leases.get(claim_ref)
            if owner == (delegate_id, task_id):
                return ClaimVerificationResult(valid=True)
            return ClaimVerificationResult(
                valid=False,
                error=f"No active lease found for lease_id={claim_ref}, "
                f"delegate={delegate_id}, task={task_id}",
            )
        return ClaimVerificationResult(
            valid=False,
            error=f"Unknown claim type: {claim_type}",
        )


# ──────────────────────────────────────────────────────────────
# Lease Record
# ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class LeaseRecord:
    """Immutable lease record for persistence.

    Matches the runtime_worker_leases table schema.
    """
    lease_id: str
    task_id: str
    owner_kind: str
    owner_id: str | None
    lease_status: str
    heartbeat_at: str | None
    expires_at: str
    created_at: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "lease_id": self.lease_id,
            "task_id": self.task_id,
            "owner_kind": self.owner_kind,
            "owner_id": self.owner_id,
            "lease_status": self.lease_status,
            "heartbeat_at": self.heartbeat_at,
            "expires_at": self.expires_at,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class LeaseClaimResult:
    """Result of a lease claim attempt."""
    success: bool
    lease: LeaseRecord | None = None
    event: TaskEvent | None = None
    error: str | None = None


@dataclass(frozen=True)
class LeaseExpiryResult:
    """Result of processing an expired lease."""
    success: bool
    task_id: str
    lease_id: str
    expired_event: TaskEvent | None = None
    recovery_event: TaskEvent | None = None
    recovery_status: TaskStatus | None = None
    task_update: dict[str, Any] | None = None
    error: str | None = None


# ──────────────────────────────────────────────────────────────
# Lease Operations
# ──────────────────────────────────────────────────────────────

def claim_lease(
    task_id: str,
    project_id: str,
    owner_kind: OwnerKind,
    owner_id: str,
    ttl_seconds: int = 3600,
    metadata: dict[str, Any] | None = None,
    created_at: datetime | None = None,
) -> LeaseClaimResult:
    """Create a new active lease for a task.

    The caller must verify the task is claimable (e.g., status is
    ready or active) before calling this function.

    Args:
        ttl_seconds: Lease time-to-live in seconds. Default 1 hour.
        metadata: Optional metadata dict.

    Returns:
        LeaseClaimResult with the new lease and event if successful.
    """
    now = created_at or datetime.now(timezone.utc)
    lease_id = str(uuid4())

    lease = LeaseRecord(
        lease_id=lease_id,
        task_id=task_id,
        owner_kind=owner_kind.value,
        owner_id=owner_id,
        lease_status="active",
        heartbeat_at=now.isoformat(),
        expires_at=(now + timedelta(seconds=ttl_seconds)).isoformat(),
        created_at=now.isoformat(),
        metadata=metadata or {},
    )

    event = make_lease_claimed_event(
        project_id=project_id,
        task_id=task_id,
        lease_id=lease_id,
        owner_kind=owner_kind,
        owner_id=owner_id,
        reason=f"Lease claimed by {owner_kind.value}:{owner_id}",
    )

    return LeaseClaimResult(success=True, lease=lease, event=event)


def heartbeat_lease(
    lease_id: str,
    task_id: str,
    project_id: str,
    owner_kind: OwnerKind,
    owner_id: str,
    heartbeat_at: datetime | None = None,
) -> TaskEvent:
    """Create a heartbeat event for an active lease.

    The caller must update the lease's heartbeat_at and expires_at
    in the database after recording this event.

    Returns:
        TaskEvent recording the heartbeat.
    """
    ts = heartbeat_at or datetime.now(timezone.utc)
    return make_event(
        project_id=project_id,
        task_id=task_id,
        event_type=EventType.LEASE_HEARTBEAT,
        triggered_by_kind=owner_kind,
        triggered_by_id=owner_id,
        reason=f"Heartbeat for lease {lease_id}",
        payload={"lease_id": lease_id, "heartbeat_at": ts.isoformat()},
        created_at=ts,
    )


def release_lease(
    lease_id: str,
    task_id: str,
    project_id: str,
    owner_kind: OwnerKind,
    owner_id: str,
    reason: str = "Lease released",
) -> TaskEvent:
    """Create a lease release event.

    The caller must update the lease status to 'released' in the DB.

    Returns:
        TaskEvent recording the release.
    """
    return make_event(
        project_id=project_id,
        task_id=task_id,
        event_type=EventType.LEASE_RELEASED,
        triggered_by_kind=owner_kind,
        triggered_by_id=owner_id,
        reason=reason,
        payload={"lease_id": lease_id},
    )


def expire_lease(
    lease_id: str,
    task_id: str,
    project_id: str,
    expired_owner_kind: str,
    expired_owner_id: str,
    task_type: str,
    reason: str = "Lease expired",
) -> LeaseExpiryResult:
    """Process an expired lease and produce recovery artifacts.

    This is the core recovery function. It:
    1. Records that the lease expired.
    2. Determines the recovery target status from the task type.
    3. Produces a recovery event for audit.
    4. Produces a task update dict for persistence.

    Recovery must NOT silently finalize work as done.
    The recovery target is determined by TASK_TYPE_RECOVERY.

    Args:
        task_type: The task_type value from runtime_tasks (e.g., "implementation").

    Returns:
        LeaseExpiryResult with events and task update dict.
        If task_type has no recovery policy, returns error.
    """
    recovery_status = get_recovery_status(task_type)
    if recovery_status is None:
        return LeaseExpiryResult(
            success=False,
            task_id=task_id,
            lease_id=lease_id,
            error=f"No recovery policy defined for task_type '{task_type}'",
        )

    # 1. Record lease expiry
    expired_event = make_lease_expired_event(
        project_id=project_id,
        task_id=task_id,
        lease_id=lease_id,
        expired_owner_kind=expired_owner_kind,
        expired_owner_id=expired_owner_id,
        reason=reason,
    )

    # 2. Record recovery event
    recovery_event = make_recovery_event(
        project_id=project_id,
        task_id=task_id,
        from_status=TaskStatus.ACTIVE,
        to_status=recovery_status,
        task_type=task_type,
        reason=f"Recovery from lease expiry: {task_type} -> {recovery_status.value}",
        lease_id=lease_id,
    )

    # 3. Build task update dict
    task_update: dict[str, Any] = {
        "status": recovery_status.value,
        "current_lease_id": None,  # clear the expired lease pointer
        "updated_at": datetime.now(timezone.utc),
    }

    # For implementation/workflow tasks going to WAITING, set waiting_reason
    if recovery_status == TaskStatus.WAITING:
        task_update["waiting_reason"] = "delegate_result"
        task_update["waiting_detail"] = (
            f"Worker ({expired_owner_kind}:{expired_owner_id}) lease expired. "
            f"Task recovered to waiting for reassignment."
        )

    return LeaseExpiryResult(
        success=True,
        task_id=task_id,
        lease_id=lease_id,
        expired_event=expired_event,
        recovery_event=recovery_event,
        recovery_status=recovery_status,
        task_update=task_update,
    )


def recover_stale_active_task(
    task_id: str,
    project_id: str,
    task_type: str,
    expired_lease_id: str | None = None,
    reason: str = "Stale active task detected",
) -> LeaseExpiryResult:
    """Recover a task stuck in active with no valid lease.

    This handles the case where a task is in 'active' state but has
    no corresponding active lease (e.g., lease was deleted or DB
    inconsistency). Uses the same recovery policy as lease expiry.

    Returns:
        LeaseExpiryResult with recovery event and task update.
    """
    recovery_status = get_recovery_status(task_type)
    if recovery_status is None:
        return LeaseExpiryResult(
            success=False,
            task_id=task_id,
            lease_id=expired_lease_id or "unknown",
            error=f"No recovery policy defined for task_type '{task_type}'",
        )

    payload: dict[str, Any] = {
        "recovery": True,
        "recovery_type": "stale_active",
        "task_type": task_type,
        "from_status": "active",
        "to_status": recovery_status.value,
    }
    if expired_lease_id:
        payload["lease_id"] = expired_lease_id

    recovery_event = make_event(
        project_id=project_id,
        task_id=task_id,
        event_type=EventType.RECOVERY_STALE_ACTIVE,
        from_status=TaskStatus.ACTIVE,
        to_status=recovery_status,
        triggered_by_kind=OwnerKind.RUNTIME,
        triggered_by_id="runtime",
        reason=reason,
        payload=payload,
    )

    task_update: dict[str, Any] = {
        "status": recovery_status.value,
        "current_lease_id": None,
        "updated_at": datetime.now(timezone.utc),
    }

    if recovery_status == TaskStatus.WAITING:
        task_update["waiting_reason"] = "delegate_result"
        task_update["waiting_detail"] = reason

    return LeaseExpiryResult(
        success=True,
        task_id=task_id,
        lease_id=expired_lease_id or "unknown",
        expired_event=None,
        recovery_event=recovery_event,
        recovery_status=recovery_status,
        task_update=task_update,
    )


# ──────────────────────────────────────────────────────────────
# Lease Update Helpers
# ──────────────────────────────────────────────────────────────

def build_lease_heartbeat_update(
    extends_seconds: int = 3600,
    heartbeat_at: datetime | None = None,
) -> dict[str, Any]:
    """Build DB update dict for refreshing a lease heartbeat.

    Returns:
        Dict with new heartbeat_at and extended expires_at.
    """
    now = heartbeat_at or datetime.now(timezone.utc)
    return {
        "heartbeat_at": now.isoformat(),
        "expires_at": (now + timedelta(seconds=extends_seconds)).isoformat(),
    }


def build_lease_release_update(
    released_at: datetime | None = None,
) -> dict[str, Any]:
    """Build DB update dict for releasing a lease."""
    return {
        "lease_status": "released",
        "heartbeat_at": (released_at or datetime.now(timezone.utc)).isoformat(),
    }


def build_lease_expired_update(
    expired_at: datetime | None = None,
) -> dict[str, Any]:
    """Build DB update dict for marking a lease as expired."""
    return {
        "lease_status": "expired",
        "heartbeat_at": (expired_at or datetime.now(timezone.utc)).isoformat(),
    }
