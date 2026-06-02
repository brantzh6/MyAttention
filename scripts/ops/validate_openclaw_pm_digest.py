#!/usr/bin/env python3
"""Validate OpenClaw PM run digest invariants without third-party packages."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


STALE_THRESHOLD_MINUTES = 240
VALID_DECISIONS = {
    "quiet",
    "triggered",
    "bridge_busy",
    "bridge_failed",
    "invalid_state",
}
VALID_STATUSES = {"ok", "warning", "error"}


def fail(message: str) -> int:
    print(f"INVALID: {message}", file=sys.stderr)
    return 1


def require_string(data: dict[str, Any], key: str) -> str | None:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        return None
    return value


def validate(path: Path) -> int:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - exercised by CLI use
        return fail(f"cannot read JSON: {exc}")

    required = [
        "schema_version",
        "run_id",
        "checked_at",
        "source",
        "cron_job_id",
        "decision",
        "status",
        "evidence",
        "next_expected_run",
        "controller_action_needed",
    ]
    missing = [key for key in required if key not in data]
    if missing:
        return fail(f"missing required fields: {', '.join(missing)}")

    if data["schema_version"] != 1:
        return fail("schema_version must be 1")

    run_id = require_string(data, "run_id")
    if run_id is None or not run_id.startswith("openclaw_pm_run_"):
        return fail("run_id must start with openclaw_pm_run_")

    if data.get("source") != "openclaw-ike-pm":
        return fail("source must be openclaw-ike-pm")

    decision = data.get("decision")
    if decision not in VALID_DECISIONS:
        return fail(f"invalid decision: {decision}")

    status = data.get("status")
    if status not in VALID_STATUSES:
        return fail(f"invalid status: {status}")

    evidence = data.get("evidence")
    if not isinstance(evidence, list) or not evidence or not all(
        isinstance(item, str) and item for item in evidence
    ):
        return fail("evidence must be a non-empty string array")

    controller_action_needed = data.get("controller_action_needed")
    if not isinstance(controller_action_needed, bool):
        return fail("controller_action_needed must be boolean")

    staleness = data.get("staleness_minutes")
    if not isinstance(staleness, (int, float)):
        return fail("staleness_minutes must be a number")

    if staleness >= STALE_THRESHOLD_MINUTES:
        if decision == "quiet":
            return fail(
                "decision quiet is forbidden when "
                f"staleness_minutes={staleness} >= {STALE_THRESHOLD_MINUTES}"
            )
        if controller_action_needed is not True:
            return fail(
                "controller_action_needed must be true when "
                f"staleness_minutes={staleness} >= {STALE_THRESHOLD_MINUTES}"
            )

    if decision == "quiet" and controller_action_needed:
        return fail("quiet digest cannot require controller action")

    print(f"VALID: {path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("digest", type=Path)
    args = parser.parse_args()
    return validate(args.digest)


if __name__ == "__main__":
    raise SystemExit(main())
