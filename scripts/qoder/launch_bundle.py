from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def emit_json(payload: dict) -> None:
    data = json.dumps(payload, ensure_ascii=False)
    try:
        print(data)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((data + "\n").encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch a qoder bundle from a bundle JSON payload.")
    parser.add_argument("--bundle-json", required=True, help="JSON file produced by create_task_bundle or create_review_bundle.")
    args = parser.parse_args()

    bundle_path = Path(args.bundle_json).resolve()
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    cmd = payload["launch_command"]
    result = subprocess.run(
        cmd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    emit_json(
        {
            "bundle": str(bundle_path),
            "returncode": result.returncode,
            "stdout": (result.stdout or "").strip(),
            "stderr": (result.stderr or "").strip(),
        }
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
