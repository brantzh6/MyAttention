from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROLE_FILE_MAP = {
    "coding-agent": ".qoder/agents/coding-agent.md",
    "code-review-agent": ".qoder/agents/code-review-agent.md",
    "test-fixer-agent": ".qoder/agents/test-fixer-agent.md",
    "refactor-agent": ".qoder/agents/refactor-agent.md",
    "architect-agent": ".qoder/agents/architect-agent.md",
}


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
    parser = argparse.ArgumentParser(description="Create a bounded qoder task bundle (brief/context/result paths).")
    parser.add_argument("--cwd", default=".", help="Workspace directory.")
    parser.add_argument("--task-id", required=True, help="Delegation task identifier.")
    parser.add_argument("--title", required=True, help="Short task title.")
    parser.add_argument("--role", default="coding-agent", choices=sorted(ROLE_FILE_MAP.keys()))
    parser.add_argument("--task-type", default="implementation", help="implementation | review | analysis | validation")
    parser.add_argument("--problem-type", required=True, help="Normalized problem type label.")
    parser.add_argument("--priority", default="P1", help="P0 | P1 | P2")
    parser.add_argument("--goal", required=True, help="Specific expected outcome.")
    parser.add_argument("--scope-allowed", nargs="+", required=True, help="Files allowed to change.")
    parser.add_argument("--scope-read", nargs="*", default=[], help="Files allowed to read.")
    parser.add_argument("--out-of-scope", nargs="*", default=[], help="Explicit out-of-scope items.")
    parser.add_argument("--inputs", nargs="*", default=[], help="Input bullets.")
    parser.add_argument("--constraints", nargs="*", default=[], help="Constraint bullets.")
    parser.add_argument("--validation", nargs="*", default=[], help="Validation command/check bullets.")
    parser.add_argument("--stop-conditions", nargs="*", default=[], help="Stop condition bullets.")
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

    brief_lines = [
        "# Delegation Brief",
        "",
        f"task_id: {args.task_id}",
        f"title: {args.title}",
        f"task_type: {args.task_type}",
        f"problem_type: {args.problem_type}",
        f"priority: {args.priority}",
        f"role: {args.role}",
        "",
        "## Goal",
        f"- {args.goal}",
        "",
        "## Scope",
        "- Allowed to change:",
        *[f"  - {item}" for item in args.scope_allowed],
        "- Allowed to read:",
        *([f"  - {item}" for item in args.scope_read] or ["  - D:\\code\\MyAttention\\docs\\CURRENT_MAINLINE_HANDOFF.md"]),
        "- Out of scope:",
        *([f"  - {item}" for item in args.out_of_scope] or ["  - backend API contracts", "  - DB schema"]),
        "",
        "## Inputs",
        *([f"- {item}" for item in args.inputs] or ["- Use the current mainline handoff and task-specific context only."]),
        "",
        "## Constraints",
        *([f"- {item}" for item in args.constraints] or [
            "- Keep the patch narrow.",
            "- Do not broaden scope.",
            "- Use UTF-8.",
            "- If data is insufficient, stop and report instead of guessing.",
        ]),
        "",
        "## Expected Output",
        "- Summary",
        "- Files Changed",
        "- Commit Hash",
        "- Validation Run",
        "- Known Risks",
        "- Recommendation: accept | accept_with_changes | reject",
        "",
        "## Validation",
        *([f"- {item}" for item in args.validation] or ["- Run the task-specific validation required by the brief."]),
        "",
        "## Stop Conditions",
        *([f"- {item}" for item in args.stop_conditions] or ["- Stop if the task requires schema changes or backend contract changes."]),
        "",
        "## Version / Context Refs",
        "- D:\\code\\MyAttention\\docs\\CURRENT_MAINLINE_HANDOFF.md",
        "- D:\\code\\MyAttention\\AGENTS.md",
        f"- {str((cwd / ROLE_FILE_MAP[args.role]).resolve())}",
        "",
    ]
    brief_path.write_text("\n".join(brief_lines), encoding="utf-8", newline="\n")

    context_lines = [
        f"# Context Packet: {args.task_id}",
        "",
        "## Mainline Reminder",
        "- Improve source intelligence quality.",
        "- Keep active work surface understandable.",
        "- Do not broaden scope beyond the task brief.",
        "",
        "## Role Contract",
        str((cwd / ROLE_FILE_MAP[args.role]).resolve()),
        "",
        "## Additional Allowed Reads",
        *([f"- {item}" for item in args.scope_read] or ["- D:\\code\\MyAttention\\docs\\CURRENT_MAINLINE_HANDOFF.md"]),
        "",
    ]
    context_path.write_text("\n".join(context_lines), encoding="utf-8", newline="\n")

    if not result_path.exists():
        result_path.write_text(
            "\n".join(
                [
                    f"# {args.task_id}",
                    "",
                    "## Task ID",
                    args.task_id,
                    "",
                    "## Summary",
                    "",
                    "## Files Changed",
                    "",
                    "## Commit Hash",
                    "",
                    "## Validation Run",
                    "",
                    "## Known Risks",
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
            "role": args.role,
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
                args.role,
                "--mode",
                "agent",
                "--reuse-window",
            ],
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
