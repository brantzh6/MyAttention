import sys
import unittest
from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from feeds.auto_evolution import build_self_test_issue
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
            {"type": "voting_synthesis_content", "content": "【一句话判断】结果为 2"},
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


if __name__ == "__main__":
    unittest.main()
