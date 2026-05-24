"""Bridge OpenClaw PM triggers into bounded Codex controller runs."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ops" / "state"
BRIDGE_DIR = ROOT / "ops" / "bridge"
RUN_DIR = BRIDGE_DIR / "runs"
TASKS_DIR = ROOT / "tasks" / "codex"
PROMPT_PATH = ROOT / "ops" / "codex" / "controller_wakeup_prompt.md"
LEASE_PATH = STATE_DIR / "codex_controller_lease.json"
LOCK_PATH = STATE_DIR / "codex_controller_lease.lock"
AGENT_RUNTIME_DIR = Path("D:/code/_agent-runtimes")
MAX_STDERR_CHARS = 12000
VALID_TRIGGER_REASONS = {
    "mainline_stalled",
    "invalid_gate",
    "runtime_not_ready",
    "review_pending",
    "runner_not_ready",
    "dirty_tree_gate",
    "controller_bridge_escalation",
}


def codex_command() -> str:
    for candidate in ("codex.cmd", "codex.exe", "codex"):
        resolved = shutil.which(candidate)
        if resolved and not resolved.lower().endswith(".ps1"):
            return resolved
    return "codex"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(value: datetime | None = None) -> str:
    return (value or now_utc()).replace(microsecond=0).isoformat()


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def read_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        return default or {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def pid_is_running(pid: object) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    tmp.replace(path)


def lease_is_active(lease: dict) -> bool:
    if lease.get("status") not in {"running", "running_detached", "dispatching"}:
        return False
    expires_at = parse_time(lease.get("expires_at"))
    if not (expires_at and expires_at > now_utc()):
        return False
    if lease.get("status") == "running_detached" and "codex_pid" in lease:
        return pid_is_running(lease.get("codex_pid"))
    return True


def update_trigger(path_text: str | None, bridge: dict) -> None:
    if not path_text:
        return
    path = Path(path_text)
    if not path.exists():
        return
    data = read_json(path)
    data["bridge"] = bridge
    write_json(path, data)


def validate_trigger(path_text: str | None) -> list[str]:
    if not path_text:
        return []
    path = Path(path_text)
    if not path.exists():
        return [f"trigger file does not exist: {path}"]

    try:
        data = read_json(path)
    except json.JSONDecodeError as exc:
        return [f"trigger JSON is invalid: {exc}"]

    required = [
        "schema_version",
        "trigger_id",
        "created_at",
        "source",
        "decision",
        "reason",
        "evidence",
        "requested_controller_action",
        "forbidden_actions",
    ]
    errors = [f"missing required field: {key}" for key in required if key not in data]

    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if data.get("source") != "openclaw-ike-pm":
        errors.append("source must be openclaw-ike-pm")
    if data.get("decision") != "notify_controller":
        errors.append("decision must be notify_controller")
    if data.get("reason") not in VALID_TRIGGER_REASONS:
        errors.append("reason is not allowed")
    if not isinstance(data.get("evidence"), list) or not data.get("evidence"):
        errors.append("evidence must be a non-empty array")
    if not isinstance(data.get("forbidden_actions"), list) or not data.get(
        "forbidden_actions"
    ):
        errors.append("forbidden_actions must be a non-empty array")

    return errors


def acquire_lease(run_id: str, args: argparse.Namespace) -> tuple[bool, dict]:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    lease = read_json(LEASE_PATH)

    if LOCK_PATH.exists() and lease_is_active(lease) and not args.force:
        return False, lease

    if LOCK_PATH.exists() and not lease_is_active(lease):
        try:
            LOCK_PATH.unlink()
        except FileNotFoundError:
            pass

    if not args.force:
        try:
            fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(run_id)
                handle.write("\n")
        except FileExistsError:
            return False, read_json(LEASE_PATH)

    expires_at = now_utc() + timedelta(seconds=args.lease_seconds)
    lease = {
        "schema_version": 1,
        "status": "running",
        "run_id": run_id,
        "source": args.source,
        "reason": args.reason,
        "trigger": args.trigger,
        "started_at": iso_utc(),
        "expires_at": iso_utc(expires_at),
        "mode": args.mode,
    }
    write_json(LEASE_PATH, lease)
    return True, lease


def release_lease(run_id: str, status: str, result_path: Path | None) -> None:
    lease = read_json(LEASE_PATH)
    if lease.get("run_id") == run_id:
        lease["status"] = status
        lease["completed_at"] = iso_utc()
        if result_path:
            lease["result_path"] = str(result_path)
        write_json(LEASE_PATH, lease)

    if LOCK_PATH.exists():
        try:
            if LOCK_PATH.read_text(encoding="utf-8").strip() == run_id:
                LOCK_PATH.unlink()
        except OSError:
            pass


def build_prompt(args: argparse.Namespace, run_id: str, output_path: Path) -> str:
    if args.mode == "smoke":
        return (
            "You are a Codex bridge smoke test. Output exactly "
            "CODEX_BRIDGE_SMOKE_OK and do not inspect files, run tools, "
            "or edit anything."
        )

    base_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    trigger_text = ""
    if args.trigger and Path(args.trigger).exists():
        trigger_text = Path(args.trigger).read_text(encoding="utf-8")

    return f"""{base_prompt}

## Bridge Invocation

- bridge_run_id: `{run_id}`
- bridge_source: `{args.source}`
- bridge_reason: `{args.reason}`
- trigger_path: `{args.trigger or "none"}`
- required_result_artifact: `{output_path}`

## Trigger Content

```json
{trigger_text or "{}"}
```
"""


def build_codex_command(output_path: Path) -> list[str]:
    return [
        codex_command(),
        "exec",
        "-C",
        str(ROOT),
        "--add-dir",
        str(AGENT_RUNTIME_DIR),
        "--full-auto",
        "-s",
        "workspace-write",
        "--json",
        "-o",
        str(output_path),
        "-",
    ]


def run_codex(args: argparse.Namespace, run_id: str) -> tuple[int, dict]:
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = TASKS_DIR / f"openclaw_codex_controller_run_{run_id}.md"
    jsonl_path = RUN_DIR / f"{run_id}.jsonl"
    prompt = build_prompt(args, run_id, output_path)
    cmd = build_codex_command(output_path)

    if args.dry_run:
        return 0, {
            "status": "dry_run",
            "cmd": cmd,
            "prompt_preview": prompt[:1200],
            "output_path": str(output_path),
        }

    completed = subprocess.run(
        cmd,
        input=prompt,
        text=True,
        capture_output=True,
        timeout=args.timeout_seconds,
        cwd=str(ROOT),
    )
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    jsonl_path.write_text(completed.stdout, encoding="utf-8", newline="\n")

    stderr_path = None
    if completed.stderr:
        stderr_path = RUN_DIR / f"{run_id}.stderr.txt"
        stderr_text = completed.stderr
        if len(stderr_text) > MAX_STDERR_CHARS:
            stderr_text = (
                stderr_text[:MAX_STDERR_CHARS]
                + "\n\n[stderr truncated by openclaw_codex_bridge.py]\n"
            )
        stderr_path.write_text(stderr_text, encoding="utf-8", newline="\n")

    return completed.returncode, {
        "status": "completed" if completed.returncode == 0 else "failed",
        "cmd": cmd,
        "returncode": completed.returncode,
        "output_path": str(output_path),
        "jsonl_path": str(jsonl_path),
        "stderr_path": str(stderr_path) if stderr_path else None,
    }


def start_codex_detached(args: argparse.Namespace, run_id: str) -> dict:
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    output_path = TASKS_DIR / f"openclaw_codex_controller_run_{run_id}.md"
    jsonl_path = RUN_DIR / f"{run_id}.jsonl"
    stderr_path = RUN_DIR / f"{run_id}.stderr.txt"
    stdin_path = RUN_DIR / f"{run_id}.prompt.txt"
    prompt = build_prompt(args, run_id, output_path)
    stdin_path.write_text(prompt, encoding="utf-8", newline="\n")

    cmd = build_codex_command(output_path)
    stdin_handle = stdin_path.open("r", encoding="utf-8")
    stdout_handle = jsonl_path.open("w", encoding="utf-8", newline="\n")
    stderr_handle = stderr_path.open("w", encoding="utf-8", newline="\n")

    try:
        process = subprocess.Popen(
            cmd,
            stdin=stdin_handle,
            stdout=stdout_handle,
            stderr=stderr_handle,
            cwd=str(ROOT),
            text=True,
            creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
        )
    finally:
        stdin_handle.close()
        stdout_handle.close()
        stderr_handle.close()

    return {
        "status": "started_detached",
        "cmd": cmd,
        "pid": process.pid,
        "output_path": str(output_path),
        "jsonl_path": str(jsonl_path),
        "stderr_path": str(stderr_path),
        "prompt_path": str(stdin_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["wake", "smoke"], required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--trigger")
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    parser.add_argument("--lease-seconds", type=int, default=7200)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--detached", action="store_true")
    args = parser.parse_args()

    run_id = "openclaw_codex_" + now_utc().strftime("%Y%m%d_%H%M%S")
    result_path = RUN_DIR / f"{run_id}.json"

    if args.dry_run:
        code, payload = run_codex(args, run_id)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return code

    trigger_errors = validate_trigger(args.trigger) if args.mode == "wake" else []
    if trigger_errors:
        payload = {
            "schema_version": 1,
            "run_id": run_id,
            "status": "invalid_trigger",
            "created_at": iso_utc(),
            "source": args.source,
            "reason": args.reason,
            "trigger": args.trigger,
            "errors": trigger_errors,
        }
        write_json(result_path, payload)
        update_trigger(
            args.trigger,
            {
                "status": "failed_invalid_trigger",
                "run_id": run_id,
                "updated_at": iso_utc(),
                "result_path": str(result_path),
                "errors": trigger_errors,
            },
        )
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 3

    acquired, lease = acquire_lease(run_id, args)
    if not acquired:
        payload = {
            "schema_version": 1,
            "run_id": run_id,
            "status": "busy",
            "created_at": iso_utc(),
            "source": args.source,
            "reason": args.reason,
            "active_lease": lease,
        }
        write_json(result_path, payload)
        update_trigger(
            args.trigger,
            {
                "status": "deferred_busy",
                "run_id": run_id,
                "updated_at": iso_utc(),
                "result_path": str(result_path),
            },
        )
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 2

    update_trigger(
        args.trigger,
        {
            "status": "dispatching",
            "run_id": run_id,
            "updated_at": iso_utc(),
        },
    )

    status = "failed"
    try:
        if args.detached:
            codex_result = start_codex_detached(args, run_id)
            status = "running_detached"
            payload = {
                "schema_version": 1,
                "run_id": run_id,
                "status": "dispatched",
                "dispatch_mode": "detached",
                "created_at": lease.get("started_at"),
                "completed_at": iso_utc(),
                "source": args.source,
                "reason": args.reason,
                "trigger": args.trigger,
                "codex": codex_result,
            }
            write_json(result_path, payload)
            update_trigger(
                args.trigger,
                {
                    "status": "dispatched",
                    "run_id": run_id,
                    "updated_at": iso_utc(),
                    "result_path": str(result_path),
                    "dispatch_mode": "detached",
                },
            )
            lease["status"] = "running_detached"
            lease["result_path"] = str(result_path)
            lease["codex_output_path"] = codex_result.get("output_path")
            lease["codex_pid"] = codex_result.get("pid")
            write_json(LEASE_PATH, lease)
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0

        code, codex_result = run_codex(args, run_id)
        status = "dispatched" if code == 0 else "failed"
        payload = {
            "schema_version": 1,
            "run_id": run_id,
            "status": status,
            "created_at": lease.get("started_at"),
            "completed_at": iso_utc(),
            "source": args.source,
            "reason": args.reason,
            "trigger": args.trigger,
            "codex": codex_result,
        }
        write_json(result_path, payload)
        update_trigger(
            args.trigger,
            {
                "status": status,
                "run_id": run_id,
                "updated_at": iso_utc(),
                "result_path": str(result_path),
            },
        )
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return code
    except subprocess.TimeoutExpired as exc:
        payload = {
            "schema_version": 1,
            "run_id": run_id,
            "status": "timeout",
            "created_at": lease.get("started_at"),
            "completed_at": iso_utc(),
            "source": args.source,
            "reason": args.reason,
            "trigger": args.trigger,
            "timeout_seconds": args.timeout_seconds,
            "error": str(exc),
        }
        write_json(result_path, payload)
        update_trigger(
            args.trigger,
            {
                "status": "failed",
                "run_id": run_id,
                "updated_at": iso_utc(),
                "result_path": str(result_path),
            },
        )
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 124
    finally:
        if not args.detached:
            release_lease(run_id, status, result_path)


if __name__ == "__main__":
    sys.exit(main())
