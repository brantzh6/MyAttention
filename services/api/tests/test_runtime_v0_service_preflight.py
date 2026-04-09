"""
Tests for IKE Runtime v0 Service Preflight Helper

R2-G2: Service Preflight for Live Proof Discipline
"""

import asyncio
import json
import platform
import sys
import unittest
from datetime import datetime, timezone
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

import httpx

from runtime.service_preflight import (
    PreflightStatus,
    PreflightResult,
    ApiHealthInfo,
    PortOwnershipInfo,
    _build_canonical_launch,
    _evaluate_owner_chain,
    _evaluate_preferred_owner,
    _evaluate_windows_venv_redirector_candidate,
    check_api_health,
    check_port_ownership,
    check_port_ownership_windows,
    check_port_ownership_unix,
    run_preflight,
    run_preflight_sync,
    determine_preflight_status,
    build_preflight_summary,
)


class TestPreflightStatus(unittest.TestCase):
    """Tests for PreflightStatus enum values."""

    def test_status_values_are_strings(self):
        """PreflightStatus values must be machine-readable strings."""
        self.assertEqual(PreflightStatus.READY.value, "ready")
        self.assertEqual(PreflightStatus.AMBIGUOUS.value, "ambiguous")
        self.assertEqual(PreflightStatus.DOWN.value, "down")

    def test_status_can_be_serialized(self):
        """PreflightStatus must serialize cleanly for JSON output."""
        status = PreflightStatus.READY
        serialized = json.dumps({"status": status.value})
        self.assertEqual(serialized, '{"status": "ready"}')


class TestApiHealthInfo(unittest.TestCase):
    """Tests for ApiHealthInfo dataclass."""

    def test_default_values(self):
        """ApiHealthInfo defaults to unhealthy state."""
        info = ApiHealthInfo(endpoint="http://127.0.0.1:8000/health")
        self.assertFalse(info.is_healthy)
        self.assertIsNone(info.response_status)
        self.assertIsNone(info.response_body)
        self.assertIsNone(info.error_message)

    def test_healthy_info(self):
        """ApiHealthInfo captures healthy response details."""
        info = ApiHealthInfo(
            endpoint="http://127.0.0.1:8000/health",
            is_healthy=True,
            response_status=200,
            response_body={"status": "healthy"},
            response_time_ms=50.0,
        )
        self.assertTrue(info.is_healthy)
        self.assertEqual(info.response_status, 200)
        self.assertEqual(info.response_body["status"], "healthy")


class TestPortOwnershipInfo(unittest.TestCase):
    """Tests for PortOwnershipInfo dataclass."""

    def test_default_clear(self):
        """PortOwnershipInfo defaults to clear ownership."""
        info = PortOwnershipInfo(port=8000)
        self.assertTrue(info.is_clear)
        self.assertEqual(info.unique_count, 0)
        self.assertEqual(info.listening_processes, [])

    def test_single_process_is_clear(self):
        """Single process on port is clear ownership."""
        info = PortOwnershipInfo(
            port=8000,
            listening_processes=[{"pid": 1234, "name": "python"}],
            unique_count=1,
            is_clear=True,
        )
        self.assertTrue(info.is_clear)
        self.assertEqual(info.unique_count, 1)

    def test_multiple_processes_is_not_clear(self):
        """Multiple processes on port is ambiguous."""
        info = PortOwnershipInfo(
            port=8000,
            listening_processes=[
                {"pid": 1234, "name": "python"},
                {"pid": 5678, "name": "python3"},
            ],
            unique_count=2,
            is_clear=False,
        )
        self.assertFalse(info.is_clear)
        self.assertEqual(info.unique_count, 2)


class TestDeterminePreflightStatus(unittest.TestCase):
    """Tests for status determination logic."""

    def test_down_when_api_unhealthy(self):
        """API down means DOWN status regardless of port."""
        api_health = ApiHealthInfo(endpoint="http://127.0.0.1:8000/health")
        port_ownership = PortOwnershipInfo(port=8000, is_clear=True)
        self.assertEqual(
            determine_preflight_status(api_health, port_ownership),
            PreflightStatus.DOWN
        )

    def test_down_with_connection_refused(self):
        """Connection refused means DOWN status."""
        api_health = ApiHealthInfo(
            endpoint="http://127.0.0.1:8000/health",
            is_healthy=False,
            error_message="Connection refused",
        )
        port_ownership = PortOwnershipInfo(port=8000, is_clear=True)
        self.assertEqual(
            determine_preflight_status(api_health, port_ownership),
            PreflightStatus.DOWN
        )

    def test_ambiguous_when_api_healthy_but_port_multiple(self):
        """Healthy API with multiple processes is AMBIGUOUS."""
        api_health = ApiHealthInfo(
            endpoint="http://127.0.0.1:8000/health",
            is_healthy=True,
            response_status=200,
        )
        port_ownership = PortOwnershipInfo(
            port=8000,
            unique_count=2,
            is_clear=False,
        )
        self.assertEqual(
            determine_preflight_status(api_health, port_ownership),
            PreflightStatus.AMBIGUOUS
        )

    def test_ambiguous_when_api_healthy_but_no_port_process(self):
        """Healthy API but no detected process is AMBIGUOUS."""
        api_health = ApiHealthInfo(
            endpoint="http://127.0.0.1:8000/health",
            is_healthy=True,
            response_status=200,
        )
        port_ownership = PortOwnershipInfo(
            port=8000,
            unique_count=0,
            is_clear=False,
        )
        self.assertEqual(
            determine_preflight_status(api_health, port_ownership),
            PreflightStatus.AMBIGUOUS
        )

    def test_ready_when_healthy_and_clear(self):
        """Healthy API with single port owner is READY."""
        api_health = ApiHealthInfo(
            endpoint="http://127.0.0.1:8000/health",
            is_healthy=True,
            response_status=200,
            response_time_ms=50.0,
        )
        port_ownership = PortOwnershipInfo(
            port=8000,
            unique_count=1,
            is_clear=True,
            listening_processes=[{"pid": 1234, "name": "python"}],
        )
        self.assertEqual(
            determine_preflight_status(api_health, port_ownership),
            PreflightStatus.READY
        )

    def test_strict_preferred_owner_marks_mismatch_ambiguous(self):
        """Strict preferred owner turns mismatch into AMBIGUOUS."""
        api_health = ApiHealthInfo(
            endpoint="http://127.0.0.1:8000/health",
            is_healthy=True,
            response_status=200,
        )
        port_ownership = PortOwnershipInfo(
            port=8000,
            unique_count=1,
            is_clear=True,
            listening_processes=[{"pid": 1234, "name": "python.exe"}],
        )
        preferred_owner = {"status": "preferred_mismatch", "matched": False, "matched_hint": None}
        self.assertEqual(
            determine_preflight_status(
                api_health,
                port_ownership,
                preferred_owner=preferred_owner,
                strict_preferred_owner=True,
            ),
            PreflightStatus.AMBIGUOUS,
        )

    def test_strict_preferred_owner_accepts_match(self):
        """Strict preferred owner keeps READY when preferred owner matches."""
        api_health = ApiHealthInfo(
            endpoint="http://127.0.0.1:8000/health",
            is_healthy=True,
            response_status=200,
        )
        port_ownership = PortOwnershipInfo(
            port=8000,
            unique_count=1,
            is_clear=True,
            listening_processes=[{"pid": 1234, "name": "python.exe"}],
        )
        preferred_owner = {
            "status": "preferred_match",
            "matched": True,
            "matched_hint": r"d:\code\myattention\.venv\scripts\python.exe",
        }
        self.assertEqual(
            determine_preflight_status(
                api_health,
                port_ownership,
                preferred_owner=preferred_owner,
                strict_preferred_owner=True,
            ),
            PreflightStatus.READY,
        )


class TestBuildPreflightSummary(unittest.TestCase):
    """Tests for summary building."""

    def test_down_summary_with_error(self):
        """DOWN status includes error message in summary."""
        api_health = ApiHealthInfo(
            endpoint="http://127.0.0.1:8000/health",
            error_message="Connection refused",
        )
        port_ownership = PortOwnershipInfo(port=8000)
        summary = build_preflight_summary(PreflightStatus.DOWN, api_health, port_ownership)
        self.assertIn("API down", summary)
        self.assertIn("Connection refused", summary)

    def test_ambiguous_summary_multiple_processes(self):
        """AMBIGUOUS status includes process count in summary."""
        api_health = ApiHealthInfo(endpoint="http://127.0.0.1:8000/health", is_healthy=True)
        port_ownership = PortOwnershipInfo(port=8000, unique_count=2, is_clear=False)
        summary = build_preflight_summary(PreflightStatus.AMBIGUOUS, api_health, port_ownership)
        self.assertIn("Ambiguous", summary)
        self.assertIn("2 processes", summary)
        self.assertIn("8000", summary)

    def test_ambiguous_summary_no_processes(self):
        """AMBIGUOUS status reports no process detected."""
        api_health = ApiHealthInfo(endpoint="http://127.0.0.1:8000/health", is_healthy=True)
        port_ownership = PortOwnershipInfo(port=8000, unique_count=0, is_clear=False)
        summary = build_preflight_summary(PreflightStatus.AMBIGUOUS, api_health, port_ownership)
        self.assertIn("Ambiguous", summary)
        self.assertIn("no process detected", summary)

    def test_ready_summary(self):
        """READY summary includes health and port details."""
        api_health = ApiHealthInfo(
            endpoint="http://127.0.0.1:8000/health",
            is_healthy=True,
            response_time_ms=50.0,
        )
        port_ownership = PortOwnershipInfo(port=8000, unique_count=1, is_clear=True)
        summary = build_preflight_summary(PreflightStatus.READY, api_health, port_ownership)
        self.assertIn("Ready", summary)
        self.assertIn("API healthy", summary)
        self.assertIn("single process", summary)


class TestCanonicalLaunch(unittest.TestCase):
    def test_canonical_launch_is_machine_readable(self):
        result = _build_canonical_launch(host="127.0.0.1", port=8000)
        self.assertIn(result["status"], {"defined", "incomplete"})
        self.assertEqual(result["host"], "127.0.0.1")
        self.assertEqual(result["port"], 8000)
        self.assertIn("run_service.py", result["service_entry_path"])
        self.assertIn("--host 127.0.0.1 --port 8000", result["command_line"])


class TestWindowsVenvRedirectorCandidate(unittest.TestCase):
    def test_redirector_candidate_detected(self):
        info = PortOwnershipInfo(
            port=8000,
            listening_processes=[
                {
                    "pid": 41536,
                    "name": "python.exe",
                    "command_line": r'"C:\Users\jiuyou\AppData\Local\Programs\Python\Python312\python.exe" D:\code\MyAttention\services\api\run_service.py --host 127.0.0.1 --port 8000',
                }
            ],
            unique_count=1,
            is_clear=True,
        )
        owner_chain = {"status": "parent_preferred_child_mismatch"}
        repo_launcher = {"status": "parent_and_child_repo_launcher_match"}
        cfg = Path(__file__).resolve().parent / "test-pyvenv.cfg"
        cfg.write_text(
            "\n".join(
                [
                    "home = C:\\Users\\jiuyou\\AppData\\Local\\Programs\\Python\\Python312",
                    "executable = C:\\Users\\jiuyou\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
                ]
            ),
            encoding="utf-8",
        )
        try:
            with patch.object(platform, "system", return_value="Windows"):
                result = _evaluate_windows_venv_redirector_candidate(info, owner_chain, repo_launcher, cfg)
        finally:
            cfg.unlink(missing_ok=True)
        self.assertEqual(result["status"], "windows_venv_redirector_candidate")
        self.assertTrue(result["candidate"])


class TestPreferredOwnerEvaluation(unittest.TestCase):
    def test_preferred_owner_matches_expected_hint(self):
        info = PortOwnershipInfo(
            port=8000,
            listening_processes=[
                {
                    "pid": 1234,
                    "name": "python.exe",
                    "command_line": r'"D:\code\MyAttention\.venv\Scripts\python.exe" run_service.py --host 127.0.0.1 --port 8000',
                }
            ],
            unique_count=1,
            is_clear=True,
        )
        result = _evaluate_preferred_owner(info, [r"d:\code\myattention\.venv\scripts\python.exe"])
        self.assertEqual(result["status"], "preferred_match")
        self.assertTrue(result["matched"])

    def test_preferred_owner_detects_mismatch(self):
        info = PortOwnershipInfo(
            port=8000,
            listening_processes=[
                {
                    "pid": 1234,
                    "name": "python.exe",
                    "command_line": r'"C:\Users\jiuyou\AppData\Local\Programs\Python\Python312\python.exe" run_service.py --host 127.0.0.1 --port 8000',
                }
            ],
            unique_count=1,
            is_clear=True,
        )
        result = _evaluate_preferred_owner(info, [r"d:\code\myattention\.venv\scripts\python.exe"])
        self.assertEqual(result["status"], "preferred_mismatch")
        self.assertFalse(result["matched"])

    def test_owner_chain_detects_parent_preferred_child_mismatch(self):
        info = PortOwnershipInfo(
            port=8000,
            listening_processes=[
                {
                    "pid": 1234,
                    "name": "python.exe",
                    "command_line": r'"C:\Python312\python.exe" run_service.py --host 127.0.0.1 --port 8000',
                    "parent_pid": 1233,
                    "parent_name": "python.exe",
                    "parent_command_line": r'"D:\code\MyAttention\.venv\Scripts\python.exe" run_service.py --host 127.0.0.1 --port 8000',
                }
            ],
            unique_count=1,
            is_clear=True,
        )
        result = _evaluate_owner_chain(info, [r"d:\code\myattention\.venv\scripts\python.exe"])
        self.assertEqual(result["status"], "parent_preferred_child_mismatch")
        self.assertTrue(result["parent_matches_preferred"])

    def test_owner_chain_detects_parent_and_child_preferred(self):
        info = PortOwnershipInfo(
            port=8000,
            listening_processes=[
                {
                    "pid": 1234,
                    "name": "python.exe",
                    "command_line": r'"D:\code\MyAttention\.venv\Scripts\python.exe" run_service.py --host 127.0.0.1 --port 8000',
                    "parent_pid": 1233,
                    "parent_name": "python.exe",
                    "parent_command_line": r'"D:\code\MyAttention\.venv\Scripts\python.exe" powershell-helper',
                }
            ],
            unique_count=1,
            is_clear=True,
        )
        result = _evaluate_owner_chain(info, [r"d:\code\myattention\.venv\scripts\python.exe"])
        self.assertEqual(result["status"], "parent_and_child_preferred")


class TestCheckApiHealth(unittest.IsolatedAsyncioTestCase):
    """Tests for async API health check."""

    async def test_health_check_success(self):
        """Successful health check returns healthy info."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy", "version": "0.1.0"}

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client_instance

            info = await check_api_health(host="127.0.0.1", port=8000)

            self.assertTrue(info.is_healthy)
            self.assertEqual(info.response_status, 200)
            self.assertEqual(info.response_body["status"], "healthy")

    async def test_health_check_connection_refused(self):
        """Connection refused returns unhealthy with error."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client_instance

            info = await check_api_health(host="127.0.0.1", port=8000)

            self.assertFalse(info.is_healthy)
            self.assertIn("Connection refused", info.error_message)

    async def test_health_check_timeout(self):
        """Timeout returns unhealthy with timeout message."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client_instance

            info = await check_api_health(host="127.0.0.1", port=8000, timeout_seconds=5.0)

            self.assertFalse(info.is_healthy)
            self.assertIn("Timeout", info.error_message)

    async def test_health_check_non_200(self):
        """Non-200 status code is unhealthy."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal error"}

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client_instance

            info = await check_api_health(host="127.0.0.1", port=8000)

            self.assertFalse(info.is_healthy)
            self.assertEqual(info.response_status, 500)


class TestCheckPortOwnership(unittest.TestCase):
    """Tests for port ownership inspection."""

    def test_platform_detection_windows(self):
        """Port ownership uses Windows method on Windows."""
        with patch.object(platform, "system", return_value="Windows"):
            with patch("runtime.service_preflight.check_port_ownership_windows") as mock_win:
                mock_win.return_value = PortOwnershipInfo(port=8000)
                info = check_port_ownership(8000)
                mock_win.assert_called_once_with(8000)

    def test_platform_detection_linux(self):
        """Port ownership uses Unix method on Linux."""
        with patch.object(platform, "system", return_value="Linux"):
            with patch("runtime.service_preflight.check_port_ownership_unix") as mock_unix:
                mock_unix.return_value = PortOwnershipInfo(port=8000)
                info = check_port_ownership(8000)
                mock_unix.assert_called_once_with(8000)


class TestCheckPortOwnershipWindows(unittest.TestCase):
    """Tests for Windows port ownership check."""

    def test_single_process_detected(self):
        """Windows netstat finds single process."""
        mock_netstat_result = MagicMock()
        mock_netstat_result.returncode = 0
        mock_netstat_result.stdout = """
Active Connections

  Proto  Local Address          Foreign Address        State           PID
  TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       1234
  TCP    127.0.0.1:8001         0.0.0.0:0              LISTENING       5678
"""
        mock_netstat_result.stderr = ""

        mock_ps_result = MagicMock()
        mock_ps_result.returncode = 0
        mock_ps_result.stdout = '{"ProcessId": 1234, "Name": "python", "CommandLine": "uvicorn main:app"}'

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [mock_netstat_result, mock_ps_result]
            info = check_port_ownership_windows(8000)

            self.assertEqual(info.unique_count, 1)
            self.assertTrue(info.is_clear)
            self.assertEqual(info.listening_processes[0]["pid"], 1234)

    def test_multiple_processes_detected(self):
        """Windows netstat detects multiple processes on same port."""
        mock_netstat_result = MagicMock()
        mock_netstat_result.returncode = 0
        mock_netstat_result.stdout = """
Active Connections

  Proto  Local Address          Foreign Address        State           PID
  TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       1234
  TCP    127.0.0.1:8000         0.0.0.0:0              LISTENING       5678
"""
        mock_netstat_result.stderr = ""

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = mock_netstat_result
            info = check_port_ownership_windows(8000)

            self.assertEqual(info.unique_count, 2)
            self.assertFalse(info.is_clear)

    def test_no_processes_detected(self):
        """Windows netstat returns no LISTENING on port."""
        mock_netstat_result = MagicMock()
        mock_netstat_result.returncode = 0
        mock_netstat_result.stdout = """
Active Connections

  Proto  Local Address          Foreign Address        State           PID
  TCP    0.0.0.0:8001           0.0.0.0:0              LISTENING       1234
"""
        mock_netstat_result.stderr = ""

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = mock_netstat_result
            info = check_port_ownership_windows(8000)

            self.assertEqual(info.unique_count, 0)
            self.assertFalse(info.is_clear)

    def test_netstat_failure(self):
        """Windows netstat failure captures error."""
        mock_netstat_result = MagicMock()
        mock_netstat_result.returncode = 1
        mock_netstat_result.stdout = ""
        mock_netstat_result.stderr = "netstat error"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = mock_netstat_result
            info = check_port_ownership_windows(8000)

            self.assertIsNotNone(info.inspection_error)
            self.assertIn("netstat failed", info.inspection_error)


class TestCheckPortOwnershipUnix(unittest.TestCase):
    """Tests for Unix/Linux/Mac port ownership check."""

    def test_single_process_lsof(self):
        """Unix lsof finds single process."""
        mock_lsof_result = MagicMock()
        mock_lsof_result.returncode = 0
        mock_lsof_result.stdout = """
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python   1234 user   3u  IPv4 12345      0t0  TCP *:8000 (LISTEN)
"""
        mock_lsof_result.stderr = ""

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = mock_lsof_result
            info = check_port_ownership_unix(8000)

            self.assertEqual(info.unique_count, 1)
            self.assertTrue(info.is_clear)
            self.assertEqual(info.listening_processes[0]["pid"], 1234)

    def test_multiple_processes_lsof(self):
        """Unix lsof detects multiple processes."""
        mock_lsof_result = MagicMock()
        mock_lsof_result.returncode = 0
        mock_lsof_result.stdout = """
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python   1234 user   3u  IPv4 12345      0t0  TCP *:8000 (LISTEN)
python3  5678 user   4u  IPv4 12346      0t0  TCP *:8000 (LISTEN)
"""
        mock_lsof_result.stderr = ""

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = mock_lsof_result
            info = check_port_ownership_unix(8000)

            self.assertEqual(info.unique_count, 2)
            self.assertFalse(info.is_clear)

    def test_no_processes_lsof(self):
        """Unix lsof returns no listeners."""
        mock_lsof_result = MagicMock()
        mock_lsof_result.returncode = 1  # lsof returns 1 if nothing found
        mock_lsof_result.stdout = ""
        mock_lsof_result.stderr = ""

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = mock_lsof_result
            info = check_port_ownership_unix(8000)

            self.assertEqual(info.unique_count, 0)
            self.assertFalse(info.is_clear)

    def test_lsof_not_available_fallback_netstat(self):
        """Unix falls back to netstat if lsof not available."""
        mock_netstat_result = MagicMock()
        mock_netstat_result.returncode = 0
        mock_netstat_result.stdout = """
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 0.0.0.0:8000            0.0.0.0:*               LISTEN      1234/python
"""

        with patch("subprocess.run") as mock_run:
            # First call (lsof) raises FileNotFoundError
            # Second call (netstat) succeeds
            mock_run.side_effect = [
                FileNotFoundError("lsof not found"),
                mock_netstat_result,
            ]
            info = check_port_ownership_unix(8000)

            self.assertEqual(info.inspection_method, "unix_netstat")
            self.assertEqual(info.unique_count, 1)
            self.assertTrue(info.is_clear)


class TestRunPreflight(unittest.IsolatedAsyncioTestCase):
    """Tests for complete preflight check."""

    async def test_preflight_ready(self):
        """Complete preflight returns READY when all checks pass."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}

        mock_netstat_result = MagicMock()
        mock_netstat_result.returncode = 0
        mock_netstat_result.stdout = """
Proto  Local Address          Foreign Address        State           PID
TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       1234
"""

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_http_client)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client_instance

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = mock_netstat_result
                with patch.object(platform, "system", return_value="Windows"):
                    result = await run_preflight(host="127.0.0.1", port=8000)

                    self.assertEqual(result.status, PreflightStatus.READY)
                    self.assertIn("Ready", result.summary)
                    self.assertTrue(result.api_health.is_healthy)
                    self.assertTrue(result.port_ownership.is_clear)

    async def test_preflight_down(self):
        """Complete preflight returns DOWN when API unreachable."""
        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))

        mock_netstat_result = MagicMock()
        mock_netstat_result.returncode = 0
        mock_netstat_result.stdout = ""

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_http_client)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client_instance

            with patch.object(platform, "system", return_value="Windows"):
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = mock_netstat_result
                    result = await run_preflight(host="127.0.0.1", port=8000)

                    self.assertEqual(result.status, PreflightStatus.DOWN)
                    self.assertIn("API down", result.summary)

    async def test_preflight_result_is_machine_readable(self):
        """PreflightResult must be JSON-serializable for controller."""
        result = PreflightResult(
            status=PreflightStatus.READY,
            timestamp="2026-04-08T12:00:00+00:00",
            api_health=ApiHealthInfo(
                endpoint="http://127.0.0.1:8000/health",
                is_healthy=True,
                response_status=200,
                response_time_ms=50.0,
            ),
            port_ownership=PortOwnershipInfo(
                port=8000,
                unique_count=1,
                is_clear=True,
            ),
            summary="Ready: API healthy",
            details={},
        )

        result_dict = asdict(result)
        serialized = json.dumps(result_dict)

        self.assertIn('"status": "ready"', serialized)
        self.assertIn('"timestamp"', serialized)

    async def test_preflight_strict_preferred_owner_marks_mismatch_ambiguous(self):
        """Strict preferred owner mode returns AMBIGUOUS when owner mismatches."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}

        mock_netstat_result = MagicMock()
        mock_netstat_result.returncode = 0
        mock_netstat_result.stdout = """
Proto  Local Address          Foreign Address        State           PID
TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       1234
"""

        mock_proc_result = MagicMock()
        mock_proc_result.returncode = 0
        mock_proc_result.stdout = json.dumps(
            {
                "ProcessId": 1234,
                "Name": "python.exe",
                "CommandLine": r'"C:\Python312\python.exe" run_service.py --host 127.0.0.1 --port 8000',
            }
        )

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_http_client)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client_instance

            with patch.object(platform, "system", return_value="Windows"):
                with patch("subprocess.run") as mock_run:
                    mock_run.side_effect = [mock_netstat_result, mock_proc_result]
                    result = await run_preflight(
                        host="127.0.0.1",
                        port=8000,
                        strict_preferred_owner=True,
                        preferred_owner_hints=[r"d:\code\myattention\.venv\scripts\python.exe"],
                    )

        self.assertEqual(result.status, PreflightStatus.AMBIGUOUS)
        self.assertEqual(result.details["preferred_owner"]["status"], "preferred_mismatch")
        self.assertTrue(result.port_ownership.is_clear)

    async def test_preflight_strict_code_freshness_marks_mismatch_ambiguous(self):
        """Strict code freshness mode returns AMBIGUOUS when fingerprint mismatches."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}

        mock_netstat_result = MagicMock()
        mock_netstat_result.returncode = 0
        mock_netstat_result.stdout = """
Proto  Local Address          Foreign Address        State           PID
TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       1234
"""

        mock_proc_result = MagicMock()
        mock_proc_result.returncode = 0
        mock_proc_result.stdout = json.dumps(
            {
                "ProcessId": 1234,
                "Name": "python.exe",
                "CommandLine": r'"D:\code\MyAttention\.venv\Scripts\python.exe" run_service.py --host 127.0.0.1 --port 8000',
            }
        )

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_http_client)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client_instance

            with patch.object(platform, "system", return_value="Windows"):
                with patch("subprocess.run") as mock_run:
                    mock_run.side_effect = [mock_netstat_result, mock_proc_result]
                    with patch(
                        "runtime.service_preflight._build_code_fingerprint",
                        return_value={
                            "status": "available",
                            "scope": "runtime_service_preflight_surface_v1",
                            "fingerprint": "actual-1234",
                            "sources": ["service_preflight.py", "ike_v0.py"],
                            "source_count": 2,
                        },
                    ):
                        result = await run_preflight(
                            host="127.0.0.1",
                            port=8000,
                            expected_code_fingerprint="expected-9999",
                            strict_code_freshness=True,
                        )

        self.assertEqual(result.status, PreflightStatus.AMBIGUOUS)
        self.assertEqual(result.details["code_freshness"]["status"], "mismatch")
        self.assertIn("code fingerprint mismatch", result.summary)

    async def test_preflight_repo_launcher_is_machine_readable(self):
        """Repo launcher evidence is captured separately from interpreter ownership."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}

        mock_netstat_result = MagicMock()
        mock_netstat_result.returncode = 0
        mock_netstat_result.stdout = """
Proto  Local Address          Foreign Address        State           PID
TCP    127.0.0.1:8013         0.0.0.0:0              LISTENING       41800
"""

        mock_proc_result = MagicMock()
        mock_proc_result.returncode = 0
        mock_proc_result.stdout = json.dumps(
            {
                "ProcessId": 41800,
                "Name": "python.exe",
                "CommandLine": r'"C:\Users\jiuyou\AppData\Local\Programs\Python\Python312\python.exe" "D:\code\MyAttention\.venv\Scripts\uvicorn.exe" main:app --host 127.0.0.1 --port 8013',
                "ParentProcessId": 35368,
            }
        )

        mock_parent_proc_result = MagicMock()
        mock_parent_proc_result.returncode = 0
        mock_parent_proc_result.stdout = json.dumps(
            {
                "ProcessId": 35368,
                "Name": "python.exe",
                "CommandLine": r'"D:\code\MyAttention\.venv\Scripts\python.exe" "D:\code\MyAttention\.venv\Scripts\uvicorn.exe" main:app --host 127.0.0.1 --port 8013',
            }
        )

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_http_client)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client_instance

            with patch.object(platform, "system", return_value="Windows"):
                with patch("subprocess.run") as mock_run:
                    mock_run.side_effect = [mock_netstat_result, mock_proc_result, mock_parent_proc_result]
                    result = await run_preflight(host="127.0.0.1", port=8013)

        self.assertEqual(
            result.details["repo_launcher"]["status"],
            "parent_and_child_repo_launcher_match",
        )
        self.assertTrue(result.details["repo_launcher"]["child_matches"])
        self.assertTrue(result.details["repo_launcher"]["parent_matches"])
        self.assertEqual(
            result.details["controller_acceptability"]["status"],
            "blocked_owner_mismatch",
        )

    async def test_preflight_controller_acceptability_bounded_live_proof_ready(self):
        """Repo-launcher match plus fresh code can be controller-acceptable for bounded live proof."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}

        mock_netstat_result = MagicMock()
        mock_netstat_result.returncode = 0
        mock_netstat_result.stdout = """
Proto  Local Address          Foreign Address        State           PID
TCP    127.0.0.1:8013         0.0.0.0:0              LISTENING       41800
"""

        mock_proc_result = MagicMock()
        mock_proc_result.returncode = 0
        mock_proc_result.stdout = json.dumps(
            {
                "ProcessId": 41800,
                "Name": "python.exe",
                "CommandLine": r'"C:\Users\jiuyou\AppData\Local\Programs\Python\Python312\python.exe" "D:\code\MyAttention\.venv\Scripts\uvicorn.exe" main:app --host 127.0.0.1 --port 8013',
                "ParentProcessId": 35368,
            }
        )

        mock_parent_proc_result = MagicMock()
        mock_parent_proc_result.returncode = 0
        mock_parent_proc_result.stdout = json.dumps(
            {
                "ProcessId": 35368,
                "Name": "python.exe",
                "CommandLine": r'"D:\code\MyAttention\.venv\Scripts\python.exe" "D:\code\MyAttention\.venv\Scripts\uvicorn.exe" main:app --host 127.0.0.1 --port 8013',
            }
        )

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_http_client)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client_instance

            with patch.object(platform, "system", return_value="Windows"):
                with patch("subprocess.run") as mock_run:
                    mock_run.side_effect = [mock_netstat_result, mock_proc_result, mock_parent_proc_result]
                    with patch(
                        "runtime.service_preflight._build_code_fingerprint",
                        return_value={
                            "status": "available",
                            "scope": "runtime_service_preflight_surface_v1",
                            "fingerprint": "fresh-8013",
                            "sources": ["service_preflight.py", "ike_v0.py"],
                            "source_count": 2,
                        },
                    ):
                        result = await run_preflight(
                            host="127.0.0.1",
                            port=8013,
                            expected_code_fingerprint="fresh-8013",
                            strict_preferred_owner=True,
                            strict_code_freshness=True,
                        )

        self.assertEqual(result.status, PreflightStatus.AMBIGUOUS)
        self.assertEqual(result.details["code_freshness"]["status"], "match")
        self.assertEqual(
            result.details["controller_acceptability"]["status"],
            "bounded_live_proof_ready",
        )
        self.assertTrue(result.details["controller_acceptability"]["acceptable"])


class TestRunPreflightSync(unittest.TestCase):
    """Tests for synchronous preflight wrapper."""

    def test_sync_wrapper_returns_result(self):
        """run_preflight_sync wraps async function correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}

        mock_netstat_result = MagicMock()
        mock_netstat_result.returncode = 0
        mock_netstat_result.stdout = """
Proto  Local Address          Foreign Address        State           PID
TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       1234
"""

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_http_client)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client_instance

            with patch.object(platform, "system", return_value="Windows"):
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = mock_netstat_result
                    result = run_preflight_sync(host="127.0.0.1", port=8000)

                    self.assertEqual(result.status, PreflightStatus.READY)


class TestPreflightIntegrationPatterns(unittest.TestCase):
    """Integration-style tests for preflight usage patterns."""

    def test_preflight_result_has_all_required_fields(self):
        """PreflightResult must have all fields for controller decision."""
        result = PreflightResult(
            status=PreflightStatus.READY,
            timestamp=datetime.now(timezone.utc).isoformat(),
            api_health=ApiHealthInfo(endpoint="http://127.0.0.1:8000/health"),
            port_ownership=PortOwnershipInfo(port=8000),
            summary="Test summary",
            details={"key": "value"},
        )

        self.assertTrue(hasattr(result, "status"))
        self.assertTrue(hasattr(result, "timestamp"))
        self.assertTrue(hasattr(result, "summary"))
        self.assertTrue(hasattr(result, "api_health"))
        self.assertTrue(hasattr(result, "port_ownership"))
        self.assertTrue(hasattr(result, "details"))

    def test_preflight_status_enum_coverage(self):
        """PreflightStatus must cover all required states."""
        required_states = {"ready", "ambiguous", "down"}
        actual_states = {s.value for s in PreflightStatus}
        self.assertEqual(required_states, actual_states)

    def test_preflight_ambiguous_captures_inspection_errors(self):
        """AMBIGUOUS status must capture inspection errors."""
        api_health = ApiHealthInfo(endpoint="http://127.0.0.1:8000/health", is_healthy=True)
        port_ownership = PortOwnershipInfo(
            port=8000,
            inspection_error="lsof permission denied",
        )
        port_ownership.is_clear = False

        summary = build_preflight_summary(
            PreflightStatus.AMBIGUOUS, api_health, port_ownership
        )
        self.assertIn("Ambiguous", summary)


if __name__ == "__main__":
    unittest.main()
