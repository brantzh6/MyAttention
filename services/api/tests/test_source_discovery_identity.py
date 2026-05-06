import unittest

from feeds.source_contracts import SourceDiscoveryCandidate
from feeds.source_postprocess import compress_source_candidates
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
    def _candidate(
        self,
        *,
        item_type: str,
        object_key: str,
        domain: str,
        authority_score: float,
    ) -> SourceDiscoveryCandidate:
        return SourceDiscoveryCandidate(
            item_type=item_type,
            object_key=object_key,
            domain=domain,
            name=object_key,
            url=f"https://{object_key}",
            authority_tier="B",
            authority_score=authority_score,
            recommendation="review",
            recommendation_reason="test",
            evidence_count=1,
            matched_queries=["test"],
            sample_titles=["test"],
            sample_snippets=["test"],
        )

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

    def test_preserves_github_release_tag_path_without_scheme(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "github.com/openclaw/openclaw/releases/tag/v1.2.3",
            SourceDiscoveryFocus.FRONTIER,
        )
        self.assertEqual(item_type, "release")
        self.assertEqual(object_key, "github.com/openclaw/openclaw/release/v1.2.3")
        self.assertEqual(domain, "github.com")
        self.assertIn("release", display_name)
        self.assertIn("/releases/tag/v1.2.3", canonical_url)

    def test_identifies_github_user_profile_as_organization_object(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "https://github.com/openclaw",
            SourceDiscoveryFocus.METHOD,
        )
        self.assertEqual(item_type, "organization")
        self.assertEqual(object_key, "github.com/org/openclaw")
        self.assertEqual(display_name, "openclaw")
        self.assertEqual(canonical_url, "https://github.com/openclaw")
        self.assertEqual(domain, "github.com")

    def test_keeps_reserved_github_single_segment_paths_as_domain(self) -> None:
        for path in ("pricing", "search"):
            with self.subTest(path=path):
                item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
                    f"https://github.com/{path}",
                    SourceDiscoveryFocus.METHOD,
                )
                self.assertEqual(item_type, "domain")
                self.assertEqual(object_key, "github.com")
                self.assertEqual(display_name, "github.com")
                self.assertEqual(canonical_url, "https://github.com")
                self.assertEqual(domain, "github.com")

    def test_keeps_reserved_gitlab_single_segment_paths_as_domain(self) -> None:
        for path in ("explore", "projects", "groups"):
            with self.subTest(path=path):
                item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
                    f"https://gitlab.com/{path}",
                    SourceDiscoveryFocus.METHOD,
                )
                self.assertEqual(item_type, "domain")
                self.assertEqual(object_key, "gitlab.com")
                self.assertEqual(display_name, "gitlab.com")
                self.assertEqual(canonical_url, "https://gitlab.com")
                self.assertEqual(domain, "gitlab.com")

    def test_identifies_gitlab_user_profile_as_organization_object(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "https://gitlab.com/openclaw",
            SourceDiscoveryFocus.METHOD,
        )
        self.assertEqual(item_type, "organization")
        self.assertEqual(object_key, "gitlab.com/org/openclaw")
        self.assertEqual(display_name, "openclaw")
        self.assertEqual(canonical_url, "https://gitlab.com/openclaw")
        self.assertEqual(domain, "gitlab.com")

    def test_identifies_gitlab_repository_as_repository_object(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "https://gitlab.com/openclaw/openclaw",
            SourceDiscoveryFocus.METHOD,
        )
        self.assertEqual(item_type, "repository")
        self.assertEqual(object_key, "gitlab.com/openclaw/openclaw")
        self.assertEqual(display_name, "openclaw/openclaw")
        self.assertEqual(canonical_url, "https://gitlab.com/openclaw/openclaw")
        self.assertEqual(domain, "gitlab.com")

    def test_identifies_changelog_page_as_release_stream_object(self) -> None:
        for url in ("https://example.com/changelog", "https://example.com/whats-new"):
            with self.subTest(url=url):
                item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
                    url,
                    SourceDiscoveryFocus.LATEST,
                )
                self.assertEqual(item_type, "release")
                self.assertEqual(object_key, "example.com:release")
                self.assertEqual(domain, "example.com")
                self.assertIn("release stream", display_name)

    def test_identifies_event_pages_as_event_object(self) -> None:
        for url in (
            "https://example.org/events/agent-summit-2026",
            "https://example.org/ai-conference-2026",
            "https://example.org/agent-summit-2026",
            "https://example.org/workshop/agent-evaluation",
            "https://example.org/webinar/source-intelligence",
            "https://example.org/talks/agent-memory-boundaries",
        ):
            with self.subTest(url=url):
                item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
                    url,
                    SourceDiscoveryFocus.FRONTIER,
                )
                self.assertEqual(item_type, "event")
                self.assertEqual(object_key, "example.org:event")
                self.assertEqual(domain, "example.org")
                self.assertIn("events", display_name)
                self.assertIn("example.org", canonical_url)

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

    def test_identifies_github_issue_as_signal_object_in_authoritative_focus(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "https://github.com/openclaw/openclaw/issues/123",
            SourceDiscoveryFocus.AUTHORITATIVE,
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

    def test_identifies_github_discussion_as_signal_object_in_authoritative_focus(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "https://github.com/openclaw/openclaw/discussions/456",
            SourceDiscoveryFocus.AUTHORITATIVE,
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

    def test_related_repository_owner_can_seed_organization_candidate(self) -> None:
        candidate = _build_related_candidate_seed(
            {
                "relation": "owner",
                "item_type": "organization",
                "object_key": "github.com/org/openclaw",
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
        self.assertEqual(candidate["item_type"], "organization")
        self.assertEqual(candidate["url"], "https://github.com/openclaw")
        self.assertEqual(candidate["inferred_roles"], [])
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

    def test_github_issue_signal_emits_repository_and_owner_relation_hints(self) -> None:
        related = _candidate_relation_hints(
            "signal",
            "github.com/openclaw/openclaw/issue/123",
            "https://github.com/openclaw/openclaw/issues/123",
        )

        self.assertIn(
            {
                "relation": "repository",
                "item_type": "repository",
                "object_key": "github.com/openclaw/openclaw",
                "label": "openclaw/openclaw",
            },
            related,
        )
        self.assertIn(
            {
                "relation": "owner",
                "item_type": "organization",
                "object_key": "github.com/org/openclaw",
                "label": "openclaw",
            },
            related,
        )

    def test_github_discussion_and_pull_signals_emit_repository_relation_hint(self) -> None:
        for object_key, url in (
            (
                "github.com/openclaw/openclaw/discussion/456",
                "https://github.com/openclaw/openclaw/discussions/456",
            ),
            (
                "github.com/openclaw/openclaw/pull/789",
                "https://github.com/openclaw/openclaw/pull/789",
            ),
        ):
            with self.subTest(object_key=object_key):
                related = _candidate_relation_hints("signal", object_key, url)
                self.assertIn(
                    {
                        "relation": "repository",
                        "item_type": "repository",
                        "object_key": "github.com/openclaw/openclaw",
                        "label": "openclaw/openclaw",
                    },
                    related,
                )

    def test_reserved_github_namespace_signal_does_not_emit_repository_hints(self) -> None:
        related = _candidate_relation_hints(
            "signal",
            "github.com/orgs/openai/discussion/123",
            "https://github.com/orgs/openai/discussions/123",
        )

        self.assertNotIn("repository", {item["relation"] for item in related})
        self.assertFalse(
            any(item["object_key"].startswith("github.com/org/orgs") for item in related),
        )

    def test_reserved_github_namespace_discussion_stays_organization(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "https://github.com/orgs/openai/discussions/123",
            SourceDiscoveryFocus.METHOD,
        )

        self.assertEqual(item_type, "organization")
        self.assertEqual(object_key, "github.com/org/openai")
        self.assertEqual(display_name, "openai")
        self.assertEqual(canonical_url, "https://github.com/orgs/openai")
        self.assertEqual(domain, "github.com")

    def test_github_signal_repository_relation_can_seed_repository_candidate(self) -> None:
        candidate = _build_related_candidate_seed(
            {
                "relation": "repository",
                "item_type": "repository",
                "object_key": "github.com/openclaw/openclaw",
                "label": "openclaw/openclaw",
            },
            parent_object_key="github.com/openclaw/openclaw/issue/123",
            parent_name="openclaw/openclaw issue 123",
            parent_score=0.82,
            parent_tier="A",
            focus=SourceDiscoveryFocus.METHOD,
        )

        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate["item_type"], "repository")
        self.assertEqual(candidate["object_key"], "github.com/openclaw/openclaw")
        self.assertEqual(candidate["url"], "https://github.com/openclaw/openclaw")
        self.assertEqual(candidate["related_entities"][0]["item_type"], "signal")
        self.assertEqual(candidate["related_entities"][0]["object_key"], "github.com/openclaw/openclaw/issue/123")
        self.assertNotIn("status", candidate)
        self.assertNotIn("subscribed", candidate)

    def test_identifies_x_and_twitter_direct_profiles_as_person_objects(self) -> None:
        for url, object_key, display_name, canonical_url in (
            ("https://x.com/openclaw", "x.com/openclaw", "@openclaw", "https://x.com/openclaw"),
            (
                "https://twitter.com/openclaw",
                "twitter.com/openclaw",
                "@openclaw",
                "https://twitter.com/openclaw",
            ),
        ):
            with self.subTest(url=url):
                item_type, actual_object_key, actual_display_name, actual_canonical_url, domain = _candidate_identity(
                    url,
                    SourceDiscoveryFocus.METHOD,
                )
                self.assertEqual(item_type, "person")
                self.assertEqual(actual_object_key, object_key)
                self.assertEqual(actual_display_name, display_name)
                self.assertEqual(actual_canonical_url, canonical_url)
                self.assertIn(domain, {"x.com", "twitter.com"})

    def test_identifies_x_and_twitter_status_urls_as_signal_objects(self) -> None:
        for url, object_key, display_name in (
            ("https://x.com/openclaw/status/123456", "x.com/openclaw/status/123456", "@openclaw status 123456"),
            (
                "https://twitter.com/openclaw/status/123456",
                "twitter.com/openclaw/status/123456",
                "@openclaw status 123456",
            ),
        ):
            with self.subTest(url=url):
                item_type, actual_object_key, actual_display_name, canonical_url, domain = _candidate_identity(
                    url,
                    SourceDiscoveryFocus.METHOD,
                )
                self.assertEqual(item_type, "signal")
                self.assertEqual(actual_object_key, object_key)
                self.assertEqual(actual_display_name, display_name)
                self.assertEqual(canonical_url, url)
                self.assertIn(domain, {"x.com", "twitter.com"})

    def test_keeps_reserved_x_and_twitter_status_like_namespaces_as_domain(self) -> None:
        for url, expected_domain in (
            ("https://x.com/i/status/123456", "x.com"),
            ("https://twitter.com/search/status/123456", "twitter.com"),
        ):
            with self.subTest(url=url):
                item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
                    url,
                    SourceDiscoveryFocus.METHOD,
                )
                self.assertEqual(item_type, "domain")
                self.assertEqual(object_key, expected_domain)
                self.assertEqual(display_name, expected_domain)
                self.assertEqual(canonical_url, f"https://{expected_domain}")
                self.assertEqual(domain, expected_domain)

    def test_keeps_reserved_x_and_twitter_namespaces_as_domain(self) -> None:
        for url, domain in (
            ("https://x.com/hashtag/openclaw", "x.com"),
            ("https://twitter.com/intent/tweet", "twitter.com"),
            ("https://x.com/login", "x.com"),
            ("https://x.com/share", "x.com"),
        ):
            with self.subTest(url=url):
                item_type, object_key, display_name, canonical_url, actual_domain = _candidate_identity(
                    url,
                    SourceDiscoveryFocus.METHOD,
                )
                self.assertEqual(item_type, "domain")
                self.assertEqual(object_key, domain)
                self.assertEqual(display_name, domain)
                self.assertEqual(canonical_url, f"https://{domain}")
                self.assertEqual(actual_domain, domain)

    def test_direct_social_profile_person_does_not_emit_synthetic_latest_signal_hint(self) -> None:
        self.assertEqual(
            _candidate_relation_hints("person", "x.com/openclaw", "https://x.com/openclaw"),
            [],
        )
        self.assertEqual(
            _candidate_relation_hints("person", "twitter.com/openclaw", "https://twitter.com/openclaw"),
            [],
        )

    def test_reserved_social_status_like_relation_hints_do_not_emit_author_seed(self) -> None:
        for object_key, url in (
            ("x.com/i/status/123456", "https://x.com/i/status/123456"),
            ("twitter.com/search/status/123456", "https://twitter.com/search/status/123456"),
        ):
            with self.subTest(object_key=object_key):
                related = _candidate_relation_hints("signal", object_key, url)
                self.assertNotIn("author", {item["relation"] for item in related})
                self.assertFalse(
                    any(item["item_type"] == "person" for item in related),
                )
                self.assertEqual(_parent_related_item_type(object_key), "domain")

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

    def test_compress_source_candidates_applies_regularized_postprocess_order(self) -> None:
        candidates = [
            self._candidate(
                item_type="domain",
                object_key="github.com",
                domain="github.com",
                authority_score=0.72,
            ),
            self._candidate(
                item_type="repository",
                object_key="github.com/openclaw/openclaw",
                domain="github.com",
                authority_score=0.73,
            ),
            self._candidate(
                item_type="release",
                object_key="github.com/openclaw/openclaw/release/latest",
                domain="github.com",
                authority_score=0.74,
            ),
        ]

        compressed = compress_source_candidates(candidates, SourceDiscoveryFocus.LATEST)

        self.assertEqual(
            [candidate.object_key for candidate in compressed],
            ["github.com/openclaw/openclaw/release/latest"],
        )


if __name__ == "__main__":
    unittest.main()
