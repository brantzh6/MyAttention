from typing import Optional, Dict, Any, List
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from db.models import Task, TaskHistory, TaskStatus

router = APIRouter(tags=["ai-testing"])
logger = logging.getLogger(__name__)

TESTING_SOURCE_TYPES = ("api_test", "ui_test", "log_analysis", "system_health")
OPEN_ISSUE_STATUSES = (
    TaskStatus.PENDING.value,
    TaskStatus.CONFIRMED.value,
    TaskStatus.EXECUTING.value,
    TaskStatus.FAILED.value,
)


class RunTestRequest(BaseModel):
    """运行测试请求"""
    test_types: Optional[List[str]] = None
    include_analysis: bool = True


class UITestRequest(BaseModel):
    """UI 测试请求"""
    base_url: str = "http://localhost:3000"


class TestResponse(BaseModel):
    """测试响应"""
    status: str
    summary: Dict[str, Any]
    results: List[Dict]
    issues: List[Dict]
    analysis: Dict[str, Any]


class IssueListResponse(BaseModel):
    """问题列表响应"""
    issues: List[Dict]
    total: int


def _extract_severity(task: Task) -> str:
    source_data = task.source_data or {}
    original_data = source_data.get("original_data", {})
    if not isinstance(original_data, dict):
        original_data = {}

    return (
        source_data.get("severity")
        or original_data.get("severity")
        or {0: "critical", 1: "warning", 2: "error", 3: "info"}.get(task.priority, "info")
    )


def _extract_issue_type(task: Task) -> str:
    source_data = task.source_data or {}
    original_data = source_data.get("original_data", {})
    if not isinstance(original_data, dict):
        original_data = {}

    return (
        source_data.get("task_type")
        or source_data.get("type")
        or original_data.get("type")
        or task.category
        or "unknown"
    )


def _serialize_task(task: Task) -> Dict[str, Any]:
    source_data = task.source_data or {}
    details = source_data.get("latest_payload") or source_data.get("original_data") or source_data

    return {
        "id": str(task.id),
        "source_type": task.source_type,
        "source_id": task.source_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "severity": _extract_severity(task),
        "issue_type": _extract_issue_type(task),
        "category": task.category,
        "status": task.status,
        "auto_processible": task.auto_processible,
        "occurrence_count": int(source_data.get("occurrence_count") or 1),
        "first_seen_at": source_data.get("first_seen_at"),
        "last_seen_at": source_data.get("last_seen_at"),
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        "details": details,
    }


def _serialize_history_entry(history: TaskHistory, task: Task) -> Dict[str, Any]:
    return {
        "id": str(history.id),
        "task_id": str(task.id),
        "task_title": task.title,
        "source_type": task.source_type,
        "task_status": task.status,
        "action": history.action,
        "result": history.result,
        "details": history.details or {},
        "performed_by": history.performed_by,
        "created_at": history.created_at.isoformat() if history.created_at else None,
    }


async def _create_tasks_from_test_results(
    test_type: str,
    test_result: dict,
    db: AsyncSession,
) -> Dict[str, int]:
    """Create or reuse tasks based on test results."""
    from feeds.task_classifier import get_task_classifier
    from feeds.task_processor import get_task_processor
    from notifications.task_notification import get_task_notification_service

    created_count = 0
    reused_count = 0
    issues = test_result.get("issues", [])
    classifier = get_task_classifier()
    processor = get_task_processor(db)
    notification_service = get_task_notification_service()

    for issue in issues:
        try:
            classification = classifier.classify(test_type, issue)
            task = await processor.create_task(classification)

            if getattr(task, "_was_created", True):
                await processor.process(task)
                await notification_service.notify_task_created(task)
                created_count += 1
            else:
                reused_count += 1
        except Exception as exc:
            logger.error(f"创建任务失败: {exc}")

    return {"created": created_count, "reused": reused_count}


@router.post("/run", response_model=TestResponse)
async def run_tests(
    request: RunTestRequest = None,
    db: AsyncSession = Depends(get_db),
):
    """
    运行完整测试套件

    执行所有 API 测试并返回结果
    """
    from feeds.ai_tester import run_ai_test

    result = await run_ai_test(llm_client=None)
    task_summary = await _create_tasks_from_test_results("api_test", result, db)

    analysis = dict(result.get("analysis", {}))
    analysis["task_summary"] = task_summary

    return TestResponse(
        status="completed",
        summary=result["summary"],
        results=result["results"],
        issues=result["issues"],
        analysis=analysis,
    )


@router.get("/issues", response_model=IssueListResponse)
async def get_issues(
    severity: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """获取发现的问题列表"""
    limit = max(1, min(limit, 200))
    fetch_limit = max(limit * 5, 100)

    stmt = select(Task).where(Task.source_type.in_(TESTING_SOURCE_TYPES))
    if status:
        stmt = stmt.where(Task.status == status)
    else:
        stmt = stmt.where(Task.status.in_(OPEN_ISSUE_STATUSES))

    stmt = stmt.order_by(Task.updated_at.desc().nullslast(), Task.created_at.desc()).limit(fetch_limit)
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    issues: List[Dict[str, Any]] = []
    for task in tasks:
        item = _serialize_task(task)
        if severity and item["severity"] != severity:
            continue
        if category and item["category"] != category:
            continue
        issues.append(item)

    return IssueListResponse(
        issues=issues[:limit],
        total=len(issues),
    )


@router.get("/history")
async def get_test_history(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """获取测试历史"""
    limit = max(1, min(limit, 100))

    stmt = (
        select(TaskHistory, Task)
        .join(Task, TaskHistory.task_id == Task.id)
        .where(Task.source_type.in_(TESTING_SOURCE_TYPES))
        .order_by(TaskHistory.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()

    history = [_serialize_history_entry(task_history, task) for task_history, task in rows]
    return {
        "history": history,
        "total": len(history),
    }


@router.get("/health")
async def health_check():
    """测试系统健康检查"""
    import aiohttp

    api_status = {}
    base_url = "http://127.0.0.1:8000"
    endpoints = [
        "/api/feeds",
        "/api/sources",
        "/api/chat",
        "/api/evolution/status",
    ]

    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            try:
                async with session.get(f"{base_url}{endpoint}", timeout=3) as resp:
                    api_status[endpoint] = {
                        "status": resp.status,
                        "available": resp.status == 200,
                    }
            except Exception as exc:
                api_status[endpoint] = {
                    "status": 0,
                    "available": False,
                    "error": str(exc),
                }

    available_count = sum(1 for value in api_status.values() if value.get("available", False))
    health_score = available_count / len(api_status) if api_status else 0

    return {
        "health_score": health_score,
        "status": "healthy" if health_score > 0.5 else "degraded",
        "api_status": api_status,
    }


@router.post("/ui/run")
async def run_ui_tests(
    request: UITestRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    运行 UI 自动化测试

    使用 Selenium 模拟浏览器操作，测试：
    - 功能：页面加载、导航、交互
    - 性能：加载时间、渲染速度
    - UI：布局、响应式
    - 质量：控制台错误
    """
    try:
        from feeds.ai_ui_tester import run_ui_tests as run_ui
        import asyncio

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_ui, request.base_url)
        task_summary = await _create_tasks_from_test_results("ui_test", result, db)

        return {
            "status": "completed",
            "summary": result["summary"],
            "results": result["results"],
            "issues": result["issues"],
            "analysis": {"task_summary": task_summary},
        }
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Playwright not installed. Run: pip install playwright && playwright install chromium",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/ui/dimensions")
async def get_test_dimensions():
    """获取测试维度说明"""
    return {
        "dimensions": {
            "functional": "功能测试 - 页面加载、按钮点击、表单提交等",
            "performance": "性能测试 - 加载时间、响应速度、资源大小",
            "ui": "UI测试 - 布局、响应式、样式",
            "ux": "用户体验 - 操作流程、交互反馈",
            "quality": "质量测试 - 控制台错误、JavaScript错误",
            "depth": "深度测试 - 复杂功能、数据处理",
            "evolution": "进化建议 - 基于测试结果的优化方向",
        }
    }
