from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def resolve_acpx_command() -> list[str]:
    direct = shutil.which("acpx")
    if direct:
        return [direct]
    npm_bin = Path(os.environ.get("APPDATA", "")) / "npm" / "acpx.cmd"
    if npm_bin.exists():
        return [str(npm_bin)]
    raise FileNotFoundError("acpx executable not found")


def run_acpx(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*resolve_acpx_command(), *args],
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def require_ok(result: subprocess.CompletedProcess[str], step: str) -> str:
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or f"{step} failed"
        raise RuntimeError(f"{step}: {message}")
    return result.stdout.strip()


def ensure_session(session: str, cwd: Path) -> dict[str, Any]:
    result = run_acpx(
        ["--format", "json", "openclaw", "sessions", "ensure", "--name", session],
        cwd,
    )
    stdout = require_ok(result, "sessions ensure")
    return json.loads(stdout)


def send_prompt(session: str, prompt: str, cwd: Path) -> None:
    result = run_acpx(
        ["openclaw", "prompt", "-s", session, prompt],
        cwd,
    )
    require_ok(result, "prompt submit")


def fetch_history(session: str, limit: int, cwd: Path) -> dict[str, Any]:
    result = run_acpx(
        ["--format", "json", "openclaw", "sessions", "history", session, "--limit", str(limit)],
        cwd,
    )
    stdout = require_ok(result, "sessions history")
    return json.loads(stdout)


def fetch_session(session: str, cwd: Path) -> dict[str, Any]:
    result = run_acpx(
        ["--format", "json", "openclaw", "sessions", "show", session],
        cwd,
    )
    stdout = require_ok(result, "sessions show")
    return json.loads(stdout)


def find_latest_assistant(entries: list[dict[str, Any]]) -> dict[str, Any] | None:
    for entry in reversed(entries):
        if entry.get("role") == "assistant":
            return entry
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Submit a delegated task through acpx/openclaw and recover the result.")
    parser.add_argument("prompt", nargs="?", help="Task prompt to delegate.")
    parser.add_argument("--file", help="Read prompt text from a UTF-8 file.")
    parser.add_argument("--session", default="myattention-coder", help="Named acpx session to use.")
    parser.add_argument("--cwd", default=".", help="Workspace directory.")
    parser.add_argument("--timeout", type=int, default=120, help="Seconds to wait for a result.")
    parser.add_argument("--poll-interval", type=float, default=2.0, help="Polling interval in seconds.")
    parser.add_argument("--history-limit", type=int, default=20, help="How many history entries to fetch.")
    args = parser.parse_args()
    if bool(args.prompt) == bool(args.file):
        parser.error("Provide exactly one of: prompt or --file")

    cwd = Path(args.cwd).resolve()
    prompt_text = args.prompt
    if args.file:
        prompt_text = Path(args.file).read_text(encoding="utf-8")
    ensure_session(args.session, cwd)
    before = fetch_session(args.session, cwd)
    before_ts = before.get("updated_at") or before.get("lastUsedAt") or ""

    send_prompt(args.session, prompt_text, cwd)

    deadline = time.time() + args.timeout
    while time.time() < deadline:
        session_info = fetch_session(args.session, cwd)
        updated_at = session_info.get("updated_at") or session_info.get("lastUsedAt") or ""
        history = fetch_history(args.session, args.history_limit, cwd)
        latest = find_latest_assistant(history.get("entries", []))
        if latest and latest.get("timestamp", "") >= before_ts and updated_at >= before_ts:
            print(
                json.dumps(
                    {
                        "session": args.session,
                        "cwd": str(cwd),
                        "assistant": latest,
                        "history": history,
                        "session_info": session_info,
                    },
                    ensure_ascii=False,
                )
            )
            return 0
        time.sleep(args.poll_interval)

    raise TimeoutError(f"Timed out waiting for delegated result in session {args.session}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise
