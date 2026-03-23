import sys
import unittest
from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from feeds.auto_evolution import build_self_test_issue
from feeds.auto_evolution import build_source_plan_quality_issues
from feeds.auto_evolution import evaluate_source_plan_quality_snapshot
from feeds.auto_evolution import is_voting_canary_successful
from feeds.auto_evolution import update_voting_canary_state


class AutoEvolutionSelfTestIssueTest(unittest.TestCase):
    def test_healthy_snapshot_creates_no_issue(self) -> None:
        self.assertIsNone(build_self_test_issue({"healthy": True, "checks": []}))

    def test_voting_canary_failure_becomes_critical_issue(self) -> None:
        issue = build_self_test_issue(
            {
                "healthy": False,
                "checks": [
                    {
                        "id": "chat-voting-canary",
                        "name": "Voting canary",
                        "ok": False,
                        "error": "invalid api key",
                    }
                ],
            }
        )

        self.assertIsNotNone(issue)
        self.assertEqual(issue["priority"], 0)
        self.assertEqual(issue["source_type"], "system_health")
        self.assertEqual(issue["source_id"], "self_test")
        self.assertEqual(issue["source_data"]["health"], "critical")

    def test_frontend_chat_failure_becomes_critical_issue(self) -> None:
        issue = build_self_test_issue(
            {
                "healthy": False,
                "checks": [
                    {
                        "id": "frontend:/chat",
                        "name": "Frontend page /chat",
                        "ok": False,
                        "error": "Cannot find module './682.js'",
                    }
                ],
            }
        )

        self.assertIsNotNone(issue)
        self.assertEqual(issue["priority"], 0)
        self.assertEqual(issue["source_data"]["health"], "critical")

    def test_single_chat_canary_failure_becomes_critical_issue(self) -> None:
        issue = build_self_test_issue(
            {
                "healthy": False,
                "checks": [
                    {
                        "id": "chat-single-canary",
                        "name": "Single chat canary",
                        "ok": False,
                        "error": "API error 400: model `qwen-max` is not supported",
                    }
                ],
            }
        )

        self.assertIsNotNone(issue)
        self.assertEqual(issue["priority"], 0)
        self.assertEqual(issue["source_data"]["health"], "critical")

    def test_voting_canary_succeeds_after_two_models_and_synthesis_start(self) -> None:
        state = {
            "saw_start": False,
            "participants": [],
            "successful_models": set(),
            "failed_models": {},
            "saw_synthesizing": False,
            "saw_synthesis_content": False,
            "saw_result": False,
            "result_consensus": "",
            "result_successes": 0,
            "stream_error": "",
        }

        for event in (
            {"type": "voting_start", "models": ["qwen3.5-plus", "deepseek-v3.2"]},
            {"type": "voting_progress", "model": "qwen3.5-plus", "success": True},
            {"type": "voting_progress", "model": "deepseek-v3.2", "success": True},
            {"type": "voting_synthesizing"},
        ):
            state = update_voting_canary_state(state, event)

        self.assertTrue(is_voting_canary_successful(state))

    def test_voting_canary_requires_synthesis_stage(self) -> None:
        state = {
            "saw_start": True,
            "participants": ["qwen3.5-plus", "deepseek-v3.2"],
            "successful_models": {"qwen3.5-plus", "deepseek-v3.2"},
            "failed_models": {},
            "saw_synthesizing": False,
            "saw_synthesis_content": False,
            "saw_result": False,
            "result_consensus": "",
            "result_successes": 0,
            "stream_error": "",
        }

        self.assertFalse(is_voting_canary_successful(state))

    def test_browser_ui_failure_becomes_critical_issue(self) -> None:
        issue = build_self_test_issue(
            {
                "healthy": False,
                "checks": [
                    {
                        "id": "ui-browser:/chat",
                        "name": "Browser UI check /chat",
                        "ok": False,
                        "error": "browser ui probe detected layout regression",
                    }
                ],
            }
        )

        self.assertIsNotNone(issue)
        self.assertEqual(issue["priority"], 0)
        self.assertEqual(issue["source_data"]["health"], "critical")

    def test_source_plan_quality_detects_legacy_method_plan(self) -> None:
        quality = evaluate_source_plan_quality_snapshot(
            topic="multi agent research",
            focus="method",
            review_status="accepted",
            policy_version=1,
            live_policy_version=2,
            item_types=["domain", "domain"],
            bucket_counts={"implementation": 1, "authority": 1},
            gate_status_counts={"needs_review": 2},
            gate_policy={
                "require_implementation_bucket": True,
                "minimum_distinct_buckets": 4,
            },
        )

        self.assertEqual(quality["status"], "degraded")
        self.assertIn("outdated attention policy version", " ".join(quality["reasons"]))

    def test_source_plan_quality_issue_is_emitted(self) -> None:
        issues = build_source_plan_quality_issues(
            {
                "quality_findings": [
                    {
                        "plan_id": "12345678-1234-1234-1234-1234567890ab",
                        "status": "degraded",
                        "reasons": ["plan is still using an outdated attention policy version"],
                        "summary": {"policy_version": 1, "live_policy_version": 2},
                    }
                ]
            }
        )

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["priority"], 0)
        self.assertEqual(issues[0]["source_data"]["type"], "source_plan_quality")


if __name__ == "__main__":
    unittest.main()
