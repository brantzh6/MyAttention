from __future__ import annotations

import json
from pathlib import Path


REQUIRED_HEADERS = [
    "## Task ID",
    "## Summary",
    "## Files Changed",
    "## Commit Hash",
    "## Validation Run",
    "## Known Risks",
    "## Recommendation",
]


def is_result_complete(text: str) -> bool:
    if not all(header in text for header in REQUIRED_HEADERS):
        return False
    placeholder_markers = [
        "\n## Summary\n\n## Files Changed",
        "\n## Files Changed\n\n## Commit Hash",
        "\n## Commit Hash\n\n## Validation Run",
        "\n## Validation Run\n\n## Known Risks",
        "\n## Known Risks\n\n## Recommendation",
    ]
    return not any(marker in text for marker in placeholder_markers)


def read_done_status(done_path: str | Path) -> dict:
    path = Path(done_path)
    if not path.exists():
        return {"status": "missing"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"status": "invalid", "error": str(exc)}
    required = {"task_id", "status", "result_file", "commit_hash", "timestamp"}
    if not required.issubset(payload.keys()):
        return {"status": "invalid", "error": "missing required keys", "payload": payload}
    return {"status": "ok", "payload": payload}
