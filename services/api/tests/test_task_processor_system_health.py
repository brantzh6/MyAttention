import sys
import unittest
from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from feeds.task_processor import (
    build_system_health_recovery_plan,
    classify_feedback_signal,
    is_system_health_improved,
    make_ascii_safe,
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

    def test_make_ascii_safe_normalizes_nested_unicode_payload(self) -> None:
        sanitized = make_ascii_safe(
            {
                "message": "添加到定期汇总报告",
                "nested": ["进化大脑", {"label": "智能对话"}],
            }
        )

        self.assertEqual(sanitized["message"], "?????????")
        self.assertEqual(sanitized["nested"][0], "????")
        self.assertEqual(sanitized["nested"][1]["label"], "????")

    def test_feed_collection_health_defaults_to_low_cost_monitoring(self) -> None:
        routing = classify_feedback_signal(
            source_type="system_health",
            category="quality",
            source_data={
                "type": "feed_collection_health",
                "status": "degraded",
                "state": "backlog",
            },
        )
        self.assertEqual(routing["feedback_class"], "operational_degradation")
        self.assertEqual(routing["routing_lane"], "low_cost_monitoring")
        self.assertFalse(routing["controller_escalation"])

    def test_log_analysis_redis_signal_defaults_to_acceleration_degradation(self) -> None:
        routing = classify_feedback_signal(
            source_type="log_analysis",
            category="reliability",
            source_data={
                "type": "log_insight",
                "evidence": ["redis read failed for cs_com: connection refused localhost:6379"],
            },
        )
        self.assertEqual(routing["feedback_class"], "acceleration_degradation")
        self.assertEqual(routing["routing_lane"], "low_cost_monitoring")
        self.assertFalse(routing["controller_escalation"])


if __name__ == "__main__":
    unittest.main()
