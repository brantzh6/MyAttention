import json
from pathlib import Path

from runtime.phase_evidence import summarize_runtime_phase_evidence


class TestRuntimePhaseEvidence:
    def _write_json(self, directory: Path, name: str, payload: dict) -> None:
        directory.joinpath(name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def test_summarize_phase_distinguishes_delegated_fallback_and_missing(self, tmp_path):
        self._write_json(
            tmp_path,
            "ike-runtime-r1-g1-review-provenance-coding-glm.json",
            {
                "summary": "Coding lane completed.",
                "recommendation": "accept_with_changes",
            },
        )
        self._write_json(
            tmp_path,
            "ike-runtime-r1-g2-review-provenance-review-kimi.json",
            {
                "validation_gaps": [
                    "Independent delegated review evidence was not durably recovered for R1-G2."
                ],
                "recommendation": "accept_with_changes",
            },
        )
        self._write_json(
            tmp_path,
            "ike-runtime-r1-g3-review-provenance-test.json",
            {
                "status": "pending",
                "recommendation": "",
            },
        )
        self._write_json(
            tmp_path,
            "ike-runtime-r1-g4-review-provenance-evolution-kimi.json",
            {
                "summary": "Evolution lane completed.",
                "recommendation": "accept_with_changes",
            },
        )

        summary = summarize_runtime_phase_evidence(tmp_path, "r1-g")

        assert [lane.lane for lane in summary.delegated_lanes] == ["coding", "evolution"]
        assert [lane.lane for lane in summary.fallback_lanes] == ["review"]
        assert [lane.lane for lane in summary.missing_lanes] == ["testing"]
        assert "not durably recovered" in summary.fallback_lanes[0].notes[0].lower()
        assert "pending" in summary.missing_lanes[0].notes[0].lower()

    def test_missing_result_file_is_reported_as_missing(self, tmp_path):
        self._write_json(
            tmp_path,
            "ike-runtime-r1-f1-controller-read-surface-coding-glm.json",
            {
                "summary": "Coding lane completed.",
                "recommendation": "accept_with_changes",
            },
        )

        summary = summarize_runtime_phase_evidence(tmp_path, "r1-f")

        assert [lane.lane for lane in summary.delegated_lanes] == ["coding"]
        assert [lane.lane for lane in summary.missing_lanes] == [
            "review",
            "testing",
            "evolution",
        ]
