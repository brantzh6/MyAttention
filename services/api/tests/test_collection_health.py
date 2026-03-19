import sys
import unittest
from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from feeds.collection_health import build_collection_health_issue, summarize_collection_health


class CollectionHealthSummaryTest(unittest.TestCase):
    def test_idle_collection_is_not_marked_unhealthy(self) -> None:
        summary = summarize_collection_health(
            {
                "counts": {
                    "raw_ingest_total": 0,
                    "feed_items_total": 0,
                    "raw_ingest_1h": 0,
                    "raw_ingest_24h": 0,
                    "feed_items_24h": 0,
                    "raw_errors_24h": 0,
                    "raw_durable_24h": 0,
                    "raw_pending_1h": 0,
                    "raw_pending_24h": 0,
                },
                "freshness": {
                    "last_raw_ingest_age_hours": None,
                },
                "ratios": {
                    "durable_ratio_24h": 1.0,
                    "persist_ratio_24h": 1.0,
                },
            }
        )
        self.assertEqual(summary["status"], "healthy")
        self.assertEqual(summary["state"], "idle")

    def test_raw_without_feed_items_is_unhealthy(self) -> None:
        summary = summarize_collection_health(
            {
                "counts": {
                    "raw_ingest_total": 10,
                    "feed_items_total": 2,
                    "raw_ingest_1h": 5,
                    "raw_ingest_24h": 5,
                    "feed_items_24h": 0,
                    "raw_errors_24h": 0,
                    "raw_durable_24h": 0,
                    "raw_pending_1h": 5,
                    "raw_pending_24h": 5,
                },
                "freshness": {
                    "last_raw_ingest_age_hours": 1.2,
                },
                "ratios": {
                    "durable_ratio_24h": 0.0,
                    "persist_ratio_24h": 0.0,
                },
            }
        )
        self.assertEqual(summary["status"], "unhealthy")
        self.assertEqual(summary["state"], "write_blocked")

    def test_large_unresolved_backlog_is_degraded(self) -> None:
        summary = summarize_collection_health(
            {
                "counts": {
                    "raw_ingest_total": 100,
                    "feed_items_total": 80,
                    "raw_ingest_1h": 10,
                    "raw_ingest_24h": 10,
                    "feed_items_24h": 4,
                    "raw_errors_24h": 1,
                    "raw_durable_24h": 4,
                    "raw_pending_1h": 6,
                    "raw_pending_24h": 6,
                },
                "freshness": {
                    "last_raw_ingest_age_hours": 0.5,
                },
                "ratios": {
                    "durable_ratio_24h": 0.4,
                    "persist_ratio_24h": 0.4,
                },
            }
        )
        self.assertEqual(summary["status"], "degraded")
        self.assertEqual(summary["state"], "backlog")

    def test_build_issue_for_non_healthy_snapshot(self) -> None:
        snapshot = {
            "counts": {
                "raw_ingest_1h": 12,
                "raw_durable_24h": 3,
                "raw_pending_1h": 9,
                "raw_errors_24h": 1,
            },
            "pending_sources_1h": [
                {"source_key": "alpha", "pending_count": 6, "last_seen": "2026-03-19T00:00:00+00:00"},
                {"source_key": "beta", "pending_count": 3, "last_seen": "2026-03-19T00:10:00+00:00"},
            ],
            "error_sources_24h": [
                {"source_key": "gamma", "error_count": 1, "last_seen": "2026-03-19T00:20:00+00:00"},
            ],
            "summary": {
                "status": "degraded",
                "state": "backlog",
                "message": "Collection backlog detected.",
            },
        }
        issue = build_collection_health_issue(snapshot)
        self.assertIsNotNone(issue)
        self.assertEqual(issue["source_type"], "system_health")
        self.assertEqual(issue["source_id"], "feed_collection")
        self.assertEqual(issue["priority"], 2)
        self.assertTrue(issue["auto_processible"])
        self.assertIn("backlog", issue["title"])
        self.assertIn("alpha(6)", issue["description"])
        self.assertEqual(issue["source_data"]["pending_sources_1h"][0]["source_key"], "alpha")

    def test_build_issue_skips_healthy_snapshot(self) -> None:
        issue = build_collection_health_issue(
            {"summary": {"status": "healthy", "state": "active", "message": "ok"}}
        )
        self.assertIsNone(issue)


if __name__ == "__main__":
    unittest.main()
