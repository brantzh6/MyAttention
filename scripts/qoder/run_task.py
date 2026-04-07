from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from result_check import is_result_complete, read_done_status


def emit_json(payload: dict) -> None:
    data = json.dumps(payload, ensure_ascii=False)
    try:
        print(data)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((data + "\n").encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Create, launch, and wait for a bounded qoder task.")
    parser.add_argument("--cwd", default=".", help="Workspace directory.")
    parser.add_argument("--task-id", required=True, help="Delegation task identifier.")
    parser.add_argument("--title", required=True, help="Short task title.")
    parser.add_argument("--role", default="coding-agent", choices=["coding-agent", "code-review-agent", "test-fixer-agent", "refactor-agent", "architect-agent"])
    parser.add_argument("--task-type", default="implementation")
    parser.add_argument("--problem-type", required=True)
    parser.add_argument("--priority", default="P1")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--scope-allowed", nargs="+", required=True)
    parser.add_argument("--scope-read", nargs="*", default=[])
    parser.add_argument("--out-of-scope", nargs="*", default=[])
    parser.add_argument("--inputs", nargs="*", default=[])
    parser.add_argument("--constraints", nargs="*", default=[])
    parser.add_argument("--validation", nargs="*", default=[])
    parser.add_argument("--stop-conditions", nargs="*", default=[])
    parser.add_argument("--timeout", type=int, default=1800, help="Max seconds to wait for completion.")
    parser.add_argument("--poll-interval", type=int, default=10, help="Seconds between result checks.")
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve()
    bundle_script = cwd / "scripts" / "qoder" / "create_task_bundle.py"
    launch_script = cwd / "scripts" / "qoder" / "launch_bundle.py"

    create_cmd = [
        sys.executable,
        str(bundle_script),
        "--cwd",
        str(cwd),
        "--task-id",
        args.task_id,
        "--title",
        args.title,
        "--role",
        args.role,
        "--task-type",
        args.task_type,
        "--problem-type",
        args.problem_type,
        "--priority",
        args.priority,
        "--goal",
        args.goal,
        "--scope-allowed",
        *args.scope_allowed,
        "--scope-read",
        *args.scope_read,
        "--out-of-scope",
        *args.out_of_scope,
        "--inputs",
        *args.inputs,
        "--constraints",
        *args.constraints,
        "--validation",
        *args.validation,
        "--stop-conditions",
        *args.stop_conditions,
    ]
    created = subprocess.run(
        create_cmd,
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if created.returncode != 0:
        sys.stderr.write(created.stderr or created.stdout or "failed to create bundle\n")
        return created.returncode

    try:
        bundle = json.loads(created.stdout.strip())
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"invalid bundle json: {exc}\n")
        return 1

    bundle_path = cwd / ".runtime" / "delegation" / "bundles" / f"{args.task_id}.json"
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")

    launch_cmd = [
        sys.executable,
        str(launch_script),
        "--bundle-json",
        str(bundle_path),
    ]
    launched = subprocess.run(
        launch_cmd,
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if launched.returncode != 0:
        sys.stderr.write(launched.stderr or launched.stdout or "failed to launch qoder\n")
        return launched.returncode

    result_path = Path(bundle["result"])
    done_path = Path(bundle["done"])
    deadline = time.time() + args.timeout
    last_text = ""
    last_done = {}
    while time.time() < deadline:
        last_done = read_done_status(done_path)
        if result_path.exists():
            try:
                text = result_path.read_text(encoding="utf-8")
            except Exception as exc:  # noqa: BLE001
                sys.stderr.write(f"failed to read result file: {exc}\n")
                return 1
            last_text = text
            if last_done.get("status") == "ok":
                payload = last_done["payload"]
                task_status = payload.get("status")
                if task_status in {"completed", "blocked", "failed"} and is_result_complete(text):
                    emit_json(
                        {
                            "task_id": args.task_id,
                            "bundle": str(bundle_path),
                            "result_file": str(result_path),
                            "done_file": str(done_path),
                            "status": task_status,
                            "bundle_launch": json.loads(launched.stdout.strip()) if launched.stdout.strip() else {},
                            "done_payload": payload,
                            "result": text,
                        }
                    )
                    return 0 if task_status == "completed" else 2
            elif is_result_complete(text):
                emit_json(
                    {
                        "task_id": args.task_id,
                        "bundle": str(bundle_path),
                        "result_file": str(result_path),
                        "status": "completed",
                        "bundle_launch": json.loads(launched.stdout.strip()) if launched.stdout.strip() else {},
                        "result": text,
                    }
                )
                return 0
        time.sleep(args.poll_interval)

    emit_json(
        {
            "task_id": args.task_id,
            "bundle": str(bundle_path),
            "result_file": str(result_path),
            "done_file": str(done_path),
            "status": "pending_or_blocked",
            "last_done": last_done,
            "last_result_snapshot": last_text[-2000:],
            "bundle_launch": json.loads(launched.stdout.strip()) if launched.stdout.strip() else {},
            "note": "Timed out waiting for qoder to finish and populate the result file.",
        }
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
