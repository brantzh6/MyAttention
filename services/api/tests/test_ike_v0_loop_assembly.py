"""
Tests for IKE v0.1 Full Loop Assembly.

Tests verify:
- Full loop can be assembled end-to-end from a single Observation
- All loop objects are present in the returned chain
- Chain is complete after assembly
- Harness validation passes for complete chain
- All traceability links are preserved
"""

import unittest
from datetime import datetime, timezone

from ike_v0.schemas.observation import Observation
from ike_v0.runtime.loop_assembly import assemble_full_loop


class TestFullLoopAssembly(unittest.TestCase):
    """Tests for assemble_full_loop helper."""

    def _make_test_observation(self):
        """Create a test Observation object."""
        now = datetime.now(timezone.utc)
        return Observation(
            id="ike:observation:" + str(now.timestamp()).replace(".", "-"),
            kind="observation",
            created_at=now,
            updated_at=now,
            source_ref="source:test",
            observed_at=now,
            captured_at=now,
            title="Test Observation for Full Loop",
            summary="This is a test observation that will be used to prove the full IKE v0.1 loop can be assembled end-to-end.",
        )

    def test_assemble_full_loop_basic(self):
        """Assemble full loop from observation."""
        obs = self._make_test_observation()

        chain, entity, claim = assemble_full_loop(obs)

        # Verify chain is returned
        self.assertIsNotNone(chain)
        self.assertIsNotNone(chain.chain_id)

        # Verify entity and claim are returned
        self.assertIsNotNone(entity)
        self.assertIsNotNone(claim)

    def test_assemble_full_loop_chain_complete(self):
        """Assembled chain is complete."""
        obs = self._make_test_observation()

        chain, entity, claim = assemble_full_loop(obs)

        self.assertTrue(chain.is_complete())

    def test_assemble_full_loop_all_objects_present(self):
        """All loop objects are present in assembled chain."""
        obs = self._make_test_observation()

        chain, entity, claim = assemble_full_loop(obs)

        # Verify all required objects
        self.assertIsNotNone(chain.observation)
        self.assertEqual(chain.observation.id, obs.id)

        self.assertIsNotNone(chain.entity)
        self.assertEqual(chain.entity.id, entity.id)

        self.assertIsNotNone(chain.claim)
        self.assertEqual(chain.claim.id, claim.id)

        self.assertIsNotNone(chain.research_task)

        self.assertIsNotNone(chain.experiment)

        self.assertIsNotNone(chain.decision)

        self.assertIsNotNone(chain.harness_case)

    def test_assemble_full_loop_harness_passes(self):
        """Harness validation passes for complete loop."""
        obs = self._make_test_observation()

        chain, entity, claim = assemble_full_loop(obs)

        self.assertTrue(chain.harness_case.pass_fail)
        self.assertEqual(chain.harness_case.case_type, "loop_completeness")

    def test_assemble_full_loop_traceability(self):
        """All traceability links are preserved."""
        obs = self._make_test_observation()

        chain, entity, claim = assemble_full_loop(obs)

        # Check observation references
        self.assertIn(obs.id, chain.get_all_refs())

        # Check entity references
        self.assertIn(entity.id, chain.get_all_refs())
        self.assertIn(obs.id, entity.references)

        # Check claim references
        self.assertIn(claim.id, chain.get_all_refs())
        self.assertIn(entity.id, claim.subject_refs)
        self.assertIn(obs.id, claim.source_observation_refs)

        # Check task references
        self.assertIn(chain.research_task.id, chain.get_all_refs())
        self.assertIn(obs.id, chain.research_task.input_refs)
        self.assertIn(entity.id, chain.research_task.input_refs)
        self.assertIn(claim.id, chain.research_task.input_refs)

        # Check experiment references
        self.assertIn(chain.experiment.id, chain.get_all_refs())
        self.assertEqual(chain.experiment.task_ref, chain.research_task.id)
        self.assertIn(claim.id, chain.experiment.input_refs)

        # Check decision references
        self.assertIn(chain.decision.id, chain.get_all_refs())
        self.assertEqual(chain.decision.task_ref, chain.research_task.id)
        self.assertIn(chain.experiment.id, chain.decision.experiment_refs)

    def test_assemble_full_loop_custom_entity_type(self):
        """Full loop with custom entity type."""
        obs = self._make_test_observation()

        chain, entity, claim = assemble_full_loop(
            obs,
            entity_type="technology",
        )

        self.assertEqual(entity.entity_type, "technology")

    def test_assemble_full_loop_custom_claim_type(self):
        """Full loop with custom claim type."""
        obs = self._make_test_observation()

        chain, entity, claim = assemble_full_loop(
            obs,
            claim_type="relationship",
        )

        self.assertEqual(claim.claim_type, "relationship")

    def test_assemble_full_loop_custom_task_type(self):
        """Full loop with custom task type."""
        obs = self._make_test_observation()

        chain, entity, claim = assemble_full_loop(
            obs,
            task_type="validation",
        )

        self.assertEqual(chain.research_task.task_type, "validation")

    def test_assemble_full_loop_custom_decision_outcome(self):
        """Full loop with custom decision outcome."""
        obs = self._make_test_observation()

        chain, entity, claim = assemble_full_loop(
            obs,
            decision_outcome="reject",
        )

        self.assertEqual(chain.decision.decision_outcome, "reject")

    def test_assemble_full_loop_provisional_status(self):
        """All loop objects have provisional status."""
        obs = self._make_test_observation()

        chain, entity, claim = assemble_full_loop(obs)

        # All objects should be in draft status (provisional)
        self.assertEqual(chain.research_task.status, "draft")
        self.assertEqual(chain.experiment.status, "draft")
        self.assertEqual(chain.decision.status, "draft")
        # Harness case status depends on pass/fail
        self.assertEqual(chain.harness_case.status, "completed")  # Pass -> completed

    def test_assemble_full_loop_chain_serializable(self):
        """Assembled chain can be serialized to dict."""
        obs = self._make_test_observation()

        chain, entity, claim = assemble_full_loop(obs)

        # Should not raise
        payload = chain.to_dict()

        # Verify key fields
        self.assertEqual(payload["chain_id"], chain.chain_id)
        self.assertTrue(payload["is_complete"])
        self.assertIsNotNone(payload["observation"])
        self.assertIsNotNone(payload["entity"])
        self.assertIsNotNone(payload["claim"])
        self.assertIsNotNone(payload["research_task"])
        self.assertIsNotNone(payload["experiment"])
        self.assertIsNotNone(payload["decision"])
        self.assertIsNotNone(payload["harness_case"])

    def test_assemble_full_loop_derivation_path(self):
        """Loop objects have correct derivation path in provenance."""
        obs = self._make_test_observation()

        chain, entity, claim = assemble_full_loop(obs)

        # Check entity provenance
        self.assertEqual(entity.provenance.get("mapper"), "extract_entity_and_claim_from_observation")
        self.assertEqual(entity.provenance.get("source_observation_id"), obs.id)

        # Check claim provenance
        self.assertEqual(claim.provenance.get("mapper"), "extract_entity_and_claim_from_observation")
        self.assertEqual(claim.provenance.get("source_observation_id"), obs.id)
        self.assertEqual(claim.provenance.get("derived_from_entity_id"), entity.id)

        # Check task provenance
        self.assertEqual(chain.research_task.provenance.get("mapper"), "derive_research_task_from_entity_claim")
        self.assertEqual(chain.research_task.provenance.get("derivation_path"), "observation -> entity/claim -> research_task")

        # Check experiment provenance
        self.assertEqual(chain.experiment.provenance.get("mapper"), "create_claim_validation_experiment")
        self.assertEqual(chain.experiment.provenance.get("experiment_type"), "claim_validation")

        # Check decision provenance
        self.assertEqual(chain.decision.provenance.get("mapper"), "derive_decision_from_experiment")
        self.assertEqual(chain.decision.provenance.get("derivation_path"), "research_task -> experiment -> decision")

        # Check harness provenance
        self.assertEqual(chain.harness_case.provenance.get("mapper"), "validate_chain_loop_completeness")


if __name__ == "__main__":
    unittest.main()
