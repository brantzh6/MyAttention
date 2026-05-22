"""
Tests for IKE Runtime v0 Redis rebuild and acceleration layer.

Validates:
- Rebuild from Postgres truth produces correct Redis commands
- Redis-loss recovery reconstructs all queue state
- No hidden queue-only truth (rebuild from canonical data only)
- Queue operations produce correct key structures
- Lease pointers and heartbeats rebuild correctly
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from runtime.redis_runtime import (
    READY_QUEUE,
    ACTIVE_SET,
    WAITING_SET,
    REVIEW_PENDING_SET,
    project_ready_queue,
    project_active_set,
    project_work_context_key,
    project_latest_decision_key,
    task_lease_key,
    task_checkpoint_key,
    worker_heartbeat_key,
    DEDUPE_SET,
    task_dedupe_key,
    lease_dedupe_key,
    DEFAULT_HEARTBEAT_TTL,
    DEFAULT_DEDUPE_WINDOW,
    DEFAULT_LEASE_DEDUPE_WINDOW,
    make_dedupe_event_id,
    make_task_dedupe_id,
    RedisCommand,
    RedisOperationBatch,
    enqueue_ready,
    dequeue_ready,
    enqueue_active,
    dequeue_active,
    enqueue_waiting,
    dequeue_waiting,
    enqueue_review_pending,
    dequeue_review_pending,
    set_work_context_pointer,
    set_latest_decision_pointer,
    set_task_lease_pointer,
    delete_task_lease_pointer,
    set_heartbeat,
    check_heartbeat,
    check_dedupe_event,
    check_task_dedupe,
    check_lease_dedupe,
    build_queue_sync_batch,
)

from runtime.redis_rebuild import (
    TaskRebuildSnapshot,
    LeaseRebuildSnapshot,
    WorkContextRebuildSnapshot,
    DecisionRebuildSnapshot,
    rebuild_all_from_canonical,
    rebuild_queues_from_tasks,
    rebuild_lease_pointers,
    rebuild_pointers_from_contexts,
    rebuild_decision_pointers,
    sync_task_state_change,
    sync_lease_claim,
    sync_lease_release,
)


# ──────────────────────────────────────────────────────────────
# Key Conventions
# ──────────────────────────────────────────────────────────────

class TestKeyConventions:
    def test_ready_queue_key(self):
        assert ":queue:ready" in READY_QUEUE

    def test_active_set_key(self):
        assert ":queue:active" in ACTIVE_SET

    def test_project_ready_queue(self):
        key = project_ready_queue("proj-1")
        assert "proj-1" in key
        assert "ready" in key

    def test_project_active_set(self):
        key = project_active_set("proj-1")
        assert "proj-1" in key
        assert "active" in key

    def test_work_context_key(self):
        key = project_work_context_key("proj-1")
        assert "proj-1" in key
        assert "ctx" in key

    def test_latest_decision_key(self):
        key = project_latest_decision_key("proj-1")
        assert "proj-1" in key
        assert "dec" in key

    def test_task_lease_key(self):
        key = task_lease_key("task-1")
        assert "task-1" in key
        assert "lease" in key

    def test_worker_heartbeat_key(self):
        key = worker_heartbeat_key("task-1", "del-001")
        assert "task-1" in key
        assert "del-001" in key
        assert "hb" in key

    def test_dedupe_set_key(self):
        assert ":dedupe:events" in DEDUPE_SET

    def test_task_dedupe_key(self):
        key = task_dedupe_key("proj-1")
        assert "proj-1" in key
        assert "dedupe:tasks" in key

    def test_lease_dedupe_key(self):
        key = lease_dedupe_key("task-1")
        assert "task-1" in key
        assert "dedupe:lease" in key


# ──────────────────────────────────────────────────────────────
# Dedupe ID Generation
# ──────────────────────────────────────────────────────────────

class TestDedupeIdGeneration:
    def test_dedupe_event_id_is_deterministic(self):
        id1 = make_dedupe_event_id("state_transition", "task-1", "2026-04-06T00:00:00")
        id2 = make_dedupe_event_id("state_transition", "task-1", "2026-04-06T00:00:00")
        assert id1 == id2

    def test_dedupe_event_id_differs_by_task(self):
        id1 = make_dedupe_event_id("state_transition", "task-1", "2026-04-06T00:00:00")
        id2 = make_dedupe_event_id("state_transition", "task-2", "2026-04-06T00:00:00")
        assert id1 != id2

    def test_dedupe_event_id_differs_by_type(self):
        id1 = make_dedupe_event_id("state_transition", "task-1", "2026-04-06T00:00:00")
        id2 = make_dedupe_event_id("lease_claimed", "task-1", "2026-04-06T00:00:00")
        assert id1 != id2

    def test_task_dedupe_id_is_deterministic(self):
        id1 = make_task_dedupe_id("Build API", "proj-1")
        id2 = make_task_dedupe_id("Build API", "proj-1")
        assert id1 == id2

    def test_task_dedupe_id_differs_by_title(self):
        id1 = make_task_dedupe_id("Build API", "proj-1")
        id2 = make_task_dedupe_id("Build UI", "proj-1")
        assert id1 != id2


# ──────────────────────────────────────────────────────────────
# RedisCommand and Batch
# ──────────────────────────────────────────────────────────────

class TestRedisBatch:
    def test_add_command(self):
        batch = RedisOperationBatch()
        batch.add("SET", "key1", "value1")
        assert batch.size == 1
        assert batch.commands[0].command == "SET"
        assert batch.commands[0].args == ["key1", "value1"]

    def test_clear(self):
        batch = RedisOperationBatch()
        batch.add("SET", "key1", "value1")
        batch.add("GET", "key1")
        batch.clear()
        assert batch.size == 0

    def test_kwargs_preserved(self):
        batch = RedisOperationBatch()
        batch.add("SETEX", "key", 3600, "value", nx=True)
        assert batch.commands[0].kwargs == {"nx": True}


# ──────────────────────────────────────────────────────────────
# Queue Operations
# ──────────────────────────────────────────────────────────────

class TestQueueOperations:
    def test_enqueue_ready(self):
        batch = RedisOperationBatch()
        enqueue_ready(batch, "task-1", "proj-1", priority=1)
        assert batch.size == 2  # global + project queue
        assert batch.commands[0].command == "ZADD"
        assert batch.commands[0].args == [READY_QUEUE, 1, "task-1"]
        assert batch.commands[1].args[0] == project_ready_queue("proj-1")

    def test_dequeue_ready(self):
        batch = RedisOperationBatch()
        dequeue_ready(batch, "task-1", "proj-1")
        assert batch.size == 2
        assert batch.commands[0].command == "ZREM"

    def test_enqueue_active(self):
        batch = RedisOperationBatch()
        enqueue_active(batch, "task-1", "proj-1")
        assert batch.size == 2
        assert batch.commands[0].command == "SADD"
        assert batch.commands[0].args[0] == ACTIVE_SET

    def test_dequeue_active(self):
        batch = RedisOperationBatch()
        dequeue_active(batch, "task-1", "proj-1")
        assert batch.size == 2
        assert batch.commands[0].command == "SREM"

    def test_enqueue_waiting(self):
        batch = RedisOperationBatch()
        enqueue_waiting(batch, "task-1")
        assert batch.size == 1
        assert batch.commands[0].args[0] == WAITING_SET

    def test_enqueue_review_pending(self):
        batch = RedisOperationBatch()
        enqueue_review_pending(batch, "task-1")
        assert batch.size == 1
        assert batch.commands[0].args[0] == REVIEW_PENDING_SET


# ──────────────────────────────────────────────────────────────
# Pointer Operations
# ──────────────────────────────────────────────────────────────

class TestPointerOperations:
    def test_set_work_context_pointer(self):
        batch = RedisOperationBatch()
        set_work_context_pointer(batch, "proj-1", "ctx-1")
        assert batch.size == 1
        assert batch.commands[0].command == "SET"
        assert batch.commands[0].args[1] == "ctx-1"

    def test_set_latest_decision_pointer(self):
        batch = RedisOperationBatch()
        set_latest_decision_pointer(batch, "proj-1", "dec-1")
        assert batch.size == 1
        assert batch.commands[0].args[1] == "dec-1"

    def test_set_task_lease_pointer_with_ttl(self):
        batch = RedisOperationBatch()
        set_task_lease_pointer(batch, "task-1", "lease-1", ttl=7200)
        assert batch.size == 1
        assert batch.commands[0].command == "SETEX"
        assert batch.commands[0].args == [task_lease_key("task-1"), 7200, "lease-1"]

    def test_delete_task_lease_pointer(self):
        batch = RedisOperationBatch()
        delete_task_lease_pointer(batch, "task-1")
        assert batch.size == 1
        assert batch.commands[0].command == "DEL"

    def test_set_heartbeat(self):
        batch = RedisOperationBatch()
        set_heartbeat(batch, "task-1", "del-001", ttl=1800)
        assert batch.size == 1
        assert batch.commands[0].command == "SETEX"
        assert batch.commands[0].args[1] == 1800


# ──────────────────────────────────────────────────────────────
# Queue Sync Batch
# ──────────────────────────────────────────────────────────────

class TestQueueSyncBatch:
    def test_sync_ready_to_active(self):
        """Task moves from ready to active: remove from ready, add to active."""
        batch = build_queue_sync_batch(
            task_id="task-1",
            project_id="proj-1",
            from_status="ready",
            to_status="active",
            priority=1,
        )
        # Remove from ready (2 commands: global + project)
        # Add to active (2 commands: global + project)
        assert batch.size == 4
        commands = [c.command + str(c.args) for c in batch.commands]
        assert any("ZREM" in c for c in commands)
        assert any("SADD" in c for c in commands)

    def test_sync_active_to_waiting(self):
        """Task moves from active to waiting: remove from active, add to waiting."""
        batch = build_queue_sync_batch(
            task_id="task-1",
            project_id="proj-1",
            from_status="active",
            to_status="waiting",
        )
        assert batch.size == 3  # 2 SREM + 1 SADD
        commands = [c.command + str(c.args) for c in batch.commands]
        assert any("SREM" in c for c in commands)
        assert any("SADD" in c and "waiting" in c for c in commands)

    def test_sync_active_to_review_pending(self):
        batch = build_queue_sync_batch(
            task_id="task-1",
            project_id="proj-1",
            from_status="active",
            to_status="review_pending",
        )
        assert batch.size == 3  # 2 SREM + 1 SADD

    def test_sync_to_done_clears_all_queues(self):
        """Task moves to done: removed from all queues, not added to any."""
        batch = build_queue_sync_batch(
            task_id="task-1",
            project_id="proj-1",
            from_status="active",
            to_status="done",
        )
        # Only removal commands, no additions
        for cmd in batch.commands:
            assert cmd.command in ("SREM", "ZREM")

    def test_sync_new_task_to_ready(self):
        """New task to ready: only add, no removal."""
        batch = build_queue_sync_batch(
            task_id="task-1",
            project_id="proj-1",
            from_status=None,
            to_status="ready",
            priority=2,
        )
        assert batch.size == 2  # 2 ZADD commands
        for cmd in batch.commands:
            assert cmd.command == "ZADD"


# ──────────────────────────────────────────────────────────────
# Rebuild from Canonical State
# ──────────────────────────────────────────────────────────────

class TestRebuildFromCanonical:
    """The core rebuild tests: Postgres truth -> Redis state."""

    def test_rebuild_ready_tasks(self):
        tasks = [
            TaskRebuildSnapshot(
                task_id="task-1", project_id="proj-1",
                status="ready", task_type="implementation", priority=1,
                current_lease_id=None,
            ),
            TaskRebuildSnapshot(
                task_id="task-2", project_id="proj-1",
                status="ready", task_type="study", priority=3,
                current_lease_id=None,
            ),
        ]
        batch, result = rebuild_all_from_canonical(
            tasks=tasks,
            leases=[],
            work_contexts=[],
            decisions=[],
        )
        assert result.success is True
        assert result.tasks_rebuilt == 2
        # Each ready task: 2 ZADD commands (global + project)
        assert batch.size == 4
        commands = [c.command for c in batch.commands]
        assert commands.count("ZADD") == 4

    def test_rebuild_active_tasks(self):
        tasks = [
            TaskRebuildSnapshot(
                task_id="task-1", project_id="proj-1",
                status="active", task_type="implementation", priority=1,
                current_lease_id="lease-1",
            ),
        ]
        batch, result = rebuild_all_from_canonical(
            tasks=tasks,
            leases=[],
            work_contexts=[],
            decisions=[],
        )
        assert result.tasks_rebuilt == 1
        # Each active task: 2 SADD commands
        assert batch.size == 2
        assert all(c.command == "SADD" for c in batch.commands)

    def test_rebuild_waiting_tasks(self):
        tasks = [
            TaskRebuildSnapshot(
                task_id="task-1", project_id="proj-1",
                status="waiting", task_type="implementation", priority=2,
                current_lease_id=None,
            ),
        ]
        batch, result = rebuild_all_from_canonical(
            tasks=tasks,
            leases=[],
            work_contexts=[],
            decisions=[],
        )
        assert result.tasks_rebuilt == 1
        assert batch.size == 1
        assert batch.commands[0].args[0] == WAITING_SET

    def test_rebuild_review_pending_tasks(self):
        tasks = [
            TaskRebuildSnapshot(
                task_id="task-1", project_id="proj-1",
                status="review_pending", task_type="implementation", priority=2,
                current_lease_id=None,
            ),
        ]
        batch, result = rebuild_all_from_canonical(
            tasks=tasks,
            leases=[],
            work_contexts=[],
            decisions=[],
        )
        assert result.tasks_rebuilt == 1
        assert batch.size == 1
        assert batch.commands[0].args[0] == REVIEW_PENDING_SET

    def test_rebuild_skips_terminal_states(self):
        """done and failed tasks should not be in any queue."""
        tasks = [
            TaskRebuildSnapshot(
                task_id="task-1", project_id="proj-1",
                status="done", task_type="implementation", priority=1,
                current_lease_id=None,
            ),
            TaskRebuildSnapshot(
                task_id="task-2", project_id="proj-1",
                status="failed", task_type="implementation", priority=1,
                current_lease_id=None,
            ),
            TaskRebuildSnapshot(
                task_id="task-3", project_id="proj-1",
                status="inbox", task_type="implementation", priority=1,
                current_lease_id=None,
            ),
        ]
        batch, result = rebuild_all_from_canonical(
            tasks=tasks,
            leases=[],
            work_contexts=[],
            decisions=[],
        )
        assert result.tasks_rebuilt == 3  # counted but no queue commands
        assert batch.size == 0  # no queue commands for terminal/inbox states

    def test_rebuild_active_lease_pointers(self):
        now = datetime(2026, 4, 6, 12, 0, 0, tzinfo=timezone.utc)
        expires = now + timedelta(hours=2)
        leases = [
            LeaseRebuildSnapshot(
                lease_id="lease-1",
                task_id="task-1",
                owner_id="del-001",
                lease_status="active",
                expires_at=expires.isoformat(),
                heartbeat_at=now.isoformat(),
            ),
        ]
        batch, result = rebuild_all_from_canonical(
            tasks=[],
            leases=leases,
            work_contexts=[],
            decisions=[],
            now=now,
        )
        assert result.leases_rebuilt == 1
        # 2 commands: lease pointer (SETEX) + heartbeat (SETEX)
        assert batch.size == 2
        assert all(c.command == "SETEX" for c in batch.commands)

    def test_rebuild_skips_expired_leases(self):
        """Expired leases should not be rebuilt."""
        now = datetime(2026, 4, 6, 12, 0, 0, tzinfo=timezone.utc)
        expired = now - timedelta(hours=1)
        leases = [
            LeaseRebuildSnapshot(
                lease_id="lease-1",
                task_id="task-1",
                owner_id="del-001",
                lease_status="active",
                expires_at=expired.isoformat(),
                heartbeat_at=(now - timedelta(hours=2)).isoformat(),
            ),
        ]
        batch, result = rebuild_all_from_canonical(
            tasks=[],
            leases=leases,
            work_contexts=[],
            decisions=[],
            now=now,
        )
        assert result.leases_rebuilt == 1  # counted
        assert batch.size == 0  # but no commands (expired)

    def test_rebuild_skips_non_active_leases(self):
        """Released/expired leases should be skipped."""
        leases = [
            LeaseRebuildSnapshot(
                lease_id="lease-1",
                task_id="task-1",
                owner_id="del-001",
                lease_status="released",
                expires_at="2026-04-06T12:00:00+00:00",
                heartbeat_at="2026-04-06T11:00:00+00:00",
            ),
            LeaseRebuildSnapshot(
                lease_id="lease-2",
                task_id="task-2",
                owner_id="del-002",
                lease_status="expired",
                expires_at="2026-04-06T12:00:00+00:00",
                heartbeat_at="2026-04-06T11:00:00+00:00",
            ),
        ]
        batch, result = rebuild_all_from_canonical(
            tasks=[],
            leases=leases,
            work_contexts=[],
            decisions=[],
        )
        assert result.leases_rebuilt == 2
        assert batch.size == 0

    def test_rebuild_work_context_pointers(self):
        contexts = [
            WorkContextRebuildSnapshot(
                project_id="proj-1",
                work_context_id="ctx-1",
                status="active",
            ),
            WorkContextRebuildSnapshot(
                project_id="proj-2",
                work_context_id="ctx-2",
                status="archived",
            ),
        ]
        batch, result = rebuild_all_from_canonical(
            tasks=[],
            leases=[],
            work_contexts=contexts,
            decisions=[],
        )
        assert result.contexts_rebuilt == 2
        # Only active context produces a command
        assert batch.size == 1
        assert batch.commands[0].command == "SET"

    def test_rebuild_decision_pointers(self):
        decisions = [
            DecisionRebuildSnapshot(
                project_id="proj-1",
                decision_id="dec-1",
                status="final",
                finalized_at="2026-04-06T00:00:00+00:00",
            ),
            DecisionRebuildSnapshot(
                project_id="proj-1",
                decision_id="dec-2",
                status="draft",
                finalized_at=None,
            ),
            DecisionRebuildSnapshot(
                project_id="proj-1",
                decision_id="dec-3",
                status="final",
                finalized_at="2026-04-05T00:00:00+00:00",
            ),
        ]
        batch, result = rebuild_all_from_canonical(
            tasks=[],
            leases=[],
            work_contexts=[],
            decisions=decisions,
        )
        assert result.decisions_rebuilt == 3
        # Only finalized decisions produce commands
        assert batch.size == 2
        assert all(c.command == "SET" for c in batch.commands)


# ──────────────────────────────────────────────────────────────
# Redis-Loss Recovery Proof
# ──────────────────────────────────────────────────────────────

class TestRedisLossRecovery:
    """Prove: after Redis loss, full state is reconstructable from Postgres."""

    def test_full_rebuild_from_canonical(self):
        """Simulate full Redis loss and rebuild from canonical data."""
        now = datetime(2026, 4, 6, 12, 0, 0, tzinfo=timezone.utc)
        expires = now + timedelta(hours=4)

        # Canonical Postgres state
        tasks = [
            TaskRebuildSnapshot(
                task_id="task-ready-1", project_id="proj-1",
                status="ready", task_type="implementation", priority=1,
                current_lease_id=None,
            ),
            TaskRebuildSnapshot(
                task_id="task-ready-2", project_id="proj-1",
                status="ready", task_type="study", priority=2,
                current_lease_id=None,
            ),
            TaskRebuildSnapshot(
                task_id="task-active-1", project_id="proj-1",
                status="active", task_type="implementation", priority=1,
                current_lease_id="lease-1",
            ),
            TaskRebuildSnapshot(
                task_id="task-waiting-1", project_id="proj-1",
                status="waiting", task_type="implementation", priority=2,
                current_lease_id=None,
            ),
            TaskRebuildSnapshot(
                task_id="task-review-1", project_id="proj-1",
                status="review_pending", task_type="implementation", priority=1,
                current_lease_id=None,
            ),
            TaskRebuildSnapshot(
                task_id="task-done-1", project_id="proj-1",
                status="done", task_type="implementation", priority=1,
                current_lease_id=None,
            ),
        ]
        leases = [
            LeaseRebuildSnapshot(
                lease_id="lease-1",
                task_id="task-active-1",
                owner_id="del-001",
                lease_status="active",
                expires_at=expires.isoformat(),
                heartbeat_at=now.isoformat(),
            ),
        ]
        contexts = [
            WorkContextRebuildSnapshot(
                project_id="proj-1",
                work_context_id="ctx-1",
                status="active",
            ),
        ]
        decisions = [
            DecisionRebuildSnapshot(
                project_id="proj-1",
                decision_id="dec-1",
                status="final",
                finalized_at="2026-04-06T00:00:00+00:00",
            ),
        ]

        # Rebuild
        batch, result = rebuild_all_from_canonical(
            tasks=tasks,
            leases=leases,
            work_contexts=contexts,
            decisions=decisions,
            now=now,
        )

        assert result.success is True
        assert result.tasks_rebuilt == 6  # all tasks counted
        assert result.leases_rebuilt == 1
        assert result.contexts_rebuilt == 1
        assert result.decisions_rebuilt == 1
        assert batch.size > 0

        # Verify queue state
        zadd_count = sum(1 for c in batch.commands if c.command == "ZADD")
        sadd_count = sum(1 for c in batch.commands if c.command == "SADD")
        set_count = sum(1 for c in batch.commands if c.command == "SET")
        setex_count = sum(1 for c in batch.commands if c.command == "SETEX")

        # 2 ready tasks * 2 (global + project) = 4 ZADD
        assert zadd_count == 4
        # 1 active * 2 (global + project) + 1 waiting + 1 review_pending = 4 SADD
        assert sadd_count == 4
        # 1 context + 1 decision = 2 SET
        assert set_count == 2
        # 1 lease pointer + 1 heartbeat = 2 SETEX
        assert setex_count == 2

    def test_rebuild_produces_no_hidden_state(self):
        """Rebuild should only produce state derivable from input data."""
        batch, result = rebuild_all_from_canonical(
            tasks=[],
            leases=[],
            work_contexts=[],
            decisions=[],
        )
        assert result.success is True
        assert batch.size == 0  # No input = no output


# ──────────────────────────────────────────────────────────────
# Partial Rebuild Helpers
# ──────────────────────────────────────────────────────────────

class TestPartialRebuild:
    def test_rebuild_queues_from_tasks(self):
        tasks = [
            TaskRebuildSnapshot(
                task_id="task-1", project_id="proj-1",
                status="ready", task_type="implementation", priority=1,
                current_lease_id=None,
            ),
        ]
        batch = rebuild_queues_from_tasks(tasks)
        assert batch.size == 2
        assert all(c.command == "ZADD" for c in batch.commands)

    def test_rebuild_lease_pointers(self):
        now = datetime(2026, 4, 6, 12, 0, 0, tzinfo=timezone.utc)
        expires = now + timedelta(hours=2)
        leases = [
            LeaseRebuildSnapshot(
                lease_id="lease-1",
                task_id="task-1",
                owner_id="del-001",
                lease_status="active",
                expires_at=expires.isoformat(),
                heartbeat_at=now.isoformat(),
            ),
        ]
        batch = rebuild_lease_pointers(leases, now=now)
        assert batch.size == 2
        assert all(c.command == "SETEX" for c in batch.commands)

    def test_rebuild_pointers_from_contexts(self):
        contexts = [
            WorkContextRebuildSnapshot(
                project_id="proj-1",
                work_context_id="ctx-1",
                status="active",
            ),
        ]
        batch = rebuild_pointers_from_contexts(contexts)
        assert batch.size == 1
        assert batch.commands[0].command == "SET"

    def test_rebuild_decision_pointers(self):
        decisions = [
            DecisionRebuildSnapshot(
                project_id="proj-1",
                decision_id="dec-1",
                status="final",
                finalized_at="2026-04-06T00:00:00+00:00",
            ),
        ]
        batch = rebuild_decision_pointers(decisions)
        assert batch.size == 1
        assert batch.commands[0].command == "SET"


# ──────────────────────────────────────────────────────────────
# Incremental Sync
# ──────────────────────────────────────────────────────────────

class TestIncrementalSync:
    def test_sync_task_state_change(self):
        task = TaskRebuildSnapshot(
            task_id="task-1", project_id="proj-1",
            status="ready", task_type="implementation", priority=1,
            current_lease_id=None,
        )
        batch = sync_task_state_change(task)
        assert batch.size == 2
        assert all(c.command == "ZADD" for c in batch.commands)

    def test_sync_lease_claim(self):
        batch = sync_lease_claim("task-1", "lease-1", "del-001")
        assert batch.size == 2
        assert all(c.command == "SETEX" for c in batch.commands)

    def test_sync_lease_release(self):
        batch = sync_lease_release("task-1")
        assert batch.size == 1
        assert batch.commands[0].command == "DEL"
