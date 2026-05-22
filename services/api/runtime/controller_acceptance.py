"""
IKE Runtime v0 - Controller Acceptance Record Helper

Narrow durable helper for one explicit controller acceptance record above the
current runtime service preflight decision surface.

This module does NOT implement a general approval workflow. It records one
bounded acceptance decision for the scope `canonical_service_acceptance`.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from db.models import (
    RuntimeDecision,
    RuntimeDecisionOutcome,
    RuntimeDecisionStatus,
    RuntimeOwnerKind,
    RuntimeProject,
    RuntimeTask,
    RuntimeTaskEvent,
)
from runtime.operational_closure import (
    align_project_current_work_context,
    persist_reconstructed_work_context,
    reconstruct_runtime_work_context,
)


DECISION_SCOPE = "canonical_service_acceptance"
EVENT_TYPE = "controller_acceptance_recorded"


class ControllerAcceptanceError(ValueError):
    """Bounded runtime-domain error for controller acceptance recording."""


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _resolve_project(db_session, project_key: str | None) -> RuntimeProject:
    query = select(RuntimeProject)
    if project_key:
        query = query.where(RuntimeProject.project_key == project_key)
    else:
        query = query.order_by(
            RuntimeProject.created_at.desc(),
            RuntimeProject.project_key.desc(),
        ).limit(1)

    project = db_session.execute(query).scalars().one_or_none()
    if project is None:
        if project_key:
            raise ControllerAcceptanceError(
                f"Runtime project not found for project_key '{project_key}'."
            )
        raise ControllerAcceptanceError(
            "No runtime project exists for controller acceptance recording."
        )
    return project


def _latest_scope_decision(db_session, project_id) -> RuntimeDecision | None:
    return (
        db_session.execute(
            select(RuntimeDecision)
            .where(
                RuntimeDecision.project_id == project_id,
                RuntimeDecision.decision_scope == DECISION_SCOPE,
                RuntimeDecision.finalized_at.is_not(None),
            )
            .order_by(
                RuntimeDecision.finalized_at.desc(),
                RuntimeDecision.created_at.desc(),
            )
            .limit(1)
        )
        .scalars()
        .one_or_none()
    )


def _latest_task_anchor(db_session, project_id) -> RuntimeTask | None:
    return (
        db_session.execute(
            select(RuntimeTask)
            .where(RuntimeTask.project_id == project_id)
            .order_by(RuntimeTask.created_at.desc(), RuntimeTask.priority.asc())
            .limit(1)
        )
        .scalars()
        .one_or_none()
    )


def _build_current_record(row: RuntimeDecision | None) -> dict[str, Any]:
    if row is None:
        return {
            "exists": False,
            "decision_id": None,
            "decision_scope": DECISION_SCOPE,
            "outcome": None,
            "status": None,
            "basis": None,
            "target_status": None,
            "finalized_at": None,
            "supersedes_decision_id": None,
            "project_id": None,
            "project_key": None,
        }

    metadata = row.extra or {}
    return {
        "exists": True,
        "decision_id": str(row.decision_id),
        "decision_scope": row.decision_scope,
        "outcome": _enum_value(row.outcome),
        "status": _enum_value(row.status),
        "basis": metadata.get("basis"),
        "target_status": metadata.get("target_status"),
        "finalized_at": row.finalized_at.isoformat() if row.finalized_at else None,
        "supersedes_decision_id": (
            str(row.supersedes_decision_id) if row.supersedes_decision_id else None
        ),
        "project_id": str(row.project_id),
        "project_key": metadata.get("project_key"),
    }


def _preflight_shape(preflight_data: dict[str, Any]) -> dict[str, Any]:
    details = preflight_data.get("details") or {}
    promotion = details.get("controller_promotion") or {}
    launch = details.get("canonical_launch") or {}
    return {
        "basis": promotion.get("basis"),
        "target_status": promotion.get("target_status"),
        "host": details.get("host"),
        "port": details.get("port"),
        "launch_mode": launch.get("launch_mode"),
        "launcher_path": launch.get("launcher_path"),
        "service_entry_path": launch.get("service_entry_path"),
    }


def _decision_matches_preflight(
    row: RuntimeDecision,
    preflight_shape: dict[str, Any],
) -> bool:
    metadata = row.extra or {}
    for key, value in preflight_shape.items():
        if metadata.get(key) != value:
            return False
    return True


def _default_summary(basis: str | None, host: str | None, port: int | None) -> str:
    basis_part = basis or "current_preflight_basis"
    host_part = host or "127.0.0.1"
    port_part = port if port is not None else 8000
    return (
        f"Controller accepted {basis_part} canonical service proof at "
        f"{host_part}:{port_part}"
    )


def inspect_controller_acceptance_record(
    db_session,
    *,
    preflight_data: dict[str, Any],
    project_key: str | None = None,
) -> dict[str, Any]:
    project = _resolve_project(db_session, project_key)
    latest = _latest_scope_decision(db_session, project.project_id)
    current_record = _build_current_record(latest)
    current_record["project_id"] = str(project.project_id)
    current_record["project_key"] = project.project_key
    return {
        "status": "ready",
        "project": {
            "project_id": str(project.project_id),
            "project_key": project.project_key,
            "title": project.title,
        },
        "current_preflight": preflight_data,
        "decision_record": current_record,
        "truth_boundary": {
            "inspect_only": True,
            "mutates_acceptance": False,
            "records_controller_decision": False,
            "implies_canonical_accepted": False,
        },
    }


def record_controller_acceptance(
    db_session,
    *,
    preflight_data: dict[str, Any],
    controller_id: str,
    project_key: str | None = None,
    summary: str | None = None,
    rationale: str | None = None,
) -> dict[str, Any]:
    controller_id = (controller_id or "").strip()
    if not controller_id:
        raise ControllerAcceptanceError("controller_id is required.")

    details = preflight_data.get("details") or {}
    promotion = details.get("controller_promotion") or {}
    if promotion.get("status") != "controller_confirmation_required":
        raise ControllerAcceptanceError(
            "Current preflight truth is not controller_confirmation_required."
        )

    project = _resolve_project(db_session, project_key)
    task_anchor = _latest_task_anchor(db_session, project.project_id)
    if task_anchor is None:
        raise ControllerAcceptanceError(
            "Runtime project has no task anchor for controller acceptance event recording."
        )

    preflight_shape = _preflight_shape(preflight_data)
    latest = _latest_scope_decision(db_session, project.project_id)
    if latest is not None and _decision_matches_preflight(latest, preflight_shape):
        return {
            "recorded": False,
            "idempotent_reuse": True,
            "rejected": False,
            "decision_id": str(latest.decision_id),
            "decision_scope": DECISION_SCOPE,
            "outcome": _enum_value(latest.outcome),
            "status": _enum_value(latest.status),
            "target_status": (latest.extra or {}).get("target_status"),
            "basis": (latest.extra or {}).get("basis"),
            "superseded": False,
            "supersedes_decision_id": None,
            "event_recorded": False,
            "work_context_updated": False,
            "project_id": str(project.project_id),
            "project_key": project.project_key,
            "task_anchor_id": str(task_anchor.task_id),
            "truth_boundary": {
                "inspect_only": False,
                "mutates_acceptance": True,
                "records_controller_decision": True,
                "implies_canonical_accepted": False,
            },
        }

    now = datetime.now(timezone.utc)
    basis = preflight_shape.get("basis")
    target_status = preflight_shape.get("target_status")
    host = preflight_shape.get("host")
    port = preflight_shape.get("port")
    launch = details.get("canonical_launch") or {}
    title = (summary or "").strip() or _default_summary(basis, host, port)
    final_rationale = (
        (rationale or "").strip()
        or "Controller reviewed current preflight basis and recorded narrow acceptance."
    )

    if latest is not None and latest.status == RuntimeDecisionStatus.FINAL:
        latest.status = RuntimeDecisionStatus.SUPERSEDED

    metadata = {
        "basis": basis,
        "target_status": target_status,
        "controller_acceptability": details.get("controller_acceptability"),
        "controller_promotion": promotion,
        "host": host,
        "port": port,
        "launch_mode": launch.get("launch_mode"),
        "launcher_path": launch.get("launcher_path"),
        "service_entry_path": launch.get("service_entry_path"),
        "project_key": project.project_key,
        "task_anchor_reason": "latest_runtime_task_in_project",
    }

    decision = RuntimeDecision(
        project_id=project.project_id,
        task_id=task_anchor.task_id,
        decision_scope=DECISION_SCOPE,
        title=title,
        summary=title,
        rationale=final_rationale,
        outcome=RuntimeDecisionOutcome.ADOPT,
        status=RuntimeDecisionStatus.FINAL,
        supersedes_decision_id=latest.decision_id if latest is not None else None,
        created_by_kind=RuntimeOwnerKind.CONTROLLER,
        created_by_id=controller_id,
        finalized_at=now,
        extra=metadata,
    )
    db_session.add(decision)
    db_session.flush()

    event = RuntimeTaskEvent(
        project_id=project.project_id,
        task_id=task_anchor.task_id,
        event_type=EVENT_TYPE,
        triggered_by_kind=RuntimeOwnerKind.CONTROLLER,
        triggered_by_id=controller_id,
        reason=title,
        payload={
            "decision_id": str(decision.decision_id),
            "decision_scope": DECISION_SCOPE,
            "target_status": target_status,
            "basis": basis,
            "project_key": project.project_key,
            "task_anchor_reason": "latest_runtime_task_in_project",
        },
    )
    db_session.add(event)
    db_session.flush()

    context = reconstruct_runtime_work_context(db_session, str(project.project_id))
    persisted = persist_reconstructed_work_context(db_session, context)
    align_project_current_work_context(
        db_session, str(project.project_id), str(persisted.work_context_id)
    )

    return {
        "recorded": True,
        "idempotent_reuse": False,
        "rejected": False,
        "decision_id": str(decision.decision_id),
        "decision_scope": DECISION_SCOPE,
        "outcome": _enum_value(decision.outcome),
        "status": _enum_value(decision.status),
        "target_status": target_status,
        "basis": basis,
        "superseded": latest is not None,
        "supersedes_decision_id": str(latest.decision_id) if latest is not None else None,
        "event_recorded": True,
        "work_context_updated": True,
        "project_id": str(project.project_id),
        "project_key": project.project_key,
        "task_anchor_id": str(task_anchor.task_id),
        "truth_boundary": {
            "inspect_only": False,
            "mutates_acceptance": True,
            "records_controller_decision": True,
            "implies_canonical_accepted": False,
        },
    }
