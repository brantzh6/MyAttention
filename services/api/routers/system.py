"""
System Health Check Router

提供全套服务健康检查，包括：
- Docker 容器状态
- 数据库连接状态
- 外部 API 状态
- 依赖服务状态
"""

import os
import subprocess
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import socket
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from config import create_qdrant_client, get_settings, is_local_qdrant_mode
from db.session import async_session_maker

router = APIRouter(prefix="/system", tags=["系统状态"])

# Docker 容器名称
DOCKER_CONTAINERS = [
    "myattention-postgres",
    "myattention-redis",
    "myattention-qdrant",
]

# 外部服务健康检查
EXTERNAL_SERVICES = [
    {"name": "qwen", "url": "https://dashscope.aliyuncs.com/api/v1/services", "timeout": 5},
]


async def check_docker_container(container_name: str) -> Dict[str, Any]:
    """检查单个 Docker 容器状态"""
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Status}}", container_name],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            status = result.stdout.strip()
            # 获取更多信息
            inspect_result = subprocess.run(
                ["docker", "inspect", "--format", "{{.State.Health.Status}}", container_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            health = inspect_result.stdout.strip() if inspect_result.returncode == 0 else None

            return {
                "name": container_name,
                "status": "running" if status == "running" else "stopped",
                "health": health if health and health != "" else "unknown",
                "running": status == "running"
            }
        else:
            return {
                "name": container_name,
                "status": "not_found",
                "health": None,
                "running": False
            }
    except subprocess.TimeoutExpired:
        return {
            "name": container_name,
            "status": "timeout",
            "health": None,
            "running": False
        }
    except Exception as e:
        return {
            "name": container_name,
            "status": "error",
            "error": str(e),
            "running": False
        }


async def check_database_postgres() -> Dict[str, Any]:
    """检查 PostgreSQL 连接"""
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        return {
            "name": "PostgreSQL",
            "type": "local",
            "status": "healthy",
            "running": True,
            "details": "local process connection ok"
        }
    except Exception as e:
        return {
            "name": "PostgreSQL",
            "type": "local",
            "status": "error",
            "running": False,
            "error": str(e)
        }


async def check_database_redis() -> Dict[str, Any]:
    """检查 Redis 连接"""
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
            "details": f"tcp://{redis_host}:{redis_port}"
        }
    except Exception as e:
        return {
            "name": "Redis",
            "type": "local",
            "status": "unhealthy",
            "running": False,
            "error": str(e)
        }


async def check_database_qdrant() -> Dict[str, Any]:
    """检查 Qdrant 连接"""
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
                "details": settings.qdrant_local_path
            }
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.qdrant_url}/readyz")
            running = response.status_code == 200

        return {
            "name": "Qdrant",
            "type": "service",
            "status": "healthy" if running else "unhealthy",
            "running": running,
            "details": response.text if response.text else ""
        }
    except Exception as e:
        return {
            "name": "Qdrant",
            "type": "embedded" if is_local_qdrant_mode(settings) else "service",
            "status": "error",
            "running": False,
            "error": str(e)
        }


async def check_api_service() -> Dict[str, Any]:
    """检查 API 服务自身状态"""
    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/health")
            data = response.json()
            return {
                "name": "MyAttention API",
                "type": "service",
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "running": True,
                "details": data
            }
    except Exception as e:
        return {
            "name": "MyAttention API",
            "type": "service",
            "status": "error",
            "running": False,
            "error": str(e)
        }


async def check_llm_service() -> Dict[str, Any]:
    """检查 LLM 服务 (通义千问)"""
    settings = get_settings()
    if not settings.qwen_api_key:
        return {
            "name": "通义千问 (LLM)",
            "type": "external",
            "status": "not_configured",
            "running": False
        }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://dashscope.aliyuncs.com/api/v1/services",
                headers={"Authorization": f"Bearer {settings.qwen_api_key}"}
            )
            running = response.status_code in [200, 401]  # 401 means valid key but wrong endpoint
            return {
                "name": "通义千问 (LLM)",
                "type": "external",
                "status": "healthy" if running else "unhealthy",
                "running": running
            }
    except Exception as e:
        return {
            "name": "通义千问 (LLM)",
            "type": "external",
            "status": "error",
            "running": False,
            "error": str(e)
        }


@router.get("/health")
async def get_system_health():
    """
    获取系统完整健康状态

    返回所有依赖服务的健康检查结果：
    - Docker 容器状态
    - 数据库连接状态
    - 外部 API 状态
    """
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
            "error": 0
        }
    }

    # 1. 检查 Docker 容器
    for container in DOCKER_CONTAINERS:
        container_status = await check_docker_container(container)
        results["containers"].append(container_status)

    # 2. 检查数据库服务
    results["databases"].append(await check_database_postgres())
    results["databases"].append(await check_database_redis())
    results["databases"].append(await check_database_qdrant())

    # 3. 检查 API 服务
    results["services"].append(await check_api_service())

    # 4. 检查外部服务
    results["external"].append(await check_llm_service())

    # 5. 汇总统计
    all_services = (
        results["containers"] +
        results["databases"] +
        results["services"] +
        results["external"]
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

    # 设置总体状态
    if results["summary"]["error"] > 0:
        results["overall_status"] = "error"
    elif results["summary"]["unhealthy"] > 0:
        results["overall_status"] = "degraded"
    else:
        results["overall_status"] = "healthy"

    return results


@router.get("/status")
async def get_system_status():
    """获取简化的系统状态（供前端轮询使用）"""
    health = await get_system_health()

    return {
        "overall_status": health["overall_status"],
        "summary": health["summary"],
        "services": [
            {"name": s["name"], "status": s["status"], "running": s.get("running", False)}
            for s in health["databases"] + health["services"]
        ]
    }


@router.post("/restart/{container_name}")
async def restart_container(container_name: str):
    """重启指定容器"""
    if container_name not in DOCKER_CONTAINERS:
        raise HTTPException(status_code=404, detail=f"Container {container_name} not found")

    try:
        result = subprocess.run(
            ["docker", "restart", container_name],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return {"status": "success", "message": f"Container {container_name} restarted"}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to restart: {result.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
