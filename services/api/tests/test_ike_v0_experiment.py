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
from ike_v0.mappers.experiment import (
    create_source_plan_comparison_experiment,
    create_claim_validation_experiment,
)
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
        plan_a = "source_plan:" + str(uuid4())
        plan_b = "source_plan:" + str(uuid4())
        hypothesis = "Plan A will have higher quality than Plan B"

        exp = create_source_plan_comparison_experiment(
            task_ref=task_ref,
            plan_a_ref=plan_a,
            plan_b_ref=plan_b,
            hypothesis=hypothesis,
        )

        self.assertEqual(exp.kind, "experiment")
        self.assertEqual(exp.experiment_type, "source_plan_comparison")
        self.assertEqual(exp.task_ref, task_ref)
        self.assertEqual(exp.input_refs, [plan_a, plan_b])
        self.assertEqual(exp.hypothesis, hypothesis)
        self.assertEqual(exp.method_ref, "source_plan_comparison:v0.1")
        self.assertEqual(exp.title, "Source Plan Comparison")
        self.assertEqual(exp.status, "draft")
        self.assertIsNone(exp.result_summary)
        self.assertIn("mapper", exp.provenance)

    def test_create_with_custom_title(self):
        """Create experiment with custom title."""
        task_ref = "ike:research_task:" + str(uuid4())
        plan_a = "source_plan:" + str(uuid4())
        plan_b = "source_plan:" + str(uuid4())

        exp = create_source_plan_comparison_experiment(
            task_ref=task_ref,
            plan_a_ref=plan_a,
            plan_b_ref=plan_b,
            hypothesis="Test",
            title="Custom Comparison Title",
        )

        self.assertEqual(exp.title, "Custom Comparison Title")

    def test_create_with_custom_method(self):
        """Create experiment with custom method reference."""
        task_ref = "ike:research_task:" + str(uuid4())
        plan_a = "source_plan:" + str(uuid4())
        plan_b = "source_plan:" + str(uuid4())

        exp = create_source_plan_comparison_experiment(
            task_ref=task_ref,
            plan_a_ref=plan_a,
            plan_b_ref=plan_b,
            hypothesis="Test",
            method_ref="custom_method:v0.2",
        )

        self.assertEqual(exp.method_ref, "custom_method:v0.2")

    def test_generated_id_format(self):
        """Experiment generates properly formatted IKE ID."""
        task_ref = "ike:research_task:" + str(uuid4())
        plan_a = "source_plan:" + str(uuid4())
        plan_b = "source_plan:" + str(uuid4())

        exp = create_source_plan_comparison_experiment(
            task_ref=task_ref,
            plan_a_ref=plan_a,
            plan_b_ref=plan_b,
            hypothesis="Test",
        )

        self.assertTrue(exp.id.startswith("ike:experiment:"))
        self.assertEqual(len(exp.id), len("ike:experiment:") + 36)

    def test_references_includes_task_and_plans(self):
        """References list includes task_ref and both plan refs."""
        task_ref = "ike:research_task:" + str(uuid4())
        plan_a = "source_plan:" + str(uuid4())
        plan_b = "source_plan:" + str(uuid4())

        exp = create_source_plan_comparison_experiment(
            task_ref=task_ref,
            plan_a_ref=plan_a,
            plan_b_ref=plan_b,
            hypothesis="Test",
        )

        self.assertIn(task_ref, exp.references)
        self.assertIn(plan_a, exp.references)
        self.assertIn(plan_b, exp.references)

    def test_provenance_includes_experiment_type(self):
        """Provenance includes experiment type metadata."""
        task_ref = "ike:research_task:" + str(uuid4())
        plan_a = "source_plan:" + str(uuid4())
        plan_b = "source_plan:" + str(uuid4())

        exp = create_source_plan_comparison_experiment(
            task_ref=task_ref,
            plan_a_ref=plan_a,
            plan_b_ref=plan_b,
            hypothesis="Test",
        )

        self.assertEqual(exp.provenance.get("experiment_type"), "source_plan_comparison")
        self.assertEqual(exp.provenance.get("input_count"), 2)

    def test_provenance_includes_plan_refs(self):
        """Provenance includes explicit plan_a_ref and plan_b_ref for traceability."""
        task_ref = "ike:research_task:" + str(uuid4())
        plan_a = "source_plan:" + str(uuid4())
        plan_b = "source_plan:" + str(uuid4())

        exp = create_source_plan_comparison_experiment(
            task_ref=task_ref,
            plan_a_ref=plan_a,
            plan_b_ref=plan_b,
            hypothesis="Test",
        )

        self.assertEqual(exp.provenance.get("plan_a_ref"), plan_a)
        self.assertEqual(exp.provenance.get("plan_b_ref"), plan_b)

    def test_provenance_includes_source_domain(self):
        """Provenance includes source_domain when provided."""
        task_ref = "ike:research_task:" + str(uuid4())
        plan_a = "source_plan:" + str(uuid4())
        plan_b = "source_plan:" + str(uuid4())

        exp = create_source_plan_comparison_experiment(
            task_ref=task_ref,
            plan_a_ref=plan_a,
            plan_b_ref=plan_b,
            hypothesis="Test",
            source_domain="github.com",
        )

        self.assertEqual(exp.provenance.get("source_domain"), "github.com")

    def test_provenance_includes_plan_versions(self):
        """Provenance includes plan_versions when provided."""
        task_ref = "ike:research_task:" + str(uuid4())
        plan_a = "source_plan_version:" + str(uuid4())
        plan_b = "source_plan_version:" + str(uuid4())
        plan_versions = {
            plan_a: "v1.2.0",
            plan_b: "v1.3.0",
        }

        exp = create_source_plan_comparison_experiment(
            task_ref=task_ref,
            plan_a_ref=plan_a,
            plan_b_ref=plan_b,
            hypothesis="Test",
            plan_versions=plan_versions,
        )

        self.assertEqual(exp.provenance.get("plan_versions"), plan_versions)

    def test_input_refs_order(self):
        """Input refs maintains plan_a first, plan_b second order."""
        task_ref = "ike:research_task:" + str(uuid4())
        plan_a = "source_plan:" + str(uuid4())
        plan_b = "source_plan:" + str(uuid4())

        exp = create_source_plan_comparison_experiment(
            task_ref=task_ref,
            plan_a_ref=plan_a,
            plan_b_ref=plan_b,
            hypothesis="Test",
        )

        self.assertEqual(exp.input_refs[0], plan_a)
        self.assertEqual(exp.input_refs[1], plan_b)

    def test_create_with_source_plan_versions(self):
        """Create experiment with source_plan_version refs for version comparison."""
        task_ref = "ike:research_task:" + str(uuid4())
        plan_a = "source_plan_version:" + str(uuid4())
        plan_b = "source_plan_version:" + str(uuid4())

        exp = create_source_plan_comparison_experiment(
            task_ref=task_ref,
            plan_a_ref=plan_a,
            plan_b_ref=plan_b,
            hypothesis="Version B has improved coverage over Version A",
        )

        self.assertEqual(exp.experiment_type, "source_plan_comparison")
        self.assertEqual(exp.input_refs, [plan_a, plan_b])
        self.assertIn(plan_a, exp.references)
        self.assertIn(plan_b, exp.references)


class TestCreateClaimValidationExperiment(unittest.TestCase):
    """Tests for create_claim_validation_experiment helper."""

    def test_create_basic(self):
        """Create a basic claim_validation experiment."""
        task_ref = "ike:research_task:" + str(uuid4())
        claim_ref = "ike:claim:" + str(uuid4())
        hypothesis = "The claim is valid and supported by evidence"

        exp = create_claim_validation_experiment(
            task_ref=task_ref,
            claim_ref=claim_ref,
            hypothesis=hypothesis,
        )

        self.assertEqual(exp.kind, "experiment")
        self.assertEqual(exp.experiment_type, "claim_validation")
        self.assertEqual(exp.task_ref, task_ref)
        self.assertEqual(exp.input_refs, [claim_ref])
        self.assertEqual(exp.hypothesis, hypothesis)
        self.assertEqual(exp.method_ref, "claim_validation:v0.1")
        self.assertEqual(exp.title, "Claim Validation")
        self.assertEqual(exp.status, "draft")
        self.assertIsNone(exp.result_summary)
        self.assertIn("mapper", exp.provenance)

    def test_create_with_custom_title(self):
        """Create experiment with custom title."""
        task_ref = "ike:research_task:" + str(uuid4())
        claim_ref = "ike:claim:" + str(uuid4())

        exp = create_claim_validation_experiment(
            task_ref=task_ref,
            claim_ref=claim_ref,
            hypothesis="Test",
            title="Validate Organization Claim",
        )

        self.assertEqual(exp.title, "Validate Organization Claim")

    def test_create_with_custom_method(self):
        """Create experiment with custom method reference."""
        task_ref = "ike:research_task:" + str(uuid4())
        claim_ref = "ike:claim:" + str(uuid4())

        exp = create_claim_validation_experiment(
            task_ref=task_ref,
            claim_ref=claim_ref,
            hypothesis="Test",
            method_ref="claim_validation:v0.2",
        )

        self.assertEqual(exp.method_ref, "claim_validation:v0.2")

    def test_create_with_evidence_refs(self):
        """Create experiment with supporting evidence refs."""
        task_ref = "ike:research_task:" + str(uuid4())
        claim_ref = "ike:claim:" + str(uuid4())
        evidence_refs = [
            "ike:observation:" + str(uuid4()),
            "ike:entity:" + str(uuid4()),
        ]

        exp = create_claim_validation_experiment(
            task_ref=task_ref,
            claim_ref=claim_ref,
            hypothesis="Test",
            evidence_refs=evidence_refs,
        )

        self.assertEqual(exp.evidence_refs, evidence_refs)
        self.assertEqual(exp.provenance.get("evidence_count"), 2)

    def test_generated_id_format(self):
        """Experiment generates properly formatted IKE ID."""
        task_ref = "ike:research_task:" + str(uuid4())
        claim_ref = "ike:claim:" + str(uuid4())

        exp = create_claim_validation_experiment(
            task_ref=task_ref,
            claim_ref=claim_ref,
            hypothesis="Test",
        )

        self.assertTrue(exp.id.startswith("ike:experiment:"))
        self.assertEqual(len(exp.id), len("ike:experiment:") + 36)

    def test_references_includes_task_and_claim(self):
        """References list includes task_ref and claim_ref."""
        task_ref = "ike:research_task:" + str(uuid4())
        claim_ref = "ike:claim:" + str(uuid4())

        exp = create_claim_validation_experiment(
            task_ref=task_ref,
            claim_ref=claim_ref,
            hypothesis="Test",
        )

        self.assertIn(task_ref, exp.references)
        self.assertIn(claim_ref, exp.references)

    def test_references_includes_evidence(self):
        """References list includes evidence refs when provided."""
        task_ref = "ike:research_task:" + str(uuid4())
        claim_ref = "ike:claim:" + str(uuid4())
        evidence_refs = [
            "ike:observation:" + str(uuid4()),
            "ike:entity:" + str(uuid4()),
        ]

        exp = create_claim_validation_experiment(
            task_ref=task_ref,
            claim_ref=claim_ref,
            hypothesis="Test",
            evidence_refs=evidence_refs,
        )

        for ref in evidence_refs:
            self.assertIn(ref, exp.references)

    def test_provenance_includes_experiment_type(self):
        """Provenance includes experiment type metadata."""
        task_ref = "ike:research_task:" + str(uuid4())
        claim_ref = "ike:claim:" + str(uuid4())

        exp = create_claim_validation_experiment(
            task_ref=task_ref,
            claim_ref=claim_ref,
            hypothesis="Test",
        )

        self.assertEqual(exp.provenance.get("experiment_type"), "claim_validation")
        self.assertEqual(exp.provenance.get("claim_ref"), claim_ref)

    def test_provenance_includes_claim_ref(self):
        """Provenance includes explicit claim_ref for traceability."""
        task_ref = "ike:research_task:" + str(uuid4())
        claim_ref = "ike:claim:" + str(uuid4())

        exp = create_claim_validation_experiment(
            task_ref=task_ref,
            claim_ref=claim_ref,
            hypothesis="Test",
        )

        self.assertEqual(exp.provenance.get("claim_ref"), claim_ref)
        self.assertEqual(exp.provenance.get("mapper"), "create_claim_validation_experiment")

    def test_input_refs_contains_claim(self):
        """Input refs contains the claim ref as primary input."""
        task_ref = "ike:research_task:" + str(uuid4())
        claim_ref = "ike:claim:" + str(uuid4())

        exp = create_claim_validation_experiment(
            task_ref=task_ref,
            claim_ref=claim_ref,
            hypothesis="Test",
        )

        self.assertEqual(exp.input_refs, [claim_ref])


if __name__ == "__main__":
    unittest.main()
