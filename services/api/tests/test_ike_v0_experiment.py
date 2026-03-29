"""
Minimal tests for IKE v0 Experiment schema and mapper.

Tests verify:
- Experiment schema can be imported and instantiated
- Mapper can create source_plan_comparison experiments
- Required fields are validated
- Generated ID format is valid
- Timestamps are timezone-aware
"""

import unittest
from datetime import datetime, timezone
from uuid import uuid4

from ike_v0.schemas.experiment import Experiment
from ike_v0.mappers.experiment import create_source_plan_comparison_experiment
from ike_v0.types.ids import IKEKind


class TestExperimentSchema(unittest.TestCase):
    """Tests for Experiment schema."""

    def test_import(self):
        """Experiment can be imported."""
        self.assertIsNotNone(Experiment)

    def test_instantiation_required_fields(self):
        """Experiment can be instantiated with required fields."""
        now = datetime.now(timezone.utc)
        exp = Experiment(
            id="ike:experiment:12345678-1234-1234-1234-123456789012",
            kind="experiment",
            created_at=now,
            updated_at=now,
            task_ref="ike:research_task:12345678-1234-1234-1234-123456789012",
            experiment_type="source_plan_comparison",
            title="Test Experiment",
            hypothesis="Test hypothesis",
            method_ref="test_method:v0.1",
        )
        self.assertEqual(exp.kind, "experiment")
        self.assertEqual(exp.experiment_type, "source_plan_comparison")
        self.assertEqual(exp.title, "Test Experiment")
        self.assertEqual(exp.hypothesis, "Test hypothesis")
        self.assertEqual(exp.method_ref, "test_method:v0.1")
        self.assertEqual(exp.status, "draft")
        self.assertEqual(exp.result_summary, None)

    def test_timestamps_timezone_aware(self):
        """Experiment timestamps are timezone-aware."""
        now = datetime.now(timezone.utc)
        exp = Experiment(
            id="ike:experiment:12345678-1234-1234-1234-123456789012",
            kind="experiment",
            created_at=now,
            updated_at=now,
            task_ref="ike:research_task:12345678-1234-1234-1234-123456789012",
            experiment_type="source_plan_comparison",
            title="Test",
            hypothesis="Test",
            method_ref="test",
        )
        self.assertIsNotNone(exp.created_at.tzinfo)
        self.assertIsNotNone(exp.updated_at.tzinfo)

    def test_evidence_refs_default_empty(self):
        """Evidence refs default to empty list."""
        now = datetime.now(timezone.utc)
        exp = Experiment(
            id="ike:experiment:12345678-1234-1234-1234-123456789012",
            kind="experiment",
            created_at=now,
            updated_at=now,
            task_ref="ike:research_task:12345678-1234-1234-1234-123456789012",
            experiment_type="source_plan_comparison",
            title="Test",
            hypothesis="Test",
            method_ref="test",
        )
        self.assertEqual(exp.evidence_refs, [])


class TestCreateSourcePlanComparisonExperiment(unittest.TestCase):
    """Tests for create_source_plan_comparison_experiment helper."""

    def test_create_basic(self):
        """Create a basic source_plan_comparison experiment."""
        task_ref = "ike:research_task:" + str(uuid4())
        input_a = "ike:observation:" + str(uuid4())
        input_b = "ike:observation:" + str(uuid4())
        hypothesis = "Plan A will have higher quality than Plan B"

        exp = create_source_plan_comparison_experiment(
            task_ref=task_ref,
            input_ref_a=input_a,
            input_ref_b=input_b,
            hypothesis=hypothesis,
        )

        self.assertEqual(exp.kind, "experiment")
        self.assertEqual(exp.experiment_type, "source_plan_comparison")
        self.assertEqual(exp.task_ref, task_ref)
        self.assertEqual(exp.input_refs, [input_a, input_b])
        self.assertEqual(exp.hypothesis, hypothesis)
        self.assertEqual(exp.method_ref, "source_plan_comparison:v0.1")
        self.assertEqual(exp.title, "Source Plan Comparison")
        self.assertEqual(exp.status, "draft")
        self.assertIsNone(exp.result_summary)
        self.assertIn("mapper", exp.provenance)

    def test_create_with_custom_title(self):
        """Create experiment with custom title."""
        task_ref = "ike:research_task:" + str(uuid4())
        input_a = "ike:observation:" + str(uuid4())
        input_b = "ike:observation:" + str(uuid4())

        exp = create_source_plan_comparison_experiment(
            task_ref=task_ref,
            input_ref_a=input_a,
            input_ref_b=input_b,
            hypothesis="Test",
            title="Custom Comparison Title",
        )

        self.assertEqual(exp.title, "Custom Comparison Title")

    def test_create_with_custom_method(self):
        """Create experiment with custom method reference."""
        task_ref = "ike:research_task:" + str(uuid4())
        input_a = "ike:observation:" + str(uuid4())
        input_b = "ike:observation:" + str(uuid4())

        exp = create_source_plan_comparison_experiment(
            task_ref=task_ref,
            input_ref_a=input_a,
            input_ref_b=input_b,
            hypothesis="Test",
            method_ref="custom_method:v0.2",
        )

        self.assertEqual(exp.method_ref, "custom_method:v0.2")

    def test_generated_id_format(self):
        """Experiment generates properly formatted IKE ID."""
        task_ref = "ike:research_task:" + str(uuid4())
        input_a = "ike:observation:" + str(uuid4())
        input_b = "ike:observation:" + str(uuid4())

        exp = create_source_plan_comparison_experiment(
            task_ref=task_ref,
            input_ref_a=input_a,
            input_ref_b=input_b,
            hypothesis="Test",
        )

        self.assertTrue(exp.id.startswith("ike:experiment:"))
        self.assertEqual(len(exp.id), len("ike:experiment:") + 36)

    def test_references_includes_task_ref(self):
        """References list includes the task_ref."""
        task_ref = "ike:research_task:" + str(uuid4())
        input_a = "ike:observation:" + str(uuid4())
        input_b = "ike:observation:" + str(uuid4())

        exp = create_source_plan_comparison_experiment(
            task_ref=task_ref,
            input_ref_a=input_a,
            input_ref_b=input_b,
            hypothesis="Test",
        )

        self.assertIn(task_ref, exp.references)

    def test_provenance_includes_experiment_type(self):
        """Provenance includes experiment type metadata."""
        task_ref = "ike:research_task:" + str(uuid4())
        input_a = "ike:observation:" + str(uuid4())
        input_b = "ike:observation:" + str(uuid4())

        exp = create_source_plan_comparison_experiment(
            task_ref=task_ref,
            input_ref_a=input_a,
            input_ref_b=input_b,
            hypothesis="Test",
        )

        self.assertEqual(exp.provenance.get("experiment_type"), "source_plan_comparison")
        self.assertEqual(exp.provenance.get("input_count"), 2)


if __name__ == "__main__":
    unittest.main()
