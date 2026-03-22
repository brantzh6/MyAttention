#!/usr/bin/env python3
"""
MyAttention cross-platform development launcher.

Supports:
- setup validation and bootstrap
- start api / web / infra / watchdog / dev
- stop api / web / infra / postgres / redis / watchdog / dev
- status
- health
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


REPO_ROOT = Path(__file__).resolve().parent
CONFIG_DIR = REPO_ROOT / "config" / "runtime"
RUNTIME_DIR = REPO_ROOT / ".runtime"
RUNTIME_LOG_DIR = RUNTIME_DIR / "logs"
DEFAULT_MODE = "local-process"
DEFAULT_TIMEOUT = 30
DEFAULT_WINDOWS_SERVICE_NAMES = {
    "api": "MyAttentionApi",
    "web": "MyAttentionWeb",
    "watchdog": "MyAttentionWatchdog",
}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_runtime_config(mode: str) -> dict[str, Any]:
    config_path = CONFIG_DIR / f"{mode}.toml"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing runtime config: {config_path}")

    with config_path.open("rb") as fh:
        config = tomllib.load(fh)

    local_override = CONFIG_DIR / f"{mode}.local.toml"
    if local_override.exists():
        with local_override.open("rb") as fh:
            config = deep_merge(config, tomllib.load(fh))

    return config


def runtime_paths() -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_LOG_DIR.mkdir(parents=True, exist_ok=True)


def pid_file(name: str) -> Path:
    runtime_paths()
    return RUNTIME_DIR / f"{name}.pid"


def meta_file(name: str) -> Path:
    runtime_paths()
    return RUNTIME_DIR / f"{name}.json"


def component_log_path(name: str) -> Path:
    runtime_paths()
    return RUNTIME_LOG_DIR / f"{name}.log"


def read_pid(name: str) -> int | None:
    path = pid_file(name)
    if not path.exists():
        return None
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except Exception:
        return None


def write_pid(name: str, pid: int) -> None:
    pid_file(name).write_text(str(pid), encoding="utf-8")


def write_meta(name: str, data: dict[str, Any]) -> None:
    meta_file(name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_meta(name: str) -> dict[str, Any] | None:
    path = meta_file(name)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def clear_pid(name: str) -> None:
    path = pid_file(name)
    if path.exists():
        path.unlink()


def clear_meta(name: str) -> None:
    path = meta_file(name)
    if path.exists():
        path.unlink()


def is_pid_running(pid: int | None) -> bool:
    if not pid:
        return False
    if os.name == "nt":
        result = run_capture(f'tasklist /FI "PID eq {pid}" /FO CSV /NH')
        output = ((result.stdout or "") + (result.stderr or "")).strip()
        if not output or output.startswith("INFO:"):
            return False
        return f'"{pid}"' in output or f",{pid}," in output
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def run_capture(command: str, workdir: Path | None = None) -> subprocess.CompletedProcess[str]:
    args = windows_command_args(command) if os.name == "nt" else shlex.split(command, posix=True)
    return subprocess.run(
        args,
        cwd=str(workdir or REPO_ROOT),
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def service_enabled(config: dict[str, Any], name: str) -> bool:
    service_cfg = config.get(name, {})
    return os.name == "nt" and bool(service_cfg.get("use_service", False))


def service_name(config: dict[str, Any], name: str) -> str:
    service_cfg = config.get(name, {})
    configured = str(service_cfg.get("service_name", "")).strip()
    if configured:
        return configured
    return name


def default_windows_service_name(name: str) -> str:
    return DEFAULT_WINDOWS_SERVICE_NAMES.get(name, "")


def candidate_service_names(config: dict[str, Any], name: str) -> list[str]:
    names: list[str] = []
    configured = str(config.get(name, {}).get("service_name", "")).strip()
    default_name = default_windows_service_name(name)
    for candidate in (configured, default_name):
        if candidate and candidate not in names:
            names.append(candidate)
    return names


def service_log_path(config: dict[str, Any], name: str) -> Path | None:
    service_cfg = config.get(name, {})
    configured = str(service_cfg.get("log_path", "")).strip()
    if not configured:
        return None
    return resolve_config_path(configured)


def component_log_path_for(config: dict[str, Any], name: str) -> Path:
    return service_log_path(config, name) or component_log_path(name)


def service_exists_name(name: str) -> bool:
    result = run_capture(f'sc.exe qc "{name}"')
    return result.returncode == 0


def service_exists(config: dict[str, Any], name: str) -> bool:
    return service_exists_name(service_name(config, name))


def parse_sc_field(output: str, field: str) -> str:
    pattern = re.compile(rf"^\s*{re.escape(field)}\s*:\s*(.+)$", re.MULTILINE)
    match = pattern.search(output)
    return match.group(1).strip() if match else ""


def windows_service_info_by_name(
    name: str,
    *,
    log_path: Path | None = None,
    mode: str = "service",
) -> dict[str, Any]:
    info = {
        "mode": mode,
        "name": name,
        "registered": False,
        "running": False,
        "pid": None,
        "start_type": "",
        "state": "",
        "log_path": str(log_path) if log_path else "",
    }
    if not service_exists_name(name):
        return info

    info["registered"] = True
    qc = run_capture(f'sc.exe qc "{name}"')
    qc_output = (qc.stdout or "") + (qc.stderr or "")
    info["start_type"] = parse_sc_field(qc_output, "START_TYPE")

    query = run_capture(f'sc.exe queryex "{name}"')
    query_output = (query.stdout or "") + (query.stderr or "")
    state_raw = parse_sc_field(query_output, "STATE")
    pid_raw = parse_sc_field(query_output, "PID")
    if state_raw:
        parts = state_raw.split()
        info["state"] = parts[-1] if parts else state_raw
        info["running"] = "RUNNING" in state_raw
    if pid_raw.isdigit():
        info["pid"] = int(pid_raw)
    return info


def windows_service_info(config: dict[str, Any], name: str) -> dict[str, Any]:
    info = windows_service_info_by_name(
        service_name(config, name),
        log_path=service_log_path(config, name),
        mode="service" if service_enabled(config, name) else "process",
    )
    if not service_enabled(config, name):
        info["mode"] = "process"
        info["registered"] = False
        info["running"] = False
        info["pid"] = None
        info["start_type"] = ""
        info["state"] = ""
    return info


def residual_service_info(config: dict[str, Any], name: str) -> dict[str, Any] | None:
    if os.name != "nt" or service_enabled(config, name):
        return None
    for candidate in candidate_service_names(config, name):
        info = windows_service_info_by_name(candidate, log_path=service_log_path(config, name))
        if info["registered"]:
            return info
    return None


def component_runtime_info(config: dict[str, Any], name: str) -> dict[str, Any]:
    if service_enabled(config, name):
        info = windows_service_info(config, name)
        return {
            "mode": info["mode"],
            "pid": info["pid"],
            "running": info["running"],
            "meta": {
                "service_name": info["name"],
                "state": info["state"],
                "start_type": info["start_type"],
                "log_path": info["log_path"],
                "registered": info["registered"],
            },
        }

    pid = read_pid(name)
    meta = read_meta(name) or {}
    residual = residual_service_info(config, name)
    if residual:
        meta = dict(meta)
        meta["residual_service"] = {
            "service_name": residual["name"],
            "state": residual["state"],
            "running": residual["running"],
            "start_type": residual["start_type"],
        }
    return {
        "mode": "process",
        "pid": pid,
        "running": is_pid_running(pid),
        "meta": meta or None,
    }


def start_windows_service(config: dict[str, Any], name: str) -> int:
    svc = service_name(config, name)
    result = run_capture(f'sc.exe start "{svc}"')
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0 and "service has already been started" not in output.lower():
        print(output.strip() or f"Failed to start service {svc}")
        return 1
    print(output.strip() or f"Start requested for service {svc}")
    return 0


def stop_windows_service(config: dict[str, Any], name: str) -> int:
    svc = service_name(config, name)
    result = run_capture(f'sc.exe stop "{svc}"')
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0 and "service has not been started" not in output.lower():
        print(output.strip() or f"Failed to stop service {svc}")
        return 1
    print(output.strip() or f"Stop requested for service {svc}")
    return 0


def wait_for_service_state(service: str, desired_state: str, timeout: int = 20) -> bool:
    deadline = time.time() + timeout
    desired = desired_state.upper()
    while time.time() < deadline:
        info = windows_service_info_by_name(service)
        state = str(info.get("state", "")).upper()
        if desired == "DELETED":
            if not info.get("registered"):
                return True
        elif state == desired:
            return True
        time.sleep(1)
    return False


def stop_residual_windows_service(config: dict[str, Any], name: str) -> bool:
    residual = residual_service_info(config, name)
    if not residual or not residual.get("registered"):
        return False

    service = str(residual["name"])
    if residual.get("running"):
        print(f"Stopping residual {name} service {service}")
        run_capture(f'sc.exe stop "{service}"')
        wait_for_service_state(service, "STOPPED", timeout=20)

    return True


def quote_arg(value: str) -> str:
    if os.name == "nt":
        return f'"{value}"'
    return shlex.quote(value)


def command_env(config: dict[str, Any]) -> dict[str, str]:
    runtime_cfg = config.get("runtime", {})
    api_port = int(runtime_cfg.get("api_port", 8000))
    web_port = int(runtime_cfg.get("web_port", 3000))
    api_host = runtime_cfg.get("api_host", "0.0.0.0")
    web_host = runtime_cfg.get("web_host", "127.0.0.1")
    return {
        "repo_root": str(REPO_ROOT),
        "api_port": str(api_port),
        "web_port": str(web_port),
        "api_host": str(api_host),
        "web_host": str(web_host),
    }


def format_command(template: str, config: dict[str, Any], extra: dict[str, str] | None = None) -> str:
    context = command_env(config)
    if extra:
        context.update(extra)
    return template.format(**context)


def resolve_config_path(path_value: str, workdir: Path | None = None) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    if workdir is not None:
        return (workdir / path).resolve()
    return (REPO_ROOT / path).resolve()


def resolve_tool(config: dict[str, Any], key: str, fallback: str) -> str:
    tools_cfg = config.get("tools", {})
    configured = str(tools_cfg.get(key, "")).strip()
    if configured:
        configured_path = Path(configured)
        if configured_path.is_absolute() or configured.startswith("."):
            return str(resolve_config_path(configured))
        return configured
    return fallback


def command_exists(command: str) -> bool:
    command_path = Path(command)
    if command_path.is_absolute() or "\\" in command or "/" in command:
        return command_path.exists()
    return shutil.which(command) is not None


def resolve_bootstrap_python(config: dict[str, Any]) -> str:
    return resolve_tool(config, "bootstrap_python", sys.executable)


def venv_python_path(config: dict[str, Any]) -> Path:
    setup_cfg = config.get("setup", {})
    venv_root = resolve_config_path(setup_cfg.get("venv_path", ".venv"))
    if os.name == "nt":
        return venv_root / "Scripts" / "python.exe"
    return venv_root / "bin" / "python"


def resolve_python(config: dict[str, Any]) -> str:
    api_cfg = config.get("api", {})
    configured = str(api_cfg.get("python", "")).strip()
    if configured:
        if configured.startswith(".") or Path(configured).is_absolute():
            return str(resolve_config_path(configured))
        return configured

    venv_python = venv_python_path(config)
    if venv_python.exists():
        return str(venv_python)

    return resolve_bootstrap_python(config)


def watchdog_python(config: dict[str, Any]) -> str:
    watchdog_cfg = config.get("watchdog", {})
    configured = str(watchdog_cfg.get("python", "")).strip()
    if configured:
        if configured.startswith(".") or Path(configured).is_absolute():
            return str(resolve_config_path(configured))
        return configured
    return resolve_python(config)


def detect_package_manager(workdir: Path) -> str:
    if (workdir / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (workdir / "yarn.lock").exists():
        return "yarn"
    return "npm"


def resolve_package_manager(config: dict[str, Any]) -> str:
    tools_cfg = config.get("tools", {})
    configured = str(tools_cfg.get("package_manager", "")).strip()
    if configured:
        return configured
    web_workdir = resolve_config_path(config.get("web", {}).get("workdir", "services/web"))
    return detect_package_manager(web_workdir)


def package_manager_command(config: dict[str, Any], subcommand: str) -> str:
    package_manager = resolve_package_manager(config)
    tools_cfg = config.get("tools", {})
    executable = str(tools_cfg.get(package_manager, "")).strip()
    if os.name == "nt" and package_manager in {"npm", "pnpm", "yarn"} and executable in {"", package_manager}:
        executable = f"{package_manager}.cmd"
    if not executable:
        executable = package_manager
    executable = quote_arg(executable) if (Path(executable).is_absolute() or "\\" in executable or "/" in executable or " " in executable) else executable
    if package_manager == "yarn":
        if subcommand == "install":
            return executable
        if subcommand == "dev":
            return f"{executable} dev"
    if package_manager == "pnpm":
        return f"{executable} {subcommand}"
    if package_manager == "npm":
        if subcommand == "install":
            return f"{executable} install"
        return f"{executable} run {subcommand}"
    return f"{executable} {subcommand}"


def test_tcp(host: str, port: int, timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def http_ok(url: str, timeout: float = 3.0) -> tuple[bool, str]:
    try:
        response = requests.get(url, timeout=timeout)
        return response.ok, f"HTTP {response.status_code}"
    except Exception as exc:
        return False, str(exc)


def windows_command_args(command: str) -> list[str]:
    args = [arg[1:-1] if len(arg) >= 2 and arg.startswith('"') and arg.endswith('"') else arg for arg in shlex.split(command, posix=False)]
    if args and args[0].lower().endswith((".cmd", ".bat")):
        return ["cmd.exe", "/c", *args]
    return args


def detached_popen(
    command: str,
    workdir: Path,
    extra_env: dict[str, str] | None = None,
    stdout_path: Path | None = None,
) -> subprocess.Popen[Any]:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    args = windows_command_args(command) if os.name == "nt" else shlex.split(command, posix=True)
    log_handle = None
    stdout_target: Any = subprocess.DEVNULL
    stderr_target: Any = subprocess.DEVNULL
    if stdout_path is not None:
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        log_handle = stdout_path.open("ab")
        stdout_target = log_handle
        stderr_target = subprocess.STDOUT
    kwargs: dict[str, Any] = {
        "cwd": str(workdir),
        "env": env,
        "shell": False,
        "stdout": stdout_target,
        "stderr": stderr_target,
    }

    if os.name == "nt":
        kwargs["creationflags"] = (
            subprocess.CREATE_NEW_PROCESS_GROUP
            | getattr(subprocess, "DETACHED_PROCESS", 0)
            | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
    else:
        kwargs["start_new_session"] = True

    try:
        process = subprocess.Popen(args, **kwargs)
    finally:
        if log_handle is not None:
            log_handle.close()
    return process


def run_command(command: str, workdir: Path, extra_env: dict[str, str] | None = None) -> int:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    args = windows_command_args(command) if os.name == "nt" else shlex.split(command, posix=True)
    result = subprocess.run(args, cwd=str(workdir), env=env, shell=False)
    return result.returncode


def start_component(name: str, command: str, workdir: Path, env: dict[str, str]) -> bool:
    pid = read_pid(name)
    if is_pid_running(pid):
        print(f"{name} already running (pid={pid})")
        return True
    clear_pid(name)
    clear_meta(name)

    log_path = component_log_path(name)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(f"\n[{datetime.now(timezone.utc).isoformat()}] START {name}\n")
        fh.write(f"command={command}\n")
        fh.write(f"workdir={workdir}\n")

    process = detached_popen(command, workdir, env, stdout_path=log_path)
    write_pid(name, process.pid)
    write_meta(
        name,
        {
            "pid": process.pid,
            "command": command,
            "workdir": str(workdir),
            "log_path": str(log_path),
            "started_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    print(f"Started {name} (pid={process.pid})")
    return True


def stop_component(name: str) -> bool:
    pid = read_pid(name)
    if not is_pid_running(pid):
        clear_pid(name)
        clear_meta(name)
        print(f"{name} not running")
        return True

    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        else:
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
            if is_pid_running(pid):
                kill_signal = signal.SIGKILL if hasattr(signal, "SIGKILL") else signal.SIGTERM
                os.kill(pid, kill_signal)
        print(f"Stopped {name} (pid={pid})")
    finally:
        clear_pid(name)
        clear_meta(name)
    return True


def build_api_command(config: dict[str, Any]) -> tuple[str, Path, dict[str, str]]:
    api_cfg = config.get("api", {})
    runtime_cfg = config.get("runtime", {})
    workdir = resolve_config_path(api_cfg.get("workdir", "services/api"))
    python_exe = resolve_python(config)
    entry = str(api_cfg.get("entry", "")).strip()
    command = str(api_cfg.get("command", "")).strip()
    host = runtime_cfg.get("api_host", "0.0.0.0")
    port = int(runtime_cfg.get("api_port", 8000))

    if command:
        command = format_command(command, config, {"python": python_exe})
    elif entry:
        entry_path = resolve_config_path(entry, workdir)
        command = f"{quote_arg(python_exe)} {quote_arg(str(entry_path))}"
    else:
        command = (
            f"{quote_arg(python_exe)} -m uvicorn main:app "
            f"--reload --host {host} --port {port}"
        )

    env = {
        "API_PORT": str(port),
        "DEPLOYMENT_MODE": runtime_cfg.get("mode", DEFAULT_MODE),
        "INFRASTRUCTURE_MODE": runtime_cfg.get("mode", DEFAULT_MODE),
        "PYTHONUTF8": "1",
    }
    return command, workdir, env


def build_service_commands(
    config: dict[str, Any], name: str
) -> tuple[str | None, str | None, Path, dict[str, str]]:
    service_cfg = config.get(name, {})
    start_command = str(service_cfg.get("start_command", "")).strip() or None
    stop_command = str(service_cfg.get("stop_command", "")).strip() or None
    env = {
        "PYTHONUTF8": "1",
    }
    if start_command:
        start_command = format_command(start_command, config)
    if stop_command:
        stop_command = format_command(stop_command, config)
    return start_command, stop_command, REPO_ROOT, env


def build_web_command(config: dict[str, Any]) -> tuple[str, Path, dict[str, str]]:
    web_cfg = config.get("web", {})
    runtime_cfg = config.get("runtime", {})
    workdir = resolve_config_path(web_cfg.get("workdir", "services/web"))
    api_port = int(runtime_cfg.get("api_port", 8000))
    web_port = int(runtime_cfg.get("web_port", 3000))
    web_host = runtime_cfg.get("web_host", "127.0.0.1")

    command = str(web_cfg.get("command", "")).strip()
    if command:
        command = format_command(command, config)
    else:
        command = package_manager_command(config, "dev")

    standalone_server = workdir / ".next" / "standalone" / "server.js"
    if ".next/standalone/server.js" in command and not standalone_server.exists():
        command = (
            f"node {quote_arg(str(workdir / 'node_modules' / 'next' / 'dist' / 'bin' / 'next'))} "
            f"dev --hostname {web_host} --port {web_port}"
        )

    env = {
        "PORT": str(web_port),
        "HOSTNAME": str(web_host),
        "API_URL": f"http://127.0.0.1:{api_port}",
        "NEXT_PUBLIC_API_URL": f"http://127.0.0.1:{api_port}",
    }
    return command, workdir, env


def sync_web_standalone_assets(config: dict[str, Any]) -> None:
    web_cfg = config.get("web", {})
    workdir = resolve_config_path(web_cfg.get("workdir", "services/web"))
    standalone_root = workdir / ".next" / "standalone"
    standalone_server = standalone_root / "server.js"

    if not standalone_server.exists():
        return

    static_source = workdir / ".next" / "static"
    static_target = standalone_root / ".next" / "static"
    if static_source.exists():
        static_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(static_source, static_target, dirs_exist_ok=True)

    public_source = workdir / "public"
    public_target = standalone_root / "public"
    if public_source.exists():
        shutil.copytree(public_source, public_target, dirs_exist_ok=True)


def build_watchdog_command(config: dict[str, Any], mode: str) -> tuple[str, Path, dict[str, str]]:
    watchdog_cfg = config.get("watchdog", {})
    python_exe = watchdog_python(config)
    command = str(watchdog_cfg.get("command", "")).strip()
    if command:
        command = format_command(command, config, {"python": python_exe, "mode": mode})
    else:
        script_path = resolve_config_path(watchdog_cfg.get("script", "runtime_watchdog.py"))
        command = f"{quote_arg(python_exe)} {quote_arg(str(script_path))} --mode {mode}"

    env = {
        "MYATTENTION_RUNTIME_MODE": mode,
        "PYTHONUTF8": "1",
        "PYTHONUNBUFFERED": "1",
    }
    return command, REPO_ROOT, env


def wait_for_http(url: str, timeout: int) -> bool:
    for _ in range(timeout):
        ok, _ = http_ok(url)
        if ok:
            return True
        time.sleep(1)
    return False


def ensure_env_file(source: Path | None, target: Path, force: bool = False) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() and not force:
        return "exists"

    if source and source.exists():
        shutil.copyfile(source, target)
        return "copied"

    if target.name == ".env.local":
        target.write_text("API_URL=http://localhost:8000\nNEXT_PUBLIC_API_URL=http://localhost:8000\n", encoding="utf-8")
    else:
        target.write_text("", encoding="utf-8")
    return "created"


def create_venv(config: dict[str, Any]) -> str:
    setup_cfg = config.get("setup", {})
    if not setup_cfg.get("create_venv", False):
        return "skipped"

    venv_root = resolve_config_path(setup_cfg.get("venv_path", ".venv"))
    python_in_venv = venv_python_path(config)
    if python_in_venv.exists():
        return "exists"

    bootstrap_python = resolve_bootstrap_python(config)
    result = subprocess.run([bootstrap_python, "-m", "venv", str(venv_root)], cwd=str(REPO_ROOT))
    return "created" if result.returncode == 0 else "failed"


def validate_setup(config: dict[str, Any]) -> tuple[int, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    python_exe = resolve_python(config)
    package_manager = resolve_package_manager(config)
    api_workdir = resolve_config_path(config.get("api", {}).get("workdir", "services/api"))
    web_workdir = resolve_config_path(config.get("web", {}).get("workdir", "services/web"))

    if not command_exists(python_exe):
        errors.append(f"Python executable not found: {python_exe}")

    if not command_exists(package_manager):
        warnings.append(f"Package manager not found on PATH: {package_manager}")

    if not api_workdir.exists():
        errors.append(f"API workdir missing: {api_workdir}")
    if not web_workdir.exists():
        errors.append(f"Web workdir missing: {web_workdir}")

    if not (api_workdir / ".env").exists():
        warnings.append(f"Missing API env file: {api_workdir / '.env'}")
    if not (web_workdir / ".env.local").exists():
        warnings.append(f"Missing web env file: {web_workdir / '.env.local'}")

    return (1 if errors else 0), warnings, errors


def default_setup_command(config: dict[str, Any], component: str) -> str:
    if component == "api":
        python_exe = resolve_python(config)
        api_workdir = resolve_config_path(config.get("api", {}).get("workdir", "services/api"))
        requirements = resolve_config_path(config.get("setup", {}).get("api_requirements", "requirements.txt"), api_workdir)
        return f"{quote_arg(python_exe)} -m pip install -r {quote_arg(str(requirements))}"
    if component == "web":
        return package_manager_command(config, "install")
    raise ValueError(f"Unsupported component: {component}")


def install_dependencies(config: dict[str, Any]) -> int:
    api_cfg = config.get("api", {})
    web_cfg = config.get("web", {})
    api_workdir = resolve_config_path(api_cfg.get("workdir", "services/api"))
    web_workdir = resolve_config_path(web_cfg.get("workdir", "services/web"))

    api_command = str(api_cfg.get("install_command", "")).strip() or default_setup_command(config, "api")
    web_command = str(web_cfg.get("install_command", "")).strip() or default_setup_command(config, "web")

    api_command = format_command(api_command, config, {"python": resolve_python(config)})
    web_command = format_command(web_command, config)

    if run_command(api_command, api_workdir) != 0:
        return 1
    if run_command(web_command, web_workdir) != 0:
        return 1
    return 0


def maybe_run_migrations(config: dict[str, Any]) -> int:
    setup_cfg = config.get("setup", {})
    migrate_command = str(setup_cfg.get("migrate_command", "")).strip()
    if not migrate_command:
        return 0
    api_workdir = resolve_config_path(config.get("api", {}).get("workdir", "services/api"))
    command = format_command(migrate_command, config, {"python": resolve_python(config)})
    return run_command(command, api_workdir)


def run_setup(config: dict[str, Any], install: bool, migrate: bool, force_env: bool) -> int:
    runtime_paths()

    setup_cfg = config.get("setup", {})
    api_env_source = resolve_config_path(setup_cfg.get("api_env_source", "services/api/.env.example"))
    api_env_target = resolve_config_path(setup_cfg.get("api_env_target", "services/api/.env"))
    web_env_source_value = str(setup_cfg.get("web_env_source", "")).strip()
    web_env_source = resolve_config_path(web_env_source_value) if web_env_source_value else None
    web_env_target = resolve_config_path(setup_cfg.get("web_env_target", "services/web/.env.local"))

    venv_result = create_venv(config)
    api_env_result = ensure_env_file(api_env_source if api_env_source.exists() else None, api_env_target, force=force_env)
    web_env_result = ensure_env_file(web_env_source if web_env_source and web_env_source.exists() else None, web_env_target, force=force_env)

    code, warnings, errors = validate_setup(config)

    print("MyAttention setup")
    print("=" * 40)
    print(f"runtime_dir     {RUNTIME_DIR}")
    print(f"venv            {venv_result}")
    print(f"api_env         {api_env_result} {api_env_target}")
    print(f"web_env         {web_env_result} {web_env_target}")

    for warning in warnings:
        print(f"WARNING         {warning}")
    for error in errors:
        print(f"ERROR           {error}")

    if code != 0:
        return code

    if install:
        print("Installing dependencies...")
        if install_dependencies(config) != 0:
            return 1

    if migrate:
        print("Running migrations...")
        if maybe_run_migrations(config) != 0:
            return 1

    print("Setup completed.")
    return 0


def health(config: dict[str, Any]) -> dict[str, dict[str, str]]:
    runtime_cfg = config.get("runtime", {})
    postgres_cfg = config.get("postgres", {})
    redis_cfg = config.get("redis", {})
    qdrant_cfg = config.get("qdrant", {})

    api_port = int(runtime_cfg.get("api_port", 8000))
    web_port = int(runtime_cfg.get("web_port", 3000))
    api_health_path = runtime_cfg.get("api_health_path", "/health")
    web_health_url = runtime_cfg.get("web_health_url", f"http://127.0.0.1:{web_port}")

    results: dict[str, dict[str, str]] = {}
    results["runtime_mode"] = {"status": runtime_cfg.get("mode", DEFAULT_MODE), "detail": ""}

    pg_host = str(postgres_cfg.get("host", "")).strip()
    pg_port = int(postgres_cfg.get("port", 5432))
    pg_service = windows_service_info(config, "postgres")
    if not pg_host:
        results["postgres"] = {"status": "not_configured", "detail": ""}
    else:
        pg_ok = test_tcp(pg_host, pg_port)
        pg_detail = f"{pg_host}:{pg_port}"
        if pg_service["mode"] == "service":
            if pg_service["registered"]:
                pg_detail = f"{pg_detail} service={pg_service['name']} state={pg_service['state'] or 'unknown'}"
            else:
                pg_detail = f"{pg_detail} service={pg_service['name']} unregistered"
        results["postgres"] = {"status": "healthy" if pg_ok else "down", "detail": pg_detail}

    redis_host = str(redis_cfg.get("host", "")).strip()
    redis_port = int(redis_cfg.get("port", 6379))
    redis_service = windows_service_info(config, "redis")
    if not redis_host:
        results["redis"] = {"status": "not_configured", "detail": ""}
    else:
        redis_ok = test_tcp(redis_host, redis_port)
        redis_detail = f"{redis_host}:{redis_port}"
        if redis_service["mode"] == "service":
            if redis_service["registered"]:
                redis_detail = f"{redis_detail} service={redis_service['name']} state={redis_service['state'] or 'unknown'}"
            else:
                redis_detail = f"{redis_detail} service={redis_service['name']} unregistered"
        results["redis"] = {"status": "healthy" if redis_ok else "down", "detail": redis_detail}

    if qdrant_cfg.get("mode", "embedded") == "embedded":
        results["qdrant"] = {"status": "embedded", "detail": "managed by API process"}
    else:
        qdrant_host = str(qdrant_cfg.get("host", "")).strip()
        qdrant_port = int(qdrant_cfg.get("port", 6333))
        if not qdrant_host:
            results["qdrant"] = {"status": "not_configured", "detail": ""}
        else:
            qdrant_ok = test_tcp(qdrant_host, qdrant_port)
            results["qdrant"] = {"status": "healthy" if qdrant_ok else "down", "detail": f"{qdrant_host}:{qdrant_port}"}

    api_service = windows_service_info(config, "api")
    api_residual_service = residual_service_info(config, "api")
    api_ok, api_msg = http_ok(f"http://127.0.0.1:{api_port}{api_health_path}")
    api_status = "healthy" if api_ok else "down"
    api_detail = api_msg
    if api_service["mode"] == "service":
        if api_service["registered"]:
            api_detail = f"{api_msg} service={api_service['name']} state={api_service['state'] or 'unknown'}"
            if api_ok and not api_service["running"]:
                api_status = "degraded"
        else:
            api_detail = f"{api_msg} service={api_service['name']} unregistered"
            if api_ok:
                api_status = "degraded"
    elif api_residual_service:
        api_detail = (
            f"{api_msg} residual_service={api_residual_service['name']} "
            f"state={api_residual_service['state'] or 'unknown'}"
        )
    results["api"] = {"status": api_status, "detail": api_detail}

    if api_ok:
        try:
            evolution_resp = requests.get(f"http://127.0.0.1:{api_port}/api/evolution/status", timeout=3.0)
            if evolution_resp.ok:
                payload = evolution_resp.json()
                evolution_status = payload.get("status", "unknown")
                results["auto_evolution"] = {"status": evolution_status, "detail": "api managed"}
            else:
                results["auto_evolution"] = {"status": "down", "detail": f"HTTP {evolution_resp.status_code}"}
        except Exception as exc:
            results["auto_evolution"] = {"status": "down", "detail": str(exc)}
    else:
        results["auto_evolution"] = {"status": "down", "detail": "api unavailable"}

    web_service = windows_service_info(config, "web")
    web_residual_service = residual_service_info(config, "web")
    web_ok, web_msg = http_ok(web_health_url)
    web_status = "healthy" if web_ok else "down"
    web_detail = web_msg
    if web_service["mode"] == "service":
        if web_service["registered"]:
            web_detail = f"{web_msg} service={web_service['name']} state={web_service['state'] or 'unknown'}"
            if web_ok and not web_service["running"]:
                web_status = "degraded"
        else:
            web_detail = f"{web_msg} service={web_service['name']} unregistered"
            if web_ok:
                web_status = "degraded"
    elif web_residual_service:
        web_detail = (
            f"{web_msg} residual_service={web_residual_service['name']} "
            f"state={web_residual_service['state'] or 'unknown'}"
        )
    results["web"] = {"status": web_status, "detail": web_detail}

    watchdog_service = windows_service_info(config, "watchdog")
    watchdog_residual_service = residual_service_info(config, "watchdog")
    watchdog_pid = read_pid("watchdog")
    watchdog_running = watchdog_service["running"] if watchdog_service["mode"] == "service" else is_pid_running(watchdog_pid)
    watchdog_detail = str(component_log_path_for(config, "watchdog"))
    if watchdog_service["mode"] == "service":
        if watchdog_service["registered"]:
            watchdog_detail = f"{watchdog_detail} service={watchdog_service['name']} state={watchdog_service['state'] or 'unknown'}"
        else:
            watchdog_detail = f"{watchdog_detail} service={watchdog_service['name']} unregistered"
    elif watchdog_residual_service:
        watchdog_detail = (
            f"{watchdog_detail} residual_service={watchdog_residual_service['name']} "
            f"state={watchdog_residual_service['state'] or 'unknown'}"
        )
    watchdog_status = "running" if watchdog_running else "down"
    if watchdog_service["mode"] == "service" and watchdog_service["registered"] and not watchdog_service["running"]:
        watchdog_status = "degraded" if read_pid("watchdog") or watchdog_running else "down"
    results["watchdog"] = {
        "status": watchdog_status,
        "detail": watchdog_detail,
    }

    component_states = [value["status"] for key, value in results.items() if key != "runtime_mode"]
    overall = "healthy"
    if any(state in {"down", "degraded"} for state in component_states):
        overall = "degraded"
    if all(state in {"healthy", "embedded"} for state in component_states):
        overall = "healthy"
    results["overall"] = {"status": overall, "detail": ""}
    return results


def print_health(results: dict[str, dict[str, str]], as_json: bool) -> None:
    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print("MyAttention health")
    print("=" * 40)
    for name, data in results.items():
        label = name.ljust(14)
        print(f"{label} {data['status']} {data['detail']}".rstrip())


def status(config: dict[str, Any]) -> dict[str, Any]:
    health_results = health(config)
    api_info = component_runtime_info(config, "api")
    web_info = component_runtime_info(config, "web")
    watchdog_info = component_runtime_info(config, "watchdog")
    postgres_service = windows_service_info(config, "postgres")
    redis_service = windows_service_info(config, "redis")
    results = {
        "pids": {
            "api": {
                "pid": api_info["pid"],
                "running": api_info["running"] if api_info["mode"] == "service" else (api_info["running"] or health_results["api"]["status"] == "healthy"),
                "mode": api_info["mode"],
                "meta": api_info["meta"],
            },
            "web": {
                "pid": web_info["pid"],
                "running": web_info["running"] if web_info["mode"] == "service" else (web_info["running"] or health_results["web"]["status"] == "healthy"),
                "mode": web_info["mode"],
                "meta": web_info["meta"],
            },
            "watchdog": {
                "pid": watchdog_info["pid"],
                "running": watchdog_info["running"],
                "mode": watchdog_info["mode"],
                "meta": watchdog_info["meta"],
            },
        },
        "infra": {
            "postgres": postgres_service,
            "redis": redis_service,
            "qdrant": {
                "mode": config.get("qdrant", {}).get("mode", "embedded"),
                "registered": False,
                "running": health_results["qdrant"]["status"] in {"healthy", "embedded"},
                "pid": None,
                "state": health_results["qdrant"]["status"],
                "log_path": "",
            },
        },
        "health": health_results,
    }
    return results


def print_status(results: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print("MyAttention status")
    print("=" * 40)
    for component, info in results["pids"].items():
        mode = info.get("mode", "process")
        log_path = ""
        if info.get("meta"):
            log_path = info["meta"].get("log_path", "")
        extra = ""
        if mode == "service":
            extra = f"service={info['meta'].get('service_name')} state={info['meta'].get('state')}"
        elif info.get("meta", {}).get("residual_service"):
            residual = info["meta"]["residual_service"]
            extra = f"residual_service={residual.get('service_name')} state={residual.get('state')}"
        print(f"{component.ljust(14)} mode={mode} pid={info['pid']} running={info['running']} {extra} {log_path}".rstrip())
    for component, info in results.get("infra", {}).items():
        mode = info.get("mode", "unknown")
        pid = info.get("pid")
        running = info.get("running")
        extra = ""
        if mode == "service":
            extra = f"name={info.get('name')} state={info.get('state')}"
        elif mode == "embedded":
            extra = f"state={info.get('state')}"
        log_path = info.get("log_path", "")
        print(f"{component.ljust(14)} mode={mode} pid={pid} running={running} {extra} {log_path}".rstrip())
    print_health(results["health"], as_json=False)


def start_infra(config: dict[str, Any], targets: list[str] | None = None) -> int:
    names = targets or ["postgres", "redis", "qdrant"]
    for name in names:
        service_cfg = config.get(name, {})
        if name == "qdrant" and service_cfg.get("mode", "embedded") == "embedded":
            print("Qdrant running in embedded mode; no external startup required.")
            continue

        host = str(service_cfg.get("host", "")).strip()
        port = int(service_cfg.get("port", 0))
        if host and port and test_tcp(host, port):
            print(f"{name} already reachable on {host}:{port}")
            continue

        if service_enabled(config, name):
            if not service_exists(config, name):
                print(f"{name} service is configured but not registered: {service_name(config, name)}")
                continue
            start_windows_service(config, name)
            continue

        start_command, _stop_command, workdir, env = build_service_commands(config, name)
        if not start_command:
            print(f"{name} is not running and no start_command is configured.")
            continue

        start_component(name, start_command, workdir, env)
        print(f"Start requested for {name}")
    return 0


def stop_infra(config: dict[str, Any], target: str | None = None) -> int:
    names = [target] if target else ["redis", "postgres", "qdrant"]
    for name in names:
        if not name:
            continue
        service_cfg = config.get(name, {})
        if name == "qdrant" and service_cfg.get("mode", "embedded") == "embedded":
            continue

        if service_enabled(config, name):
            if not service_exists(config, name):
                print(f"{name} service is configured but not registered: {service_name(config, name)}")
                continue
            stop_windows_service(config, name)
            clear_pid(name)
            clear_meta(name)
            continue

        _start_command, stop_command, workdir, env = build_service_commands(config, name)
        pid = read_pid(name)
        if stop_command:
            log_path = component_log_path(name)
            with log_path.open("a", encoding="utf-8") as fh:
                fh.write(f"\n[{datetime.now(timezone.utc).isoformat()}] STOP {name}\n")
                fh.write(f"command={stop_command}\n")
            run_command(stop_command, workdir, env)
        elif is_pid_running(pid):
            stop_component(name)
            continue
        else:
            print(f"{name} not running and no stop_command is configured.")
            clear_pid(name)
            clear_meta(name)
            continue

        time.sleep(1)
        clear_pid(name)
        clear_meta(name)
        print(f"Stop requested for {name}")
    return 0


def print_logs(config: dict[str, Any], component: str, tail: int) -> int:
    path = service_log_path(config, component) or component_log_path(component)
    if not path.exists():
        print(f"No log file for {component}: {path}")
        return 1

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines[-tail:]:
        sys.stdout.buffer.write((line + "\n").encode("utf-8", errors="replace"))
    return 0


def start_api(config: dict[str, Any]) -> int:
    runtime_cfg = config.get("runtime", {})
    api_port = int(runtime_cfg.get("api_port", 8000))
    api_health_path = runtime_cfg.get("api_health_path", "/health")
    timeout = int(runtime_cfg.get("start_timeout", DEFAULT_TIMEOUT))
    if service_enabled(config, "api"):
        api_service = windows_service_info(config, "api")
        if api_service["running"] and http_ok(f"http://127.0.0.1:{api_port}{api_health_path}")[0]:
            print(f"API already healthy on http://127.0.0.1:{api_port}{api_health_path}")
            return 0
        if not service_exists(config, "api"):
            print(f"api service is configured but not registered: {service_name(config, 'api')}")
            return 1
        start_windows_service(config, "api")
        if wait_for_http(f"http://127.0.0.1:{api_port}{api_health_path}", timeout):
            print(f"API healthy on http://127.0.0.1:{api_port}{api_health_path}")
            return 0
        print("API service start requested, but health check did not pass within timeout.")
        return 1

    if http_ok(f"http://127.0.0.1:{api_port}{api_health_path}")[0]:
        print(f"API already healthy on http://127.0.0.1:{api_port}{api_health_path}")
        return 0

    command, workdir, env = build_api_command(config)
    start_component("api", command, workdir, env)
    if wait_for_http(f"http://127.0.0.1:{api_port}{api_health_path}", timeout):
        print(f"API healthy on http://127.0.0.1:{api_port}{api_health_path}")
        return 0
    print("API start requested, but health check did not pass within timeout.")
    return 1


def start_web(config: dict[str, Any]) -> int:
    runtime_cfg = config.get("runtime", {})
    timeout = int(runtime_cfg.get("start_timeout", DEFAULT_TIMEOUT))
    web_url = runtime_cfg.get("web_health_url", f"http://127.0.0.1:{int(runtime_cfg.get('web_port', 3000))}")
    if not service_enabled(config, "web"):
        stop_residual_windows_service(config, "web")

    if http_ok(web_url)[0]:
        print(f"Web already healthy on {web_url}")
        return 0

    if service_enabled(config, "web"):
        if not service_exists(config, "web"):
            print(f"web service is configured but not registered: {service_name(config, 'web')}")
            return 1
        sync_web_standalone_assets(config)
        start_windows_service(config, "web")
        if wait_for_http(web_url, timeout):
            print(f"Web healthy on {web_url}")
            return 0
        print("Web service start requested, but health check did not pass within timeout.")
        return 1

    command, workdir, env = build_web_command(config)
    sync_web_standalone_assets(config)
    start_component("web", command, workdir, env)
    if wait_for_http(web_url, timeout):
        print(f"Web healthy on {web_url}")
        return 0
    print("Web start requested, but health check did not pass within timeout.")
    return 1


def start_watchdog(config: dict[str, Any], mode: str) -> int:
    if service_enabled(config, "watchdog"):
        if not service_exists(config, "watchdog"):
            print(f"watchdog service is configured but not registered: {service_name(config, 'watchdog')}")
            return 1
        start_windows_service(config, "watchdog")
        print("Watchdog service start requested")
        return 0

    pid = read_pid("watchdog")
    if is_pid_running(pid):
        print(f"Watchdog already running (pid={pid})")
        return 0

    command, workdir, env = build_watchdog_command(config, mode)
    start_component("watchdog", command, workdir, env)
    time.sleep(1)
    watchdog_pid = read_pid("watchdog")
    if is_pid_running(watchdog_pid):
        print("Watchdog running")
        return 0
    print("Watchdog start requested, but process is not running.")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MyAttention cross-platform launcher")
    parser.add_argument("--mode", default=os.environ.get("MYATTENTION_RUNTIME_MODE", DEFAULT_MODE))

    subparsers = parser.add_subparsers(dest="command")

    setup_parser = subparsers.add_parser("setup", help="Bootstrap local development environment")
    setup_parser.add_argument("--install", action="store_true", help="Install API and web dependencies")
    setup_parser.add_argument("--migrate", action="store_true", help="Run configured migration command after setup")
    setup_parser.add_argument("--force-env", action="store_true", help="Overwrite existing env files from template")

    start_parser = subparsers.add_parser("start", help="Start services")
    start_parser.add_argument("target", choices=["api", "web", "infra", "postgres", "redis", "watchdog", "dev"])

    stop_parser = subparsers.add_parser("stop", help="Stop services")
    stop_parser.add_argument("target", choices=["api", "web", "infra", "postgres", "redis", "watchdog", "dev"])

    status_parser = subparsers.add_parser("status", help="Show runtime status")
    status_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")

    health_parser = subparsers.add_parser("health", help="Show runtime health")
    health_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")

    logs_parser = subparsers.add_parser("logs", help="Show component launcher logs")
    logs_parser.add_argument("target", choices=["api", "web", "postgres", "redis", "qdrant", "watchdog"])
    logs_parser.add_argument("--tail", type=int, default=80, help="Number of lines to print")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = load_runtime_config(args.mode)

    if not args.command:
        print_status(status(config), as_json=False)
        return 0

    if args.command == "setup":
        return run_setup(config, install=args.install, migrate=args.migrate, force_env=args.force_env)

    if args.command == "health":
        print_health(health(config), as_json=args.json)
        return 0

    if args.command == "status":
        print_status(status(config), as_json=args.json)
        return 0

    if args.command == "logs":
        return print_logs(config, args.target, args.tail)

    if args.command == "start":
        if args.target == "infra":
            return start_infra(config)
        if args.target in {"postgres", "redis"}:
            return start_infra(config, [args.target])
        if args.target == "api":
            return start_api(config)
        if args.target == "web":
            return start_web(config)
        if args.target == "watchdog":
            return start_watchdog(config, args.mode)
        if args.target == "dev":
            runtime_cfg = config.get("runtime", {})
            if runtime_cfg.get("start_infra_with_dev", False):
                start_infra(config)
            api_result = start_api(config)
            web_result = start_web(config)
            watchdog_cfg = config.get("watchdog", {})
            watchdog_result = 0
            if watchdog_cfg.get("auto_start", True):
                watchdog_result = start_watchdog(config, args.mode)
            return 0 if api_result == 0 and web_result == 0 and watchdog_result == 0 else 1

    if args.command == "stop":
        if args.target == "api":
            if service_enabled(config, "api"):
                return stop_windows_service(config, "api")
            stop_component("api")
            return 0
        if args.target == "web":
            if service_enabled(config, "web"):
                return stop_windows_service(config, "web")
            stop_component("web")
            return 0
        if args.target == "infra":
            return stop_infra(config)
        if args.target in {"postgres", "redis"}:
            return stop_infra(config, args.target)
        if args.target == "watchdog":
            if service_enabled(config, "watchdog"):
                return stop_windows_service(config, "watchdog")
            stop_component("watchdog")
            return 0
        if args.target == "dev":
            if service_enabled(config, "watchdog"):
                stop_windows_service(config, "watchdog")
            else:
                stop_component("watchdog")
            if service_enabled(config, "web"):
                stop_windows_service(config, "web")
            else:
                stop_component("web")
            if service_enabled(config, "api"):
                stop_windows_service(config, "api")
            else:
                stop_component("api")
            return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
