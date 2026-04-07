from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROLE = "code-review-agent"


def emit_json(payload: dict) -> None:
    data = json.dumps(payload, ensure_ascii=False)
    try:
        print(data)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((data + "\n").encode("utf-8"))


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "task"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a bounded qoder review bundle.")
    parser.add_argument("--cwd", default=".", help="Workspace directory.")
    parser.add_argument("--task-id", required=True, help="Review task identifier.")
    parser.add_argument("--title", required=True, help="Short review title.")
    parser.add_argument("--problem-type", default="patch_review", help="Normalized problem type label.")
    parser.add_argument("--priority", default="P1", help="P0 | P1 | P2")
    parser.add_argument("--target-brief", required=True, help="Path to the implementation brief.")
    parser.add_argument("--target-result", required=True, help="Path to the implementation result file.")
    parser.add_argument("--target-files", nargs="*", default=[], help="Files changed by the implementation task.")
    parser.add_argument("--validation", nargs="*", default=[], help="Validation/check bullets.")
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve()
    base = cwd / ".runtime" / "delegation"
    briefs_dir = base / "briefs"
    contexts_dir = base / "contexts"
    results_dir = base / "results"
    done_dir = base / "done"
    for directory in (briefs_dir, contexts_dir, results_dir, done_dir):
        directory.mkdir(parents=True, exist_ok=True)

    safe_name = slugify(args.task_id)
    brief_path = briefs_dir / f"{safe_name}.md"
    context_path = contexts_dir / f"{safe_name}.md"
    result_path = results_dir / f"{safe_name}.md"
    done_path = done_dir / f"{safe_name}.json"
    role_path = (cwd / ".qoder" / "agents" / f"{ROLE}.md").resolve()

    brief_lines = [
        "# Delegation Brief",
        "",
        f"task_id: {args.task_id}",
        f"title: {args.title}",
        "task_type: review",
        f"problem_type: {args.problem_type}",
        f"priority: {args.priority}",
        f"role: {ROLE}",
        "",
        "## Goal",
        "- Review the implementation patch for correctness, scope discipline, regressions, and validation quality.",
        "",
        "## Scope",
        "- Allowed to read:",
        f"  - {Path(args.target_brief).resolve()}",
        f"  - {Path(args.target_result).resolve()}",
        *[f"  - {Path(item).resolve()}" for item in args.target_files],
        "- Out of scope:",
        "  - editing project files",
        "  - changing task scope",
        "  - making final acceptance decisions",
        "",
        "## Constraints",
        "- Findings first, if any.",
        "- Focus on blockers, regressions, incorrect assumptions, and validation gaps.",
        "- Do not broaden into architecture redesign.",
        "- Use UTF-8.",
        "",
        "## Expected Output",
        "- Findings",
        "- Open Questions",
        "- Validation Gaps",
        "- Recommendation: accept | accept_with_changes | reject",
        "",
        "## Validation",
        *([f"- {item}" for item in args.validation] or ["- Review the provided result and changed files only."]),
        "",
        "## Stop Conditions",
        "- Stop if the patch cannot be reviewed without files outside the declared scope.",
        "",
        "## Version / Context Refs",
        "- D:\\code\\MyAttention\\AGENTS.md",
        f"- {role_path}",
        "",
    ]
    brief_path.write_text("\n".join(brief_lines), encoding="utf-8", newline="\n")

    context_lines = [
        f"# Context Packet: {args.task_id}",
        "",
        "## Review Target",
        f"- Brief: {Path(args.target_brief).resolve()}",
        f"- Result: {Path(args.target_result).resolve()}",
        *[f"- File: {Path(item).resolve()}" for item in args.target_files],
        "",
    ]
    context_path.write_text("\n".join(context_lines), encoding="utf-8", newline="\n")

    if not result_path.exists():
        result_path.write_text(
            "\n".join(
                [
                    f"# {args.task_id}",
                    "",
                    "## Findings",
                    "",
                    "## Open Questions",
                    "",
                    "## Validation Gaps",
                    "",
                    "## Recommendation",
                    "",
                ]
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if not done_path.exists():
        done_path.write_text(
            json.dumps(
                {
                    "task_id": args.task_id,
                    "status": "pending",
                    "result_file": str(result_path),
                    "commit_hash": "",
                    "timestamp": "",
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )

    emit_json(
        {
            "task_id": args.task_id,
            "role": ROLE,
            "brief": str(brief_path),
            "context": str(context_path),
            "result": str(result_path),
            "done": str(done_path),
            "launch_command": [
                sys.executable,
                str((cwd / "scripts" / "qoder" / "qoder_delegate.py").resolve()),
                "--cwd",
                str(cwd),
                "--task-id",
                args.task_id,
                "--brief",
                str(brief_path),
                "--context",
                str(context_path),
                "--result",
                str(result_path),
                "--done",
                str(done_path),
                "--role",
                ROLE,
                "--mode",
                "agent",
                "--reuse-window",
            ],
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
