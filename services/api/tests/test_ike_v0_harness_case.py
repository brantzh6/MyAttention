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
from ike_v0.schemas.observation import Observation
from ike_v0.schemas.research_task import ResearchTask
from ike_v0.schemas.experiment import Experiment
from ike_v0.schemas.decision import Decision
from ike_v0.mappers.harness_case import (
    create_loop_completeness_harness_case,
    validate_chain_loop_completeness,
)
from ike_v0.runtime.chain_artifact import ChainArtifact
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


class TestValidateChainLoopCompleteness(unittest.TestCase):
    """Tests for validate_chain_loop_completeness helper."""

    def _make_complete_chain(self):
        """Create a complete chain for testing."""
        now = datetime.now(timezone.utc)
        task_id = "ike:research_task:" + str(uuid4())
        exp_id = "ike:experiment:" + str(uuid4())
        
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
        
        task = ResearchTask(
            id=task_id,
            kind="research_task",
            created_at=now,
            updated_at=now,
            task_type="discovery",
            title="Test Task",
            goal="Test goal",
        )
        
        exp = Experiment(
            id=exp_id,
            kind="experiment",
            created_at=now,
            updated_at=now,
            task_ref=task_id,
            experiment_type="source_plan_comparison",
            title="Test Experiment",
            hypothesis="Test hypothesis",
            method_ref="test_method:v0.1",
        )
        
        dec = Decision(
            id="ike:decision:" + str(uuid4()),
            kind="decision",
            created_at=now,
            updated_at=now,
            task_ref=task_id,
            experiment_refs=[exp_id],
            decision_type="experiment_evaluation",
            decision_outcome="adopt",
            rationale="Test rationale",
        )
        
        return ChainArtifact(
            chain_id="chain-test-001",
            observation=obs,
            research_task=task,
            experiment=exp,
            decision=dec,
        )

    def test_validate_complete_chain_passes(self):
        """Complete chain with valid references passes validation."""
        chain = self._make_complete_chain()
        
        hc = validate_chain_loop_completeness(chain)
        
        self.assertTrue(hc.pass_fail)
        self.assertEqual(hc.case_type, "loop_completeness")
        self.assertEqual(hc.status, "completed")
        self.assertIn(chain.research_task.id, hc.subject_refs)
        self.assertIn(chain.experiment.id, hc.subject_refs)
        self.assertIn(chain.decision.id, hc.subject_refs)
        self.assertIn(chain.observation.id, hc.evidence_refs)

    def test_validate_incomplete_chain_fails(self):
        """Incomplete chain fails validation."""
        now = datetime.now(timezone.utc)
        
        obs = Observation(
            id="ike:observation:" + str(uuid4()),
            kind="observation",
            created_at=now,
            updated_at=now,
            source_ref="source:test",
            observed_at=now,
            captured_at=now,
            title="Test",
            summary="Test",
        )
        
        # Missing research_task, experiment, decision
        chain = ChainArtifact(
            chain_id="chain-incomplete",
            observation=obs,
        )
        
        hc = validate_chain_loop_completeness(chain)
        
        self.assertFalse(hc.pass_fail)
        self.assertEqual(hc.status, "open")
        self.assertIn("Missing required objects", hc.notes)
        self.assertFalse(hc.provenance.get("required_present", True))

    def test_validate_traceability_issue_fails(self):
        """Chain with traceability issues fails validation."""
        now = datetime.now(timezone.utc)
        
        obs = Observation(
            id="ike:observation:" + str(uuid4()),
            kind="observation",
            created_at=now,
            updated_at=now,
            source_ref="source:test",
            observed_at=now,
            captured_at=now,
            title="Test",
            summary="Test",
        )
        
        task = ResearchTask(
            id="ike:research_task:" + str(uuid4()),
            kind="research_task",
            created_at=now,
            updated_at=now,
            task_type="discovery",
            title="Test",
            goal="Test",
        )
        
        # experiment.task_ref does NOT match task.id
        exp = Experiment(
            id="ike:experiment:" + str(uuid4()),
            kind="experiment",
            created_at=now,
            updated_at=now,
            task_ref="ike:research_task:wrong-id",
            experiment_type="source_plan_comparison",
            title="Test",
            hypothesis="Test",
            method_ref="test:v0.1",
        )
        
        dec = Decision(
            id="ike:decision:" + str(uuid4()),
            kind="decision",
            created_at=now,
            updated_at=now,
            task_ref=task.id,
            experiment_refs=[exp.id],
            decision_type="experiment_evaluation",
            decision_outcome="adopt",
            rationale="Test",
        )
        
        chain = ChainArtifact(
            chain_id="chain-trace-issue",
            observation=obs,
            research_task=task,
            experiment=exp,
            decision=dec,
        )
        
        hc = validate_chain_loop_completeness(chain)
        
        self.assertFalse(hc.pass_fail)
        self.assertGreater(hc.provenance.get("traceability_issues_count", 0), 0)
        self.assertIn("traceability", hc.notes.lower())

    def test_validate_derives_expected_behavior(self):
        """Validation derives explicit expected_behavior."""
        chain = self._make_complete_chain()
        
        hc = validate_chain_loop_completeness(chain)
        
        self.assertIn("required_objects", hc.expected_behavior)
        self.assertIn("observation", hc.expected_behavior["required_objects"])
        self.assertIn("research_task", hc.expected_behavior["required_objects"])
        self.assertIn("experiment", hc.expected_behavior["required_objects"])
        self.assertIn("decision", hc.expected_behavior["required_objects"])
        self.assertIn("traceability_checks", hc.expected_behavior)

    def test_validate_derives_actual_behavior(self):
        """Validation derives actual_behavior from chain."""
        chain = self._make_complete_chain()
        
        hc = validate_chain_loop_completeness(chain)
        
        self.assertIn("present_objects", hc.actual_behavior)
        self.assertIn("object_count", hc.actual_behavior)
        self.assertEqual(hc.actual_behavior["object_count"], 4)  # obs, task, exp, dec

    def test_validate_provenance_includes_chain_id(self):
        """Provenance includes source chain_id."""
        chain = self._make_complete_chain()
        
        hc = validate_chain_loop_completeness(chain)
        
        self.assertEqual(hc.provenance.get("chain_id"), "chain-test-001")
        self.assertEqual(hc.provenance.get("mapper"), "validate_chain_loop_completeness")

    def test_validate_references_includes_all_refs(self):
        """References includes all object IDs from chain."""
        chain = self._make_complete_chain()
        
        hc = validate_chain_loop_completeness(chain)
        
        all_chain_refs = chain.get_all_refs()
        for ref in all_chain_refs:
            self.assertIn(ref, hc.references)

    def test_validate_evidence_refs_includes_observation(self):
        """Evidence refs includes observation ID."""
        chain = self._make_complete_chain()
        
        hc = validate_chain_loop_completeness(chain)
        
        self.assertIn(chain.observation.id, hc.evidence_refs)


if __name__ == "__main__":
    unittest.main()
