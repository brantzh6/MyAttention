"""
IKE Runtime v0 - Benchmark Bridge Helpers

Narrow R2-B5 bridge from reviewed benchmark artifacts into runtime packet review.
This module does NOT auto-promote benchmark outputs into trusted runtime memory.

Bridge rule:
- benchmark candidate -> runtime pending_review packet
- runtime acceptance remains a separate truth gate
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import UUID

from sqlalchemy import select

from db.models import RuntimeMemoryPacket, RuntimePacketStatus, RuntimeProject
from runtime.memory_packets import create_packet, transition_to_review
from runtime.state_machine import OwnerKind


class BenchmarkBridgeError(ValueError):
    """Raised when benchmark candidate payloads cannot be bridged truthfully."""


@dataclass(frozen=True)
class BenchmarkProceduralCandidate:
    """Validated benchmark-originated procedural-memory candidate."""

    title: str
    lesson: str
    why_it_mattered: str
    how_to_apply: str
    confidence: float
    source_artifact_ref: str
    status: str
    derived_from: dict[str, Any]
    notes: list[str]


def _parse_uuid(value: str | UUID, field_name: str) -> UUID:
    try:
        return UUID(str(value))
    except (TypeError, ValueError) as exc:
        raise BenchmarkBridgeError(f"Invalid {field_name}: {value}") from exc


def _require_non_empty_str(payload: Mapping[str, Any], field_name: str) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise BenchmarkBridgeError(
            f"Benchmark bridge requires non-empty string field '{field_name}'."
        )
    return value.strip()


def validate_benchmark_procedural_candidate(
    payload: Mapping[str, Any],
) -> BenchmarkProceduralCandidate:
    """Validate the narrow reviewed benchmark candidate shape for R2-B5."""
    title = _require_non_empty_str(payload, "title")
    lesson = _require_non_empty_str(payload, "lesson")
    why_it_mattered = _require_non_empty_str(payload, "why_it_mattered")
    how_to_apply = _require_non_empty_str(payload, "how_to_apply")
    source_artifact_ref = _require_non_empty_str(payload, "source_artifact_ref")

    confidence = payload.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
        raise BenchmarkBridgeError(
            "Benchmark bridge requires confidence between 0.0 and 1.0."
        )

    status = payload.get("status")
    if status != "candidate":
        raise BenchmarkBridgeError(
            "Benchmark bridge only accepts reviewed benchmark payloads with status='candidate'."
        )

    derived_from = payload.get("derived_from", {})
    if not isinstance(derived_from, dict) or not derived_from:
        raise BenchmarkBridgeError(
            "Benchmark bridge requires non-empty derived_from metadata."
        )

    notes = payload.get("notes", [])
    if not isinstance(notes, list) or not all(isinstance(note, str) for note in notes):
        raise BenchmarkBridgeError(
            "Benchmark bridge requires notes to be a list of strings."
        )

    return BenchmarkProceduralCandidate(
        title=title,
        lesson=lesson,
        why_it_mattered=why_it_mattered,
        how_to_apply=how_to_apply,
        confidence=float(confidence),
        source_artifact_ref=source_artifact_ref,
        status=status,
        derived_from=dict(derived_from),
        notes=list(notes),
    )


def load_benchmark_procedural_candidate(candidate_path: str | Path) -> dict[str, Any]:
    """Load a reviewed benchmark candidate JSON artifact from disk."""
    path = Path(candidate_path)
    if not path.exists():
        raise BenchmarkBridgeError(
            f"Benchmark candidate artifact does not exist: {path}"
        )
    with path.open("r", encoding="utf-8") as handle:
        try:
            payload = json.load(handle)
        except json.JSONDecodeError as exc:
            raise BenchmarkBridgeError(
                f"Benchmark candidate artifact is not valid JSON: {path}"
            ) from exc
    if not isinstance(payload, dict):
        raise BenchmarkBridgeError(
            f"Benchmark candidate artifact must contain a JSON object: {path}"
        )
    return payload


def import_benchmark_candidate_as_runtime_packet(
    db_session,
    project_id: str,
    payload: Mapping[str, Any],
    *,
    source_artifact_path: str | Path | None = None,
    bridge_actor_id: str = "benchmark_bridge",
) -> RuntimeMemoryPacket:
    """Bridge one reviewed benchmark candidate into runtime pending_review.

    The imported runtime packet is intentionally NOT accepted/trusted.
    Acceptance remains a later runtime review action.
    """
    project_uuid = _parse_uuid(project_id, "project_id")
    project = (
        db_session.execute(
            select(RuntimeProject).where(RuntimeProject.project_id == project_uuid)
        )
        .scalars()
        .one_or_none()
    )
    if project is None:
        raise BenchmarkBridgeError(
            f"Project '{project_id}' does not exist for benchmark bridge import."
        )

    candidate = validate_benchmark_procedural_candidate(payload)
    now = datetime.now(timezone.utc)
    source_path_str = str(Path(source_artifact_path)) if source_artifact_path else None

    bridge_metadata = {
        "bridge": {
            "source_kind": "benchmark_procedural_memory_candidate",
            "source_artifact_ref": candidate.source_artifact_ref,
            "source_artifact_path": source_path_str,
            "bridge_actor": f"runtime:{bridge_actor_id}",
            "bridge_phase": "R2-B5",
            "bridge_imported_at": now.isoformat(),
        },
        "benchmark_candidate": {
            "lesson": candidate.lesson,
            "why_it_mattered": candidate.why_it_mattered,
            "how_to_apply": candidate.how_to_apply,
            "confidence": candidate.confidence,
            "status": candidate.status,
            "derived_from": candidate.derived_from,
            "notes": candidate.notes,
        },
    }
    draft_packet = create_packet(
        project_id=str(project_uuid),
        packet_type="benchmark_procedural_candidate",
        title=candidate.title,
        summary=candidate.lesson,
        created_by_kind=OwnerKind.RUNTIME,
        created_by_id=bridge_actor_id,
        acceptance_trigger="benchmark_bridge_import",
        metadata=bridge_metadata,
        created_at=now,
    )
    review_updates = transition_to_review(
        draft_packet,
        triggered_by_kind=OwnerKind.RUNTIME,
        triggered_by_id=bridge_actor_id,
        trigger_reason="Benchmark candidate imported for runtime review",
    )

    packet_row = RuntimeMemoryPacket(
        memory_packet_id=_parse_uuid(draft_packet.memory_packet_id, "memory_packet_id"),
        project_id=project_uuid,
        task_id=None,
        packet_type=draft_packet.packet_type,
        status=RuntimePacketStatus.PENDING_REVIEW,
        acceptance_trigger=draft_packet.acceptance_trigger,
        title=draft_packet.title,
        summary=draft_packet.summary,
        storage_ref=source_path_str,
        content_hash=None,
        parent_packet_id=None,
        created_by_kind=OwnerKind.RUNTIME,
        created_by_id=bridge_actor_id,
        created_at=now,
        accepted_at=None,
        extra=review_updates["metadata"],
    )
    db_session.add(packet_row)
    db_session.commit()
    return packet_row


def import_benchmark_candidate_into_runtime_project(
    db_session,
    project_key: str,
    payload: Mapping[str, Any],
    *,
    source_artifact_path: str | Path | None = None,
    bridge_actor_id: str = "benchmark_bridge",
) -> RuntimeMemoryPacket:
    """Import one reviewed benchmark candidate by runtime project key.

    This keeps the visible/action surface aligned to runtime truth:
    the project must already exist as a runtime project.
    """
    project = (
        db_session.execute(
            select(RuntimeProject).where(RuntimeProject.project_key == project_key)
        )
        .scalars()
        .one_or_none()
    )
    if project is None:
        raise BenchmarkBridgeError(
            f"Runtime project '{project_key}' does not exist for benchmark bridge import."
        )
    return import_benchmark_candidate_as_runtime_packet(
        db_session,
        str(project.project_id),
        payload,
        source_artifact_path=source_artifact_path,
        bridge_actor_id=bridge_actor_id,
    )
