import unittest
from types import SimpleNamespace

from routers.feeds import (
    _diff_source_plan_snapshots,
    _build_source_plan_version_judgment_targets,
    _evaluate_source_plan_refresh,
    _snapshot_source_plan,
    _snapshot_source_plan_from_payload,
    SourcePlanVersionResponse,
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
                {"object_key": "github.com", "authority_score": 0.8, "authority_tier": "A", "status": "active", "evidence": {"evidence_count": 3}},
                {"object_key": "arxiv.org", "authority_score": 1.0, "authority_tier": "S", "status": "active", "evidence": {"evidence_count": 4}},
            ]
        }
        current = {
            "items": [
                {"object_key": "github.com", "authority_score": 0.55, "authority_tier": "B", "status": "active", "evidence": {"evidence_count": 1}},
                {"object_key": "arxiv.org", "authority_score": 1.0, "authority_tier": "S", "status": "stale", "evidence": {"evidence_count": 4}},
            ]
        }

        diff = _diff_source_plan_snapshots(previous, current)
        evaluation = _evaluate_source_plan_refresh(diff)

        self.assertEqual(diff["summary"]["stale_count"], 1)
        self.assertLessEqual(diff["summary"]["largest_score_drop"], -0.15)
        self.assertEqual(diff["summary"]["authority_regression_count"], 1)
        self.assertEqual(evaluation["decision_status"], "needs_review")
        self.assertGreater(len(evaluation["gate_signals"]), 0)

    def test_diff_and_evaluation_accept_non_degrading_refresh(self):
        previous = {
            "items": [
                {"object_key": "github.com", "authority_score": 0.72, "authority_tier": "B", "status": "active", "evidence": {"evidence_count": 2}},
                {"object_key": "arxiv.org", "authority_score": 0.95, "authority_tier": "S", "status": "active", "evidence": {"evidence_count": 5}},
            ]
        }
        current = {
            "items": [
                {"object_key": "github.com", "authority_score": 0.76, "authority_tier": "B", "status": "active", "evidence": {"evidence_count": 3}},
                {"object_key": "arxiv.org", "authority_score": 0.95, "authority_tier": "S", "status": "active", "evidence": {"evidence_count": 5}},
                {"object_key": "openai.com", "authority_score": 0.88, "authority_tier": "A", "status": "active", "evidence": {"evidence_count": 2}},
            ]
        }

        diff = _diff_source_plan_snapshots(previous, current)
        evaluation = _evaluate_source_plan_refresh(diff)

        self.assertEqual(diff["summary"]["added_count"], 1)
        self.assertGreaterEqual(diff["summary"]["average_score_delta"], 0)
        self.assertEqual(evaluation["decision_status"], "accepted")

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

    def test_build_source_plan_version_judgment_targets_prioritizes_risky_changes(self):
        version = SourcePlanVersionResponse(
            id="version-1",
            version_number=2,
            parent_version=1,
            trigger_type="manual_refresh",
            decision_status="needs_review",
            topic="AI coding agents",
            focus="method",
            change_reason="manual refresh",
            change_summary={
                "summary": {"removed_count": 1, "stale_count": 1},
                "removed": ["github.com/openclaw/openclaw"],
                "stale": ["reddit.com/r/machinelearning/comments/abc123"],
                "score_deltas": [
                    {"object_key": "github.com/openclaw/openclaw", "delta": -0.22},
                    {"object_key": "reddit.com/r/machinelearning/comments/abc123", "delta": -0.08},
                ],
                "authority_regressions": [
                    {"object_key": "github.com/openclaw/openclaw", "before_tier": "A", "after_tier": "B"}
                ],
            },
            evaluation={"decision_status": "needs_review", "gate_signals": {"removed_count": 1}},
            created_by="source_intelligence_v1",
        )
        snapshot_items = [
            {
                "object_key": "reddit.com/r/machinelearning/comments/abc123",
                "item_type": "signal",
                "name": "discussion thread",
                "status": "stale",
                "authority_tier": "B",
                "authority_score": 0.61,
                "evidence": {"evidence_count": 2},
            }
        ]

        targets = _build_source_plan_version_judgment_targets(version, snapshot_items, max_candidates=3)

        self.assertEqual(targets[0].object_key, "github.com/openclaw/openclaw")
        self.assertEqual(targets[0].change_type, "removed")
        self.assertEqual(targets[1].object_key, "reddit.com/r/machinelearning/comments/abc123")
        self.assertEqual(targets[1].change_type, "stale")

    def test_build_source_plan_version_judgment_targets_falls_back_to_snapshot_only(self):
        version = SourcePlanVersionResponse(
            id="version-2",
            version_number=3,
            parent_version=2,
            trigger_type="manual_refresh",
            decision_status="accepted",
            topic="AI coding agents",
            focus="method",
            change_reason="snapshot-only baseline",
            change_summary={"summary": {"current_item_count": 2}},
            evaluation={"decision_status": "accepted", "gate_signals": {}},
            created_by="source_intelligence_v1",
        )
        snapshot_items = [
            {
                "object_key": "github.com/openclaw/openclaw",
                "item_type": "repository",
                "name": "openclaw/openclaw",
                "status": "active",
                "authority_tier": "A",
                "authority_score": 0.82,
                "evidence": {"evidence_count": 4},
            },
            {
                "object_key": "reddit.com/r/machinelearning",
                "item_type": "community",
                "name": "r/MachineLearning",
                "status": "active",
                "authority_tier": "B",
                "authority_score": 0.61,
                "evidence": {"evidence_count": 2},
            },
        ]

        targets = _build_source_plan_version_judgment_targets(version, snapshot_items, max_candidates=1)

        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0].object_key, "github.com/openclaw/openclaw")
        self.assertEqual(targets[0].change_type, "snapshot_only")


if __name__ == "__main__":
    unittest.main()
