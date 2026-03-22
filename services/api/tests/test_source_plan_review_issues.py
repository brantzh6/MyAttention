import unittest

from feeds.auto_evolution import build_source_plan_review_issues


class SourcePlanReviewIssueTests(unittest.TestCase):
    def test_returns_failure_issue(self):
        snapshot = {
            "failures": [
                {
                    "plan_id": "plan-12345678",
                    "topic": "ai agents",
                    "status": 500,
                    "error": {"detail": "boom"},
                }
            ],
            "refreshed": [],
        }

        issues = build_source_plan_review_issues(snapshot)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["source_id"], "plan-12345678")
        self.assertEqual(issues[0]["source_data"]["state"], "failed")

    def test_returns_needs_review_issue_for_candidate_drift(self):
        snapshot = {
            "failures": [],
            "refreshed": [
                {
                    "plan_id": "plan-abcdef12",
                    "topic": "source intelligence",
                    "review_status": "needs_review",
                    "current_version": 2,
                    "latest_version": 3,
                }
            ],
        }

        issues = build_source_plan_review_issues(snapshot)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["source_id"], "plan-abcdef12")
        self.assertEqual(issues[0]["source_data"]["state"], "needs_review")

    def test_skips_accepted_refresh_without_version_drift(self):
        snapshot = {
            "failures": [],
            "refreshed": [
                {
                    "plan_id": "plan-ok",
                    "topic": "stable",
                    "review_status": "accepted",
                    "current_version": 4,
                    "latest_version": 4,
                }
            ],
        }

        issues = build_source_plan_review_issues(snapshot)
        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
