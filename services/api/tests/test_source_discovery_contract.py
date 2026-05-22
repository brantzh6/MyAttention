import unittest
from types import SimpleNamespace

from routers.feeds import (
    SourceDiscoveryCandidate,
    SourceDiscoveryFocus,
    SourceDiscoveryInterestBias,
    SourceDiscoveryRequest,
    SourcePlanCreateRequest,
    _discovery_request_from_persisted_plan,
    _serialize_source_plan,
    _discovery_notes,
    _discovery_request_from_source_plan,
    _discovery_truth_boundary,
    _enrich_discovery_candidate,
    _interest_bias_for_focus,
    _source_nature_for_candidate,
    _temperature_for_candidate,
)


class SourceDiscoveryContractTests(unittest.TestCase):
    def test_interest_bias_defaults_follow_focus(self) -> None:
        self.assertEqual(_interest_bias_for_focus(SourceDiscoveryFocus.AUTHORITATIVE), SourceDiscoveryInterestBias.AUTHORITY)
        self.assertEqual(_interest_bias_for_focus(SourceDiscoveryFocus.FRONTIER), SourceDiscoveryInterestBias.FRONTIER)
        self.assertEqual(_interest_bias_for_focus(SourceDiscoveryFocus.METHOD), SourceDiscoveryInterestBias.METHOD)

    def test_enrich_candidate_adds_contract_fields(self) -> None:
        candidate = SourceDiscoveryCandidate(
            item_type="repository",
            object_key="github.com/openclaw/openclaw",
            domain="github.com",
            name="openclaw/openclaw",
            url="https://github.com/openclaw/openclaw",
            authority_tier="A",
            authority_score=0.82,
            recommendation="subscribe",
            recommendation_reason="method artifact",
            evidence_count=3,
            matched_queries=["openclaw github repository"],
            sample_titles=["OpenClaw repository"],
            sample_snippets=["OpenClaw code and releases"],
        )
        enriched = _enrich_discovery_candidate(candidate, SourceDiscoveryFocus.METHOD)
        self.assertEqual(enriched.source_nature, "artifact")
        self.assertEqual(enriched.recommended_mode, "subscribe")
        self.assertEqual(enriched.recommended_execution_strategy, "agent_assisted")
        self.assertEqual(enriched.canonical_ref, "github.com/openclaw/openclaw")
        self.assertEqual(enriched.candidate_endpoints, ["https://github.com/openclaw/openclaw"])
        self.assertTrue(enriched.confidence_note)

    def test_notes_and_truth_boundary_are_explicit(self) -> None:
        request = SourceDiscoveryRequest(
            topic="agent harness patterns",
            focus=SourceDiscoveryFocus.METHOD,
            task_intent="prepare bounded discovery loop",
            interest_bias=SourceDiscoveryInterestBias.METHOD,
            limit=8,
        )
        notes = _discovery_notes(request, 4)
        truth_boundary = _discovery_truth_boundary()
        self.assertIn("task_intent=prepare bounded discovery loop", notes)
        self.assertIn("interest_bias=method", notes)
        self.assertEqual(len(truth_boundary), 3)
        self.assertIn("not canonical source truth", truth_boundary[0])

    def test_source_nature_and_temperature_stay_bounded(self) -> None:
        self.assertEqual(_source_nature_for_candidate("person", "x.com"), "actor")
        self.assertEqual(_source_nature_for_candidate("signal", "reddit.com"), "community")
        self.assertEqual(_temperature_for_candidate(SourceDiscoveryFocus.AUTHORITATIVE, "domain"), "low")
        self.assertEqual(_temperature_for_candidate(SourceDiscoveryFocus.METHOD, "repository"), "high")

    def test_source_plan_request_maps_into_discovery_request(self) -> None:
        plan_request = SourcePlanCreateRequest(
            topic="agent harness patterns",
            focus=SourceDiscoveryFocus.METHOD,
            objective="build a reusable plan",
            task_intent="prepare first source plan",
            interest_bias=SourceDiscoveryInterestBias.METHOD,
            limit=9,
            review_cadence_days=14,
        )
        discovery_request = _discovery_request_from_source_plan(plan_request)
        self.assertEqual(discovery_request.topic, "agent harness patterns")
        self.assertEqual(discovery_request.focus, SourceDiscoveryFocus.METHOD)
        self.assertEqual(discovery_request.task_intent, "prepare first source plan")
        self.assertEqual(discovery_request.interest_bias, SourceDiscoveryInterestBias.METHOD)
        self.assertEqual(discovery_request.limit, 9)

    def test_persisted_plan_maps_back_into_discovery_request(self) -> None:
        plan = SimpleNamespace(
            topic="agent harness patterns",
            objective="build reusable plan",
            extra={
                "task_intent": "refresh same source plan",
                "interest_bias": "method",
            },
        )
        discovery_request = _discovery_request_from_persisted_plan(
            plan,
            SourceDiscoveryFocus.METHOD,
            7,
        )
        self.assertEqual(discovery_request.topic, "agent harness patterns")
        self.assertEqual(discovery_request.task_intent, "refresh same source plan")
        self.assertEqual(discovery_request.interest_bias, SourceDiscoveryInterestBias.METHOD)
        self.assertEqual(discovery_request.limit, 7)

    def test_serialize_source_plan_exposes_discovery_context(self) -> None:
        plan = SimpleNamespace(
            id="plan-123",
            topic="agent harness patterns",
            focus="method",
            objective="build reusable plan",
            planning_brain="source-intelligence-brain",
            status="active",
            review_status="draft",
            review_cadence_days=14,
            current_version=1,
            latest_version=1,
            extra={
                "task_intent": "prepare first source plan",
                "interest_bias": "method",
                "discovery_notes": ["topic=agent harness patterns"],
                "discovery_truth_boundary": ["candidate discovery is inspect output, not canonical source truth"],
                "attention_policy": {"policy_id": "source-method-v1", "policy_version": 1, "policy_name": "Method"},
                "latest_evaluation": {"decision_status": "accepted"},
            },
            items=[],
            created_at=None,
            updated_at=None,
        )
        response = _serialize_source_plan(plan)
        self.assertEqual(response.task_intent, "prepare first source plan")
        self.assertEqual(response.interest_bias, "method")
        self.assertEqual(response.discovery_notes, ["topic=agent harness patterns"])
        self.assertEqual(
            response.discovery_truth_boundary,
            ["candidate discovery is inspect output, not canonical source truth"],
        )


if __name__ == "__main__":
    unittest.main()
