from __future__ import annotations

import argparse
import json
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare and launch a bounded qoder file delegation.")
    parser.add_argument("--cwd", default=".", help="Workspace directory.")
    parser.add_argument("--task-id", required=True, help="Delegation task identifier.")
    parser.add_argument("--brief", required=True, help="Path to the task brief.")
    parser.add_argument("--context", required=True, help="Path to the context packet.")
    parser.add_argument("--result", required=True, help="Path to the result markdown file.")
    parser.add_argument(
        "--role",
        default="coding-agent",
        choices=sorted(ROLE_FILE_MAP.keys()),
        help="Delegated qoder role contract to attach.",
    )
    parser.add_argument("--mode", default="agent", choices=["ask", "edit", "agent"], help="qoder chat mode.")
    parser.add_argument("--reuse-window", action="store_true", help="Reuse the last active Qoder window.")
    parser.add_argument("--new-window", action="store_true", help="Force a new Qoder window.")
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve()
    brief_path = Path(args.brief).resolve()
    context_path = Path(args.context).resolve()
    result_path = Path(args.result).resolve()
    result_path.parent.mkdir(parents=True, exist_ok=True)

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

    emit_json(
        {
            "task_id": args.task_id,
            "brief": str(brief_path),
            "context": str(context_path),
            "result": str(result_path),
            "role": args.role,
            "role_file": str((cwd / ROLE_FILE_MAP[args.role]).resolve()),
            "next_command": [
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
                "--role",
                args.role,
                "--mode",
                args.mode,
                *(["--reuse-window"] if args.reuse_window else []),
                *(["--new-window"] if args.new_window else []),
            ],
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
