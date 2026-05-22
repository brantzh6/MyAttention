import unittest
from types import SimpleNamespace

from attention.policies import _is_tool_project_frontier_topic, apply_attention_policy, get_attention_policy_specs
from routers.feeds import SourceDiscoveryCandidate, SourceDiscoveryFocus


class AttentionPolicyFoundationTests(unittest.TestCase):
    def test_default_policies_cover_all_source_focuses(self) -> None:
        specs = get_attention_policy_specs()
        by_focus = {item.focus: item.policy_id for item in specs}
        self.assertIn(SourceDiscoveryFocus.AUTHORITATIVE.value, by_focus)
        self.assertIn(SourceDiscoveryFocus.LATEST.value, by_focus)
        self.assertIn(SourceDiscoveryFocus.FRONTIER.value, by_focus)
        self.assertIn(SourceDiscoveryFocus.METHOD.value, by_focus)
        self.assertTrue(all(item.version >= 2 for item in specs))

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

    def test_method_policy_dedupes_by_object_not_domain(self) -> None:
        policy = SimpleNamespace(
            policy_id="source-method-v1",
            current_version=3,
            candidate_mix_policy={
                "bucket_order": ["implementation", "authority", "community", "research", "signal"],
                "target_mix": {"implementation": 3, "authority": 1},
                "minimum_distinct_buckets": 2,
            },
            scoring_policy={"prefer_tiers": ["A", "B", "S"]},
            gate_policy={"require_implementation_bucket": True, "max_single_bucket_share": 0.8},
        )
        candidates = [
            SourceDiscoveryCandidate(
                item_type="repository",
                object_key="github.com/microsoft/autogen",
                domain="github.com",
                name="microsoft/autogen",
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
                item_type="repository",
                object_key="github.com/langchain-ai/langgraph",
                domain="github.com",
                name="langchain-ai/langgraph",
                url="https://github.com/langchain-ai/langgraph",
                authority_tier="A",
                authority_score=0.87,
                recommendation="subscribe",
                recommendation_reason="implementation venue",
                evidence_count=4,
                matched_queries=["langgraph github"],
                sample_titles=["LangGraph"],
                sample_snippets=["agent graph framework"],
            ).model_dump(),
            SourceDiscoveryCandidate(
                item_type="repository",
                object_key="github.com/openai/swarm",
                domain="github.com",
                name="openai/swarm",
                url="https://github.com/openai/swarm",
                authority_tier="B",
                authority_score=0.79,
                recommendation="monitor",
                recommendation_reason="implementation venue",
                evidence_count=3,
                matched_queries=["swarm github"],
                sample_titles=["Swarm"],
                sample_snippets=["agent orchestration"],
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
        ]

        result = apply_attention_policy(policy, SourceDiscoveryFocus.METHOD, candidates, 4)
        selected_keys = {item["object_key"] for item in result.selected}
        self.assertIn("github.com/microsoft/autogen", selected_keys)
        self.assertIn("github.com/langchain-ai/langgraph", selected_keys)
        self.assertIn("github.com/openai/swarm", selected_keys)

    def test_person_follow_score_boosts_person_candidate(self) -> None:
        policy = SimpleNamespace(
            policy_id="source-frontier-v1",
            current_version=5,
            candidate_mix_policy={
                "bucket_order": ["research", "authority", "community", "signal", "implementation"],
                "target_mix": {"research": 1, "community": 1},
                "minimum_distinct_buckets": 1,
            },
            scoring_policy={"prefer_tiers": ["S", "A"]},
            gate_policy={"require_research_bucket": False, "max_single_bucket_share": 1.0},
        )
        candidates = [
            SourceDiscoveryCandidate(
                item_type="person",
                object_key="github.com/user/openclaw",
                domain="github.com",
                name="openclaw",
                url="https://github.com/openclaw",
                authority_tier="A",
                authority_score=0.62,
                recommendation="monitor",
                recommendation_reason="maintainer profile",
                evidence_count=2,
                follow_score=0.1,
                inferred_roles=["maintainer"],
                matched_queries=["openclaw maintainer"],
                sample_titles=["OpenClaw maintainer"],
                sample_snippets=["maintainer profile"],
            ).model_dump(),
            SourceDiscoveryCandidate(
                item_type="domain",
                object_key="example.com",
                domain="example.com",
                name="example.com",
                url="https://example.com",
                authority_tier="A",
                authority_score=0.62,
                recommendation="review",
                recommendation_reason="generic site",
                evidence_count=2,
                matched_queries=["openclaw site"],
                sample_titles=["Example"],
                sample_snippets=["generic site"],
            ).model_dump(),
        ]

        result = apply_attention_policy(policy, SourceDiscoveryFocus.FRONTIER, candidates, 2)
        self.assertEqual(result.selected[0]["item_type"], "person")

    def test_frontier_tool_project_topic_does_not_require_research_bucket(self) -> None:
        self.assertTrue(_is_tool_project_frontier_topic("openclaw agent framework"))

        policy = SimpleNamespace(
            policy_id="source-frontier-v1",
            current_version=6,
            candidate_mix_policy={
                "bucket_order": ["research", "authority", "community", "signal", "implementation"],
                "target_mix": {"community": 1, "implementation": 1, "signal": 1},
                "minimum_distinct_buckets": 2,
            },
            scoring_policy={"prefer_tiers": ["S", "A"]},
            gate_policy={"require_research_bucket": "conditional", "max_single_bucket_share": 1.0},
        )
        candidates = [
            SourceDiscoveryCandidate(
                item_type="repository",
                object_key="github.com/openclaw/openclaw",
                domain="github.com",
                name="openclaw/openclaw",
                url="https://github.com/openclaw/openclaw",
                authority_tier="A",
                authority_score=0.78,
                recommendation="subscribe",
                recommendation_reason="implementation venue",
                evidence_count=3,
                matched_queries=["openclaw github"],
                sample_titles=["OpenClaw"],
                sample_snippets=["agent framework"],
            ).model_dump(),
            SourceDiscoveryCandidate(
                item_type="person",
                object_key="github.com/user/openclaw",
                domain="github.com",
                name="openclaw maintainer",
                url="https://github.com/openclaw",
                authority_tier="A",
                authority_score=0.7,
                recommendation="monitor",
                recommendation_reason="maintainer",
                evidence_count=2,
                follow_score=0.1,
                inferred_roles=["maintainer"],
                matched_queries=["openclaw maintainer"],
                sample_titles=["Maintainer"],
                sample_snippets=["project maintainer"],
            ).model_dump(),
        ]

        result = apply_attention_policy(
            policy,
            SourceDiscoveryFocus.FRONTIER,
            candidates,
            2,
            topic="openclaw agent framework",
        )
        self.assertEqual(result.portfolio_summary["decision_status"], "accepted")

    def test_frontier_contextual_tech_media_is_treated_as_signal(self) -> None:
        policy = SimpleNamespace(
            policy_id="source-frontier-v1",
            current_version=6,
            candidate_mix_policy={
                "bucket_order": ["research", "authority", "community", "signal", "implementation"],
                "target_mix": {"signal": 1},
                "minimum_distinct_buckets": 1,
            },
            scoring_policy={"prefer_tiers": ["S", "A"]},
            gate_policy={"require_research_bucket": False, "max_single_bucket_share": 1.0},
        )
        candidates = [
            SourceDiscoveryCandidate(
                item_type="domain",
                object_key="36kr.com",
                domain="36kr.com",
                name="36kr.com",
                url="https://36kr.com/p/example",
                authority_tier="A",
                authority_score=0.6,
                recommendation="monitor",
                recommendation_reason="contextual tech media",
                evidence_count=1,
                matched_queries=["openclaw latest"],
                sample_titles=["OpenClaw release discussed"],
                sample_snippets=["community and industry reaction"],
            ).model_dump(),
        ]

        result = apply_attention_policy(policy, SourceDiscoveryFocus.FRONTIER, candidates, 1, topic="openclaw")
        self.assertEqual(result.selected[0]["object_bucket"], "signal")
        self.assertEqual(result.portfolio_summary["topic_profile"], "tool_project")


if __name__ == "__main__":
    unittest.main()
