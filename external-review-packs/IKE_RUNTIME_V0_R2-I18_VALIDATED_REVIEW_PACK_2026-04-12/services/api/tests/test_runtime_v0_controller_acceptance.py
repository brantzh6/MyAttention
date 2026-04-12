from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select

from db.models import (
    RuntimeDecision,
    RuntimeProject,
    RuntimeTask,
    RuntimeTaskEvent,
    RuntimeTaskStatus,
    RuntimeTaskType,
)
from runtime.controller_acceptance import (
    ControllerAcceptanceError,
    inspect_controller_acceptance_record,
    record_controller_acceptance,
)
from runtime.project_surface import build_project_runtime_read_surface


def _make_preflight_data(
    *,
    status: str = "controller_confirmation_required",
    basis: str = "windows_venv_redirector_v1",
) -> dict:
    return {
        "status": "ready",
        "timestamp": "2026-04-11T02:15:00+00:00",
        "api_health": {
            "endpoint": "http://127.0.0.1:8000/health",
            "is_healthy": True,
            "response_status": 200,
            "response_body": {"status": "healthy"},
            "response_time_ms": 12.0,
        },
        "port_ownership": {
            "port": 8000,
            "listening_processes": [{"pid": 1, "name": "python.exe"}],
            "unique_count": 1,
            "is_clear": True,
            "inspection_method": "windows_powershell",
        },
        "summary": "Ready",
        "details": {
            "host": "127.0.0.1",
            "port": 8000,
            "controller_acceptability": {
                "status": "acceptable_windows_venv_redirector",
                "acceptable": True,
                "controller_confirmation_required": True,
                "rule": basis,
            },
            "controller_promotion": {
                "status": status,
                "eligible": status == "controller_confirmation_required",
                "target_status": "canonical_accepted",
                "controller_confirmation_required": status == "controller_confirmation_required",
                "basis": basis,
            },
            "canonical_launch": {
                "launch_mode": "repo_uvicorn_entry",
                "launcher_path": "D:\\code\\MyAttention\\.venv\\Scripts\\uvicorn.exe",
                "service_entry_path": "D:\\code\\MyAttention\\services\\api\\main.py",
            },
        },
    }


class TestRuntimeControllerAcceptance:
    def _make_project(self, db_session, suffix: str) -> RuntimeProject:
        project = RuntimeProject(
            project_key=f"controller-acceptance-{suffix}-{uuid4().hex[:8]}",
            title="Controller Acceptance Runtime",
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

    def _make_task(self, db_session, project: RuntimeProject, title: str) -> RuntimeTask:
        task = RuntimeTask(
            project_id=project.project_id,
            task_type=RuntimeTaskType.IMPLEMENTATION,
            title=title,
            status=RuntimeTaskStatus.DONE,
            priority=1,
            result_summary="Completed runtime work",
            ended_at=datetime.now(timezone.utc),
        )
        db_session.add(task)
        db_session.commit()
        return (
            db_session.execute(select(RuntimeTask).where(RuntimeTask.task_id == task.task_id))
            .scalars()
            .one()
        )

    def test_inspect_controller_acceptance_record_returns_absent_state(self, db_session):
        project = self._make_project(db_session, "inspect")

        result = inspect_controller_acceptance_record(
            db_session,
            preflight_data=_make_preflight_data(),
            project_key=project.project_key,
        )

        assert result["status"] == "ready"
        assert result["project"]["project_key"] == project.project_key
        assert result["decision_record"]["exists"] is False
        assert result["truth_boundary"]["inspect_only"] is True

    def test_record_controller_acceptance_persists_decision_event_and_surface(self, db_session):
        project = self._make_project(db_session, "record")
        task = self._make_task(db_session, project, "Anchor task")

        result = record_controller_acceptance(
            db_session,
            preflight_data=_make_preflight_data(),
            controller_id="controller-001",
            project_key=project.project_key,
            summary="Accept runtime proof baseline",
        )

        assert result["recorded"] is True
        assert result["event_recorded"] is True
        assert result["work_context_updated"] is True
        assert result["task_anchor_id"] == str(task.task_id)

        decision_rows = (
            db_session.execute(
                select(RuntimeDecision).where(
                    RuntimeDecision.project_id == project.project_id,
                    RuntimeDecision.decision_scope == "canonical_service_acceptance",
                )
            )
            .scalars()
            .all()
        )
        assert len(decision_rows) == 1
        assert decision_rows[0].extra["basis"] == "windows_venv_redirector_v1"

        event_rows = (
            db_session.execute(
                select(RuntimeTaskEvent).where(
                    RuntimeTaskEvent.project_id == project.project_id,
                    RuntimeTaskEvent.event_type == "controller_acceptance_recorded",
                )
            )
            .scalars()
            .all()
        )
        assert len(event_rows) == 1
        assert str(event_rows[0].task_id) == str(task.task_id)

        surface = build_project_runtime_read_surface(db_session, str(project.project_id))
        assert surface is not None
        assert surface.latest_decision is not None
        assert surface.latest_decision.decision_id == result["decision_id"]

    def test_record_controller_acceptance_reuses_same_basis_idempotently(self, db_session):
        project = self._make_project(db_session, "reuse")
        self._make_task(db_session, project, "Reuse anchor task")
        preflight_data = _make_preflight_data()

        first = record_controller_acceptance(
            db_session,
            preflight_data=preflight_data,
            controller_id="controller-001",
            project_key=project.project_key,
        )
        second = record_controller_acceptance(
            db_session,
            preflight_data=preflight_data,
            controller_id="controller-001",
            project_key=project.project_key,
        )

        assert first["recorded"] is True
        assert second["recorded"] is False
        assert second["idempotent_reuse"] is True
        assert second["decision_id"] == first["decision_id"]

        decision_count = (
            db_session.execute(
                select(RuntimeDecision).where(
                    RuntimeDecision.project_id == project.project_id,
                    RuntimeDecision.decision_scope == "canonical_service_acceptance",
                )
            )
            .scalars()
            .all()
        )
        event_count = (
            db_session.execute(
                select(RuntimeTaskEvent).where(
                    RuntimeTaskEvent.project_id == project.project_id,
                    RuntimeTaskEvent.event_type == "controller_acceptance_recorded",
                )
            )
            .scalars()
            .all()
        )
        assert len(decision_count) == 1
        assert len(event_count) == 1

    def test_record_controller_acceptance_rejects_project_without_task_anchor(self, db_session):
        project = self._make_project(db_session, "no-task")

        try:
            record_controller_acceptance(
                db_session,
                preflight_data=_make_preflight_data(),
                controller_id="controller-001",
                project_key=project.project_key,
            )
        except ControllerAcceptanceError as exc:
            assert "no task anchor" in str(exc)
        else:
            raise AssertionError("Expected ControllerAcceptanceError for missing task anchor")
