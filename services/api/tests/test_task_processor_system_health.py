import sys
import unittest
from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from feeds.task_processor import (
    build_system_health_recovery_plan,
    is_system_health_improved,
)


class TaskProcessorSystemHealthTest(unittest.TestCase):
    def test_feed_collection_health_has_pipeline_recovery_plan(self) -> None:
        plan = build_system_health_recovery_plan(
            {
                "type": "feed_collection_health",
                "status": "degraded",
                "state": "backlog",
            }
        )
        self.assertEqual(plan["strategy"], "trigger_pipeline")
        self.assertEqual(plan["state"], "backlog")
        self.assertEqual(plan["verify_endpoint"], "/api/evolution/collection-health")

    def test_unknown_system_health_issue_falls_back_to_observe_only(self) -> None:
        plan = build_system_health_recovery_plan({"type": "custom_health_check"})
        self.assertEqual(plan["strategy"], "observe_only")

    def test_system_health_improvement_detects_rank_upgrade(self) -> None:
        self.assertTrue(is_system_health_improved("unhealthy", "degraded"))
        self.assertTrue(is_system_health_improved("degraded", "healthy"))
        self.assertFalse(is_system_health_improved("healthy", "degraded"))
        self.assertFalse(is_system_health_improved("degraded", "degraded"))


if __name__ == "__main__":
    unittest.main()
