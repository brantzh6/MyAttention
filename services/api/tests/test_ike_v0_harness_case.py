"""
Minimal tests for IKE v0 HarnessCase schema and mapper.

Tests verify:
- HarnessCase schema can be imported and instantiated
- Mapper can create loop_completeness harness cases
- Required fields are validated
- Generated ID format is valid
- Timestamps are timezone-aware
- Pass/fail logic affects status correctly
"""

import unittest
from datetime import datetime, timezone
from uuid import uuid4

from ike_v0.schemas.harness_case import HarnessCase
from ike_v0.mappers.harness_case import create_loop_completeness_harness_case
from ike_v0.types.ids import IKEKind


class TestHarnessCaseSchema(unittest.TestCase):
    """Tests for HarnessCase schema."""

    def test_import(self):
        """HarnessCase can be imported."""
        self.assertIsNotNone(HarnessCase)

    def test_instantiation_required_fields(self):
        """HarnessCase can be instantiated with required fields."""
        now = datetime.now(timezone.utc)
        hc = HarnessCase(
            id="ike:harness_case:12345678-1234-1234-1234-123456789012",
            kind="harness_case",
            created_at=now,
            updated_at=now,
            case_type="loop_completeness",
            subject_refs=["ike:research_task:" + str(uuid4())],
            expected_behavior={"has_task": True, "has_experiment": True, "has_decision": True},
            actual_behavior={"has_task": True, "has_experiment": True, "has_decision": True},
            pass_fail=True,
        )
        self.assertEqual(hc.kind, "harness_case")
        self.assertEqual(hc.case_type, "loop_completeness")
        self.assertEqual(hc.pass_fail, True)
        self.assertEqual(hc.status, "draft")  # Default status
        self.assertEqual(hc.notes, None)
        self.assertEqual(hc.evidence_refs, [])

    def test_timestamps_timezone_aware(self):
        """HarnessCase timestamps are timezone-aware."""
        now = datetime.now(timezone.utc)
        hc = HarnessCase(
            id="ike:harness_case:12345678-1234-1234-1234-123456789012",
            kind="harness_case",
            created_at=now,
            updated_at=now,
            case_type="loop_completeness",
            subject_refs=["ike:research_task:" + str(uuid4())],
            expected_behavior={"test": True},
            actual_behavior={"test": True},
            pass_fail=True,
        )
        self.assertIsNotNone(hc.created_at.tzinfo)
        self.assertIsNotNone(hc.updated_at.tzinfo)

    def test_status_can_be_set(self):
        """Status can be explicitly set."""
        now = datetime.now(timezone.utc)
        
        # Completed status
        hc_completed = HarnessCase(
            id="ike:harness_case:12345678-1234-1234-1234-123456789012",
            kind="harness_case",
            created_at=now,
            updated_at=now,
            case_type="loop_completeness",
            subject_refs=[],
            expected_behavior={},
            actual_behavior={},
            pass_fail=True,
            status="completed",
        )
        self.assertEqual(hc_completed.status, "completed")
        
        # Open status
        hc_open = HarnessCase(
            id="ike:harness_case:12345678-1234-1234-1234-123456789013",
            kind="harness_case",
            created_at=now,
            updated_at=now,
            case_type="loop_completeness",
            subject_refs=[],
            expected_behavior={},
            actual_behavior={},
            pass_fail=False,
            status="open",
        )
        self.assertEqual(hc_open.status, "open")

    def test_notes_optional(self):
        """Notes field is optional."""
        now = datetime.now(timezone.utc)
        hc = HarnessCase(
            id="ike:harness_case:12345678-1234-1234-1234-123456789012",
            kind="harness_case",
            created_at=now,
            updated_at=now,
            case_type="loop_completeness",
            subject_refs=[],
            expected_behavior={},
            actual_behavior={},
            pass_fail=True,
            notes="Test notes",
        )
        self.assertEqual(hc.notes, "Test notes")

    def test_evidence_refs_default_empty(self):
        """Evidence refs default to empty list."""
        now = datetime.now(timezone.utc)
        hc = HarnessCase(
            id="ike:harness_case:12345678-1234-1234-1234-123456789012",
            kind="harness_case",
            created_at=now,
            updated_at=now,
            case_type="loop_completeness",
            subject_refs=[],
            expected_behavior={},
            actual_behavior={},
            pass_fail=True,
        )
        self.assertEqual(hc.evidence_refs, [])


class TestCreateLoopCompletenessHarnessCase(unittest.TestCase):
    """Tests for create_loop_completeness_harness_case helper."""

    def test_create_basic(self):
        """Create a basic loop_completeness harness case."""
        task_ref = "ike:research_task:" + str(uuid4())
        exp_ref = "ike:experiment:" + str(uuid4())
        dec_ref = "ike:decision:" + str(uuid4())
        subject_refs = [task_ref, exp_ref, dec_ref]
        
        expected = {"has_task": True, "has_experiment": True, "has_decision": True}
        actual = {"has_task": True, "has_experiment": True, "has_decision": True}

        hc = create_loop_completeness_harness_case(
            subject_refs=subject_refs,
            expected_behavior=expected,
            actual_behavior=actual,
            pass_fail=True,
        )

        self.assertEqual(hc.kind, "harness_case")
        self.assertEqual(hc.case_type, "loop_completeness")
        self.assertEqual(hc.subject_refs, subject_refs)
        self.assertEqual(hc.expected_behavior, expected)
        self.assertEqual(hc.actual_behavior, actual)
        self.assertEqual(hc.pass_fail, True)
        self.assertEqual(hc.status, "completed")
        self.assertEqual(hc.notes, None)
        self.assertIn("mapper", hc.provenance)

    def test_create_with_notes(self):
        """Create harness case with notes."""
        hc = create_loop_completeness_harness_case(
            subject_refs=[],
            expected_behavior={},
            actual_behavior={},
            pass_fail=True,
            notes="Loop completeness verified for sprint 1",
        )
        self.assertEqual(hc.notes, "Loop completeness verified for sprint 1")

    def test_create_with_evidence_refs(self):
        """Create harness case with evidence references."""
        evidence_refs = [
            "ike:observation:" + str(uuid4()),
            "ike:observation:" + str(uuid4()),
        ]
        
        hc = create_loop_completeness_harness_case(
            subject_refs=[],
            expected_behavior={},
            actual_behavior={},
            pass_fail=True,
            evidence_refs=evidence_refs,
        )
        self.assertEqual(hc.evidence_refs, evidence_refs)

    def test_create_fail_case(self):
        """Create a failing harness case."""
        expected = {"has_task": True, "has_experiment": True, "has_decision": True}
        actual = {"has_task": True, "has_experiment": False, "has_decision": False}

        hc = create_loop_completeness_harness_case(
            subject_refs=[],
            expected_behavior=expected,
            actual_behavior=actual,
            pass_fail=False,
        )

        self.assertEqual(hc.pass_fail, False)
        self.assertEqual(hc.status, "open")

    def test_generated_id_format(self):
        """HarnessCase generates properly formatted IKE ID."""
        hc = create_loop_completeness_harness_case(
            subject_refs=[],
            expected_behavior={},
            actual_behavior={},
            pass_fail=True,
        )

        self.assertTrue(hc.id.startswith("ike:harness_case:"))
        self.assertEqual(len(hc.id), len("ike:harness_case:") + 36)

    def test_references_includes_subject_refs(self):
        """References list includes all subject_refs."""
        task_ref = "ike:research_task:" + str(uuid4())
        exp_ref = "ike:experiment:" + str(uuid4())
        subject_refs = [task_ref, exp_ref]

        hc = create_loop_completeness_harness_case(
            subject_refs=subject_refs,
            expected_behavior={},
            actual_behavior={},
            pass_fail=True,
        )

        self.assertIn(task_ref, hc.references)
        self.assertIn(exp_ref, hc.references)
        self.assertEqual(len(hc.references), len(subject_refs))

    def test_provenance_includes_case_type(self):
        """Provenance includes case type metadata."""
        hc = create_loop_completeness_harness_case(
            subject_refs=[],
            expected_behavior={},
            actual_behavior={},
            pass_fail=True,
        )

        self.assertEqual(hc.provenance.get("case_type"), "loop_completeness")
        self.assertEqual(hc.provenance.get("subject_count"), 0)

    def test_provenance_includes_subject_count(self):
        """Provenance includes count of subject refs."""
        subject_refs = [
            "ike:research_task:" + str(uuid4()),
            "ike:experiment:" + str(uuid4()),
            "ike:decision:" + str(uuid4()),
        ]

        hc = create_loop_completeness_harness_case(
            subject_refs=subject_refs,
            expected_behavior={},
            actual_behavior={},
            pass_fail=True,
        )

        self.assertEqual(hc.provenance.get("subject_count"), 3)


if __name__ == "__main__":
    unittest.main()
