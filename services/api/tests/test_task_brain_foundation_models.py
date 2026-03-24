import sys
import unittest
from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from db.models import (
    BrainFallback,
    BrainPolicy,
    BrainProfile,
    BrainRoute,
    Task,
    TaskArtifact,
    TaskContext,
    TaskHistory,
    TaskRelation,
)


class TaskBrainFoundationModelsTest(unittest.TestCase):
    def test_task_has_v1_workflow_columns(self) -> None:
        self.assertEqual(Task.__table__.c.context_id.name, "context_id")
        self.assertEqual(Task.__table__.c.task_type.name, "task_type")
        self.assertEqual(Task.__table__.c.parent_task_id.name, "parent_task_id")
        self.assertEqual(Task.__table__.c.result_summary.name, "result_summary")

    def test_task_history_has_event_fields(self) -> None:
        self.assertEqual(TaskHistory.__table__.c.context_id.name, "context_id")
        self.assertEqual(TaskHistory.__table__.c.event_type.name, "event_type")
        self.assertEqual(TaskHistory.__table__.c.payload.name, "payload")
        self.assertTrue(TaskHistory.__table__.c.task_id.nullable)

    def test_task_context_metadata_maps_correctly(self) -> None:
        self.assertEqual(TaskContext.extra.property.columns[0].name, "metadata")

    def test_task_artifact_metadata_maps_correctly(self) -> None:
        self.assertEqual(TaskArtifact.extra.property.columns[0].name, "metadata")
        self.assertTrue(TaskArtifact.__table__.c.task_id.nullable)

    def test_task_relation_metadata_maps_correctly(self) -> None:
        self.assertEqual(TaskRelation.extra.property.columns[0].name, "metadata")

    def test_brain_control_plane_tables_exist(self) -> None:
        self.assertEqual(BrainProfile.__tablename__, "brain_profiles")
        self.assertEqual(BrainRoute.__tablename__, "brain_routes")
        self.assertEqual(BrainPolicy.__tablename__, "brain_policies")
        self.assertEqual(BrainFallback.__tablename__, "brain_fallbacks")


if __name__ == "__main__":
    unittest.main()
