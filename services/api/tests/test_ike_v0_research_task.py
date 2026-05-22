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
from ike_v0.schemas.observation import Observation
from ike_v0.schemas.entity import Entity
from ike_v0.schemas.claim import Claim
from ike_v0.mappers.research_task import (
    map_task_to_research_task,
    TASK_TO_RESEARCH_STATUS,
    derive_research_task_from_entity_claim,
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

    def test_trigger_type_evolution_governance(self):
        """Evolution source_type triggers governance."""
        task = {
            "title": "Evolution Issue",
            "goal": "Fix quality issue",
            "status": "pending",
            "priority": 1,
            "source_type": "evolution_quality_check",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        rt = map_task_to_research_task(task)
        self.assertEqual(rt.trigger_type, "governance")

    def test_trigger_type_health_gap(self):
        """System health source_type triggers gap."""
        task = {
            "title": "Health Check Failed",
            "goal": "Investigate health issue",
            "status": "pending",
            "priority": 0,
            "source_type": "system_health",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        rt = map_task_to_research_task(task)
        self.assertEqual(rt.trigger_type, "gap")

    def test_trigger_type_quality_gap(self):
        """Quality issue source_type triggers gap."""
        task = {
            "title": "Quality Issue",
            "goal": "Address quality gap",
            "status": "pending",
            "priority": 1,
            "source_type": "quality_check",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        rt = map_task_to_research_task(task)
        self.assertEqual(rt.trigger_type, "gap")

    def test_artifact_refs_in_input_refs(self):
        """Artifact refs from task are included in input_refs."""
        artifact_refs = [
            "artifact-001",
            "artifact-002",
        ]
        task = {
            "title": "Test",
            "goal": "Test",
            "status": "pending",
            "priority": 2,
            "artifact_refs": artifact_refs,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        rt = map_task_to_research_task(task)
        for ref in artifact_refs:
            self.assertIn(ref, rt.input_refs)

    def test_artifact_refs_in_references(self):
        """Artifact refs from task are included in references."""
        artifact_refs = [
            "artifact-001",
            "artifact-002",
        ]
        task = {
            "title": "Test",
            "goal": "Test",
            "status": "pending",
            "priority": 2,
            "artifact_refs": artifact_refs,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        rt = map_task_to_research_task(task)
        for ref in artifact_refs:
            self.assertIn(ref, rt.references)

    def test_provenance_includes_artifact_count(self):
        """Provenance includes artifact count when artifacts present."""
        artifact_refs = ["artifact-001", "artifact-002", "artifact-003"]
        task = {
            "id": str(uuid4()),
            "title": "Test",
            "goal": "Test",
            "status": "pending",
            "priority": 2,
            "artifact_refs": artifact_refs,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        rt = map_task_to_research_task(task)
        self.assertEqual(rt.provenance.get("artifact_count"), 3)
        self.assertEqual(rt.provenance.get("original_task_id"), task["id"])

    def test_provenance_includes_context_id(self):
        """Provenance includes context_id when task_context provided."""
        task = {
            "id": str(uuid4()),
            "title": "Test",
            "goal": "Test",
            "status": "pending",
            "priority": 2,
            "context_id": "context-123",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        context = {"id": "context-123", "type": "evolution"}
        rt = map_task_to_research_task(task, task_context=context)
        self.assertTrue(rt.provenance.get("has_context"))
        self.assertEqual(rt.provenance.get("context_id"), "context-123")

    def test_owner_brain_preserved(self):
        """Owner brain is preserved from task substrate."""
        task = {
            "title": "Test",
            "goal": "Test",
            "status": "pending",
            "priority": 2,
            "assigned_brain": "evolution-chief-brain",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        rt = map_task_to_research_task(task)
        self.assertEqual(rt.owner_brain, "evolution-chief-brain")

    def test_input_refs_order_context_first(self):
        """Context ID appears first in input_refs, then artifacts."""
        artifact_refs = ["artifact-001", "artifact-002"]
        task = {
            "title": "Test",
            "goal": "Test",
            "status": "pending",
            "priority": 2,
            "context_id": "context-123",
            "artifact_refs": artifact_refs,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        rt = map_task_to_research_task(task)
        self.assertEqual(rt.input_refs[0], "context-123")
        self.assertIn("artifact-001", rt.input_refs)
        self.assertIn("artifact-002", rt.input_refs)


class TestDeriveResearchTaskFromEntityClaim(unittest.TestCase):
    """Tests for derive_research_task_from_entity_claim helper."""

    def _make_test_objects(self):
        """Create test Observation, Entity, and Claim objects."""
        now = datetime.now(timezone.utc)

        obs = Observation(
            id="ike:observation:" + str(uuid4()),
            kind="observation",
            created_at=now,
            updated_at=now,
            source_ref="source:test",
            observed_at=now,
            captured_at=now,
            title="Test Observation",
            summary="Test summary",
        )

        entity = Entity(
            id="ike:entity:" + str(uuid4()),
            kind="entity",
            created_at=now,
            updated_at=now,
            entity_type="organization",
            canonical_key="org:test",
            display_name="Test Org",
        )

        claim = Claim(
            id="ike:claim:" + str(uuid4()),
            kind="claim",
            created_at=now,
            updated_at=now,
            claim_type="capability",
            statement="Test Org has AI capabilities",
            subject_refs=[entity.id],
            source_observation_refs=[obs.id],
        )

        return obs, entity, claim

    def test_derive_basic(self):
        """Derive ResearchTask from Entity/Claim/Observation."""
        obs, entity, claim = self._make_test_objects()

        rt = derive_research_task_from_entity_claim(obs, entity, claim)

        self.assertEqual(rt.kind, "research_task")
        self.assertEqual(rt.task_type, "discovery")
        self.assertEqual(rt.trigger_type, "gap")
        self.assertEqual(rt.status, "draft")
        self.assertEqual(rt.priority, 2)

    def test_derive_input_refs(self):
        """Derived task includes all source objects in input_refs."""
        obs, entity, claim = self._make_test_objects()

        rt = derive_research_task_from_entity_claim(obs, entity, claim)

        self.assertIn(obs.id, rt.input_refs)
        self.assertIn(entity.id, rt.input_refs)
        self.assertIn(claim.id, rt.input_refs)
        self.assertEqual(len(rt.input_refs), 3)

    def test_derive_references(self):
        """Derived task includes all source objects in references."""
        obs, entity, claim = self._make_test_objects()

        rt = derive_research_task_from_entity_claim(obs, entity, claim)

        self.assertIn(obs.id, rt.references)
        self.assertIn(entity.id, rt.references)
        self.assertIn(claim.id, rt.references)

    def test_derive_provenance(self):
        """Derived task has explicit provenance trace."""
        obs, entity, claim = self._make_test_objects()

        rt = derive_research_task_from_entity_claim(obs, entity, claim)

        self.assertEqual(rt.provenance.get("mapper"), "derive_research_task_from_entity_claim")
        self.assertEqual(rt.provenance.get("source_observation_id"), obs.id)
        self.assertEqual(rt.provenance.get("source_entity_id"), entity.id)
        self.assertEqual(rt.provenance.get("source_claim_id"), claim.id)
        self.assertEqual(rt.provenance.get("derivation_path"), "observation -> entity/claim -> research_task")

    def test_derive_title_from_claim(self):
        """Derived task title is derived from claim statement."""
        obs, entity, claim = self._make_test_objects()

        rt = derive_research_task_from_entity_claim(obs, entity, claim)

        self.assertIn("Investigate", rt.title)
        self.assertIn("AI capabilities", rt.title)

    def test_derive_custom_title(self):
        """Derived task uses custom title when provided."""
        obs, entity, claim = self._make_test_objects()

        rt = derive_research_task_from_entity_claim(
            obs, entity, claim, title="Custom Research Task"
        )

        self.assertEqual(rt.title, "Custom Research Task")

    def test_derive_goal_from_claim(self):
        """Derived task goal is derived from claim statement."""
        obs, entity, claim = self._make_test_objects()

        rt = derive_research_task_from_entity_claim(obs, entity, claim)

        self.assertIn("Validate claim", rt.goal)
        self.assertIn("AI capabilities", rt.goal)

    def test_derive_custom_goal(self):
        """Derived task uses custom goal when provided."""
        obs, entity, claim = self._make_test_objects()

        rt = derive_research_task_from_entity_claim(
            obs, entity, claim, goal="Custom research goal"
        )

        self.assertEqual(rt.goal, "Custom research goal")

    def test_derive_custom_task_type(self):
        """Derived task uses custom task_type when provided."""
        obs, entity, claim = self._make_test_objects()

        rt = derive_research_task_from_entity_claim(
            obs, entity, claim, task_type="validation"
        )

        self.assertEqual(rt.task_type, "validation")

    def test_derive_assigned_brain(self):
        """Derived task preserves assigned_brain when provided."""
        obs, entity, claim = self._make_test_objects()

        rt = derive_research_task_from_entity_claim(
            obs, entity, claim, assigned_brain="research-brain-001"
        )

        self.assertEqual(rt.owner_brain, "research-brain-001")

    def test_derive_generated_id_format(self):
        """Derived task generates properly formatted IKE ID."""
        obs, entity, claim = self._make_test_objects()

        rt = derive_research_task_from_entity_claim(obs, entity, claim)

        self.assertTrue(rt.id.startswith("ike:research_task:"))
        self.assertEqual(len(rt.id), len("ike:research_task:") + 36)

    def test_derive_preserves_object_ids(self):
        """Derived task correctly extracts IDs from objects."""
        obs, entity, claim = self._make_test_objects()

        rt = derive_research_task_from_entity_claim(obs, entity, claim)

        self.assertEqual(rt.provenance["source_observation_id"], obs.id)
        self.assertEqual(rt.provenance["source_entity_id"], entity.id)
        self.assertEqual(rt.provenance["source_claim_id"], claim.id)


if __name__ == "__main__":
    unittest.main()
