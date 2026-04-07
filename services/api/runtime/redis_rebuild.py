"""
IKE Runtime v0 – Redis Rebuild from Postgres Truth

Reconstructs Redis acceleration state from canonical Postgres truth.
If Redis is lost, this module rebuilds all queues, pointers, and
dedupe windows from the durable database state.

This module does NOT connect to Redis or Postgres directly.
It accepts snapshot data and produces RedisOperationBatch commands
that the caller executes against a Redis client.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .redis_runtime import (
    RedisOperationBatch,
    enqueue_ready,
    enqueue_active,
    enqueue_waiting,
    enqueue_review_pending,
    set_work_context_pointer,
    set_latest_decision_pointer,
    set_task_lease_pointer,
    delete_task_lease_pointer,
    set_heartbeat,
    DEFAULT_HEARTBEAT_TTL,
)


# ──────────────────────────────────────────────────────────────
# Canonical State Snapshots (Input for Rebuild)
# ──────────────────────────────────────────────────────────────

@dataclass
class TaskRebuildSnapshot:
    """Minimal task data needed for Redis queue rebuild."""
    task_id: str
    project_id: str
    status: str
    task_type: str
    priority: int
    current_lease_id: str | None


@dataclass
class LeaseRebuildSnapshot:
    """Minimal lease data needed for Redis lease pointer rebuild."""
    lease_id: str
    task_id: str
    owner_id: str
    lease_status: str
    expires_at: str  # ISO format
    heartbeat_at: str | None


@dataclass
class WorkContextRebuildSnapshot:
    """Minimal work context data for Redis pointer rebuild."""
    project_id: str
    work_context_id: str
    status: str


@dataclass
class DecisionRebuildSnapshot:
    """Minimal decision data for Redis pointer rebuild."""
    project_id: str
    decision_id: str
    status: str
    finalized_at: str | None


# ──────────────────────────────────────────────────────────────
# Rebuild Results
# ──────────────────────────────────────────────────────────────

@dataclass
class RebuildResult:
    """Result of a Redis rebuild operation."""
    success: bool
    commands_executed: int
    tasks_rebuilt: int
    leases_rebuilt: int
    contexts_rebuilt: int
    decisions_rebuilt: int
    errors: list[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0


# ──────────────────────────────────────────────────────────────
# Full Rebuild
# ──────────────────────────────────────────────────────────────

def rebuild_all_from_canonical(
    tasks: list[TaskRebuildSnapshot],
    leases: list[LeaseRebuildSnapshot],
    work_contexts: list[WorkContextRebuildSnapshot],
    decisions: list[DecisionRebuildSnapshot],
    now: datetime | None = None,
) -> tuple[RedisOperationBatch, RebuildResult]:
    """Rebuild all Redis acceleration state from canonical Postgres truth.

    This is the recovery path after Redis loss. It produces a complete
    batch of Redis commands to reconstruct:
    1. Ready/active/waiting/review_pending queues from task state
    2. Lease pointers from active leases
    3. Work context pointers from active contexts
    4. Latest decision pointers from finalized decisions

    Args:
        tasks: All tasks from Postgres (filtered to non-terminal states).
        leases: All leases from Postgres.
        work_contexts: All work contexts from Postgres.
        decisions: All decisions from Postgres.
        now: Current time (for TTL calculations). Defaults to now.

    Returns:
        (batch, result) tuple. The batch contains all Redis commands
        to execute. The result summarizes what was rebuilt.
    """
    ts = now or datetime.now(timezone.utc)
    batch = RedisOperationBatch()
    errors: list[str] = []
    tasks_rebuilt = 0
    leases_rebuilt = 0
    contexts_rebuilt = 0
    decisions_rebuilt = 0

    # 1. Build queue state from tasks
    for task in tasks:
        try:
            _rebuild_task_queues(batch, task)
            tasks_rebuilt += 1
        except Exception as e:
            errors.append(f"Task {task.task_id}: {e}")

    # 2. Build lease pointers from active leases
    for lease in leases:
        try:
            _rebuild_lease_pointer(batch, lease, ts)
            leases_rebuilt += 1
        except Exception as e:
            errors.append(f"Lease {lease.lease_id}: {e}")

    # 3. Build work context pointers
    for ctx in work_contexts:
        try:
            _rebuild_context_pointer(batch, ctx)
            contexts_rebuilt += 1
        except Exception as e:
            errors.append(f"Context {ctx.work_context_id}: {e}")

    # 4. Build latest decision pointers
    for dec in decisions:
        try:
            _rebuild_decision_pointer(batch, dec)
            decisions_rebuilt += 1
        except Exception as e:
            errors.append(f"Decision {dec.decision_id}: {e}")

    result = RebuildResult(
        success=len(errors) == 0,
        commands_executed=batch.size,
        tasks_rebuilt=tasks_rebuilt,
        leases_rebuilt=leases_rebuilt,
        contexts_rebuilt=contexts_rebuilt,
        decisions_rebuilt=decisions_rebuilt,
        errors=errors,
    )

    return batch, result


def _rebuild_task_queues(
    batch: RedisOperationBatch,
    task: TaskRebuildSnapshot,
) -> None:
    """Rebuild queue membership for a single task."""
    if task.status == "ready":
        enqueue_ready(batch, task.task_id, task.project_id, task.priority)
    elif task.status == "active":
        enqueue_active(batch, task.task_id, task.project_id)
    elif task.status == "waiting":
        enqueue_waiting(batch, task.task_id)
    elif task.status == "review_pending":
        enqueue_review_pending(batch, task.task_id)
    # Terminal states (done, failed, inbox) don't go in queues


def _rebuild_lease_pointer(
    batch: RedisOperationBatch,
    lease: LeaseRebuildSnapshot,
    now: datetime,
) -> None:
    """Rebuild lease pointer for an active lease."""
    if lease.lease_status != "active":
        return  # Skip non-active leases

    # Calculate remaining TTL
    try:
        expires = datetime.fromisoformat(lease.expires_at)
        remaining = int((expires - now).total_seconds())
        if remaining <= 0:
            return  # Lease already expired, skip
    except (ValueError, TypeError):
        remaining = DEFAULT_HEARTBEAT_TTL

    # Set lease pointer with remaining TTL
    set_task_lease_pointer(batch, lease.task_id, lease.lease_id, ttl=max(remaining, 60))

    # Set heartbeat with remaining TTL
    set_heartbeat(batch, lease.task_id, lease.owner_id, ttl=max(remaining, 60))


def _rebuild_context_pointer(
    batch: RedisOperationBatch,
    ctx: WorkContextRebuildSnapshot,
) -> None:
    """Rebuild work context pointer for an active context."""
    if ctx.status != "active":
        return
    set_work_context_pointer(batch, ctx.project_id, ctx.work_context_id)


def _rebuild_decision_pointer(
    batch: RedisOperationBatch,
    dec: DecisionRebuildSnapshot,
) -> None:
    """Rebuild latest decision pointer for a finalized decision."""
    if dec.status != "final" or dec.finalized_at is None:
        return
    set_latest_decision_pointer(batch, dec.project_id, dec.decision_id)


# ──────────────────────────────────────────────────────────────
# Partial Rebuild Helpers
# ──────────────────────────────────────────────────────────────

def rebuild_queues_from_tasks(
    tasks: list[TaskRebuildSnapshot],
) -> RedisOperationBatch:
    """Rebuild only queue state from task snapshots.

    Use this when only queues need refreshing (not pointers).
    """
    batch = RedisOperationBatch()
    for task in tasks:
        _rebuild_task_queues(batch, task)
    return batch


def rebuild_lease_pointers(
    leases: list[LeaseRebuildSnapshot],
    now: datetime | None = None,
) -> RedisOperationBatch:
    """Rebuild only lease pointers from lease snapshots."""
    ts = now or datetime.now(timezone.utc)
    batch = RedisOperationBatch()
    for lease in leases:
        _rebuild_lease_pointer(batch, lease, ts)
    return batch


def rebuild_pointers_from_contexts(
    work_contexts: list[WorkContextRebuildSnapshot],
) -> RedisOperationBatch:
    """Rebuild only work context pointers."""
    batch = RedisOperationBatch()
    for ctx in work_contexts:
        _rebuild_context_pointer(batch, ctx)
    return batch


def rebuild_decision_pointers(
    decisions: list[DecisionRebuildSnapshot],
) -> RedisOperationBatch:
    """Rebuild only decision pointers."""
    batch = RedisOperationBatch()
    for dec in decisions:
        _rebuild_decision_pointer(batch, dec)
    return batch


# ──────────────────────────────────────────────────────────────
# Incremental Sync
# ──────────────────────────────────────────────────────────────

def sync_task_state_change(
    task: TaskRebuildSnapshot,
) -> RedisOperationBatch:
    """Sync a single task's queue membership after a state change.

    This is the incremental path: after a task transitions state,
    call this to update Redis queues without a full rebuild.
    """
    batch = RedisOperationBatch()
    _rebuild_task_queues(batch, task)
    return batch


def sync_lease_claim(
    task_id: str,
    lease_id: str,
    owner_id: str,
    ttl: int = DEFAULT_HEARTBEAT_TTL,
) -> RedisOperationBatch:
    """Sync Redis after a lease claim.

    Sets the lease pointer and heartbeat, removes from ready queue.
    """
    batch = RedisOperationBatch()
    set_task_lease_pointer(batch, task_id, lease_id, ttl=ttl)
    set_heartbeat(batch, task_id, owner_id, ttl=ttl)
    return batch


def sync_lease_release(
    task_id: str,
) -> RedisOperationBatch:
    """Sync Redis after a lease release/expiry.

    Removes the lease pointer.
    """
    batch = RedisOperationBatch()
    delete_task_lease_pointer(batch, task_id)
    return batch
