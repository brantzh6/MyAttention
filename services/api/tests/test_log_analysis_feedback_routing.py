import sys
from pathlib import Path
from types import SimpleNamespace


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from pipeline.log_analysis_scheduler import _classify_log_insight_feedback


def test_redis_cache_insight_defaults_to_acceleration_degradation():
    insight = SimpleNamespace(
        category="reliability",
        severity="warning",
        evidence=["redis read failed for cs_com: Error 22 connecting to localhost:6379"],
    )

    routing = _classify_log_insight_feedback(insight)

    assert routing["feedback_class"] == "acceleration_degradation"
    assert routing["routing_lane"] == "low_cost_monitoring"
    assert routing["controller_escalation"] is False


def test_canonical_preflight_insight_escalates_to_controller():
    insight = SimpleNamespace(
        category="reliability",
        severity="critical",
        evidence=["canonical service preflight mismatch on runtime controller surface"],
    )

    routing = _classify_log_insight_feedback(insight)

    assert routing["feedback_class"] == "canonical_truth_risk"
    assert routing["routing_lane"] == "controller"
    assert routing["controller_escalation"] is True
