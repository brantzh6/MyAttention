import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from db.models import (
    RuntimeMemoryPacket,
    RuntimeOwnerKind,
    RuntimeProject,
    RuntimeTask,
    RuntimeTaskStatus,
    RuntimeTaskType,
)
from sqlalchemy import select
from runtime.benchmark_bridge import (
    BenchmarkBridgeError,
    import_benchmark_candidate_as_runtime_packet,
    import_benchmark_candidate_into_runtime_project,
    load_benchmark_procedural_candidate,
    validate_benchmark_procedural_candidate,
)
from runtime.operational_closure import (
    align_project_current_work_context,
    persist_reconstructed_work_context,
    reconstruct_runtime_work_context,
)
from runtime.project_surface import build_project_runtime_read_surface


def _candidate_payload() -> dict:
    return {
        "title": "Three-tier evaluation workflow improves agent auditability",
        "lesson": "A pre-action / in-action / post-action evaluation structure is more inspectable than a single pass-fail gate when reviewing agent behavior.",
        "why_it_mattered": "The reviewed harness study found a concrete audit workflow shape that maps to IKE's evolution-layer evaluation operations, but only partially and with security-specific limits.",
        "how_to_apply": "When designing IKE evaluation operations, prefer explicit preflight checks, execution-time checks, and closure/audit checks instead of a single aggregated result gate.",
        "confidence": 0.74,
        "source_artifact_ref": "SR-HARNESS-B4S4-8098e069",
        "derived_from": {
            "study_result_ref": "SR-HARNESS-B4S4-8098e069",
            "decision_handoff_ref": "DH-HARNESS-B4S4-8098e069",
            "closure_summary": "Real bounded study closure for harness: documentation-level evidence supports continued study, not prototype.",
        },
        "status": "candidate",
        "notes": [
            "This is an explicit reviewed benchmark closure payload candidate, not an automatically inferred memory.",
            "It should be consumed only through the truthful procedural-memory payload adapter.",
        ],
    }


class TestBenchmarkBridgeValidation:
    def test_validate_candidate_accepts_reviewed_payload(self):
        candidate = validate_benchmark_procedural_candidate(_candidate_payload())
        assert candidate.status == "candidate"
        assert candidate.confidence == 0.74
        assert candidate.derived_from["study_result_ref"] == "SR-HARNESS-B4S4-8098e069"

    def test_validate_candidate_rejects_non_candidate_status(self):
        payload = _candidate_payload()
        payload["status"] = "accepted"
        with pytest.raises(BenchmarkBridgeError, match="status='candidate'"):
            validate_benchmark_procedural_candidate(payload)

    def test_load_candidate_rejects_bad_json_shape(self, tmp_path: Path):
        candidate_file = tmp_path / "candidate.json"
        candidate_file.write_text('["not-an-object"]', encoding="utf-8")
        with pytest.raises(BenchmarkBridgeError, match="JSON object"):
            load_benchmark_procedural_candidate(candidate_file)


class TestBenchmarkBridgeImport:
    def _make_project(self, db_session):
        project = RuntimeProject(
            project_key=f"benchmark-bridge-{uuid4().hex[:8]}",
            title="Benchmark Bridge Runtime",
        )
        db_session.add(project)
        db_session.commit()
        return (
            db_session.execute(
                select(RuntimeProject).where(RuntimeProject.project_id == project.project_id)
            )
            .scalars()
            .one()
        )

    def test_import_creates_pending_review_runtime_packet(self, db_session, tmp_path: Path):
        project = self._make_project(db_session)
        candidate_file = tmp_path / "candidate.json"
        candidate_file.write_text(
            json.dumps(_candidate_payload(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        packet = import_benchmark_candidate_as_runtime_packet(
            db_session,
            str(project.project_id),
            load_benchmark_procedural_candidate(candidate_file),
            source_artifact_path=candidate_file,
        )

        assert packet.packet_type == "benchmark_procedural_candidate"
        assert packet.status.value == "pending_review"
        assert packet.accepted_at is None
        assert packet.created_by_kind == RuntimeOwnerKind.RUNTIME
        assert packet.created_by_id == "benchmark_bridge"
        assert packet.storage_ref == str(candidate_file)
        assert packet.extra["bridge"]["source_kind"] == "benchmark_procedural_memory_candidate"
        assert packet.extra["bridge"]["source_artifact_ref"] == "SR-HARNESS-B4S4-8098e069"
        assert packet.extra["review_submission"]["submitted_by"] == "runtime"
        assert packet.extra["review_submission"]["submitted_by_id"] == "benchmark_bridge"
        assert packet.extra["benchmark_candidate"]["status"] == "candidate"

    def test_import_rejects_missing_project(self, db_session):
        with pytest.raises(BenchmarkBridgeError, match="does not exist"):
            import_benchmark_candidate_as_runtime_packet(
                db_session,
                str(uuid4()),
                _candidate_payload(),
            )

    def test_import_by_project_key_rejects_missing_runtime_project(self, db_session):
        with pytest.raises(BenchmarkBridgeError, match="does not exist"):
            import_benchmark_candidate_into_runtime_project(
                db_session,
                "missing-runtime-project",
                _candidate_payload(),
            )

    def test_imported_bridge_packet_is_not_visible_as_trusted_project_surface(self, db_session):
        project = self._make_project(db_session)
        active_task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title="Runtime active task",
            status=RuntimeTaskStatus.ACTIVE,
            priority=1,
            owner_kind=RuntimeOwnerKind.DELEGATE,
            owner_id="del-001",
        )
        db_session.add(active_task)
        db_session.commit()

        packet = import_benchmark_candidate_as_runtime_packet(
            db_session,
            str(project.project_id),
            _candidate_payload(),
        )
        assert packet.status.value == "pending_review"

        context = reconstruct_runtime_work_context(db_session, str(project.project_id))
        persisted = persist_reconstructed_work_context(db_session, context)
        align_project_current_work_context(
            db_session, str(project.project_id), str(persisted.work_context_id)
        )
        surface = build_project_runtime_read_surface(db_session, str(project.project_id))

        assert surface is not None
        assert len(surface.active_tasks) == 1
        assert surface.trusted_packets == []

    def test_import_does_not_promote_to_accepted(self, db_session):
        project = self._make_project(db_session)
        import_benchmark_candidate_as_runtime_packet(
            db_session,
            str(project.project_id),
            _candidate_payload(),
        )
        packets = (
            db_session.execute(
                RuntimeMemoryPacket.__table__.select().where(
                    RuntimeMemoryPacket.project_id == project.project_id
                )
            )
            .mappings()
            .all()
        )
        assert len(packets) == 1
        assert packets[0]["status"].value == "pending_review"
        assert packets[0]["accepted_at"] is None
