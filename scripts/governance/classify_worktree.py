#!/usr/bin/env python3
"""Read-only dirty worktree classifier for governance review prep."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


BUDGET = {
    "max_entries": 20,
    "max_groups": 3,
}

GROUP_ORDER = [
    "review_automation",
    "flywheel_readiness",
    "visual_control_surface",
    "source_intelligence",
    "evolution_ui",
    "governance_docs",
    "review_packs_archives",
    "other_docs",
    "other_code",
]


def normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip()


def status_path(line: str) -> str:
    raw_path = line[3:] if len(line) > 3 else ""
    if " -> " in raw_path:
        raw_path = raw_path.split(" -> ", 1)[1]
    return normalize_path(raw_path.strip().strip('"'))


def run_git_status(cwd: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(cwd), "status", "--short"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "git status failed"
        raise RuntimeError(message)
    return [line for line in result.stdout.splitlines() if line.strip()]


def classify_path(path: str) -> str:
    lower_path = path.lower()
    name = Path(path).name.lower()

    if lower_path.startswith("scripts/governance/") or "review_automation" in lower_path:
        return "review_automation"

    if "review_pack" in lower_path or "review-packs" in lower_path:
        return "review_packs_archives"
    if lower_path.startswith("archive/") or lower_path.startswith("archives/"):
        return "review_packs_archives"
    if "/archive/" in lower_path or "/archives/" in lower_path:
        return "review_packs_archives"

    if "source_intelligence" in lower_path or "source-intelligence" in lower_path:
        return "source_intelligence"
    if "source intelligence" in lower_path:
        return "source_intelligence"

    if "flywheel" in lower_path or "readiness" in lower_path:
        return "flywheel_readiness"

    if "evolution" in lower_path and any(
        token in lower_path for token in ("ui", "frontend", "component", "surface")
    ):
        return "evolution_ui"

    if any(
        token in lower_path
        for token in ("visual_control", "control_surface", "control-surface")
    ):
        return "visual_control_surface"
    if lower_path.startswith(("app/control", "src/app/control", "frontend/control")):
        return "visual_control_surface"

    if lower_path.startswith("docs/") or name.endswith(".md"):
        if any(
            token in lower_path
            for token in (
                "governance",
                "worktree",
                "classifier",
                "dirty_worktree",
                "current_mainline",
                "current_active_artifacts",
                "current_review_queue",
                "change_management",
                "version_management",
                "project_agent_harness_contract",
            )
        ):
            return "governance_docs"
        return "other_docs"

    return "other_code"


def build_report(status_lines: list[str]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, str]]] = {group: [] for group in GROUP_ORDER}
    for line in status_lines:
        path = status_path(line)
        group = classify_path(path)
        groups[group].append(
            {
                "status": line[:2],
                "path": path,
                "raw": line,
            }
        )

    active_groups = [group for group, entries in groups.items() if entries]
    total = len(status_lines)
    if total == 0:
        recommendation = "clean"
    elif total <= BUDGET["max_entries"] and len(active_groups) <= BUDGET["max_groups"]:
        recommendation = "within_budget"
    else:
        recommendation = "requires_scoped_review_prep"

    return {
        "total": total,
        "groups": groups,
        "recommendation": recommendation,
        "budget": {
            **BUDGET,
            "groups_with_entries": len(active_groups),
        },
    }


def print_human(report: dict[str, Any], limit: int) -> None:
    print("Dirty Worktree Classification")
    print(f"total: {report['total']}")
    print(f"recommendation: {report['recommendation']}")
    print(
        "budget: "
        f"max_entries={report['budget']['max_entries']}, "
        f"max_groups={report['budget']['max_groups']}, "
        f"groups_with_entries={report['budget']['groups_with_entries']}"
    )
    print()
    print("groups:")
    for group in GROUP_ORDER:
        entries = report["groups"][group]
        print(f"- {group}: {len(entries)}")
        for entry in entries[:limit]:
            print(f"  - {entry['status']} {entry['path']}")
        if len(entries) > limit:
            print(f"  - ... {len(entries) - limit} more")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify git status --short entries into governance groups."
    )
    parser.add_argument(
        "--cwd",
        default=".",
        help="Repository working directory to inspect.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print parseable JSON instead of a human-readable report.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum entries to show per group in human-readable output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cwd = Path(args.cwd).resolve()
    try:
        report = build_report(run_git_status(cwd))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_human(report, max(args.limit, 0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
