"""
Tests for IKE v0.1 Chain Artifact helper.

Tests verify:
- ChainArtifact can be created and inspected
- Completeness checking works correctly
- Serialization to dict works
- Reference collection works
"""

import unittest
from datetime import datetime, timezone
from uuid import uuid4

from ike_v0.runtime.chain_artifact import (
    ChainArtifact,
    ARTIFACT_TYPE_IKE_CHAIN,
    assemble_chain_artifact,
    build_chain_artifact_payload,
    reconstruct_chain_from_payload,
    bootstrap_chain_from_observation,
    attach_harness_validation,
)
from ike_v0.schemas.observation import Observation
from ike_v0.schemas.research_task import ResearchTask
from ike_v0.schemas.experiment import Experiment
from ike_v0.schemas.decision import Decision
from ike_v0.schemas.harness_case import HarnessCase


def _make_test_observation():
    """Create a test Observation object."""
    now = datetime.now(timezone.utc)
    return Observation(
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


def _make_test_research_task():
    """Create a test ResearchTask object."""
    now = datetime.now(timezone.utc)
    return ResearchTask(
        id="ike:research_task:" + str(uuid4()),
        kind="research_task",
        created_at=now,
        updated_at=now,
        task_type="discovery",
        title="Test Research Task",
        goal="Test goal",
    )


def _make_test_experiment(task_ref: str):
    """Create a test Experiment object."""
    now = datetime.now(timezone.utc)
    return Experiment(
        id="ike:experiment:" + str(uuid4()),
        kind="experiment",
        created_at=now,
        updated_at=now,
        task_ref=task_ref,
        experiment_type="source_plan_comparison",
        title="Test Experiment",
        hypothesis="Test hypothesis",
        method_ref="test_method:v0.1",
    )


def _make_test_decision(task_ref: str, experiment_ref: str):
    """Create a test Decision object."""
    now = datetime.now(timezone.utc)
    return Decision(
        id="ike:decision:" + str(uuid4()),
        kind="decision",
        created_at=now,
        updated_at=now,
        task_ref=task_ref,
        experiment_refs=[experiment_ref],
        decision_type="experiment_evaluation",
        decision_outcome="adopt",
        rationale="Test rationale",
    )


def _make_test_harness_case(subject_refs: list):
    """Create a test HarnessCase object."""
    now = datetime.now(timezone.utc)
    return HarnessCase(
        id="ike:harness_case:" + str(uuid4()),
        kind="harness_case",
        created_at=now,
        updated_at=now,
        case_type="loop_completeness",
        subject_refs=subject_refs,
        expected_behavior={"complete": True},
        actual_behavior={"complete": True},
        pass_fail=True,
    )


class TestChainArtifact(unittest.TestCase):
    """Tests for ChainArtifact class."""

    def test_create_minimal_chain(self):
        """Create a chain with only required observation."""
        obs = _make_test_observation()
        chain = ChainArtifact(
            chain_id="chain-001",
            observation=obs,
        )

        self.assertEqual(chain.chain_id, "chain-001")
        self.assertFalse(chain.is_complete())
        self.assertEqual(chain.get_all_refs(), [obs.id])

    def test_create_complete_chain(self):
        """Create a complete chain with all objects."""
        obs = _make_test_observation()
        task = _make_test_research_task()
        exp = _make_test_experiment(task.id)
        dec = _make_test_decision(task.id, exp.id)
        harness = _make_test_harness_case([task.id, exp.id, dec.id])

        chain = ChainArtifact(
            chain_id="chain-002",
            observation=obs,
            research_task=task,
            experiment=exp,
            decision=dec,
            harness_case=harness,
        )

        self.assertTrue(chain.is_complete())
        self.assertEqual(len(chain.get_all_refs()), 5)

    def test_chain_with_optional_entity_claim(self):
        """Create a chain with optional Entity and Claim."""
        from ike_v0.schemas.entity import Entity
        from ike_v0.schemas.claim import Claim

        now = datetime.now(timezone.utc)
        obs = _make_test_observation()
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
            statement="Test claim",
            subject_refs=[entity.id],
            source_observation_refs=[obs.id],
        )

        chain = ChainArtifact(
            chain_id="chain-003",
            observation=obs,
            entity=entity,
            claim=claim,
        )

        self.assertFalse(chain.is_complete())  # Missing task, exp, dec, harness
        refs = chain.get_all_refs()
        self.assertIn(obs.id, refs)
        self.assertIn(entity.id, refs)
        self.assertIn(claim.id, refs)

    def test_to_dict_serialization(self):
        """Chain serializes to dict correctly."""
        obs = _make_test_observation()
        task = _make_test_research_task()

        chain = ChainArtifact(
            chain_id="chain-004",
            observation=obs,
            research_task=task,
        )

        data = chain.to_dict()

        self.assertEqual(data["chain_id"], "chain-004")
        self.assertIn("created_at", data)
        self.assertFalse(data["is_complete"])
        self.assertIsNotNone(data["observation"])
        self.assertIsNotNone(data["research_task"])
        self.assertIsNone(data["experiment"])
        self.assertIn("all_refs", data)

    def test_get_completeness_summary(self):
        """Completeness summary shows object presence."""
        obs = _make_test_observation()
        task = _make_test_research_task()

        chain = ChainArtifact(
            chain_id="chain-005",
            observation=obs,
            research_task=task,
        )

        summary = chain.get_completeness_summary()

        self.assertEqual(summary["chain_id"], "chain-005")
        self.assertFalse(summary["is_complete"])
        self.assertEqual(summary["object_count"], 2)
        self.assertIsNotNone(summary["objects"]["observation"])
        self.assertIsNotNone(summary["objects"]["research_task"])
        self.assertIsNone(summary["objects"]["experiment"])


class TestAssembleChainArtifact(unittest.TestCase):
    """Tests for assemble_chain_artifact helper."""

    def test_assemble_complete_chain(self):
        """Assemble a complete chain using the helper."""
        obs = _make_test_observation()
        task = _make_test_research_task()
        exp = _make_test_experiment(task.id)
        dec = _make_test_decision(task.id, exp.id)
        harness = _make_test_harness_case([task.id, exp.id, dec.id])

        chain = assemble_chain_artifact(
            chain_id="chain-006",
            observation=obs,
            research_task=task,
            experiment=exp,
            decision=dec,
            harness_case=harness,
        )

        self.assertTrue(chain.is_complete())
        self.assertEqual(chain.chain_id, "chain-006")


class TestBuildChainArtifactPayload(unittest.TestCase):
    """Tests for build_chain_artifact_payload helper."""

    def test_build_payload_with_linkage(self):
        """Build payload with context and task linkage."""
        obs = _make_test_observation()
        task = _make_test_research_task()

        chain = ChainArtifact(
            chain_id="chain-007",
            observation=obs,
            research_task=task,
        )

        payload = build_chain_artifact_payload(
            chain=chain,
            context_id="context-123",
            task_id="task-456",
        )

        self.assertEqual(payload["chain_id"], "chain-007")
        self.assertEqual(payload["context_id"], "context-123")
        self.assertEqual(payload["task_id"], "task-456")
        self.assertEqual(payload["artifact_type_marker"], ARTIFACT_TYPE_IKE_CHAIN)

    def test_build_payload_without_linkage(self):
        """Build payload without optional linkage."""
        obs = _make_test_observation()

        chain = ChainArtifact(
            chain_id="chain-008",
            observation=obs,
        )

        payload = build_chain_artifact_payload(chain=chain)

        self.assertEqual(payload["chain_id"], "chain-008")
        self.assertNotIn("context_id", payload)
        self.assertNotIn("task_id", payload)
        self.assertEqual(payload["artifact_type_marker"], ARTIFACT_TYPE_IKE_CHAIN)


class TestArtifactTypeMarker(unittest.TestCase):
    """Tests for artifact type marker constant."""

    def test_artifact_type_constant(self):
        """Artifact type marker is defined correctly."""
        self.assertEqual(ARTIFACT_TYPE_IKE_CHAIN, "ike_v0_chain")


class TestReconstructChainFromPayload(unittest.TestCase):
    """Tests for reconstruct_chain_from_payload helper."""

    def test_reconstruct_minimal_chain(self):
        """Reconstruct minimal chain from payload."""
        obs = _make_test_observation()
        chain = ChainArtifact(chain_id="chain-recon-001", observation=obs)
        payload = chain.to_dict()

        reconstructed = reconstruct_chain_from_payload(payload)

        self.assertEqual(reconstructed.chain_id, "chain-recon-001")
        self.assertIsNotNone(reconstructed.observation)
        self.assertEqual(reconstructed.observation.id, obs.id)

    def test_reconstruct_complete_chain(self):
        """Reconstruct complete chain from payload."""
        obs = _make_test_observation()
        task = _make_test_research_task()
        exp = _make_test_experiment(task.id)
        dec = _make_test_decision(task.id, exp.id)
        harness = _make_test_harness_case([task.id, exp.id, dec.id])

        chain = ChainArtifact(
            chain_id="chain-recon-002",
            observation=obs,
            research_task=task,
            experiment=exp,
            decision=dec,
            harness_case=harness,
        )
        payload = chain.to_dict()

        reconstructed = reconstruct_chain_from_payload(payload)

        self.assertTrue(reconstructed.is_complete())
        self.assertEqual(reconstructed.observation.id, obs.id)
        self.assertEqual(reconstructed.research_task.id, task.id)

    def test_reconstruct_preserves_completeness(self):
        """Reconstructed chain preserves completeness status."""
        obs = _make_test_observation()
        task = _make_test_research_task()

        chain = ChainArtifact(
            chain_id="chain-recon-003",
            observation=obs,
            research_task=task,
        )
        payload = chain.to_dict()

        reconstructed = reconstruct_chain_from_payload(payload)

        self.assertFalse(reconstructed.is_complete())
        self.assertEqual(reconstructed.get_completeness_summary()["object_count"], 2)


class TestBootstrapChainFromObservation(unittest.TestCase):
    """Tests for bootstrap_chain_from_observation helper."""

    def test_bootstrap_generates_chain_id(self):
        """Bootstrap generates a chain_id when not provided."""
        obs = _make_test_observation()
        chain = bootstrap_chain_from_observation(obs)

        self.assertIsNotNone(chain.chain_id)
        self.assertTrue(chain.chain_id.startswith("ike_chain:"))

    def test_bootstrap_uses_provided_chain_id(self):
        """Bootstrap uses provided chain_id."""
        obs = _make_test_observation()
        chain = bootstrap_chain_from_observation(obs, chain_id="custom-chain-123")

        self.assertEqual(chain.chain_id, "custom-chain-123")

    def test_bootstrap_sets_observation(self):
        """Bootstrap sets the observation correctly."""
        obs = _make_test_observation()
        chain = bootstrap_chain_from_observation(obs)

        self.assertEqual(chain.observation.id, obs.id)
        self.assertEqual(chain.observation.title, obs.title)

    def test_bootstrap_other_objects_none(self):
        """Bootstrap leaves other objects as None."""
        obs = _make_test_observation()
        chain = bootstrap_chain_from_observation(obs)

        self.assertIsNone(chain.entity)
        self.assertIsNone(chain.claim)
        self.assertIsNone(chain.research_task)
        self.assertIsNone(chain.experiment)
        self.assertIsNone(chain.decision)
        self.assertIsNone(chain.harness_case)

    def test_bootstrap_chain_not_complete(self):
        """Bootstrapped chain is not complete (only has observation)."""
        obs = _make_test_observation()
        chain = bootstrap_chain_from_observation(obs)

        self.assertFalse(chain.is_complete())

    def test_bootstrap_payload_compatible(self):
        """Bootstrapped chain produces TaskArtifact-compatible payload."""
        obs = _make_test_observation()
        chain = bootstrap_chain_from_observation(obs)

        payload = build_chain_artifact_payload(chain)

        self.assertEqual(payload["chain_id"], chain.chain_id)
        self.assertEqual(payload["artifact_type_marker"], ARTIFACT_TYPE_IKE_CHAIN)
        self.assertIsNotNone(payload["observation"])
        self.assertFalse(payload["is_complete"])

    def test_bootstrap_reflects_observation_in_refs(self):
        """Bootstrapped chain includes observation in refs."""
        obs = _make_test_observation()
        chain = bootstrap_chain_from_observation(obs)

        refs = chain.get_all_refs()
        self.assertEqual(refs, [obs.id])


class TestAttachHarnessValidation(unittest.TestCase):
    """Tests for attach_harness_validation helper."""

    def _make_populated_chain(self):
        """Create a chain with all objects except harness_case."""
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

        task = ResearchTask(
            id="ike:research_task:" + str(uuid4()),
            kind="research_task",
            created_at=now,
            updated_at=now,
            task_type="discovery",
            title="Test Task",
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

        dec = Decision(
            id="ike:decision:" + str(uuid4()),
            kind="decision",
            created_at=now,
            updated_at=now,
            task_ref=task.id,
            experiment_refs=[exp.id],
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

    def test_attach_adds_harness_case(self):
        """attach_harness_validation adds harness_case to chain."""
        chain = self._make_populated_chain()

        result = attach_harness_validation(chain)

        self.assertIsNotNone(result.harness_case)
        self.assertEqual(result.harness_case.case_type, "loop_completeness")

    def test_attach_preserves_chain_id(self):
        """attach_harness_validation preserves original chain_id."""
        chain = self._make_populated_chain()

        result = attach_harness_validation(chain)

        self.assertEqual(result.chain_id, chain.chain_id)

    def test_attach_preserves_all_objects(self):
        """attach_harness_validation preserves all original objects."""
        chain = self._make_populated_chain()

        result = attach_harness_validation(chain)

        self.assertEqual(result.observation.id, chain.observation.id)
        self.assertEqual(result.research_task.id, chain.research_task.id)
        self.assertEqual(result.experiment.id, chain.experiment.id)
        self.assertEqual(result.decision.id, chain.decision.id)

    def test_attach_makes_chain_complete(self):
        """attach_harness_validation makes chain complete (if required objects present)."""
        chain = self._make_populated_chain()

        result = attach_harness_validation(chain)

        self.assertTrue(result.is_complete())

    def test_attach_harness_pass_fail_reflects_chain(self):
        """HarnessCase pass_fail reflects chain completeness."""
        chain = self._make_populated_chain()

        result = attach_harness_validation(chain)

        # Complete chain should pass validation
        self.assertTrue(result.harness_case.pass_fail)

    def test_attach_harness_provenance(self):
        """HarnessCase has explicit provenance from validation."""
        chain = self._make_populated_chain()

        result = attach_harness_validation(chain)

        self.assertEqual(result.harness_case.provenance.get("mapper"), "validate_chain_loop_completeness")
        self.assertEqual(result.harness_case.provenance.get("chain_id"), chain.chain_id)

    def test_attach_harness_references(self):
        """HarnessCase references include all chain object IDs."""
        chain = self._make_populated_chain()

        result = attach_harness_validation(chain)

        all_chain_refs = chain.get_all_refs()
        for ref in all_chain_refs:
            self.assertIn(ref, result.harness_case.references)

    def test_attach_incomplete_chain_fails(self):
        """attach_harness_validation on incomplete chain produces failing harness."""
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

        # Chain missing research_task, experiment, decision
        chain = ChainArtifact(
            chain_id="chain-incomplete",
            observation=obs,
        )

        result = attach_harness_validation(chain)

        self.assertIsNotNone(result.harness_case)
        self.assertFalse(result.harness_case.pass_fail)
        self.assertFalse(result.is_complete())

    def test_attach_returns_new_chain(self):
        """attach_harness_validation returns new ChainArtifact, not modified input."""
        chain = self._make_populated_chain()

        result = attach_harness_validation(chain)

        self.assertIsNot(result, chain)  # Different object
        self.assertIsNone(chain.harness_case)  # Original unchanged
        self.assertIsNotNone(result.harness_case)


if __name__ == "__main__":
    unittest.main()
