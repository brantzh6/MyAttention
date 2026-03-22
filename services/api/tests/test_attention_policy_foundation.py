import unittest
from types import SimpleNamespace

from attention.policies import apply_attention_policy, get_attention_policy_specs
from routers.feeds import SourceDiscoveryCandidate, SourceDiscoveryFocus


class AttentionPolicyFoundationTests(unittest.TestCase):
    def test_default_policies_cover_all_source_focuses(self) -> None:
        specs = get_attention_policy_specs()
        by_focus = {item.focus: item.policy_id for item in specs}
        self.assertIn(SourceDiscoveryFocus.AUTHORITATIVE.value, by_focus)
        self.assertIn(SourceDiscoveryFocus.LATEST.value, by_focus)
        self.assertIn(SourceDiscoveryFocus.FRONTIER.value, by_focus)
        self.assertIn(SourceDiscoveryFocus.METHOD.value, by_focus)

    def test_method_policy_preserves_diversity_across_key_buckets(self) -> None:
        policy = SimpleNamespace(
            policy_id="source-method-v1",
            current_version=1,
            candidate_mix_policy={
                "bucket_order": ["implementation", "authority", "community", "research", "signal"],
                "target_mix": {"implementation": 2, "authority": 1, "community": 1, "research": 1},
                "minimum_distinct_buckets": 4,
            },
            scoring_policy={"prefer_tiers": ["A", "B", "S"]},
            gate_policy={"require_implementation_bucket": True, "max_single_bucket_share": 0.7},
        )
        candidates = [
            SourceDiscoveryCandidate(
                domain="github.com",
                name="GitHub",
                url="https://github.com/microsoft/autogen",
                authority_tier="A",
                authority_score=0.88,
                recommendation="subscribe",
                recommendation_reason="implementation venue",
                evidence_count=5,
                matched_queries=["multi agent framework github"],
                sample_titles=["AutoGen"],
                sample_snippets=["multi-agent framework"],
            ).model_dump(),
            SourceDiscoveryCandidate(
                domain="langchain-ai.github.io",
                name="LangGraph",
                url="https://langchain-ai.github.io/langgraph/",
                authority_tier="A",
                authority_score=0.86,
                recommendation="monitor",
                recommendation_reason="implementation docs",
                evidence_count=4,
                matched_queries=["langgraph docs"],
                sample_titles=["LangGraph"],
                sample_snippets=["multi-agent network"],
            ).model_dump(),
            SourceDiscoveryCandidate(
                domain="openai.com",
                name="OpenAI",
                url="https://openai.com",
                authority_tier="S",
                authority_score=0.95,
                recommendation="monitor",
                recommendation_reason="authority",
                evidence_count=3,
                matched_queries=["openai agents"],
                sample_titles=["OpenAI"],
                sample_snippets=["engineering blog"],
            ).model_dump(),
            SourceDiscoveryCandidate(
                domain="reddit.com",
                name="Reddit",
                url="https://reddit.com/r/MachineLearning",
                authority_tier="B",
                authority_score=0.72,
                recommendation="review",
                recommendation_reason="community signal",
                evidence_count=4,
                matched_queries=["multi agent reddit"],
                sample_titles=["Discussion"],
                sample_snippets=["community feedback"],
            ).model_dump(),
            SourceDiscoveryCandidate(
                domain="openreview.net",
                name="OpenReview",
                url="https://openreview.net",
                authority_tier="A",
                authority_score=0.84,
                recommendation="monitor",
                recommendation_reason="research venue",
                evidence_count=4,
                matched_queries=["agent workshop"],
                sample_titles=["Workshop"],
                sample_snippets=["research discussion"],
            ).model_dump(),
        ]

        result = apply_attention_policy(policy, SourceDiscoveryFocus.METHOD, candidates, 5)

        buckets = {item["object_bucket"] for item in result.selected}
        self.assertIn("implementation", buckets)
        self.assertIn("authority", buckets)
        self.assertIn("community", buckets)
        self.assertIn("research", buckets)
        self.assertEqual(result.portfolio_summary["decision_status"], "accepted")


if __name__ == "__main__":
    unittest.main()
