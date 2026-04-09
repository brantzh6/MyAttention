import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from claude_worker.worker import (
    ClaudeWorkerRuntime,
    WorkerPacket,
    build_parser,
    _resolve_claude_binary,
    normalize_coding_result,
    normalize_review_result,
)


class FakeProcess:
    def __init__(self, stdout: str, stderr: str = "", returncode: int = 0) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = None
        self._next_returncode = returncode
        self.terminated = False
        self.killed = False
        self.communicate_calls = 0

    def communicate(self, timeout: int | None = None):
        self.communicate_calls += 1
        self.returncode = self._next_returncode
        return self.stdout, self.stderr

    def wait(self, timeout: int | None = None):
        self.returncode = self._next_returncode
        return self._next_returncode

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminated = True

    def kill(self):
        self.killed = True


class ClaudeWorkerRuntimeTest(unittest.TestCase):
    def _run_cli(self, args: list[str]) -> dict[str, object]:
        command = [sys.executable, "-m", "claude_worker", *args]
        proc = subprocess.run(
            command,
            cwd=str(API_ROOT),
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(proc.stdout.strip())

    def test_start_wait_and_fetch_writes_durable_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launched = {}

            def launcher(command, **kwargs):
                launched["command"] = command
                launched["kwargs"] = kwargs
                return FakeProcess(
                    json.dumps(
                        {
                            "summary": "Added the new worker runtime files.",
                            "files_changed": [
                                "services/api/claude_worker/worker.py",
                                "services/api/tests/test_claude_worker.py",
                            ],
                            "validation_run": "python -m unittest tests.test_claude_worker",
                            "known_risks": ["CLI schema may need tightening"],
                            "recommendation": "accept_with_changes",
                            "patch_diff": "--- a/foo\n+++ b/foo\n",
                        }
                    )
                )

            runtime = ClaudeWorkerRuntime(run_root=tmpdir, launcher=launcher)
            record = runtime.start(
                WorkerPacket(
                    kind="coding",
                    prompt="Add the worker runtime.",
                    cwd=tmpdir,
                    model="qwen3-coder-next",
                    task_id="task-123",
                    title="Toy coding packet",
                )
            )

            self.assertTrue((record.run_dir / "meta.json").exists())
            self.assertTrue((record.run_dir / "events.ndjson").exists())
            self.assertTrue((record.run_dir / "summary.md").exists())
            self.assertTrue((record.run_dir / "patch.diff").exists())

            final_payload = runtime.wait(record.run_id)

            self.assertEqual(final_payload["kind"], "coding")
            self.assertEqual(final_payload["recommendation"], "accept_with_changes")
            self.assertEqual(final_payload["files_changed"][0], "services/api/claude_worker/worker.py")
            self.assertEqual(final_payload["validation_run"], "python -m unittest tests.test_claude_worker")
            self.assertIn("Added the new worker runtime files.", final_payload["summary"])

            fetched = runtime.fetch(record.run_id)
            self.assertEqual(fetched["final"]["recommendation"], "accept_with_changes")
            self.assertIn("meta", fetched)
            self.assertIn("events", fetched)
            self.assertIn("summary", fetched)

            self.assertTrue(Path(launched["command"][0]).name.startswith("claude"))
            self.assertIn("--model", launched["command"])
            self.assertIn("qwen3-coder-next", launched["command"])
            self.assertEqual(launched["kwargs"]["cwd"], tmpdir)

    def test_review_result_is_normalized(self) -> None:
        raw = {
            "summary": "Found a scope leak in the worker packet.",
            "findings": [
                {"title": "Scope leak", "body": "The packet touches too many files.", "file": "docs/plan.md"}
            ],
            "validation_gaps": ["No real CLI proof yet"],
            "recommendation": "accept_with_changes",
        }
        normalized = normalize_review_result(raw)
        self.assertEqual(normalized["kind"], "review")
        self.assertEqual(normalized["recommendation"], "accept_with_changes")
        self.assertEqual(normalized["findings"][0]["title"], "Scope leak")
        self.assertEqual(normalized["validation_gaps"][0], "No real CLI proof yet")

    def test_coding_result_is_normalized(self) -> None:
        raw = {
            "summary": "Worker is ready.",
            "files_changed": ["services/api/claude_worker/worker.py"],
            "validation_run": "python -m unittest tests.test_claude_worker",
            "known_risks": ["Need a real toy-run proof"],
            "recommendation": "accept_with_changes",
        }
        normalized = normalize_coding_result(raw)
        self.assertEqual(normalized["kind"], "coding")
        self.assertEqual(normalized["files_changed"], ["services/api/claude_worker/worker.py"])
        self.assertEqual(normalized["validation_run"], "python -m unittest tests.test_claude_worker")

    def test_abort_marks_run_aborted(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            class HangingProcess(FakeProcess):
                def communicate(self, timeout: int | None = None):
                    self.communicate_calls += 1
                    self.returncode = -15
                    return "", ""

            def launcher(command, **kwargs):
                return HangingProcess("", "")

            runtime = ClaudeWorkerRuntime(run_root=tmpdir, launcher=launcher)
            record = runtime.start(
                WorkerPacket(
                    kind="review",
                    prompt="Review the patch.",
                    cwd=tmpdir,
                )
            )
            result = runtime.abort(record.run_id)
            self.assertEqual(result["status"], "aborted")
            self.assertTrue((record.run_dir / "final.json").exists())

    def test_resolve_claude_binary_prefers_cmd_on_windows(self) -> None:
        with patch.object(os, "name", "nt"):
            with patch.object(shutil, "which") as mock_which:
                mock_which.side_effect = lambda name: f"C:\\path\\{name}" if name == "claude.cmd" else None
                resolved = _resolve_claude_binary("claude")
                self.assertEqual(resolved, "C:\\path\\claude.cmd")

    def test_timeout_path_terminates_kills_and_finalizes(self) -> None:
        class TimeoutThenFailProcess:
            def __init__(self) -> None:
                self.returncode = None
                self.terminated = False
                self.killed = False
                self.calls = 0

            def communicate(self, timeout: int | None = None):
                self.calls += 1
                if self.calls == 1:
                    raise subprocess.TimeoutExpired(cmd="claude", timeout=timeout)
                raise RuntimeError("post-timeout drain failed")

            def wait(self, timeout: int | None = None):
                self.returncode = 124
                return 124

            def poll(self):
                return self.returncode

            def terminate(self):
                self.terminated = True

            def kill(self):
                self.killed = True

        with tempfile.TemporaryDirectory() as tmpdir:
            runtime = ClaudeWorkerRuntime(run_root=tmpdir, launcher=lambda *args, **kwargs: TimeoutThenFailProcess())
            record = runtime.start(WorkerPacket(kind="coding", prompt="Hang test", cwd=tmpdir))
            result = runtime.wait(record.run_id)
            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["returncode"], 124)
            self.assertIn("Timed out", result["stderr"])
            self.assertEqual(
                result["lifecycle"],
                {"timeout": True, "terminate_requested": True, "kill_requested": True},
            )
            self.assertTrue(record.process.terminated)
            self.assertTrue(record.process.killed)
            self.assertTrue((record.run_dir / "final.json").exists())
            events = (record.run_dir / "events.ndjson").read_text(encoding="utf-8")
            self.assertIn('"event": "terminate_requested"', events)
            self.assertIn('"event": "kill_requested"', events)

    def test_live_hanging_subprocess_times_out_and_records_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            def launcher(*args, **kwargs):
                return subprocess.Popen(
                    [sys.executable, "-c", "import time; time.sleep(30)"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=kwargs.get("cwd"),
                )

            runtime = ClaudeWorkerRuntime(
                run_root=Path(tmpdir) / "runs",
                wait_timeout_seconds=0.1,
                launcher=launcher,
            )
            record = runtime.start(
                WorkerPacket(
                    kind="coding",
                    prompt="Real hang test",
                    cwd=tmpdir,
                )
            )
            result = runtime.wait(record.run_id)
            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["returncode"], 124)
            self.assertIn("Timed out", result["stderr"])
            self.assertTrue(result["lifecycle"]["timeout"])
            self.assertTrue(result["lifecycle"]["terminate_requested"])
            self.assertTrue((record.run_dir / "final.json").exists())
            events = (record.run_dir / "events.ndjson").read_text(encoding="utf-8")
            self.assertIn('"event": "wait_timeout"', events)
            self.assertIn('"event": "terminate_requested"', events)

    def test_detached_wait_returns_running_snapshot_and_abort_requires_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_root = Path(tmpdir) / "runs"
            if os.name == "nt":
                detached_binary = Path(tmpdir) / "claude.cmd"
                detached_binary.write_text(
                    "@echo off\r\n"
                    ":loop\r\n"
                    "ping -n 2 127.0.0.1 >nul\r\n"
                    "goto loop\r\n",
                    encoding="utf-8",
                )
            else:
                detached_binary = Path(tmpdir) / "claude"
                detached_binary.write_text(
                    "#!/bin/sh\n"
                    "while true; do\n"
                    "  sleep 1\n"
                    "done\n",
                    encoding="utf-8",
                )
                detached_binary.chmod(0o755)
            owner_runtime = ClaudeWorkerRuntime(run_root=run_root, claude_binary=str(detached_binary))
            record = owner_runtime.start(WorkerPacket(kind="coding", prompt="Detached", cwd=tmpdir, task_id="detached-1"))

            detached_runtime = ClaudeWorkerRuntime(
                run_root=run_root,
                detached_wait_timeout_seconds=0.05,
                detached_poll_interval_seconds=0.01,
            )
            snapshot = detached_runtime.wait(record.run_id)
            self.assertEqual(snapshot["status"], "running")
            self.assertEqual(snapshot["detached_wait"]["state"], "timed_out")
            self.assertEqual(snapshot["detached_wait"]["strategy"]["wait_mode"], "poll-final-json")
            self.assertIn("owner_pid", snapshot["detached_wait"])

            aborted = detached_runtime.abort(record.run_id)
            self.assertEqual(aborted["status"], "aborted")
            self.assertTrue(aborted["lifecycle"]["detached_abort"])
            owner_process = owner_runtime._records[record.run_id].process
            if owner_process is not None and hasattr(owner_process, "communicate"):
                try:
                    owner_process.communicate(timeout=1)
                except Exception:
                    pass

    def test_reload_rejects_corrupted_meta_and_invalid_kind(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_root = Path(tmpdir)
            bad_run = run_root / "bad-run"
            bad_run.mkdir()

            (bad_run / "meta.json").write_text("{not-json", encoding="utf-8")
            runtime = ClaudeWorkerRuntime(run_root=run_root)
            with self.assertRaises(ValueError):
                runtime.fetch("bad-run")

            kind_run = run_root / "kind-run"
            kind_run.mkdir()
            (kind_run / "meta.json").write_text(
                json.dumps(
                    {
                        "kind": "coding",
                        "packet": {
                            "kind": "bogus",
                            "prompt": "x",
                        },
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                runtime.fetch("kind-run")

            missing_run = run_root / "missing-run"
            missing_run.mkdir()
            (missing_run / "meta.json").write_text(
                json.dumps(
                    {
                        "kind": "coding",
                        "packet": {
                            "kind": "coding",
                        },
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                runtime.fetch("missing-run")

    def test_unknown_run_id_raises_key_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            runtime = ClaudeWorkerRuntime(run_root=tmpdir)
            with self.assertRaises(KeyError):
                runtime.fetch("missing-run")

    def test_malformed_json_finalizes_with_fallback_summary(self) -> None:
        class BadJsonProcess(FakeProcess):
            pass

        with tempfile.TemporaryDirectory() as tmpdir:
            runtime = ClaudeWorkerRuntime(
                run_root=tmpdir,
                launcher=lambda *args, **kwargs: BadJsonProcess("not-json-output"),
            )
            record = runtime.start(WorkerPacket(kind="coding", prompt="Bad JSON", cwd=tmpdir))
            result = runtime.wait(record.run_id)
            self.assertEqual(result["status"], "succeeded")
            self.assertEqual(result["summary"], "not-json-output")
            self.assertEqual(result["files_changed"], [])

    def test_finalize_writes_harness_result_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result_root = Path(tmpdir) / "results"
            runtime = ClaudeWorkerRuntime(
                run_root=Path(tmpdir) / "runs",
                result_root=result_root,
                launcher=lambda *args, **kwargs: FakeProcess(
                    json.dumps(
                        {
                            "summary": "Harness projection test",
                            "files_changed": ["services/api/claude_worker/worker.py"],
                            "validation_run": "python -m unittest tests.test_claude_worker",
                            "known_risks": ["none"],
                            "recommendation": "accept",
                        }
                    )
                ),
            )
            record = runtime.start(WorkerPacket(kind="coding", prompt="Projection", cwd=tmpdir, task_id="task-harness"))
            runtime.wait(record.run_id)
            result_path = result_root / "task-harness.json"
            self.assertTrue(result_path.exists())
            payload = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["protocol"], "delegation_result.v1")
            self.assertEqual(payload["task_id"], "task-harness")
            self.assertEqual(payload["status"], "succeeded")
            self.assertIn("artifacts", payload)
            self.assertEqual(payload["files_changed"], ["services/api/claude_worker/worker.py"])

    def test_invalid_payload_shape_sets_normalization_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            runtime = ClaudeWorkerRuntime(
                run_root=tmpdir,
                launcher=lambda *args, **kwargs: FakeProcess(
                    json.dumps(
                        {
                            "structured_output": {
                                "summary": "bad shape",
                                "findings": {"title": "not-a-list"},
                                "validation_gaps": [],
                                "recommendation": "reject",
                            }
                        }
                    )
                ),
            )
            record = runtime.start(WorkerPacket(kind="review", prompt="Bad shape", cwd=tmpdir))
            result = runtime.wait(record.run_id)
            self.assertEqual(result["status"], "failed")
            self.assertIn("normalization_error", result)
            self.assertEqual(result["recommendation"], "reject")

    def test_cli_parser_accepts_start_wait_abort(self) -> None:
        parser = build_parser()
        start = parser.parse_args(["start", "--kind", "coding", "--prompt", "hello"])
        self.assertEqual(start.command, "start")
        self.assertEqual(start.kind, "coding")
        self.assertEqual(start.wait_timeout_seconds, 600)
        parsed = parser.parse_args(["--wait-timeout-seconds", "7", "start", "--kind", "coding", "--prompt", "hello"])
        self.assertEqual(parsed.wait_timeout_seconds, 7.0)
        parsed = parser.parse_args(
            [
                "--detached-wait-timeout-seconds",
                "2.5",
                "--detached-poll-interval-seconds",
                "0.5",
                "--result-root",
                "D:\\tmp\\results",
                "start",
                "--kind",
                "coding",
                "--prompt",
                "hello",
            ]
        )
        self.assertEqual(parsed.detached_wait_timeout_seconds, 2.5)
        self.assertEqual(parsed.detached_poll_interval_seconds, 0.5)
        self.assertEqual(parsed.result_root, "D:\\tmp\\results")
        wait = parser.parse_args(["wait", "--run-id", "abc"])
        self.assertEqual(wait.command, "wait")
        abort = parser.parse_args(["abort", "--run-id", "abc"])
        self.assertEqual(abort.command, "abort")

    def test_cli_end_to_end_start_fetch_abort(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            run_root = tmp_path / "runs"
            result_root = tmp_path / "results"
            if os.name == "nt":
                cli_binary = tmp_path / "claude.cmd"
                cli_binary.write_text(
                    "@echo off\r\n"
                    ":loop\r\n"
                    "ping -n 2 127.0.0.1 >nul\r\n"
                    "goto loop\r\n",
                    encoding="utf-8",
                )
            else:
                cli_binary = tmp_path / "claude"
                cli_binary.write_text(
                    "#!/bin/sh\n"
                    "while true; do\n"
                    "  sleep 1\n"
                    "done\n",
                    encoding="utf-8",
                )
                cli_binary.chmod(0o755)

            base_args = [
                "--run-root",
                str(run_root),
                "--result-root",
                str(result_root),
                "--claude-binary",
                str(cli_binary),
                "--wait-timeout-seconds",
                "0.1",
                "--detached-wait-timeout-seconds",
                "0.1",
                "--detached-poll-interval-seconds",
                "0.01",
            ]
            started = self._run_cli(base_args + ["start", "--kind", "coding", "--prompt", "e2e", "--cwd", tmpdir, "--task-id", "cli-e2e"])
            run_id = str(started["run_id"])

            fetched_before = self._run_cli(base_args + ["fetch", "--run-id", run_id])
            self.assertEqual(fetched_before["meta"]["task_id"], "cli-e2e")
            self.assertIsNone(fetched_before["final"])

            aborted = self._run_cli(base_args + ["abort", "--run-id", run_id])
            self.assertEqual(aborted["status"], "aborted")

            fetched_after = self._run_cli(base_args + ["fetch", "--run-id", run_id])
            self.assertEqual(fetched_after["final"]["status"], "aborted")
            self.assertTrue((result_root / "cli-e2e.json").exists())


if __name__ == "__main__":
    unittest.main()
