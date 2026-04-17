import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient


api_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(api_dir))


def load_feeds_router_module():
    router_path = api_dir / "routers" / "feeds.py"
    spec = importlib.util.spec_from_file_location("feeds_router_test_module", router_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


feeds_module = load_feeds_router_module()
feeds_router = feeds_module.router

test_app = FastAPI(title="Feeds Source Discovery Test API")
test_app.include_router(feeds_router, prefix="/api")


class _DummySearch:
    ENGINE_ADVANCED = "advanced"
    TIME_ONE_MONTH = "month"
    TIME_NO_LIMIT = "all"

    def search(self, *args, **kwargs):
        return {
            "success": True,
            "results": [
                SimpleNamespace(
                    link="https://github.com/openclaw/openclaw",
                    source="github.com",
                    title="OpenClaw repository",
                    snippet="OpenClaw coding agent repository and releases",
                    main_text="OpenClaw coding agent repository and releases",
                ),
                SimpleNamespace(
                    link="https://reddit.com/r/MachineLearning/comments/abc123/openclaw_release_discussion/",
                    source="reddit.com",
                    title="OpenClaw release discussion",
                    snippet="Maintainers and users discuss the latest release",
                    main_text="Maintainers and users discuss the latest release",
                ),
            ],
        }


class _DummyClassifier:
    def classify(self, *args, **kwargs):
        return SimpleNamespace(score=0.78, tier="A")


class SourceDiscoveryRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(test_app)

    def test_sources_discover_returns_extended_contract_fields(self):
        from db import get_db

        async def mock_get_db():
            return object()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "AliyunWebSearch", return_value=_DummySearch()), patch.object(
                feeds_module, "get_authority_classifier", return_value=_DummyClassifier()
            ), patch.object(
                feeds_module,
                "resolve_attention_policy",
                AsyncMock(return_value=SimpleNamespace(execution_policy={})),
            ), patch.object(
                feeds_module,
                "apply_attention_policy",
                return_value=SimpleNamespace(
                    policy_id="source-method-v1",
                    policy_version=1,
                    portfolio_summary={"decision_status": "accepted", "topic_profile": "tool_project"},
                    selected=[],
                ),
            ) as mock_apply:
                def _selected_candidates(*args, **kwargs):
                    payloads = args[2]
                    return SimpleNamespace(
                        policy_id="source-method-v1",
                        policy_version=1,
                        portfolio_summary={"decision_status": "accepted", "topic_profile": "tool_project"},
                        selected=payloads[:2],
                    )

                mock_apply.side_effect = _selected_candidates

                response = self.client.post(
                    "/api/sources/discover",
                    json={
                        "topic": "agent harness patterns",
                        "focus": "method",
                        "task_intent": "prepare first discovery loop",
                        "interest_bias": "method",
                        "limit": 6,
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["topic"], "agent harness patterns")
            self.assertEqual(data["focus"], "method")
            self.assertEqual(data["task_intent"], "prepare first discovery loop")
            self.assertEqual(data["interest_bias"], "method")
            self.assertTrue(data["notes"])
            self.assertEqual(len(data["truth_boundary"]), 3)
            self.assertGreaterEqual(len(data["candidates"]), 1)

            first = data["candidates"][0]
            self.assertIn("source_nature", first)
            self.assertIn("temperature", first)
            self.assertIn("recommended_mode", first)
            self.assertIn("recommended_execution_strategy", first)
            self.assertIn("why_relevant", first)
            self.assertIn("confidence_note", first)
            self.assertIn("candidate_endpoints", first)
            self.assertTrue(first["candidate_endpoints"])
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_judge_inspect_returns_ai_advisory_judgments(self):
        from db import get_db

        async def mock_get_db():
            return object()

        discovery = feeds_module.SourceDiscoveryResponse(
            topic="openclaw operator patterns",
            focus=feeds_module.SourceDiscoveryFocus.METHOD,
            task_intent="judge which candidates are worth following",
            interest_bias=feeds_module.SourceDiscoveryInterestBias.METHOD,
            queries=["openclaw github repository"],
            notes=["topic=openclaw operator patterns"],
            truth_boundary=feeds_module._discovery_truth_boundary(),
            candidates=[
                feeds_module.SourceDiscoveryCandidate(
                    item_type="repository",
                    object_key="github.com/openclaw/openclaw",
                    domain="github.com",
                    name="openclaw/openclaw",
                    url="https://github.com/openclaw/openclaw",
                    authority_tier="A",
                    authority_score=0.82,
                    recommendation="subscribe",
                    recommendation_reason="method-relevant repository",
                    evidence_count=3,
                    matched_queries=["openclaw github repository"],
                    sample_titles=["OpenClaw repository"],
                    sample_snippets=["OpenClaw coding agent repository"],
                ),
                feeds_module.SourceDiscoveryCandidate(
                    item_type="signal",
                    object_key="github.com/openclaw/openclaw/issue/123",
                    domain="github.com",
                    name="openclaw/openclaw issue 123",
                    url="https://github.com/openclaw/openclaw/issues/123",
                    authority_tier="B",
                    authority_score=0.64,
                    recommendation="monitor",
                    recommendation_reason="implementation discussion",
                    evidence_count=2,
                    matched_queries=["openclaw github issue"],
                    sample_titles=["Issue 123"],
                    sample_snippets=["Runtime orchestration discussion"],
                ),
            ],
        )

        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                return """
                {
                  "summary": "repository should be followed first",
                  "judgments": [
                    {
                      "object_key": "github.com/openclaw/openclaw",
                      "verdict": "follow",
                      "rationale": "core implementation surface",
                      "confidence": 0.91,
                      "review_priority": "high"
                    },
                    {
                      "object_key": "github.com/openclaw/openclaw/issue/123",
                      "verdict": "review",
                      "rationale": "specific but secondary thread",
                      "confidence": 0.62,
                      "review_priority": "normal"
                    },
                    {
                      "object_key": "github.com/out-of-scope/repo",
                      "verdict": "follow",
                      "rationale": "should be ignored",
                      "confidence": 1.0,
                      "review_priority": "high"
                    }
                  ]
                }
                """

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "_run_source_discovery", AsyncMock(return_value=discovery)), patch.object(
                feeds_module, "LLMAdapter", return_value=_DummyAdapter()
            ):
                response = self.client.post(
                    "/api/sources/discover/judge/inspect",
                    json={
                        "topic": "openclaw operator patterns",
                        "focus": "method",
                        "task_intent": "judge which candidates are worth following",
                        "interest_bias": "method",
                        "limit": 6,
                        "max_candidates": 2,
                        "provider": "qwen",
                        "model": "qwen3.6-plus",
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["topic"], "openclaw operator patterns")
            self.assertEqual(data["provider"], "qwen")
            self.assertEqual(data["model"], "qwen3.6-plus")
            self.assertEqual(len(data["judged_candidates"]), 2)
            self.assertEqual(len(data["judgments"]), 2)
            self.assertEqual(data["judgments"][0]["object_key"], "github.com/openclaw/openclaw")
            self.assertEqual(data["judgments"][0]["verdict"], "follow")
            self.assertEqual(data["judgments"][0]["review_priority"], "high")
            self.assertEqual(data["judgments"][1]["object_key"], "github.com/openclaw/openclaw/issue/123")
            self.assertEqual(data["judgments"][1]["verdict"], "review")
            self.assertIn("advisory", " ".join(data["truth_boundary"]).lower())
            self.assertIn("summary is advisory", " ".join(data["truth_boundary"]).lower())
            self.assertEqual(data["summary"], "repository should be followed first")
            self.assertIn("ai_judgment_parse_status=valid_json", data["notes"])
            self.assertIn("discarded_judgments=1", data["notes"])
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_judge_inspect_handles_invalid_json_without_500(self):
        from db import get_db

        async def mock_get_db():
            return object()

        discovery = feeds_module.SourceDiscoveryResponse(
            topic="openclaw operator patterns",
            focus=feeds_module.SourceDiscoveryFocus.METHOD,
            task_intent="judge invalid-json resilience",
            interest_bias=feeds_module.SourceDiscoveryInterestBias.METHOD,
            queries=["openclaw github repository"],
            notes=["topic=openclaw operator patterns"],
            truth_boundary=feeds_module._discovery_truth_boundary(),
            candidates=[
                feeds_module.SourceDiscoveryCandidate(
                    item_type="repository",
                    object_key="github.com/openclaw/openclaw",
                    domain="github.com",
                    name="openclaw/openclaw",
                    url="https://github.com/openclaw/openclaw",
                    authority_tier="A",
                    authority_score=0.82,
                    recommendation="subscribe",
                    recommendation_reason="method-relevant repository",
                    evidence_count=3,
                    matched_queries=["openclaw github repository"],
                    sample_titles=["OpenClaw repository"],
                    sample_snippets=["OpenClaw coding agent repository"],
                ),
            ],
        )

        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                return "```json\n{bad json}\n```"

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "_run_source_discovery", AsyncMock(return_value=discovery)), patch.object(
                feeds_module, "LLMAdapter", return_value=_DummyAdapter()
            ):
                response = self.client.post(
                    "/api/sources/discover/judge/inspect",
                    json={
                        "topic": "openclaw operator patterns",
                        "focus": "method",
                        "task_intent": "judge invalid-json resilience",
                        "interest_bias": "method",
                        "limit": 6,
                        "max_candidates": 1,
                        "provider": "qwen",
                        "model": "qwen3.6-plus",
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["summary"], "")
            self.assertEqual(data["judgments"], [])
            self.assertIn("ai_judgment_parse_status=invalid_json_fallback", data["notes"])
            self.assertIn("discarded_judgments=0", data["notes"])
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_judge_panel_inspect_exposes_agreement_shape(self):
        from db import get_db

        async def mock_get_db():
            return object()

        discovery = feeds_module.SourceDiscoveryResponse(
            topic="openclaw operator patterns",
            focus=feeds_module.SourceDiscoveryFocus.METHOD,
            task_intent="compare model judgments on the same candidates",
            interest_bias=feeds_module.SourceDiscoveryInterestBias.METHOD,
            queries=["openclaw github repository"],
            notes=["topic=openclaw operator patterns"],
            truth_boundary=feeds_module._discovery_truth_boundary(),
            candidates=[
                feeds_module.SourceDiscoveryCandidate(
                    item_type="repository",
                    object_key="github.com/openclaw/openclaw",
                    domain="github.com",
                    name="openclaw/openclaw",
                    url="https://github.com/openclaw/openclaw",
                    authority_tier="A",
                    authority_score=0.82,
                    recommendation="subscribe",
                    recommendation_reason="method-relevant repository",
                    evidence_count=3,
                    matched_queries=["openclaw github repository"],
                    sample_titles=["OpenClaw repository"],
                    sample_snippets=["OpenClaw coding agent repository"],
                ),
                feeds_module.SourceDiscoveryCandidate(
                    item_type="signal",
                    object_key="github.com/openclaw/openclaw/issue/123",
                    domain="github.com",
                    name="openclaw/openclaw issue 123",
                    url="https://github.com/openclaw/openclaw/issues/123",
                    authority_tier="B",
                    authority_score=0.64,
                    recommendation="monitor",
                    recommendation_reason="implementation discussion",
                    evidence_count=2,
                    matched_queries=["openclaw github issue"],
                    sample_titles=["Issue 123"],
                    sample_snippets=["Runtime orchestration discussion"],
                ),
            ],
        )

        class _DummyAdapter:
            def __init__(self):
                self.chat = AsyncMock(
                    side_effect=[
                        """
                        {
                          "summary": "primary prefers following repo and reviewing thread",
                          "judgments": [
                            {
                              "object_key": "github.com/openclaw/openclaw",
                              "verdict": "follow",
                              "rationale": "core implementation surface",
                              "confidence": 0.91,
                              "review_priority": "high"
                            },
                            {
                              "object_key": "github.com/openclaw/openclaw/issue/123",
                              "verdict": "review",
                              "rationale": "secondary discussion",
                              "confidence": 0.60,
                              "review_priority": "normal"
                            }
                          ]
                        }
                        """,
                        """
                        {
                          "summary": "secondary agrees on repo but ignores thread",
                          "judgments": [
                            {
                              "object_key": "github.com/openclaw/openclaw",
                              "verdict": "follow",
                              "rationale": "still the main object",
                              "confidence": 0.87,
                              "review_priority": "high"
                            },
                            {
                              "object_key": "github.com/openclaw/openclaw/issue/123",
                              "verdict": "ignore",
                              "rationale": "too specific",
                              "confidence": 0.55,
                              "review_priority": "low"
                            }
                          ]
                        }
                        """,
                    ]
                )

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "_run_source_discovery", AsyncMock(return_value=discovery)), patch.object(
                feeds_module, "LLMAdapter", return_value=_DummyAdapter()
            ):
                response = self.client.post(
                    "/api/sources/discover/judge/panel/inspect",
                    json={
                        "topic": "openclaw operator patterns",
                        "focus": "method",
                        "task_intent": "compare model judgments on the same candidates",
                        "interest_bias": "method",
                        "limit": 6,
                        "max_candidates": 2,
                        "primary_provider": "qwen",
                        "primary_model": "qwen3.6-plus",
                        "secondary_provider": "anthropic",
                        "secondary_model": "claude-sonnet",
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["primary_provider"], "qwen")
            self.assertEqual(data["secondary_provider"], "anthropic")
            self.assertEqual(len(data["primary_judgments"]), 2)
            self.assertEqual(len(data["secondary_judgments"]), 2)
            self.assertEqual(data["panel_summary"]["shared_candidates"], 2)
            self.assertEqual(data["panel_summary"]["agreement_count"], 1)
            self.assertEqual(data["panel_summary"]["disagreement_count"], 1)
            self.assertEqual(data["panel_summary"]["panel_signal"], "mixed")
            self.assertIn("github.com/openclaw/openclaw/issue/123", data["panel_summary"]["disagreed_object_keys"])
            self.assertIn("panel inspect exposes agreement shape", " ".join(data["truth_boundary"]).lower())
            self.assertIn("primary_parse_status=valid_json", data["notes"])
            self.assertIn("secondary_parse_status=valid_json", data["notes"])
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_judge_panel_inspect_surfaces_consensus_and_disagreement_insights(self):
        from db import get_db

        async def mock_get_db():
            return object()

        discovery = feeds_module.SourceDiscoveryResponse(
            topic="llm agent evaluation",
            focus=feeds_module.SourceDiscoveryFocus.AUTHORITATIVE,
            task_intent="panel insight test",
            interest_bias=feeds_module.SourceDiscoveryInterestBias.AUTHORITY,
            queries=["llm agent eval benchmark"],
            notes=["test"],
            truth_boundary=feeds_module._discovery_truth_boundary(),
            candidates=[
                feeds_module.SourceDiscoveryCandidate(
                    item_type="domain",
                    object_key="eval-leaderboard.ai",
                    domain="eval-leaderboard.ai",
                    name="Eval Leaderboard",
                    url="https://eval-leaderboard.ai",
                    authority_tier="A",
                    authority_score=0.9,
                    recommendation="subscribe",
                    recommendation_reason="top eval site",
                    evidence_count=5,
                    matched_queries=["llm agent eval benchmark"],
                    sample_titles=["LLM Eval Leaderboard"],
                    sample_snippets=["Benchmark results for LLM agents"],
                ),
                feeds_module.SourceDiscoveryCandidate(
                    item_type="blog",
                    object_key="eval-leaderboard.ai/blog/obscure-metric",
                    domain="eval-leaderboard.ai",
                    name="Obscure Metric Blog",
                    url="https://eval-leaderboard.ai/blog/obscure-metric",
                    authority_tier="B",
                    authority_score=0.55,
                    recommendation="monitor",
                    recommendation_reason="niche blog",
                    evidence_count=1,
                    matched_queries=["llm agent eval benchmark"],
                    sample_titles=["Obscure metric"],
                    sample_snippets=["Deep dive into a niche metric"],
                ),
                feeds_module.SourceDiscoveryCandidate(
                    item_type="paper",
                    object_key="arxiv.org/abs/2501.00001",
                    domain="arxiv.org",
                    name="ArXiv paper 2501.00001",
                    url="https://arxiv.org/abs/2501.00001",
                    authority_tier="A",
                    authority_score=0.85,
                    recommendation="review",
                    recommendation_reason="relevant paper",
                    evidence_count=3,
                    matched_queries=["llm agent eval benchmark"],
                    sample_titles=["New eval method"],
                    sample_snippets=["A new evaluation methodology"],
                ),
            ],
        )

        class _DummyAdapter:
            def __init__(self):
                self.chat = AsyncMock(
                    side_effect=[
                        """
                        {
                          "summary": "primary: follow leaderboard, ignore blog, review paper",
                          "judgments": [
                            {
                              "object_key": "eval-leaderboard.ai",
                              "verdict": "follow",
                              "rationale": "primary eval surface",
                              "confidence": 0.92,
                              "review_priority": "high"
                            },
                            {
                              "object_key": "eval-leaderboard.ai/blog/obscure-metric",
                              "verdict": "ignore",
                              "rationale": "too niche",
                              "confidence": 0.78,
                              "review_priority": "low"
                            },
                            {
                              "object_key": "arxiv.org/abs/2501.00001",
                              "verdict": "follow",
                              "rationale": "promising new method",
                              "confidence": 0.80,
                              "review_priority": "high"
                            }
                          ]
                        }
                        """,
                        """
                        {
                          "summary": "secondary: follow leaderboard, ignore blog, review paper",
                          "judgments": [
                            {
                              "object_key": "eval-leaderboard.ai",
                              "verdict": "follow",
                              "rationale": "main benchmark source",
                              "confidence": 0.88,
                              "review_priority": "high"
                            },
                            {
                              "object_key": "eval-leaderboard.ai/blog/obscure-metric",
                              "verdict": "ignore",
                              "rationale": "not broadly useful",
                              "confidence": 0.60,
                              "review_priority": "low"
                            },
                            {
                              "object_key": "arxiv.org/abs/2501.00001",
                              "verdict": "review",
                              "rationale": "needs more evidence",
                              "confidence": 0.65,
                              "review_priority": "normal"
                            }
                          ]
                        }
                        """,
                    ]
                )

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "_run_source_discovery", AsyncMock(return_value=discovery)), patch.object(
                feeds_module, "LLMAdapter", return_value=_DummyAdapter()
            ):
                response = self.client.post(
                    "/api/sources/discover/judge/panel/inspect",
                    json={
                        "topic": "llm agent evaluation",
                        "focus": "authoritative",
                        "task_intent": "panel insight test",
                        "limit": 10,
                        "max_candidates": 3,
                        "primary_provider": "qwen",
                        "primary_model": "qwen3.6-plus",
                        "secondary_provider": "anthropic",
                        "secondary_model": "claude-sonnet",
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            insights = data["panel_insights"]

            # Consensus: both models follow eval-leaderboard.ai with high confidence
            self.assertEqual(len(insights["consensus_worthy"]), 1)
            consensus = insights["consensus_worthy"][0]
            self.assertEqual(consensus["object_key"], "eval-leaderboard.ai")
            self.assertEqual(consensus["shared_verdict"], "follow")
            self.assertIn("why_consensus", consensus)

            # Disagreement: arxiv paper is follow vs review (conviction-gap)
            self.assertEqual(len(insights["disagreement_worthy"]), 1)
            disagreement = insights["disagreement_worthy"][0]
            self.assertEqual(disagreement["object_key"], "arxiv.org/abs/2501.00001")
            self.assertIn(disagreement["primary_verdict"], ["follow", "review"])
            self.assertIn(disagreement["secondary_verdict"], ["follow", "review"])
            self.assertEqual(disagreement["divergence_type"], "conviction-gap")
            self.assertIn("why_opportunity", disagreement)

            # Follow-up hints present
            self.assertTrue(len(insights["follow_up_hints"]) > 0)
        finally:
            test_app.dependency_overrides.clear()

    def test_derive_panel_insights_classifies_polarized_disagreement(self):
        primary = [
            feeds_module.SourceCandidateJudgment(
                object_key="niche-blog.example",
                item_type="blog",
                verdict="follow",
                rationale="unique signal source",
                confidence=0.90,
                review_priority="high",
            ),
        ]
        secondary = [
            feeds_module.SourceCandidateJudgment(
                object_key="niche-blog.example",
                item_type="blog",
                verdict="ignore",
                rationale="too narrow",
                confidence=0.85,
                review_priority="low",
            ),
        ]
        insights = feeds_module._derive_panel_insights(primary, secondary)
        self.assertEqual(len(insights.consensus_worthy), 0)
        self.assertEqual(len(insights.disagreement_worthy), 1)
        d = insights.disagreement_worthy[0]
        self.assertEqual(d.divergence_type, "polarized")
        self.assertIn("maximally split", d.why_opportunity.lower())
        self.assertTrue(len(insights.follow_up_hints) > 0)
        self.assertTrue(any("polarized" in h.lower() for h in insights.follow_up_hints))

    def test_derive_panel_insights_classifies_uncertainty_driven(self):
        primary = [
            feeds_module.SourceCandidateJudgment(
                object_key="weak-signal.example",
                item_type="domain",
                verdict="follow",
                rationale="maybe useful",
                confidence=0.40,
                review_priority="normal",
            ),
        ]
        secondary = [
            feeds_module.SourceCandidateJudgment(
                object_key="weak-signal.example",
                item_type="domain",
                verdict="ignore",
                rationale="no evidence",
                confidence=0.70,
                review_priority="low",
            ),
        ]
        insights = feeds_module._derive_panel_insights(primary, secondary)
        self.assertEqual(len(insights.disagreement_worthy), 1)
        d = insights.disagreement_worthy[0]
        self.assertEqual(d.divergence_type, "uncertainty-driven")
        self.assertTrue(any("uncertainty" in h.lower() for h in insights.follow_up_hints))

    def test_derive_panel_insights_classifies_threshold_gap(self):
        primary = [
            feeds_module.SourceCandidateJudgment(
                object_key="borderline.example",
                item_type="domain",
                verdict="review",
                rationale="some signal",
                confidence=0.80,
                review_priority="normal",
            ),
        ]
        secondary = [
            feeds_module.SourceCandidateJudgment(
                object_key="borderline.example",
                item_type="domain",
                verdict="ignore",
                rationale="not enough",
                confidence=0.78,
                review_priority="low",
            ),
        ]
        insights = feeds_module._derive_panel_insights(primary, secondary)
        self.assertEqual(len(insights.disagreement_worthy), 1)
        d = insights.disagreement_worthy[0]
        self.assertEqual(d.divergence_type, "threshold-gap")

    def test_derive_panel_insights_empty_when_no_signal(self):
        primary: list[feeds_module.SourceCandidateJudgment] = []
        secondary: list[feeds_module.SourceCandidateJudgment] = []
        insights = feeds_module._derive_panel_insights(primary, secondary)
        self.assertEqual(len(insights.consensus_worthy), 0)
        self.assertEqual(len(insights.disagreement_worthy), 0)
        self.assertEqual(len(insights.follow_up_hints), 1)
        self.assertTrue(any("widening" in h.lower() or "refining" in h.lower() for h in insights.follow_up_hints))

    def test_sources_discover_judge_panel_inspect_response_has_panel_insights_field(self):
        from db import get_db

        async def mock_get_db():
            return object()

        discovery = feeds_module.SourceDiscoveryResponse(
            topic="test topic",
            focus=feeds_module.SourceDiscoveryFocus.AUTHORITATIVE,
            task_intent="schema test",
            queries=["test"],
            notes=[],
            truth_boundary=feeds_module._discovery_truth_boundary(),
            candidates=[
                feeds_module.SourceDiscoveryCandidate(
                    item_type="domain",
                    object_key="example.com",
                    domain="example.com",
                    name="Example",
                    url="https://example.com",
                    authority_tier="A",
                    authority_score=0.9,
                    recommendation="subscribe",
                    recommendation_reason="test",
                    evidence_count=1,
                    matched_queries=["test"],
                    sample_titles=["Test"],
                    sample_snippets=["Test snippet"],
                ),
            ],
        )

        class _DummyAdapter:
            def __init__(self):
                self.chat = AsyncMock(
                    side_effect=[
                        '{"summary": "follow", "judgments": [{"object_key": "example.com", "verdict": "follow", "rationale": "good", "confidence": 0.9}]}',
                        '{"summary": "follow", "judgments": [{"object_key": "example.com", "verdict": "follow", "rationale": "still good", "confidence": 0.85}]}',
                    ]
                )

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "_run_source_discovery", AsyncMock(return_value=discovery)), patch.object(
                feeds_module, "LLMAdapter", return_value=_DummyAdapter()
            ):
                response = self.client.post(
                    "/api/sources/discover/judge/panel/inspect",
                    json={
                        "topic": "test topic",
                        "focus": "authoritative",
                        "limit": 5,
                        "max_candidates": 1,
                        "primary_provider": "qwen",
                        "primary_model": "qwen3.6-plus",
                        "secondary_provider": "anthropic",
                        "secondary_model": "claude-sonnet",
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("panel_insights", data)
            self.assertIn("selective_absorption", data)
            self.assertIn("consensus_worthy", data["panel_insights"])
            self.assertIn("disagreement_worthy", data["panel_insights"])
            self.assertIn("follow_up_hints", data["panel_insights"])
            self.assertIn("ready_to_follow", data["selective_absorption"])
            self.assertEqual(len(data["selective_absorption"]["ready_to_follow"]), 1)
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_judge_panel_inspect_can_report_stable_shape(self):
        from db import get_db

        async def mock_get_db():
            return object()

        discovery = feeds_module.SourceDiscoveryResponse(
            topic="stable panel test",
            focus=feeds_module.SourceDiscoveryFocus.AUTHORITATIVE,
            task_intent="stable panel proof",
            interest_bias=feeds_module.SourceDiscoveryInterestBias.AUTHORITY,
            queries=["stable panel proof"],
            notes=["test"],
            truth_boundary=feeds_module._discovery_truth_boundary(),
            candidates=[
                feeds_module.SourceDiscoveryCandidate(
                    item_type="domain",
                    object_key="stable.example",
                    domain="stable.example",
                    name="Stable Example",
                    url="https://stable.example",
                    authority_tier="A",
                    authority_score=0.9,
                    recommendation="follow",
                    recommendation_reason="stable signal",
                    evidence_count=1,
                    matched_queries=["test"],
                    sample_titles=["Stable Example"],
                    sample_snippets=["Stable snippet"],
                ),
            ],
        )

        class _DummyAdapter:
            def __init__(self):
                self.chat = AsyncMock(
                    side_effect=[
                        '{"summary": "stable", "judgments": [{"object_key": "stable.example", "verdict": "follow", "rationale": "good", "confidence": 0.9}]}',
                        '{"summary": "stable", "judgments": [{"object_key": "stable.example", "verdict": "follow", "rationale": "also good", "confidence": 0.88}]}',
                    ]
                )

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "_run_source_discovery", AsyncMock(return_value=discovery)), patch.object(
                feeds_module, "LLMAdapter", return_value=_DummyAdapter()
            ):
                response = self.client.post(
                    "/api/sources/discover/judge/panel/inspect",
                    json={
                        "topic": "stable panel test",
                        "focus": "authoritative",
                        "limit": 5,
                        "max_candidates": 1,
                        "primary_provider": "qwen",
                        "primary_model": "qwen3.6-plus",
                        "secondary_provider": "anthropic",
                        "secondary_model": "claude-sonnet",
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["panel_summary"]["shared_candidates"], 1)
            self.assertEqual(data["panel_summary"]["agreement_count"], 1)
            self.assertEqual(data["panel_summary"]["primary_only_count"], 0)
            self.assertEqual(data["panel_summary"]["secondary_only_count"], 0)
            self.assertEqual(data["panel_summary"]["panel_signal"], "stable")
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_judge_panel_inspect_marks_invalid_secondary_as_mixed(self):
        from db import get_db

        async def mock_get_db():
            return object()

        discovery = feeds_module.SourceDiscoveryResponse(
            topic="invalid panel test",
            focus=feeds_module.SourceDiscoveryFocus.AUTHORITATIVE,
            task_intent="invalid panel proof",
            interest_bias=feeds_module.SourceDiscoveryInterestBias.AUTHORITY,
            queries=["invalid panel proof"],
            notes=["test"],
            truth_boundary=feeds_module._discovery_truth_boundary(),
            candidates=[
                feeds_module.SourceDiscoveryCandidate(
                    item_type="domain",
                    object_key="invalid.example",
                    domain="invalid.example",
                    name="Invalid Example",
                    url="https://invalid.example",
                    authority_tier="A",
                    authority_score=0.9,
                    recommendation="follow",
                    recommendation_reason="test",
                    evidence_count=1,
                    matched_queries=["test"],
                    sample_titles=["Invalid Example"],
                    sample_snippets=["Invalid snippet"],
                ),
            ],
        )

        class _DummyAdapter:
            def __init__(self):
                self.chat = AsyncMock(
                    side_effect=[
                        '{"summary": "primary ok", "judgments": [{"object_key": "invalid.example", "verdict": "follow", "rationale": "good", "confidence": 0.9}]}',
                        '```json\n{"summary": "broken", "judgments": [}\n```',
                    ]
                )

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "_run_source_discovery", AsyncMock(return_value=discovery)), patch.object(
                feeds_module, "LLMAdapter", return_value=_DummyAdapter()
            ):
                response = self.client.post(
                    "/api/sources/discover/judge/panel/inspect",
                    json={
                        "topic": "invalid panel test",
                        "focus": "authoritative",
                        "limit": 5,
                        "max_candidates": 1,
                        "primary_provider": "qwen",
                        "primary_model": "qwen3.6-plus",
                        "secondary_provider": "anthropic",
                        "secondary_model": "claude-sonnet",
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["panel_summary"]["shared_candidates"], 0)
            self.assertEqual(data["panel_summary"]["primary_only_count"], 1)
            self.assertEqual(data["panel_summary"]["secondary_only_count"], 0)
            self.assertEqual(data["panel_summary"]["panel_signal"], "mixed")
            self.assertIn("secondary_parse_status=invalid_json_fallback", data["notes"])
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_judge_panel_inspect_uses_provider_aware_default_models(self):
        from db import get_db

        async def mock_get_db():
            return object()

        discovery = feeds_module.SourceDiscoveryResponse(
            topic="provider default test",
            focus=feeds_module.SourceDiscoveryFocus.AUTHORITATIVE,
            task_intent="verify provider-aware defaults",
            interest_bias=feeds_module.SourceDiscoveryInterestBias.AUTHORITY,
            queries=["provider aware panel defaults"],
            notes=["test"],
            truth_boundary=feeds_module._discovery_truth_boundary(),
            candidates=[
                feeds_module.SourceDiscoveryCandidate(
                    item_type="domain",
                    object_key="example.com",
                    domain="example.com",
                    url="https://example.com",
                    name="Example",
                    title="Example",
                    authority_tier="high",
                    authority_score=0.92,
                    recommendation="follow",
                    recommendation_reason="good signal",
                    follow_score=0.88,
                    activity_freshness=0.2,
                    evidence_count=1,
                    matched_queries=["test"],
                    sample_titles=["Example"],
                    sample_snippets=["Snippet"],
                ),
            ],
        )

        async def _fake_panel_lane(*, provider, model, **kwargs):
            return (
                [
                    feeds_module.SourceCandidateJudgment(
                        object_key="example.com",
                        item_type="domain",
                        verdict="follow",
                        rationale=f"{provider}:{model}",
                        confidence=0.8,
                        review_priority="normal",
                    )
                ],
                f"{provider}:{model}",
                "valid_json",
                0,
            )

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "_run_source_discovery", AsyncMock(return_value=discovery)), patch.object(
                feeds_module, "_run_ai_candidate_judgment_once", AsyncMock(side_effect=_fake_panel_lane)
            ):
                response = self.client.post(
                    "/api/sources/discover/judge/panel/inspect",
                    json={
                        "topic": "provider default test",
                        "focus": "authoritative",
                        "limit": 5,
                        "max_candidates": 1,
                        "primary_provider": "qwen",
                        "secondary_provider": "anthropic",
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["primary_model"], "qwen3.6-plus")
            self.assertEqual(data["secondary_model"], "claude-3-5-sonnet-20241022")
            self.assertIn("primary_model=qwen3.6-plus", data["notes"])
            self.assertIn("secondary_model=claude-3-5-sonnet-20241022", data["notes"])
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_compresses_generic_domain_when_specific_source_exists(self):
        from db import get_db

        class _MixedGithubSearch:
            ENGINE_ADVANCED = "advanced"
            TIME_ONE_MONTH = "month"
            TIME_NO_LIMIT = "all"

            def search(self, *args, **kwargs):
                return {
                    "success": True,
                    "results": [
                        SimpleNamespace(
                            link="https://github.com",
                            source="github.com",
                            title="GitHub",
                            snippet="GitHub home page",
                            main_text="GitHub home page",
                        ),
                        SimpleNamespace(
                            link="https://github.com/openclaw/openclaw",
                            source="github.com",
                            title="OpenClaw repository",
                            snippet="OpenClaw coding agent repository and releases",
                            main_text="OpenClaw coding agent repository and releases",
                        ),
                    ],
                }

        async def mock_get_db():
            return object()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "AliyunWebSearch", return_value=_MixedGithubSearch()), patch.object(
                feeds_module, "get_authority_classifier", return_value=_DummyClassifier()
            ), patch.object(
                feeds_module,
                "resolve_attention_policy",
                AsyncMock(return_value=SimpleNamespace(execution_policy={})),
            ), patch.object(
                feeds_module,
                "apply_attention_policy",
                return_value=SimpleNamespace(
                    policy_id="source-method-v1",
                    policy_version=1,
                    portfolio_summary={"decision_status": "accepted", "topic_profile": "tool_project"},
                    selected=[],
                ),
            ) as mock_apply:
                def _selected_candidates(*args, **kwargs):
                    payloads = args[2]
                    return SimpleNamespace(
                        policy_id="source-method-v1",
                        policy_version=1,
                        portfolio_summary={"decision_status": "accepted", "topic_profile": "tool_project"},
                        selected=payloads,
                    )

                mock_apply.side_effect = _selected_candidates

                response = self.client.post(
                    "/api/sources/discover",
                    json={
                        "topic": "openclaw implementation sources",
                        "focus": "method",
                        "task_intent": "compress generic source noise",
                        "interest_bias": "method",
                        "limit": 6,
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            item_types = [candidate["item_type"] for candidate in data["candidates"]]
            object_keys = [candidate["object_key"] for candidate in data["candidates"]]
            self.assertIn("repository", item_types)
            self.assertIn("github.com/openclaw/openclaw", object_keys)
            self.assertNotIn("github.com", object_keys)
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_method_focus_classifies_github_issue_as_signal(self):
        from db import get_db

        class _GithubIssueSearch:
            ENGINE_ADVANCED = "advanced"
            TIME_ONE_MONTH = "month"
            TIME_NO_LIMIT = "all"

            def search(self, *args, **kwargs):
                return {
                    "success": True,
                    "results": [
                        SimpleNamespace(
                            link="https://github.com/openclaw/openclaw/issues/123",
                            source="github.com",
                            title="OpenClaw issue about runtime orchestration",
                            snippet="Discussion about controller/runtime task behavior",
                            main_text="Discussion about controller/runtime task behavior",
                        ),
                    ],
                }

        async def mock_get_db():
            return object()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "AliyunWebSearch", return_value=_GithubIssueSearch()), patch.object(
                feeds_module, "get_authority_classifier", return_value=_DummyClassifier()
            ), patch.object(
                feeds_module,
                "resolve_attention_policy",
                AsyncMock(return_value=SimpleNamespace(execution_policy={})),
            ), patch.object(
                feeds_module,
                "apply_attention_policy",
                return_value=SimpleNamespace(
                    policy_id="source-method-v1",
                    policy_version=1,
                    portfolio_summary={"decision_status": "accepted", "topic_profile": "tool_project"},
                    selected=[],
                ),
            ) as mock_apply:
                def _selected_candidates(*args, **kwargs):
                    payloads = args[2]
                    return SimpleNamespace(
                        policy_id="source-method-v1",
                        policy_version=1,
                        portfolio_summary={"decision_status": "accepted", "topic_profile": "tool_project"},
                        selected=payloads,
                    )

                mock_apply.side_effect = _selected_candidates

                response = self.client.post(
                    "/api/sources/discover",
                    json={
                        "topic": "openclaw implementation issues",
                        "focus": "method",
                        "task_intent": "surface GitHub repo issue as method signal",
                        "interest_bias": "method",
                        "limit": 6,
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data["candidates"]), 1)
            candidate = data["candidates"][0]
            self.assertEqual(candidate["item_type"], "signal")
            self.assertEqual(candidate["object_key"], "github.com/openclaw/openclaw/issue/123")
            self.assertEqual(candidate["domain"], "github.com")
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_seeds_person_candidate_from_x_status_signal(self):
        from db import get_db

        class _XStatusSearch:
            ENGINE_ADVANCED = "advanced"
            TIME_ONE_MONTH = "month"
            TIME_NO_LIMIT = "all"

            def search(self, *args, **kwargs):
                return {
                    "success": True,
                    "results": [
                        SimpleNamespace(
                            link="https://x.com/openclaw/status/123456",
                            source="x.com",
                            title="OpenClaw maintainer shared roadmap update",
                            snippet="Maintainer discusses release plan and implementation direction",
                            main_text="Maintainer discusses release plan and implementation direction",
                        ),
                    ],
                }

        async def mock_get_db():
            return object()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "AliyunWebSearch", return_value=_XStatusSearch()), patch.object(
                feeds_module, "get_authority_classifier", return_value=_DummyClassifier()
            ), patch.object(
                feeds_module,
                "resolve_attention_policy",
                AsyncMock(return_value=SimpleNamespace(execution_policy={})),
            ), patch.object(
                feeds_module,
                "apply_attention_policy",
                return_value=SimpleNamespace(
                    policy_id="source-method-v1",
                    policy_version=1,
                    portfolio_summary={"decision_status": "accepted", "topic_profile": "tool_project"},
                    selected=[],
                ),
            ) as mock_apply:
                def _selected_candidates(*args, **kwargs):
                    payloads = args[2]
                    person_payloads = [payload for payload in payloads if payload.get("item_type") == "person"]
                    signal_payloads = [payload for payload in payloads if payload.get("item_type") == "signal"]
                    return SimpleNamespace(
                        policy_id="source-method-v1",
                        policy_version=1,
                        portfolio_summary={"decision_status": "accepted", "topic_profile": "tool_project"},
                        selected=[*person_payloads[:1], *signal_payloads[:1]],
                    )

                mock_apply.side_effect = _selected_candidates

                response = self.client.post(
                    "/api/sources/discover",
                    json={
                        "topic": "openclaw maintainer activity",
                        "focus": "method",
                        "task_intent": "surface maintainer actors from social signal",
                        "interest_bias": "method",
                        "limit": 6,
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            person_candidates = [candidate for candidate in data["candidates"] if candidate["item_type"] == "person"]
            signal_candidates = [candidate for candidate in data["candidates"] if candidate["item_type"] == "signal"]
            self.assertTrue(person_candidates)
            self.assertTrue(signal_candidates)
            self.assertEqual(person_candidates[0]["object_key"], "x.com/openclaw")
            self.assertEqual(person_candidates[0]["recommended_execution_strategy"], "agent_assisted")
            self.assertIn("builder", person_candidates[0]["inferred_roles"])
            self.assertEqual(person_candidates[0]["related_entities"][0]["item_type"], "signal")
            self.assertEqual(person_candidates[0]["related_entities"][0]["object_key"], "x.com/openclaw/status/123456")
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_latest_focus_prefers_release_over_repository_for_same_repo(self):
        from db import get_db

        class _RepoReleaseSearch:
            ENGINE_ADVANCED = "advanced"
            TIME_ONE_MONTH = "month"
            TIME_NO_LIMIT = "all"

            def search(self, *args, **kwargs):
                return {
                    "success": True,
                    "results": [
                        SimpleNamespace(
                            link="https://github.com/openclaw/openclaw",
                            source="github.com",
                            title="OpenClaw repository",
                            snippet="OpenClaw coding agent repository",
                            main_text="OpenClaw coding agent repository",
                        ),
                        SimpleNamespace(
                            link="https://github.com/openclaw/openclaw/releases",
                            source="github.com",
                            title="OpenClaw releases",
                            snippet="OpenClaw latest release stream",
                            main_text="OpenClaw latest release stream",
                        ),
                    ],
                }

        async def mock_get_db():
            return object()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "AliyunWebSearch", return_value=_RepoReleaseSearch()), patch.object(
                feeds_module, "get_authority_classifier", return_value=_DummyClassifier()
            ), patch.object(
                feeds_module,
                "resolve_attention_policy",
                AsyncMock(return_value=SimpleNamespace(execution_policy={})),
            ), patch.object(
                feeds_module,
                "apply_attention_policy",
                return_value=SimpleNamespace(
                    policy_id="source-latest-v1",
                    policy_version=1,
                    portfolio_summary={"decision_status": "accepted", "topic_profile": "latest_intelligence"},
                    selected=[],
                ),
            ) as mock_apply:
                def _selected_candidates(*args, **kwargs):
                    payloads = args[2]
                    return SimpleNamespace(
                        policy_id="source-latest-v1",
                        policy_version=1,
                        portfolio_summary={"decision_status": "accepted", "topic_profile": "latest_intelligence"},
                        selected=payloads,
                    )

                mock_apply.side_effect = _selected_candidates

                response = self.client.post(
                    "/api/sources/discover",
                    json={
                        "topic": "openclaw latest releases",
                        "focus": "latest",
                        "task_intent": "prefer timely release surface over generic repo duplicate",
                        "interest_bias": "authority",
                        "limit": 6,
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            item_types = [candidate["item_type"] for candidate in data["candidates"]]
            object_keys = [candidate["object_key"] for candidate in data["candidates"]]
            self.assertIn("release", item_types)
            self.assertIn("github.com/openclaw/openclaw/release/latest", object_keys)
            self.assertNotIn("github.com/openclaw/openclaw", object_keys)
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_frontier_focus_prefers_release_over_repository_for_same_repo(self):
        from db import get_db

        class _RepoReleaseSearch:
            ENGINE_ADVANCED = "advanced"
            TIME_ONE_MONTH = "month"
            TIME_NO_LIMIT = "all"

            def search(self, *args, **kwargs):
                return {
                    "success": True,
                    "results": [
                        SimpleNamespace(
                            link="https://github.com/openclaw/openclaw",
                            source="github.com",
                            title="OpenClaw repository",
                            snippet="OpenClaw coding agent repository",
                            main_text="OpenClaw coding agent repository",
                        ),
                        SimpleNamespace(
                            link="https://github.com/openclaw/openclaw/releases",
                            source="github.com",
                            title="OpenClaw releases",
                            snippet="OpenClaw frontier release stream",
                            main_text="OpenClaw frontier release stream",
                        ),
                    ],
                }

        async def mock_get_db():
            return object()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "AliyunWebSearch", return_value=_RepoReleaseSearch()), patch.object(
                feeds_module, "get_authority_classifier", return_value=_DummyClassifier()
            ), patch.object(
                feeds_module,
                "resolve_attention_policy",
                AsyncMock(return_value=SimpleNamespace(execution_policy={})),
            ), patch.object(
                feeds_module,
                "apply_attention_policy",
                return_value=SimpleNamespace(
                    policy_id="source-frontier-v1",
                    policy_version=1,
                    portfolio_summary={"decision_status": "accepted", "topic_profile": "tool_project"},
                    selected=[],
                ),
            ) as mock_apply:
                def _selected_candidates(*args, **kwargs):
                    payloads = args[2]
                    return SimpleNamespace(
                        policy_id="source-frontier-v1",
                        policy_version=1,
                        portfolio_summary={"decision_status": "accepted", "topic_profile": "tool_project"},
                        selected=payloads,
                    )

                mock_apply.side_effect = _selected_candidates

                response = self.client.post(
                    "/api/sources/discover",
                    json={
                        "topic": "openclaw frontier releases",
                        "focus": "frontier",
                        "task_intent": "prefer release signal over duplicate repository",
                        "interest_bias": "frontier",
                        "limit": 6,
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            object_keys = [candidate["object_key"] for candidate in data["candidates"]]
            self.assertIn("github.com/openclaw/openclaw/release/latest", object_keys)
            self.assertNotIn("github.com/openclaw/openclaw", object_keys)
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_method_focus_keeps_repository_alongside_release_for_same_repo(self):
        from db import get_db

        class _RepoReleaseSearch:
            ENGINE_ADVANCED = "advanced"
            TIME_ONE_MONTH = "month"
            TIME_NO_LIMIT = "all"

            def search(self, *args, **kwargs):
                return {
                    "success": True,
                    "results": [
                        SimpleNamespace(
                            link="https://github.com/openclaw/openclaw",
                            source="github.com",
                            title="OpenClaw repository",
                            snippet="OpenClaw coding agent repository",
                            main_text="OpenClaw coding agent repository",
                        ),
                        SimpleNamespace(
                            link="https://github.com/openclaw/openclaw/releases",
                            source="github.com",
                            title="OpenClaw releases",
                            snippet="OpenClaw release stream",
                            main_text="OpenClaw release stream",
                        ),
                    ],
                }

        async def mock_get_db():
            return object()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "AliyunWebSearch", return_value=_RepoReleaseSearch()), patch.object(
                feeds_module, "get_authority_classifier", return_value=_DummyClassifier()
            ), patch.object(
                feeds_module,
                "resolve_attention_policy",
                AsyncMock(return_value=SimpleNamespace(execution_policy={})),
            ), patch.object(
                feeds_module,
                "apply_attention_policy",
                return_value=SimpleNamespace(
                    policy_id="source-method-v1",
                    policy_version=1,
                    portfolio_summary={"decision_status": "accepted", "topic_profile": "tool_project"},
                    selected=[],
                ),
            ) as mock_apply:
                def _selected_candidates(*args, **kwargs):
                    payloads = args[2]
                    return SimpleNamespace(
                        policy_id="source-method-v1",
                        policy_version=1,
                        portfolio_summary={"decision_status": "accepted", "topic_profile": "tool_project"},
                        selected=payloads,
                    )

                mock_apply.side_effect = _selected_candidates

                response = self.client.post(
                    "/api/sources/discover",
                    json={
                        "topic": "openclaw implementation releases",
                        "focus": "method",
                        "task_intent": "keep repository baseline object in method focus",
                        "interest_bias": "method",
                        "limit": 6,
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            object_keys = [candidate["object_key"] for candidate in data["candidates"]]
            self.assertIn("github.com/openclaw/openclaw/release/latest", object_keys)
            self.assertIn("github.com/openclaw/openclaw", object_keys)
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_latest_focus_classifies_contextual_media_article_as_signal(self):
        from db import get_db

        class _MediaArticleSearch:
            ENGINE_ADVANCED = "advanced"
            TIME_ONE_MONTH = "month"
            TIME_NO_LIMIT = "all"

            def search(self, *args, **kwargs):
                return {
                    "success": True,
                    "results": [
                        SimpleNamespace(
                            link="https://36kr.com/p/3572628833139843",
                            source="36kr.com",
                            title="OpenClaw latest funding and release update",
                            snippet="Industry and community reaction to the latest release move",
                            main_text="Industry and community reaction to the latest release move",
                        ),
                    ],
                }

        async def mock_get_db():
            return object()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "AliyunWebSearch", return_value=_MediaArticleSearch()), patch.object(
                feeds_module, "get_authority_classifier", return_value=_DummyClassifier()
            ), patch.object(
                feeds_module,
                "resolve_attention_policy",
                AsyncMock(return_value=SimpleNamespace(execution_policy={})),
            ), patch.object(
                feeds_module,
                "apply_attention_policy",
                return_value=SimpleNamespace(
                    policy_id="source-latest-v1",
                    policy_version=1,
                    portfolio_summary={"decision_status": "accepted", "topic_profile": "latest_intelligence"},
                    selected=[],
                ),
            ) as mock_apply:
                def _selected_candidates(*args, **kwargs):
                    payloads = args[2]
                    return SimpleNamespace(
                        policy_id="source-latest-v1",
                        policy_version=1,
                        portfolio_summary={"decision_status": "accepted", "topic_profile": "latest_intelligence"},
                        selected=payloads,
                    )

                mock_apply.side_effect = _selected_candidates

                response = self.client.post(
                    "/api/sources/discover",
                    json={
                        "topic": "openclaw latest industry reaction",
                        "focus": "latest",
                        "task_intent": "surface contextual media article as signal",
                        "interest_bias": "community",
                        "limit": 6,
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data["candidates"]), 1)
            candidate = data["candidates"][0]
            self.assertEqual(candidate["item_type"], "signal")
            self.assertEqual(candidate["object_key"], "36kr.com/article/p-3572628833139843")
            self.assertEqual(candidate["domain"], "36kr.com")
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_frontier_focus_classifies_contextual_media_article_as_signal(self):
        from db import get_db

        class _MediaArticleSearch:
            ENGINE_ADVANCED = "advanced"
            TIME_ONE_MONTH = "month"
            TIME_NO_LIMIT = "all"

            def search(self, *args, **kwargs):
                return {
                    "success": True,
                    "results": [
                        SimpleNamespace(
                            link="https://36kr.com/p/3572628833139843",
                            source="36kr.com",
                            title="OpenClaw frontier ecosystem discussion",
                            snippet="Ecosystem and industry discussion around an AI frontier move",
                            main_text="Ecosystem and industry discussion around an AI frontier move",
                        ),
                    ],
                }

        async def mock_get_db():
            return object()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "AliyunWebSearch", return_value=_MediaArticleSearch()), patch.object(
                feeds_module, "get_authority_classifier", return_value=_DummyClassifier()
            ), patch.object(
                feeds_module,
                "resolve_attention_policy",
                AsyncMock(return_value=SimpleNamespace(execution_policy={})),
            ), patch.object(
                feeds_module,
                "apply_attention_policy",
                return_value=SimpleNamespace(
                    policy_id="source-frontier-v1",
                    policy_version=1,
                    portfolio_summary={"decision_status": "accepted", "topic_profile": "tool_project"},
                    selected=[],
                ),
            ) as mock_apply:
                def _selected_candidates(*args, **kwargs):
                    payloads = args[2]
                    return SimpleNamespace(
                        policy_id="source-frontier-v1",
                        policy_version=1,
                        portfolio_summary={"decision_status": "accepted", "topic_profile": "tool_project"},
                        selected=payloads,
                    )

                mock_apply.side_effect = _selected_candidates

                response = self.client.post(
                    "/api/sources/discover",
                    json={
                        "topic": "openclaw frontier ecosystem reaction",
                        "focus": "frontier",
                        "task_intent": "surface contextual media article as frontier signal",
                        "interest_bias": "frontier",
                        "limit": 6,
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data["candidates"]), 1)
            candidate = data["candidates"][0]
            self.assertEqual(candidate["item_type"], "signal")
            self.assertEqual(candidate["object_key"], "36kr.com/article/p-3572628833139843")
            self.assertEqual(candidate["domain"], "36kr.com")
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_latest_focus_keeps_contextual_media_tag_page_outside_article_rule(self):
        from db import get_db

        class _MediaTagSearch:
            ENGINE_ADVANCED = "advanced"
            TIME_ONE_MONTH = "month"
            TIME_NO_LIMIT = "all"

            def search(self, *args, **kwargs):
                return {
                    "success": True,
                    "results": [
                        SimpleNamespace(
                            link="https://36kr.com/tag/agent",
                            source="36kr.com",
                            title="Agent topic page",
                            snippet="Topic aggregation page",
                            main_text="Topic aggregation page",
                        ),
                    ],
                }

        async def mock_get_db():
            return object()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "AliyunWebSearch", return_value=_MediaTagSearch()), patch.object(
                feeds_module, "get_authority_classifier", return_value=_DummyClassifier()
            ), patch.object(
                feeds_module,
                "resolve_attention_policy",
                AsyncMock(return_value=SimpleNamespace(execution_policy={})),
            ), patch.object(
                feeds_module,
                "apply_attention_policy",
                return_value=SimpleNamespace(
                    policy_id="source-latest-v1",
                    policy_version=1,
                    portfolio_summary={"decision_status": "accepted", "topic_profile": "latest_intelligence"},
                    selected=[],
                ),
            ) as mock_apply:
                def _selected_candidates(*args, **kwargs):
                    payloads = args[2]
                    return SimpleNamespace(
                        policy_id="source-latest-v1",
                        policy_version=1,
                        portfolio_summary={"decision_status": "accepted", "topic_profile": "latest_intelligence"},
                        selected=payloads,
                    )

                mock_apply.side_effect = _selected_candidates

                response = self.client.post(
                    "/api/sources/discover",
                    json={
                        "topic": "agent media topic pages",
                        "focus": "latest",
                        "task_intent": "keep contextual media tag page out of article signal path",
                        "interest_bias": "community",
                        "limit": 6,
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data["candidates"]), 1)
            candidate = data["candidates"][0]
            self.assertEqual(candidate["item_type"], "domain")
            self.assertEqual(candidate["object_key"], "36kr.com")
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_latest_focus_keeps_social_person_seed_weak(self):
        from db import get_db

        class _XStatusSearch:
            ENGINE_ADVANCED = "advanced"
            TIME_ONE_MONTH = "month"
            TIME_NO_LIMIT = "all"

            def search(self, *args, **kwargs):
                return {
                    "success": True,
                    "results": [
                        SimpleNamespace(
                            link="https://x.com/openclaw/status/123456",
                            source="x.com",
                            title="OpenClaw roadmap update",
                            snippet="Latest project update and release timing",
                            main_text="Latest project update and release timing",
                        ),
                    ],
                }

        async def mock_get_db():
            return object()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "AliyunWebSearch", return_value=_XStatusSearch()), patch.object(
                feeds_module, "get_authority_classifier", return_value=_DummyClassifier()
            ), patch.object(
                feeds_module,
                "resolve_attention_policy",
                AsyncMock(return_value=SimpleNamespace(execution_policy={})),
            ), patch.object(
                feeds_module,
                "apply_attention_policy",
                return_value=SimpleNamespace(
                    policy_id="source-latest-v1",
                    policy_version=1,
                    portfolio_summary={"decision_status": "accepted", "topic_profile": "latest_intelligence"},
                    selected=[],
                ),
            ) as mock_apply:
                def _selected_candidates(*args, **kwargs):
                    payloads = args[2]
                    person_payloads = [payload for payload in payloads if payload.get("item_type") == "person"]
                    return SimpleNamespace(
                        policy_id="source-latest-v1",
                        policy_version=1,
                        portfolio_summary={"decision_status": "accepted", "topic_profile": "latest_intelligence"},
                        selected=person_payloads[:1],
                    )

                mock_apply.side_effect = _selected_candidates

                response = self.client.post(
                    "/api/sources/discover",
                    json={
                        "topic": "openclaw latest updates",
                        "focus": "latest",
                        "task_intent": "watch latest social updates without actor escalation",
                        "interest_bias": "community",
                        "limit": 6,
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data["candidates"]), 1)
            candidate = data["candidates"][0]
            self.assertEqual(candidate["item_type"], "person")
            self.assertEqual(candidate["object_key"], "x.com/openclaw")
            self.assertEqual(candidate["inferred_roles"], [])
            self.assertLessEqual(candidate["follow_score"], 0.04)
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_discover_seeds_person_candidate_from_twitter_status_signal(self):
        from db import get_db

        class _TwitterStatusSearch:
            ENGINE_ADVANCED = "advanced"
            TIME_ONE_MONTH = "month"
            TIME_NO_LIMIT = "all"

            def search(self, *args, **kwargs):
                return {
                    "success": True,
                    "results": [
                        SimpleNamespace(
                            link="https://twitter.com/openclaw/status/987654",
                            source="twitter.com",
                            title="OpenClaw builder shared implementation note",
                            snippet="Builder explains the latest implementation direction",
                            main_text="Builder explains the latest implementation direction",
                        ),
                    ],
                }

        async def mock_get_db():
            return object()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "AliyunWebSearch", return_value=_TwitterStatusSearch()), patch.object(
                feeds_module, "get_authority_classifier", return_value=_DummyClassifier()
            ), patch.object(
                feeds_module,
                "resolve_attention_policy",
                AsyncMock(return_value=SimpleNamespace(execution_policy={})),
            ), patch.object(
                feeds_module,
                "apply_attention_policy",
                return_value=SimpleNamespace(
                    policy_id="source-method-v1",
                    policy_version=1,
                    portfolio_summary={"decision_status": "accepted", "topic_profile": "tool_project"},
                    selected=[],
                ),
            ) as mock_apply:
                def _selected_candidates(*args, **kwargs):
                    payloads = args[2]
                    person_payloads = [payload for payload in payloads if payload.get("item_type") == "person"]
                    signal_payloads = [payload for payload in payloads if payload.get("item_type") == "signal"]
                    return SimpleNamespace(
                        policy_id="source-method-v1",
                        policy_version=1,
                        portfolio_summary={"decision_status": "accepted", "topic_profile": "tool_project"},
                        selected=[*person_payloads[:1], *signal_payloads[:1]],
                    )

                mock_apply.side_effect = _selected_candidates

                response = self.client.post(
                    "/api/sources/discover",
                    json={
                        "topic": "openclaw builder activity",
                        "focus": "method",
                        "task_intent": "surface builder actors from twitter signal",
                        "interest_bias": "method",
                        "limit": 6,
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            person_candidates = [candidate for candidate in data["candidates"] if candidate["item_type"] == "person"]
            signal_candidates = [candidate for candidate in data["candidates"] if candidate["item_type"] == "signal"]
            self.assertTrue(person_candidates)
            self.assertTrue(signal_candidates)
            self.assertEqual(person_candidates[0]["object_key"], "twitter.com/openclaw")
            self.assertIn("builder", person_candidates[0]["inferred_roles"])
            self.assertEqual(person_candidates[0]["related_entities"][0]["item_type"], "signal")
            self.assertEqual(person_candidates[0]["related_entities"][0]["object_key"], "twitter.com/openclaw/status/987654")
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_plan_creation_preserves_discovery_context(self):
        from db import get_db

        class _MockScalarResult:
            def __init__(self, value):
                self._value = value

            def unique(self):
                return self

            def all(self):
                return self._value

            def one(self):
                return self._value

        class _MockDB:
            def __init__(self):
                self.added = []
                self.persisted_plan = None
                self.execute_calls = 0

            async def execute(self, statement):
                self.execute_calls += 1
                if self.execute_calls == 1:
                    return SimpleNamespace(scalars=lambda: _MockScalarResult([]))
                return SimpleNamespace(scalars=lambda: _MockScalarResult(self.persisted_plan))

            def add(self, instance):
                self.added.append(instance)
                if instance.__class__.__name__ == "SourcePlan":
                    self.persisted_plan = instance

            async def flush(self):
                for instance in self.added:
                    if getattr(instance, "id", None) is None:
                        instance.id = uuid4()
                if self.persisted_plan is not None and getattr(self.persisted_plan, "items", None) is None:
                    self.persisted_plan.items = []

            async def commit(self):
                if self.persisted_plan is not None:
                    self.persisted_plan.items = [
                        instance
                        for instance in self.added
                        if instance.__class__.__name__ == "SourcePlanItem"
                    ]
                return None

        async def mock_get_db():
            return _MockDB()

        discovery = feeds_module.SourceDiscoveryResponse(
            topic="agent harness patterns",
            focus=feeds_module.SourceDiscoveryFocus.METHOD,
            task_intent="prepare source plan",
            interest_bias=feeds_module.SourceDiscoveryInterestBias.METHOD,
            queries=["agent harness patterns github repository"],
            policy_id="source-method-v1",
            policy_version=1,
            portfolio_summary={"decision_status": "accepted"},
            notes=["task_intent=prepare source plan"],
            truth_boundary=["candidate discovery is inspect output, not canonical source truth"],
            candidates=[
                feeds_module.SourceDiscoveryCandidate(
                    item_type="repository",
                    object_key="github.com/openclaw/openclaw",
                    domain="github.com",
                    name="openclaw/openclaw",
                    url="https://github.com/openclaw/openclaw",
                    authority_tier="A",
                    authority_score=0.82,
                    recommendation="subscribe",
                    recommendation_reason="strong method artifact",
                    evidence_count=3,
                    matched_queries=["agent harness patterns github repository"],
                    sample_titles=["OpenClaw repository"],
                    sample_snippets=["OpenClaw coding agent repository and releases"],
                    recommended_execution_strategy="agent_assisted",
                )
            ],
        )

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(feeds_module, "_run_source_discovery", AsyncMock(return_value=discovery)):
                response = self.client.post(
                    "/api/sources/plans",
                    json={
                        "topic": "agent harness patterns",
                        "focus": "method",
                        "objective": "build a reusable monitoring plan",
                        "task_intent": "prepare source plan",
                        "interest_bias": "method",
                        "limit": 6,
                        "review_cadence_days": 14,
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["topic"], "agent harness patterns")
            self.assertEqual(data["focus"], "method")
            self.assertEqual(data["task_intent"], "prepare source plan")
            self.assertEqual(data["interest_bias"], "method")
            self.assertEqual(data["discovery_notes"], ["task_intent=prepare source plan"])
            self.assertEqual(
                data["discovery_truth_boundary"],
                ["candidate discovery is inspect output, not canonical source truth"],
            )
            self.assertEqual(len(data["items"]), 1)
            self.assertEqual(data["items"][0]["object_key"], "github.com/openclaw/openclaw")
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_plan_refresh_returns_preserved_discovery_context(self):
        from db import get_db

        class _MockScalarResult:
            def __init__(self, value):
                self._value = value

            def unique(self):
                return self

            def one_or_none(self):
                return self._value

        persisted_plan = SimpleNamespace(
            id=uuid4(),
            topic="agent harness patterns",
            focus="method",
            objective="build a reusable monitoring plan",
            planning_brain="source-intelligence-brain",
            status="active",
            review_status="accepted",
            review_cadence_days=14,
            current_version=2,
            latest_version=2,
            extra={
                "task_intent": "refresh source plan",
                "interest_bias": "method",
                "discovery_notes": ["task_intent=refresh source plan"],
                "discovery_truth_boundary": ["candidate discovery is inspect output, not canonical source truth"],
                "attention_policy": {
                    "policy_id": "source-method-v1",
                    "policy_version": 1,
                    "policy_name": "Method",
                },
                "latest_evaluation": {"decision_status": "accepted"},
            },
            items=[
                SimpleNamespace(
                    id=uuid4(),
                    item_type="repository",
                    object_key="github.com/openclaw/openclaw",
                    name="openclaw/openclaw",
                    url="https://github.com/openclaw/openclaw",
                    authority_tier="A",
                    authority_score=0.82,
                    monitoring_mode="subscribe",
                    execution_strategy="agent_assisted",
                    review_cadence_days=14,
                    rationale="strong method artifact",
                    status="active",
                    evidence={},
                )
            ],
            created_at=None,
            updated_at=None,
        )

        class _MockDB:
            async def execute(self, statement):
                return SimpleNamespace(scalars=lambda: _MockScalarResult(persisted_plan))

        async def mock_get_db():
            return _MockDB()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(
                feeds_module,
                "_apply_source_plan_refresh",
                AsyncMock(return_value=persisted_plan),
            ) as mock_refresh:
                response = self.client.post(
                    f"/api/sources/plans/{persisted_plan.id}/refresh",
                    params={"limit": 8, "trigger_type": "manual_refresh"},
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["topic"], "agent harness patterns")
            self.assertEqual(data["focus"], "method")
            self.assertEqual(data["task_intent"], "refresh source plan")
            self.assertEqual(data["interest_bias"], "method")
            self.assertEqual(data["discovery_notes"], ["task_intent=refresh source plan"])
            self.assertEqual(
                data["discovery_truth_boundary"],
                ["candidate discovery is inspect output, not canonical source truth"],
            )
            mock_refresh.assert_awaited_once()
            self.assertEqual(mock_refresh.await_args.kwargs["limit"], 8)
            self.assertEqual(mock_refresh.await_args.kwargs["trigger_type"], "manual_refresh")
        finally:
            test_app.dependency_overrides.clear()

    def test_source_intelligence_m2_loop_reuses_existing_m1_path(self):
        from db import get_db

        class _MockScalarResult:
            def __init__(self, value):
                self._value = value

            def unique(self):
                return self

            def all(self):
                return self._value

            def one(self):
                return self._value

            def one_or_none(self):
                return self._value

        class _LoopDB:
            def __init__(self):
                self.added = []
                self.persisted_plan = None
                self.versions = []
                self.execute_calls = 0

            async def execute(self, statement):
                self.execute_calls += 1
                if self.execute_calls == 1:
                    return SimpleNamespace(scalars=lambda: _MockScalarResult([]))
                if self.execute_calls == 2:
                    return SimpleNamespace(scalars=lambda: _MockScalarResult(self.persisted_plan))
                if self.execute_calls == 3:
                    return SimpleNamespace(scalars=lambda: _MockScalarResult(self.persisted_plan))
                return SimpleNamespace(scalars=lambda: _MockScalarResult(self.versions))

            def add(self, instance):
                self.added.append(instance)
                if instance.__class__.__name__ == "SourcePlan":
                    self.persisted_plan = instance

            async def flush(self):
                for instance in self.added:
                    if getattr(instance, "id", None) is None:
                        instance.id = uuid4()
                if self.persisted_plan is not None and getattr(self.persisted_plan, "items", None) is None:
                    self.persisted_plan.items = []

            async def commit(self):
                if self.persisted_plan is not None:
                    self.persisted_plan.items = [
                        instance
                        for instance in self.added
                        if instance.__class__.__name__ == "SourcePlanItem"
                    ]
                return None

        loop_db = _LoopDB()

        async def mock_get_db():
            return loop_db

        initial_discovery = feeds_module.SourceDiscoveryResponse(
            topic="agent harness patterns",
            focus=feeds_module.SourceDiscoveryFocus.METHOD,
            task_intent="run real discovery loop",
            interest_bias=feeds_module.SourceDiscoveryInterestBias.METHOD,
            queries=["agent harness patterns github repository"],
            policy_id="source-method-v1",
            policy_version=1,
            portfolio_summary={"decision_status": "accepted"},
            notes=["initial loop run through M1 path"],
            truth_boundary=["candidate discovery is inspect output, not canonical source truth"],
            candidates=[
                feeds_module.SourceDiscoveryCandidate(
                    item_type="repository",
                    object_key="github.com/openclaw/openclaw",
                    domain="github.com",
                    name="openclaw/openclaw",
                    url="https://github.com/openclaw/openclaw",
                    authority_tier="A",
                    authority_score=0.82,
                    recommendation="subscribe",
                    recommendation_reason="strong method artifact",
                    evidence_count=3,
                    matched_queries=["agent harness patterns github repository"],
                    sample_titles=["OpenClaw repository"],
                    sample_snippets=["OpenClaw coding agent repository and releases"],
                    recommended_execution_strategy="agent_assisted",
                )
            ],
        )

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(
                feeds_module,
                "_run_source_discovery",
                AsyncMock(return_value=initial_discovery),
            ):
                create_response = self.client.post(
                    "/api/sources/plans",
                    json={
                        "topic": "agent harness patterns",
                        "focus": "method",
                        "objective": "run one bounded source-intelligence loop",
                        "task_intent": "run real discovery loop",
                        "interest_bias": "method",
                        "limit": 6,
                        "review_cadence_days": 14,
                    },
                )

            self.assertEqual(create_response.status_code, 200)
            created = create_response.json()
            plan_id = created["id"]
            self.assertEqual(created["task_intent"], "run real discovery loop")
            self.assertEqual(created["items"][0]["object_key"], "github.com/openclaw/openclaw")

            created_version = SimpleNamespace(
                id=uuid4(),
                version_number=1,
                parent_version=None,
                trigger_type="initial_create",
                decision_status="accepted",
                plan_snapshot={
                    "topic": "agent harness patterns",
                    "focus": "method",
                    "task_intent": "run real discovery loop",
                    "interest_bias": "method",
                    "discovery_notes": ["initial loop run through M1 path"],
                    "discovery_truth_boundary": ["candidate discovery is inspect output, not canonical source truth"],
                },
                change_reason="Initial source plan created from topic-driven discovery.",
                change_summary={"summary": {"previous_item_count": 0, "current_item_count": 1}},
                evaluation={"decision_status": "accepted", "confidence": 1.0},
                created_by="system",
                accepted_at=None,
                created_at=None,
            )

            async def _fake_refresh(db, plan, limit, trigger_type, change_reason):
                plan.current_version = 2
                plan.latest_version = 2
                plan.review_status = "accepted"
                plan.extra = {
                    **dict(plan.extra or {}),
                    "task_intent": "run real discovery loop",
                    "interest_bias": "method",
                    "discovery_notes": ["refresh loop confirmed repository remains useful"],
                    "discovery_truth_boundary": ["candidate discovery is inspect output, not canonical source truth"],
                    "latest_evaluation": {
                        "decision_status": "accepted",
                        "confidence": 0.84,
                        "gate_signals": {"average_score_delta": 0.04, "evidence_delta": 1},
                    },
                }
                loop_db.versions = [
                    SimpleNamespace(
                        id=uuid4(),
                        version_number=2,
                        parent_version=1,
                        trigger_type=trigger_type,
                        decision_status="accepted",
                        plan_snapshot={
                            "topic": "agent harness patterns",
                            "focus": "method",
                            "task_intent": "run real discovery loop",
                            "interest_bias": "method",
                            "discovery_notes": ["refresh loop confirmed repository remains useful"],
                            "discovery_truth_boundary": ["candidate discovery is inspect output, not canonical source truth"],
                        },
                        change_reason=change_reason,
                        change_summary={"summary": {"previous_item_count": 1, "current_item_count": 1, "average_score_delta": 0.04, "evidence_delta": 1}},
                        evaluation={
                            "decision_status": "accepted",
                            "confidence": 0.84,
                            "gate_signals": {"average_score_delta": 0.04, "evidence_delta": 1},
                        },
                        created_by="system",
                        accepted_at=None,
                        created_at=None,
                    ),
                    created_version,
                ]
                return plan

            with patch.object(
                feeds_module,
                "_apply_source_plan_refresh",
                AsyncMock(side_effect=_fake_refresh),
            ):
                refresh_response = self.client.post(
                    f"/api/sources/plans/{plan_id}/refresh",
                    params={"limit": 6, "trigger_type": "manual_refresh"},
                )

            self.assertEqual(refresh_response.status_code, 200)
            refreshed = refresh_response.json()
            self.assertEqual(refreshed["current_version"], 2)
            self.assertEqual(
                refreshed["discovery_notes"],
                ["refresh loop confirmed repository remains useful"],
            )

            versions_response = self.client.get(f"/api/sources/plans/{plan_id}/versions")
            self.assertEqual(versions_response.status_code, 200)
            versions = versions_response.json()
            self.assertEqual([item["version_number"] for item in versions], [2, 1])
            self.assertEqual(versions[0]["evaluation"]["decision_status"], "accepted")
            self.assertEqual(
                versions[0]["change_summary"]["summary"]["average_score_delta"],
                0.04,
            )
            self.assertEqual(
                versions[1]["discovery_notes"],
                ["initial loop run through M1 path"],
            )
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_plan_versions_expose_bounded_context_summary(self):
        from db import get_db

        class _MockScalarResult:
            def __init__(self, value):
                self._value = value

            def unique(self):
                return self

            def all(self):
                return self._value

        plan_id = uuid4()
        version = SimpleNamespace(
            id=uuid4(),
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
            change_summary={
                "summary": {
                    "previous_item_count": 1,
                    "current_item_count": 1,
                    "average_score_delta": 0.04,
                    "evidence_delta": 1,
                }
            },
            evaluation={
                "decision_status": "accepted",
                "confidence": 0.8,
                "gate_signals": {
                    "largest_score_drop": 0.0,
                    "average_score_delta": 0.04,
                    "evidence_delta": 1,
                    "trusted_count_delta": 0,
                    "authority_regression_count": 0,
                    "stale_count": 0,
                    "removed_count": 0,
                },
            },
            created_by="system",
            accepted_at=None,
            created_at=None,
        )

        class _MockDB:
            async def execute(self, statement):
                return SimpleNamespace(scalars=lambda: _MockScalarResult([version]))

        async def mock_get_db():
            return _MockDB()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            response = self.client.get(f"/api/sources/plans/{plan_id}/versions")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data), 1)
            item = data[0]
            self.assertEqual(item["version_number"], 2)
            self.assertEqual(item["topic"], "agent harness patterns")
            self.assertEqual(item["focus"], "method")
            self.assertEqual(item["task_intent"], "refresh source plan")
            self.assertEqual(item["interest_bias"], "method")
            self.assertEqual(item["discovery_notes"], ["task_intent=refresh source plan"])
            self.assertEqual(
                item["discovery_truth_boundary"],
                ["candidate discovery is inspect output, not canonical source truth"],
            )
            self.assertEqual(item["change_summary"]["summary"]["average_score_delta"], 0.04)
            self.assertEqual(item["evaluation"]["decision_status"], "accepted")
            self.assertEqual(item["evaluation"]["gate_signals"]["evidence_delta"], 1)
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_plan_versions_preserve_repeated_refresh_evaluation_order(self):
        from db import get_db

        class _MockScalarResult:
            def __init__(self, value):
                self._value = value

            def all(self):
                return self._value

        plan_id = uuid4()
        newer = SimpleNamespace(
            id=uuid4(),
            version_number=3,
            parent_version=2,
            trigger_type="manual_refresh",
            decision_status="accepted",
            plan_snapshot={
                "topic": "agent harness patterns",
                "focus": "method",
                "task_intent": "refresh source plan",
                "interest_bias": "method",
            },
            change_reason="refresh accepted",
            change_summary={"summary": {"average_score_delta": 0.03, "evidence_delta": 2}},
            evaluation={
                "decision_status": "accepted",
                "confidence": 0.82,
                "gate_signals": {"average_score_delta": 0.03, "evidence_delta": 2},
            },
            created_by="system",
            accepted_at=None,
            created_at=None,
        )
        older = SimpleNamespace(
            id=uuid4(),
            version_number=2,
            parent_version=1,
            trigger_type="manual_refresh",
            decision_status="needs_review",
            plan_snapshot={
                "topic": "agent harness patterns",
                "focus": "method",
                "task_intent": "refresh source plan",
                "interest_bias": "method",
            },
            change_reason="refresh degraded",
            change_summary={"summary": {"average_score_delta": -0.16, "evidence_delta": -1}},
            evaluation={
                "decision_status": "needs_review",
                "confidence": 0.45,
                "gate_signals": {"average_score_delta": -0.16, "evidence_delta": -1},
            },
            created_by="system",
            accepted_at=None,
            created_at=None,
        )

        class _MockDB:
            async def execute(self, statement):
                return SimpleNamespace(scalars=lambda: _MockScalarResult([newer, older]))

        async def mock_get_db():
            return _MockDB()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            response = self.client.get(f"/api/sources/plans/{plan_id}/versions")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual([item["version_number"] for item in data], [3, 2])
            self.assertEqual(data[0]["evaluation"]["decision_status"], "accepted")
            self.assertEqual(data[0]["change_summary"]["summary"]["evidence_delta"], 2)
            self.assertEqual(data[1]["evaluation"]["decision_status"], "needs_review")
            self.assertEqual(data[1]["change_summary"]["summary"]["average_score_delta"], -0.16)
            self.assertEqual(data[1]["discovery_notes"], [])
            self.assertEqual(data[1]["discovery_truth_boundary"], [])
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_plan_versions_preserve_sparse_repeated_refresh_defaults(self):
        from db import get_db

        class _MockScalarResult:
            def __init__(self, value):
                self._value = value

            def all(self):
                return self._value

        plan_id = uuid4()
        newest = SimpleNamespace(
            id=uuid4(),
            version_number=4,
            parent_version=3,
            trigger_type="manual_refresh",
            decision_status="accepted",
            plan_snapshot={
                "topic": "agent harness patterns",
                "focus": "method",
                "task_intent": "refresh source plan",
                "interest_bias": "method",
                "discovery_notes": ["latest pass improved evidence"],
                "discovery_truth_boundary": ["candidate discovery is inspect output, not canonical source truth"],
            },
            change_reason="refresh accepted",
            change_summary={"summary": {"average_score_delta": 0.05, "evidence_delta": 3}},
            evaluation={
                "decision_status": "accepted",
                "confidence": 0.86,
                "gate_signals": {"average_score_delta": 0.05, "evidence_delta": 3},
            },
            created_by="system",
            accepted_at=None,
            created_at=None,
        )
        middle = SimpleNamespace(
            id=uuid4(),
            version_number=3,
            parent_version=2,
            trigger_type="manual_refresh",
            decision_status="needs_review",
            plan_snapshot={
                "topic": "agent harness patterns",
                "focus": "method",
                "task_intent": "refresh source plan",
                "interest_bias": "method",
            },
            change_reason="refresh partial",
            change_summary=None,
            evaluation=None,
            created_by="system",
            accepted_at=None,
            created_at=None,
        )
        older = SimpleNamespace(
            id=uuid4(),
            version_number=2,
            parent_version=1,
            trigger_type="manual_refresh",
            decision_status="needs_review",
            plan_snapshot={
                "topic": "agent harness patterns",
                "focus": "method",
                "task_intent": "refresh source plan",
                "interest_bias": "method",
            },
            change_reason="refresh degraded",
            change_summary={"summary": {"average_score_delta": -0.1, "evidence_delta": -1}},
            evaluation={
                "decision_status": "needs_review",
                "confidence": 0.41,
                "gate_signals": {"average_score_delta": -0.1, "evidence_delta": -1},
            },
            created_by="system",
            accepted_at=None,
            created_at=None,
        )

        class _MockDB:
            async def execute(self, statement):
                return SimpleNamespace(scalars=lambda: _MockScalarResult([newest, middle, older]))

        async def mock_get_db():
            return _MockDB()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            response = self.client.get(f"/api/sources/plans/{plan_id}/versions")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual([item["version_number"] for item in data], [4, 3, 2])
            self.assertEqual(data[0]["evaluation"]["decision_status"], "accepted")
            self.assertEqual(data[1]["change_summary"], {})
            self.assertEqual(data[1]["evaluation"], {})
            self.assertEqual(data[1]["discovery_notes"], [])
            self.assertEqual(data[1]["discovery_truth_boundary"], [])
            self.assertEqual(data[2]["evaluation"]["decision_status"], "needs_review")
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_plan_versions_allow_latest_sparse_refresh_snapshot(self):
        from db import get_db

        class _MockScalarResult:
            def __init__(self, value):
                self._value = value

            def all(self):
                return self._value

        plan_id = uuid4()
        newest = SimpleNamespace(
            id=uuid4(),
            version_number=5,
            parent_version=4,
            trigger_type="manual_refresh",
            decision_status="needs_review",
            plan_snapshot={
                "topic": "agent harness patterns",
                "focus": "method",
                "task_intent": "refresh source plan",
                "interest_bias": "method",
            },
            change_reason="refresh pending evaluation materialization",
            change_summary=None,
            evaluation=None,
            created_by="system",
            accepted_at=None,
            created_at=None,
        )
        older = SimpleNamespace(
            id=uuid4(),
            version_number=4,
            parent_version=3,
            trigger_type="manual_refresh",
            decision_status="accepted",
            plan_snapshot={
                "topic": "agent harness patterns",
                "focus": "method",
                "task_intent": "refresh source plan",
                "interest_bias": "method",
                "discovery_notes": ["prior refresh improved evidence"],
                "discovery_truth_boundary": ["candidate discovery is inspect output, not canonical source truth"],
            },
            change_reason="refresh accepted",
            change_summary={"summary": {"average_score_delta": 0.06, "evidence_delta": 2}},
            evaluation={
                "decision_status": "accepted",
                "confidence": 0.84,
                "gate_signals": {"average_score_delta": 0.06, "evidence_delta": 2},
            },
            created_by="system",
            accepted_at=None,
            created_at=None,
        )

        class _MockDB:
            async def execute(self, statement):
                return SimpleNamespace(scalars=lambda: _MockScalarResult([newest, older]))

        async def mock_get_db():
            return _MockDB()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            response = self.client.get(f"/api/sources/plans/{plan_id}/versions")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual([item["version_number"] for item in data], [5, 4])
            self.assertEqual(data[0]["decision_status"], "needs_review")
            self.assertEqual(data[0]["change_summary"], {})
            self.assertEqual(data[0]["evaluation"], {})
            self.assertEqual(data[0]["discovery_notes"], [])
            self.assertEqual(data[0]["discovery_truth_boundary"], [])
            self.assertEqual(data[1]["evaluation"]["decision_status"], "accepted")
            self.assertEqual(data[1]["change_summary"]["summary"]["evidence_delta"], 2)
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_plan_versions_allow_uniform_needs_review_history(self):
        from db import get_db

        class _MockScalarResult:
            def __init__(self, value):
                self._value = value

            def all(self):
                return self._value

        plan_id = uuid4()
        newest = SimpleNamespace(
            id=uuid4(),
            version_number=6,
            parent_version=5,
            trigger_type="manual_refresh",
            decision_status="needs_review",
            plan_snapshot={
                "topic": "agent harness patterns",
                "focus": "method",
                "task_intent": "refresh source plan",
                "interest_bias": "method",
            },
            change_reason="refresh remained weak",
            change_summary={"summary": {"average_score_delta": -0.02, "evidence_delta": 0}},
            evaluation={
                "decision_status": "needs_review",
                "confidence": 0.49,
                "gate_signals": {"average_score_delta": -0.02, "evidence_delta": 0},
            },
            created_by="system",
            accepted_at=None,
            created_at=None,
        )
        older = SimpleNamespace(
            id=uuid4(),
            version_number=5,
            parent_version=4,
            trigger_type="manual_refresh",
            decision_status="needs_review",
            plan_snapshot={
                "topic": "agent harness patterns",
                "focus": "method",
                "task_intent": "refresh source plan",
                "interest_bias": "method",
            },
            change_reason="refresh also weak",
            change_summary={"summary": {"average_score_delta": -0.04, "evidence_delta": -1}},
            evaluation={
                "decision_status": "needs_review",
                "confidence": 0.42,
                "gate_signals": {"average_score_delta": -0.04, "evidence_delta": -1},
            },
            created_by="system",
            accepted_at=None,
            created_at=None,
        )

        class _MockDB:
            async def execute(self, statement):
                return SimpleNamespace(scalars=lambda: _MockScalarResult([newest, older]))

        async def mock_get_db():
            return _MockDB()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            response = self.client.get(f"/api/sources/plans/{plan_id}/versions")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual([item["version_number"] for item in data], [6, 5])
            self.assertEqual(data[0]["evaluation"]["decision_status"], "needs_review")
            self.assertEqual(data[1]["evaluation"]["decision_status"], "needs_review")
            self.assertEqual(data[0]["change_summary"]["summary"]["average_score_delta"], -0.02)
            self.assertEqual(data[1]["change_summary"]["summary"]["evidence_delta"], -1)
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_plan_version_judge_inspect_returns_advisory_refresh_change_judgment(self):
        from db import get_db

        async def mock_get_db():
            return object()

        version = feeds_module.SourcePlanVersionResponse(
            id="version-7",
            version_number=7,
            parent_version=6,
            trigger_type="manual_refresh",
            decision_status="needs_review",
            topic="agent harness patterns",
            focus="method",
            task_intent="keep source plan high-signal",
            interest_bias="method",
            change_reason="refresh weakened one core repository and added a noisy thread",
            change_summary={
                "summary": {"removed_count": 1, "stale_count": 1, "average_score_delta": -0.04},
                "removed": ["github.com/openclaw/openclaw"],
                "stale": ["reddit.com/r/machinelearning/comments/abc123"],
            },
            evaluation={
                "decision_status": "needs_review",
                "confidence": 0.46,
                "gate_signals": {"removed_count": 1, "stale_count": 1},
            },
            created_by="source_intelligence_v1",
        )
        judged_targets = [
            feeds_module.SourcePlanVersionJudgmentTarget(
                object_key="github.com/openclaw/openclaw",
                item_type="repository",
                name="openclaw/openclaw",
                url="https://github.com/openclaw/openclaw",
                status="removed",
                authority_tier="A",
                authority_score=0.82,
                change_type="removed",
                score_delta=-0.22,
                evidence_count=4,
            ),
            feeds_module.SourcePlanVersionJudgmentTarget(
                object_key="reddit.com/r/machinelearning/comments/abc123",
                item_type="signal",
                name="discussion thread",
                url="https://reddit.com/r/machinelearning/comments/abc123",
                status="stale",
                authority_tier="B",
                authority_score=0.58,
                change_type="stale",
                score_delta=-0.07,
                evidence_count=2,
            ),
        ]
        snapshot_items = [
            {
                "object_key": target.object_key,
                "item_type": target.item_type,
                "name": target.name,
                "url": target.url,
                "status": target.status,
                "authority_tier": target.authority_tier,
                "authority_score": target.authority_score,
                "evidence": {"evidence_count": target.evidence_count},
            }
            for target in judged_targets
        ]

        class _DummyAdapter:
            async def chat(self, *args, **kwargs):
                return """
                {
                  "summary": "repo removal is the main follow-up item",
                  "judgments": [
                    {
                      "object_key": "github.com/openclaw/openclaw",
                      "verdict": "review",
                      "rationale": "core object removal deserves immediate inspection",
                      "confidence": 0.88,
                      "review_priority": "high"
                    },
                    {
                      "object_key": "reddit.com/r/machinelearning/comments/abc123",
                      "verdict": "ignore",
                      "rationale": "stale thread is lower-value noise",
                      "confidence": 0.63,
                      "review_priority": "low"
                    }
                  ]
                }
                """

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(
                feeds_module,
                "_load_source_plan_version_judgment_context",
                AsyncMock(return_value=(version, snapshot_items)),
            ), patch.object(
                feeds_module,
                "_build_source_plan_version_judgment_targets",
                return_value=judged_targets,
            ), patch.object(feeds_module, "LLMAdapter", return_value=_DummyAdapter()):
                response = self.client.post(
                    "/api/sources/plans/plan-123/versions/7/judge/inspect",
                    json={"provider": "anthropic", "model": "", "max_candidates": 2},
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["plan_id"], "plan-123")
            self.assertEqual(data["version_number"], 7)
            self.assertEqual(data["provider"], "anthropic")
            self.assertEqual(data["model"], "claude-3-5-sonnet-20241022")
            self.assertEqual(data["summary"], "repo removal is the main follow-up item")
            self.assertEqual(len(data["judged_targets"]), 2)
            self.assertEqual(data["judgments"][0]["object_key"], "github.com/openclaw/openclaw")
            self.assertEqual(data["judgments"][0]["verdict"], "review")
            self.assertIn("ai_judgment_parse_status=valid_json", data["notes"])
            self.assertIn("plan-version inspect judges refresh-change targets", " ".join(data["truth_boundary"]))
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_plan_version_judge_inspect_returns_404_when_version_missing(self):
        from db import get_db

        async def mock_get_db():
            return object()

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(
                feeds_module,
                "_load_source_plan_version_judgment_context",
                AsyncMock(side_effect=feeds_module.HTTPException(status_code=404, detail="Source plan version not found")),
            ):
                response = self.client.post(
                    "/api/sources/plans/plan-404/versions/99/judge/inspect",
                    json={"provider": "qwen", "model": "", "max_candidates": 2},
                )

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json()["detail"], "Source plan version not found")
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_plan_version_judge_panel_inspect_exposes_agreement_shape(self):
        from db import get_db

        async def mock_get_db():
            return object()

        version = feeds_module.SourcePlanVersionResponse(
            id="version-8",
            version_number=8,
            parent_version=7,
            trigger_type="manual_refresh",
            decision_status="needs_review",
            topic="agent harness patterns",
            focus="method",
            task_intent="compare model judgment over version changes",
            interest_bias="method",
            change_reason="refresh weakened one core repository and one thread",
            change_summary={
                "summary": {"removed_count": 1, "stale_count": 1},
                "removed": ["github.com/openclaw/openclaw"],
                "stale": ["reddit.com/r/machinelearning/comments/abc123"],
            },
            evaluation={
                "decision_status": "needs_review",
                "confidence": 0.44,
                "gate_signals": {"removed_count": 1, "stale_count": 1},
            },
            created_by="source_intelligence_v1",
        )
        judged_targets = [
            feeds_module.SourcePlanVersionJudgmentTarget(
                object_key="github.com/openclaw/openclaw",
                item_type="repository",
                name="openclaw/openclaw",
                url="https://github.com/openclaw/openclaw",
                status="removed",
                authority_tier="A",
                authority_score=0.82,
                change_type="removed",
                score_delta=-0.22,
                evidence_count=4,
            ),
            feeds_module.SourcePlanVersionJudgmentTarget(
                object_key="reddit.com/r/machinelearning/comments/abc123",
                item_type="signal",
                name="discussion thread",
                url="https://reddit.com/r/machinelearning/comments/abc123",
                status="stale",
                authority_tier="B",
                authority_score=0.58,
                change_type="stale",
                score_delta=-0.07,
                evidence_count=2,
            ),
        ]
        snapshot_items = [
            {
                "object_key": target.object_key,
                "item_type": target.item_type,
                "name": target.name,
                "url": target.url,
                "status": target.status,
                "authority_tier": target.authority_tier,
                "authority_score": target.authority_score,
                "evidence": {"evidence_count": target.evidence_count},
            }
            for target in judged_targets
        ]

        class _DummyAdapter:
            def __init__(self):
                self.chat = AsyncMock(
                    side_effect=[
                        """
                        {
                          "summary": "primary prefers reviewing both targets",
                          "judgments": [
                            {
                              "object_key": "github.com/openclaw/openclaw",
                              "verdict": "review",
                              "rationale": "core removal deserves inspection",
                              "confidence": 0.91,
                              "review_priority": "high"
                            },
                            {
                              "object_key": "reddit.com/r/machinelearning/comments/abc123",
                              "verdict": "review",
                              "rationale": "thread staleness may reflect topic drift",
                              "confidence": 0.55,
                              "review_priority": "normal"
                            }
                          ]
                        }
                        """,
                        """
                        {
                          "summary": "secondary focuses on repo and ignores stale thread",
                          "judgments": [
                            {
                              "object_key": "github.com/openclaw/openclaw",
                              "verdict": "review",
                              "rationale": "repo removal is the main problem",
                              "confidence": 0.86,
                              "review_priority": "high"
                            },
                            {
                              "object_key": "reddit.com/r/machinelearning/comments/abc123",
                              "verdict": "ignore",
                              "rationale": "stale thread is lower-signal noise",
                              "confidence": 0.66,
                              "review_priority": "low"
                            }
                          ]
                        }
                        """,
                    ]
                )

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(
                feeds_module,
                "_load_source_plan_version_judgment_context",
                AsyncMock(return_value=(version, snapshot_items)),
            ), patch.object(
                feeds_module,
                "_build_source_plan_version_judgment_targets",
                return_value=judged_targets,
            ), patch.object(feeds_module, "LLMAdapter", return_value=_DummyAdapter()):
                response = self.client.post(
                    "/api/sources/plans/plan-123/versions/8/judge/panel/inspect",
                    json={
                        "primary_provider": "qwen",
                        "primary_model": "",
                        "secondary_provider": "anthropic",
                        "secondary_model": "",
                        "max_candidates": 2,
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["plan_id"], "plan-123")
            self.assertEqual(data["version_number"], 8)
            self.assertEqual(data["primary_model"], feeds_module.default_model_for_provider("qwen"))
            self.assertEqual(data["secondary_model"], "claude-3-5-sonnet-20241022")
            self.assertEqual(data["panel_summary"]["agreement_count"], 1)
            self.assertEqual(data["panel_summary"]["disagreement_count"], 1)
            self.assertEqual(data["panel_summary"]["panel_signal"], "mixed")
            self.assertEqual(len(data["panel_insights"]["disagreement_worthy"]), 1)
            self.assertIn("selective_absorption", data)
            self.assertEqual(len(data["selective_absorption"]["watch_candidates"]), 0)
            self.assertEqual(len(data["selective_absorption"]["needs_manual_review"]), 1)
            self.assertIn("plan-version panel inspect exposes agreement shape", " ".join(data["truth_boundary"]))
        finally:
            test_app.dependency_overrides.clear()

    def test_sources_plan_version_judge_panel_inspect_marks_invalid_secondary_as_mixed(self):
        from db import get_db

        async def mock_get_db():
            return object()

        version = feeds_module.SourcePlanVersionResponse(
            id="version-9",
            version_number=9,
            parent_version=8,
            trigger_type="manual_refresh",
            decision_status="needs_review",
            topic="agent harness patterns",
            focus="method",
            task_intent="compare model judgment over version changes",
            interest_bias="method",
            change_reason="refresh removed one core repository",
            change_summary={
                "summary": {"removed_count": 1},
                "removed": ["github.com/openclaw/openclaw"],
            },
            evaluation={
                "decision_status": "needs_review",
                "confidence": 0.43,
                "gate_signals": {"removed_count": 1},
            },
            created_by="source_intelligence_v1",
        )
        judged_targets = [
            feeds_module.SourcePlanVersionJudgmentTarget(
                object_key="github.com/openclaw/openclaw",
                item_type="repository",
                name="openclaw/openclaw",
                url="https://github.com/openclaw/openclaw",
                status="removed",
                authority_tier="A",
                authority_score=0.82,
                change_type="removed",
                score_delta=-0.22,
                evidence_count=4,
            )
        ]
        snapshot_items = [
            {
                "object_key": target.object_key,
                "item_type": target.item_type,
                "name": target.name,
                "url": target.url,
                "status": target.status,
                "authority_tier": target.authority_tier,
                "authority_score": target.authority_score,
                "evidence": {"evidence_count": target.evidence_count},
            }
            for target in judged_targets
        ]

        class _DummyAdapter:
            def __init__(self):
                self.chat = AsyncMock(
                    side_effect=[
                        """
                        {
                          "summary": "primary flags the repo removal for review",
                          "judgments": [
                            {
                              "object_key": "github.com/openclaw/openclaw",
                              "verdict": "review",
                              "rationale": "core removal deserves inspection",
                              "confidence": 0.90,
                              "review_priority": "high"
                            }
                          ]
                        }
                        """,
                        "```json\n{bad json}\n```",
                    ]
                )

        test_app.dependency_overrides[get_db] = mock_get_db
        try:
            with patch.object(
                feeds_module,
                "_load_source_plan_version_judgment_context",
                AsyncMock(return_value=(version, snapshot_items)),
            ), patch.object(
                feeds_module,
                "_build_source_plan_version_judgment_targets",
                return_value=judged_targets,
            ), patch.object(feeds_module, "LLMAdapter", return_value=_DummyAdapter()):
                response = self.client.post(
                    "/api/sources/plans/plan-123/versions/9/judge/panel/inspect",
                    json={
                        "primary_provider": "qwen",
                        "primary_model": "",
                        "secondary_provider": "anthropic",
                        "secondary_model": "",
                        "max_candidates": 1,
                    },
                )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["panel_summary"]["panel_signal"], "mixed")
            self.assertEqual(data["panel_summary"]["agreement_count"], 0)
            self.assertEqual(data["panel_summary"]["primary_only_count"], 1)
            self.assertEqual(data["panel_summary"]["secondary_only_count"], 0)
            self.assertIn("secondary_parse_status=invalid_json_fallback", data["notes"])
        finally:
            test_app.dependency_overrides.clear()


if __name__ == "__main__":
    unittest.main()
