from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def emit_json(payload: dict) -> None:
    data = json.dumps(payload, ensure_ascii=False)
    try:
        print(data)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((data + "\n").encode("utf-8"))


def build_prompt(
    brief_path: Path,
    context_path: Path,
    output_path: Path,
    output_schema: str,
) -> str:
    return "\n".join(
        [
            "Complete this task in one turn.",
            "Do not ask follow-up questions.",
            "Do not scan the workspace beyond the files explicitly listed below.",
            "Use the brief file and context file as the only task context.",
            "",
            "Required files:",
            f"- Brief file: {brief_path}",
            f"- Context file: {context_path}",
            f"- Output file to write: {output_path}",
            "",
            "Execution requirements:",
            "- Read the brief file and the context file.",
            "- Produce exactly one UTF-8 JSON file at the output path.",
            "- Do not wrap JSON in markdown fences.",
            "- Do not write any other project files.",
            "- If you cannot complete the task, still write a JSON object describing the blocker.",
            "",
            "Required JSON schema:",
            output_schema,
            "",
            "Return a short confirmation message after writing the output file.",
        ]
    ) + "\n"


def run_delegate(
    cwd: Path,
    agent_alias: str,
    session: str,
    prompt_file: Path,
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str((cwd / "scripts" / "acpx" / "openclaw_delegate.py").resolve()),
            "--mode",
            "prompt",
            "--agent-alias",
            agent_alias,
            "--cwd",
            str(cwd),
            "--session",
            session,
            "--file",
            str(prompt_file),
            "--timeout",
            str(timeout),
        ],
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a bounded file-based delegation through acpx/openclaw.")
    parser.add_argument("--cwd", default=".", help="Workspace directory.")
    parser.add_argument(
        "--agent-alias",
        default="openclaw-qwen",
        help="acpx agent alias from .acpxrc.json.",
    )
    parser.add_argument("--session", required=True, help="Delegation session name.")
    parser.add_argument("--brief", required=True, help="Path to the brief file.")
    parser.add_argument("--context", required=True, help="Path to the context file.")
    parser.add_argument("--output", required=True, help="Path to the delegated result file.")
    parser.add_argument("--prompt-file", required=True, help="Temporary prompt file path.")
    parser.add_argument("--timeout", type=int, default=180, help="Delegation timeout in seconds.")
    parser.add_argument(
        "--output-schema",
        default='{"summary":"string","results":[]}',
        help="Human-readable JSON schema to embed in the prompt.",
    )
    parser.add_argument("--wait-for-output", type=int, default=30, help="Seconds to wait for output file after prompt completes.")
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve()
    brief_path = Path(args.brief).resolve()
    context_path = Path(args.context).resolve()
    output_path = Path(args.output).resolve()
    prompt_path = Path(args.prompt_file).resolve()

    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    prompt_text = build_prompt(brief_path, context_path, output_path, args.output_schema)
    prompt_path.write_text(prompt_text, encoding="utf-8", newline="\n")

    result = run_delegate(cwd, args.agent_alias, args.session, prompt_path, args.timeout)
    if result.returncode != 0:
        sys.stderr.write(result.stderr or result.stdout or "delegation failed\n")
        return result.returncode

    deadline = time.time() + args.wait_for_output
    while time.time() < deadline:
        if output_path.exists():
            try:
                payload = json.loads(output_path.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001
                sys.stderr.write(json.dumps({"error": f"invalid output file: {exc}"}, ensure_ascii=False) + "\n")
                return 1
            emit_json(
                {
                    "session": args.session,
                    "output_file": str(output_path),
                    "result": payload,
                }
            )
            return 0
        time.sleep(1)

    sys.stderr.write(
        json.dumps(
            {
                "error": "delegated output file not created",
                "output_file": str(output_path),
                "delegate_stdout": result.stdout.strip(),
                "delegate_stderr": result.stderr.strip(),
            },
            ensure_ascii=False,
        )
        + "\n"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
