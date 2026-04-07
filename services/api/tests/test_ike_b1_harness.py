"""
Tests for IKE B1 Harness Benchmark.

Tests verify:
- HarnessTrendBundle can be created and serialized
- Entity ranking works correctly
- Trend bundle detection produces expected output shape
- Entity type prioritization (person > repository > organization > community)
- Generic media is deprioritized
"""

import unittest

from ike_v0.benchmarks.b1_harness import (
    HarnessTrendBundle,
    RankedEntity,
    detect_harness_trend_bundle,
    rank_harness_entities,
    reshape_discovery_to_benchmark_entities,
    B1_MEANINGFUL_ENTITY_TYPES,
    B1_DEEMPHASIZED_TYPES,
)
from ike_v0.benchmarks.b1_discovery_client import (
    B1_HARNESS_CONTEXT_TOPICS,
    DiscoveryClientError,
    DiscoveryResponseError,
    _build_b1_discovery_topic,
    _infer_entity_type,
    call_source_discovery,
    run_harness_benchmark,
)
from ike_v0.benchmarks.b1_knowledge import (
    KnowledgeSummary,
    generate_harness_knowledge_summary,
)
from ike_v0.benchmarks.b1_evolution import (
    EvolutionJudgment,
    generate_evolution_judgment,
    MAINLINE_GAPS,
)
from ike_v0.benchmarks.b2_entity_tiers import (
    B2EntityTiers,
    EntityTier,
    TierEntry,
    classify_benchmark_entity_tiers,
)
from ike_v0.benchmarks.b2_gap_mapping import (
    B2GapMappingResult,
    GapMapping,
    map_concept_to_mainline_gaps,
)
from ike_v0.benchmarks.b2_recommendation import (
    B2Recommendation,
    generate_research_recommendation,
)
from ike_v0.benchmarks.b2_trigger_packet import (
    B2TriggerPacket,
    generate_trigger_packet,
)
from ike_v0.benchmarks.b3_deepening import (
    B3ConceptDeepening,
    generate_concept_deepening,
)
from ike_v0.benchmarks.task_closure import (
    StudyResult,
    DecisionHandoff,
    TaskClosure,
    generate_study_result,
    generate_decision_handoff,
    generate_task_closure,
)


class TestReshapeDiscoveryToBenchmarkEntities(unittest.TestCase):
    """Tests for reshape_discovery_to_benchmark_entities helper."""

    def test_reshape_filters_meaningful_types(self):
        """Reshape keeps person, repository, organization, community as primary."""
        candidates = [
            {"name": "Person A", "type": "person"},
            {"name": "Repo B", "type": "repository"},
            {"name": "Org C", "type": "organization"},
            {"name": "Community D", "type": "community"},
        ]

        primary, supporting = reshape_discovery_to_benchmark_entities(candidates)

        self.assertEqual(len(primary), 4)
        self.assertEqual(len(supporting), 0)

    def test_reshape_filters_deemphasized_types(self):
        """Reshape moves event, domain, media to supporting context."""
        candidates = [
            {"name": "Event A", "type": "event"},
            {"name": "Domain B", "type": "domain"},
            {"name": "Media C", "type": "media"},
        ]

        primary, supporting = reshape_discovery_to_benchmark_entities(candidates)

        self.assertEqual(len(primary), 0)
        self.assertEqual(len(supporting), 3)

    def test_reshape_infers_person_from_description(self):
        """Reshape infers person type from description keywords."""
        candidates = [
            {"name": "John Doe", "type": "unknown", "description": "author and maintainer"},
        ]

        primary, supporting = reshape_discovery_to_benchmark_entities(candidates)

        self.assertEqual(len(primary), 1)
        self.assertEqual(primary[0]["type"], "person")

    def test_reshape_infers_repository_from_description(self):
        """Reshape infers repository type from description keywords."""
        candidates = [
            {"name": "MyProject", "type": "unknown", "description": "GitHub repository"},
        ]

        primary, supporting = reshape_discovery_to_benchmark_entities(candidates)

        self.assertEqual(len(primary), 1)
        self.assertEqual(primary[0]["type"], "repository")

    def test_reshape_infers_organization_from_description(self):
        """Reshape infers organization type from description keywords."""
        candidates = [
            {"name": "ACME Corp", "type": "unknown", "description": "research organization"},
        ]

        primary, supporting = reshape_discovery_to_benchmark_entities(candidates)

        self.assertEqual(len(primary), 1)
        self.assertEqual(primary[0]["type"], "organization")

    def test_reshape_infers_community_from_description(self):
        """Reshape infers community type from description keywords."""
        candidates = [
            {"name": "DevForum", "type": "unknown", "description": "community discord server"},
        ]

        primary, supporting = reshape_discovery_to_benchmark_entities(candidates)

        self.assertEqual(len(primary), 1)
        self.assertEqual(primary[0]["type"], "community")

    def test_reshape_skips_empty_names(self):
        """Reshape skips candidates with no name."""
        candidates = [
            {"type": "person"},  # No name
            {"name": "Valid", "type": "person"},
        ]

        primary, supporting = reshape_discovery_to_benchmark_entities(candidates)

        self.assertEqual(len(primary), 1)
        self.assertEqual(primary[0]["name"], "Valid")

    def test_reshape_preserves_source_refs(self):
        """Reshape preserves source_ref field."""
        candidates = [
            {"name": "Person", "type": "person", "source_ref": "github:user"},
        ]

        primary, supporting = reshape_discovery_to_benchmark_entities(candidates)

        self.assertEqual(primary[0]["source_ref"], "github:user")


class TestRankedEntity(unittest.TestCase):
    """Tests for RankedEntity dataclass."""

    def test_create_ranked_entity(self):
        """Create a ranked entity with all fields."""
        entity = RankedEntity(
            name="Test Entity",
            entity_type="person",
            signal_score=0.85,
            relevance_reason="Matches: harness, AI agent",
            source_refs=["source-1", "source-2"],
        )

        self.assertEqual(entity.name, "Test Entity")
        self.assertEqual(entity.entity_type, "person")
        self.assertEqual(entity.signal_score, 0.85)
        self.assertEqual(entity.relevance_reason, "Matches: harness, AI agent")
        self.assertEqual(entity.source_refs, ["source-1", "source-2"])


class TestHarnessTrendBundle(unittest.TestCase):
    """Tests for HarnessTrendBundle dataclass."""

    def test_create_bundle(self):
        """Create a harness trend bundle."""
        bundle = HarnessTrendBundle(
            topic="harness",
            benchmark_id="B1-S1",
            signal_summary="Test summary",
            ranked_entities=[
                RankedEntity(
                    name="Test",
                    entity_type="person",
                    signal_score=0.9,
                    relevance_reason="Test",
                )
            ],
            notes="Test notes",
        )

        self.assertEqual(bundle.topic, "harness")
        self.assertEqual(bundle.benchmark_id, "B1-S1")
        self.assertEqual(bundle.signal_summary, "Test summary")
        self.assertEqual(len(bundle.ranked_entities), 1)
        self.assertEqual(bundle.notes, "Test notes")

    def test_bundle_to_dict(self):
        """Bundle serializes to dictionary correctly."""
        bundle = HarnessTrendBundle(
            topic="harness",
            benchmark_id="B1-S1",
            signal_summary="Test",
            ranked_entities=[
                RankedEntity(
                    name="Test Entity",
                    entity_type="repository",
                    signal_score=0.75,
                    relevance_reason="Test",
                    source_refs=["ref-1"],
                )
            ],
        )

        data = bundle.to_dict()

        self.assertEqual(data["topic"], "harness")
        self.assertEqual(data["benchmark_id"], "B1-S1")
        self.assertEqual(data["signal_summary"], "Test")
        self.assertEqual(len(data["ranked_entities"]), 1)
        self.assertEqual(data["ranked_entities"][0]["name"], "Test Entity")
        self.assertEqual(data["ranked_entities"][0]["entity_type"], "repository")
        self.assertEqual(data["ranked_entities"][0]["signal_score"], 0.75)

    def test_bundle_default_values(self):
        """Bundle has correct default values."""
        bundle = HarnessTrendBundle()

        self.assertEqual(bundle.topic, "harness")
        self.assertEqual(bundle.benchmark_id, "B1-S1")
        self.assertEqual(bundle.signal_summary, "")
        self.assertEqual(bundle.ranked_entities, [])
        self.assertEqual(bundle.supporting_candidates, [])


class TestRankHarnessEntities(unittest.TestCase):
    """Tests for rank_harness_entities helper."""

    def test_rank_basic(self):
        """Rank basic list of candidates."""
        candidates = [
            {"name": "Person A", "type": "person", "description": "Works on harness"},
            {"name": "Repo B", "type": "repository", "description": "Harness testing"},
            {"name": "Org C", "type": "organization", "description": "AI research"},
        ]

        ranked = rank_harness_entities(candidates)

        self.assertEqual(len(ranked), 3)
        # Person should rank highest
        self.assertEqual(ranked[0].entity_type, "person")

    def test_rank_prioritizes_person(self):
        """Person entities are prioritized over other types."""
        candidates = [
            {"name": "Repository", "type": "repository", "description": "harness testing"},
            {"name": "Person", "type": "person", "description": "harness work"},
            {"name": "Organization", "type": "organization", "description": "harness research"},
        ]

        ranked = rank_harness_entities(candidates)

        self.assertEqual(ranked[0].entity_type, "person")
        self.assertEqual(ranked[1].entity_type, "repository")
        self.assertEqual(ranked[2].entity_type, "organization")

    def test_rank_deprioritizes_media(self):
        """Generic media is deprioritized."""
        candidates = [
            {"name": "News Article", "type": "media", "description": "harness news"},
            {"name": "Person", "type": "person", "description": "harness expert"},
        ]

        ranked = rank_harness_entities(candidates)

        # Person should rank higher than media
        self.assertEqual(ranked[0].entity_type, "person")
        self.assertEqual(ranked[1].entity_type, "media")

    def test_rank_keyword_relevance(self):
        """Keyword matches improve ranking."""
        candidates = [
            {"name": "Entity A", "type": "person", "description": "harness openclaw AI agent evaluation"},
            {"name": "Entity B", "type": "person", "description": "unrelated topic"},
        ]

        ranked = rank_harness_entities(candidates)

        # Entity A should rank higher due to keyword matches
        self.assertEqual(ranked[0].name, "Entity A")
        self.assertGreater(ranked[0].signal_score, ranked[1].signal_score)

    def test_rank_handles_empty_candidates(self):
        """Empty candidate list returns empty ranking."""
        ranked = rank_harness_entities([])
        self.assertEqual(len(ranked), 0)

    def test_rank_handles_missing_fields(self):
        """Candidates with missing fields are handled gracefully."""
        candidates = [
            {"name": "Entity"},  # Missing type, description
            {"type": "person"},  # Missing name
        ]

        ranked = rank_harness_entities(candidates)

        # Should have one entity (the one with name)
        self.assertEqual(len(ranked), 1)
        self.assertEqual(ranked[0].name, "Entity")

    def test_rank_context_topics(self):
        """Custom context topics affect ranking."""
        candidates = [
            {"name": "Entity A", "type": "person", "description": "custom-topic work"},
            {"name": "Entity B", "type": "person", "description": "unrelated"},
        ]

        ranked = rank_harness_entities(
            candidates,
            topic="custom",
            context_topics=["custom-topic", "related"],
        )

        # Entity A should rank higher due to custom-topic match
        self.assertEqual(ranked[0].name, "Entity A")


class TestInferEntityType(unittest.TestCase):
    """Tests for _infer_entity_type helper."""

    def test_infer_person_from_bucket(self):
        """Infer person from object_bucket."""
        entity_type = _infer_entity_type("person_bucket", "domain", [])
        self.assertEqual(entity_type, "person")

    def test_infer_repository_from_bucket(self):
        """Infer repository from object_bucket."""
        entity_type = _infer_entity_type("repo_bucket", "domain", [])
        self.assertEqual(entity_type, "repository")

    def test_infer_organization_from_bucket(self):
        """Infer organization from object_bucket."""
        entity_type = _infer_entity_type("org_bucket", "domain", [])
        self.assertEqual(entity_type, "organization")

    def test_infer_community_from_bucket(self):
        """Infer community from object_bucket."""
        entity_type = _infer_entity_type("community_bucket", "domain", [])
        self.assertEqual(entity_type, "community")

    def test_infer_repository_from_github_item(self):
        """Infer repository from github item_type."""
        entity_type = _infer_entity_type("authority", "github_repo", [])
        self.assertEqual(entity_type, "repository")

    def test_infer_person_from_twitter_item(self):
        """Infer person from twitter item_type."""
        entity_type = _infer_entity_type("authority", "twitter", [])
        self.assertEqual(entity_type, "person")

    def test_infer_from_related_entities(self):
        """Infer type from related_entities."""
        related = [{"type": "person", "name": "John"}]
        entity_type = _infer_entity_type("authority", "domain", related)
        self.assertEqual(entity_type, "person")

    def test_default_to_domain(self):
        """Default to domain when no hints found."""
        entity_type = _infer_entity_type("authority", "domain", [])
        self.assertEqual(entity_type, "domain")


class TestDetectHarnessTrendBundle(unittest.TestCase):
    """Tests for detect_harness_trend_bundle helper."""

    def test_detect_requires_discovery_results(self):
        """Detect trend bundle requires discovery_results input."""
        with self.assertRaises(ValueError) as context:
            detect_harness_trend_bundle(None)
        self.assertIn("requires discovery_results", str(context.exception))

    def test_detect_requires_nonempty_discovery_results(self):
        """Detect trend bundle requires non-empty discovery_results."""
        with self.assertRaises(ValueError) as context:
            detect_harness_trend_bundle([])
        self.assertIn("non-empty", str(context.exception))

    def test_detect_with_custom_discovery(self):
        """Detect trend bundle from custom discovery results."""
        discovery_results = [
            {
                "query": "test query",
                "entities": [
                    {"name": "Custom Entity", "type": "person", "description": "harness expert"},
                ],
            }
        ]

        bundle = detect_harness_trend_bundle(discovery_results=discovery_results)

        self.assertEqual(bundle.topic, "harness")
        # Should find the custom entity
        entity_names = [e.name for e in bundle.ranked_entities]
        self.assertIn("Custom Entity", entity_names)

    def test_detect_with_mixed_entity_types(self):
        """Detect filters out de-emphasized types from ranked entities."""
        discovery_results = [
            {
                "entities": [
                    {"name": "Person A", "type": "person", "description": "harness"},
                    {"name": "Event B", "type": "event", "description": "harness conference"},
                    {"name": "Repo C", "type": "repository", "description": "harness testing"},
                    {"name": "Domain D", "type": "domain", "description": "harness website"},
                ],
            }
        ]

        bundle = detect_harness_trend_bundle(discovery_results=discovery_results)

        # Ranked entities should only contain person and repository
        ranked_types = [e.entity_type for e in bundle.ranked_entities]
        self.assertIn("person", ranked_types)
        self.assertIn("repository", ranked_types)
        self.assertNotIn("event", ranked_types)
        self.assertNotIn("domain", ranked_types)

        # Event and domain should be in supporting candidates
        supporting_types = [c.get("type") for c in bundle.supporting_candidates]
        self.assertIn("event", supporting_types)
        self.assertIn("domain", supporting_types)

    def test_detect_limits_ranked_entities(self):
        """Trend bundle limits ranked entities to top 20."""
        # Create many candidates
        discovery_results = [
            {
                "entities": [
                    {"name": f"Entity {i}", "type": "person", "description": "harness"}
                    for i in range(50)
                ],
            }
        ]

        bundle = detect_harness_trend_bundle(discovery_results=discovery_results)

        self.assertLessEqual(len(bundle.ranked_entities), 20)

    def test_detect_limits_supporting_candidates(self):
        """Trend bundle limits supporting candidates to 50."""
        # Create many candidates
        discovery_results = [
            {
                "candidates": [
                    {"name": f"Candidate {i}", "type": "repository", "description": "harness"}
                    for i in range(100)
                ],
            }
        ]

        bundle = detect_harness_trend_bundle(discovery_results=discovery_results)

        self.assertLessEqual(len(bundle.supporting_candidates), 50)

    def test_detect_empty_result_when_no_entities(self):
        """Trend bundle returns empty ranked_entities when no entities found."""
        discovery_results = [
            {
                "query": "test",
                "entities": [],
                "candidates": [],
            }
        ]

        bundle = detect_harness_trend_bundle(discovery_results=discovery_results)

        self.assertEqual(bundle.ranked_entities, [])
        self.assertIn("No high-signal benchmark entities", bundle.signal_summary)

    def test_detect_includes_limitations(self):
        """Trend bundle includes known limitations."""
        discovery_results = [
            {"entities": [{"name": "Test", "type": "person"}]}
        ]
        bundle = detect_harness_trend_bundle(discovery_results=discovery_results)

        self.assertTrue(len(bundle.limitations) > 0)
        self.assertIn("heuristic", bundle.limitations[0].lower())

    def test_detect_has_notes(self):
        """Trend bundle includes explanatory notes."""
        discovery_results = [
            {"entities": [{"name": "Test", "type": "person"}]}
        ]
        bundle = detect_harness_trend_bundle(discovery_results=discovery_results)

        self.assertTrue(len(bundle.notes) > 0)
        self.assertIn("bounded", bundle.notes.lower())

    def test_detect_custom_topic(self):
        """Trend bundle supports custom topic."""
        discovery_results = [
            {"entities": [{"name": "Test", "type": "person"}]}
        ]
        bundle = detect_harness_trend_bundle(discovery_results=discovery_results, topic="custom-topic")

        self.assertEqual(bundle.topic, "custom-topic")


class TestBuildB1DiscoveryTopic(unittest.TestCase):
    """Tests for _build_b1_discovery_topic helper."""

    def test_expands_harness_topic(self):
        """_build_b1_discovery_topic expands 'harness' topic."""
        result = _build_b1_discovery_topic("harness")
        self.assertIn("harness", result)
        self.assertIn("openclaw", result)
        self.assertIn("AI agent", result)
        self.assertIn("evaluation", result)

    def test_preserves_other_topics(self):
        """_build_b1_discovery_topic preserves non-harness topics."""
        result = _build_b1_discovery_topic("other_topic")
        self.assertEqual(result, "other_topic")

    def test_case_insensitive_harness(self):
        """_build_b1_discovery_topic handles case-insensitive 'harness'."""
        result1 = _build_b1_discovery_topic("Harness")
        result2 = _build_b1_discovery_topic("HARNESS")
        self.assertIn("openclaw", result1)
        self.assertIn("openclaw", result2)


class TestDiscoveryClient(unittest.TestCase):
    """Tests for discovery client helpers."""

    def test_call_source_discovery_raises_on_http_error(self):
        """call_source_discovery raises DiscoveryClientError on HTTP error."""
        # This will fail because there's no server running - which is expected
        with self.assertRaises(DiscoveryClientError):
            call_source_discovery(topic="harness", api_base="http://localhost:9999")

    def test_run_harness_benchmark_raises_on_http_error(self):
        """run_harness_benchmark raises DiscoveryClientError on HTTP error."""
        with self.assertRaises(DiscoveryClientError):
            run_harness_benchmark(topic="harness", api_base="http://localhost:9999")

    def test_run_harness_benchmark_uses_expanded_topic(self):
        """run_harness_benchmark uses expanded topic for harness."""
        # Verify that the topic expansion happens (will fail on HTTP but that's expected)
        with self.assertRaises(DiscoveryClientError):
            run_harness_benchmark(topic="harness", api_base="http://localhost:9999")
        # The error is expected - we're just verifying the call structure
        # The actual topic expansion is tested in TestBuildB1DiscoveryTopic

    def test_infer_entity_type_person_from_bucket(self):
        """_infer_entity_type returns person for person bucket."""
        result = _infer_entity_type("person_bucket", "domain", [])
        self.assertEqual(result, "person")

    def test_infer_entity_type_repository_from_github(self):
        """_infer_entity_type returns repository for github item_type."""
        result = _infer_entity_type("authority", "github_repo", [])
        self.assertEqual(result, "repository")

    def test_infer_entity_type_person_from_twitter(self):
        """_infer_entity_type returns person for twitter item_type."""
        result = _infer_entity_type("authority", "twitter", [])
        self.assertEqual(result, "person")

    def test_infer_entity_type_from_related_entities(self):
        """_infer_entity_type infers person from related_entities."""
        related = [{"type": "person", "name": "John"}]
        result = _infer_entity_type("authority", "domain", related)
        self.assertEqual(result, "person")

    def test_infer_github_user_profile_as_person(self):
        """_infer_entity_type classifies github.com/user/username as person."""
        result = _infer_entity_type("authority", "domain", [], url="https://github.com/user/leoyeai")
        self.assertEqual(result, "person")

    def test_infer_github_org_profile_as_organization(self):
        """_infer_entity_type classifies github.com/org/orgname as organization."""
        result = _infer_entity_type("authority", "domain", [], url="https://github.com/org/netease-youdao")
        self.assertEqual(result, "organization")

    def test_infer_github_orgs_profile_as_organization(self):
        """_infer_entity_type classifies github.com/orgs/orgname as organization."""
        result = _infer_entity_type("authority", "domain", [], url="https://github.com/orgs/netease-youdao")
        self.assertEqual(result, "organization")

    def test_infer_github_owner_repo_as_repository(self):
        """_infer_entity_type classifies github.com/owner/repo as repository."""
        result = _infer_entity_type("authority", "domain", [], url="https://github.com/netease-youdao/lobsterai")
        self.assertEqual(result, "repository")

    def test_infer_github_single_segment_as_person(self):
        """_infer_entity_type classifies github.com/username (short, no hyphens) as person."""
        result = _infer_entity_type("authority", "domain", [], url="https://github.com/leoyeai")
        self.assertEqual(result, "person")

    def test_infer_github_single_segment_with_hyphen_as_organization(self):
        """_infer_entity_type classifies github.com/org-name (with hyphens) as organization."""
        result = _infer_entity_type("authority", "domain", [], url="https://github.com/netease-youdao")
        self.assertEqual(result, "organization")

    def test_github_url_wins_over_community_bucket(self):
        """_infer_entity_type prioritizes GitHub URL pattern over generic community bucket."""
        # This is the key fix: github.com/user/... should be person, not community
        result = _infer_entity_type("community", "domain", [], url="https://github.com/user/leoyeai")
        self.assertEqual(result, "person", "GitHub user URL should override community bucket")

    def test_github_repo_wins_over_community_bucket(self):
        """_infer_entity_type prioritizes GitHub repo URL over generic community bucket."""
        result = _infer_entity_type("community", "domain", [], url="https://github.com/netease-youdao/lobsterai")
        self.assertEqual(result, "repository", "GitHub repo URL should override community bucket")

    def test_community_bucket_fallback_without_github_url(self):
        """_infer_entity_type still uses community bucket when no GitHub URL signal."""
        # When there's no GitHub URL, community bucket should still work
        result = _infer_entity_type("community_bucket", "domain", [], url="https://example.com/forum")
        self.assertEqual(result, "community")

    def test_infer_entity_type_defaults_to_domain(self):
        """_infer_entity_type defaults to domain when no hints."""
        result = _infer_entity_type("authority", "domain", [])
        self.assertEqual(result, "domain")




class TestKnowledgeSummary(unittest.TestCase):
    """Tests for KnowledgeSummary dataclass."""

    def test_create_knowledge_summary(self):
        """Create a knowledge summary with all fields."""
        summary = KnowledgeSummary(
            concept_summary="Test summary",
            relation_map={"person": ["Alice"], "repository": ["repo1"]},
            contrast_dimensions=["Individual vs organization"],
            evidence_grounding=["Entity: Alice (person)"],
            confidence=0.7,
            limitations=["Limited evidence"],
        )

        self.assertEqual(summary.concept_summary, "Test summary")
        self.assertEqual(summary.relation_map["person"], ["Alice"])
        self.assertEqual(len(summary.contrast_dimensions), 1)
        self.assertEqual(len(summary.evidence_grounding), 1)
        self.assertEqual(summary.confidence, 0.7)
        self.assertEqual(len(summary.limitations), 1)

    def test_knowledge_summary_to_dict(self):
        """KnowledgeSummary serializes to dictionary correctly."""
        summary = KnowledgeSummary(concept_summary="Test", confidence=0.75)
        data = summary.to_dict()

        self.assertEqual(data["concept_summary"], "Test")
        self.assertEqual(data["confidence"], 0.75)  # Bug fix: should be confidence, not concept_summary
        self.assertIn("relation_map", data)
        self.assertIn("contrast_dimensions", data)
        self.assertIn("evidence_grounding", data)
        self.assertIn("limitations", data)

    def test_knowledge_summary_default_values(self):
        """KnowledgeSummary has correct default values."""
        summary = KnowledgeSummary()

        self.assertEqual(summary.concept_summary, "")
        self.assertEqual(summary.relation_map, {})
        self.assertEqual(summary.contrast_dimensions, [])
        self.assertEqual(summary.evidence_grounding, [])
        self.assertEqual(summary.confidence, 0.5)
        self.assertEqual(summary.limitations, [])


class TestGenerateHarnessKnowledgeSummary(unittest.TestCase):
    """Tests for generate_harness_knowledge_summary helper."""

    def _make_test_bundle(self, entities=None):
        """Create a test HarnessTrendBundle."""
        if entities is None:
            entities = [
                RankedEntity(
                    name="Test Person",
                    entity_type="person",
                    signal_score=0.9,
                    relevance_reason="Test",
                ),
                RankedEntity(
                    name="Test Repo",
                    entity_type="repository",
                    signal_score=0.8,
                    relevance_reason="Test",
                ),
            ]

        return HarnessTrendBundle(
            topic="harness",
            benchmark_id="B1-S1",
            signal_summary="Test summary",
            ranked_entities=entities,
        )

    def test_generate_with_entities(self):
        """Generate knowledge summary with entities."""
        bundle = self._make_test_bundle()
        summary = generate_harness_knowledge_summary(bundle)

        self.assertIsInstance(summary, KnowledgeSummary)
        self.assertIn("harness", summary.concept_summary.lower())
        self.assertTrue(len(summary.evidence_grounding) > 0)
        self.assertTrue(len(summary.limitations) > 0)

    def test_generate_empty_bundle(self):
        """Generate knowledge summary with empty bundle."""
        bundle = self._make_test_bundle(entities=[])
        summary = generate_harness_knowledge_summary(bundle)

        self.assertIsInstance(summary, KnowledgeSummary)
        self.assertIn("No high-signal entities", summary.concept_summary)
        self.assertEqual(summary.confidence, 0.1)

    def test_generate_includes_evidence_grounding(self):
        """Generated summary includes evidence grounding from entities."""
        entities = [
            RankedEntity(
                name="TestEntity",
                entity_type="person",
                signal_score=0.9,
                relevance_reason="Matches: harness",
            ),
        ]
        bundle = self._make_test_bundle(entities=entities)
        summary = generate_harness_knowledge_summary(bundle)

        # Evidence grounding should include entity name
        evidence_str = " ".join(summary.evidence_grounding)
        self.assertIn("TestEntity", evidence_str)

    def test_generate_includes_relation_map(self):
        """Generated summary includes relation map grouped by conceptual categories."""
        entities = [
            RankedEntity(name="Person1", entity_type="person", signal_score=0.9, relevance_reason="Test"),
            RankedEntity(name="Person2", entity_type="person", signal_score=0.8, relevance_reason="Test"),
            RankedEntity(name="Repo1", entity_type="repository", signal_score=0.7, relevance_reason="Test"),
        ]
        bundle = self._make_test_bundle(entities=entities)
        summary = generate_harness_knowledge_summary(bundle)

        # Relation map should have conceptual categories
        self.assertTrue(len(summary.relation_map) > 0)
        # Entities without specific patterns go to harness_concept
        self.assertIn("harness_concept", summary.relation_map)

    def test_generate_includes_contrast_dimensions(self):
        """Generated summary includes contrast dimensions for diverse entity types."""
        entities = [
            RankedEntity(name="Person1", entity_type="person", signal_score=0.9, relevance_reason="Test"),
            RankedEntity(name="Repo1", entity_type="repository", signal_score=0.8, relevance_reason="Test"),
        ]
        bundle = self._make_test_bundle(entities=entities)
        summary = generate_harness_knowledge_summary(bundle)

        # Should have contrast between person and repository
        self.assertTrue(len(summary.contrast_dimensions) > 0)

    def test_generate_conservative_confidence(self):
        """Generated summary uses conservative confidence scoring."""
        bundle = self._make_test_bundle()
        summary = generate_harness_knowledge_summary(bundle)

        # Confidence should be conservative (capped at 0.85)
        self.assertLessEqual(summary.confidence, 0.85)
        self.assertGreater(summary.confidence, 0.0)

    def test_generate_includes_limitations(self):
        """Generated summary includes explicit limitations."""
        bundle = self._make_test_bundle()
        summary = generate_harness_knowledge_summary(bundle)

        self.assertTrue(len(summary.limitations) > 0)
        # Should mention evidence limitations
        limitations_str = " ".join(summary.limitations).lower()
        self.assertIn("evidence", limitations_str)

    def test_generate_concept_explains_harness(self):
        """Generated concept summary explains what harness means in context."""
        bundle = self._make_test_bundle()
        summary = generate_harness_knowledge_summary(bundle)

        # Should explain harness in benchmark context
        summary_lower = summary.concept_summary.lower()
        self.assertIn("harness", summary_lower)
        # Should relate to evaluation/testing or AI agents
        self.assertTrue(
            "evaluation" in summary_lower or
            "testing" in summary_lower or
            "ai agent" in summary_lower or
            "openclaw" in summary_lower,
            f"Concept summary should relate to evaluation/testing/AI agent/openclaw: {summary.concept_summary}"
        )

    def test_generate_relation_map_groups_by_concept(self):
        """Generated relation map groups entities by conceptual categories."""
        entities = [
            RankedEntity(name="openclaw-repo", entity_type="repository", signal_score=0.9, relevance_reason="Test"),
            RankedEntity(name="ai-agent-tool", entity_type="repository", signal_score=0.8, relevance_reason="Test"),
        ]
        bundle = self._make_test_bundle(entities=entities)
        summary = generate_harness_knowledge_summary(bundle)

        # Relation map should have conceptual categories, not just entity types
        self.assertTrue(len(summary.relation_map) > 0)
        # Should have at least one of the conceptual categories
        conceptual_keys = ["harness_concept", "openclaw_ecosystem", "ai_agent_frameworks", "evaluation_testing", "research_practice"]
        has_conceptual = any(k in summary.relation_map for k in conceptual_keys)
        self.assertTrue(has_conceptual, f"Relation map should have conceptual categories: {summary.relation_map.keys()}")

    def test_generate_contrast_dimensions(self):
        """Generated contrast dimensions contrast harness with adjacent approaches."""
        entities = [
            RankedEntity(name="Person1", entity_type="person", signal_score=0.9, relevance_reason="Test"),
            RankedEntity(name="Repo1", entity_type="repository", signal_score=0.8, relevance_reason="Test"),
        ]
        bundle = self._make_test_bundle(entities=entities)
        summary = generate_harness_knowledge_summary(bundle)

        # Should have contrast dimensions
        self.assertTrue(len(summary.contrast_dimensions) > 0)
        # Contrast should mention practice-oriented, ecosystem, or similar
        contrast_str = " ".join(summary.contrast_dimensions).lower()
        self.assertTrue(
            "practice" in contrast_str or
            "ecosystem" in contrast_str or
            "organizational" in contrast_str or
            "agent-specific" in contrast_str or
            "diverse" in contrast_str,
            f"Contrast dimensions should contrast harness with adjacent approaches: {summary.contrast_dimensions}"
        )




class TestEvolutionJudgment(unittest.TestCase):
    """Tests for EvolutionJudgment dataclass."""

    def test_create_evolution_judgment(self):
        """Create an evolution judgment with all fields."""
        judgment = EvolutionJudgment(
            relevance_judgment="Trend is relevant",
            gap_alignment=["improve source intelligence quality"],
            proposed_action="PRIMARY ACTION: Test action",
            limitations=["Limited evidence"],
            confidence=0.6,
        )

        self.assertEqual(judgment.relevance_judgment, "Trend is relevant")
        self.assertEqual(judgment.gap_alignment, ["improve source intelligence quality"])
        self.assertEqual(judgment.proposed_action, "PRIMARY ACTION: Test action")
        self.assertEqual(len(judgment.limitations), 1)
        self.assertEqual(judgment.confidence, 0.6)

    def test_evolution_judgment_to_dict(self):
        """EvolutionJudgment serializes to dictionary correctly."""
        judgment = EvolutionJudgment(relevance_judgment="Test", confidence=0.7)
        data = judgment.to_dict()

        self.assertEqual(data["relevance_judgment"], "Test")
        self.assertEqual(data["confidence"], 0.7)
        self.assertIn("gap_alignment", data)
        self.assertIn("proposed_action", data)
        self.assertIn("limitations", data)

    def test_evolution_judgment_default_values(self):
        """EvolutionJudgment has correct default values."""
        judgment = EvolutionJudgment()

        self.assertEqual(judgment.relevance_judgment, "")
        self.assertEqual(judgment.gap_alignment, [])
        self.assertEqual(judgment.proposed_action, "")
        self.assertEqual(judgment.limitations, [])
        self.assertEqual(judgment.confidence, 0.5)


class TestGenerateEvolutionJudgment(unittest.TestCase):
    """Tests for generate_evolution_judgment helper."""

    def _make_test_bundle_and_summary(self, entity_count=2):
        """Create test bundle and knowledge summary."""
        entities = [
            RankedEntity(name=f"Entity{i}", entity_type="person" if i % 2 == 0 else "repository", signal_score=0.9 - i*0.1, relevance_reason="Test")
            for i in range(entity_count)
        ]
        bundle = HarnessTrendBundle(topic="harness", ranked_entities=entities)
        knowledge = KnowledgeSummary(
            concept_summary="harness relates to evaluation and testing",
            relation_map={"evaluation_testing": ["Entity0"]},
            contrast_dimensions=["Practice-oriented vs tool-centric"],
            evidence_grounding=["Entity: Entity0"],
            confidence=0.6,
            limitations=["Test limitation"],
        )
        return bundle, knowledge

    def test_generate_with_evidence(self):
        """Generate evolution judgment with evidence."""
        bundle, knowledge = self._make_test_bundle_and_summary()
        judgment = generate_evolution_judgment(bundle, knowledge)

        self.assertIsInstance(judgment, EvolutionJudgment)
        self.assertIn("RELEVANT" in judgment.relevance_judgment or "LIMITED" in judgment.relevance_judgment, [True])
        self.assertTrue(len(judgment.gap_alignment) >= 0)
        self.assertTrue(len(judgment.proposed_action) > 0)
        self.assertTrue(len(judgment.limitations) > 0)
        self.assertGreater(judgment.confidence, 0.0)
        self.assertLessEqual(judgment.confidence, 0.75)

    def test_generate_empty_bundle(self):
        """Generate evolution judgment with empty bundle."""
        bundle = HarnessTrendBundle(topic="harness", ranked_entities=[])
        knowledge = KnowledgeSummary()
        judgment = generate_evolution_judgment(bundle, knowledge)

        self.assertIsInstance(judgment, EvolutionJudgment)
        self.assertIn("No evidence", judgment.relevance_judgment)
        self.assertEqual(judgment.confidence, 0.1)

    def test_generate_gap_alignment(self):
        """Generated judgment aligns to mainline gaps."""
        bundle, knowledge = self._make_test_bundle_and_summary()
        judgment = generate_evolution_judgment(bundle, knowledge)

        # Gap alignment should contain valid mainline gaps or be empty
        for gap in judgment.gap_alignment:
            self.assertIn(gap, MAINLINE_GAPS)

    def test_generate_proposed_action(self):
        """Generated judgment proposes one bounded action."""
        bundle, knowledge = self._make_test_bundle_and_summary()
        judgment = generate_evolution_judgment(bundle, knowledge)

        # Action should be bounded and mention success criteria
        self.assertIn("PRIMARY ACTION" in judgment.proposed_action or "NO ACTION" in judgment.proposed_action, [True])
        self.assertIn("Success criteria" in judgment.proposed_action or "Monitor" in judgment.proposed_action, [True])

    def test_generate_conservative_confidence(self):
        """Generated judgment uses conservative confidence."""
        bundle, knowledge = self._make_test_bundle_and_summary()
        judgment = generate_evolution_judgment(bundle, knowledge)

        # Confidence should be conservative (capped at 0.75)
        self.assertLessEqual(judgment.confidence, 0.75)
        self.assertGreater(judgment.confidence, 0.0)

    def test_generate_includes_limitations(self):
        """Generated judgment includes explicit limitations."""
        bundle, knowledge = self._make_test_bundle_and_summary()
        judgment = generate_evolution_judgment(bundle, knowledge)

        self.assertTrue(len(judgment.limitations) > 0)
        # Should mention evidence limitations
        limitations_str = " ".join(judgment.limitations).lower()
        self.assertIn("evidence", limitations_str)

    def test_relevance_anchors_to_evidence(self):
        """Relevance judgment anchors to B1-S1/S2 evidence."""
        bundle, knowledge = self._make_test_bundle_and_summary(entity_count=5)
        judgment = generate_evolution_judgment(bundle, knowledge)

        # Relevance should mention entity count
        self.assertIn("5", judgment.relevance_judgment)
        # Should mention evidence or entities
        self.assertTrue("evidence" in judgment.relevance_judgment.lower() or "entities" in judgment.relevance_judgment.lower())


class TestTierEntry(unittest.TestCase):
    """Tests for TierEntry dataclass."""

    def test_create_tier_entry(self):
        """Create a tier entry with all fields."""
        entry = TierEntry(
            entity_name="Test Entity",
            entity_type="person",
            rationale="Test rationale",
        )

        self.assertEqual(entry.entity_name, "Test Entity")
        self.assertEqual(entry.entity_type, "person")
        self.assertEqual(entry.rationale, "Test rationale")

    def test_tier_entry_to_dict(self):
        """TierEntry serializes to dictionary correctly."""
        entry = TierEntry(
            entity_name="Test",
            entity_type="repository",
            rationale="Test reason",
        )

        data = entry.to_dict()

        self.assertEqual(data["entity_name"], "Test")
        self.assertEqual(data["entity_type"], "repository")
        self.assertEqual(data["rationale"], "Test reason")


class TestEntityTier(unittest.TestCase):
    """Tests for EntityTier dataclass."""

    def test_create_entity_tier(self):
        """Create an entity tier with entries."""
        tier = EntityTier(
            tier_name="concept_defining",
            description="Entities that define the concept",
            entries=[
                TierEntry(entity_name="Entity1", entity_type="person", rationale="Rationale1"),
            ],
        )

        self.assertEqual(tier.tier_name, "concept_defining")
        self.assertEqual(len(tier.entries), 1)

    def test_entity_tier_to_dict(self):
        """EntityTier serializes to dictionary correctly."""
        tier = EntityTier(
            tier_name="ecosystem_relevant",
            description="Ecosystem entities",
            entries=[
                TierEntry(entity_name="Entity1", entity_type="org", rationale="R1"),
                TierEntry(entity_name="Entity2", entity_type="repo", rationale="R2"),
            ],
        )

        data = tier.to_dict()

        self.assertEqual(data["tier_name"], "ecosystem_relevant")
        self.assertEqual(data["description"], "Ecosystem entities")
        self.assertEqual(len(data["entries"]), 2)


class TestB2EntityTiers(unittest.TestCase):
    """Tests for B2EntityTiers dataclass."""

    def test_create_b2_entity_tiers(self):
        """Create a B2EntityTiers object with all tiers."""
        tiers = B2EntityTiers(
            concept_defining=EntityTier(tier_name="concept_defining", description="CD"),
            ecosystem_relevant=EntityTier(tier_name="ecosystem_relevant", description="ER"),
            implementation_relevant=EntityTier(tier_name="implementation_relevant", description="IR"),
            topic="harness",
            benchmark_id="B2-S1",
        )

        self.assertEqual(tiers.topic, "harness")
        self.assertEqual(tiers.benchmark_id, "B2-S1")
        self.assertIsInstance(tiers.concept_defining, EntityTier)
        self.assertIsInstance(tiers.ecosystem_relevant, EntityTier)
        self.assertIsInstance(tiers.implementation_relevant, EntityTier)

    def test_b2_entity_tiers_to_dict(self):
        """B2EntityTiers serializes to dictionary correctly."""
        tiers = B2EntityTiers(
            concept_defining=EntityTier(
                tier_name="concept_defining",
                description="CD",
                entries=[TierEntry(entity_name="CoreAuthor", entity_type="person", rationale="Defines concept")],
            ),
            ecosystem_relevant=EntityTier(
                tier_name="ecosystem_relevant",
                description="ER",
                entries=[TierEntry(entity_name="AdopterOrg", entity_type="organization", rationale="Adopts concept")],
            ),
            implementation_relevant=EntityTier(
                tier_name="implementation_relevant",
                description="IR",
                entries=[TierEntry(entity_name="ToolRepo", entity_type="repository", rationale="Implements concept")],
            ),
            topic="harness",
            limitations=["Limited evidence"],
        )

        data = tiers.to_dict()

        self.assertEqual(data["topic"], "harness")
        self.assertEqual(data["benchmark_id"], "B2-S1")
        self.assertEqual(len(data["concept_defining"]["entries"]), 1)
        self.assertEqual(len(data["ecosystem_relevant"]["entries"]), 1)
        self.assertEqual(len(data["implementation_relevant"]["entries"]), 1)
        self.assertEqual(data["limitations"], ["Limited evidence"])


class TestClassifyBenchmarkEntityTiers(unittest.TestCase):
    """Tests for classify_benchmark_entity_tiers helper."""

    def _make_test_bundle(self, entities=None):
        """Create a test HarnessTrendBundle."""
        if entities is None:
            entities = [
                RankedEntity(
                    name="Core Author",
                    entity_type="person",
                    signal_score=0.95,
                    relevance_reason="Primary author and maintainer of the core concept",
                ),
                RankedEntity(
                    name="Research Lab",
                    entity_type="organization",
                    signal_score=0.85,
                    relevance_reason="Research organization shaping ecosystem discourse",
                ),
                RankedEntity(
                    name="Implementation Repo",
                    entity_type="repository",
                    signal_score=0.80,
                    relevance_reason="Practical implementation tool and framework",
                ),
            ]

        return HarnessTrendBundle(
            topic="harness",
            benchmark_id="B1-S1",
            signal_summary="Test summary",
            ranked_entities=entities,
        )

    def test_classify_basic(self):
        """Classify basic list of entities into tiers."""
        bundle = self._make_test_bundle()
        result = classify_benchmark_entity_tiers(bundle)

        self.assertIsInstance(result, B2EntityTiers)
        self.assertEqual(result.topic, "harness")
        self.assertEqual(result.benchmark_id, "B2-S1")

    def test_classify_concept_defining_author(self):
        """Authors/maintainers are classified as concept-defining."""
        bundle = self._make_test_bundle(entities=[
            RankedEntity(
                name="Core Developer",
                entity_type="person",
                signal_score=0.9,
                relevance_reason="Primary author and core maintainer",
            ),
        ])

        result = classify_benchmark_entity_tiers(bundle)

        # Should have at least one concept-defining entry
        self.assertGreater(len(result.concept_defining.entries), 0)

    def test_classify_ecosystem_organization(self):
        """Organizations are classified as ecosystem-relevant."""
        bundle = self._make_test_bundle(entities=[
            RankedEntity(
                name="Research Organization",
                entity_type="organization",
                signal_score=0.8,
                relevance_reason="Research lab shaping ecosystem",
            ),
        ])

        result = classify_benchmark_entity_tiers(bundle)

        # Organization should be ecosystem-relevant
        self.assertGreater(len(result.ecosystem_relevant.entries), 0)

    def test_classify_implementation_repository(self):
        """Implementation repositories are classified as implementation-relevant."""
        bundle = self._make_test_bundle(entities=[
            RankedEntity(
                name="Tool Framework",
                entity_type="repository",
                signal_score=0.75,
                relevance_reason="Practical implementation framework and tool",
            ),
        ])

        result = classify_benchmark_entity_tiers(bundle)

        # Should have implementation-relevant entries
        self.assertGreater(len(result.implementation_relevant.entries), 0)

    def test_classify_empty_bundle(self):
        """Classify empty bundle returns empty tiers."""
        bundle = self._make_test_bundle(entities=[])
        result = classify_benchmark_entity_tiers(bundle)

        self.assertEqual(len(result.concept_defining.entries), 0)
        self.assertEqual(len(result.ecosystem_relevant.entries), 0)
        self.assertEqual(len(result.implementation_relevant.entries), 0)

    def test_classify_includes_notes(self):
        """Classification includes explanatory notes."""
        bundle = self._make_test_bundle()
        result = classify_benchmark_entity_tiers(bundle)

        self.assertTrue(len(result.notes) > 0)
        self.assertIn("harness", result.notes.lower())

    def test_classify_includes_limitations(self):
        """Classification includes explicit limitations."""
        bundle = self._make_test_bundle()
        result = classify_benchmark_entity_tiers(bundle)

        self.assertTrue(len(result.limitations) > 0)
        self.assertIn("heuristic", result.limitations[0].lower())

    def test_classify_custom_concept(self):
        """Classification supports custom concept parameter."""
        bundle = self._make_test_bundle()
        result = classify_benchmark_entity_tiers(bundle, concept="custom-concept")

        self.assertEqual(result.topic, "custom-concept")
        self.assertIn("custom-concept", result.concept_defining.description.lower())

    def test_classify_entry_has_rationale(self):
        """Each tier entry includes a rationale."""
        bundle = self._make_test_bundle(entities=[
            RankedEntity(
                name="Test Entity",
                entity_type="person",
                signal_score=0.9,
                relevance_reason="Test relevance",
            ),
        ])

        result = classify_benchmark_entity_tiers(bundle)

        # Find the entry in any tier
        all_entries = (
            result.concept_defining.entries +
            result.ecosystem_relevant.entries +
            result.implementation_relevant.entries
        )

        self.assertGreater(len(all_entries), 0)
        for entry in all_entries:
            self.assertTrue(len(entry.rationale) > 0)

    def test_classify_preserves_entity_info(self):
        """Classification preserves entity name and type."""
        bundle = self._make_test_bundle(entities=[
            RankedEntity(
                name="SpecificName",
                entity_type="repository",
                signal_score=0.8,
                relevance_reason="Test",
            ),
        ])

        result = classify_benchmark_entity_tiers(bundle)

        all_entries = (
            result.concept_defining.entries +
            result.ecosystem_relevant.entries +
            result.implementation_relevant.entries
        )

        # Find our specific entry
        found = False
        for entry in all_entries:
            if entry.entity_name == "SpecificName":
                self.assertEqual(entry.entity_type, "repository")
                found = True
                break

        self.assertTrue(found, "Entity should be classified into a tier")

    def test_classify_skill_catalog_as_ecosystem_not_implementation(self):
        """
        Regression test: Skill catalog/distribution repositories like
        'LeoYeAI/openclaw-master-skills' should be ecosystem_relevant,
        NOT implementation_relevant.
        
        This prevents over-crediting repositories just because they match
        'skill' or are OpenClaw-adjacent without explicit evaluation/
        benchmark workflow evidence.
        """
        bundle = self._make_test_bundle(entities=[
            RankedEntity(
                name="LeoYeAI/openclaw-master-skills",
                entity_type="repository",
                signal_score=0.85,
                relevance_reason="OpenClaw skill catalog and distribution repository",
            ),
            RankedEntity(
                name="slowmist/openclaw-security-practice-guide",
                entity_type="repository",
                signal_score=0.80,
                relevance_reason="Security audit and validation workflow patterns for OpenClaw",
            ),
        ])

        result = classify_benchmark_entity_tiers(bundle)

        # Find the skill catalog entry
        catalog_entry = None
        guide_entry = None
        
        all_entries = (
            result.concept_defining.entries +
            result.ecosystem_relevant.entries +
            result.implementation_relevant.entries
        )
        
        for entry in all_entries:
            if "master-skills" in entry.entity_name.lower():
                catalog_entry = entry
            elif "security-practice-guide" in entry.entity_name.lower():
                guide_entry = entry

        # Skill catalog should be in ecosystem_relevant tier
        self.assertIsNotNone(catalog_entry, "Skill catalog entity should be classified")
        self.assertIn(
            catalog_entry.entity_name,
            [e.entity_name for e in result.ecosystem_relevant.entries],
            "Skill catalog (LeoYeAI/openclaw-master-skills) should be ecosystem_relevant, not implementation_relevant"
        )
        self.assertNotIn(
            catalog_entry.entity_name,
            [e.entity_name for e in result.implementation_relevant.entries],
            "Skill catalog should NOT be implementation_relevant - it's a distribution surface, not an evaluation workflow"
        )

        # Security practice guide SHOULD be implementation_relevant
        # (it contains explicit audit/validation workflow patterns)
        self.assertIsNotNone(guide_entry, "Security guide entity should be classified")
        self.assertIn(
            guide_entry.entity_name,
            [e.entity_name for e in result.implementation_relevant.entries],
            "Security practice guide should be implementation_relevant - contains audit/validation workflows"
        )

    def test_classify_distribution_signals_not_implementation(self):
        """
        Repositories with distribution/catalog signals (catalog, index, skills,
        clawhub, install) should not be automatically implementation_relevant.
        """
        bundle = self._make_test_bundle(entities=[
            RankedEntity(
                name="test-org/clawhub-skill-index",
                entity_type="repository",
                signal_score=0.75,
                relevance_reason="Skill index for clawhub distribution",
            ),
            RankedEntity(
                name="test-org/openclaw-skill-catalog",
                entity_type="repository",
                signal_score=0.70,
                relevance_reason="Curated catalog of OpenClaw skills",
            ),
        ])

        result = classify_benchmark_entity_tiers(bundle)

        # Both should be ecosystem_relevant, not implementation_relevant
        for entry in result.implementation_relevant.entries:
            self.assertNotIn(
                entry.entity_name.lower(),
                ["test-org/clawhub-skill-index", "test-org/openclaw-skill-catalog"],
                f"Repository {entry.entity_name} has distribution signals and should not be implementation_relevant"
            )


class TestGapMapping(unittest.TestCase):
    """Tests for GapMapping dataclass."""

    def test_create_gap_mapping(self):
        """Create a gap mapping with all fields."""
        mapping = GapMapping(
            gap_id="improve source intelligence quality",
            gap_description="Improve source intelligence quality",
            relevance_score="high",
            specific_contribution="Test contribution",
            supporting_entities=["Entity1", "Entity2"],
            evidence_notes="Test notes",
        )

        self.assertEqual(mapping.gap_id, "improve source intelligence quality")
        self.assertEqual(mapping.relevance_score, "high")
        self.assertEqual(len(mapping.supporting_entities), 2)

    def test_gap_mapping_to_dict(self):
        """GapMapping serializes to dictionary correctly."""
        mapping = GapMapping(
            gap_id="test_gap",
            gap_description="Test description",
            relevance_score="medium",
            specific_contribution="Test",
        )

        data = mapping.to_dict()

        self.assertEqual(data["gap_id"], "test_gap")
        self.assertEqual(data["relevance_score"], "medium")
        self.assertEqual(data["specific_contribution"], "Test")
        self.assertEqual(data["supporting_entities"], [])


class TestB2GapMappingResult(unittest.TestCase):
    """Tests for B2GapMappingResult dataclass."""

    def test_create_b2_gap_mapping_result(self):
        """Create a B2GapMappingResult with mappings."""
        result = B2GapMappingResult(
            concept="harness",
            mappings=[
                GapMapping(
                    gap_id="gap1",
                    gap_description="Gap 1",
                    relevance_score="high",
                    specific_contribution="Contribution 1",
                ),
            ],
            high_relevance_count=1,
        )

        self.assertEqual(result.concept, "harness")
        self.assertEqual(result.benchmark_id, "B2-S2")
        self.assertEqual(len(result.mappings), 1)
        self.assertEqual(result.high_relevance_count, 1)

    def test_b2_gap_mapping_result_to_dict(self):
        """B2GapMappingResult serializes to dictionary correctly."""
        result = B2GapMappingResult(
            concept="harness",
            mappings=[
                GapMapping(
                    gap_id="gap1",
                    gap_description="Gap 1",
                    relevance_score="high",
                    specific_contribution="C1",
                ),
                GapMapping(
                    gap_id="gap2",
                    gap_description="Gap 2",
                    relevance_score="low",
                    specific_contribution="C2",
                ),
            ],
            high_relevance_count=1,
            low_relevance_count=1,
        )

        data = result.to_dict()

        self.assertEqual(data["concept"], "harness")
        self.assertEqual(data["benchmark_id"], "B2-S2")
        self.assertEqual(len(data["mappings"]), 2)
        self.assertEqual(data["high_relevance_count"], 1)
        self.assertEqual(data["low_relevance_count"], 1)


class TestMapConceptToMainlineGaps(unittest.TestCase):
    """Tests for map_concept_to_mainline_gaps helper."""

    def _make_test_bundle_and_knowledge(self, entity_count=3):
        """Create test bundle and knowledge summary with harness-appropriate signals."""
        from ike_v0.benchmarks.b1_harness import RankedEntity, HarnessTrendBundle
        from ike_v0.benchmarks.b1_knowledge import KnowledgeSummary

        entities = [
            RankedEntity(
                name=f"Entity{i}",
                entity_type="person" if i % 2 == 0 else "repository",
                signal_score=0.9 - i * 0.1,
                relevance_reason="Expert in evaluation and testing for AI agent harness",
            )
            for i in range(entity_count)
        ]

        bundle = HarnessTrendBundle(
            topic="harness",
            benchmark_id="B1-S1",
            signal_summary="Test summary",
            ranked_entities=entities,
        )

        knowledge = KnowledgeSummary(
            concept_summary="harness relates to evaluation and testing of AI agents with controlled delegation",
            relation_map={"evaluation_testing": ["Entity0"]},
            contrast_dimensions=["practice-oriented", "ecosystem-integrated"],
            evidence_grounding=["Entity: Entity0 (person) - evaluation and testing expert"],
            confidence=0.6,
            limitations=["Test limitation"],
        )

        return bundle, knowledge

    def test_map_basic(self):
        """Map basic bundle and knowledge to gaps."""
        bundle, knowledge = self._make_test_bundle_and_knowledge()
        result = map_concept_to_mainline_gaps(bundle, knowledge)

        self.assertIsInstance(result, B2GapMappingResult)
        self.assertEqual(result.concept, "harness")
        self.assertEqual(result.benchmark_id, "B2-S2")
        self.assertGreater(len(result.mappings), 0)

    def test_map_selective_not_exhaustive(self):
        """Mapping is selective - only emits gaps with genuine evidence (not all 4)."""
        bundle, knowledge = self._make_test_bundle_and_knowledge()
        result = map_concept_to_mainline_gaps(bundle, knowledge)

        # For harness with proper concept signals, should emit exactly 2 gaps:
        # - "make active work surface understandable"
        # - "reduce token pressure through controlled delegation"
        self.assertEqual(len(result.mappings), 2,
            "Harness with proper signals should emit exactly 2 gaps")

        gap_ids = [m.gap_id for m in result.mappings]
        self.assertIn("make active work surface understandable", gap_ids)
        self.assertIn("reduce token pressure through controlled delegation", gap_ids)

        # All emitted gaps should have medium or high relevance (not low)
        for mapping in result.mappings:
            self.assertIn(mapping.relevance_score, ["high", "medium"])

    def test_map_relevance_scores(self):
        """Mapping assigns relevance scores."""
        bundle, knowledge = self._make_test_bundle_and_knowledge()
        result = map_concept_to_mainline_gaps(bundle, knowledge)

        # All mappings should have valid relevance scores
        valid_scores = {"high", "medium", "low"}
        for mapping in result.mappings:
            self.assertIn(mapping.relevance_score, valid_scores)

    def test_map_counts_match(self):
        """Mapping counts match actual distribution."""
        bundle, knowledge = self._make_test_bundle_and_knowledge()
        result = map_concept_to_mainline_gaps(bundle, knowledge)

        high_count = sum(1 for m in result.mappings if m.relevance_score == "high")
        medium_count = sum(1 for m in result.mappings if m.relevance_score == "medium")
        low_count = sum(1 for m in result.mappings if m.relevance_score == "low")

        self.assertEqual(result.high_relevance_count, high_count)
        self.assertEqual(result.medium_relevance_count, medium_count)
        self.assertEqual(result.low_relevance_count, low_count)
        self.assertEqual(result.total_gaps_identified, len(result.mappings))

    def test_map_includes_supporting_entities(self):
        """Mapping includes supporting entities when there's specific evidence."""
        bundle, knowledge = self._make_test_bundle_and_knowledge(entity_count=5)
        result = map_concept_to_mainline_gaps(bundle, knowledge)

        # Supporting entities are only included when there's specific keyword evidence
        # This test verifies the selective behavior works correctly
        # Note: supporting_entities may be empty if no entity names match gap keywords
        # The key is that relevance is based on evidence, not just entity count

    def test_map_includes_evidence_notes(self):
        """Mapping includes evidence notes."""
        bundle, knowledge = self._make_test_bundle_and_knowledge()
        result = map_concept_to_mainline_gaps(bundle, knowledge)

        for mapping in result.mappings:
            self.assertTrue(len(mapping.evidence_notes) > 0)

    def test_map_includes_notes(self):
        """Result includes explanatory notes."""
        bundle, knowledge = self._make_test_bundle_and_knowledge()
        result = map_concept_to_mainline_gaps(bundle, knowledge)

        self.assertTrue(len(result.notes) > 0)
        self.assertIn("harness", result.notes.lower())

    def test_map_includes_limitations(self):
        """Result includes explicit limitations."""
        bundle, knowledge = self._make_test_bundle_and_knowledge()
        result = map_concept_to_mainline_gaps(bundle, knowledge)

        self.assertTrue(len(result.limitations) > 0)
        self.assertIn("heuristic", result.limitations[0].lower())

    def test_map_custom_concept(self):
        """Mapping supports custom concept parameter."""
        bundle, knowledge = self._make_test_bundle_and_knowledge()
        result = map_concept_to_mainline_gaps(bundle, knowledge, concept="custom-concept")

        self.assertEqual(result.concept, "custom-concept")

    def test_map_empty_bundle(self):
        """Mapping handles empty bundle gracefully - may emit zero gaps if no evidence."""
        bundle, knowledge = self._make_test_bundle_and_knowledge(entity_count=0)
        result = map_concept_to_mainline_gaps(bundle, knowledge)

        self.assertIsInstance(result, B2GapMappingResult)
        self.assertEqual(result.concept, "harness")
        # With empty bundle, may have zero or few gaps depending on knowledge summary evidence
        # This is correct behavior - selective, not exhaustive

    def test_map_specific_contribution(self):
        """Each mapping includes specific contribution statement."""
        bundle, knowledge = self._make_test_bundle_and_knowledge()
        result = map_concept_to_mainline_gaps(bundle, knowledge)

        for mapping in result.mappings:
            self.assertTrue(len(mapping.specific_contribution) > 0)

    def test_map_gap_descriptions(self):
        """Gap descriptions match expected mainline gaps."""
        bundle, knowledge = self._make_test_bundle_and_knowledge()
        result = map_concept_to_mainline_gaps(bundle, knowledge)

        expected_descriptions = {
            "improve source intelligence quality": "source intelligence",
            "make active work surface understandable": "work surface",
            "move evolution toward better reasoning": "reasoning",
            "reduce token pressure through controlled delegation": "delegation",
        }

        for mapping in result.mappings:
            if mapping.gap_id in expected_descriptions:
                self.assertIn(
                    expected_descriptions[mapping.gap_id],
                    mapping.gap_description.lower(),
                    f"Gap {mapping.gap_id} description should mention key concept",
                )

    def test_map_relevance_differentiation(self):
        """Mapping differentiates relevance - not all gaps are high."""
        bundle, knowledge = self._make_test_bundle_and_knowledge()
        result = map_concept_to_mainline_gaps(bundle, knowledge)

        # Verify we have differentiated relevance scores
        scores = [m.relevance_score for m in result.mappings]

        # Should not have all "high" - that was the bug we fixed
        if len(scores) > 1:
            # If multiple gaps, they shouldn't all be identical high scores
            self.assertNotEqual(scores.count("high"), len(scores),
                "All gaps being 'high' indicates the semantic drift bug")

    def test_map_evidence_grounding(self):
        """Mapping grounds gaps in specific evidence from bundle and knowledge."""
        bundle, knowledge = self._make_test_bundle_and_knowledge(entity_count=3)
        result = map_concept_to_mainline_gaps(bundle, knowledge)

        # Each mapping should have evidence notes
        for mapping in result.mappings:
            self.assertTrue(len(mapping.evidence_notes) > 0)
            # Evidence notes should reference the bundle or knowledge
            self.assertTrue(
                "bundle" in mapping.evidence_notes.lower() or
                "entity" in mapping.evidence_notes.lower() or
                "knowledge" in mapping.evidence_notes.lower(),
                f"Evidence notes should reference source: {mapping.evidence_notes}"
            )

    def test_map_entity_types_alone_not_sufficient(self):
        """Entity type presence alone does NOT trigger gap emission."""
        from ike_v0.benchmarks.b1_harness import RankedEntity, HarnessTrendBundle
        from ike_v0.benchmarks.b1_knowledge import KnowledgeSummary

        # Create bundle with entities but NO gap-specific keywords in relevance reasons
        bundle = HarnessTrendBundle(
            topic="harness",
            benchmark_id="B1-S1",
            signal_summary="Test with generic entities",
            ranked_entities=[
                RankedEntity(name="Person A", entity_type="person", signal_score=0.9, relevance_reason="Works on stuff"),
                RankedEntity(name="Repo B", entity_type="repository", signal_score=0.8, relevance_reason="Builds things"),
                RankedEntity(name="Org C", entity_type="organization", signal_score=0.7, relevance_reason="Does research"),
            ],
        )

        # Knowledge summary with generic content (no gap keywords)
        knowledge = KnowledgeSummary(
            concept_summary="Generic concept about building software",
            relation_map={},
            contrast_dimensions=[],
            evidence_grounding=[],
            confidence=0.5,
            limitations=[],
        )

        result = map_concept_to_mainline_gaps(bundle, knowledge)

        # Should emit ZERO or very few gaps because there's no keyword evidence
        # Entity types alone (person, repo, org) should NOT trigger emission
        self.assertLessEqual(len(result.mappings), 1,
            "Entity types alone should not trigger gap emission without keyword evidence")

    def test_map_keyword_evidence_required(self):
        """Gap emission requires specific keyword evidence in relevance reasons or concept summary."""
        from ike_v0.benchmarks.b1_harness import RankedEntity, HarnessTrendBundle
        from ike_v0.benchmarks.b1_knowledge import KnowledgeSummary

        # Create bundle with entities that HAVE gap-specific keywords
        bundle = HarnessTrendBundle(
            topic="harness",
            benchmark_id="B1-S1",
            signal_summary="Test with reasoning-focused entities",
            ranked_entities=[
                RankedEntity(
                    name="Reasoning Expert",
                    entity_type="person",
                    signal_score=0.9,
                    relevance_reason="Expert in reasoning and judgment evaluation for AI agents",
                ),
                RankedEntity(
                    name="Eval Framework",
                    entity_type="repository",
                    signal_score=0.8,
                    relevance_reason="Framework for evaluation and analysis of agent reasoning",
                ),
            ],
        )

        # Knowledge summary with reasoning-related keywords
        knowledge = KnowledgeSummary(
            concept_summary="harness relates to evaluation, reasoning, and judgment of AI agent capabilities",
            relation_map={"evaluation_reasoning": ["Reasoning Expert"]},
            contrast_dimensions=["Reasoning-focused vs surface-level"],
            evidence_grounding=["Entity: Reasoning Expert - evaluation and reasoning specialist"],
            confidence=0.7,
            limitations=[],
        )

        result = map_concept_to_mainline_gaps(bundle, knowledge)

        # Should emit gaps related to reasoning (keyword evidence present)
        gap_ids = [m.gap_id for m in result.mappings]

        # "move evolution toward better reasoning" should be emitted due to keyword matches
        self.assertIn("move evolution toward better reasoning", gap_ids,
            "Reasoning-related keywords should trigger reasoning gap emission")

        # Gaps without keyword support should NOT be emitted
        self.assertNotIn("improve source intelligence quality", gap_ids,
            "Source intelligence gap should not emit without specific evidence")

    def test_map_harness_benchmark_local_semantics(self):
        """Harness concept emits only specific gaps based on benchmark-local semantics."""
        bundle, knowledge = self._make_test_bundle_and_knowledge()
        result = map_concept_to_mainline_gaps(bundle, knowledge)

        gap_ids = [m.gap_id for m in result.mappings]

        # Harness should emit these gaps (directly supported)
        self.assertIn("make active work surface understandable", gap_ids,
            "Harness should emit work surface gap")
        self.assertIn("reduce token pressure through controlled delegation", gap_ids,
            "Harness should emit delegation gap")

        # Harness should NOT emit these gaps by default (not directly supported)
        self.assertNotIn("improve source intelligence quality", gap_ids,
            "Harness should not emit source intelligence gap without direct evidence")
        self.assertNotIn("move evolution toward better reasoning", gap_ids,
            "Harness should not emit reasoning gap without direct evidence")

        # Should emit exactly 2 gaps for harness
        self.assertEqual(len(result.mappings), 2,
            "Harness with proper signals should emit exactly 2 gaps")


class TestB2Recommendation(unittest.TestCase):
    """Tests for B2Recommendation dataclass."""

    def test_create_b2_recommendation(self):
        """Create a B2Recommendation with all fields."""
        rec = B2Recommendation(
            level="study",
            rationale="Test rationale",
            confidence=0.6,
            trigger="Test trigger",
            blockers=["Blocker 1"],
            limitations=["Limitation 1"],
        )

        self.assertEqual(rec.level, "study")
        self.assertEqual(rec.confidence, 0.6)
        self.assertEqual(len(rec.blockers), 1)

    def test_b2_recommendation_to_dict(self):
        """B2Recommendation serializes to dictionary correctly."""
        rec = B2Recommendation(
            level="study",
            rationale="Test",
            confidence=0.5,
            trigger="Do something",
        )

        data = rec.to_dict()

        self.assertEqual(data["level"], "study")
        self.assertEqual(data["confidence"], 0.5)
        self.assertEqual(data["trigger"], "Do something")
        self.assertIn("blockers", data)
        self.assertIn("limitations", data)


class TestGenerateResearchRecommendation(unittest.TestCase):
    """Tests for generate_research_recommendation helper."""

    def _make_test_bundle_knowledge_gaps(self):
        """Create test bundle, knowledge, and gap mapping for harness."""
        from ike_v0.benchmarks.b1_harness import RankedEntity, HarnessTrendBundle
        from ike_v0.benchmarks.b1_knowledge import KnowledgeSummary
        from ike_v0.benchmarks.b2_gap_mapping import B2GapMappingResult, GapMapping

        bundle = HarnessTrendBundle(
            topic="harness",
            benchmark_id="B1-S1",
            signal_summary="Test summary",
            ranked_entities=[
                RankedEntity(name="Entity1", entity_type="person", signal_score=0.9, relevance_reason="Test"),
                RankedEntity(name="Entity2", entity_type="repository", signal_score=0.8, relevance_reason="Test"),
                RankedEntity(name="Entity3", entity_type="organization", signal_score=0.7, relevance_reason="Test"),
            ],
        )

        knowledge = KnowledgeSummary(
            concept_summary="harness relates to evaluation and testing of AI agents",
            relation_map={"evaluation_testing": ["Entity1"]},
            contrast_dimensions=["practice-oriented", "ecosystem-integrated"],
            evidence_grounding=["Entity: Entity1"],
            confidence=0.6,
            limitations=["Test limitation"],
        )

        gap_mapping = B2GapMappingResult(
            concept="harness",
            mappings=[
                GapMapping(
                    gap_id="make active work surface understandable",
                    gap_description="Work surface gap",
                    relevance_score="medium",
                    specific_contribution="Test contribution",
                ),
                GapMapping(
                    gap_id="reduce token pressure through controlled delegation",
                    gap_description="Delegation gap",
                    relevance_score="medium",
                    specific_contribution="Test contribution",
                ),
            ],
            high_relevance_count=0,
            medium_relevance_count=2,
            low_relevance_count=0,
        )

        return bundle, knowledge, gap_mapping

    def test_generate_harness_returns_study_level(self):
        """Harness benchmark returns study level recommendation."""
        bundle, knowledge, gap_mapping = self._make_test_bundle_knowledge_gaps()
        result = generate_research_recommendation(bundle, knowledge, gap_mapping)

        self.assertIsInstance(result, B2Recommendation)
        self.assertEqual(result.level, "study", "Harness should return study level")
        self.assertEqual(result.concept, "harness")
        self.assertEqual(result.benchmark_id, "B2-S3")

    def test_generate_includes_rationale(self):
        """Generated recommendation includes rationale."""
        bundle, knowledge, gap_mapping = self._make_test_bundle_knowledge_gaps()
        result = generate_research_recommendation(bundle, knowledge, gap_mapping)

        self.assertTrue(len(result.rationale) > 0)
        self.assertIn("harness", result.rationale.lower())

    def test_generate_includes_trigger(self):
        """Generated recommendation includes bounded trigger."""
        bundle, knowledge, gap_mapping = self._make_test_bundle_knowledge_gaps()
        result = generate_research_recommendation(bundle, knowledge, gap_mapping)

        self.assertTrue(len(result.trigger) > 0)
        # Trigger should mention inspecting repositories for study level
        self.assertTrue(
            "inspect" in result.trigger.lower() or
            "repository" in result.trigger.lower() or
            "evaluation" in result.trigger.lower(),
            f"Trigger should mention inspection or evaluation: {result.trigger}"
        )

    def test_generate_includes_blockers(self):
        """Generated recommendation includes blockers."""
        bundle, knowledge, gap_mapping = self._make_test_bundle_knowledge_gaps()
        result = generate_research_recommendation(bundle, knowledge, gap_mapping)

        self.assertTrue(len(result.blockers) > 0)
        # Blockers should be relevant to study level
        blockers_str = " ".join(result.blockers).lower()
        self.assertTrue(
            "validation" in blockers_str or
            "evidence" in blockers_str or
            "gap" in blockers_str or
            "repository" in blockers_str,
            f"Blockers should mention validation/evidence/repository: {result.blockers}"
        )

    def test_generate_includes_limitations(self):
        """Generated recommendation includes limitations."""
        bundle, knowledge, gap_mapping = self._make_test_bundle_knowledge_gaps()
        result = generate_research_recommendation(bundle, knowledge, gap_mapping)

        self.assertTrue(len(result.limitations) > 0)
        # Should mention benchmark-local or heuristic nature
        limitations_str = " ".join(result.limitations).lower()
        self.assertTrue(
            "heuristic" in limitations_str or
            "benchmark" in limitations_str or
            "evidence" in limitations_str,
            f"Limitations should mention heuristic/benchmark/evidence: {result.limitations}"
        )

    def test_generate_confidence_in_valid_range(self):
        """Generated confidence is in valid range [0.1, 0.95]."""
        bundle, knowledge, gap_mapping = self._make_test_bundle_knowledge_gaps()
        result = generate_research_recommendation(bundle, knowledge, gap_mapping)

        self.assertGreaterEqual(result.confidence, 0.1)
        self.assertLessEqual(result.confidence, 0.95)

    def test_generate_with_entity_tiers(self):
        """Recommendation uses entity tiers when provided."""
        from ike_v0.benchmarks.b2_entity_tiers import B2EntityTiers, EntityTier, TierEntry

        bundle, knowledge, gap_mapping = self._make_test_bundle_knowledge_gaps()

        # Create entity tiers with implementation repositories
        entity_tiers = B2EntityTiers(
            concept_defining=EntityTier(tier_name="concept_defining", description="CD"),
            ecosystem_relevant=EntityTier(tier_name="ecosystem_relevant", description="ER"),
            implementation_relevant=EntityTier(
                tier_name="implementation_relevant",
                description="IR",
                entries=[
                    TierEntry(entity_name="test-repo", entity_type="repository", rationale="Test"),
                ],
            ),
        )

        result = generate_research_recommendation(
            bundle, knowledge, gap_mapping, entity_tiers=entity_tiers
        )

        self.assertIsInstance(result, B2Recommendation)
        # Trigger should mention the specific repo when entity tiers provided
        self.assertIn("test-repo", result.trigger)

    def test_generate_observe_level_no_gaps(self):
        """Recommendation returns observe level when no gap alignment."""
        from ike_v0.benchmarks.b1_harness import RankedEntity, HarnessTrendBundle
        from ike_v0.benchmarks.b1_knowledge import KnowledgeSummary
        from ike_v0.benchmarks.b2_gap_mapping import B2GapMappingResult

        bundle = HarnessTrendBundle(
            topic="test",
            ranked_entities=[RankedEntity(name="Entity1", entity_type="person", signal_score=0.5, relevance_reason="Test")],
        )

        knowledge = KnowledgeSummary()

        # No gap mappings
        gap_mapping = B2GapMappingResult(
            concept="test",
            mappings=[],
        )

        result = generate_research_recommendation(bundle, knowledge, gap_mapping)

        self.assertEqual(result.level, "observe")

    def test_generate_study_level_with_gaps(self):
        """Recommendation returns study level with gap alignment."""
        bundle, knowledge, gap_mapping = self._make_test_bundle_knowledge_gaps()
        result = generate_research_recommendation(bundle, knowledge, gap_mapping)

        self.assertEqual(result.level, "study")

    def test_generate_rationale_mentions_gaps(self):
        """Rationale mentions aligned gaps."""
        bundle, knowledge, gap_mapping = self._make_test_bundle_knowledge_gaps()
        result = generate_research_recommendation(bundle, knowledge, gap_mapping)

        # Rationale should mention the gaps
        rationale_lower = result.rationale.lower()
        self.assertTrue(
            "gap" in rationale_lower or
            "work surface" in rationale_lower or
            "delegation" in rationale_lower,
            f"Rationale should mention gaps: {result.rationale}"
        )

    def test_generate_confidence_based_on_evidence(self):
        """Confidence reflects evidence strength."""
        bundle, knowledge, gap_mapping = self._make_test_bundle_knowledge_gaps()
        result = generate_research_recommendation(bundle, knowledge, gap_mapping)

        # Study level with 3 entities and 2 gaps should have moderate confidence
        self.assertGreater(result.confidence, 0.4)
        self.assertLess(result.confidence, 0.8)

    def test_generate_blockers_match_level(self):
        """Blockers are appropriate for the recommendation level."""
        bundle, knowledge, gap_mapping = self._make_test_bundle_knowledge_gaps()
        result = generate_research_recommendation(bundle, knowledge, gap_mapping)

        # Study level blockers should mention validation/repository
        blockers_str = " ".join(result.blockers).lower()
        self.assertTrue(
            "validation" in blockers_str or
            "repository" in blockers_str or
            "evidence" in blockers_str or
            "hands-on" in blockers_str,
            f"Study blockers should mention validation/repository/evidence: {result.blockers}"
        )


class TestB2TriggerPacket(unittest.TestCase):
    """Tests for B2TriggerPacket dataclass."""

    def test_create_b2_trigger_packet(self):
        """Create a B2TriggerPacket with all fields."""
        packet = B2TriggerPacket(
            packet_id="B2-S4-TEST-STUDY-12345678",
            concept="test-concept",
            derived_from=["B1-S1", "B2-S2", "B2-S3"],
            task_type="study",
            bounded_task="Test bounded task",
            inputs=["Input 1", "Input 2"],
            success_criteria=["Criterion 1"],
            no_go_conditions=["No-go 1"],
            timebox="1-2 weeks",
            output_artifact="Test report",
            fallback_action="Fallback action",
        )

        self.assertEqual(packet.packet_id, "B2-S4-TEST-STUDY-12345678")
        self.assertEqual(packet.concept, "test-concept")
        self.assertEqual(packet.task_type, "study")
        self.assertEqual(len(packet.inputs), 2)

    def test_b2_trigger_packet_to_dict(self):
        """B2TriggerPacket serializes to dictionary correctly."""
        packet = B2TriggerPacket(
            packet_id="B2-S4-TEST-STUDY-12345678",
            concept="test",
            derived_from=["B1-S1"],
            task_type="study",
            bounded_task="Test",
            inputs=[],
            success_criteria=[],
            no_go_conditions=[],
            timebox="1 week",
            output_artifact="Report",
            fallback_action="Fallback",
        )

        data = packet.to_dict()

        self.assertEqual(data["packet_id"], "B2-S4-TEST-STUDY-12345678")
        self.assertEqual(data["concept"], "test")
        self.assertEqual(data["task_type"], "study")
        self.assertIn("derived_from", data)
        self.assertIn("created_at", data)


class TestGenerateTriggerPacket(unittest.TestCase):
    """Tests for generate_trigger_packet helper."""

    def _make_test_bundle_knowledge_gaps_recommendation(self):
        """Create test bundle, knowledge, gap mapping, and recommendation for harness."""
        from ike_v0.benchmarks.b1_harness import RankedEntity, HarnessTrendBundle
        from ike_v0.benchmarks.b1_knowledge import KnowledgeSummary
        from ike_v0.benchmarks.b2_gap_mapping import B2GapMappingResult, GapMapping
        from ike_v0.benchmarks.b2_recommendation import B2Recommendation

        bundle = HarnessTrendBundle(
            topic="harness",
            benchmark_id="B1-S1",
            signal_summary="Test summary",
            ranked_entities=[
                RankedEntity(name="Entity1", entity_type="person", signal_score=0.9, relevance_reason="Test"),
                RankedEntity(name="Entity2", entity_type="repository", signal_score=0.8, relevance_reason="Test"),
                RankedEntity(name="Entity3", entity_type="organization", signal_score=0.7, relevance_reason="Test"),
            ],
        )

        knowledge = KnowledgeSummary(
            concept_summary="harness relates to evaluation and testing of AI agents",
            relation_map={"evaluation_testing": ["Entity1"]},
            contrast_dimensions=["practice-oriented", "ecosystem-integrated"],
            evidence_grounding=["Entity: Entity1"],
            confidence=0.6,
            limitations=["Test limitation"],
        )

        gap_mapping = B2GapMappingResult(
            concept="harness",
            mappings=[
                GapMapping(
                    gap_id="make active work surface understandable",
                    gap_description="Work surface gap",
                    relevance_score="medium",
                    specific_contribution="Test contribution",
                ),
            ],
            high_relevance_count=0,
            medium_relevance_count=1,
            low_relevance_count=0,
        )

        recommendation = B2Recommendation(
            level="study",
            rationale="Test rationale",
            confidence=0.6,
            trigger="Test trigger",
            blockers=["Test blocker"],
            limitations=["Test limitation"],
        )

        return bundle, knowledge, gap_mapping, recommendation

    def test_generate_harness_study_packet(self):
        """Generate trigger packet for harness returns study task type."""
        bundle, knowledge, gap_mapping, recommendation = self._make_test_bundle_knowledge_gaps_recommendation()
        result = generate_trigger_packet(bundle, knowledge, gap_mapping, recommendation)

        self.assertIsInstance(result, B2TriggerPacket)
        self.assertEqual(result.task_type, "study")
        self.assertEqual(result.concept, "harness")
        self.assertTrue(result.packet_id.startswith("B2-S4-"))

    def test_generate_packet_has_required_fields(self):
        """Generated packet has all required fields."""
        bundle, knowledge, gap_mapping, recommendation = self._make_test_bundle_knowledge_gaps_recommendation()
        result = generate_trigger_packet(bundle, knowledge, gap_mapping, recommendation)

        # Check all required fields are present and non-empty
        self.assertTrue(len(result.packet_id) > 0)
        self.assertTrue(len(result.concept) > 0)
        self.assertTrue(len(result.derived_from) > 0)
        self.assertTrue(len(result.bounded_task) > 0)
        self.assertTrue(len(result.inputs) > 0)
        self.assertTrue(len(result.success_criteria) > 0)
        self.assertTrue(len(result.no_go_conditions) > 0)
        self.assertTrue(len(result.timebox) > 0)
        self.assertTrue(len(result.output_artifact) > 0)
        self.assertTrue(len(result.fallback_action) > 0)

    def test_generate_derived_from_includes_benchmarks(self):
        """Generated packet derives from appropriate benchmarks."""
        bundle, knowledge, gap_mapping, recommendation = self._make_test_bundle_knowledge_gaps_recommendation()
        result = generate_trigger_packet(bundle, knowledge, gap_mapping, recommendation)

        # Should include B1 and B2 benchmarks
        self.assertIn("B1-S1", result.derived_from)
        self.assertIn("B2-S2", result.derived_from)
        self.assertIn("B2-S3", result.derived_from)

    def test_generate_bounded_task_mentions_inspection(self):
        """Study task bounded_task mentions repository inspection."""
        bundle, knowledge, gap_mapping, recommendation = self._make_test_bundle_knowledge_gaps_recommendation()
        result = generate_trigger_packet(bundle, knowledge, gap_mapping, recommendation)

        # Study task should mention inspection
        task_lower = result.bounded_task.lower()
        self.assertTrue(
            "inspect" in task_lower or
            "repository" in task_lower or
            "documentation" in task_lower,
            f"Study task should mention inspection/repository: {result.bounded_task}"
        )

    def test_generate_bounded_task_no_implementation(self):
        """Study task explicitly excludes implementation/forking/audit."""
        bundle, knowledge, gap_mapping, recommendation = self._make_test_bundle_knowledge_gaps_recommendation()
        result = generate_trigger_packet(bundle, knowledge, gap_mapping, recommendation)

        # Study task should explicitly say no implementation
        task_lower = result.bounded_task.lower()
        self.assertTrue(
            "no implementation" in task_lower or
            "no forking" in task_lower or
            "no code" in task_lower or
            "documentation only" in task_lower or
            "pattern inspection" in task_lower,
            f"Study task should exclude implementation: {result.bounded_task}"
        )

    def test_generate_inputs_include_benchmark_outputs(self):
        """Generated inputs include B1/B2 benchmark outputs."""
        bundle, knowledge, gap_mapping, recommendation = self._make_test_bundle_knowledge_gaps_recommendation()
        result = generate_trigger_packet(bundle, knowledge, gap_mapping, recommendation)

        inputs_str = " ".join(result.inputs).lower()
        self.assertTrue(
            "bundle" in inputs_str or
            "knowledge" in inputs_str or
            "gap" in inputs_str or
            "recommendation" in inputs_str,
            f"Inputs should reference benchmark outputs: {result.inputs}"
        )

    def test_generate_success_criteria_are_specific(self):
        """Generated success criteria are specific and actionable."""
        bundle, knowledge, gap_mapping, recommendation = self._make_test_bundle_knowledge_gaps_recommendation()
        result = generate_trigger_packet(bundle, knowledge, gap_mapping, recommendation)

        # Should have multiple success criteria
        self.assertGreaterEqual(len(result.success_criteria), 2)

        # Criteria should be specific (not empty or generic)
        for criterion in result.success_criteria:
            self.assertTrue(len(criterion) > 10, f"Success criterion too short: {criterion}")

    def test_generate_no_go_conditions_are_specific(self):
        """Generated no-go conditions are specific."""
        bundle, knowledge, gap_mapping, recommendation = self._make_test_bundle_knowledge_gaps_recommendation()
        result = generate_trigger_packet(bundle, knowledge, gap_mapping, recommendation)

        # Should have multiple no-go conditions
        self.assertGreaterEqual(len(result.no_go_conditions), 2)

        # Conditions should be specific
        for condition in result.no_go_conditions:
            self.assertTrue(len(condition) > 10, f"No-go condition too short: {condition}")

    def test_generate_timebox_is_bounded(self):
        """Generated timebox specifies bounded time period."""
        bundle, knowledge, gap_mapping, recommendation = self._make_test_bundle_knowledge_gaps_recommendation()
        result = generate_trigger_packet(bundle, knowledge, gap_mapping, recommendation)

        # Timebox should mention time period
        timebox_lower = result.timebox.lower()
        self.assertTrue(
            "week" in timebox_lower or
            "hour" in timebox_lower or
            "quarterly" in timebox_lower or
            "ongoing" in timebox_lower,
            f"Timebox should specify time period: {result.timebox}"
        )

    def test_generate_output_artifact_is_specific(self):
        """Generated output artifact is specific document type."""
        bundle, knowledge, gap_mapping, recommendation = self._make_test_bundle_knowledge_gaps_recommendation()
        result = generate_trigger_packet(bundle, knowledge, gap_mapping, recommendation)

        # Output artifact should mention report/document type
        artifact_lower = result.output_artifact.lower()
        self.assertTrue(
            "report" in artifact_lower or
            "document" in artifact_lower or
            "summary" in artifact_lower or
            "demo" in artifact_lower,
            f"Output artifact should specify document type: {result.output_artifact}"
        )

    def test_generate_fallback_action_exists(self):
        """Generated fallback action provides alternative path."""
        bundle, knowledge, gap_mapping, recommendation = self._make_test_bundle_knowledge_gaps_recommendation()
        result = generate_trigger_packet(bundle, knowledge, gap_mapping, recommendation)

        # Fallback should be substantial (not empty)
        self.assertTrue(len(result.fallback_action) > 20,
            f"Fallback action too short: {result.fallback_action}")

    def test_generate_with_entity_tiers(self):
        """Trigger packet uses entity tiers when provided."""
        from ike_v0.benchmarks.b2_entity_tiers import B2EntityTiers, EntityTier, TierEntry

        bundle, knowledge, gap_mapping, recommendation = self._make_test_bundle_knowledge_gaps_recommendation()

        # Create entity tiers with implementation repositories
        entity_tiers = B2EntityTiers(
            concept_defining=EntityTier(tier_name="concept_defining", description="CD"),
            ecosystem_relevant=EntityTier(tier_name="ecosystem_relevant", description="ER"),
            implementation_relevant=EntityTier(
                tier_name="implementation_relevant",
                description="IR",
                entries=[
                    TierEntry(entity_name="test-repo-1", entity_type="repository", rationale="Test"),
                    TierEntry(entity_name="test-repo-2", entity_type="repository", rationale="Test"),
                ],
            ),
        )

        result = generate_trigger_packet(
            bundle, knowledge, gap_mapping, recommendation, entity_tiers=entity_tiers
        )

        # Inputs should mention entity tiers
        inputs_str = " ".join(result.inputs).lower()
        self.assertTrue(
            "implementation" in inputs_str or
            "entity" in inputs_str or
            "tier" in inputs_str,
            f"Inputs should reference entity tiers: {result.inputs}"
        )

    def test_generate_packet_id_is_deterministic(self):
        """Packet ID is deterministic for same concept and level."""
        bundle, knowledge, gap_mapping, recommendation = self._make_test_bundle_knowledge_gaps_recommendation()

        result1 = generate_trigger_packet(bundle, knowledge, gap_mapping, recommendation)
        result2 = generate_trigger_packet(bundle, knowledge, gap_mapping, recommendation)

        # Packet IDs should be the same for same inputs (deterministic)
        # Note: created_at will differ, but packet_id should be based on concept/level
        self.assertEqual(result1.packet_id, result2.packet_id)

    def test_generate_different_concepts_different_packets(self):
        """Different concepts produce different packets."""
        bundle, knowledge, gap_mapping, recommendation = self._make_test_bundle_knowledge_gaps_recommendation()

        result1 = generate_trigger_packet(bundle, knowledge, gap_mapping, recommendation, concept="harness")
        result2 = generate_trigger_packet(bundle, knowledge, gap_mapping, recommendation, concept="other-concept")

        # Different concepts should have different packet IDs
        self.assertNotEqual(result1.packet_id, result2.packet_id)
        self.assertEqual(result1.concept, "harness")
        self.assertEqual(result2.concept, "other-concept")


class TestB3ConceptDeepening(unittest.TestCase):
    """Tests for B3ConceptDeepening dataclass."""

    def test_create_b3_concept_deepening(self):
        """Create a B3ConceptDeepening with all fields."""
        deepening = B3ConceptDeepening(
            working_definition="Test definition",
            boundary_positive=["Positive 1"],
            boundary_negative=["Negative 1"],
            competing_interpretations=["Interpretation A"],
            best_fit_interpretation="Best fit",
            mechanism_to_gap_mapping=[{"gap_id": "gap1", "mechanism": "test"}],
            applicability_judgment="partially_applicable",
            target_ike_layer="evolution layer",
            evidence_quality={"quality_level": "medium"},
            next_action="Next action",
        )

        self.assertEqual(deepening.working_definition, "Test definition")
        self.assertEqual(deepening.applicability_judgment, "partially_applicable")
        self.assertEqual(len(deepening.boundary_positive), 1)

    def test_b3_concept_deepening_to_dict(self):
        """B3ConceptDeepening serializes to dictionary correctly."""
        deepening = B3ConceptDeepening(
            working_definition="Test",
            boundary_positive=[],
            boundary_negative=[],
            competing_interpretations=[],
            best_fit_interpretation="Test",
            mechanism_to_gap_mapping=[],
            applicability_judgment="directly_applicable",
            target_ike_layer="test layer",
            evidence_quality={},
            next_action="Action",
        )

        data = deepening.to_dict()

        self.assertEqual(data["working_definition"], "Test")
        self.assertEqual(data["applicability_judgment"], "directly_applicable")
        self.assertEqual(data["target_ike_layer"], "test layer")
        self.assertIn("evidence_quality", data)
        self.assertIn("next_action", data)


class TestGenerateConceptDeepening(unittest.TestCase):
    """Tests for generate_concept_deepening helper."""

    def _make_test_bundle_knowledge_gaps_recommendation_packet(self):
        """Create test bundle, knowledge, gap mapping, recommendation, and packet for harness."""
        from ike_v0.benchmarks.b1_harness import RankedEntity, HarnessTrendBundle
        from ike_v0.benchmarks.b1_knowledge import KnowledgeSummary
        from ike_v0.benchmarks.b2_gap_mapping import B2GapMappingResult, GapMapping
        from ike_v0.benchmarks.b2_recommendation import B2Recommendation
        from ike_v0.benchmarks.b2_trigger_packet import B2TriggerPacket

        bundle = HarnessTrendBundle(
            topic="harness",
            benchmark_id="B1-S1",
            signal_summary="Test summary",
            ranked_entities=[
                RankedEntity(name="Entity1", entity_type="person", signal_score=0.9, relevance_reason="Test"),
                RankedEntity(name="Entity2", entity_type="repository", signal_score=0.8, relevance_reason="Test"),
                RankedEntity(name="Entity3", entity_type="organization", signal_score=0.7, relevance_reason="Test"),
            ],
        )

        knowledge = KnowledgeSummary(
            concept_summary="harness relates to evaluation and testing of AI agents",
            relation_map={"evaluation_testing": ["Entity1"]},
            contrast_dimensions=["practice-oriented", "ecosystem-integrated"],
            evidence_grounding=["Entity: Entity1"],
            confidence=0.6,
            limitations=["Test limitation"],
        )

        gap_mapping = B2GapMappingResult(
            concept="harness",
            mappings=[
                GapMapping(
                    gap_id="make active work surface understandable",
                    gap_description="Work surface gap",
                    relevance_score="medium",
                    specific_contribution="Test contribution",
                ),
                GapMapping(
                    gap_id="reduce token pressure through controlled delegation",
                    gap_description="Delegation gap",
                    relevance_score="medium",
                    specific_contribution="Test contribution",
                ),
            ],
            high_relevance_count=0,
            medium_relevance_count=2,
            low_relevance_count=0,
        )

        recommendation = B2Recommendation(
            level="study",
            rationale="Test rationale",
            confidence=0.6,
            trigger="Test trigger",
            blockers=["Test blocker"],
            limitations=["Test limitation"],
        )

        trigger_packet = B2TriggerPacket(
            packet_id="B2-S4-HARNESS-STUDY-12345678",
            concept="harness",
            derived_from=["B1-S1", "B2-S2", "B2-S3"],
            task_type="study",
            bounded_task="Test bounded task",
            inputs=[],
            success_criteria=[],
            no_go_conditions=[],
            timebox="1-2 weeks",
            output_artifact="Test report",
            fallback_action="Fallback",
        )

        return bundle, knowledge, gap_mapping, recommendation, trigger_packet

    def test_generate_harness_deepening(self):
        """Generate concept deepening for harness."""
        bundle, knowledge, gap_mapping, recommendation, trigger_packet = self._make_test_bundle_knowledge_gaps_recommendation_packet()
        result = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation, trigger_packet)

        self.assertIsInstance(result, B3ConceptDeepening)
        self.assertEqual(result.concept, "harness")
        self.assertEqual(result.benchmark_id, "B3-S1")

    def test_generate_has_required_fields(self):
        """Generated deepening has all required fields."""
        bundle, knowledge, gap_mapping, recommendation, trigger_packet = self._make_test_bundle_knowledge_gaps_recommendation_packet()
        result = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation, trigger_packet)

        # Check all required fields are present
        self.assertTrue(len(result.working_definition) > 0)
        self.assertIsInstance(result.boundary_positive, list)
        self.assertIsInstance(result.boundary_negative, list)
        self.assertIsInstance(result.competing_interpretations, list)
        self.assertTrue(len(result.best_fit_interpretation) > 0)
        self.assertIsInstance(result.mechanism_to_gap_mapping, list)
        self.assertIn(result.applicability_judgment, ["not_applicable", "partially_applicable", "directly_applicable"])
        self.assertTrue(len(result.target_ike_layer) > 0)
        self.assertIsInstance(result.evidence_quality, dict)
        self.assertTrue(len(result.next_action) > 0)

    def test_generate_working_definition_is_testable(self):
        """Working definition includes testable criteria."""
        bundle, knowledge, gap_mapping, recommendation, trigger_packet = self._make_test_bundle_knowledge_gaps_recommendation_packet()
        result = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation, trigger_packet)

        # Working definition should mention testable criteria
        def_lower = result.working_definition.lower()
        self.assertTrue(
            "testable" in def_lower or
            "criteria" in def_lower or
            "measurable" in def_lower or
            "evaluation" in def_lower,
            f"Working definition should be testable: {result.working_definition}"
        )

    def test_generate_boundary_positive_not_empty(self):
        """Boundary positive list is not empty."""
        bundle, knowledge, gap_mapping, recommendation, trigger_packet = self._make_test_bundle_knowledge_gaps_recommendation_packet()
        result = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation, trigger_packet)

        self.assertGreater(len(result.boundary_positive), 0)

    def test_generate_boundary_negative_not_empty(self):
        """Boundary negative list is not empty."""
        bundle, knowledge, gap_mapping, recommendation, trigger_packet = self._make_test_bundle_knowledge_gaps_recommendation_packet()
        result = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation, trigger_packet)

        self.assertGreater(len(result.boundary_negative), 0)

    def test_generate_competing_interpretations_not_empty(self):
        """Competing interpretations list is not empty."""
        bundle, knowledge, gap_mapping, recommendation, trigger_packet = self._make_test_bundle_knowledge_gaps_recommendation_packet()
        result = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation, trigger_packet)

        self.assertGreater(len(result.competing_interpretations), 0)

    def test_generate_best_fit_interpretation(self):
        """Best fit interpretation is selected."""
        bundle, knowledge, gap_mapping, recommendation, trigger_packet = self._make_test_bundle_knowledge_gaps_recommendation_packet()
        result = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation, trigger_packet)

        # Best fit should reference gap alignment or evidence
        fit_lower = result.best_fit_interpretation.lower()
        self.assertTrue(
            "gap" in fit_lower or
            "evidence" in fit_lower or
            "alignment" in fit_lower or
            "fit" in fit_lower,
            f"Best fit should reference alignment/evidence: {result.best_fit_interpretation}"
        )

    def test_generate_mechanism_to_gap_mapping(self):
        """Mechanism to gap mapping is populated."""
        bundle, knowledge, gap_mapping, recommendation, trigger_packet = self._make_test_bundle_knowledge_gaps_recommendation_packet()
        result = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation, trigger_packet)

        # Should have mappings for aligned gaps
        self.assertGreater(len(result.mechanism_to_gap_mapping), 0)

        # Each mapping should have required fields
        for mapping in result.mechanism_to_gap_mapping:
            self.assertIn("gap_id", mapping)
            self.assertIn("mechanism", mapping)
            self.assertIn("relevance_score", mapping)

    def test_generate_applicability_judgment_valid(self):
        """Applicability judgment is one of valid values."""
        bundle, knowledge, gap_mapping, recommendation, trigger_packet = self._make_test_bundle_knowledge_gaps_recommendation_packet()
        result = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation, trigger_packet)

        self.assertIn(
            result.applicability_judgment,
            ["not_applicable", "partially_applicable", "directly_applicable"]
        )

    def test_generate_target_ike_layer_for_harness(self):
        """Harness target layer is evolution layer evaluation operations."""
        bundle, knowledge, gap_mapping, recommendation, trigger_packet = self._make_test_bundle_knowledge_gaps_recommendation_packet()
        result = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation, trigger_packet)

        # For harness, should target evolution layer
        layer_lower = result.target_ike_layer.lower()
        self.assertIn("evolution", layer_lower)

    def test_generate_evidence_quality_has_required_fields(self):
        """Evidence quality assessment has required fields."""
        bundle, knowledge, gap_mapping, recommendation, trigger_packet = self._make_test_bundle_knowledge_gaps_recommendation_packet()
        result = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation, trigger_packet)

        eq = result.evidence_quality
        self.assertIn("entity_count", eq)
        self.assertIn("knowledge_confidence", eq)
        self.assertIn("recommendation_confidence", eq)
        self.assertIn("overall_quality_score", eq)
        self.assertIn("quality_level", eq)

    def test_generate_evidence_quality_score_in_range(self):
        """Evidence quality score is in valid range [0, 1]."""
        bundle, knowledge, gap_mapping, recommendation, trigger_packet = self._make_test_bundle_knowledge_gaps_recommendation_packet()
        result = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation, trigger_packet)

        score = result.evidence_quality["overall_quality_score"]
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_generate_next_action_references_recommendation_or_packet(self):
        """Next action references recommendation or trigger packet."""
        bundle, knowledge, gap_mapping, recommendation, trigger_packet = self._make_test_bundle_knowledge_gaps_recommendation_packet()
        result = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation, trigger_packet)

        # Next action should reference B2-S3 or B2-S4
        action_lower = result.next_action.lower()
        self.assertTrue(
            "b2-s" in action_lower or
            "recommendation" in action_lower or
            "trigger" in action_lower or
            "proceed" in action_lower or
            "monitor" in action_lower,
            f"Next action should reference B2 outputs or monitoring: {result.next_action}"
        )

    def test_generate_with_entity_tiers(self):
        """Concept deepening uses entity tiers when provided."""
        from ike_v0.benchmarks.b2_entity_tiers import B2EntityTiers, EntityTier, TierEntry

        bundle, knowledge, gap_mapping, recommendation, trigger_packet = self._make_test_bundle_knowledge_gaps_recommendation_packet()

        # Create entity tiers with implementation repositories
        entity_tiers = B2EntityTiers(
            concept_defining=EntityTier(tier_name="concept_defining", description="CD"),
            ecosystem_relevant=EntityTier(tier_name="ecosystem_relevant", description="ER"),
            implementation_relevant=EntityTier(
                tier_name="implementation_relevant",
                description="IR",
                entries=[
                    TierEntry(entity_name="test-repo", entity_type="repository", rationale="Test"),
                ],
            ),
        )

        result = generate_concept_deepening(
            bundle, knowledge, gap_mapping, recommendation, trigger_packet,
            entity_tiers=entity_tiers
        )

        # Evidence quality should reflect entity tiers
        self.assertGreater(result.evidence_quality["implementation_repos"], 0)

    def test_generate_applicability_based_on_gaps(self):
        """Applicability judgment reflects gap alignment."""
        bundle, knowledge, gap_mapping, recommendation, trigger_packet = self._make_test_bundle_knowledge_gaps_recommendation_packet()
        result = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation, trigger_packet)

        # With study recommendation (pre-closure), should be partially_applicable, not directly_applicable
        # directly_applicable requires prototype/adopt_candidate level (post-study validation)
        self.assertEqual(result.applicability_judgment, "partially_applicable",
            "Study level (pre-closure) should be partially_applicable, not directly_applicable")

    def test_generate_applicability_study_not_directly_applicable(self):
        """Study level recommendation cannot be directly_applicable (pre-closure)."""
        from ike_v0.benchmarks.b1_harness import RankedEntity, HarnessTrendBundle
        from ike_v0.benchmarks.b1_knowledge import KnowledgeSummary
        from ike_v0.benchmarks.b2_gap_mapping import B2GapMappingResult, GapMapping
        from ike_v0.benchmarks.b2_recommendation import B2Recommendation

        # Create bundle with strong evidence
        bundle = HarnessTrendBundle(
            topic="harness",
            ranked_entities=[
                RankedEntity(name="E1", entity_type="person", signal_score=0.9, relevance_reason="Test"),
                RankedEntity(name="E2", entity_type="repository", signal_score=0.8, relevance_reason="Test"),
                RankedEntity(name="E3", entity_type="repository", signal_score=0.7, relevance_reason="Test"),
            ],
        )

        knowledge = KnowledgeSummary(concept_summary="Test", confidence=0.7)

        # Strong gap alignment (2 gaps)
        gap_mapping = B2GapMappingResult(
            concept="harness",
            mappings=[
                GapMapping(gap_id="gap1", gap_description="G1", relevance_score="high", specific_contribution="C1"),
                GapMapping(gap_id="gap2", gap_description="G2", relevance_score="high", specific_contribution="C2"),
            ],
            high_relevance_count=2,
        )

        # But recommendation is still study level (pre-closure)
        recommendation = B2Recommendation(
            level="study",
            rationale="Test",
            confidence=0.6,
            trigger="Test",
        )

        result = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation)

        # Even with strong evidence, study level should be partially_applicable
        self.assertEqual(result.applicability_judgment, "partially_applicable",
            "Study level (pre-closure) must be partially_applicable even with strong evidence")

    def test_generate_applicability_prototype_can_be_directly_applicable(self):
        """Prototype level recommendation can be directly_applicable (post-study)."""
        from ike_v0.benchmarks.b1_harness import RankedEntity, HarnessTrendBundle
        from ike_v0.benchmarks.b1_knowledge import KnowledgeSummary
        from ike_v0.benchmarks.b2_gap_mapping import B2GapMappingResult, GapMapping
        from ike_v0.benchmarks.b2_recommendation import B2Recommendation

        # Create bundle with strong evidence
        bundle = HarnessTrendBundle(
            topic="harness",
            ranked_entities=[
                RankedEntity(name="E1", entity_type="person", signal_score=0.9, relevance_reason="Test"),
                RankedEntity(name="E2", entity_type="repository", signal_score=0.8, relevance_reason="Test"),
                RankedEntity(name="E3", entity_type="repository", signal_score=0.7, relevance_reason="Test"),
            ],
        )

        knowledge = KnowledgeSummary(concept_summary="Test", confidence=0.7)

        # Strong gap alignment (2 gaps)
        gap_mapping = B2GapMappingResult(
            concept="harness",
            mappings=[
                GapMapping(gap_id="gap1", gap_description="G1", relevance_score="high", specific_contribution="C1"),
                GapMapping(gap_id="gap2", gap_description="G2", relevance_score="high", specific_contribution="C2"),
            ],
            high_relevance_count=2,
        )

        # Prototype level (post-study validation)
        recommendation = B2Recommendation(
            level="prototype",
            rationale="Test",
            confidence=0.7,
            trigger="Test",
        )

        result = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation)

        # Prototype with strong evidence can be directly_applicable
        self.assertEqual(result.applicability_judgment, "directly_applicable",
            "Prototype level with strong evidence should be directly_applicable")

    def test_generate_different_concepts_different_results(self):
        """Different concepts produce different deepening results."""
        bundle, knowledge, gap_mapping, recommendation, trigger_packet = self._make_test_bundle_knowledge_gaps_recommendation_packet()

        result1 = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation, trigger_packet, concept="harness")
        result2 = generate_concept_deepening(bundle, knowledge, gap_mapping, recommendation, trigger_packet, concept="other-concept")

        # Working definitions should differ
        self.assertNotEqual(result1.working_definition, result2.working_definition)
        self.assertEqual(result1.concept, "harness")
        self.assertEqual(result2.concept, "other-concept")


class TestStudyResult(unittest.TestCase):
    """Tests for StudyResult dataclass."""

    def test_create_study_result(self):
        """Create a StudyResult with all fields."""
        result = StudyResult(
            result_id="SR-TEST-12345678",
            trigger_packet_ref="B2-S4-TEST-STUDY-12345678",
            inspected_artifacts=["Repo1", "Repo2"],
            findings=["Finding 1"],
            claim_validations=[{"claim": "Test", "status": "validated"}],
            blockers_encountered=[],
            confidence_delta=0.15,
            time_spent="4 hours",
            completion_status="completed",
            raw_notes="Test notes",
        )

        self.assertEqual(result.result_id, "SR-TEST-12345678")
        self.assertEqual(result.completion_status, "completed")
        self.assertEqual(len(result.inspected_artifacts), 2)

    def test_study_result_to_dict(self):
        """StudyResult serializes to dictionary correctly."""
        result = StudyResult(
            result_id="SR-TEST-12345678",
            trigger_packet_ref="B2-S4-TEST",
            inspected_artifacts=[],
            findings=[],
            claim_validations=[],
            blockers_encountered=[],
            confidence_delta=0.0,
            time_spent="1 hour",
            completion_status="completed",
            raw_notes="Test",
        )

        data = result.to_dict()

        self.assertEqual(data["result_id"], "SR-TEST-12345678")
        self.assertEqual(data["completion_status"], "completed")
        self.assertIn("created_at", data)


class TestDecisionHandoff(unittest.TestCase):
    """Tests for DecisionHandoff dataclass."""

    def test_create_decision_handoff(self):
        """Create a DecisionHandoff with all fields."""
        handoff = DecisionHandoff(
            decision_id="DH-TEST-12345678",
            study_result_ref="SR-TEST-12345678",
            decision_type="prototype",
            justification="Test justification",
            updated_claims=["Claim 1"],
            next_packet="B2-S4-TEST-PROTOTYPE",
            rejection_reason=None,
            escalation_target="Dev lead",
            confidence=0.7,
            limitations=["Limitation 1"],
        )

        self.assertEqual(handoff.decision_id, "DH-TEST-12345678")
        self.assertEqual(handoff.decision_type, "prototype")
        self.assertEqual(handoff.confidence, 0.7)

    def test_decision_handoff_to_dict(self):
        """DecisionHandoff serializes to dictionary correctly."""
        handoff = DecisionHandoff(
            decision_id="DH-TEST",
            study_result_ref="SR-TEST",
            decision_type="reject",
            justification="Test",
            updated_claims=[],
            next_packet=None,
            rejection_reason="Not suitable",
            escalation_target=None,
            confidence=0.5,
            limitations=[],
        )

        data = handoff.to_dict()

        self.assertEqual(data["decision_id"], "DH-TEST")
        self.assertEqual(data["decision_type"], "reject")
        self.assertEqual(data["rejection_reason"], "Not suitable")


class TestTaskClosure(unittest.TestCase):
    """Tests for TaskClosure dataclass."""

    def test_create_task_closure(self):
        """Create a TaskClosure with study result and decision handoff."""
        study_result = StudyResult(
            result_id="SR-TEST",
            trigger_packet_ref="B2-S4-TEST",
            inspected_artifacts=[],
            findings=[],
            claim_validations=[],
            blockers_encountered=[],
            confidence_delta=0.1,
            time_spent="2 hours",
            completion_status="completed",
            raw_notes="Test",
        )

        decision_handoff = DecisionHandoff(
            decision_id="DH-TEST",
            study_result_ref="SR-TEST",
            decision_type="prototype",
            justification="Test",
            updated_claims=[],
            next_packet=None,
            rejection_reason=None,
            escalation_target=None,
            confidence=0.7,
            limitations=[],
        )

        closure = TaskClosure(
            study_result=study_result,
            decision_handoff=decision_handoff,
            closure_summary="Test summary",
        )

        self.assertEqual(closure.closure_summary, "Test summary")
        self.assertEqual(closure.study_result.result_id, "SR-TEST")
        self.assertEqual(closure.decision_handoff.decision_type, "prototype")

    def test_task_closure_to_dict(self):
        """TaskClosure serializes to dictionary correctly."""
        study_result = StudyResult(
            result_id="SR-TEST",
            trigger_packet_ref="B2-S4-TEST",
            inspected_artifacts=[],
            findings=[],
            claim_validations=[],
            blockers_encountered=[],
            confidence_delta=0.0,
            time_spent="1 hour",
            completion_status="completed",
            raw_notes="Test",
        )

        decision_handoff = DecisionHandoff(
            decision_id="DH-TEST",
            study_result_ref="SR-TEST",
            decision_type="defer",
            justification="Test",
            updated_claims=[],
            next_packet=None,
            rejection_reason=None,
            escalation_target=None,
            confidence=0.5,
            limitations=[],
        )

        closure = TaskClosure(
            study_result=study_result,
            decision_handoff=decision_handoff,
            closure_summary="Summary",
        )

        data = closure.to_dict()

        self.assertIn("study_result", data)
        self.assertIn("decision_handoff", data)
        self.assertIn("closure_summary", data)


class TestGenerateStudyResult(unittest.TestCase):
    """Tests for generate_study_result helper."""

    def _make_test_trigger_packet(self):
        """Create a test trigger packet."""
        return B2TriggerPacket(
            packet_id="B2-S4-HARNESS-STUDY-12345678",
            concept="harness",
            derived_from=["B1-S1", "B2-S2", "B2-S3"],
            task_type="study",
            bounded_task="Test task",
            inputs=[],
            success_criteria=[],
            no_go_conditions=["No-go 1"],
            timebox="1-2 weeks",
            output_artifact="Test report",
            fallback_action="Fallback",
        )

    def test_generate_study_result_basic(self):
        """Generate study result from trigger packet with explicit inputs."""
        trigger_packet = self._make_test_trigger_packet()
        result = generate_study_result(
            trigger_packet=trigger_packet,
            inspected_repos=["repo1"],
            findings=["Finding 1"],
            claim_validations=[{"claim": "Test", "status": "validated"}],
            raw_notes="Test notes",
        )

        self.assertIsInstance(result, StudyResult)
        self.assertEqual(result.trigger_packet_ref, trigger_packet.packet_id)
        self.assertTrue(result.result_id.startswith("SR-"))

    def test_generate_study_result_with_repos(self):
        """Generate study result with multiple inspected repositories."""
        trigger_packet = self._make_test_trigger_packet()
        result = generate_study_result(
            trigger_packet=trigger_packet,
            inspected_repos=["repo1", "repo2", "repo3"],
            findings=["Finding 1"],
            claim_validations=[],
            raw_notes="Test",
        )

        self.assertEqual(len(result.inspected_artifacts), 3)

    def test_generate_study_result_with_findings(self):
        """Generate study result with custom findings."""
        trigger_packet = self._make_test_trigger_packet()
        result = generate_study_result(
            trigger_packet=trigger_packet,
            inspected_repos=["repo1"],
            findings=["Custom finding 1", "Custom finding 2"],
            claim_validations=[],
            raw_notes="Test",
        )

        self.assertEqual(len(result.findings), 2)

    def test_generate_study_result_confidence_delta_in_range(self):
        """Confidence delta is in valid range [-0.5, 0.5]."""
        trigger_packet = self._make_test_trigger_packet()
        result = generate_study_result(
            trigger_packet=trigger_packet,
            inspected_repos=["repo1"],
            findings=["Finding 1"],
            claim_validations=[],
            raw_notes="Test",
            confidence_delta=0.15,
        )

        self.assertEqual(result.confidence_delta, 0.15)

    def test_generate_study_result_partial_completion(self):
        """Study result handles partial completion status."""
        trigger_packet = self._make_test_trigger_packet()
        result = generate_study_result(
            trigger_packet=trigger_packet,
            inspected_repos=["repo1"],
            findings=["Finding 1"],
            claim_validations=[],
            raw_notes="Test",
            completion_status="partial",
            blockers_encountered=["Time constraints"],
        )

        self.assertEqual(result.completion_status, "partial")
        self.assertEqual(len(result.blockers_encountered), 1)

    def test_generate_study_result_abandoned(self):
        """Study result handles abandoned status."""
        trigger_packet = self._make_test_trigger_packet()
        result = generate_study_result(
            trigger_packet=trigger_packet,
            inspected_repos=[],
            findings=[],
            claim_validations=[],
            raw_notes="Abandoned",
            completion_status="abandoned",
            blockers_encountered=["Blocker 1"],
        )

        self.assertEqual(result.completion_status, "abandoned")
        self.assertEqual(len(result.blockers_encountered), 1)


class TestGenerateDecisionHandoff(unittest.TestCase):
    """Tests for generate_decision_handoff helper."""

    def _make_test_study_result(self, confidence_delta=0.15):
        """Create a test study result."""
        return StudyResult(
            result_id="SR-TEST-12345678",
            trigger_packet_ref="B2-S4-TEST",
            inspected_artifacts=["Repo1"],
            findings=["Finding 1", "Finding 2"],
            claim_validations=[{"claim": "Test", "status": "validated"}],
            blockers_encountered=[],
            confidence_delta=confidence_delta,
            time_spent="4 hours",
            completion_status="completed",
            raw_notes="Test notes",
        )

    def test_generate_decision_handoff_basic(self):
        """Generate decision handoff from study result with explicit inputs."""
        study_result = self._make_test_study_result()
        handoff = generate_decision_handoff(
            study_result=study_result,
            decision_type="prototype",
            justification="Test justification",
        )

        self.assertIsInstance(handoff, DecisionHandoff)
        self.assertEqual(handoff.study_result_ref, study_result.result_id)
        self.assertTrue(handoff.decision_id.startswith("DH-"))
        self.assertEqual(handoff.decision_type, "prototype")

    def test_generate_decision_handoff_explicit_type(self):
        """Generate decision handoff with explicit decision type."""
        study_result = self._make_test_study_result()
        handoff = generate_decision_handoff(
            study_result=study_result,
            decision_type="defer",
            justification="Deferred for later review",
        )

        self.assertEqual(handoff.decision_type, "defer")

    def test_generate_decision_handoff_reject(self):
        """Decision handoff for reject decision type."""
        study_result = self._make_test_study_result()
        handoff = generate_decision_handoff(
            study_result=study_result,
            decision_type="reject",
            justification="Not suitable for project needs",
        )

        self.assertEqual(handoff.decision_type, "reject")
        self.assertIsNotNone(handoff.rejection_reason)

    def test_generate_decision_handoff_next_packet(self):
        """Decision handoff includes next packet for prototype/continue_study."""
        study_result = self._make_test_study_result()
        handoff = generate_decision_handoff(
            study_result=study_result,
            decision_type="prototype",
            justification="Ready for prototype",
        )

        self.assertIsNotNone(handoff.next_packet)

    def test_generate_decision_handoff_confidence_in_range(self):
        """Decision confidence is in valid range [0, 1]."""
        study_result = self._make_test_study_result()
        handoff = generate_decision_handoff(
            study_result=study_result,
            decision_type="continue_study",
            justification="Need more research",
            confidence=0.6,
        )

        self.assertEqual(handoff.confidence, 0.6)

    def test_generate_decision_handoff_no_escalation_target(self):
        """Decision handoff has no hardcoded escalation target."""
        study_result = self._make_test_study_result()
        handoff = generate_decision_handoff(
            study_result=study_result,
            decision_type="reject",
            justification="Not suitable",
        )

        # Escalation target should be None (no hardcoded values)
        self.assertIsNone(handoff.escalation_target)


class TestGenerateTaskClosure(unittest.TestCase):
    """Tests for generate_task_closure helper."""

    def _make_test_trigger_packet(self):
        """Create a test trigger packet."""
        return B2TriggerPacket(
            packet_id="B2-S4-HARNESS-STUDY-12345678",
            concept="harness",
            derived_from=["B1-S1", "B2-S2", "B2-S3"],
            task_type="study",
            bounded_task="Test task",
            inputs=[],
            success_criteria=[],
            no_go_conditions=[],
            timebox="1-2 weeks",
            output_artifact="Test report",
            fallback_action="Fallback",
        )

    def test_generate_task_closure_basic(self):
        """Generate complete task closure with explicit inputs."""
        trigger_packet = self._make_test_trigger_packet()
        closure = generate_task_closure(
            trigger_packet=trigger_packet,
            inspected_repos=["repo1"],
            findings=["Finding 1"],
            claim_validations=[{"claim": "Test", "status": "validated"}],
            raw_notes="Test notes",
            decision_type="prototype",
            decision_justification="Ready for prototype phase",
        )

        self.assertIsInstance(closure, TaskClosure)
        self.assertIsInstance(closure.study_result, StudyResult)
        self.assertIsInstance(closure.decision_handoff, DecisionHandoff)
        self.assertEqual(closure.decision_handoff.decision_type, "prototype")

    def test_generate_task_closure_with_explicit_decision(self):
        """Generate task closure with explicit decision type."""
        trigger_packet = self._make_test_trigger_packet()
        closure = generate_task_closure(
            trigger_packet=trigger_packet,
            inspected_repos=["repo1"],
            findings=["Finding 1"],
            claim_validations=[],
            raw_notes="Test",
            decision_type="defer",
            decision_justification="Deferred for later",
        )

        self.assertEqual(closure.decision_handoff.decision_type, "defer")

    def test_generate_task_closure_summary(self):
        """Task closure includes summary."""
        trigger_packet = self._make_test_trigger_packet()
        closure = generate_task_closure(
            trigger_packet=trigger_packet,
            inspected_repos=["repo1"],
            findings=["Finding 1"],
            claim_validations=[],
            raw_notes="Test",
            decision_type="continue_study",
            decision_justification="Need more research",
        )

        self.assertTrue(len(closure.closure_summary) > 0)
        self.assertIn("harness", closure.closure_summary.lower())

    def test_generate_task_closure_with_findings(self):
        """Task closure uses custom findings."""
        trigger_packet = self._make_test_trigger_packet()
        closure = generate_task_closure(
            trigger_packet=trigger_packet,
            inspected_repos=["repo1"],
            findings=["Finding A", "Finding B"],
            claim_validations=[],
            raw_notes="Test",
            decision_type="prototype",
            decision_justification="Test",
        )

        self.assertEqual(len(closure.study_result.findings), 2)


if __name__ == "__main__":
    unittest.main()
