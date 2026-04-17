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


def emit_json(payload: dict[str, Any], stream: str = "stdout") -> None:
    data = json.dumps(payload, ensure_ascii=False)
    target = sys.stdout if stream == "stdout" else sys.stderr
    try:
        print(data, file=target)
    except UnicodeEncodeError:
        buffer = sys.stdout.buffer if stream == "stdout" else sys.stderr.buffer
        buffer.write((data + "\n").encode("utf-8"))


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


def run_acpx_stream(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
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


def ensure_session(agent_alias: str, session: str, cwd: Path) -> dict[str, Any]:
    result = run_acpx(
        ["--format", "json", agent_alias, "sessions", "ensure", "--name", session],
        cwd,
    )
    stdout = require_ok(result, "sessions ensure")
    return json.loads(stdout)


def send_prompt(agent_alias: str, session: str, prompt: str, cwd: Path) -> None:
    result = run_acpx(
        [agent_alias, "prompt", "-s", session, prompt],
        cwd,
    )
    require_ok(result, "prompt submit")


def send_prompt_file(agent_alias: str, session: str, prompt_file: str, cwd: Path) -> None:
    result = run_acpx(
        [agent_alias, "prompt", "-s", session, "-f", prompt_file],
        cwd,
    )
    require_ok(result, "prompt submit")


def run_exec(agent_alias: str, prompt_file: str, cwd: Path) -> dict[str, Any]:
    result = run_acpx_stream(
        ["--format", "json", "--cwd", str(cwd), agent_alias, "exec", "-f", prompt_file],
        cwd,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "exec failed"
        raise RuntimeError(f"exec submit: {message}")
    stdout = result.stdout.strip()
    if not stdout:
        return {"raw_stdout": "", "raw_stderr": result.stderr.strip(), "mode": "exec"}
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        payload = {"raw_stdout": stdout, "raw_stderr": result.stderr.strip(), "mode": "exec"}
    return payload


def fetch_history(agent_alias: str, session: str, limit: int, cwd: Path) -> dict[str, Any]:
    result = run_acpx(
        ["--format", "json", agent_alias, "sessions", "history", session, "--limit", str(limit)],
        cwd,
    )
    stdout = require_ok(result, "sessions history")
    return json.loads(stdout)


def fetch_session(agent_alias: str, session: str, cwd: Path) -> dict[str, Any]:
    result = run_acpx(
        ["--format", "json", agent_alias, "sessions", "show", session],
        cwd,
    )
    stdout = require_ok(result, "sessions show")
    return json.loads(stdout)


def try_fetch_session(agent_alias: str, session: str, cwd: Path) -> dict[str, Any] | None:
    result = run_acpx(
        ["--format", "json", agent_alias, "sessions", "show", session],
        cwd,
    )
    if result.returncode != 0:
        return None
    stdout = result.stdout.strip()
    if not stdout:
        return None
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return None


def find_latest_assistant(entries: list[dict[str, Any]]) -> dict[str, Any] | None:
    for entry in reversed(entries):
        if entry.get("role") == "assistant":
            return entry
    return None


def default_capability_profile(lane: str | None, reasoning_mode: str | None) -> str | None:
    if reasoning_mode == "high":
        if lane == "coding":
            return "coding_high_reasoning"
        if lane == "review":
            return "review_high_reasoning"
    return None


def default_network_policy(lane: str | None, capability_profile: str | None) -> str | None:
    if capability_profile == "review_high_reasoning":
        return "disabled"
    if capability_profile == "coding_high_reasoning":
        return "restricted"
    if lane == "review":
        return "disabled"
    if lane == "coding":
        return "restricted"
    return None


def default_sandbox_identity(agent_alias: str, session: str, sandbox_kind: str | None) -> str | None:
    if not sandbox_kind:
        return None
    return f"{sandbox_kind}:{agent_alias}:{session}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Submit a delegated task through acpx/openclaw and recover the result.")
    parser.add_argument("prompt", nargs="?", help="Task prompt to delegate.")
    parser.add_argument("--file", help="Read prompt text from a UTF-8 file.")
    parser.add_argument("--mode", choices=["prompt", "exec"], default="prompt", help="Delegation mode.")
    parser.add_argument(
        "--agent-alias",
        default="openclaw-qwen",
        help="acpx agent alias from .acpxrc.json (for example: openclaw-qwen, openclaw-glm, openclaw-reviewer).",
    )
    parser.add_argument("--session", default="ike-coder", help="Named acpx session to use.")
    parser.add_argument("--cwd", default=".", help="Workspace directory.")
    parser.add_argument("--timeout", type=int, default=120, help="Seconds to wait for a result.")
    parser.add_argument("--poll-interval", type=float, default=2.0, help="Polling interval in seconds.")
    parser.add_argument("--history-limit", type=int, default=20, help="How many history entries to fetch.")
    parser.add_argument("--lane", default=None, help="Machine-readable lane label for this delegation.")
    parser.add_argument("--reasoning-mode", default="high", help="Requested reasoning / thinking depth for this delegation.")
    parser.add_argument("--sandbox-identity", default=None, help="Machine-readable sandbox identity.")
    parser.add_argument("--sandbox-kind", default="openclaw_workspace", help="Machine-readable sandbox kind.")
    parser.add_argument("--capability-profile", default=None, help="Explicit capability profile override.")
    parser.add_argument("--write-scope", action="append", default=[], help="Machine-readable write scope item. Repeat for multiple values.")
    parser.add_argument("--network-policy", default=None, help="Machine-readable network policy intent.")
    args = parser.parse_args()
    if bool(args.prompt) == bool(args.file):
        parser.error("Provide exactly one of: prompt or --file")

    cwd = Path(args.cwd).resolve()
    agent_alias = args.agent_alias
    capability_profile = args.capability_profile or default_capability_profile(args.lane, args.reasoning_mode)
    network_policy = args.network_policy or default_network_policy(args.lane, capability_profile)
    sandbox_identity = args.sandbox_identity or default_sandbox_identity(agent_alias, args.session, args.sandbox_kind)
    prompt_text = args.prompt
    if args.file:
        prompt_text = Path(args.file).read_text(encoding="utf-8")

    if args.mode == "exec":
        payload = run_exec(agent_alias, str(Path(args.file).resolve()) if args.file else "-", cwd)
        emit_json(payload)
        return 0

    ensure_session(agent_alias, args.session, cwd)
    before = try_fetch_session(agent_alias, args.session, cwd) or {}
    before_ts = before.get("updated_at") or before.get("lastUsedAt") or ""

    if args.file:
        send_prompt_file(agent_alias, args.session, str(Path(args.file).resolve()), cwd)
    else:
        send_prompt(agent_alias, args.session, prompt_text, cwd)

    deadline = time.time() + args.timeout
    while time.time() < deadline:
        session_info = fetch_session(agent_alias, args.session, cwd)
        updated_at = session_info.get("updated_at") or session_info.get("lastUsedAt") or ""
        history = fetch_history(agent_alias, args.session, args.history_limit, cwd)
        latest = find_latest_assistant(history.get("entries", []))
        if latest and latest.get("timestamp", "") >= before_ts and updated_at >= before_ts:
            emit_json(
                {
                    "agent_alias": agent_alias,
                    "session": args.session,
                    "cwd": str(cwd),
                    "lane": args.lane,
                    "reasoning_mode": args.reasoning_mode,
                    "sandbox_identity": sandbox_identity,
                    "sandbox_kind": args.sandbox_kind,
                    "capability_profile": capability_profile,
                    "write_scope": args.write_scope,
                    "network_policy": network_policy,
                    "assistant": latest,
                    "history": history,
                    "session_info": session_info,
                }
            )
            return 0
        time.sleep(args.poll_interval)

    raise TimeoutError(f"Timed out waiting for delegated result in session {args.session} via {agent_alias}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        emit_json({"error": str(exc)}, stream="stderr")
        raise
