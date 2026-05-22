"""
Tests for IKE B4 Evidence Layer Tagger.

Tests verify:
- EvidenceLayerTag can be created and serialized
- B4EvidenceLayers output shape is correct
- Layer assignment heuristics work correctly
- Entity type defaults are appropriate
- Media/context is lowest priority
"""

import unittest

from ike_v0.benchmarks.b4_evidence_layers import (
    EvidenceLayerTag,
    B4EvidenceLayers,
    tag_evidence_layer,
    tag_benchmark_evidence_layers,
    tag_ranked_entities,
    EVIDENCE_LAYER_PRIORITY,
    VALID_EVIDENCE_LAYERS,
)
from ike_v0.benchmarks.b1_harness import RankedEntity


class TestEvidenceLayerTag(unittest.TestCase):
    """Tests for EvidenceLayerTag dataclass."""

    def test_create_evidence_layer_tag(self):
        """Create an evidence layer tag with all fields."""
        tag = EvidenceLayerTag(
            entity_name="Test Entity",
            entity_type="person",
            evidence_layer="expert_maintainer",
            reason="Test rationale",
            source_refs=["source-1", "source-2"],
        )

        self.assertEqual(tag.entity_name, "Test Entity")
        self.assertEqual(tag.entity_type, "person")
        self.assertEqual(tag.evidence_layer, "expert_maintainer")
        self.assertEqual(tag.reason, "Test rationale")
        self.assertEqual(tag.source_refs, ["source-1", "source-2"])

    def test_evidence_layer_tag_to_dict(self):
        """EvidenceLayerTag serializes to dictionary correctly."""
        tag = EvidenceLayerTag(
            entity_name="Test",
            entity_type="repository",
            evidence_layer="implementation_repository",
            reason="Test",
        )

        data = tag.to_dict()

        self.assertEqual(data["entity_name"], "Test")
        self.assertEqual(data["entity_type"], "repository")
        self.assertEqual(data["evidence_layer"], "implementation_repository")
        self.assertEqual(data["reason"], "Test")
        self.assertEqual(data["source_refs"], [])

    def test_evidence_layer_tag_default_source_refs(self):
        """EvidenceLayerTag has empty list as default for source_refs."""
        tag = EvidenceLayerTag(
            entity_name="Test",
            entity_type="person",
            evidence_layer="expert_maintainer",
            reason="Test",
        )

        self.assertEqual(tag.source_refs, [])


class TestB4EvidenceLayers(unittest.TestCase):
    """Tests for B4EvidenceLayers dataclass."""

    def test_create_b4_evidence_layers(self):
        """Create a B4EvidenceLayers with tagged entities."""
        b4 = B4EvidenceLayers(
            tagged_entities=[
                EvidenceLayerTag(
                    entity_name="Entity1",
                    entity_type="person",
                    evidence_layer="expert_maintainer",
                    reason="Test",
                ),
            ],
            topic="harness",
        )

        self.assertEqual(len(b4.tagged_entities), 1)
        self.assertEqual(b4.topic, "harness")
        self.assertEqual(b4.benchmark_id, "B4-S1")

    def test_b4_evidence_layers_to_dict(self):
        """B4EvidenceLayers serializes to dictionary correctly."""
        b4 = B4EvidenceLayers(
            tagged_entities=[
                EvidenceLayerTag(
                    entity_name="Entity1",
                    entity_type="person",
                    evidence_layer="expert_maintainer",
                    reason="R1",
                ),
                EvidenceLayerTag(
                    entity_name="Entity2",
                    entity_type="repository",
                    evidence_layer="implementation_repository",
                    reason="R2",
                ),
            ],
            topic="test-concept",
            notes="Test notes",
        )

        data = b4.to_dict()

        self.assertEqual(len(data["tagged_entities"]), 2)
        self.assertEqual(data["topic"], "test-concept")
        self.assertEqual(data["benchmark_id"], "B4-S1")
        self.assertEqual(data["notes"], "Test notes")
        self.assertIn("limitations", data)

    def test_b4_evidence_layers_default_values(self):
        """B4EvidenceLayers has correct default values."""
        b4 = B4EvidenceLayers()

        self.assertEqual(b4.tagged_entities, [])
        self.assertEqual(b4.topic, "harness")
        self.assertEqual(b4.benchmark_id, "B4-S1")
        self.assertEqual(b4.notes, "")
        self.assertEqual(b4.limitations, [])


class TestEvidenceLayerPriority(unittest.TestCase):
    """Tests for evidence layer priority constants."""

    def test_all_valid_layers_have_priority(self):
        """All valid evidence layers have priority values."""
        for layer in VALID_EVIDENCE_LAYERS:
            self.assertIn(layer, EVIDENCE_LAYER_PRIORITY)
            self.assertGreater(EVIDENCE_LAYER_PRIORITY[layer], 0)

    def test_authoritative_is_highest_priority(self):
        """authoritative_official has highest priority."""
        self.assertEqual(EVIDENCE_LAYER_PRIORITY["authoritative_official"], 5)

    def test_media_is_lowest_priority(self):
        """media_context has lowest priority."""
        self.assertEqual(EVIDENCE_LAYER_PRIORITY["media_context"], 1)

    def test_priority_ordering(self):
        """Evidence layers are ordered correctly by priority."""
        self.assertGreater(
            EVIDENCE_LAYER_PRIORITY["authoritative_official"],
            EVIDENCE_LAYER_PRIORITY["expert_maintainer"]
        )
        self.assertGreater(
            EVIDENCE_LAYER_PRIORITY["expert_maintainer"],
            EVIDENCE_LAYER_PRIORITY["implementation_repository"]
        )
        self.assertGreater(
            EVIDENCE_LAYER_PRIORITY["implementation_repository"],
            EVIDENCE_LAYER_PRIORITY["community_discourse"]
        )
        self.assertGreater(
            EVIDENCE_LAYER_PRIORITY["community_discourse"],
            EVIDENCE_LAYER_PRIORITY["media_context"]
        )


class TestTagEvidenceLayer(unittest.TestCase):
    """Tests for tag_evidence_layer helper."""

    def test_tag_authoritative_official_from_official_keyword(self):
        """Official keyword triggers authoritative_official layer."""
        tag = tag_evidence_layer(
            entity_name="Official Docs",
            entity_type="repository",
            relevance_reason="Official project documentation",
        )

        self.assertEqual(tag.evidence_layer, "authoritative_official")

    def test_tag_authoritative_official_from_org_owned(self):
        """Organization-owned triggers authoritative_official layer."""
        tag = tag_evidence_layer(
            entity_name="Org Repo",
            entity_type="repository",
            relevance_reason="Organization-owned repository",
        )

        self.assertEqual(tag.evidence_layer, "authoritative_official")

    def test_tag_expert_maintainer_person_with_author_signal(self):
        """Person with author signal gets expert_maintainer layer."""
        tag = tag_evidence_layer(
            entity_name="John Doe",
            entity_type="person",
            relevance_reason="Primary author and maintainer",
        )

        self.assertEqual(tag.evidence_layer, "expert_maintainer")

    def test_tag_expert_maintainer_person_with_core_signal(self):
        """Person with core signal gets expert_maintainer layer."""
        tag = tag_evidence_layer(
            entity_name="Jane Smith",
            entity_type="person",
            relevance_reason="Core contributor",
        )

        self.assertEqual(tag.evidence_layer, "expert_maintainer")

    def test_tag_implementation_repository_from_type(self):
        """Repository type gets implementation_repository layer."""
        tag = tag_evidence_layer(
            entity_name="test-repo",
            entity_type="repository",
            relevance_reason="Testing framework",
        )

        self.assertEqual(tag.evidence_layer, "implementation_repository")

    def test_tag_implementation_repository_from_technical_signal(self):
        """Technical implementation signals trigger implementation_repository."""
        tag = tag_evidence_layer(
            entity_name="Some Entity",
            entity_type="person",
            relevance_reason="Implementation patterns and technical integration",
        )

        self.assertEqual(tag.evidence_layer, "implementation_repository")

    def test_tag_community_discourse_from_type(self):
        """Community type gets community_discourse layer."""
        tag = tag_evidence_layer(
            entity_name="DevForum",
            entity_type="community",
            relevance_reason="Developer community",
        )

        self.assertEqual(tag.evidence_layer, "community_discourse")

    def test_tag_community_discourse_from_discussion_signal(self):
        """Discussion signals trigger community_discourse layer."""
        tag = tag_evidence_layer(
            entity_name="Some Entity",
            entity_type="person",
            relevance_reason="Community discussion and adoption chatter",
        )

        self.assertEqual(tag.evidence_layer, "community_discourse")

    def test_tag_media_context_from_type(self):
        """Media type gets media_context layer."""
        tag = tag_evidence_layer(
            entity_name="Tech News",
            entity_type="media",
            relevance_reason="News coverage",
        )

        self.assertEqual(tag.evidence_layer, "media_context")

    def test_tag_media_context_from_article_signal(self):
        """Article signals trigger media_context layer."""
        tag = tag_evidence_layer(
            entity_name="Some Entity",
            entity_type="person",
            relevance_reason="Article and blog coverage",
        )

        self.assertEqual(tag.evidence_layer, "media_context")

    def test_tag_default_organization_to_authoritative(self):
        """Organization type defaults to authoritative_official."""
        tag = tag_evidence_layer(
            entity_name="ACME Corp",
            entity_type="organization",
            relevance_reason="Research organization",
        )

        self.assertEqual(tag.evidence_layer, "authoritative_official")

    def test_tag_default_person_to_expert(self):
        """Person type defaults to expert_maintainer."""
        tag = tag_evidence_layer(
            entity_name="John Doe",
            entity_type="person",
            relevance_reason="Works on related projects",
        )

        self.assertEqual(tag.evidence_layer, "expert_maintainer")

    def test_tag_default_repository_to_implementation(self):
        """Repository type defaults to implementation_repository."""
        tag = tag_evidence_layer(
            entity_name="some-repo",
            entity_type="repository",
            relevance_reason="Some repository",
        )

        self.assertEqual(tag.evidence_layer, "implementation_repository")

    def test_tag_default_community_to_discourse(self):
        """Community type defaults to community_discourse."""
        tag = tag_evidence_layer(
            entity_name="Forum",
            entity_type="community",
            relevance_reason="Some community",
        )

        self.assertEqual(tag.evidence_layer, "community_discourse")

    def test_tag_default_unknown_to_media(self):
        """Unknown entity type defaults to media_context."""
        tag = tag_evidence_layer(
            entity_name="Unknown Entity",
            entity_type="unknown_type",
            relevance_reason="No signals",
        )

        self.assertEqual(tag.evidence_layer, "media_context")

    def test_tag_preserves_source_refs(self):
        """Source references are preserved in the tag."""
        tag = tag_evidence_layer(
            entity_name="Test",
            entity_type="person",
            relevance_reason="Test",
            source_refs=["github:user/test", "twitter:test"],
        )

        self.assertEqual(tag.source_refs, ["github:user/test", "twitter:test"])

    def test_tag_includes_reason(self):
        """Tag includes a human-readable reason."""
        tag = tag_evidence_layer(
            entity_name="Test",
            entity_type="person",
            relevance_reason="Primary author",
        )

        self.assertTrue(len(tag.reason) > 0)


class TestTagBenchmarkEvidenceLayers(unittest.TestCase):
    """Tests for tag_benchmark_evidence_layers helper."""

    def test_tag_list_of_entities(self):
        """Tag a list of entity dicts."""
        entities = [
            {"name": "Person A", "type": "person", "relevance_reason": "Author"},
            {"name": "Repo B", "type": "repository", "relevance_reason": "Tool"},
            {"name": "Org C", "type": "organization"},
        ]

        result = tag_benchmark_evidence_layers(entities)

        self.assertIsInstance(result, B4EvidenceLayers)
        self.assertEqual(len(result.tagged_entities), 3)

    def test_tag_skips_empty_names(self):
        """Entities without names are skipped."""
        entities = [
            {"type": "person"},  # No name
            {"name": "Valid", "type": "person"},
        ]

        result = tag_benchmark_evidence_layers(entities)

        self.assertEqual(len(result.tagged_entities), 1)
        self.assertEqual(result.tagged_entities[0].entity_name, "Valid")

    def test_tag_sorts_by_priority(self):
        """Tagged entities are sorted by evidence layer priority."""
        entities = [
            {"name": "Media", "type": "media"},
            {"name": "Person", "type": "person"},
            {"name": "Official", "type": "organization", "relevance_reason": "Official"},
        ]

        result = tag_benchmark_evidence_layers(entities)

        # Should be sorted: authoritative > expert > media
        self.assertEqual(result.tagged_entities[0].evidence_layer, "authoritative_official")
        self.assertEqual(result.tagged_entities[1].evidence_layer, "expert_maintainer")
        self.assertEqual(result.tagged_entities[2].evidence_layer, "media_context")

    def test_tag_includes_notes(self):
        """Result includes explanatory notes."""
        entities = [
            {"name": "Test", "type": "person"},
        ]

        result = tag_benchmark_evidence_layers(entities)

        self.assertTrue(len(result.notes) > 0)
        self.assertIn("harness", result.notes.lower())

    def test_tag_includes_limitations(self):
        """Result includes explicit limitations."""
        entities = [
            {"name": "Test", "type": "person"},
        ]

        result = tag_benchmark_evidence_layers(entities)

        self.assertTrue(len(result.limitations) > 0)
        self.assertIn("heuristic", result.limitations[0].lower())

    def test_tag_custom_topic(self):
        """Tagging supports custom topic parameter."""
        entities = [
            {"name": "Test", "type": "person"},
        ]

        result = tag_benchmark_evidence_layers(entities, topic="custom-concept")

        self.assertEqual(result.topic, "custom-concept")
        self.assertIn("custom-concept", result.notes.lower())

    def test_tag_handles_missing_fields(self):
        """Entities with missing fields are handled gracefully."""
        entities = [
            {"name": "Entity"},  # Missing type, relevance_reason
            {"type": "person"},  # Missing name
        ]

        result = tag_benchmark_evidence_layers(entities)

        # Should have one entity (the one with name)
        self.assertEqual(len(result.tagged_entities), 1)
        self.assertEqual(result.tagged_entities[0].entity_name, "Entity")


class TestTagRankedEntities(unittest.TestCase):
    """Tests for tag_ranked_entities helper."""

    def test_tag_ranked_entities(self):
        """Tag RankedEntity objects from B1."""
        entities = [
            RankedEntity(
                name="Core Author",
                entity_type="person",
                signal_score=0.9,
                relevance_reason="Primary author and maintainer",
                source_refs=["github:author"],
            ),
            RankedEntity(
                name="Tool Repo",
                entity_type="repository",
                signal_score=0.8,
                relevance_reason="Implementation framework",
            ),
        ]

        result = tag_ranked_entities(entities)

        self.assertIsInstance(result, B4EvidenceLayers)
        self.assertEqual(len(result.tagged_entities), 2)

    def test_tag_ranked_entities_preserves_source_refs(self):
        """Source refs from RankedEntity are preserved."""
        entities = [
            RankedEntity(
                name="Test",
                entity_type="person",
                signal_score=0.9,
                relevance_reason="Test",
                source_refs=["source-1", "source-2"],
            ),
        ]

        result = tag_ranked_entities(entities)

        self.assertEqual(result.tagged_entities[0].source_refs, ["source-1", "source-2"])

    def test_tag_ranked_entities_sorts_by_priority(self):
        """Ranked entities are sorted by evidence layer priority."""
        entities = [
            RankedEntity(name="Media", entity_type="media", signal_score=0.5, relevance_reason="News"),
            RankedEntity(name="Person", entity_type="person", signal_score=0.6, relevance_reason="Author"),
            RankedEntity(name="Org", entity_type="organization", signal_score=0.7, relevance_reason="Official"),
        ]

        result = tag_ranked_entities(entities)

        # Should be sorted: authoritative > expert > media
        layers = [e.evidence_layer for e in result.tagged_entities]
        self.assertEqual(layers[0], "authoritative_official")
        self.assertEqual(layers[1], "expert_maintainer")
        self.assertEqual(layers[2], "media_context")


class TestEvidenceLayerDistribution(unittest.TestCase):
    """Tests for evidence layer distribution in results."""

    def test_distribution_in_notes(self):
        """Notes include distribution of evidence layers."""
        entities = [
            {"name": "Official", "type": "organization", "relevance_reason": "Official"},
            {"name": "Author", "type": "person", "relevance_reason": "Maintainer"},
            {"name": "Repo", "type": "repository"},
            {"name": "Community", "type": "community"},
            {"name": "Article", "type": "media"},
        ]

        result = tag_benchmark_evidence_layers(entities)

        # Notes should mention all 5 layers
        self.assertIn("authoritative_official", result.notes.lower())
        self.assertIn("expert_maintainer", result.notes.lower())
        self.assertIn("implementation_repository", result.notes.lower())
        self.assertIn("community_discourse", result.notes.lower())
        self.assertIn("media_context", result.notes.lower())


if __name__ == "__main__":
    unittest.main()
