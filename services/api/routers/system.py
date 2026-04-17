"""
System health router.

Provides narrow operational visibility for:
- local containers
- local databases
- API health
- external LLM reachability
"""

import asyncio
import socket
import subprocess
from datetime import datetime
from typing import Any, Dict, List
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from config import create_qdrant_client, get_effective_qwen_base_url, get_settings, is_local_qdrant_mode
from db.session import async_session_maker

router = APIRouter(prefix="/system", tags=["system-status"])

# Canonical container identities with legacy aliases kept for compatibility.
DOCKER_CONTAINERS = [
    {
        "key": "ike-postgres",
        "display_name": "IKE PostgreSQL",
        "aliases": ["ike-postgres", "myattention-postgres"],
    },
    {
        "key": "ike-redis",
        "display_name": "IKE Redis",
        "aliases": ["ike-redis", "myattention-redis"],
    },
    {
        "key": "ike-qdrant",
        "display_name": "IKE Qdrant",
        "aliases": ["ike-qdrant", "myattention-qdrant"],
    },
]

EXTERNAL_SERVICES = [
    {"name": "qwen", "url": "https://dashscope.aliyuncs.com/api/v1/services", "timeout": 5},
]


def _inspect_container_state(container_name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "inspect", "--format", "{{.State.Status}}", container_name],
        capture_output=True,
        text=True,
        timeout=5,
    )


def _resolve_container_alias(container_aliases: List[str]) -> str | None:
    for alias in container_aliases:
        result = _inspect_container_state(alias)
        if result.returncode == 0:
            return alias
    return None


async def check_docker_container(container_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Check one Docker container using canonical name plus legacy aliases."""
    display_name = container_spec["display_name"]
    container_name = _resolve_container_alias(container_spec["aliases"])
    try:
        if not container_name:
            return {
                "name": display_name,
                "container_key": container_spec["key"],
                "container_name": None,
                "status": "not_found",
                "health": None,
                "running": False,
            }

        result = _inspect_container_state(container_name)
        if result.returncode == 0:
            status = result.stdout.strip()
            inspect_result = subprocess.run(
                ["docker", "inspect", "--format", "{{.State.Health.Status}}", container_name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            health = inspect_result.stdout.strip() if inspect_result.returncode == 0 else None

            return {
                "name": display_name,
                "container_key": container_spec["key"],
                "container_name": container_name,
                "status": "running" if status == "running" else "stopped",
                "health": health if health and health != "" else "unknown",
                "running": status == "running",
            }

        return {
            "name": display_name,
            "container_key": container_spec["key"],
            "container_name": container_name,
            "status": "not_found",
            "health": None,
            "running": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "name": display_name,
            "container_key": container_spec["key"],
            "container_name": container_name,
            "status": "timeout",
            "health": None,
            "running": False,
        }
    except Exception as e:
        return {
            "name": display_name,
            "container_key": container_spec["key"],
            "container_name": container_name,
            "status": "error",
            "error": str(e),
            "running": False,
        }


async def check_database_postgres() -> Dict[str, Any]:
    """Check PostgreSQL connectivity."""
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        return {
            "name": "PostgreSQL",
            "type": "local",
            "status": "healthy",
            "running": True,
            "details": "local process connection ok",
        }
    except Exception as e:
        return {
            "name": "PostgreSQL",
            "type": "local",
            "status": "error",
            "running": False,
            "error": str(e),
        }


async def check_database_redis() -> Dict[str, Any]:
    """Check Redis connectivity."""
    try:
        settings = get_settings()
        redis = urlparse(settings.redis_url)
        redis_host = redis.hostname or "localhost"
        redis_port = redis.port or 6379
        with socket.create_connection((redis_host, redis_port), timeout=2):
            pass
        return {
            "name": "Redis",
            "type": "local",
            "status": "healthy",
            "running": True,
            "details": f"tcp://{redis_host}:{redis_port}",
        }
    except Exception as e:
        return {
            "name": "Redis",
            "type": "local",
            "status": "unhealthy",
            "running": False,
            "error": str(e),
        }


async def check_database_qdrant() -> Dict[str, Any]:
    """Check Qdrant connectivity."""
    settings = get_settings()
    try:
        if is_local_qdrant_mode(settings):
            client = create_qdrant_client(settings)
            client.get_collections()
            return {
                "name": "Qdrant",
                "type": "embedded",
                "status": "healthy",
                "running": True,
                "details": settings.qdrant_local_path,
            }
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.qdrant_url}/readyz")
            running = response.status_code == 200

        return {
            "name": "Qdrant",
            "type": "service",
            "status": "healthy" if running else "unhealthy",
            "running": running,
            "details": response.text if response.text else "",
        }
    except Exception as e:
        return {
            "name": "Qdrant",
            "type": "embedded" if is_local_qdrant_mode(settings) else "service",
            "status": "error",
            "running": False,
            "error": str(e),
        }


async def check_api_service() -> Dict[str, Any]:
    """Check the API service itself."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/health")
            data = response.json()
            return {
                "name": "IKE API",
                "type": "service",
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "running": True,
                "details": data,
            }
    except Exception as e:
        return {
            "name": "IKE API",
            "type": "service",
            "status": "error",
            "running": False,
            "error": str(e),
        }


async def check_llm_service() -> Dict[str, Any]:
    """Check external Qwen model service reachability."""
    settings = get_settings()
    api_key = (settings.qwen_api_key or "").strip()
    base_url = get_effective_qwen_base_url(settings)
    if not api_key:
        return {
            "name": "Tongyi Qwen (LLM)",
            "type": "external",
            "status": "not_configured",
            "running": False,
            "detail": "QWEN_API_KEY is not configured",
        }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{base_url}/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            running = response.status_code == 200
            if response.status_code == 401:
                return {
                    "name": "Tongyi Qwen (LLM)",
                    "type": "external",
                    "status": "unhealthy",
                    "running": False,
                    "detail": f"QWEN_API_KEY authentication failed at {base_url}",
                }
            return {
                "name": "Tongyi Qwen (LLM)",
                "type": "external",
                "status": "healthy" if running else "unhealthy",
                "running": running,
                "detail": f"{base_url} -> HTTP {response.status_code}",
            }
    except Exception as e:
        return {
            "name": "Tongyi Qwen (LLM)",
            "type": "external",
            "status": "error",
            "running": False,
            "error": str(e),
        }


@router.get("/health")
async def get_system_health():
    """Return full system health status."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "containers": [],
        "databases": [],
        "services": [],
        "external": [],
        "summary": {
            "total": 0,
            "healthy": 0,
            "unhealthy": 0,
            "error": 0,
        },
    }

    for container in DOCKER_CONTAINERS:
        container_status = await check_docker_container(container)
        results["containers"].append(container_status)

    results["databases"].append(await check_database_postgres())
    results["databases"].append(await check_database_redis())
    results["databases"].append(await check_database_qdrant())
    results["services"].append(await check_api_service())
    results["external"].append(await check_llm_service())

    all_services = (
        results["containers"]
        + results["databases"]
        + results["services"]
        + results["external"]
    )

    results["summary"]["total"] = len(all_services)
    for service in all_services:
        status = service.get("status", "unknown")
        if status in ["healthy", "running"]:
            results["summary"]["healthy"] += 1
        elif status in ["unhealthy", "not_configured"]:
            results["summary"]["unhealthy"] += 1
        else:
            results["summary"]["error"] += 1

    if results["summary"]["error"] > 0:
        results["overall_status"] = "error"
    elif results["summary"]["unhealthy"] > 0:
        results["overall_status"] = "degraded"
    else:
        results["overall_status"] = "healthy"

    return results


@router.get("/status")
async def get_system_status():
    """Return a simplified system status for polling surfaces."""
    health = await get_system_health()
    return {
        "overall_status": health["overall_status"],
        "summary": health["summary"],
        "services": [
            {"name": s["name"], "status": s["status"], "running": s.get("running", False)}
            for s in health["databases"] + health["services"]
        ],
    }


@router.post("/restart/{container_name}")
async def restart_container(container_name: str):
    """Restart one canonical or legacy-named container."""
    container_spec = next(
        (
            spec
            for spec in DOCKER_CONTAINERS
            if container_name == spec["key"] or container_name in spec["aliases"]
        ),
        None,
    )
    if container_spec is None:
        raise HTTPException(status_code=404, detail=f"Container {container_name} not found")

    resolved_name = _resolve_container_alias(container_spec["aliases"])
    if resolved_name is None:
        raise HTTPException(status_code=404, detail=f"Container {container_name} not found")

    try:
        result = subprocess.run(
            ["docker", "restart", resolved_name],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            return {
                "status": "success",
                "message": f"Container {resolved_name} restarted",
                "requested_name": container_name,
                "resolved_name": resolved_name,
            }

        raise HTTPException(status_code=500, detail=f"Failed to restart: {result.stderr}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
