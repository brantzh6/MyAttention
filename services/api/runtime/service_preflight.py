"""
IKE Runtime v0 - Service Preflight Helper

Narrow operational helper for runtime live proof preflight checks.
Checks local API health and port ownership to report whether live proof
is safe to proceed.

This module does NOT:
- Create new runtime truth semantics
- Implement a broad service supervisor
- Implement a daemon/job manager
- Implement automatic kill-or-restart policy

R2-G2: Service Preflight for Live Proof Discipline
"""

from __future__ import annotations

import asyncio
import hashlib
import platform
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class PreflightStatus(str, Enum):
    """Machine-readable preflight status for controller decision."""

    READY = "ready"
    """API is healthy and port ownership is clear. Live proof safe to proceed."""

    AMBIGUOUS = "ambiguous"
    """Multiple processes claim the port or ownership is unclear. Controller should investigate."""

    DOWN = "down"
    """API is not running or health endpoint unreachable."""


@dataclass
class PortOwnershipInfo:
    """Information about port ownership from platform-specific inspection."""

    port: int
    listening_processes: list[dict[str, Any]] = field(default_factory=list)
    """List of processes found listening on the port."""

    unique_count: int = 0
    """Number of unique processes claiming the port."""

    is_clear: bool = True
    """True if exactly one process owns the port, False if zero or multiple."""

    inspection_method: str = ""
    """Platform-specific method used (e.g., 'netstat', 'powershell')."""

    inspection_error: str | None = None
    """Error message if inspection failed."""


@dataclass
class ApiHealthInfo:
    """Information from API health endpoint check."""

    endpoint: str
    is_healthy: bool = False
    response_status: int | None = None
    response_body: dict[str, Any] | None = None
    response_time_ms: float | None = None
    error_message: str | None = None


@dataclass
class PreflightResult:
    """Complete preflight result for controller consumption.

    Machine-readable and controller-friendly output.
    """

    status: PreflightStatus
    timestamp: str
    api_health: ApiHealthInfo
    port_ownership: PortOwnershipInfo

    # Summary for quick controller assessment
    summary: str
    """Human-readable one-line summary."""

    details: dict[str, Any] = field(default_factory=dict)
    """Additional structured details for debugging."""


# Default configuration
DEFAULT_API_PORT = 8000
DEFAULT_API_HOST = "127.0.0.1"
DEFAULT_HEALTH_ENDPOINT = "/health"
DEFAULT_TIMEOUT_SECONDS = 5.0
DEFAULT_PREFERRED_OWNER_HINTS = [
    str((Path(__file__).resolve().parents[3] / ".venv" / "Scripts" / "python.exe")).lower(),
]
DEFAULT_REPO_PYTHON_PATH = Path(__file__).resolve().parents[3] / ".venv" / "Scripts" / "python.exe"
DEFAULT_REPO_UVICORN_PATH = Path(__file__).resolve().parents[3] / ".venv" / "Scripts" / "uvicorn.exe"
DEFAULT_REPO_SERVICE_ENTRY = Path(__file__).resolve().parents[1] / "run_service.py"
DEFAULT_PYVENV_CFG_PATH = Path(__file__).resolve().parents[3] / ".venv" / "pyvenv.cfg"
DEFAULT_REPO_LAUNCHER_HINTS = [
    str(DEFAULT_REPO_SERVICE_ENTRY).lower(),
    str(DEFAULT_REPO_UVICORN_PATH).lower(),
]
DEFAULT_CODE_FINGERPRINT_PATHS = [
    Path(__file__).resolve(),
    Path(__file__).resolve().parents[1] / "routers" / "ike_v0.py",
]


def _evaluate_preferred_owner(
    port_ownership: PortOwnershipInfo,
    preferred_owner_hints: list[str] | None = None,
) -> dict[str, Any]:
    hints = [hint.lower() for hint in (preferred_owner_hints or DEFAULT_PREFERRED_OWNER_HINTS) if hint]
    if not hints:
        return {"status": "unspecified", "matched": False, "matched_hint": None}

    if port_ownership.unique_count != 1 or not port_ownership.listening_processes:
        return {"status": "indeterminate", "matched": False, "matched_hint": None}

    process = port_ownership.listening_processes[0]
    command_line = str(process.get("command_line", "")).lower()
    for hint in hints:
        if hint in command_line:
            return {"status": "preferred_match", "matched": True, "matched_hint": hint}

    return {"status": "preferred_mismatch", "matched": False, "matched_hint": None}


def _evaluate_owner_chain(
    port_ownership: PortOwnershipInfo,
    preferred_owner_hints: list[str] | None = None,
) -> dict[str, Any]:
    hints = [hint.lower() for hint in (preferred_owner_hints or DEFAULT_PREFERRED_OWNER_HINTS) if hint]
    if not hints:
        return {"status": "unspecified", "parent_matches_preferred": False}

    if port_ownership.unique_count != 1 or not port_ownership.listening_processes:
        return {"status": "indeterminate", "parent_matches_preferred": False}

    process = port_ownership.listening_processes[0]
    parent_command_line = str(process.get("parent_command_line", "")).lower()
    child_command_line = str(process.get("command_line", "")).lower()
    matched_hint = next((hint for hint in hints if hint in parent_command_line), None)

    if not parent_command_line:
        return {"status": "no_parent_data", "parent_matches_preferred": False}
    if not matched_hint:
        return {"status": "parent_not_preferred", "parent_matches_preferred": False}
    if matched_hint in child_command_line:
        return {
            "status": "parent_and_child_preferred",
            "parent_matches_preferred": True,
            "matched_hint": matched_hint,
        }
    return {
        "status": "parent_preferred_child_mismatch",
        "parent_matches_preferred": True,
        "matched_hint": matched_hint,
    }


def _evaluate_repo_launcher(
    port_ownership: PortOwnershipInfo,
    repo_launcher_hints: list[str] | None = None,
) -> dict[str, Any]:
    hints = [hint.lower() for hint in (repo_launcher_hints or DEFAULT_REPO_LAUNCHER_HINTS) if hint]
    if not hints:
        return {"status": "unspecified", "child_matches": False, "parent_matches": False, "matched_hint": None}

    if port_ownership.unique_count != 1 or not port_ownership.listening_processes:
        return {"status": "indeterminate", "child_matches": False, "parent_matches": False, "matched_hint": None}

    process = port_ownership.listening_processes[0]
    child_command_line = str(process.get("command_line", "")).lower()
    parent_command_line = str(process.get("parent_command_line", "")).lower()

    child_match = next((hint for hint in hints if hint in child_command_line), None)
    parent_match = next((hint for hint in hints if hint in parent_command_line), None)

    if child_match and parent_match:
        return {
            "status": "parent_and_child_repo_launcher_match",
            "child_matches": True,
            "parent_matches": True,
            "matched_hint": child_match,
        }
    if child_match:
        return {
            "status": "child_repo_launcher_match",
            "child_matches": True,
            "parent_matches": False,
            "matched_hint": child_match,
        }
    if parent_match:
        return {
            "status": "parent_repo_launcher_match",
            "child_matches": False,
            "parent_matches": True,
            "matched_hint": parent_match,
        }
    return {
        "status": "repo_launcher_mismatch",
        "child_matches": False,
        "parent_matches": False,
        "matched_hint": None,
    }


def _evaluate_controller_acceptability(
    api_health: ApiHealthInfo,
    port_ownership: PortOwnershipInfo,
    preferred_owner: dict[str, Any],
    owner_chain: dict[str, Any],
    repo_launcher: dict[str, Any],
    windows_venv_redirector: dict[str, Any],
    canonical_launch: dict[str, Any],
    code_freshness: dict[str, Any],
) -> dict[str, Any]:
    if not api_health.is_healthy:
        return {"status": "blocked_api_down", "acceptable": False}
    if not port_ownership.is_clear:
        return {"status": "blocked_port_ambiguity", "acceptable": False}

    preferred_status = preferred_owner.get("status")
    owner_chain_status = owner_chain.get("status")
    repo_launcher_status = repo_launcher.get("status")
    windows_redirector_status = windows_venv_redirector.get("status")
    canonical_launch_status = canonical_launch.get("status")
    code_freshness_status = code_freshness.get("status")

    if preferred_status == "preferred_match" and code_freshness_status in {"match", "unchecked"}:
        return {"status": "canonical_ready", "acceptable": True}
    if (
        platform.system() == "Windows"
        and windows_redirector_status == "windows_venv_redirector_candidate"
        and repo_launcher_status == "parent_and_child_repo_launcher_match"
        and owner_chain_status == "parent_preferred_child_mismatch"
        and canonical_launch_status == "defined"
        and code_freshness_status == "match"
    ):
        return {
            "status": "acceptable_windows_venv_redirector",
            "acceptable": True,
            "controller_confirmation_required": True,
            "rule": "windows_venv_redirector_v1",
            "promotion_path": "controller_confirmation_required",
        }
    if code_freshness_status == "mismatch":
        return {"status": "blocked_code_freshness", "acceptable": False}
    if preferred_status != "preferred_match":
        return {"status": "blocked_owner_mismatch", "acceptable": False}
    return {"status": "blocked_other", "acceptable": False}


def _evaluate_controller_promotion(
    controller_acceptability: dict[str, Any],
) -> dict[str, Any]:
    status = controller_acceptability.get("status")

    if status == "canonical_ready":
        return {
            "status": "controller_can_promote_now",
            "eligible": True,
            "target_status": "canonical_accepted",
            "controller_confirmation_required": False,
            "basis": "direct_canonical_owner_match",
        }

    if status == "acceptable_windows_venv_redirector":
        return {
            "status": "controller_confirmation_required",
            "eligible": True,
            "target_status": "canonical_accepted",
            "controller_confirmation_required": True,
            "basis": "windows_venv_redirector_v1",
        }

    return {
        "status": "not_promotable",
        "eligible": False,
        "target_status": None,
        "controller_confirmation_required": False,
        "basis": status,
    }


def _build_code_fingerprint(file_paths: list[Path] | None = None) -> dict[str, Any]:
    paths = file_paths or DEFAULT_CODE_FINGERPRINT_PATHS
    existing_paths = [path for path in paths if path.exists()]
    if not existing_paths:
        return {
            "status": "unavailable",
            "scope": "runtime_service_preflight_surface_v1",
            "fingerprint": None,
            "sources": [],
        }

    hasher = hashlib.sha256()
    serialized_sources: list[str] = []
    for path in existing_paths:
        serialized_sources.append(str(path))
        hasher.update(str(path).encode("utf-8"))
        hasher.update(path.read_bytes())

    return {
        "status": "available",
        "scope": "runtime_service_preflight_surface_v1",
        "fingerprint": hasher.hexdigest()[:16],
        "sources": serialized_sources,
        "source_count": len(serialized_sources),
    }


def _evaluate_code_freshness(
    code_fingerprint: dict[str, Any],
    expected_code_fingerprint: str | None = None,
) -> dict[str, Any]:
    actual_fingerprint = code_fingerprint.get("fingerprint")
    if not expected_code_fingerprint:
        return {
            "status": "unchecked",
            "expected_fingerprint": None,
            "actual_fingerprint": actual_fingerprint,
        }
    if not actual_fingerprint:
        return {
            "status": "unavailable",
            "expected_fingerprint": expected_code_fingerprint,
            "actual_fingerprint": actual_fingerprint,
        }
    if actual_fingerprint == expected_code_fingerprint:
        return {
            "status": "match",
            "expected_fingerprint": expected_code_fingerprint,
            "actual_fingerprint": actual_fingerprint,
        }
    return {
        "status": "mismatch",
        "expected_fingerprint": expected_code_fingerprint,
        "actual_fingerprint": actual_fingerprint,
    }


def _build_canonical_launch(host: str, port: int) -> dict[str, Any]:
    repo_python = DEFAULT_REPO_PYTHON_PATH
    repo_uvicorn = DEFAULT_REPO_UVICORN_PATH
    service_entry = DEFAULT_REPO_SERVICE_ENTRY
    if platform.system() == "Windows" and repo_uvicorn.exists():
        launch_mode = "repo_uvicorn_entry"
        launcher_path = repo_uvicorn
        command_line = f'"{repo_uvicorn}" main:app --host {host} --port {port}'
    else:
        launch_mode = "repo_python_service_entry"
        launcher_path = repo_python
        command_line = f'"{repo_python}" "{service_entry}" --host {host} --port {port}'
    return {
        "status": "defined" if repo_python.exists() and service_entry.exists() else "incomplete",
        "interpreter_path": str(repo_python),
        "launcher_path": str(launcher_path),
        "launch_mode": launch_mode,
        "service_entry_path": str(service_entry),
        "host": host,
        "port": port,
        "command_line": command_line,
        "interpreter_exists": repo_python.exists(),
        "launcher_exists": launcher_path.exists(),
        "service_entry_exists": service_entry.exists(),
    }


def _evaluate_windows_venv_redirector_candidate(
    port_ownership: PortOwnershipInfo,
    owner_chain: dict[str, Any],
    repo_launcher: dict[str, Any],
    pyvenv_cfg_path: Path | None = None,
) -> dict[str, Any]:
    cfg_path = pyvenv_cfg_path or DEFAULT_PYVENV_CFG_PATH
    if platform.system() != "Windows":
        return {"status": "not_applicable", "candidate": False}
    if port_ownership.unique_count != 1 or not port_ownership.listening_processes:
        return {"status": "indeterminate", "candidate": False}
    if owner_chain.get("status") != "parent_preferred_child_mismatch":
        return {"status": "not_candidate", "candidate": False}
    if repo_launcher.get("status") != "parent_and_child_repo_launcher_match":
        return {"status": "not_candidate", "candidate": False}
    if not cfg_path.exists():
        return {"status": "missing_pyvenv_cfg", "candidate": False}

    cfg: dict[str, str] = {}
    for line in cfg_path.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        cfg[key.strip().lower()] = value.strip()

    base_executable = cfg.get("executable") or cfg.get("home")
    process = port_ownership.listening_processes[0]
    child_command_line = str(process.get("command_line", "")).lower()
    if base_executable and base_executable.lower() in child_command_line:
        return {
            "status": "windows_venv_redirector_candidate",
            "candidate": True,
            "base_executable": base_executable,
            "pyvenv_cfg_path": str(cfg_path),
        }
    return {
        "status": "not_candidate",
        "candidate": False,
        "base_executable": base_executable,
        "pyvenv_cfg_path": str(cfg_path),
    }


async def check_api_health(
    host: str = DEFAULT_API_HOST,
    port: int = DEFAULT_API_PORT,
    endpoint: str = DEFAULT_HEALTH_ENDPOINT,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> ApiHealthInfo:
    """Check API health endpoint accessibility.

    Uses httpx for async HTTP call to the health endpoint.

    Args:
        host: API host address
        port: API port number
        endpoint: Health endpoint path (e.g., "/health")
        timeout_seconds: Request timeout

    Returns:
        ApiHealthInfo with health check results
    """
    import httpx

    url = f"http://{host}:{port}{endpoint}"
    info = ApiHealthInfo(endpoint=url)

    try:
        start_time = datetime.now(timezone.utc)
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.get(url)
        end_time = datetime.now(timezone.utc)

        info.response_status = response.status_code
        info.response_time_ms = (end_time - start_time).total_seconds() * 1000

        try:
            info.response_body = response.json()
        except Exception:
            info.response_body = None

        info.is_healthy = response.status_code == 200

    except httpx.ConnectError as exc:
        info.is_healthy = False
        info.error_message = f"Connection refused: {exc}"
    except httpx.TimeoutException as exc:
        info.is_healthy = False
        info.error_message = f"Timeout after {timeout_seconds}s: {exc}"
    except Exception as exc:
        info.is_healthy = False
        info.error_message = f"Unexpected error: {exc}"

    return info


def check_port_ownership_windows(port: int) -> PortOwnershipInfo:
    """Check port ownership on Windows using netstat or PowerShell.

    Uses Get-CimInstance to find processes with matching command lines
    for uvicorn or run_service, and netstat for port listeners.

    Args:
        port: Port number to check

    Returns:
        PortOwnershipInfo with port ownership details
    """
    info = PortOwnershipInfo(port=port, inspection_method="windows_powershell")

    try:
        # Use netstat to find listening processes on the port
        # netstat -ano shows PID for each connection
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            info.inspection_error = f"netstat failed: {result.stderr}"
            return info

        listening_pids: set[int] = set()

        for line in result.stdout.splitlines():
            # Look for LISTENING state on the port
            # Format: Proto  Local Address  Foreign Address  State  PID
            if "LISTENING" not in line:
                continue
            parts = line.split()
            if len(parts) < 5:
                continue

            local_addr = parts[1]
            pid_str = parts[-1]

            # Check if local address matches the port
            # IPv4: 127.0.0.1:8000 or 0.0.0.0:8000
            # IPv6: [::]:8000 or [::1]:8000
            if f":{port}" in local_addr:
                try:
                    pid = int(pid_str)
                    listening_pids.add(pid)
                except ValueError:
                    pass

        info.unique_count = len(listening_pids)
        info.is_clear = info.unique_count == 1

        # Get process details for each PID
        for pid in listening_pids:
            try:
                proc_result = subprocess.run(
                    ["powershell", "-Command",
                     f"Get-CimInstance Win32_Process -Filter 'ProcessId={pid}' | "
                     "Select-Object ProcessId, ParentProcessId, Name, CommandLine | "
                     "ConvertTo-Json"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if proc_result.returncode == 0 and proc_result.stdout:
                    import json
                    proc_data = json.loads(proc_result.stdout.strip())
                    if proc_data:
                        parent_pid = proc_data.get("ParentProcessId")
                        parent_name = ""
                        parent_command_line = ""
                        if parent_pid:
                            try:
                                parent_result = subprocess.run(
                                    ["powershell", "-Command",
                                     f"Get-CimInstance Win32_Process -Filter 'ProcessId={parent_pid}' | "
                                     "Select-Object ProcessId, Name, CommandLine | "
                                     "ConvertTo-Json"],
                                    capture_output=True,
                                    text=True,
                                    timeout=10,
                                )
                                if parent_result.returncode == 0 and parent_result.stdout:
                                    parent_data = json.loads(parent_result.stdout.strip())
                                    if parent_data:
                                        parent_name = parent_data.get("Name", "")
                                        parent_command_line = parent_data.get("CommandLine", "")
                            except Exception:
                                pass
                        info.listening_processes.append({
                            "pid": pid,
                            "name": proc_data.get("Name", ""),
                            "parent_pid": parent_pid,
                            "parent_name": parent_name,
                            "parent_command_line": parent_command_line,
                            "command_line": proc_data.get("CommandLine", ""),
                        })
            except Exception:
                info.listening_processes.append({"pid": pid, "name": "unknown"})

    except subprocess.TimeoutExpired:
        info.inspection_error = "Port inspection timed out"
    except Exception as exc:
        info.inspection_error = f"Inspection error: {exc}"

    return info


def check_port_ownership_unix(port: int) -> PortOwnershipInfo:
    """Check port ownership on Unix/Linux/Mac using lsof or netstat.

    Args:
        port: Port number to check

    Returns:
        PortOwnershipInfo with port ownership details
    """
    info = PortOwnershipInfo(port=port, inspection_method="unix_lsof")

    listening_pids: set[int] = set()

    try:
        # Use lsof to find processes listening on the port
        # lsof -i :PORT -P -n
        result = subprocess.run(
            ["lsof", "-i", f":{port}", "-P", "-n"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # lsof returns 0 if found, 1 if not found
        if result.returncode == 0 and result.stdout:
            for line in result.stdout.splitlines()[1:]:  # Skip header
                if "LISTEN" not in line:
                    continue
                parts = line.split()
                if len(parts) < 2:
                    continue

                # Extract PID (first column after COMMAND)
                try:
                    pid = int(parts[1])
                    listening_pids.add(pid)
                    info.listening_processes.append({
                        "pid": pid,
                        "name": parts[0],
                        "command": parts[0] if parts else "",
                    })
                except ValueError:
                    pass

    except FileNotFoundError:
        # lsof not available, try netstat fallback
        info.inspection_method = "unix_netstat"
        try:
            result = subprocess.run(
                ["netstat", "-tlnp"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if f":{port}" in line and "LISTEN" in line:
                        # netstat -tlnp format varies, try to extract PID
                        # Format: Proto Recv-Q Send-Q Local Address Foreign Address State PID/Program name
                        parts = line.split()
                        if len(parts) >= 7:
                            pid_prog = parts[-1]
                            if "/" in pid_prog:
                                pid_str, prog = pid_prog.split("/", 1)
                                try:
                                    pid = int(pid_str)
                                    listening_pids.add(pid)
                                    info.listening_processes.append({
                                        "pid": pid,
                                        "name": prog,
                                        "command": prog,
                                    })
                                except ValueError:
                                    pass
        except FileNotFoundError:
            info.inspection_error = "lsof/netstat not available"
        except subprocess.TimeoutExpired:
            info.inspection_error = "Port inspection timed out"
        except Exception as exc:
            info.inspection_error = f"netstat inspection error: {exc}"

    except subprocess.TimeoutExpired:
        info.inspection_error = "Port inspection timed out"
    except Exception as exc:
        info.inspection_error = f"Inspection error: {exc}"

    info.unique_count = len(listening_pids)
    info.is_clear = info.unique_count == 1

    return info


def check_port_ownership(port: int = DEFAULT_API_PORT) -> PortOwnershipInfo:
    """Check port ownership using platform-specific methods.

    Args:
        port: Port number to check

    Returns:
        PortOwnershipInfo with port ownership details
    """
    system = platform.system()

    if system == "Windows":
        return check_port_ownership_windows(port)
    else:
        return check_port_ownership_unix(port)


async def run_preflight(
    host: str = DEFAULT_API_HOST,
    port: int = DEFAULT_API_PORT,
    health_endpoint: str = DEFAULT_HEALTH_ENDPOINT,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    preferred_owner_hints: list[str] | None = None,
    strict_preferred_owner: bool = False,
    expected_code_fingerprint: str | None = None,
    strict_code_freshness: bool = False,
    self_check_current_code: bool = False,
) -> PreflightResult:
    """Run complete service preflight check.

    Combines API health check and port ownership inspection to determine
    whether live proof is safe to proceed.

    Args:
        host: API host address
        port: API port number
        health_endpoint: Health endpoint path
        timeout_seconds: Request timeout for health check

    Returns:
        PreflightResult with complete preflight status
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    # Run health check and port inspection
    api_health = await check_api_health(host, port, health_endpoint, timeout_seconds)
    port_ownership = check_port_ownership(port)

    # Determine overall status
    preferred_owner = _evaluate_preferred_owner(port_ownership, preferred_owner_hints)
    owner_chain = _evaluate_owner_chain(port_ownership, preferred_owner_hints)
    repo_launcher = _evaluate_repo_launcher(port_ownership)
    windows_venv_redirector = _evaluate_windows_venv_redirector_candidate(
        port_ownership,
        owner_chain,
        repo_launcher,
    )
    code_fingerprint = _build_code_fingerprint()
    resolved_expected_code_fingerprint = expected_code_fingerprint
    if self_check_current_code and not resolved_expected_code_fingerprint:
        resolved_expected_code_fingerprint = code_fingerprint.get("fingerprint")
    code_freshness = _evaluate_code_freshness(
        code_fingerprint,
        expected_code_fingerprint=resolved_expected_code_fingerprint,
    )
    canonical_launch = _build_canonical_launch(host, port)
    controller_acceptability = _evaluate_controller_acceptability(
        api_health,
        port_ownership,
        preferred_owner,
        owner_chain,
        repo_launcher,
        windows_venv_redirector,
        canonical_launch,
        code_freshness,
    )
    controller_promotion = _evaluate_controller_promotion(controller_acceptability)
    status = determine_preflight_status(
        api_health,
        port_ownership,
        preferred_owner=preferred_owner,
        strict_preferred_owner=strict_preferred_owner,
        code_freshness=code_freshness,
        strict_code_freshness=strict_code_freshness,
    )

    # Build summary
    summary = build_preflight_summary(
        status,
        api_health,
        port_ownership,
        code_freshness=code_freshness,
    )

    # Build details
    details = {
        "api_endpoint": api_health.endpoint,
        "api_port": port,
        "api_host": host,
        "health_response_time_ms": api_health.response_time_ms,
        "port_inspection_method": port_ownership.inspection_method,
        "listening_process_count": port_ownership.unique_count,
    }

    if port_ownership.listening_processes:
        details["processes"] = [
            {"pid": p.get("pid"), "name": p.get("name")}
            for p in port_ownership.listening_processes
        ]

    if api_health.error_message:
        details["health_error"] = api_health.error_message

    if port_ownership.inspection_error:
        details["port_error"] = port_ownership.inspection_error

    details["preferred_owner"] = preferred_owner
    details["owner_chain"] = owner_chain
    details["repo_launcher"] = repo_launcher
    details["windows_venv_redirector"] = windows_venv_redirector
    details["strict_preferred_owner"] = strict_preferred_owner
    details["code_fingerprint"] = code_fingerprint
    details["code_freshness"] = code_freshness
    details["strict_code_freshness"] = strict_code_freshness
    details["controller_acceptability"] = controller_acceptability
    details["controller_promotion"] = controller_promotion
    details["canonical_launch"] = canonical_launch

    return PreflightResult(
        status=status,
        timestamp=timestamp,
        api_health=api_health,
        port_ownership=port_ownership,
        summary=summary,
        details=details,
    )


def determine_preflight_status(
    api_health: ApiHealthInfo,
    port_ownership: PortOwnershipInfo,
    preferred_owner: dict[str, Any] | None = None,
    strict_preferred_owner: bool = False,
    code_freshness: dict[str, Any] | None = None,
    strict_code_freshness: bool = False,
) -> PreflightStatus:
    """Determine overall preflight status from health and port checks.

    Logic:
    - DOWN: API health endpoint unreachable or connection refused
    - AMBIGUOUS: API healthy but port ownership unclear (multiple or zero processes)
    - READY: API healthy AND exactly one process owns the port

    Args:
        api_health: API health check result
        port_ownership: Port ownership inspection result

    Returns:
        PreflightStatus for controller decision
    """
    # If API is down, that's the primary signal
    if not api_health.is_healthy:
        return PreflightStatus.DOWN

    # If API is healthy but port ownership is unclear
    if not port_ownership.is_clear:
        # Multiple processes or no processes detected
        return PreflightStatus.AMBIGUOUS

    if strict_preferred_owner:
        preferred_status = (preferred_owner or {}).get("status")
        if preferred_status != "preferred_match":
            return PreflightStatus.AMBIGUOUS

    if strict_code_freshness:
        code_freshness_status = (code_freshness or {}).get("status")
        if code_freshness_status != "match":
            return PreflightStatus.AMBIGUOUS

    # API healthy and port ownership clear
    return PreflightStatus.READY


def build_preflight_summary(
    status: PreflightStatus,
    api_health: ApiHealthInfo,
    port_ownership: PortOwnershipInfo,
    code_freshness: dict[str, Any] | None = None,
) -> str:
    """Build human-readable summary for the preflight result.

    Args:
        status: Overall preflight status
        api_health: API health check result
        port_ownership: Port ownership inspection result

    Returns:
        One-line summary string
    """
    if status == PreflightStatus.DOWN:
        if api_health.error_message:
            return f"API down: {api_health.error_message}"
        return "API down: health endpoint unreachable"

    if status == PreflightStatus.AMBIGUOUS:
        code_freshness_status = (code_freshness or {}).get("status")
        if code_freshness_status == "mismatch":
            return "Ambiguous: live service code fingerprint mismatch"
        if port_ownership.unique_count == 0:
            return f"Ambiguous: API healthy but no process detected on port {port_ownership.port}"
        if port_ownership.unique_count > 1:
            return (
                f"Ambiguous: {port_ownership.unique_count} processes "
                f"claim port {port_ownership.port}"
            )
        if port_ownership.inspection_error:
            return f"Ambiguous: port inspection failed - {port_ownership.inspection_error}"
        return "Ambiguous: port ownership unclear"

    # READY
    return (
        f"Ready: API healthy at {api_health.endpoint} "
        f"({api_health.response_time_ms:.1f}ms), "
        f"single process owns port {port_ownership.port}"
    )


# Convenience function for synchronous callers
def run_preflight_sync(
    host: str = DEFAULT_API_HOST,
    port: int = DEFAULT_API_PORT,
    health_endpoint: str = DEFAULT_HEALTH_ENDPOINT,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    preferred_owner_hints: list[str] | None = None,
    strict_preferred_owner: bool = False,
    expected_code_fingerprint: str | None = None,
    strict_code_freshness: bool = False,
    self_check_current_code: bool = False,
) -> PreflightResult:
    """Synchronous wrapper for run_preflight.

    Convenience for callers that cannot use async.

    Args:
        host: API host address
        port: API port number
        health_endpoint: Health endpoint path
        timeout_seconds: Request timeout

    Returns:
        PreflightResult with complete preflight status
    """
    return asyncio.run(
        run_preflight(
            host,
            port,
            health_endpoint,
            timeout_seconds,
            preferred_owner_hints=preferred_owner_hints,
            strict_preferred_owner=strict_preferred_owner,
            expected_code_fingerprint=expected_code_fingerprint,
            strict_code_freshness=strict_code_freshness,
            self_check_current_code=self_check_current_code,
        )
    )
