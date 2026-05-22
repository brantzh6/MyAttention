import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from routers.evolution import _build_context_summary
from routers.evolution import _dedupe_tasks


class EvolutionContextViewTests(unittest.TestCase):
    def test_build_context_summary_counts_open_tasks_and_latest_items(self):
        now = datetime.now(timezone.utc)
        context = SimpleNamespace(
            id=uuid4(),
            context_type="evolution",
            title="Auto Evolution Self-Test",
            goal="Verify critical paths",
            owner_type="system",
            owner_id="auto-evolution:self-test",
            status="active",
            priority=1,
            updated_at=now,
            tasks=[
                SimpleNamespace(status="pending"),
                SimpleNamespace(status="completed"),
                SimpleNamespace(status="failed"),
            ],
            events=[
                SimpleNamespace(
                    id=uuid4(),
                    task_id=None,
                    context_id=uuid4(),
                    event_type="self_test_snapshot",
                    action="observe",
                    result="success",
                    from_status=None,
                    to_status=None,
                    reason="periodic run",
                    details={},
                    payload={},
                    performed_by="system",
                    created_at=now,
                )
            ],
            artifacts=[
                SimpleNamespace(
                    id=uuid4(),
                    task_id=None,
                    context_id=uuid4(),
                    artifact_type="report",
                    version=1,
                    title="Self-test snapshot",
                    summary="healthy",
                    storage_ref="inline://metadata",
                    content_ref="",
                    created_by="system",
                    extra={},
                    created_at=now,
                )
            ],
        )

        summary = _build_context_summary(context)

        self.assertEqual(summary.task_count, 3)
        self.assertEqual(summary.open_task_count, 2)
        self.assertEqual(summary.event_count, 1)
        self.assertEqual(summary.artifact_count, 1)
        self.assertEqual(summary.latest_event["event_type"], "self_test_snapshot")
        self.assertEqual(summary.latest_artifact["artifact_type"], "report")

    def test_dedupe_tasks_keeps_latest_task_per_signature(self):
        now = datetime.now(timezone.utc)
        duplicate_title = "quality drift"
        source_id = "plan-1"
        tasks = [
            SimpleNamespace(
                source_type="system_health",
                source_id=source_id,
                title=duplicate_title,
                updated_at=now,
                created_at=now,
            ),
            SimpleNamespace(
                source_type="system_health",
                source_id=source_id,
                title=duplicate_title,
                updated_at=now.replace(microsecond=0),
                created_at=now.replace(microsecond=0),
            ),
            SimpleNamespace(
                source_type="system_health",
                source_id="plan-2",
                title=duplicate_title,
                updated_at=now,
                created_at=now,
            ),
        ]

        deduped = _dedupe_tasks(tasks)

        self.assertEqual(len(deduped), 2)
        self.assertEqual(deduped[0].source_id, source_id)


if __name__ == "__main__":
    unittest.main()
