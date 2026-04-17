import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from routers.feeds import (
    SourceDiscoveryCandidate,
    SourceDiscoveryFocus,
    SourceDiscoveryInterestBias,
    SourcePlanItemModel,
    _candidate_identity,
    _discovery_queries,
    _execution_strategy_for_candidate,
    _refresh_source_plan_items,
    _review_cadence_for_candidate,
    _serialize_source_plan_version,
    _snapshot_source_plan,
    _snapshot_source_plan_from_payload,
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

    def test_refresh_source_plan_items_preserves_discovery_context(self):
        plan = SimpleNamespace(
            topic="agent harness patterns",
            focus="method",
            objective="build reusable plan",
            review_cadence_days=14,
            items=[],
            extra={
                "task_intent": "refresh source plan",
                "interest_bias": "method",
            },
        )
        discovery = SimpleNamespace(
            topic="agent harness patterns",
            focus=SourceDiscoveryFocus.METHOD,
            task_intent="refresh source plan",
            interest_bias=SourceDiscoveryInterestBias.METHOD,
            queries=["agent harness patterns github repository"],
            policy_id="source-method-v1",
            policy_version=1,
            portfolio_summary={"decision_status": "accepted"},
            notes=["task_intent=refresh source plan"],
            truth_boundary=["candidate discovery is inspect output, not canonical source truth"],
            candidates=[
                SourceDiscoveryCandidate(
                    item_type="repository",
                    object_key="github.com/openclaw/openclaw",
                    domain="github.com",
                    name="openclaw/openclaw",
                    url="https://github.com/openclaw/openclaw",
                    authority_tier="A",
                    authority_score=0.8,
                    recommendation="subscribe",
                    recommendation_reason="strong method artifact",
                    evidence_count=3,
                    matched_queries=["agent harness patterns github repository"],
                    sample_titles=["OpenClaw repository"],
                    sample_snippets=["OpenClaw coding agent repository"],
                )
            ],
        )

        with patch("routers.feeds._run_source_discovery", AsyncMock(return_value=discovery)), patch(
            "routers.feeds._find_existing_source_for_object",
            return_value=None,
        ):
            result = self._run_async(
                _refresh_source_plan_items(
                    db=SimpleNamespace(),
                    plan=plan,
                    focus=SourceDiscoveryFocus.METHOD,
                    review_cadence_days=14,
                    limit=6,
                )
            )

        self.assertIs(result, plan)
        self.assertEqual(plan.extra["task_intent"], "refresh source plan")
        self.assertEqual(plan.extra["interest_bias"], "method")
        self.assertEqual(plan.extra["discovery_notes"], ["task_intent=refresh source plan"])
        self.assertEqual(
            plan.extra["discovery_truth_boundary"],
            ["candidate discovery is inspect output, not canonical source truth"],
        )
        self.assertEqual(len(plan.items), 1)
        self.assertIsInstance(plan.items[0], SourcePlanItemModel)

    def test_snapshot_source_plan_from_payload_keeps_discovery_context(self):
        snapshot = _snapshot_source_plan_from_payload(
            topic="agent harness patterns",
            focus="method",
            objective="build reusable plan",
            task_intent="prepare source plan",
            interest_bias="method",
            discovery_notes=["task_intent=prepare source plan"],
            discovery_truth_boundary=["candidate discovery is inspect output, not canonical source truth"],
            review_cadence_days=14,
            items=[
                {
                    "item_type": "repository",
                    "object_key": "github.com/openclaw/openclaw",
                    "name": "openclaw/openclaw",
                    "url": "https://github.com/openclaw/openclaw",
                }
            ],
        )
        self.assertEqual(snapshot["task_intent"], "prepare source plan")
        self.assertEqual(snapshot["interest_bias"], "method")
        self.assertEqual(snapshot["discovery_notes"], ["task_intent=prepare source plan"])
        self.assertEqual(
            snapshot["discovery_truth_boundary"],
            ["candidate discovery is inspect output, not canonical source truth"],
        )

    def test_snapshot_source_plan_reads_discovery_context_from_plan_extra(self):
        plan = SimpleNamespace(
            topic="agent harness patterns",
            focus="method",
            objective="build reusable plan",
            review_cadence_days=14,
            extra={
                "task_intent": "refresh source plan",
                "interest_bias": "method",
                "discovery_notes": ["task_intent=refresh source plan"],
                "discovery_truth_boundary": ["candidate discovery is inspect output, not canonical source truth"],
            },
            items=[],
        )
        snapshot = _snapshot_source_plan(plan)
        self.assertEqual(snapshot["task_intent"], "refresh source plan")
        self.assertEqual(snapshot["interest_bias"], "method")
        self.assertEqual(snapshot["discovery_notes"], ["task_intent=refresh source plan"])
        self.assertEqual(
            snapshot["discovery_truth_boundary"],
            ["candidate discovery is inspect output, not canonical source truth"],
        )

    def test_serialize_source_plan_version_exposes_context_summary(self):
        version = SimpleNamespace(
            id="version-123",
            version_number=2,
            parent_version=1,
            trigger_type="manual_refresh",
            decision_status="accepted",
            plan_snapshot={
                "topic": "agent harness patterns",
                "focus": "method",
                "task_intent": "refresh source plan",
                "interest_bias": "method",
                "discovery_notes": ["task_intent=refresh source plan"],
                "discovery_truth_boundary": ["candidate discovery is inspect output, not canonical source truth"],
            },
            change_reason="refresh",
            change_summary={},
            evaluation={"decision_status": "accepted"},
            created_by="system",
            accepted_at=None,
            created_at=None,
        )
        response = _serialize_source_plan_version(version)
        self.assertEqual(response.topic, "agent harness patterns")
        self.assertEqual(response.focus, "method")
        self.assertEqual(response.task_intent, "refresh source plan")
        self.assertEqual(response.interest_bias, "method")
        self.assertEqual(response.discovery_notes, ["task_intent=refresh source plan"])
        self.assertEqual(
            response.discovery_truth_boundary,
            ["candidate discovery is inspect output, not canonical source truth"],
        )

    def _run_async(self, coroutine):
        import asyncio

        return asyncio.run(coroutine)


if __name__ == "__main__":
    unittest.main()
