"""
Minimal tests for IKE v0 Entity and Claim schemas and extraction helper.

Tests verify:
- Entity schema can be imported and instantiated
- Claim schema can be imported and instantiated
- Extraction helper creates valid Entity and Claim from Observation
- Required fields are validated
- Generated ID formats are valid
- Timestamps are timezone-aware
- Traceability is preserved through references and provenance
"""

import unittest
from datetime import datetime, timezone
from uuid import uuid4

from ike_v0.schemas.entity import Entity
from ike_v0.schemas.claim import Claim
from ike_v0.schemas.observation import Observation
from ike_v0.mappers.extraction import extract_entity_and_claim_from_observation
from ike_v0.types.ids import IKEKind


class TestEntitySchema(unittest.TestCase):
    """Tests for Entity schema."""

    def test_import(self):
        """Entity can be imported."""
        self.assertIsNotNone(Entity)

    def test_instantiation_required_fields(self):
        """Entity can be instantiated with required fields."""
        now = datetime.now(timezone.utc)
        entity = Entity(
            id="ike:entity:12345678-1234-1234-1234-123456789012",
            kind="entity",
            created_at=now,
            updated_at=now,
            entity_type="organization",
            canonical_key="org:example-corp",
            display_name="Example Corp",
        )
        self.assertEqual(entity.kind, "entity")
        self.assertEqual(entity.entity_type, "organization")
        self.assertEqual(entity.canonical_key, "org:example-corp")
        self.assertEqual(entity.display_name, "Example Corp")
        self.assertEqual(entity.status, "draft")
        self.assertEqual(entity.aliases, [])

    def test_timestamps_timezone_aware(self):
        """Entity timestamps are timezone-aware."""
        now = datetime.now(timezone.utc)
        entity = Entity(
            id="ike:entity:12345678-1234-1234-1234-123456789012",
            kind="entity",
            created_at=now,
            updated_at=now,
            entity_type="organization",
            canonical_key="org:example",
            display_name="Example",
        )
        self.assertIsNotNone(entity.created_at.tzinfo)
        self.assertIsNotNone(entity.updated_at.tzinfo)

    def test_aliases_default_empty(self):
        """Aliases default to empty list."""
        now = datetime.now(timezone.utc)
        entity = Entity(
            id="ike:entity:12345678-1234-1234-1234-123456789012",
            kind="entity",
            created_at=now,
            updated_at=now,
            entity_type="organization",
            canonical_key="org:example",
            display_name="Example",
        )
        self.assertEqual(entity.aliases, [])

    def test_aliases_can_be_set(self):
        """Aliases can be explicitly set."""
        now = datetime.now(timezone.utc)
        entity = Entity(
            id="ike:entity:12345678-1234-1234-1234-123456789012",
            kind="entity",
            created_at=now,
            updated_at=now,
            entity_type="organization",
            canonical_key="org:example",
            display_name="Example Corp",
            aliases=["Example Corporation", "Example Inc"],
        )
        self.assertEqual(entity.aliases, ["Example Corporation", "Example Inc"])


class TestClaimSchema(unittest.TestCase):
    """Tests for Claim schema."""

    def test_import(self):
        """Claim can be imported."""
        self.assertIsNotNone(Claim)

    def test_instantiation_required_fields(self):
        """Claim can be instantiated with required fields."""
        now = datetime.now(timezone.utc)
        claim = Claim(
            id="ike:claim:12345678-1234-1234-1234-123456789012",
            kind="claim",
            created_at=now,
            updated_at=now,
            claim_type="capability",
            statement="Example Corp has AI capabilities",
            subject_refs=["ike:entity:12345678-1234-1234-1234-123456789012"],
            source_observation_refs=["ike:observation:12345678-1234-1234-1234-123456789012"],
        )
        self.assertEqual(claim.kind, "claim")
        self.assertEqual(claim.claim_type, "capability")
        self.assertEqual(claim.statement, "Example Corp has AI capabilities")
        self.assertEqual(claim.status, "draft")
        self.assertEqual(claim.evidence_refs, [])

    def test_timestamps_timezone_aware(self):
        """Claim timestamps are timezone-aware."""
        now = datetime.now(timezone.utc)
        claim = Claim(
            id="ike:claim:12345678-1234-1234-1234-123456789012",
            kind="claim",
            created_at=now,
            updated_at=now,
            claim_type="capability",
            statement="Test claim",
            subject_refs=[],
            source_observation_refs=[],
        )
        self.assertIsNotNone(claim.created_at.tzinfo)
        self.assertIsNotNone(claim.updated_at.tzinfo)

    def test_evidence_refs_default_empty(self):
        """Evidence refs default to empty list."""
        now = datetime.now(timezone.utc)
        claim = Claim(
            id="ike:claim:12345678-1234-1234-1234-123456789012",
            kind="claim",
            created_at=now,
            updated_at=now,
            claim_type="capability",
            statement="Test",
            subject_refs=[],
            source_observation_refs=[],
        )
        self.assertEqual(claim.evidence_refs, [])


class TestExtractEntityAndClaimFromObservation(unittest.TestCase):
    """Tests for extract_entity_and_claim_from_observation helper."""

    def _create_mock_observation(self):
        """Create a mock Observation for testing."""
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

    def test_extract_basic(self):
        """Extract Entity and Claim from Observation."""
        obs = self._create_mock_observation()

        entity, claim = extract_entity_and_claim_from_observation(
            observation=obs,
            entity_type="organization",
            canonical_key="org:example",
            display_name="Example Corp",
            claim_type="capability",
            statement="Example Corp has AI capabilities",
        )

        # Verify Entity
        self.assertEqual(entity.kind, "entity")
        self.assertEqual(entity.entity_type, "organization")
        self.assertEqual(entity.canonical_key, "org:example")
        self.assertEqual(entity.display_name, "Example Corp")
        self.assertIn(obs.id, entity.references)
        self.assertEqual(entity.provenance["source_observation_id"], obs.id)

        # Verify Claim
        self.assertEqual(claim.kind, "claim")
        self.assertEqual(claim.claim_type, "capability")
        self.assertEqual(claim.statement, "Example Corp has AI capabilities")
        self.assertEqual(claim.subject_refs, [entity.id])
        self.assertEqual(claim.source_observation_refs, [obs.id])
        self.assertEqual(claim.evidence_refs, [obs.id])
        self.assertIn(entity.id, claim.references)
        self.assertIn(obs.id, claim.references)
        self.assertEqual(claim.provenance["source_observation_id"], obs.id)
        self.assertEqual(claim.provenance["derived_from_entity_id"], entity.id)

    def test_extract_with_aliases(self):
        """Extract Entity with aliases."""
        obs = self._create_mock_observation()

        entity, claim = extract_entity_and_claim_from_observation(
            observation=obs,
            entity_type="organization",
            canonical_key="org:example",
            display_name="Example Corp",
            claim_type="capability",
            statement="Test",
            aliases=["Example Corporation", "Example Inc"],
        )

        self.assertEqual(entity.aliases, ["Example Corporation", "Example Inc"])

    def test_generated_entity_id_format(self):
        """Entity generates properly formatted IKE ID."""
        obs = self._create_mock_observation()

        entity, claim = extract_entity_and_claim_from_observation(
            observation=obs,
            entity_type="organization",
            canonical_key="org:example",
            display_name="Example",
            claim_type="capability",
            statement="Test",
        )

        self.assertTrue(entity.id.startswith("ike:entity:"))
        self.assertEqual(len(entity.id), len("ike:entity:") + 36)

    def test_generated_claim_id_format(self):
        """Claim generates properly formatted IKE ID."""
        obs = self._create_mock_observation()

        entity, claim = extract_entity_and_claim_from_observation(
            observation=obs,
            entity_type="organization",
            canonical_key="org:example",
            display_name="Example",
            claim_type="capability",
            statement="Test",
        )

        self.assertTrue(claim.id.startswith("ike:claim:"))
        self.assertEqual(len(claim.id), len("ike:claim:") + 36)

    def test_traceability_entity_to_observation(self):
        """Entity preserves traceability to source observation."""
        obs = self._create_mock_observation()

        entity, claim = extract_entity_and_claim_from_observation(
            observation=obs,
            entity_type="organization",
            canonical_key="org:example",
            display_name="Example",
            claim_type="capability",
            statement="Test",
        )

        self.assertIn(obs.id, entity.references)
        self.assertEqual(entity.provenance["source_observation_id"], obs.id)
        self.assertEqual(entity.provenance["source_signal_type"], obs.signal_type)

    def test_traceability_claim_to_entity(self):
        """Claim preserves traceability to derived entity."""
        obs = self._create_mock_observation()

        entity, claim = extract_entity_and_claim_from_observation(
            observation=obs,
            entity_type="organization",
            canonical_key="org:example",
            display_name="Example",
            claim_type="capability",
            statement="Test",
        )

        self.assertEqual(claim.subject_refs, [entity.id])
        self.assertEqual(claim.provenance["derived_from_entity_id"], entity.id)

    def test_traceability_claim_to_observation(self):
        """Claim preserves traceability to source observation."""
        obs = self._create_mock_observation()

        entity, claim = extract_entity_and_claim_from_observation(
            observation=obs,
            entity_type="organization",
            canonical_key="org:example",
            display_name="Example",
            claim_type="capability",
            statement="Test",
        )

        self.assertIn(obs.id, claim.source_observation_refs)
        self.assertIn(obs.id, claim.evidence_refs)
        self.assertIn(obs.id, claim.references)

    def test_confidence_defaults(self):
        """Entity and Claim use conservative confidence defaults."""
        obs = self._create_mock_observation()

        entity, claim = extract_entity_and_claim_from_observation(
            observation=obs,
            entity_type="organization",
            canonical_key="org:example",
            display_name="Example",
            claim_type="capability",
            statement="Test",
        )

        self.assertEqual(entity.confidence, 0.5)
        self.assertEqual(claim.confidence, 0.5)


if __name__ == "__main__":
    unittest.main()
