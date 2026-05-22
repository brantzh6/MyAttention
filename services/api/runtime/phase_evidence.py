"""
IKE Runtime v0 - Delegated Phase Evidence Helpers

These helpers do not change runtime DB truth. They provide a narrow,
controller-facing read model over delegated result artifacts so recent runtime
phases can distinguish:

- real delegated evidence
- controller fallback coverage
- missing lane evidence

The goal is to support R1-H without inventing new runtime objects.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


FALLBACK_MARKERS = (
    "controller fallback",
    "controller-reviewed",
    "controller review",
    "no independent delegated",
    "not durably recovered",
    "fallback testing",
    "fallback evolution",
    "fallback review",
)


@dataclass
class RuntimePhaseLaneEvidence:
    lane: str
    result_path: str | None
    evidence_state: str
    recommendation: str | None
    notes: list[str] = field(default_factory=list)


@dataclass
class RuntimePhaseEvidenceSummary:
    phase_id: str
    delegated_lanes: list[RuntimePhaseLaneEvidence] = field(default_factory=list)
    fallback_lanes: list[RuntimePhaseLaneEvidence] = field(default_factory=list)
    missing_lanes: list[RuntimePhaseLaneEvidence] = field(default_factory=list)


def _flatten_strings(value: Any) -> list[str]:
    flattened: list[str] = []
    if isinstance(value, str):
        flattened.append(value)
    elif isinstance(value, dict):
        for nested in value.values():
            flattened.extend(_flatten_strings(nested))
    elif isinstance(value, list):
        for nested in value:
            flattened.extend(_flatten_strings(nested))
    return flattened


def _classify_result_payload(payload: dict[str, Any]) -> tuple[str, list[str]]:
    status = str(payload.get("status") or "").strip().lower()
    if status == "pending":
        return "missing", ["Result file is still pending."]

    text_values = [text.lower() for text in _flatten_strings(payload)]
    fallback_notes = [
        text
        for text in _flatten_strings(payload)
        if any(marker in text.lower() for marker in FALLBACK_MARKERS)
    ]
    if fallback_notes:
        return "fallback", fallback_notes

    return "delegated", []


def summarize_runtime_phase_evidence(
    results_dir: str | Path,
    phase_id: str,
) -> RuntimePhaseEvidenceSummary:
    phase = phase_id.lower()
    results_root = Path(results_dir)
    summary = RuntimePhaseEvidenceSummary(phase_id=phase_id.upper())

    for lane_num, lane_name in (
        ("1", "coding"),
        ("2", "review"),
        ("3", "testing"),
        ("4", "evolution"),
    ):
        pattern = f"ike-runtime-{phase}{lane_num}-*.json"
        matches = sorted(results_root.glob(pattern))
        if not matches:
            evidence = RuntimePhaseLaneEvidence(
                lane=lane_name,
                result_path=None,
                evidence_state="missing",
                recommendation=None,
                notes=["No durable result file found."],
            )
            summary.missing_lanes.append(evidence)
            continue

        result_path = matches[0]
        payload = json.loads(result_path.read_text(encoding="utf-8"))
        evidence_state, notes = _classify_result_payload(payload)
        evidence = RuntimePhaseLaneEvidence(
            lane=lane_name,
            result_path=str(result_path),
            evidence_state=evidence_state,
            recommendation=payload.get("recommendation"),
            notes=notes,
        )
        if evidence_state == "delegated":
            summary.delegated_lanes.append(evidence)
        elif evidence_state == "fallback":
            summary.fallback_lanes.append(evidence)
        else:
            summary.missing_lanes.append(evidence)

    return summary
