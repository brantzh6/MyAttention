"""
Minimal tests for IKE v0 ResearchTask schema and mapper.

Tests verify:
- ResearchTask schema can be imported and instantiated
- Mapper can create research tasks from mock task objects
- Status mapping is correct
- Priority is preserved as numeric (not converted to string)
- Goal fallback from description when goal is missing
- Generated ID format is valid
- Timestamps are timezone-aware
"""

import unittest
from datetime import datetime, timezone
from uuid import uuid4

from ike_v0.schemas.research_task import ResearchTask
from ike_v0.mappers.research_task import (
    map_task_to_research_task,
    TASK_TO_RESEARCH_STATUS,
)
from ike_v0.types.ids import IKEKind


class TestResearchTaskSchema(unittest.TestCase):
    """Tests for ResearchTask schema."""

    def test_import(self):
        """ResearchTask can be imported."""
        self.assertIsNotNone(ResearchTask)

    def test_instantiation_required_fields(self):
        """ResearchTask can be instantiated with required fields."""
        now = datetime.now(timezone.utc)
        rt = ResearchTask(
            id="ike:research_task:12345678-1234-1234-1234-123456789012",
            kind="research_task",
            created_at=now,
            updated_at=now,
            task_type="discovery",
            title="Test Research Task",
            goal="Test goal",
        )
        self.assertEqual(rt.kind, "research_task")
        self.assertEqual(rt.task_type, "discovery")
        self.assertEqual(rt.title, "Test Research Task")
        self.assertEqual(rt.goal, "Test goal")
        self.assertEqual(rt.trigger_type, "manual")
        self.assertEqual(rt.priority, 2)  # Default priority is numeric 2 (medium)

    def test_timestamps_timezone_aware(self):
        """ResearchTask timestamps are timezone-aware."""
        now = datetime.now(timezone.utc)
        rt = ResearchTask(
            id="ike:research_task:12345678-1234-1234-1234-123456789012",
            kind="research_task",
            created_at=now,
            updated_at=now,
            task_type="discovery",
            title="Test",
            goal="Test",
        )
        self.assertIsNotNone(rt.created_at.tzinfo)
        self.assertIsNotNone(rt.updated_at.tzinfo)


class TestMapTaskToResearchTask(unittest.TestCase):
    """Tests for map_task_to_research_task function."""

    def test_map_from_dict(self):
        """Map a dict-like task to ResearchTask."""
        task = {
            "id": str(uuid4()),
            "title": "Test Task",
            "description": "Test description",
            "goal": "Test goal",
            "task_type": "workflow",
            "priority": 1,
            "status": "confirmed",
            "source_type": "api_test",
            "assigned_brain": "test-brain",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        rt = map_task_to_research_task(task)
        self.assertEqual(rt.kind, "research_task")
        self.assertEqual(rt.title, "Test Task")
        self.assertEqual(rt.goal, "Test goal")
        self.assertEqual(rt.task_type, "workflow")
        self.assertEqual(rt.priority, 1)  # Priority preserved as numeric
        self.assertEqual(rt.status, "open")
        self.assertEqual(rt.owner_brain, "test-brain")
        self.assertIn("mapper", rt.provenance)
        # Verify traceability: original task ID in provenance
        self.assertIn("original_task_id", rt.provenance)
        self.assertEqual(rt.provenance["original_task_id"], task["id"])

    def test_status_mapping(self):
        """Task status maps correctly to ResearchTask status."""
        status_tests = [
            ("pending", "draft"),
            ("confirmed", "open"),
            ("executing", "in_progress"),
            ("completed", "completed"),
            ("failed", "blocked"),
            ("rejected", "cancelled"),
            ("expired", "cancelled"),
        ]
        for task_status, expected_rt_status in status_tests:
            with self.subTest(task_status=task_status):
                task = {
                    "title": "Test",
                    "goal": "Test",
                    "status": task_status,
                    "priority": 2,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
                rt = map_task_to_research_task(task)
                self.assertEqual(rt.status, expected_rt_status)

    def test_priority_preserved_numeric(self):
        """Task priority (int) is preserved as numeric in ResearchTask."""
        priority_tests = [
            (0, 0),  # urgent
            (1, 1),  # high
            (2, 2),  # medium
            (3, 3),  # low
        ]
        for task_priority, expected_rt_priority in priority_tests:
            with self.subTest(task_priority=task_priority):
                task = {
                    "title": "Test",
                    "goal": "Test",
                    "status": "pending",
                    "priority": task_priority,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
                rt = map_task_to_research_task(task)
                self.assertEqual(rt.priority, expected_rt_priority)
                self.assertIsInstance(rt.priority, int)

    def test_trigger_type_inference(self):
        """Trigger type is inferred from source_type."""
        trigger_tests = [
            ("anti_crawl_test", "gap"),
            ("source_evolution", "governance"),
            ("system_health", "gap"),
            ("api_test", "manual"),
            (None, "manual"),
        ]
        for source_type, expected_trigger in trigger_tests:
            with self.subTest(source_type=source_type):
                task = {
                    "title": "Test",
                    "goal": "Test",
                    "status": "pending",
                    "priority": 2,
                    "source_type": source_type,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
                rt = map_task_to_research_task(task)
                self.assertEqual(rt.trigger_type, expected_trigger)

    def test_map_with_context(self):
        """Map with optional task_context."""
        task = {
            "title": "Test",
            "goal": "Test",
            "status": "pending",
            "priority": 2,
            "context_id": str(uuid4()),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        context = {"id": str(uuid4()), "type": "research"}
        rt = map_task_to_research_task(task, task_context=context)
        self.assertIn(str(task["context_id"]), rt.input_refs)
        self.assertIn(str(task["context_id"]), rt.references)
        self.assertTrue(rt.provenance.get("has_context"))

    def test_generated_id_format(self):
        """Map generates properly formatted IKE ID."""
        task = {
            "title": "Test",
            "goal": "Test",
            "status": "pending",
            "priority": 2,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        rt = map_task_to_research_task(task)
        self.assertTrue(rt.id.startswith("ike:research_task:"))
        self.assertEqual(len(rt.id), len("ike:research_task:") + 36)

    def test_goal_fallback_from_description(self):
        """Goal falls back to description when goal is missing."""
        task = {
            "title": "Test",
            "description": "Fallback description as goal",
            "status": "pending",
            "priority": 2,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        rt = map_task_to_research_task(task)
        self.assertEqual(rt.goal, "Fallback description as goal")

    def test_goal_fallback_default(self):
        """Goal uses default when both goal and description are missing."""
        task = {
            "title": "Test",
            "status": "pending",
            "priority": 2,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        rt = map_task_to_research_task(task)
        self.assertEqual(rt.goal, "No goal specified")

    def test_unknown_status_fallback(self):
        """Unknown task status falls back to 'draft'."""
        task = {
            "title": "Test",
            "goal": "Test",
            "status": "unknown_status",
            "priority": 2,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        rt = map_task_to_research_task(task)
        self.assertEqual(rt.status, "draft")


if __name__ == "__main__":
    unittest.main()
