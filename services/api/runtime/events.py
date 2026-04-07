"""
IKE Runtime v0 – Append-Only Event Log

Pure-logic helpers for building and recording runtime task events.
No DB access. Callers persist the returned dicts into runtime_task_events.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .state_machine import (
    TaskStatus,
    OwnerKind,
    WaitingReason,
)


# ──────────────────────────────────────────────────────────────
# Event Types
# ──────────────────────────────────────────────────────────────

class EventType:
    """Canonical event types for the append-only event log."""

    # State changes
    STATE_TRANSITION = "state_transition"

    # Lease events
    LEASE_CLAIMED = "lease_claimed"
    LEASE_HEARTBEAT = "lease_heartbeat"
    LEASE_RELEASED = "lease_released"
    LEASE_EXPIRED = "lease_expired"

    # Recovery events
    RECOVERY_LEASE_EXPIRY = "recovery_lease_expiry"
    RECOVERY_STALE_ACTIVE = "recovery_stale_active"

    # Control actions (non-state)
    CONTROL_ACTION = "control_action"

    # Lifecycle
    TASK_CREATED = "task_created"
    CHECKPOINT_SAVED = "checkpoint_saved"


# ──────────────────────────────────────────────────────────────
# Event Record
# ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TaskEvent:
    """Immutable, append-only event record.

    Matches the runtime_task_events table schema.
    """
    event_id: str
    project_id: str
    task_id: str
    event_type: str
    from_status: str | None
    to_status: str | None
    triggered_by_kind: str
    triggered_by_id: str
    reason: str
    payload: dict[str, Any]
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for persistence."""
        return {
            "event_id": self.event_id,
            "project_id": self.project_id,
            "task_id": self.task_id,
            "event_type": self.event_type,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "triggered_by_kind": self.triggered_by_kind,
            "triggered_by_id": self.triggered_by_id,
            "reason": self.reason,
            "payload": self.payload,
            "created_at": self.created_at,
        }


def make_event(
    project_id: str,
    task_id: str,
    event_type: str,
    triggered_by_kind: OwnerKind,
    triggered_by_id: str,
    reason: str,
    from_status: TaskStatus | str | None = None,
    to_status: TaskStatus | str | None = None,
    payload: dict[str, Any] | None = None,
    created_at: datetime | None = None,
) -> TaskEvent:
    """Create an immutable event record.

    Args:
        from_status: Source status (TaskStatus enum or string value).
        to_status: Target status (TaskStatus enum or string value).
            May be None for non-state-change events.
    """
    ts = created_at or datetime.now(timezone.utc)

    def _status_val(s: TaskStatus | str | None) -> str | None:
        if s is None:
            return None
        if isinstance(s, TaskStatus):
            return s.value
        return s

    return TaskEvent(
        event_id=str(uuid4()),
        project_id=project_id,
        task_id=task_id,
        event_type=event_type,
        from_status=_status_val(from_status),
        to_status=_status_val(to_status),
        triggered_by_kind=triggered_by_kind.value,
        triggered_by_id=triggered_by_id,
        reason=reason,
        payload=payload or {},
        created_at=ts.isoformat(),
    )


# ──────────────────────────────────────────────────────────────
# Convenience Builders
# ──────────────────────────────────────────────────────────────

def make_state_transition_event(
    project_id: str,
    task_id: str,
    from_status: TaskStatus,
    to_status: TaskStatus,
    triggered_by_kind: OwnerKind,
    triggered_by_id: str,
    reason: str,
    payload: dict[str, Any] | None = None,
) -> TaskEvent:
    """Build a state transition event."""
    return make_event(
        project_id=project_id,
        task_id=task_id,
        event_type=EventType.STATE_TRANSITION,
        from_status=from_status,
        to_status=to_status,
        triggered_by_kind=triggered_by_kind,
        triggered_by_id=triggered_by_id,
        reason=reason,
        payload=payload,
    )


def make_lease_claimed_event(
    project_id: str,
    task_id: str,
    lease_id: str,
    owner_kind: OwnerKind,
    owner_id: str,
    reason: str = "Lease claimed",
) -> TaskEvent:
    """Build a lease-claimed event."""
    return make_event(
        project_id=project_id,
        task_id=task_id,
        event_type=EventType.LEASE_CLAIMED,
        triggered_by_kind=owner_kind,
        triggered_by_id=owner_id,
        reason=reason,
        payload={"lease_id": lease_id},
    )


def make_lease_expired_event(
    project_id: str,
    task_id: str,
    lease_id: str,
    expired_owner_kind: str,
    expired_owner_id: str,
    reason: str = "Lease expired",
) -> TaskEvent:
    """Build a lease-expired event (recovery)."""
    return make_event(
        project_id=project_id,
        task_id=task_id,
        event_type=EventType.LEASE_EXPIRED,
        triggered_by_kind=OwnerKind.RUNTIME,
        triggered_by_id="runtime",
        reason=reason,
        payload={
            "lease_id": lease_id,
            "expired_owner_kind": expired_owner_kind,
            "expired_owner_id": expired_owner_id,
        },
    )


def make_recovery_event(
    project_id: str,
    task_id: str,
    from_status: TaskStatus,
    to_status: TaskStatus,
    task_type: str,
    reason: str,
    lease_id: str | None = None,
) -> TaskEvent:
    """Build a recovery event emitted when lease expiry triggers state recovery.

    This is the key audit record: it captures why the state changed and
    what recovery policy applied. It MUST NOT invent acceptance or review
    outcomes – the recovery is purely mechanical.
    """
    payload: dict[str, Any] = {
        "recovery": True,
        "task_type": task_type,
        "from_status": from_status.value,
        "to_status": to_status.value,
    }
    if lease_id:
        payload["lease_id"] = lease_id

    return make_event(
        project_id=project_id,
        task_id=task_id,
        event_type=EventType.RECOVERY_LEASE_EXPIRY,
        from_status=from_status,
        to_status=to_status,
        triggered_by_kind=OwnerKind.RUNTIME,
        triggered_by_id="runtime",
        reason=reason,
        payload=payload,
    )


# ──────────────────────────────────────────────────────────────
# Event Sequence (Append-Only Discipline)
# ──────────────────────────────────────────────────────────────

@dataclass
class EventSequence:
    """Ordered collection of events for a single transaction.

    Events are appended in order and cannot be removed or modified
    after creation, enforcing append-only discipline.
    """
    events: list[TaskEvent] = field(default_factory=list)

    def append(self, event: TaskEvent) -> None:
        """Add an event to the sequence. Cannot be undone."""
        self.events.append(event)

    def to_dicts(self) -> list[dict[str, Any]]:
        """Convert all events to persistence dicts."""
        return [e.to_dict() for e in self.events]

    @property
    def count(self) -> int:
        return len(self.events)
