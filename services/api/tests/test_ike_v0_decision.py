"""
Minimal tests for IKE v0 Decision schema and mapper.

Tests verify:
- Decision schema can be imported and instantiated
- Mapper can create experiment_evaluation decisions
- Required fields are validated
- Generated ID format is valid
- Timestamps are timezone-aware
- Review status logic is correct
"""

import unittest
from datetime import datetime, timezone
from uuid import uuid4

from ike_v0.schemas.decision import Decision
from ike_v0.schemas.research_task import ResearchTask
from ike_v0.schemas.experiment import Experiment
from ike_v0.mappers.decision import (
    create_experiment_evaluation_decision,
    derive_decision_from_experiment,
)
from ike_v0.types.ids import IKEKind


class TestDecisionSchema(unittest.TestCase):
    """Tests for Decision schema."""

    def test_import(self):
        """Decision can be imported."""
        self.assertIsNotNone(Decision)

    def test_instantiation_required_fields(self):
        """Decision can be instantiated with required fields."""
        now = datetime.now(timezone.utc)
        dec = Decision(
            id="ike:decision:12345678-1234-1234-1234-123456789012",
            kind="decision",
            created_at=now,
            updated_at=now,
            task_ref="ike:research_task:12345678-1234-1234-1234-123456789012",
            experiment_refs=[],
            decision_type="experiment_evaluation",
            decision_outcome="adopt",
            rationale="Test rationale",
        )
        self.assertEqual(dec.kind, "decision")
        self.assertEqual(dec.decision_type, "experiment_evaluation")
        self.assertEqual(dec.decision_outcome, "adopt")
        self.assertEqual(dec.rationale, "Test rationale")
        self.assertEqual(dec.status, "draft")
        self.assertEqual(dec.review_required, False)
        self.assertEqual(dec.review_status, None)

    def test_timestamps_timezone_aware(self):
        """Decision timestamps are timezone-aware."""
        now = datetime.now(timezone.utc)
        dec = Decision(
            id="ike:decision:12345678-1234-1234-1234-123456789012",
            kind="decision",
            created_at=now,
            updated_at=now,
            task_ref="ike:research_task:12345678-1234-1234-1234-123456789012",
            experiment_refs=[],
            decision_type="experiment_evaluation",
            decision_outcome="adopt",
            rationale="Test",
        )
        self.assertIsNotNone(dec.created_at.tzinfo)
        self.assertIsNotNone(dec.updated_at.tzinfo)

    def test_evidence_refs_default_empty(self):
        """Evidence refs default to empty list."""
        now = datetime.now(timezone.utc)
        dec = Decision(
            id="ike:decision:12345678-1234-1234-1234-123456789012",
            kind="decision",
            created_at=now,
            updated_at=now,
            task_ref="ike:research_task:12345678-1234-1234-1234-123456789012",
            experiment_refs=[],
            decision_type="experiment_evaluation",
            decision_outcome="adopt",
            rationale="Test",
        )
        self.assertEqual(dec.evidence_refs, [])

    def test_review_required_sets_status(self):
        """Review required flag affects status and review_status."""
        now = datetime.now(timezone.utc)
        dec = Decision(
            id="ike:decision:12345678-1234-1234-1234-123456789012",
            kind="decision",
            created_at=now,
            updated_at=now,
            task_ref="ike:research_task:12345678-1234-1234-1234-123456789012",
            experiment_refs=[],
            decision_type="experiment_evaluation",
            decision_outcome="adopt",
            rationale="Test",
            review_required=True,
            review_status="pending",
        )
        self.assertEqual(dec.review_required, True)
        self.assertEqual(dec.review_status, "pending")

    def test_invalid_decision_outcome_rejected(self):
        """Invalid decision_outcome values are rejected by the schema."""
        now = datetime.now(timezone.utc)
        invalid_outcomes = ["approved", "rejected", "needs_revision", "invalid", ""]
        
        for invalid_outcome in invalid_outcomes:
            with self.subTest(invalid_outcome=invalid_outcome):
                with self.assertRaises(Exception):  # pydantic.ValidationError
                    Decision(
                        id="ike:decision:12345678-1234-1234-1234-123456789012",
                        kind="decision",
                        created_at=now,
                        updated_at=now,
                        task_ref="ike:research_task:12345678-1234-1234-1234-123456789012",
                        experiment_refs=[],
                        decision_type="experiment_evaluation",
                        decision_outcome=invalid_outcome,
                        rationale="Test",
                    )


class TestCreateExperimentEvaluationDecision(unittest.TestCase):
    """Tests for create_experiment_evaluation_decision helper."""

    def test_create_basic(self):
        """Create a basic experiment_evaluation decision."""
        task_ref = "ike:research_task:" + str(uuid4())
        exp_ref = "ike:experiment:" + str(uuid4())
        outcome = "adopt"
        rationale = "The experiment results support the hypothesis"

        dec = create_experiment_evaluation_decision(
            task_ref=task_ref,
            experiment_refs=[exp_ref],
            decision_outcome=outcome,
            rationale=rationale,
        )

        self.assertEqual(dec.kind, "decision")
        self.assertEqual(dec.decision_type, "experiment_evaluation")
        self.assertEqual(dec.task_ref, task_ref)
        self.assertEqual(dec.experiment_refs, [exp_ref])
        self.assertEqual(dec.decision_outcome, outcome)
        self.assertEqual(dec.rationale, rationale)
        self.assertEqual(dec.status, "draft")
        self.assertEqual(dec.review_required, False)
        self.assertEqual(dec.review_status, None)
        self.assertIn("mapper", dec.provenance)

    def test_create_with_multiple_experiments(self):
        """Create decision with multiple experiment references."""
        task_ref = "ike:research_task:" + str(uuid4())
        exp_refs = [
            "ike:experiment:" + str(uuid4()),
            "ike:experiment:" + str(uuid4()),
            "ike:experiment:" + str(uuid4()),
        ]

        dec = create_experiment_evaluation_decision(
            task_ref=task_ref,
            experiment_refs=exp_refs,
            decision_outcome="adopt",
            rationale="Test",
        )

        self.assertEqual(len(dec.experiment_refs), 3)
        self.assertEqual(dec.provenance.get("experiment_count"), 3)

    def test_create_with_review_required(self):
        """Create decision requiring review."""
        task_ref = "ike:research_task:" + str(uuid4())
        exp_ref = "ike:experiment:" + str(uuid4())

        dec = create_experiment_evaluation_decision(
            task_ref=task_ref,
            experiment_refs=[exp_ref],
            decision_outcome="adopt",
            rationale="Test",
            review_required=True,
        )

        self.assertEqual(dec.review_required, True)
        self.assertEqual(dec.review_status, "pending")
        self.assertEqual(dec.status, "pending_review")

    def test_create_with_evidence_refs(self):
        """Create decision with additional evidence references."""
        task_ref = "ike:research_task:" + str(uuid4())
        exp_ref = "ike:experiment:" + str(uuid4())
        evidence_refs = [
            "ike:observation:" + str(uuid4()),
            "ike:observation:" + str(uuid4()),
        ]

        dec = create_experiment_evaluation_decision(
            task_ref=task_ref,
            experiment_refs=[exp_ref],
            decision_outcome="adopt",
            rationale="Test",
            evidence_refs=evidence_refs,
        )

        self.assertEqual(dec.evidence_refs, evidence_refs)

    def test_generated_id_format(self):
        """Decision generates properly formatted IKE ID."""
        task_ref = "ike:research_task:" + str(uuid4())
        exp_ref = "ike:experiment:" + str(uuid4())

        dec = create_experiment_evaluation_decision(
            task_ref=task_ref,
            experiment_refs=[exp_ref],
            decision_outcome="adopt",
            rationale="Test",
        )

        self.assertTrue(dec.id.startswith("ike:decision:"))
        self.assertEqual(len(dec.id), len("ike:decision:") + 36)

    def test_references_includes_task_and_experiments(self):
        """References list includes task_ref and experiment_refs."""
        task_ref = "ike:research_task:" + str(uuid4())
        exp_ref_a = "ike:experiment:" + str(uuid4())
        exp_ref_b = "ike:experiment:" + str(uuid4())

        dec = create_experiment_evaluation_decision(
            task_ref=task_ref,
            experiment_refs=[exp_ref_a, exp_ref_b],
            decision_outcome="adopt",
            rationale="Test",
        )

        self.assertIn(task_ref, dec.references)
        self.assertIn(exp_ref_a, dec.references)
        self.assertIn(exp_ref_b, dec.references)

    def test_provenance_includes_decision_type(self):
        """Provenance includes decision type metadata."""
        task_ref = "ike:research_task:" + str(uuid4())
        exp_ref = "ike:experiment:" + str(uuid4())

        dec = create_experiment_evaluation_decision(
            task_ref=task_ref,
            experiment_refs=[exp_ref],
            decision_outcome="adopt",
            rationale="Test",
        )

        self.assertEqual(dec.provenance.get("decision_type"), "experiment_evaluation")
        self.assertEqual(dec.provenance.get("experiment_count"), 1)

    def test_decision_outcome_vocabulary(self):
        """Test all valid IKE v0 decision outcome values."""
        task_ref = "ike:research_task:" + str(uuid4())
        exp_ref = "ike:experiment:" + str(uuid4())
        
        valid_outcomes = ["adopt", "reject", "defer", "escalate"]
        for outcome in valid_outcomes:
            with self.subTest(outcome=outcome):
                dec = create_experiment_evaluation_decision(
                    task_ref=task_ref,
                    experiment_refs=[exp_ref],
                    decision_outcome=outcome,
                    rationale="Test",
                )
                self.assertEqual(dec.decision_outcome, outcome)


class TestDeriveDecisionFromExperiment(unittest.TestCase):
    """Tests for derive_decision_from_experiment helper."""

    def _make_test_objects(self):
        """Create test ResearchTask and Experiment objects."""
        now = datetime.now(timezone.utc)

        task = ResearchTask(
            id="ike:research_task:" + str(uuid4()),
            kind="research_task",
            created_at=now,
            updated_at=now,
            task_type="discovery",
            title="Test Research Task",
            goal="Test goal",
        )

        exp = Experiment(
            id="ike:experiment:" + str(uuid4()),
            kind="experiment",
            created_at=now,
            updated_at=now,
            task_ref=task.id,
            experiment_type="claim_validation",
            title="Test Experiment",
            hypothesis="Test hypothesis",
            method_ref="test_method:v0.1",
        )

        return task, exp

    def test_derive_basic(self):
        """Derive Decision from ResearchTask and Experiment."""
        task, exp = self._make_test_objects()

        dec = derive_decision_from_experiment(
            task=task,
            experiment=exp,
            decision_outcome="adopt",
        )

        self.assertEqual(dec.kind, "decision")
        self.assertEqual(dec.decision_type, "experiment_evaluation")
        self.assertEqual(dec.decision_outcome, "adopt")
        self.assertEqual(dec.status, "draft")
        self.assertEqual(dec.review_required, False)

    def test_derive_task_ref(self):
        """Derived decision includes correct task_ref."""
        task, exp = self._make_test_objects()

        dec = derive_decision_from_experiment(
            task=task,
            experiment=exp,
            decision_outcome="adopt",
        )

        self.assertEqual(dec.task_ref, task.id)

    def test_derive_experiment_refs(self):
        """Derived decision includes experiment in experiment_refs."""
        task, exp = self._make_test_objects()

        dec = derive_decision_from_experiment(
            task=task,
            experiment=exp,
            decision_outcome="adopt",
        )

        self.assertEqual(dec.experiment_refs, [exp.id])

    def test_derive_references(self):
        """Derived decision includes task and experiment in references."""
        task, exp = self._make_test_objects()

        dec = derive_decision_from_experiment(
            task=task,
            experiment=exp,
            decision_outcome="adopt",
        )

        self.assertIn(task.id, dec.references)
        self.assertIn(exp.id, dec.references)

    def test_derive_provenance(self):
        """Derived decision has explicit provenance trace."""
        task, exp = self._make_test_objects()

        dec = derive_decision_from_experiment(
            task=task,
            experiment=exp,
            decision_outcome="adopt",
        )

        self.assertEqual(dec.provenance.get("mapper"), "derive_decision_from_experiment")
        self.assertEqual(dec.provenance.get("source_task_id"), task.id)
        self.assertEqual(dec.provenance.get("source_experiment_id"), exp.id)
        self.assertEqual(dec.provenance.get("derivation_path"), "research_task -> experiment -> decision")

    def test_derive_rationale_from_experiment(self):
        """Derived decision rationale is derived from experiment hypothesis."""
        task, exp = self._make_test_objects()

        dec = derive_decision_from_experiment(
            task=task,
            experiment=exp,
            decision_outcome="adopt",
        )

        self.assertIn("Test hypothesis", dec.rationale)

    def test_derive_custom_rationale(self):
        """Derived decision uses custom rationale when provided."""
        task, exp = self._make_test_objects()

        dec = derive_decision_from_experiment(
            task=task,
            experiment=exp,
            decision_outcome="adopt",
            rationale="Custom rationale",
        )

        self.assertEqual(dec.rationale, "Custom rationale")

    def test_derive_review_required(self):
        """Derived decision respects review_required flag."""
        task, exp = self._make_test_objects()

        dec = derive_decision_from_experiment(
            task=task,
            experiment=exp,
            decision_outcome="adopt",
            review_required=True,
        )

        self.assertTrue(dec.review_required)
        self.assertEqual(dec.review_status, "pending")
        self.assertEqual(dec.status, "pending_review")

    def test_derive_evidence_refs_from_experiment(self):
        """Derived decision includes experiment's evidence_refs."""
        task, exp = self._make_test_objects()
        exp.evidence_refs = ["ike:observation:" + str(uuid4())]

        dec = derive_decision_from_experiment(
            task=task,
            experiment=exp,
            decision_outcome="adopt",
        )

        self.assertEqual(dec.evidence_refs, exp.evidence_refs)

    def test_derive_generated_id_format(self):
        """Derived decision generates properly formatted IKE ID."""
        task, exp = self._make_test_objects()

        dec = derive_decision_from_experiment(
            task=task,
            experiment=exp,
            decision_outcome="adopt",
        )

        self.assertTrue(dec.id.startswith("ike:decision:"))
        self.assertEqual(len(dec.id), len("ike:decision:") + 36)

    def test_derive_all_outcomes(self):
        """Derived decision supports all valid IKE v0 outcomes."""
        task, exp = self._make_test_objects()
        valid_outcomes = ["adopt", "reject", "defer", "escalate"]

        for outcome in valid_outcomes:
            with self.subTest(outcome=outcome):
                dec = derive_decision_from_experiment(
                    task=task,
                    experiment=exp,
                    decision_outcome=outcome,
                )
                self.assertEqual(dec.decision_outcome, outcome)


if __name__ == "__main__":
    unittest.main()
