#!/usr/bin/env python3
"""
MyAttention local runtime watchdog.

Monitors local-process components and performs bounded restart attempts.
"""

from __future__ import annotations

import argparse
import json
import signal
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from manage import (
    DEFAULT_MODE,
    RUNTIME_DIR,
    health,
    load_runtime_config,
    start_api,
    start_infra,
    start_web,
    stop_component,
)


class RuntimeWatchdog:
    def __init__(self, mode: str):
        self.mode = mode
        self.config = load_runtime_config(mode)
        watchdog_cfg = self.config.get("watchdog", {})
        self.interval_seconds = int(watchdog_cfg.get("interval_seconds", 20))
        self.restart_cooldown_seconds = int(watchdog_cfg.get("restart_cooldown_seconds", 45))
        self.auto_evolution_grace_cycles = int(watchdog_cfg.get("auto_evolution_grace_cycles", 2))
        self.manage_infra = bool(watchdog_cfg.get("manage_infra", False))
        self.manage_api = bool(watchdog_cfg.get("manage_api", True))
        self.manage_web = bool(watchdog_cfg.get("manage_web", True))
        self.manage_auto_evolution = bool(watchdog_cfg.get("manage_auto_evolution", True))
        self.state_path = RUNTIME_DIR / "watchdog-state.json"
        self.running = True
        self.last_restart_at: dict[str, float] = {}
        self.auto_evolution_failures = 0

    def log(self, message: str, **extra: Any) -> None:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": message,
        }
        if extra:
            payload["extra"] = extra
        print(json.dumps(payload, ensure_ascii=False))

    def can_restart(self, component: str) -> bool:
        last = self.last_restart_at.get(component, 0.0)
        return (time.time() - last) >= self.restart_cooldown_seconds

    def mark_restart(self, component: str) -> None:
        self.last_restart_at[component] = time.time()

    def persist_state(self, snapshot: dict[str, Any]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    def handle_signal(self, *_args: Any) -> None:
        self.running = False

    def restart_api(self, reason: str) -> None:
        if not self.can_restart("api"):
            self.log("api restart skipped due to cooldown", reason=reason)
            return
        self.mark_restart("api")
        self.log("restarting api", reason=reason)
        stop_component("api")
        time.sleep(2)
        start_api(self.config)

    def run_once(self) -> None:
        snapshot = health(self.config)
        self.persist_state(snapshot)

        if self.manage_infra and (snapshot["postgres"]["status"] == "down" or snapshot["redis"]["status"] == "down"):
            if self.can_restart("infra"):
                self.mark_restart("infra")
                self.log("infra unhealthy, triggering start_infra", health=snapshot)
                start_infra(self.config)

        if self.manage_api and snapshot["api"]["status"] == "down":
            if self.can_restart("api"):
                self.mark_restart("api")
                self.log("api unhealthy, triggering start_api")
                start_api(self.config)

        if self.manage_web and snapshot["web"]["status"] == "down":
            if self.can_restart("web"):
                self.mark_restart("web")
                self.log("web unhealthy, triggering start_web")
                start_web(self.config)

        if self.manage_auto_evolution and snapshot.get("auto_evolution", {}).get("status") != "running":
            if snapshot["api"]["status"] == "healthy":
                self.auto_evolution_failures += 1
                self.log(
                    "auto_evolution unhealthy",
                    consecutive_failures=self.auto_evolution_failures,
                )
                if self.auto_evolution_failures >= self.auto_evolution_grace_cycles:
                    self.restart_api("auto_evolution down")
                    self.auto_evolution_failures = 0
            else:
                self.auto_evolution_failures = 0
        else:
            self.auto_evolution_failures = 0

    def run(self) -> int:
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)
        self.log("watchdog started", mode=self.mode)
        while self.running:
            try:
                self.run_once()
            except Exception as exc:
                self.log("watchdog iteration failed", error=str(exc))
            time.sleep(self.interval_seconds)
        self.log("watchdog stopped", mode=self.mode)
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="MyAttention runtime watchdog")
    parser.add_argument("--mode", default=DEFAULT_MODE)
    args = parser.parse_args()
    watchdog = RuntimeWatchdog(args.mode)
    return watchdog.run()


if __name__ == "__main__":
    raise SystemExit(main())
