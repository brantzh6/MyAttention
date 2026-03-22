import unittest
from types import SimpleNamespace

from routers.feeds import (
    _diff_source_plan_snapshots,
    _evaluate_source_plan_refresh,
    _snapshot_source_plan,
    _snapshot_source_plan_from_payload,
)


class SourcePlanVersioningHelperTests(unittest.TestCase):
    def test_snapshot_source_plan_collects_items(self):
        item = SimpleNamespace(
            object_key="github.com",
            name="GitHub",
            url="https://github.com",
            authority_tier="B",
            authority_score=0.75,
            monitoring_mode="review",
            execution_strategy="agent_assisted",
            review_cadence_days=14,
            rationale="community signal",
            status="active",
            evidence={"evidence_count": 2},
        )
        plan = SimpleNamespace(
            topic="AI coding agents",
            focus="method",
            objective="track tools",
            review_cadence_days=14,
            items=[item],
        )

        snapshot = _snapshot_source_plan(plan)
        self.assertEqual(snapshot["topic"], "AI coding agents")
        self.assertEqual(len(snapshot["items"]), 1)
        self.assertEqual(snapshot["items"][0]["object_key"], "github.com")

    def test_diff_and_evaluation_flag_degradation_for_review(self):
        previous = {
            "items": [
                {"object_key": "github.com", "authority_score": 0.8, "status": "active"},
                {"object_key": "arxiv.org", "authority_score": 1.0, "status": "active"},
            ]
        }
        current = {
            "items": [
                {"object_key": "github.com", "authority_score": 0.55, "status": "active"},
                {"object_key": "arxiv.org", "authority_score": 1.0, "status": "stale"},
            ]
        }

        diff = _diff_source_plan_snapshots(previous, current)
        evaluation = _evaluate_source_plan_refresh(diff)

        self.assertEqual(diff["summary"]["stale_count"], 1)
        self.assertLessEqual(diff["summary"]["largest_score_drop"], -0.15)
        self.assertEqual(evaluation["decision_status"], "needs_review")

    def test_snapshot_source_plan_from_payload_is_stable_without_orm_relationships(self):
        snapshot = _snapshot_source_plan_from_payload(
            topic="AI coding agents",
            focus="method",
            objective="track methods",
            review_cadence_days=14,
            items=[
                {
                    "object_key": "github.com",
                    "name": "GitHub",
                    "url": "https://github.com",
                    "authority_tier": "B",
                    "authority_score": 0.75,
                    "monitoring_mode": "review",
                    "execution_strategy": "agent_assisted",
                    "review_cadence_days": 14,
                    "rationale": "community signal",
                    "status": "active",
                    "evidence": {"evidence_count": 2},
                }
            ],
        )
        self.assertEqual(snapshot["topic"], "AI coding agents")
        self.assertEqual(snapshot["items"][0]["object_key"], "github.com")
        self.assertEqual(snapshot["items"][0]["execution_strategy"], "agent_assisted")


if __name__ == "__main__":
    unittest.main()
