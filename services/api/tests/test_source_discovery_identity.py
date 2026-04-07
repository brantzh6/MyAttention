import unittest

from routers.feeds import (
    SourceDiscoveryFocus,
    _build_related_candidate_seed,
    _candidate_identity,
    _candidate_selection_threshold,
    _domain_quality_adjustment,
    _focus_type_priority,
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

    def test_normalizes_common_media_subdomains(self) -> None:
        item_type, object_key, display_name, canonical_url, domain = _candidate_identity(
            "https://m.36kr.com/p/3572628833139843",
            SourceDiscoveryFocus.FRONTIER,
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


if __name__ == "__main__":
    unittest.main()
