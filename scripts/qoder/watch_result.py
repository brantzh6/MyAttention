from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from result_check import is_result_complete, read_done_status


def emit_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(description="Watch a qoder delegation result file until it is completed or blocked.")
    parser.add_argument("--result", required=True, help="Result file path.")
    parser.add_argument("--done", help="Done signal JSON file path.")
    parser.add_argument("--timeout", type=int, default=1800, help="Seconds to wait.")
    parser.add_argument("--poll-interval", type=int, default=5, help="Seconds between checks.")
    args = parser.parse_args()

    result_path = Path(args.result).resolve()
    done_path = Path(args.done).resolve() if args.done else None
    deadline = time.time() + args.timeout
    last_text = ""
    last_mtime = None
    last_done = {}

    while time.time() < deadline:
        if done_path:
            last_done = read_done_status(done_path)
        if result_path.exists():
            try:
                text = result_path.read_text(encoding="utf-8")
            except Exception as exc:  # noqa: BLE001
                emit_json({"result": str(result_path), "status": "blocked", "error": str(exc)})
                return 2
            last_text = text
            mtime = result_path.stat().st_mtime
            last_mtime = mtime
            if done_path and last_done.get("status") == "ok":
                payload = last_done["payload"]
                task_status = payload.get("status")
                if task_status in {"completed", "blocked", "failed"} and is_result_complete(text):
                    emit_json(
                        {
                            "result": str(result_path),
                            "done": str(done_path),
                            "status": task_status,
                            "mtime": mtime,
                            "done_payload": payload,
                            "result_text": text,
                        }
                    )
                    return 0 if task_status == "completed" else 2
            elif is_result_complete(text):
                emit_json(
                    {
                        "result": str(result_path),
                        "status": "completed",
                        "mtime": mtime,
                        "result_text": text,
                    }
                )
                return 0
        time.sleep(args.poll_interval)

    emit_json(
        {
            "result": str(result_path),
            "done": str(done_path) if done_path else None,
            "status": "pending_or_blocked",
            "last_mtime": last_mtime,
            "last_done": last_done,
            "last_snapshot": last_text[-2000:],
            "note": "Timed out waiting for qoder to populate a complete result file.",
        }
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
