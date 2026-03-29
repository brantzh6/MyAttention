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
from ike_v0.mappers.decision import create_experiment_evaluation_decision
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


if __name__ == "__main__":
    unittest.main()
