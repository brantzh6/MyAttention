"""
IKE Runtime v0 – Redis Queue/Cache Adapter

Redis-based acceleration layer for IKE Runtime v0.
Redis is acceleration ONLY – Postgres remains the canonical truth source.

This module provides:
- Key builders for ready queues, active queues, hot pointers, dedupe windows,
  and lease keys.
- Abstract operation interfaces (no direct Redis import – callers supply
  a Redis client or connection pool).
- Queue discipline: tasks exist in queues only if they exist in Postgres.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any


# ──────────────────────────────────────────────────────────────
# Key Conventions
# ──────────────────────────────────────────────────────────────

_KEY_PREFIX = "ike:r0"

# Ready queue: sorted set of task_ids by priority (score = priority)
READY_QUEUE = f"{_KEY_PREFIX}:queue:ready"

# Per-project ready queue
def project_ready_queue(project_id: str) -> str:
    return f"{_KEY_PREFIX}:queue:ready:{project_id}"

# Active set: set of task_ids currently being worked on
ACTIVE_SET = f"{_KEY_PREFIX}:queue:active"

# Per-project active set
def project_active_set(project_id: str) -> str:
    return f"{_KEY_PREFIX}:queue:active:{project_id}"

# Waiting set: set of task_ids in waiting state
WAITING_SET = f"{_KEY_PREFIX}:queue:waiting"

# Review pending set: set of task_ids awaiting review
REVIEW_PENDING_SET = f"{_KEY_PREFIX}:queue:review_pending"


# ──────────────────────────────────────────────────────────────
# Hot Pointers
# ──────────────────────────────────────────────────────────────

# Latest work context for a project
def project_work_context_key(project_id: str) -> str:
    return f"{_KEY_PREFIX}:ctx:{project_id}:latest"

# Latest accepted decision for a project
def project_latest_decision_key(project_id: str) -> str:
    return f"{_KEY_PREFIX}:dec:{project_id}:latest"

# Active lease pointer for a task
def task_lease_key(task_id: str) -> str:
    return f"{_KEY_PREFIX}:lease:{task_id}"

# Current checkpoint pointer for a task
def task_checkpoint_key(task_id: str) -> str:
    return f"{_KEY_PREFIX}:chkpt:{task_id}:latest"


# ──────────────────────────────────────────────────────────────
# Lease Keys
# ──────────────────────────────────────────────────────────────

# Worker heartbeat key (TTL-based expiry)
def worker_heartbeat_key(task_id: str, owner_id: str) -> str:
    return f"{_KEY_PREFIX}:hb:{task_id}:{owner_id}"

# Default heartbeat TTL (seconds)
DEFAULT_HEARTBEAT_TTL = 3600  # 1 hour


# ──────────────────────────────────────────────────────────────
# Dedupe Windows
# ────────────────────────────────────────────────────────────

# Dedupe set for event IDs (prevents replay)
DEDUPE_SET = f"{_KEY_PREFIX}:dedupe:events"

# Default dedupe window (seconds)
DEFAULT_DEDUPE_WINDOW = 86400  # 24 hours

# Dedupe set for task creation (prevents double-creation)
def task_dedupe_key(project_id: str) -> str:
    return f"{_KEY_PREFIX}:dedupe:tasks:{project_id}"

# Dedupe set for lease claims (prevents double-claim)
def lease_dedupe_key(task_id: str) -> str:
    return f"{_KEY_PREFIX}:dedupe:lease:{task_id}"

# Default lease dedupe window (seconds)
DEFAULT_LEASE_DEDUPE_WINDOW = 300  # 5 minutes


# ──────────────────────────────────────────────────────────────
# Key Generation Helpers
# ──────────────────────────────────────────────────────────────

def make_dedupe_event_id(event_type: str, task_id: str, timestamp: str) -> str:
    """Generate a deterministic dedupe ID for an event.

    This ensures the same event (same type, task, and approximate time)
    is not processed twice even if replayed.
    """
    raw = f"{event_type}:{task_id}:{timestamp}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def make_task_dedupe_id(task_title: str, project_id: str) -> str:
    """Generate a dedupe ID for task creation.

    Prevents the same task from being created twice in rapid succession.
    """
    raw = f"{project_id}:{task_title}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ──────────────────────────────────────────────────────────────
# Abstract Redis Operations Interface
# ──────────────────────────────────────────────────────────────
# This module does NOT import redis directly.
# Callers supply a client that implements these operations.
# This keeps the module testable and decoupled from the redis package.

@dataclass
class RedisCommand:
    """A single Redis command with its arguments.

    Used for testing and dry-run validation without executing.
    """
    command: str
    args: list[Any]
    kwargs: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"RedisCommand({self.command}, {self.args}, {self.kwargs})"


@dataclass
class RedisOperationBatch:
    """A batch of Redis commands to execute atomically (via pipeline)."""
    commands: list[RedisCommand] = field(default_factory=list)

    def add(self, command: str, *args: Any, **kwargs: Any) -> None:
        self.commands.append(RedisCommand(command, list(args), kwargs))

    def clear(self) -> None:
        self.commands.clear()

    @property
    def size(self) -> int:
        return len(self.commands)


# ──────────────────────────────────────────────────────────────
# Queue Operations (Command Builders)
# ──────────────────────────────────────────────────────────────

def enqueue_ready(
    batch: RedisOperationBatch,
    task_id: str,
    project_id: str,
    priority: int,
) -> None:
    """Add a task to the ready queue (sorted set by priority).

    Lower priority number = higher priority (processed first).
    Also adds to the per-project ready queue.
    """
    batch.add("ZADD", READY_QUEUE, priority, task_id)
    batch.add("ZADD", project_ready_queue(project_id), priority, task_id)


def dequeue_ready(
    batch: RedisOperationBatch,
    task_id: str,
    project_id: str,
) -> None:
    """Remove a task from the ready queue (it's being claimed)."""
    batch.add("ZREM", READY_QUEUE, task_id)
    batch.add("ZREM", project_ready_queue(project_id), task_id)


def enqueue_active(
    batch: RedisOperationBatch,
    task_id: str,
    project_id: str,
) -> None:
    """Add a task to the active set."""
    batch.add("SADD", ACTIVE_SET, task_id)
    batch.add("SADD", project_active_set(project_id), task_id)


def dequeue_active(
    batch: RedisOperationBatch,
    task_id: str,
    project_id: str,
) -> None:
    """Remove a task from the active set (completed or recovered)."""
    batch.add("SREM", ACTIVE_SET, task_id)
    batch.add("SREM", project_active_set(project_id), task_id)


def enqueue_waiting(
    batch: RedisOperationBatch,
    task_id: str,
) -> None:
    """Add a task to the waiting set."""
    batch.add("SADD", WAITING_SET, task_id)


def dequeue_waiting(
    batch: RedisOperationBatch,
    task_id: str,
) -> None:
    """Remove a task from the waiting set."""
    batch.add("SREM", WAITING_SET, task_id)


def enqueue_review_pending(
    batch: RedisOperationBatch,
    task_id: str,
) -> None:
    """Add a task to the review pending set."""
    batch.add("SADD", REVIEW_PENDING_SET, task_id)


def dequeue_review_pending(
    batch: RedisOperationBatch,
    task_id: str,
) -> None:
    """Remove a task from the review pending set."""
    batch.add("SREM", REVIEW_PENDING_SET, task_id)


# ──────────────────────────────────────────────────────────────
# Hot Pointer Operations
# ──────────────────────────────────────────────────────────────

def set_work_context_pointer(
    batch: RedisOperationBatch,
    project_id: str,
    work_context_id: str,
) -> None:
    """Set the latest work context pointer for a project."""
    batch.add("SET", project_work_context_key(project_id), work_context_id)


def set_latest_decision_pointer(
    batch: RedisOperationBatch,
    project_id: str,
    decision_id: str,
) -> None:
    """Set the latest decision pointer for a project."""
    batch.add("SET", project_latest_decision_key(project_id), decision_id)


def set_task_lease_pointer(
    batch: RedisOperationBatch,
    task_id: str,
    lease_id: str,
    ttl: int = DEFAULT_HEARTBEAT_TTL,
) -> None:
    """Set the active lease pointer for a task (with TTL)."""
    batch.add("SETEX", task_lease_key(task_id), ttl, lease_id)


def delete_task_lease_pointer(
    batch: RedisOperationBatch,
    task_id: str,
) -> None:
    """Delete the lease pointer for a task (lease expired/released)."""
    batch.add("DEL", task_lease_key(task_id))


# ──────────────────────────────────────────────────────────────
# Lease/Heartbeat Operations
# ──────────────────────────────────────────────────────────────

def set_heartbeat(
    batch: RedisOperationBatch,
    task_id: str,
    owner_id: str,
    ttl: int = DEFAULT_HEARTBEAT_TTL,
) -> None:
    """Set a heartbeat key with TTL. If the key expires, the lease is stale."""
    batch.add("SETEX", worker_heartbeat_key(task_id, owner_id), ttl, "1")


def check_heartbeat(
    task_id: str,
    owner_id: str,
) -> str:
    """Get the heartbeat key for checking existence."""
    return worker_heartbeat_key(task_id, owner_id)


# ──────────────────────────────────────────────────────────────
# Dedupe Operations
# ──────────────────────────────────────────────────────────────

def check_dedupe_event(
    batch: RedisOperationBatch,
    event_id: str,
    window: int = DEFAULT_DEDUPE_WINDOW,
) -> None:
    """Check if an event has already been processed (NX add).

    Returns True (added) if this is a new event, False (not added) if duplicate.
    The caller should check the result of the SADD command.
    """
    batch.add("SADD", DEDUPE_SET, event_id)
    batch.add("EXPIRE", DEDUPE_SET, window)


def check_task_dedupe(
    batch: RedisOperationBatch,
    project_id: str,
    dedupe_id: str,
    window: int = DEFAULT_DEDUPE_WINDOW,
) -> None:
    """Check if a task creation is a duplicate."""
    key = task_dedupe_key(project_id)
    batch.add("SADD", key, dedupe_id)
    batch.add("EXPIRE", key, window)


def check_lease_dedupe(
    batch: RedisOperationBatch,
    task_id: str,
    dedupe_id: str,
    window: int = DEFAULT_LEASE_DEDUPE_WINDOW,
) -> None:
    """Check if a lease claim is a duplicate."""
    key = lease_dedupe_key(task_id)
    batch.add("SADD", key, dedupe_id)
    batch.add("EXPIRE", key, window)


# ──────────────────────────────────────────────────────────────
# Full Queue Sync for a Task State Change
# ──────────────────────────────────────────────────────────────

def build_queue_sync_batch(
    task_id: str,
    project_id: str,
    from_status: str | None,
    to_status: str,
    priority: int = 2,
) -> RedisOperationBatch:
    """Build a Redis pipeline batch for syncing queue membership after a
    task state change.

    This ensures Redis queues reflect the new task state:
    - Remove from old queue/set
    - Add to new queue/set

    Args:
        task_id: The task that changed state.
        project_id: The project the task belongs to.
        from_status: Previous status (may be None for new tasks).
        to_status: New status.
        priority: Task priority (for ready queue scoring).
    """
    batch = RedisOperationBatch()

    # Remove from old queues
    if from_status == "ready":
        dequeue_ready(batch, task_id, project_id)
    elif from_status == "active":
        dequeue_active(batch, task_id, project_id)
    elif from_status == "waiting":
        dequeue_waiting(batch, task_id)
    elif from_status == "review_pending":
        dequeue_review_pending(batch, task_id)

    # Add to new queues
    if to_status == "ready":
        enqueue_ready(batch, task_id, project_id, priority)
    elif to_status == "active":
        enqueue_active(batch, task_id, project_id)
    elif to_status == "waiting":
        enqueue_waiting(batch, task_id)
    elif to_status == "review_pending":
        enqueue_review_pending(batch, task_id)

    return batch
