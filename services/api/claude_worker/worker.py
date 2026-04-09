from __future__ import annotations

import argparse
import json
import os
import signal
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Literal, Sequence


DEFAULT_MODEL = "glm-5"
DEFAULT_PERMISSION_MODE = "bypassPermissions"
DEFAULT_WAIT_TIMEOUT_SECONDS = 600
DEFAULT_DETACHED_WAIT_TIMEOUT_SECONDS = 5
DEFAULT_DETACHED_POLL_INTERVAL_SECONDS = 0.25


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_stamp() -> str:
    return _utc_now().strftime("%Y%m%dT%H%M%S")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_claude_binary(preferred: str) -> str:
    if os.name != "nt":
        resolved = shutil.which(preferred)
        return resolved or preferred

    if Path(preferred).suffix.lower() in {".cmd", ".exe", ".bat"}:
        return shutil.which(preferred) or preferred

    for candidate in (f"{preferred}.cmd", f"{preferred}.exe", f"{preferred}.bat", preferred):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return preferred


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _write_text(path: Path, content: str) -> None:
    _ensure_parent(path)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: Any) -> None:
    _write_text(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _append_event(path: Path, event: dict[str, Any]) -> None:
    _ensure_parent(path)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True))
        handle.write("\n")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        raise ValueError("expected a list-like value, got mapping")
    if isinstance(value, (tuple, set)):
        return list(value)
    return [value]


def _load_packet_from_meta(meta: Any, default_model: str, default_permission_mode: str) -> WorkerPacket:
    if not isinstance(meta, dict):
        raise ValueError("meta.json must be a JSON object")

    packet_meta = meta.get("packet")
    if not isinstance(packet_meta, dict):
        raise ValueError("meta.json packet must be a JSON object")

    kind = packet_meta.get("kind", meta.get("kind"))
    if kind not in {"coding", "review"}:
        raise ValueError(f"invalid worker kind in meta.json: {kind}")

    prompt = packet_meta.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("meta.json packet.prompt is required")

    return WorkerPacket(
        kind=kind,
        prompt=prompt,
        cwd=packet_meta.get("cwd", meta.get("cwd")),
        model=packet_meta.get("model", meta.get("model", default_model)),
        permission_mode=packet_meta.get("permission_mode", meta.get("permission_mode", default_permission_mode)),
        task_id=packet_meta.get("task_id", meta.get("task_id")),
        title=packet_meta.get("title", meta.get("title")),
    )


def _schema_for_kind(kind: str) -> dict[str, Any]:
    if kind == "review":
        return {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "findings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "body": {"type": "string"},
                            "file": {"type": "string"},
                            "start": {"type": "integer"},
                            "end": {"type": "integer"},
                            "priority": {"type": "integer"},
                            "confidence": {"type": "number"},
                        },
                        "required": ["title", "body", "file"],
                        "additionalProperties": True,
                    },
                },
                "validation_gaps": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "recommendation": {
                    "type": "string",
                    "enum": ["accept", "accept_with_changes", "reject"],
                },
                "patch_diff": {"type": "string"},
            },
            "required": ["summary", "findings", "validation_gaps", "recommendation"],
            "additionalProperties": True,
        }

    if kind != "coding":
        raise ValueError(f"unknown worker kind: {kind}")

    return {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "files_changed": {
                "type": "array",
                "items": {"type": "string"},
            },
            "validation_run": {"type": "string"},
            "known_risks": {
                "type": "array",
                "items": {"type": "string"},
            },
            "recommendation": {
                "type": "string",
                "enum": ["accept", "accept_with_changes", "reject"],
            },
            "patch_diff": {"type": "string"},
        },
        "required": ["summary", "files_changed", "validation_run", "known_risks", "recommendation"],
        "additionalProperties": True,
    }


def _normalize_base(raw: Any, kind: str) -> dict[str, Any]:
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            raw = {"summary": raw}
    if not isinstance(raw, dict):
        raw = {}

    payload = raw.get("structured_output") if isinstance(raw.get("structured_output"), dict) else raw
    if "result" in raw and payload is raw:
        result = raw["result"]
        if isinstance(result, str):
            try:
                payload = json.loads(result)
            except json.JSONDecodeError:
                payload = {"summary": result}
        elif isinstance(result, dict):
            payload = result
        else:
            payload = {"summary": str(result)}

    recommendation = payload.get("recommendation")
    if recommendation not in {"accept", "accept_with_changes", "reject"}:
        recommendation = "accept_with_changes"

    normalized: dict[str, Any] = {
        "kind": kind,
        "summary": str(payload.get("summary", "")).strip(),
        "recommendation": recommendation,
    }
    normalized["patch_diff"] = str(payload.get("patch_diff", "")).strip()
    normalized["raw_output"] = payload
    normalized["raw_envelope"] = raw
    return normalized


def normalize_coding_result(raw: Any) -> dict[str, Any]:
    normalized = _normalize_base(raw, "coding")
    payload = normalized["raw_output"]
    normalized["files_changed"] = [str(item) for item in _as_list(payload.get("files_changed"))]
    normalized["validation_run"] = str(payload.get("validation_run", "")).strip()
    normalized["known_risks"] = [str(item) for item in _as_list(payload.get("known_risks"))]
    return normalized


def normalize_review_result(raw: Any) -> dict[str, Any]:
    normalized = _normalize_base(raw, "review")
    payload = normalized["raw_output"]
    normalized["findings"] = _as_list(payload.get("findings"))
    normalized["validation_gaps"] = [str(item) for item in _as_list(payload.get("validation_gaps"))]
    return normalized


@dataclass(frozen=True)
class WorkerPacket:
    kind: Literal["coding", "review"]
    prompt: str
    cwd: str | None = None
    model: str = DEFAULT_MODEL
    permission_mode: str = DEFAULT_PERMISSION_MODE
    task_id: str | None = None
    title: str | None = None


@dataclass
class RunRecord:
    run_id: str
    run_dir: Path
    command: list[str]
    packet: WorkerPacket
    process: Any = field(repr=False)


class ClaudeWorkerRuntime:
    def __init__(
        self,
        run_root: str | Path | None = None,
        result_root: str | Path | None = None,
        claude_binary: str = "claude",
        default_model: str = DEFAULT_MODEL,
        default_permission_mode: str = DEFAULT_PERMISSION_MODE,
        wait_timeout_seconds: float = DEFAULT_WAIT_TIMEOUT_SECONDS,
        detached_wait_timeout_seconds: float = DEFAULT_DETACHED_WAIT_TIMEOUT_SECONDS,
        detached_poll_interval_seconds: float = DEFAULT_DETACHED_POLL_INTERVAL_SECONDS,
        launcher: Callable[..., Any] = subprocess.Popen,
    ) -> None:
        self.run_root = Path(run_root or _repo_root() / ".runtime" / "claude-worker" / "runs").resolve()
        self.run_root.mkdir(parents=True, exist_ok=True)
        self.result_root = Path(result_root or _repo_root() / ".runtime" / "delegation" / "results").resolve()
        self.result_root.mkdir(parents=True, exist_ok=True)
        self.claude_binary = _resolve_claude_binary(claude_binary)
        self.default_model = default_model
        self.default_permission_mode = default_permission_mode
        self.wait_timeout_seconds = wait_timeout_seconds
        self.detached_wait_timeout_seconds = detached_wait_timeout_seconds
        self.detached_poll_interval_seconds = detached_poll_interval_seconds
        self.launcher = launcher
        self._records: dict[str, RunRecord] = {}

    def start(self, packet: WorkerPacket) -> RunRecord:
        run_id = f"{_utc_stamp()}-{uuid.uuid4().hex[:8]}"
        run_dir = self.run_root / run_id
        run_dir.mkdir(parents=True, exist_ok=False)

        model = packet.model or self.default_model
        permission_mode = packet.permission_mode or self.default_permission_mode
        schema = _schema_for_kind(packet.kind)
        schema_json = json.dumps(schema, ensure_ascii=False)
        command = [
            self.claude_binary,
            "-p",
            "--output-format",
            "json",
            "--model",
            model,
            "--permission-mode",
            permission_mode,
            "--json-schema",
            schema_json,
            packet.prompt,
        ]

        meta = {
            "run_id": run_id,
            "kind": packet.kind,
            "task_id": packet.task_id,
            "title": packet.title,
            "model": model,
            "permission_mode": permission_mode,
            "claude_binary": self.claude_binary,
            "cwd": packet.cwd,
            "command": command,
            "owner_pid": os.getpid(),
            "ownership_mode": "single-process",
            "detached_wait_contract": {
                "wait_mode": "poll-final-json",
                "abort_requires_owner": True,
                "resume_via": ["fetch", "wait"],
            },
            "created_at": _utc_now().isoformat(),
            "status": "running",
            "packet": {
                "kind": packet.kind,
                "prompt": packet.prompt,
                "cwd": packet.cwd,
                "model": model,
                "permission_mode": permission_mode,
                "task_id": packet.task_id,
                "title": packet.title,
            },
        }
        _write_json(run_dir / "meta.json", meta)
        _append_event(run_dir / "events.ndjson", {"event": "started", "run_id": run_id, "created_at": meta["created_at"]})
        _write_text(run_dir / "summary.md", f"Run {run_id} started for {packet.kind}.\n")
        _write_text(run_dir / "patch.diff", "")

        process = self.launcher(
            command,
            cwd=packet.cwd or None,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        meta["child_pid"] = getattr(process, "pid", None)
        _write_json(run_dir / "meta.json", meta)
        record = RunRecord(run_id=run_id, run_dir=run_dir, command=command, packet=packet, process=process)
        self._records[run_id] = record
        return record

    def wait(self, run_id: str) -> dict[str, Any]:
        record = self._get_record(run_id)
        final_path = record.run_dir / "final.json"
        if record.process is None:
            if final_path.exists():
                return _read_json(final_path)
            return self._detached_wait(record)
        try:
            stdout, stderr = record.process.communicate(timeout=self.wait_timeout_seconds)
        except subprocess.TimeoutExpired:
            terminated = False
            killed = False
            _append_event(
                record.run_dir / "events.ndjson",
                {
                    "event": "wait_timeout",
                    "run_id": run_id,
                    "timeout_seconds": self.wait_timeout_seconds,
                    "at": _utc_now().isoformat(),
                },
            )
            if hasattr(record.process, "terminate"):
                record.process.terminate()
                terminated = True
                _append_event(
                    record.run_dir / "events.ndjson",
                    {"event": "terminate_requested", "run_id": run_id, "at": _utc_now().isoformat()},
                )
            try:
                stdout, stderr = record.process.communicate(timeout=5)
            except Exception:
                if hasattr(record.process, "kill"):
                    record.process.kill()
                    killed = True
                    _append_event(
                        record.run_dir / "events.ndjson",
                        {"event": "kill_requested", "run_id": run_id, "at": _utc_now().isoformat()},
                    )
                try:
                    stdout, stderr = record.process.communicate(timeout=5)
                except Exception:
                    if hasattr(record.process, "wait"):
                        try:
                            record.process.wait(timeout=1)
                        except Exception:
                            pass
                    stdout, stderr = "", ""
            stdout = stdout or ""
            stderr = (stderr or "") + f"\nTimed out after {self.wait_timeout_seconds} seconds"
            return self._finalize(
                record,
                stdout,
                stderr,
                status="failed",
                returncode=124,
                lifecycle={
                    "timeout": True,
                    "terminate_requested": terminated,
                    "kill_requested": killed,
                },
            )
        returncode = self._process_returncode(record.process)
        status = "succeeded" if returncode == 0 else "failed"
        return self._finalize(record, stdout or "", stderr or "", status=status, returncode=returncode)

    def abort(self, run_id: str) -> dict[str, Any]:
        record = self._get_record(run_id)
        final_path = record.run_dir / "final.json"
        if record.process is None:
            if final_path.exists():
                return _read_json(final_path)
            meta = _read_json(record.run_dir / "meta.json")
            owner_pid = meta.get("owner_pid")
            child_pid = meta.get("child_pid")
            terminated, detail = self._terminate_detached_child(child_pid)
            _append_event(
                record.run_dir / "events.ndjson",
                {
                    "event": "detached_abort_requested",
                    "run_id": run_id,
                    "owner_pid": owner_pid,
                    "child_pid": child_pid,
                    "terminated": terminated,
                    "at": _utc_now().isoformat(),
                },
            )
            if not terminated:
                raise RuntimeError(
                    f"Run {run_id} is detached from this process (owner_pid={owner_pid}); detached abort failed: {detail}"
                )
            detached_raw = self._detached_abort_envelope(record.packet.kind, owner_pid=owner_pid, child_pid=child_pid)
            return self._finalize(
                record,
                json.dumps(detached_raw, ensure_ascii=False),
                detail,
                status="aborted",
                returncode=143,
                lifecycle={
                    "detached_abort": True,
                    "owner_pid": owner_pid,
                    "child_pid": child_pid,
                },
            )
        process = record.process
        if hasattr(process, "poll") and process.poll() is None:
            if hasattr(process, "terminate"):
                process.terminate()
            try:
                stdout, stderr = process.communicate(timeout=5)
            except TypeError:
                stdout, stderr = process.communicate()
            except Exception:
                if hasattr(process, "kill"):
                    process.kill()
                try:
                    stdout, stderr = process.communicate(timeout=5)
                except Exception:
                    if hasattr(process, "wait"):
                        try:
                            process.wait(timeout=1)
                        except Exception:
                            pass
                    stdout, stderr = "", ""
        else:
            stdout, stderr = process.communicate()
        return self._finalize(record, stdout or "", stderr or "", status="aborted", returncode=self._process_returncode(process))

    def fetch(self, run_id: str) -> dict[str, Any]:
        record = self._get_record(run_id)
        meta_path = record.run_dir / "meta.json"
        final_path = record.run_dir / "final.json"
        summary_path = record.run_dir / "summary.md"
        patch_path = record.run_dir / "patch.diff"
        events_path = record.run_dir / "events.ndjson"
        return {
            "run_id": run_id,
            "run_dir": str(record.run_dir),
            "meta": _read_json(meta_path) if meta_path.exists() else None,
            "final": _read_json(final_path) if final_path.exists() else None,
            "summary": summary_path.read_text(encoding="utf-8") if summary_path.exists() else None,
            "patch_diff": patch_path.read_text(encoding="utf-8") if patch_path.exists() else None,
            "events": events_path.read_text(encoding="utf-8") if events_path.exists() else None,
        }

    def _detached_wait(self, record: RunRecord) -> dict[str, Any]:
        final_path = record.run_dir / "final.json"
        deadline = _utc_now().timestamp() + max(0.0, self.detached_wait_timeout_seconds)
        while _utc_now().timestamp() < deadline:
            if final_path.exists():
                return _read_json(final_path)
            sleep_seconds = max(0.01, self.detached_poll_interval_seconds)
            if sleep_seconds > 0:
                time.sleep(sleep_seconds)

        meta_path = record.run_dir / "meta.json"
        meta = _read_json(meta_path) if meta_path.exists() else {}
        return {
            "run_id": record.run_id,
            "kind": record.packet.kind,
            "task_id": record.packet.task_id,
            "status": "running",
            "recommendation": "accept_with_changes",
            "detached_wait": {
                "state": "timed_out",
                "owner_pid": meta.get("owner_pid"),
                "child_pid": meta.get("child_pid"),
                "wait_timeout_seconds": self.detached_wait_timeout_seconds,
                "poll_interval_seconds": self.detached_poll_interval_seconds,
                "strategy": meta.get("detached_wait_contract", {}),
            },
            "message": "Run is still owned by another process; retry wait/fetch or query owner process.",
        }

    def _detached_abort_envelope(self, kind: Literal["coding", "review"], owner_pid: Any, child_pid: Any) -> dict[str, Any]:
        summary = f"Detached abort requested for child_pid={child_pid} (owner_pid={owner_pid})."
        if kind == "review":
            return {
                "summary": summary,
                "findings": [],
                "validation_gaps": [],
                "recommendation": "accept_with_changes",
            }
        return {
            "summary": summary,
            "files_changed": [],
            "validation_run": "",
            "known_risks": ["Detached abort finalization does not include child stdout/stderr replay."],
            "recommendation": "accept_with_changes",
        }

    def _terminate_detached_child(self, child_pid: Any) -> tuple[bool, str]:
        if not isinstance(child_pid, int) or child_pid <= 0:
            return False, "invalid child_pid"
        try:
            if os.name == "nt":
                result = subprocess.run(
                    ["taskkill", "/PID", str(child_pid), "/T", "/F"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    detail = (result.stderr or result.stdout or "").strip()
                    return False, detail or f"taskkill failed with code {result.returncode}"
                return True, (result.stdout or "taskkill succeeded").strip()
            os.kill(child_pid, signal.SIGTERM)
            return True, f"SIGTERM sent to pid {child_pid}"
        except Exception as exc:
            return False, str(exc)

    def _get_record(self, run_id: str) -> RunRecord:
        record = self._records.get(run_id)
        if record is not None:
            return record
        meta_path = self.run_root / run_id / "meta.json"
        if not meta_path.exists():
            raise KeyError(f"Unknown run_id: {run_id}")
        try:
            meta = _read_json(meta_path)
            packet = _load_packet_from_meta(meta, self.default_model, self.default_permission_mode)
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            raise ValueError(f"Invalid persisted run metadata for {run_id}: {exc}") from exc
        record = RunRecord(
            run_id=run_id,
            run_dir=self.run_root / run_id,
            command=list(meta.get("command", [])),
            packet=packet,
            process=None,
        )
        self._records[run_id] = record
        return record

    def _process_returncode(self, process: Any) -> int:
        returncode = getattr(process, "returncode", None)
        if returncode is None and hasattr(process, "wait"):
            returncode = process.wait()
        return int(returncode or 0)

    def _finalize(
        self,
        record: RunRecord,
        stdout: str,
        stderr: str,
        *,
        status: str,
        returncode: int,
        lifecycle: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        raw_payload: Any
        try:
            raw_payload = json.loads(stdout) if stdout.strip() else {}
        except json.JSONDecodeError:
            raw_payload = {"summary": stdout.strip(), "raw_stdout": stdout}

        try:
            if record.packet.kind == "review":
                normalized = normalize_review_result(raw_payload)
            else:
                normalized = normalize_coding_result(raw_payload)
            normalization_error = None
        except (TypeError, ValueError) as exc:
            normalization_error = str(exc)
            normalized = {
                "kind": record.packet.kind,
                "summary": f"Invalid structured output: {exc}",
                "recommendation": "reject",
                "patch_diff": "",
                "raw_output": raw_payload,
                "raw_envelope": raw_payload,
            }
            if record.packet.kind == "review":
                normalized["findings"] = []
                normalized["validation_gaps"] = [str(exc)]
            else:
                normalized["files_changed"] = []
                normalized["validation_run"] = ""
                normalized["known_risks"] = [str(exc)]

        final_payload: dict[str, Any] = {
            "run_id": record.run_id,
            "kind": record.packet.kind,
            "task_id": record.packet.task_id,
            "title": record.packet.title,
            "model": record.packet.model,
            "permission_mode": record.packet.permission_mode,
            "status": "failed" if normalization_error is not None else status,
            "returncode": returncode,
            "summary": normalized.get("summary", ""),
            "recommendation": normalized.get("recommendation", "accept_with_changes"),
            "patch_diff": normalized.get("patch_diff", ""),
            "raw_output": normalized.get("raw_output", {}),
            "stdout": stdout,
            "stderr": stderr,
        }
        if lifecycle:
            final_payload["lifecycle"] = lifecycle
        if normalization_error is not None:
            final_payload["normalization_error"] = normalization_error
            if final_payload["returncode"] == 0:
                final_payload["returncode"] = 1
        if record.packet.kind == "review":
            final_payload["findings"] = normalized.get("findings", [])
            final_payload["validation_gaps"] = normalized.get("validation_gaps", [])
        else:
            final_payload["files_changed"] = normalized.get("files_changed", [])
            final_payload["validation_run"] = normalized.get("validation_run", "")
            final_payload["known_risks"] = normalized.get("known_risks", [])

        meta_path = record.run_dir / "meta.json"
        meta = _read_json(meta_path) if meta_path.exists() else {}
        final_status = final_payload["status"]
        final_returncode = final_payload["returncode"]
        meta["status"] = final_status
        meta["returncode"] = final_returncode
        meta["finished_at"] = _utc_now().isoformat()
        _write_json(meta_path, meta)
        _append_event(
            record.run_dir / "events.ndjson",
            {
                "event": "finished" if status != "aborted" else "aborted",
                "run_id": record.run_id,
                "status": final_status,
                "returncode": final_returncode,
                "finished_at": meta["finished_at"],
            },
        )
        _write_json(record.run_dir / "final.json", final_payload)
        self._write_harness_result(record, final_payload)
        summary_lines = [
            f"# Run {record.run_id}",
            "",
            f"- kind: {record.packet.kind}",
            f"- status: {final_status}",
            f"- returncode: {final_returncode}",
            f"- model: {record.packet.model}",
            "",
            normalized.get("summary", "").strip(),
        ]
        _write_text(record.run_dir / "summary.md", "\n".join(summary_lines).strip() + "\n")
        _write_text(record.run_dir / "patch.diff", normalized.get("patch_diff", ""))
        return final_payload

    def _write_harness_result(self, record: RunRecord, final_payload: dict[str, Any]) -> None:
        result_payload: dict[str, Any] = {
            "protocol": "delegation_result.v1",
            "worker": "claude-worker",
            "run_id": record.run_id,
            "task_id": record.packet.task_id,
            "kind": final_payload.get("kind"),
            "status": final_payload.get("status"),
            "recommendation": final_payload.get("recommendation"),
            "summary": final_payload.get("summary", ""),
            "run_dir": str(record.run_dir),
            "artifacts": {
                "meta": str(record.run_dir / "meta.json"),
                "events": str(record.run_dir / "events.ndjson"),
                "final": str(record.run_dir / "final.json"),
                "summary": str(record.run_dir / "summary.md"),
                "patch_diff": str(record.run_dir / "patch.diff"),
            },
        }
        if record.packet.kind == "review":
            result_payload["findings"] = final_payload.get("findings", [])
            result_payload["validation_gaps"] = final_payload.get("validation_gaps", [])
        else:
            result_payload["files_changed"] = final_payload.get("files_changed", [])
            result_payload["validation_run"] = final_payload.get("validation_run", "")
            result_payload["known_risks"] = final_payload.get("known_risks", [])

        result_key = (record.packet.task_id or record.run_id).replace("\\", "_").replace("/", "_")
        _write_json(self.result_root / f"{result_key}.json", result_payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="claude-worker")
    parser.add_argument("--run-root", default=None)
    parser.add_argument("--claude-binary", default="claude")
    parser.add_argument("--default-model", default=DEFAULT_MODEL)
    parser.add_argument("--default-permission-mode", default=DEFAULT_PERMISSION_MODE)
    parser.add_argument("--wait-timeout-seconds", type=float, default=DEFAULT_WAIT_TIMEOUT_SECONDS)
    parser.add_argument("--detached-wait-timeout-seconds", type=float, default=DEFAULT_DETACHED_WAIT_TIMEOUT_SECONDS)
    parser.add_argument("--detached-poll-interval-seconds", type=float, default=DEFAULT_DETACHED_POLL_INTERVAL_SECONDS)
    parser.add_argument("--result-root", default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start")
    start.add_argument("--kind", choices=["coding", "review"], required=True)
    start.add_argument("--prompt", required=True)
    start.add_argument("--cwd", default=None)
    start.add_argument("--model", default=None)
    start.add_argument("--permission-mode", default=None)
    start.add_argument("--task-id", default=None)
    start.add_argument("--title", default=None)

    for name in ("wait", "fetch", "abort"):
        cmd = subparsers.add_parser(name)
        cmd.add_argument("--run-id", required=True)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    runtime = ClaudeWorkerRuntime(
        run_root=args.run_root,
        result_root=args.result_root,
        claude_binary=args.claude_binary,
        default_model=args.default_model,
        default_permission_mode=args.default_permission_mode,
        wait_timeout_seconds=args.wait_timeout_seconds,
        detached_wait_timeout_seconds=args.detached_wait_timeout_seconds,
        detached_poll_interval_seconds=args.detached_poll_interval_seconds,
    )

    if args.command == "start":
        packet = WorkerPacket(
            kind=args.kind,
            prompt=args.prompt,
            cwd=args.cwd,
            model=args.model or args.default_model,
            permission_mode=args.permission_mode or args.default_permission_mode,
            task_id=args.task_id,
            title=args.title,
        )
        record = runtime.start(packet)
        print(json.dumps({"run_id": record.run_id, "run_dir": str(record.run_dir)}, ensure_ascii=False))
        return 0

    if args.command == "wait":
        print(json.dumps(runtime.wait(args.run_id), ensure_ascii=False))
        return 0

    if args.command == "fetch":
        print(json.dumps(runtime.fetch(args.run_id), ensure_ascii=False))
        return 0

    if args.command == "abort":
        print(json.dumps(runtime.abort(args.run_id), ensure_ascii=False))
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2
