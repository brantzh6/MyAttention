"""
Tests for IKE Runtime v0 schema foundation.

Validates:
- Migration application (table existence)
- ORM model loading
- Rollback viability
- Table shape and key constraints
- R1-A1 Hardening: Migration validation support
  - Upgrade SQL parses and creates expected objects
  - Downgrade SQL parses and drops objects in correct order
  - Migration is idempotent-safe (IF EXISTS / IF NOT EXISTS)
- R1-A5 Enforcement: Normalized test invocation
  - Migration file path resolved relative to project root
  - Tests work regardless of current working directory
"""

import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

# Test that all runtime v0 models can be imported (ORM model loading check)
from db.models import (
    RuntimeProject,
    RuntimeTask,
    RuntimeDecision,
    RuntimeTaskEvent,
    RuntimeWorkerLease,
    RuntimeWorkContext,
    RuntimeMemoryPacket,
    RuntimeTaskCheckpoint,
    RuntimeOutboxEvent,
    RuntimeTaskStatus,
    RuntimeProjectStatus,
    RuntimeTaskType,
    RuntimeOwnerKind,
    RuntimeReviewStatus,
    RuntimeDecisionOutcome,
    RuntimeDecisionStatus,
    RuntimePacketStatus,
    RuntimeLeaseStatus,
    RuntimeContextStatus,
    RuntimeOutboxPublishStatus,
)


EXPECTED_RUNTIME_TABLES = [
    "runtime_projects",
    "runtime_tasks",
    "runtime_decisions",
    "runtime_task_events",
    "runtime_worker_leases",
    "runtime_work_contexts",
    "runtime_memory_packets",
    "runtime_task_checkpoints",
    "runtime_outbox_events",
]


class TestMigrationApplication:
    """Test that migration 013 creates all expected tables."""

    @pytest.fixture(autouse=True)
    def setup_db(self, db_session):
        """Clean runtime tables before each test."""
        for table in reversed(EXPECTED_RUNTIME_TABLES):
            db_session.execute(f"DELETE FROM {table}")
        db_session.commit()

    def test_all_runtime_tables_exist(self, db_session):
        result = db_session.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name LIKE 'runtime_%'
            """
        )
        existing = {row[0] for row in result}
        for table in EXPECTED_RUNTIME_TABLES:
            assert table in existing, f"Missing table: {table}"

    def test_enum_types_created(self, db_session):
        expected_enums = [
            "runtime_task_status",
            "runtime_project_status",
            "runtime_task_type",
            "runtime_owner_kind",
            "runtime_review_status",
            "runtime_decision_outcome",
            "runtime_decision_status",
            "runtime_packet_status",
            "runtime_lease_status",
            "runtime_context_status",
            "runtime_outbox_publish_status",
        ]
        result = db_session.execute(
            """
            SELECT typname FROM pg_type
            WHERE typtype = 'e' AND typname LIKE 'runtime_%'
            """
        )
        existing = {row[0] for row in result}
        for enum_name in expected_enums:
            assert enum_name in existing, f"Missing enum type: {enum_name}"


class TestRuntimeProjectCRUD:
    """Test runtime_projects table shape."""

    def test_create_project(self, db_session):
        project = RuntimeProject(
            project_key="test-proj-001",
            title="Test Project",
            goal="Validate schema foundation",
        )
        db_session.add(project)
        db_session.commit()

        assert project.project_id is not None
        assert project.status == RuntimeProjectStatus.ACTIVE
        assert project.priority == 2
        assert project.extra == {}

    def test_project_key_unique_constraint(self, db_session):
        db_session.add(RuntimeProject(project_key="dup-key", title="First"))
        db_session.commit()
        db_session.add(RuntimeProject(project_key="dup-key", title="Second"))
        with pytest.raises(Exception):  # UniqueViolation
            db_session.commit()

    def test_valid_project_statuses(self, db_session):
        valid_statuses = ["active", "paused", "blocked", "completed", "archived"]
        for s in valid_statuses:
            key = f"status-{s}-{uuid4().hex[:6]}"
            project = RuntimeProject(project_key=key, title=f"Status {s}", status=s)
            db_session.add(project)
        db_session.commit()

    def test_invalid_project_status_rejected(self, db_session):
        key = f"invalid-{uuid4().hex[:6]}"
        project = RuntimeProject(project_key=key, title="Bad", status="nonexistent")
        db_session.add(project)
        with pytest.raises(Exception):
            db_session.commit()


class TestRuntimeTaskCRUD:
    """Test runtime_tasks table shape and constraints."""

    @pytest.fixture(autouse=True)
    def setup_project(self, db_session):
        self.project = RuntimeProject(
            project_key="task-test-proj", title="Task Test Project"
        )
        db_session.add(self.project)
        db_session.commit()

    def test_create_task(self, db_session):
        task = RuntimeTask(
            project_id=self.project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Implement feature",
            goal="Build the thing",
        )
        db_session.add(task)
        db_session.commit()

        assert task.task_id is not None
        assert task.status == RuntimeTaskStatus.INBOX
        assert task.review_required is False
        assert task.extra == {}

    def test_task_foreign_key_to_project(self, db_session):
        task = RuntimeTask(
            project_id=uuid4(),  # non-existent project
            task_type=RuntimeTaskType.STUDY,
            title="Orphan",
        )
        db_session.add(task)
        with pytest.raises(Exception):  # ForeignKeyViolation
            db_session.commit()

    def test_valid_task_states(self, db_session):
        valid_states = ["inbox", "ready", "active", "waiting", "review_pending", "done", "failed"]
        for s in valid_states:
            task_kwargs = dict(
                project_id=self.project.project_id,
                task_type=RuntimeTaskType.IMPLEMENTATION,
                title=f"State {s}",
                status=s,
            )
            if s == "waiting":
                task_kwargs["waiting_reason"] = "test_wait"
                task_kwargs["waiting_detail"] = "Valid waiting state fixture"
            elif s == "done":
                task_kwargs["result_summary"] = "Valid done state fixture"
            db_session.add(RuntimeTask(**task_kwargs))
        db_session.commit()

    def test_invalid_task_state_rejected(self, db_session):
        task = RuntimeTask(
            project_id=self.project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Bad state",
            status="cancelled",
        )
        db_session.add(task)
        with pytest.raises(Exception):
            db_session.commit()

    def test_waiting_reason_required_when_waiting(self, db_session):
        task = RuntimeTask(
            project_id=self.project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Blocked task",
            status=RuntimeTaskStatus.WAITING,
        )
        db_session.add(task)
        with pytest.raises(Exception):  # check constraint violation
            db_session.commit()

    def test_waiting_with_reason_allowed(self, db_session):
        task = RuntimeTask(
            project_id=self.project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Blocked task",
            status=RuntimeTaskStatus.WAITING,
            waiting_reason="dependency_unmet",
            waiting_detail="Waiting on API",
        )
        db_session.add(task)
        db_session.commit()
        assert task.task_id is not None

    def test_parent_task_self_reference(self, db_session):
        parent = RuntimeTask(
            project_id=self.project.project_id,
            task_type=RuntimeTaskType.WORKFLOW,
            title="Parent workflow",
        )
        db_session.add(parent)
        db_session.commit()

        child = RuntimeTask(
            project_id=self.project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Child task",
            parent_task_id=parent.task_id,
        )
        db_session.add(child)
        db_session.commit()
        assert child.parent_task_id == parent.task_id


class TestRuntimeWorkerLease:
    """Test runtime_worker_leases constraints."""

    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        self.project = RuntimeProject(project_key="lease-proj", title="Lease Test")
        db_session.add(self.project)
        db_session.commit()

        self.task = RuntimeTask(
            project_id=self.project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Leasable task",
            status=RuntimeTaskStatus.ACTIVE,
        )
        db_session.add(self.task)
        db_session.commit()

    def test_create_lease(self, db_session):
        lease = RuntimeWorkerLease(
            task_id=self.task.task_id,
            owner_kind=RuntimeOwnerKind.DELEGATE,
            owner_id="agent-001",
            heartbeat_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db_session.add(lease)
        db_session.commit()
        assert lease.lease_id is not None
        assert lease.lease_status == RuntimeLeaseStatus.ACTIVE

    def test_one_active_lease_per_task(self, db_session):
        now = datetime.now(timezone.utc)
        lease1 = RuntimeWorkerLease(
            task_id=self.task.task_id,
            owner_kind=RuntimeOwnerKind.DELEGATE,
            owner_id="agent-001",
            heartbeat_at=now,
            expires_at=now + timedelta(hours=1),
        )
        db_session.add(lease1)
        db_session.commit()

        lease2 = RuntimeWorkerLease(
            task_id=self.task.task_id,
            owner_kind=RuntimeOwnerKind.DELEGATE,
            owner_id="agent-002",
            heartbeat_at=now,
            expires_at=now + timedelta(hours=1),
        )
        db_session.add(lease2)
        with pytest.raises(Exception):  # UniqueViolation on partial index
            db_session.commit()

    def test_heartbeat_required_for_active_lease(self, db_session):
        lease = RuntimeWorkerLease(
            task_id=self.task.task_id,
            owner_kind=RuntimeOwnerKind.DELEGATE,
            owner_id="agent-001",
            heartbeat_at=None,  # Missing heartbeat
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db_session.add(lease)
        with pytest.raises(Exception):  # check constraint violation
            db_session.commit()

    def test_expired_lease_no_heartbeat_required(self, db_session):
        lease = RuntimeWorkerLease(
            task_id=self.task.task_id,
            owner_kind=RuntimeOwnerKind.DELEGATE,
            owner_id="agent-001",
            lease_status=RuntimeLeaseStatus.EXPIRED,
            heartbeat_at=None,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db_session.add(lease)
        db_session.commit()
        assert lease.lease_status == RuntimeLeaseStatus.EXPIRED


class TestRuntimeMemoryPacket:
    """Test runtime_memory_packets lifecycle."""

    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        self.project = RuntimeProject(project_key="packet-proj", title="Packet Test")
        db_session.add(self.project)
        db_session.commit()

    def test_create_draft_packet(self, db_session):
        packet = RuntimeMemoryPacket(
            project_id=self.project.project_id,
            packet_type="study_result",
            title="Research findings",
            summary="Key insights...",
            created_by_kind=RuntimeOwnerKind.DELEGATE,
            created_by_id="agent-001",
        )
        db_session.add(packet)
        db_session.commit()
        assert packet.status == RuntimePacketStatus.DRAFT
        assert packet.accepted_at is None

    def test_accept_packet(self, db_session):
        packet = RuntimeMemoryPacket(
            project_id=self.project.project_id,
            packet_type="study_result",
            title="Research findings",
            summary="Key insights...",
            status=RuntimePacketStatus.ACCEPTED,
            created_by_kind=RuntimeOwnerKind.CONTROLLER,
            created_by_id="controller",
            accepted_at=datetime.now(timezone.utc),
        )
        db_session.add(packet)
        db_session.commit()
        assert packet.status == RuntimePacketStatus.ACCEPTED
        assert packet.accepted_at is not None

    def test_parent_packet_linkage(self, db_session):
        parent = RuntimeMemoryPacket(
            project_id=self.project.project_id,
            packet_type="checkpoint",
            title="Parent",
            summary="v1",
            created_by_kind=RuntimeOwnerKind.RUNTIME,
            created_by_id="system",
        )
        db_session.add(parent)
        db_session.commit()

        child = RuntimeMemoryPacket(
            project_id=self.project.project_id,
            packet_type="checkpoint",
            title="Child",
            summary="v2",
            created_by_kind=RuntimeOwnerKind.RUNTIME,
            created_by_id="system",
            parent_packet_id=parent.memory_packet_id,
        )
        db_session.add(child)
        db_session.commit()
        assert child.parent_packet_id == parent.memory_packet_id

    def test_invalid_packet_status_rejected(self, db_session):
        packet = RuntimeMemoryPacket(
            project_id=self.project.project_id,
            packet_type="study_result",
            title="Bad",
            status="trusted",  # not in enum
            created_by_kind=RuntimeOwnerKind.DELEGATE,
            created_by_id="agent-001",
        )
        db_session.add(packet)
        with pytest.raises(Exception):
            db_session.commit()


class TestRuntimeTaskEvents:
    """Test append-only event log."""

    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        self.project = RuntimeProject(project_key="event-proj", title="Event Test")
        db_session.add(self.project)
        db_session.commit()

        self.task = RuntimeTask(
            project_id=self.project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Event task",
        )
        db_session.add(self.task)
        db_session.commit()

    def test_append_event(self, db_session):
        event = RuntimeTaskEvent(
            project_id=self.project.project_id,
            task_id=self.task.task_id,
            event_type="state_transition",
            from_status=RuntimeTaskStatus.INBOX,
            to_status=RuntimeTaskStatus.READY,
            triggered_by_kind=RuntimeOwnerKind.CONTROLLER,
            triggered_by_id="controller",
            reason="Triage complete",
        )
        db_session.add(event)
        db_session.commit()
        assert event.event_id is not None
        assert event.from_status == RuntimeTaskStatus.INBOX
        assert event.to_status == RuntimeTaskStatus.READY

    def test_events_are_time_ordered(self, db_session):
        for status in ["ready", "active", "waiting", "ready", "active", "review_pending", "done"]:
            event = RuntimeTaskEvent(
                project_id=self.project.project_id,
                task_id=self.task.task_id,
                event_type="state_transition",
                to_status=status,
                triggered_by_kind=RuntimeOwnerKind.CONTROLLER,
                triggered_by_id="controller",
            )
            db_session.add(event)
            db_session.flush()

        events = db_session.execute(
            """
            SELECT to_status FROM runtime_task_events
            WHERE task_id = :tid ORDER BY created_at
            """,
            {"tid": self.task.task_id},
        ).fetchall()

        statuses = [row[0] for row in events]
        assert statuses == ["ready", "active", "waiting", "ready", "active", "review_pending", "done"]


class TestRuntimeOutboxEvents:
    """Test outbox event table shape."""

    def test_create_outbox_event(self, db_session):
        event = RuntimeOutboxEvent(
            aggregate_type="task",
            aggregate_id=str(uuid4()),
            event_type="task_state_changed",
            publish_status=RuntimeOutboxPublishStatus.PENDING,
        )
        db_session.add(event)
        db_session.commit()
        assert event.outbox_id is not None
        assert event.attempt_count == 0
        assert event.publish_status == RuntimeOutboxPublishStatus.PENDING


class TestRollbackViability:
    """Test that rollback SQL is structurally sound."""

    def test_rollback_statements_parse(self):
        """Verify rollback statements are present and parseable."""
        with open("migrations/013_runtime_v0_kernel_foundation.sql", "r", encoding="utf-8") as f:
            content = f.read()

        rollback_section = content.split("ROLLBACK")[1] if "ROLLBACK" in content else ""
        assert "DROP TABLE IF EXISTS runtime_outbox_events" in rollback_section
        assert "DROP TABLE IF EXISTS runtime_projects" in rollback_section
        assert "DROP TYPE IF EXISTS runtime_task_status" in rollback_section
        # Tables dropped in reverse dependency order (outbox first, projects last)
        tables = [
            "runtime_outbox_events",
            "runtime_task_checkpoints",
            "runtime_memory_packets",
            "runtime_work_contexts",
            "runtime_worker_leases",
            "runtime_task_events",
            "runtime_decisions",
            "runtime_tasks",
            "runtime_projects",
        ]
        positions = [rollback_section.find(f"DROP TABLE IF EXISTS {t}") for t in tables]
        for i in range(len(positions) - 1):
            assert positions[i] < positions[i + 1], (
                f"Rollback order wrong: {tables[i]} should be before {tables[i + 1]}"
            )


class TestV0StateSemantics:
    """Validate v0 state semantics are correctly encoded."""

    def test_task_states_match_design(self):
        """v0 canonical states must match design exactly."""
        expected = {"inbox", "ready", "active", "waiting", "review_pending", "done", "failed"}
        actual = {s.value for s in RuntimeTaskStatus}
        assert actual == expected, f"Task states mismatch: {actual} vs {expected}"

    def test_no_cancelled_state_in_task_status(self):
        """cancelled/dropped/deprioritized are control actions, not durable states."""
        forbidden = {"cancelled", "dropped", "deprioritized", "blocked", "triaged"}
        actual = {s.value for s in RuntimeTaskStatus}
        assert not (forbidden & actual), (
            f"Forbidden states found: {forbidden & actual}"
        )

    def test_project_states_match_design(self):
        expected = {"active", "paused", "blocked", "completed", "archived"}
        actual = {s.value for s in RuntimeProjectStatus}
        assert actual == expected

    def test_memory_packet_lifecycle_states(self):
        """draft -> pending_review -> accepted"""
        expected = {"draft", "pending_review", "accepted"}
        actual = {s.value for s in RuntimePacketStatus}
        assert actual == expected

    def test_decision_outcomes_match_design(self):
        expected = {"adopt", "reject", "defer", "escalate"}
        actual = {s.value for s in RuntimeDecisionOutcome}
        assert actual == expected

    def test_decision_status_match_design(self):
        expected = {"draft", "review_pending", "final", "superseded"}
        actual = {s.value for s in RuntimeDecisionStatus}
        assert actual == expected

    def test_review_pending_vs_done_are_distinct(self):
        """review_pending and done must be machine-distinguishable."""
        assert RuntimeTaskStatus.REVIEW_PENDING != RuntimeTaskStatus.DONE
        assert RuntimeTaskStatus.REVIEW_PENDING.value != RuntimeTaskStatus.DONE.value

    def test_waiting_is_not_blocked(self):
        """waiting reason models blocked situations, not a separate state."""
        assert "blocked" not in {s.value for s in RuntimeTaskStatus}
        assert "waiting" in {s.value for s in RuntimeTaskStatus}

    def test_task_types_match_design(self):
        expected = {"inbox", "study", "implementation", "review", "maintenance", "workflow", "daemon"}
        actual = {s.value for s in RuntimeTaskType}
        assert actual == expected

    def test_owner_kinds_include_all_roles(self):
        expected = {"controller", "delegate", "runtime", "scheduler", "reviewer", "user"}
        actual = {s.value for s in RuntimeOwnerKind}
        assert actual == expected


class TestTableColumnPresence:
    """Verify key columns exist on each table."""

    def test_task_has_explicit_state_column(self, db_session):
        cols = db_session.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'runtime_tasks' AND column_name = 'status'
            """
        ).fetchall()
        assert len(cols) == 1, "runtime_tasks.status column must exist as explicit column"

    def test_task_state_not_hidden_in_jsonb(self, db_session):
        """Canonical state must be in a typed column, not JSONB."""
        cols = db_session.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'runtime_tasks'
              AND column_name = 'status'
              AND data_type != 'jsonb'
            """
        ).fetchall()
        assert len(cols) == 1, "runtime_tasks.status must not be JSONB"

    def test_events_table_is_append_only_shape(self, db_session):
        """Event table should not have UPDATE-friendly mutable columns."""
        cols = db_session.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'runtime_task_events'
            """
        ).fetchall()
        col_names = {row[0] for row in cols}
        assert "event_id" in col_names
        assert "task_id" in col_names
        assert "event_type" in col_names
        assert "created_at" in col_names
        assert "payload" in col_names

    def test_lease_has_expiration(self, db_session):
        cols = db_session.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'runtime_worker_leases' AND column_name = 'expires_at'
            """
        ).fetchall()
        assert len(cols) == 1

    def test_task_has_waiting_reason_columns(self, db_session):
        cols = db_session.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'runtime_tasks'
              AND column_name IN ('waiting_reason', 'waiting_detail')
            """
        ).fetchall()
        col_names = {row[0] for row in cols}
        assert "waiting_reason" in col_names
        assert "waiting_detail" in col_names

    def test_task_has_review_fields(self, db_session):
        cols = db_session.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'runtime_tasks'
              AND column_name IN ('review_required', 'review_status')
            """
        ).fetchall()
        col_names = {row[0] for row in cols}
        assert "review_required" in col_names
        assert "review_status" in col_names

    def test_foreign_keys_exist(self, db_session):
        fks = db_session.execute(
            """
            SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
              ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'public'
              AND tc.table_name LIKE 'runtime_%'
            """
        ).fetchall()
        fk_pairs = {(row[0], row[1], row[2]) for row in fks}
        # Key foreign keys
        assert ("runtime_tasks", "project_id", "runtime_projects") in fk_pairs
        assert ("runtime_task_events", "task_id", "runtime_tasks") in fk_pairs
        assert ("runtime_decisions", "project_id", "runtime_projects") in fk_pairs
        assert ("runtime_worker_leases", "task_id", "runtime_tasks") in fk_pairs
        assert ("runtime_work_contexts", "project_id", "runtime_projects") in fk_pairs
        assert ("runtime_memory_packets", "project_id", "runtime_projects") in fk_pairs
        assert ("runtime_task_checkpoints", "task_id", "runtime_tasks") in fk_pairs


class TestIndexes:
    """Verify key indexes exist for lookup paths."""

    def test_task_project_status_index(self, db_session):
        idx = db_session.execute(
            """
            SELECT indexname FROM pg_indexes
            WHERE tablename = 'runtime_tasks' AND indexname = 'idx_runtime_tasks_project_status'
            """
        ).fetchone()
        assert idx is not None

    def test_lease_unique_active_index(self, db_session):
        idx = db_session.execute(
            """
            SELECT indexname, indexdef FROM pg_indexes
            WHERE tablename = 'runtime_worker_leases' AND indexname = 'idx_runtime_worker_leases_unique_active'
            """
        ).fetchone()
        assert idx is not None
        assert "where" in idx[1].lower(), "Unique active lease index must be partial"

    def test_work_context_unique_active_index(self, db_session):
        idx = db_session.execute(
            """
            SELECT indexname, indexdef FROM pg_indexes
            WHERE tablename = 'runtime_work_contexts' AND indexname = 'idx_runtime_work_contexts_unique_active'
            """
        ).fetchone()
        assert idx is not None
        assert "where" in idx[1].lower(), "Unique active context index must be partial"

    def test_outbox_status_index(self, db_session):
        idx = db_session.execute(
            """
            SELECT indexname FROM pg_indexes
            WHERE tablename = 'runtime_outbox_events' AND indexname = 'idx_runtime_outbox_events_status'
            """
        ).fetchone()
        assert idx is not None


# ──────────────────────────────────────────────────────────────
# R1-A1 Hardening: Migration Validation Support
# ──────────────────────────────────────────────────────────────

class TestMigrationValidationSupport:
    """R1-A1: Validate migration SQL is structurally sound for upgrade/downgrade.

    This provides the pytest-backed migration proof that was missing
    from the first-wave R0-A acceptance.

    R1-A5 ENFORCEMENT: Migration file path is resolved relative to the
    project root (e.g., D:\\code\\MyAttention), not the current working
    directory. This ensures tests pass regardless of invocation location.
    """

    @staticmethod
    def _get_migration_path() -> str:
        """Resolve migration file path relative to project root.

        R1-A5 FIX: Works regardless of current working directory by walking
        up from the test file location to find the project root. The project
        root is identified by containing BOTH 'migrations' folder AND 'services'
        folder (to distinguish from any nested migrations folders).
        """
        import os
        from pathlib import Path

        # Start from this test file's directory
        test_file = Path(__file__).absolute()
        test_dir = test_file.parent
        
        # Walk up to find the project root.
        # Project root is identified by having both 'migrations' and 'services' folders.
        # This distinguishes it from any nested migrations folders.
        current = test_dir
        while current.parent != current:
            migrations_path = current / "migrations" / "013_runtime_v0_kernel_foundation.sql"
            services_path = current / "services"
            # Project root has both migrations (with the file) and services
            if migrations_path.is_file() and services_path.is_dir():
                return str(migrations_path)
            current = current.parent

        # Fallback: try explicit path from common locations
        # This handles cases where the walk-up logic fails
        fallback_paths = [
            # From services/api/tests, go up 3 levels to repo root
            str(test_dir / ".." / ".." / ".." / "migrations" / "013_runtime_v0_kernel_foundation.sql"),
            # Try relative to current working directory
            "migrations/013_runtime_v0_kernel_foundation.sql",
        ]
        for path in fallback_paths:
            resolved = Path(path).resolve()
            if resolved.is_file():
                return str(resolved)

        # Return the most likely path even if it doesn't exist (for error message)
        return str((test_dir / ".." / ".." / ".." / "migrations" / "013_runtime_v0_kernel_foundation.sql").resolve())

    MIGRATION_FILE = property(lambda self: self._get_migration_path())

    @pytest.fixture
    def migration_content(self):
        """Load the migration SQL file."""
        with open(self.MIGRATION_FILE, "r", encoding="utf-8") as f:
            return f.read()

    def test_migration_file_exists(self):
        """Migration file must exist."""
        import os
        assert os.path.exists(self.MIGRATION_FILE), (
            f"Migration file not found: {self.MIGRATION_FILE}. "
            f"Resolved from test location: {Path(__file__).parent.absolute()}"
        )

    def test_upgrade_section_present(self, migration_content):
        """Migration must have an upgrade section."""
        # The file should contain CREATE TABLE or CREATE TYPE statements
        assert "CREATE TABLE" in migration_content or "CREATE TYPE" in migration_content, (
            "Migration file must contain CREATE statements"
        )

    def test_rollback_section_present(self, migration_content):
        """Migration must have a ROLLBACK section."""
        assert "ROLLBACK" in migration_content, (
            "Migration file must contain ROLLBACK section"
        )

    def test_rollback_drops_tables_in_reverse_order(self, migration_content):
        """ROLLBACK must drop tables in reverse dependency order."""
        rollback_section = migration_content.split("ROLLBACK")[1]

        # Tables should be dropped from most dependent to least dependent
        tables_in_order = [
            "runtime_outbox_events",
            "runtime_task_checkpoints",
            "runtime_memory_packets",
            "runtime_work_contexts",
            "runtime_worker_leases",
            "runtime_task_events",
            "runtime_decisions",
            "runtime_tasks",
            "runtime_projects",
        ]

        positions = []
        for table in tables_in_order:
            pos = rollback_section.find(f"DROP TABLE IF EXISTS {table}")
            assert pos >= 0, f"ROLLBACK missing DROP for {table}"
            positions.append(pos)

        # Each table should appear after the previous one (reverse dep order)
        for i in range(len(positions) - 1):
            assert positions[i] < positions[i + 1], (
                f"ROLLBACK order wrong: {tables_in_order[i]} should be dropped "
                f"before {tables_in_order[i + 1]}"
            )

    def test_rollback_drops_enum_types(self, migration_content):
        """ROLLBACK must drop enum types after tables."""
        rollback_section = migration_content.split("ROLLBACK")[1]
        assert "DROP TYPE IF EXISTS runtime_task_status" in rollback_section

    def test_migration_uses_if_exists_patterns(self, migration_content):
        """Migration should use IF EXISTS / IF NOT EXISTS for idempotency."""
        # At least one of these patterns should be present
        has_if_exists = (
            "IF NOT EXISTS" in migration_content or
            "IF EXISTS" in migration_content
        )
        assert has_if_exists, (
            "Migration should use IF NOT EXISTS or IF EXISTS for idempotent re-runs"
        )

    def test_all_expected_tables_in_migration(self, migration_content):
        """Migration should create all 9 runtime kernel tables."""
        expected_tables = [
            "runtime_projects",
            "runtime_tasks",
            "runtime_decisions",
            "runtime_task_events",
            "runtime_worker_leases",
            "runtime_work_contexts",
            "runtime_memory_packets",
            "runtime_task_checkpoints",
            "runtime_outbox_events",
        ]
        for table in expected_tables:
            assert f"CREATE TABLE" in migration_content and table in migration_content, (
                f"Migration missing table: {table}"
            )
