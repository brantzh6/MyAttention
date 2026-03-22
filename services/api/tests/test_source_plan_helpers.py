import unittest

from routers.feeds import (
    SourceDiscoveryCandidate,
    SourceDiscoveryFocus,
    _candidate_identity,
    _discovery_queries,
    _execution_strategy_for_candidate,
    _review_cadence_for_candidate,
)


class SourcePlanHelperTests(unittest.TestCase):
    def test_agent_assisted_strategy_for_social_and_community_domains(self):
        candidate = SourceDiscoveryCandidate(
            domain="reddit.com",
            name="Reddit",
            url="https://reddit.com/r/MachineLearning",
            authority_tier="B",
            authority_score=0.7,
            recommendation="monitor",
            recommendation_reason="community signal",
            evidence_count=3,
            matched_queries=["ml communities"],
            sample_titles=[],
            sample_snippets=[],
        )
        strategy = _execution_strategy_for_candidate(candidate, SourceDiscoveryFocus.METHOD)
        self.assertEqual(strategy, "agent_assisted")

    def test_review_cadence_tightens_for_latest_subscriptions(self):
        candidate = SourceDiscoveryCandidate(
            domain="reuters.com",
            name="Reuters",
            url="https://www.reuters.com",
            authority_tier="A",
            authority_score=0.9,
            recommendation="subscribe",
            recommendation_reason="latest coverage",
            evidence_count=4,
            matched_queries=["ai latest official"],
            sample_titles=[],
            sample_snippets=[],
        )
        cadence = _review_cadence_for_candidate(candidate, SourceDiscoveryFocus.LATEST, 14)
        self.assertEqual(cadence, 3)

    def test_method_focus_extracts_github_repo_identity(self):
        item_type, object_key, display_name, canonical_url, source_domain = _candidate_identity(
            "https://github.com/microsoft/autogen/blob/main/README.md",
            SourceDiscoveryFocus.METHOD,
        )
        self.assertEqual(item_type, "repository")
        self.assertEqual(object_key, "github.com/microsoft/autogen")
        self.assertEqual(display_name, "microsoft/autogen")
        self.assertEqual(canonical_url, "https://github.com/microsoft/autogen")
        self.assertEqual(source_domain, "github.com")

    def test_method_focus_extracts_reddit_community_identity(self):
        item_type, object_key, display_name, canonical_url, source_domain = _candidate_identity(
            "https://reddit.com/r/MachineLearning/comments/abc123/some_post/",
            SourceDiscoveryFocus.METHOD,
        )
        self.assertEqual(item_type, "community")
        self.assertEqual(object_key, "reddit.com/r/machinelearning")
        self.assertEqual(display_name, "r/MachineLearning")
        self.assertEqual(canonical_url, "https://reddit.com/r/MachineLearning")
        self.assertEqual(source_domain, "reddit.com")

    def test_discovery_queries_use_execution_policy_templates(self):
        queries = _discovery_queries(
            "multi agent research",
            SourceDiscoveryFocus.METHOD,
            {
                "query_templates": [
                    "{topic} github stars",
                    "{topic} reddit discussion",
                ]
            },
        )
        self.assertEqual(
            queries,
            [
                "multi agent research github stars",
                "multi agent research reddit discussion",
            ],
        )


if __name__ == "__main__":
    unittest.main()
