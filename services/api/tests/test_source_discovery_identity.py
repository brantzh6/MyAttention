import unittest

from routers.feeds import (
    SourceDiscoveryFocus,
    _build_related_candidate_seed,
    _candidate_identity,
    _candidate_relation_hints,
    _candidate_selection_threshold,
    _compress_generic_domain_candidates,
    _compress_release_repository_overlap,
    _domain_quality_adjustment,
    _focus_type_priority,
    _parent_related_item_type,
    _person_activity_freshness,
)


class SourceDiscoveryIdentityTests(unittest.TestCase):
    def test_identifies_github_release_as_release_object(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "https://github.com/openclaw/openclaw/releases/tag/v0.5.0",
            SourceDiscoveryFocus.FRONTIER,
        )
        self.assertEqual(item_type, "release")
        self.assertEqual(object_key, "github.com/openclaw/openclaw/release/v0.5.0")
        self.assertEqual(domain, "github.com")
        self.assertIn("release", display_name)
        self.assertIn("/releases/tag/v0.5.0", canonical_url)

    def test_identifies_event_pages_as_event_object(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "https://example.org/events/agent-summit-2026",
            SourceDiscoveryFocus.FRONTIER,
        )
        self.assertEqual(item_type, "event")
        self.assertEqual(object_key, "example.org:event")
        self.assertEqual(domain, "example.org")
        self.assertIn("events", display_name)
        self.assertIn("/events/agent-summit-2026", canonical_url)

    def test_identifies_reddit_thread_as_signal_object(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "https://reddit.com/r/MachineLearning/comments/abc123/openclaw_release_discussion/",
            SourceDiscoveryFocus.FRONTIER,
        )
        self.assertEqual(item_type, "signal")
        self.assertEqual(object_key, "reddit.com/thread/abc123")
        self.assertEqual(domain, "reddit.com")
        self.assertIn("thread", display_name)
        self.assertIn("/comments/abc123", canonical_url)

    def test_identifies_github_issue_as_signal_object(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "https://github.com/openclaw/openclaw/issues/123",
            SourceDiscoveryFocus.METHOD,
        )
        self.assertEqual(item_type, "signal")
        self.assertEqual(object_key, "github.com/openclaw/openclaw/issue/123")
        self.assertEqual(domain, "github.com")
        self.assertIn("issue 123", display_name)
        self.assertIn("/issues/123", canonical_url)

    def test_identifies_github_discussion_as_signal_object(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "https://github.com/openclaw/openclaw/discussions/456",
            SourceDiscoveryFocus.FRONTIER,
        )
        self.assertEqual(item_type, "signal")
        self.assertEqual(object_key, "github.com/openclaw/openclaw/discussion/456")
        self.assertEqual(domain, "github.com")

    def test_identifies_contextual_media_article_as_signal_in_latest_focus(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "https://36kr.com/p/3572628833139843",
            SourceDiscoveryFocus.LATEST,
        )
        self.assertEqual(item_type, "signal")
        self.assertEqual(object_key, "36kr.com/article/p-3572628833139843")
        self.assertEqual(domain, "36kr.com")
        self.assertIn("article", display_name)
        self.assertIn("/p/3572628833139843", canonical_url)

    def test_keeps_contextual_media_article_as_domain_in_method_focus(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "https://36kr.com/p/3572628833139843",
            SourceDiscoveryFocus.METHOD,
        )
        self.assertEqual(item_type, "domain")
        self.assertEqual(object_key, "36kr.com")
        self.assertEqual(domain, "36kr.com")

    def test_identifies_contextual_media_article_as_signal_in_frontier_focus(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "https://36kr.com/p/3572628833139843",
            SourceDiscoveryFocus.FRONTIER,
        )
        self.assertEqual(item_type, "signal")
        self.assertEqual(object_key, "36kr.com/article/p-3572628833139843")
        self.assertEqual(domain, "36kr.com")

    def test_keeps_contextual_media_tag_page_outside_article_rule(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "https://36kr.com/tag/agent",
            SourceDiscoveryFocus.LATEST,
        )
        self.assertEqual(item_type, "domain")
        self.assertEqual(object_key, "36kr.com")
        self.assertEqual(domain, "36kr.com")

    def test_normalizes_common_media_subdomains(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "https://m.36kr.com/p/3572628833139843",
            SourceDiscoveryFocus.METHOD,
        )
        self.assertEqual(item_type, "domain")
        self.assertEqual(domain, "36kr.com")
        self.assertEqual(object_key, "36kr.com")

    def test_person_activity_freshness_prefers_recent_speaker_signals(self) -> None:
        score = _person_activity_freshness(
            "person",
            "OpenClaw maintainer keynote at Agent Summit 2026",
            "Speaker discussed latest release roadmap and workshop results",
            SourceDiscoveryFocus.FRONTIER,
        )
        self.assertGreater(score, 0.08)

    def test_focus_type_priority_prefers_people_in_method_focus(self) -> None:
        person_priority = _focus_type_priority("person", SourceDiscoveryFocus.METHOD)
        domain_priority = _focus_type_priority("domain", SourceDiscoveryFocus.METHOD)
        self.assertGreater(person_priority, domain_priority)

    def test_contextual_media_role_varies_by_focus(self) -> None:
        self.assertLess(_domain_quality_adjustment("36kr.com", SourceDiscoveryFocus.METHOD), 0.0)
        self.assertLess(_domain_quality_adjustment("36kr.com", SourceDiscoveryFocus.FRONTIER), 0.0)
        self.assertGreater(_domain_quality_adjustment("36kr.com", SourceDiscoveryFocus.LATEST), 0.0)
        self.assertLess(_domain_quality_adjustment("m.36kr.com", SourceDiscoveryFocus.FRONTIER), 0.0)

    def test_candidate_threshold_lowers_for_person_and_release_objects(self) -> None:
        self.assertLess(
            _candidate_selection_threshold("person", SourceDiscoveryFocus.METHOD),
            _candidate_selection_threshold("domain", SourceDiscoveryFocus.METHOD),
        )
        self.assertLess(
            _candidate_selection_threshold("release", SourceDiscoveryFocus.FRONTIER),
            _candidate_selection_threshold("domain", SourceDiscoveryFocus.FRONTIER),
        )

    def test_related_repository_owner_can_seed_person_candidate(self) -> None:
        candidate = _build_related_candidate_seed(
            {
                "relation": "owner",
                "item_type": "person",
                "object_key": "github.com/user/openclaw",
                "label": "openclaw",
            },
            parent_object_key="github.com/openclaw/openclaw",
            parent_name="openclaw/openclaw",
            parent_score=0.82,
            parent_tier="A",
            focus=SourceDiscoveryFocus.METHOD,
        )
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate["item_type"], "person")
        self.assertEqual(candidate["url"], "https://github.com/openclaw")
        self.assertIn("maintainer", candidate["inferred_roles"])
        self.assertGreaterEqual(candidate["authority_score"], 0.45)

    def test_x_status_signal_emits_person_relation_hint(self) -> None:
        related = _candidate_relation_hints(
            "signal",
            "x.com/openclaw/status/123456",
            "https://x.com/openclaw/status/123456",
        )
        self.assertIn(
            {
                "relation": "author",
                "item_type": "person",
                "object_key": "x.com/openclaw",
                "label": "@openclaw",
            },
            related,
        )

    def test_author_relation_can_seed_builder_person_candidate(self) -> None:
        candidate = _build_related_candidate_seed(
            {
                "relation": "author",
                "item_type": "person",
                "object_key": "x.com/openclaw",
                "label": "@openclaw",
            },
            parent_object_key="x.com/openclaw/status/123456",
            parent_name="@openclaw status 123456",
            parent_score=0.76,
            parent_tier="A",
            focus=SourceDiscoveryFocus.METHOD,
        )
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate["item_type"], "person")
        self.assertEqual(candidate["url"], "https://x.com/openclaw")
        self.assertIn("builder", candidate["inferred_roles"])
        self.assertGreaterEqual(candidate["follow_score"], 0.07)

    def test_author_relation_does_not_escalate_builder_outside_method_or_frontier(self) -> None:
        candidate = _build_related_candidate_seed(
            {
                "relation": "author",
                "item_type": "person",
                "object_key": "x.com/openclaw",
                "label": "@openclaw",
            },
            parent_object_key="x.com/openclaw/status/123456",
            parent_name="@openclaw status 123456",
            parent_score=0.76,
            parent_tier="A",
            focus=SourceDiscoveryFocus.LATEST,
        )
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate["inferred_roles"], [])
        self.assertEqual(candidate["follow_score"], 0.04)

    def test_parent_related_item_type_identifies_signal_status(self) -> None:
        self.assertEqual(_parent_related_item_type("x.com/openclaw/status/123456"), "signal")
        self.assertEqual(_parent_related_item_type("reddit.com/thread/abc123"), "signal")

    def test_author_seed_records_signal_parent_type(self) -> None:
        candidate = _build_related_candidate_seed(
            {
                "relation": "author",
                "item_type": "person",
                "object_key": "x.com/openclaw",
                "label": "@openclaw",
            },
            parent_object_key="x.com/openclaw/status/123456",
            parent_name="@openclaw status 123456",
            parent_score=0.76,
            parent_tier="A",
            focus=SourceDiscoveryFocus.METHOD,
        )
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate["related_entities"][0]["item_type"], "signal")
        self.assertEqual(candidate["related_entities"][0]["object_key"], "x.com/openclaw/status/123456")

    def test_noise_compression_drops_generic_domain_when_specific_candidate_exists(self) -> None:
        compressed = _compress_generic_domain_candidates(
            [
                {
                    "item_type": "domain",
                    "object_key": "github.com",
                    "domain": "github.com",
                    "authority_score": 0.72,
                },
                {
                    "item_type": "repository",
                    "object_key": "github.com/openclaw/openclaw",
                    "domain": "github.com",
                    "authority_score": 0.74,
                },
            ],
            SourceDiscoveryFocus.METHOD,
        )
        self.assertEqual(len(compressed), 1)
        self.assertEqual(compressed[0]["item_type"], "repository")

    def test_noise_compression_keeps_generic_domain_without_specific_match(self) -> None:
        compressed = _compress_generic_domain_candidates(
            [
                {
                    "item_type": "domain",
                    "object_key": "github.com",
                    "domain": "github.com",
                    "authority_score": 0.72,
                },
                {
                    "item_type": "repository",
                    "object_key": "gitlab.com/openclaw/openclaw",
                    "domain": "gitlab.com",
                    "authority_score": 0.74,
                },
            ],
            SourceDiscoveryFocus.METHOD,
        )
        self.assertEqual(len(compressed), 2)
        self.assertEqual(compressed[0]["item_type"], "domain")

    def test_noise_compression_keeps_generic_domain_when_specific_is_not_competitive(self) -> None:
        compressed = _compress_generic_domain_candidates(
            [
                {
                    "item_type": "domain",
                    "object_key": "github.com",
                    "domain": "github.com",
                    "authority_score": 0.85,
                },
                {
                    "item_type": "repository",
                    "object_key": "github.com/openclaw/openclaw",
                    "domain": "github.com",
                    "authority_score": 0.60,
                },
            ],
            SourceDiscoveryFocus.METHOD,
        )
        self.assertEqual(len(compressed), 2)
        self.assertEqual(compressed[0]["item_type"], "domain")
        self.assertEqual(compressed[1]["item_type"], "repository")

    def test_release_overlap_compression_drops_repository_in_latest_focus(self) -> None:
        compressed = _compress_release_repository_overlap(
            [
                {
                    "item_type": "repository",
                    "object_key": "github.com/openclaw/openclaw",
                    "domain": "github.com",
                    "authority_score": 0.72,
                },
                {
                    "item_type": "release",
                    "object_key": "github.com/openclaw/openclaw/release/latest",
                    "domain": "github.com",
                    "authority_score": 0.74,
                },
            ],
            SourceDiscoveryFocus.LATEST,
        )
        self.assertEqual(len(compressed), 1)
        self.assertEqual(compressed[0]["item_type"], "release")

    def test_release_overlap_compression_keeps_repository_in_method_focus(self) -> None:
        compressed = _compress_release_repository_overlap(
            [
                {
                    "item_type": "repository",
                    "object_key": "github.com/openclaw/openclaw",
                    "domain": "github.com",
                    "authority_score": 0.72,
                },
                {
                    "item_type": "release",
                    "object_key": "github.com/openclaw/openclaw/release/latest",
                    "domain": "github.com",
                    "authority_score": 0.74,
                },
            ],
            SourceDiscoveryFocus.METHOD,
        )
        self.assertEqual(len(compressed), 2)

    def test_release_overlap_compression_keeps_repository_when_release_is_not_competitive(self) -> None:
        compressed = _compress_release_repository_overlap(
            [
                {
                    "item_type": "repository",
                    "object_key": "github.com/openclaw/openclaw",
                    "domain": "github.com",
                    "authority_score": 0.85,
                },
                {
                    "item_type": "release",
                    "object_key": "github.com/openclaw/openclaw/release/latest",
                    "domain": "github.com",
                    "authority_score": 0.60,
                },
            ],
            SourceDiscoveryFocus.LATEST,
        )
        self.assertEqual(len(compressed), 2)


if __name__ == "__main__":
    unittest.main()
