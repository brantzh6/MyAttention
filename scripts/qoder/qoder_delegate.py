from __future__ import annotations

import argparse
import json
import shutil
import subprocess
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


def resolve_qoder() -> str:
    binary = shutil.which("qoder")
    if binary:
        return binary
    raise FileNotFoundError("qoder executable not found")


def build_prompt(
    brief_path: Path,
    context_path: Path,
    result_path: Path,
    done_path: Path,
    task_id: str,
    role: str,
) -> str:
    return "\n".join(
        [
            "You are executing a bounded coding task for MyAttention.",
            "Do not broaden scope.",
            "Read only the provided brief and context files as your task definition.",
            f"Operate according to the role contract: {role}",
            "",
            f"Task ID: {task_id}",
            f"Brief file: {brief_path}",
            f"Context file: {context_path}",
            f"Required result file: {result_path}",
            f"Required done signal file: {done_path}",
            "",
            "Execution rules:",
            "- Follow the brief exactly.",
            "- Keep the patch narrow.",
            "- Do not change backend behavior if the brief is UI-only.",
            "- Do not add dependencies.",
            "- Use UTF-8.",
            "- Run the validation commands required by the brief.",
            "- Write a UTF-8 Markdown result file at the required result path.",
            "- After writing the result file, write a UTF-8 JSON done signal file at the required done path.",
            "- The done signal must include: task_id, status, result_file, commit_hash, timestamp.",
            "- Status must be one of: completed, blocked, failed.",
            "",
            "The result file must contain these sections:",
            "1. Task ID",
            "2. Summary",
            "3. Files Changed",
            "4. Commit Hash",
            "5. Validation Run",
            "6. Known Risks",
            "7. Recommendation",
            "",
            "If blocked, still write both files. The result file must clearly state the blocker instead of guessing.",
        ]
    ) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch a bounded qoder CLI delegation task.")
    parser.add_argument("--cwd", default=".", help="Workspace directory.")
    parser.add_argument("--task-id", required=True, help="Delegation task identifier.")
    parser.add_argument("--brief", required=True, help="Path to the task brief.")
    parser.add_argument("--context", required=True, help="Path to the context packet.")
    parser.add_argument("--result", required=True, help="Path where qoder must write the result file.")
    parser.add_argument("--done", required=True, help="Path where qoder must write the done JSON signal.")
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
    done_path = Path(args.done).resolve()
    role_path = (cwd / ROLE_FILE_MAP[args.role]).resolve()
    result_path.parent.mkdir(parents=True, exist_ok=True)
    done_path.parent.mkdir(parents=True, exist_ok=True)

    prompt = build_prompt(brief_path, context_path, result_path, done_path, args.task_id, args.role)
    cmd = [
        resolve_qoder(),
        "chat",
        "-",
        "--mode",
        args.mode,
        "-a",
        str(brief_path),
        "-a",
        str(context_path),
        "-a",
        str(role_path),
    ]
    if args.reuse_window and not args.new_window:
        cmd.append("--reuse-window")
    if args.new_window:
        cmd.append("--new-window")

    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        input=prompt,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )

    emit_json(
        {
            "task_id": args.task_id,
            "cwd": str(cwd),
            "brief": str(brief_path),
            "context": str(context_path),
            "role": args.role,
            "role_file": str(role_path),
            "result": str(result_path),
            "done": str(done_path),
            "mode": args.mode,
            "launched": result.returncode == 0,
            "stdout": (result.stdout or "").strip(),
            "stderr": (result.stderr or "").strip(),
            "note": "Qoder CLI launched the delegated task. Review the result file after qoder completes the work.",
        }
    )
    return 0 if result.returncode == 0 else result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
