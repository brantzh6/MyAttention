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
    allowed_writes: list[Path],
    lane: str | None,
    reasoning_mode: str | None,
    sandbox_identity: str | None,
    sandbox_kind: str | None,
    capability_profile: str | None,
    network_policy: str | None,
) -> str:
    write_rules = []
    if allowed_writes:
        write_rules.extend(
            [
                "- You may modify only the explicitly allowed project files listed below.",
                "- Do not create or modify any other project files.",
                "- After project edits, still write exactly one UTF-8 JSON result file at the output path.",
                "",
                "Allowed project file writes:",
                *[f"- {path}" for path in allowed_writes],
            ]
        )
    else:
        write_rules.extend(
            [
                "- Produce exactly one UTF-8 JSON file at the output path.",
                "- Do not write any other project files.",
            ]
        )
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
            "- Do not wrap JSON in markdown fences.",
            *(["- Treat lane metadata as part of the task contract.", f"- lane: {lane}"] if lane else []),
            *(["- Use the requested reasoning mode for this task.", f"- reasoning_mode: {reasoning_mode}"] if reasoning_mode else []),
            *(["- sandbox_identity: {0}".format(sandbox_identity)] if sandbox_identity else []),
            *(["- sandbox_kind: {0}".format(sandbox_kind)] if sandbox_kind else []),
            *(["- capability_profile: {0}".format(capability_profile)] if capability_profile else []),
            *(["- network_policy: {0}".format(network_policy)] if network_policy else []),
            *write_rules,
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
    lane: str | None,
    reasoning_mode: str | None,
    sandbox_identity: str | None,
    sandbox_kind: str | None,
    capability_profile: str | None,
    write_scope: list[Path],
    network_policy: str | None,
) -> subprocess.CompletedProcess[str]:
    command = [
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
    ]
    if lane:
        command.extend(["--lane", lane])
    if reasoning_mode:
        command.extend(["--reasoning-mode", reasoning_mode])
    if sandbox_identity:
        command.extend(["--sandbox-identity", sandbox_identity])
    if sandbox_kind:
        command.extend(["--sandbox-kind", sandbox_kind])
    if capability_profile:
        command.extend(["--capability-profile", capability_profile])
    if network_policy:
        command.extend(["--network-policy", network_policy])
    for path in write_scope:
        command.extend(["--write-scope", str(path)])
    return subprocess.run(
        command,
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
    parser.add_argument(
        "--allowed-write",
        action="append",
        default=[],
        help="Project file path that the delegate is allowed to modify. Repeat for multiple files.",
    )
    parser.add_argument("--lane", default=None, help="Machine-readable lane label for this delegation.")
    parser.add_argument("--reasoning-mode", default="high", help="Requested reasoning / thinking depth for this delegation.")
    parser.add_argument("--sandbox-identity", default=None, help="Machine-readable sandbox identity.")
    parser.add_argument("--sandbox-kind", default="openclaw_workspace", help="Machine-readable sandbox kind.")
    parser.add_argument("--capability-profile", default=None, help="Explicit capability profile override.")
    parser.add_argument("--write-scope", action="append", default=[], help="Machine-readable write scope item. Repeat for multiple values.")
    parser.add_argument("--network-policy", default=None, help="Machine-readable network policy intent.")
    parser.add_argument("--wait-for-output", type=int, default=30, help="Seconds to wait for output file after prompt completes.")
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve()
    brief_path = Path(args.brief).resolve()
    context_path = Path(args.context).resolve()
    output_path = Path(args.output).resolve()
    prompt_path = Path(args.prompt_file).resolve()
    allowed_writes = [Path(path).resolve() for path in args.allowed_write]

    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_scope = [Path(path).resolve() for path in args.write_scope] if args.write_scope else allowed_writes
    sandbox_identity = args.sandbox_identity or f"{args.sandbox_kind}:{args.agent_alias}:{args.session}"

    capability_profile = args.capability_profile
    if capability_profile is None and args.reasoning_mode == "high":
        if args.lane == "coding":
            capability_profile = "coding_high_reasoning"
        elif args.lane == "review":
            capability_profile = "review_high_reasoning"
    network_policy = args.network_policy
    if network_policy is None:
        if capability_profile == "review_high_reasoning" or args.lane == "review":
            network_policy = "disabled"
        elif capability_profile == "coding_high_reasoning" or args.lane == "coding":
            network_policy = "restricted"

    prompt_text = build_prompt(brief_path, context_path, output_path, args.output_schema, allowed_writes, args.lane, args.reasoning_mode, sandbox_identity, args.sandbox_kind, capability_profile, network_policy)
    prompt_path.write_text(prompt_text, encoding="utf-8", newline="\n")

    result = run_delegate(cwd, args.agent_alias, args.session, prompt_path, args.timeout, args.lane, args.reasoning_mode, sandbox_identity, args.sandbox_kind, capability_profile, write_scope, network_policy)
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
                    "lane": args.lane,
                    "reasoning_mode": args.reasoning_mode,
                    "sandbox_identity": sandbox_identity,
                    "sandbox_kind": args.sandbox_kind,
                    "capability_profile": capability_profile,
                    "write_scope": [str(path) for path in write_scope],
                    "network_policy": network_policy,
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
