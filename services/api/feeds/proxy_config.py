import asyncio
import json
import os
import socket
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import aiohttp

try:
    import aiohttp_socks

    SOCKS_SUPPORT = True
except ImportError:
    aiohttp_socks = None
    SOCKS_SUPPORT = False


DEFAULT_HTTP_PROXY = "http://127.0.0.1:10808"
DEFAULT_SOCKS_PROXY = "socks5://127.0.0.1:10808"
DEFAULT_TEST_URL = "https://httpbin.org/ip"
VALID_PROXY_MODES = {"auto", "always", "never"}

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_PROXY_SETTINGS_PATH = _DATA_DIR / "proxy_settings.json"


def _default_proxy_settings() -> dict[str, Any]:
    return {
        "enabled": False,
        "http_proxy": os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy") or DEFAULT_HTTP_PROXY,
        "socks_proxy": os.environ.get("SOCKS_PROXY") or os.environ.get("socks_proxy") or DEFAULT_SOCKS_PROXY,
        "auto_detect_domains": True,
        "test_url": DEFAULT_TEST_URL,
        "updated_at": datetime.now().isoformat(),
    }


def normalize_proxy_mode(proxy_mode: str | None, use_proxy: bool = False) -> str:
    mode = (proxy_mode or "").strip().lower()
    if mode in VALID_PROXY_MODES:
        return mode
    return "always" if use_proxy else "auto"


def normalize_proxy_settings(data: dict[str, Any] | None) -> dict[str, Any]:
    settings = _default_proxy_settings()
    if isinstance(data, dict):
        settings.update(data)

    settings["enabled"] = bool(settings.get("enabled", False))
    settings["auto_detect_domains"] = bool(settings.get("auto_detect_domains", True))
    settings["http_proxy"] = str(settings.get("http_proxy") or "").strip()
    settings["socks_proxy"] = str(settings.get("socks_proxy") or "").strip()
    settings["test_url"] = str(settings.get("test_url") or DEFAULT_TEST_URL).strip() or DEFAULT_TEST_URL
    settings["updated_at"] = str(settings.get("updated_at") or datetime.now().isoformat())
    return settings


def load_proxy_settings() -> dict[str, Any]:
    if not _PROXY_SETTINGS_PATH.exists():
        return _default_proxy_settings()

    try:
        raw = json.loads(_PROXY_SETTINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return _default_proxy_settings()
    return normalize_proxy_settings(raw)


def save_proxy_settings(data: dict[str, Any]) -> dict[str, Any]:
    settings = normalize_proxy_settings(data)
    settings["updated_at"] = datetime.now().isoformat()

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    _PROXY_SETTINGS_PATH.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return settings


def should_use_proxy(url: str, proxy_mode: str, proxy_settings: dict[str, Any], proxy_domains: list[str]) -> tuple[bool, str]:
    if not proxy_settings.get("enabled"):
        return False, "global_disabled"

    mode = normalize_proxy_mode(proxy_mode)
    if mode == "never":
        return False, "source_never"
    if mode == "always":
        return True, "source_forced"

    if not proxy_settings.get("auto_detect_domains", True):
        return False, "auto_detection_disabled"

    url_lower = (url or "").lower()
    for domain in proxy_domains:
        if domain in url_lower:
            return True, f"domain:{domain}"
    return False, "direct"


async def _can_connect(proxy_url: str) -> tuple[bool, str | None]:
    parsed = urlparse(proxy_url)
    host = parsed.hostname
    port = parsed.port
    if not host or not port:
        return False, "Invalid proxy URL"

    def _connect() -> None:
        with socket.create_connection((host, port), timeout=2):
            return None

    try:
        await asyncio.to_thread(_connect)
        return True, None
    except Exception as exc:
        return False, str(exc)


async def _test_http_proxy(proxy_url: str, test_url: str) -> tuple[bool, str | None]:
    try:
        timeout = aiohttp.ClientTimeout(total=6, connect=3)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(test_url, proxy=proxy_url, ssl=False) as response:
                if response.status < 400:
                    return True, None
                return False, f"HTTP {response.status}"
    except Exception as exc:
        return False, str(exc)


async def _test_socks_proxy(proxy_url: str, test_url: str) -> tuple[bool, str | None]:
    if not SOCKS_SUPPORT or aiohttp_socks is None:
        return False, "aiohttp_socks not installed"

    try:
        connector = aiohttp_socks.ProxyConnector.from_url(proxy_url)
        timeout = aiohttp.ClientTimeout(total=6, connect=3)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(test_url, ssl=False) as response:
                if response.status < 400:
                    return True, None
                return False, f"HTTP {response.status}"
    except Exception as exc:
        return False, str(exc)


async def get_proxy_status(proxy_settings: dict[str, Any] | None = None) -> dict[str, Any]:
    settings = normalize_proxy_settings(proxy_settings or load_proxy_settings())
    test_url = settings["test_url"]

    status: dict[str, Any] = {
        "state": "disabled",
        "message": "Proxy is disabled",
        "checked_at": datetime.now().isoformat(),
        "http": {
            "configured": bool(settings["http_proxy"]),
            "reachable": False,
            "working": False,
            "error": None,
        },
        "socks": {
            "configured": bool(settings["socks_proxy"]),
            "reachable": False,
            "working": False,
            "supported": SOCKS_SUPPORT,
            "error": None,
        },
    }

    if not settings["enabled"]:
        return status

    results: list[bool] = []

    if settings["http_proxy"]:
        reachable, error = await _can_connect(settings["http_proxy"])
        status["http"]["reachable"] = reachable
        status["http"]["error"] = error
        if reachable:
            working, error = await _test_http_proxy(settings["http_proxy"], test_url)
            status["http"]["working"] = working
            status["http"]["error"] = error
            results.append(working)
        else:
            results.append(False)

    if settings["socks_proxy"]:
        reachable, error = await _can_connect(settings["socks_proxy"])
        status["socks"]["reachable"] = reachable
        status["socks"]["error"] = error
        if reachable and SOCKS_SUPPORT:
            working, error = await _test_socks_proxy(settings["socks_proxy"], test_url)
            status["socks"]["working"] = working
            status["socks"]["error"] = error
            results.append(working)
        elif reachable and not SOCKS_SUPPORT:
            results.append(False)
        else:
            results.append(False)

    if not settings["http_proxy"] and not settings["socks_proxy"]:
        status["state"] = "error"
        status["message"] = "Proxy is enabled but no proxy URL is configured"
        return status

    if any(results):
        failed = [not item for item in results]
        status["state"] = "degraded" if any(failed) else "healthy"
        status["message"] = "Proxy is working" if status["state"] == "healthy" else "At least one proxy path is unavailable"
        return status

    status["state"] = "error"
    status["message"] = "Proxy is enabled but unavailable"
    return status
