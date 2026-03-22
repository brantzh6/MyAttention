from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy import case, func, select

from db import get_db, AsyncSession
from db.models import Task, TaskHistory, TaskStatus

router = APIRouter(tags=["自我进化系统"])

MVP_ISSUE_SOURCE_TYPES = ("api_test", "ui_test", "log_analysis", "system_health")
MVP_OPEN_STATUSES = (
    TaskStatus.PENDING.value,
    TaskStatus.CONFIRMED.value,
    TaskStatus.EXECUTING.value,
    TaskStatus.FAILED.value,
)
MVP_BLOCKING_SOURCE_TYPES = ("api_test", "ui_test", "system_health")


# ═══════════════════════════════════════════════════════════════════════════
# 数据模型
# ═══════════════════════════════════════════════════════════════════════════

class SourceEvaluationRequest(BaseModel):
    source_id: str


class EvolutionTriggerResponse(BaseModel):
    status: str
    message: str
    timestamp: str


class SourceScorecardResponse(BaseModel):
    source_id: str
    source_name: str
    overall_score: float
    read_rate: float
    quality_rate: float
    recommendation: str


class AntiCrawlTestRequest(BaseModel):
    url: str
    method: str = "direct"


class AntiCrawlTestResponse(BaseModel):
    url: str
    success: bool
    status: str
    method_used: str
    attempts: int


class KnowledgeExtractRequest(BaseModel):
    text: str
    title: str = ""
    category: str = ""


class KnowledgeExtractResponse(BaseModel):
    status: str
    entities: List[Dict]
    relations: List[Dict]


class SourceDiscoveryRequest(BaseModel):
    domain: str
    criteria: Optional[Dict] = None


class SourceDiscoveryResponse(BaseModel):
    status: str
    candidates: List[Dict]


class KnowledgeSearchRequest(BaseModel):
    query: str
    max_results: int = 20


class KnowledgeSearchResponse(BaseModel):
    query: str
    entities: List[Dict]
    relations: List[Dict]


# ═══════════════════════════════════════════════════════════════════════════
# 进化引擎 API
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/sources/evaluate", response_model=SourceScorecardResponse)
async def evaluate_source(
    request: SourceEvaluationRequest,
    db: AsyncSession = Depends(get_db)
):
    """评估单个信息源的效果"""
    from feeds.evolution import SourceEvolutionEngine

    engine = SourceEvolutionEngine(db)
    scorecard = await engine.get_source_scorecard(request.source_id)

    if scorecard is None:
        raise HTTPException(status_code=404, detail="Source not found")

    return SourceScorecardResponse(
        source_id=scorecard.source_id,
        source_name=scorecard.source_name,
        overall_score=scorecard.overall_score,
        read_rate=scorecard.read_rate,
        quality_rate=scorecard.quality_rate,
        recommendation=scorecard.recommendation
    )


@router.post("/sources/evolve-all")
async def evolve_all_sources(db: AsyncSession = Depends(get_db)):
    """对所有信息源执行进化优化"""
    from feeds.evolution import SourceEvolutionEngine

    engine = SourceEvolutionEngine(db)
    results = await engine.evolve_all_sources()

    return {
        "status": "completed",
        "total": len(results),
        "timestamp": datetime.now().isoformat()
    }


# ═══════════════════════════════════════════════════════════════════════════
# 调度 API
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/trigger", response_model=EvolutionTriggerResponse)
async def trigger_evolution(db: AsyncSession = Depends(get_db)):
    """手动触发一次完整的进化周期"""
    from pipeline.evolution_scheduler import run_evolution_cycle

    result = await run_evolution_cycle(db)

    return EvolutionTriggerResponse(
        status="success",
        message=f"进化完成，处理了 {result.get('source_evaluation', {}).get('total_sources', 0)} 个信息源",
        timestamp=datetime.now().isoformat()
    )


@router.get("/status")
async def get_evolution_status(db: AsyncSession = Depends(get_db)):
    """获取进化系统状态"""
    from feeds.auto_evolution import get_auto_evolution_system

    system = get_auto_evolution_system()
    status = system.get_status()

    return {
        "status": "running" if status["running"] else "stopped",
        "health": status.get("health", "unknown"),
        "issues": status.get("issues", []),
        "components": status["components"],
        "intervals": status["intervals"],
        "last_results": status.get("last_results", {}),
        "timestamp": datetime.now().isoformat()
    }


@router.post("/self-test/run")
async def run_self_test_now():
    """Manually trigger one self-test cycle."""
    from feeds.auto_evolution import get_auto_evolution_system

    system = get_auto_evolution_system()
    await system._run_self_test_once()
    status = system.get_status()
    return {
        "status": "ok",
        "self_test": status.get("last_results", {}).get("self_test", {}),
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/collection-health")
async def get_collection_health(
    fresh: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """获取信息收集链路健康状态。"""
    from feeds.auto_evolution import get_auto_evolution_system
    from feeds.collection_health import collect_collection_health_snapshot

    if fresh:
        return await collect_collection_health_snapshot(db)

    system = get_auto_evolution_system()
    status = system.get_status()
    cached = status.get("last_results", {}).get("collection_health")
    if cached:
        return cached

    return await collect_collection_health_snapshot(db)


@router.get("/mvp-status")
async def get_mvp_status(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Return a compact operational view for trial runs."""
    from feeds.auto_evolution import get_auto_evolution_system
    from feeds.collection_health import collect_collection_health_snapshot

    system = get_auto_evolution_system()
    status = system.get_status()
    last_results = status.get("last_results", {})

    collection_health = last_results.get("collection_health") or await collect_collection_health_snapshot(db)
    self_test = last_results.get("self_test") or {}
    log_health = last_results.get("log_health") or {}

    scheduler = getattr(request.app.state, "pipeline_scheduler", None)
    pipeline_status: Dict[str, Any]
    if scheduler is None:
        pipeline_status = {"status": "disabled"}
    else:
        pipeline_status = {
            "status": "running" if scheduler._running else "stopped",
            **scheduler.stats,
        }

    open_tasks = (
        await db.execute(
            select(Task)
            .where(Task.source_type.in_(MVP_ISSUE_SOURCE_TYPES))
            .where(Task.status.in_(MVP_OPEN_STATUSES))
            .order_by(Task.updated_at.desc().nullslast(), Task.created_at.desc())
        )
    ).scalars().all()

    active_cutoff = datetime.now(timezone.utc) - timedelta(hours=6)

    def _task_seen_at(task: Task) -> datetime | None:
        source_data = task.source_data or {}
        last_seen_raw = source_data.get("last_seen_at")
        if isinstance(last_seen_raw, str):
            try:
                normalized = last_seen_raw.replace("Z", "+00:00")
                parsed = datetime.fromisoformat(normalized)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed
            except ValueError:
                pass
        fallback = task.updated_at or task.created_at
        if fallback and fallback.tzinfo is None:
            fallback = fallback.replace(tzinfo=timezone.utc)
        return fallback

    active_blockers = [
        task
        for task in open_tasks
        if task.source_type in MVP_BLOCKING_SOURCE_TYPES and (_task_seen_at(task) or datetime.min.replace(tzinfo=timezone.utc)) >= active_cutoff
    ]

    recent_history_stmt = (
        select(TaskHistory, Task)
        .join(Task, TaskHistory.task_id == Task.id)
        .where(Task.source_type.in_(MVP_ISSUE_SOURCE_TYPES))
        .order_by(TaskHistory.created_at.desc())
        .limit(10)
    )
    recent_history_rows = (await db.execute(recent_history_stmt)).all()
    recent_actions = [
        {
            "task_id": str(task.id),
            "title": task.title,
            "source_type": task.source_type,
            "priority": task.priority,
            "status": task.status,
            "action": history.action,
            "result": history.result,
            "details": history.details or {},
            "created_at": history.created_at.isoformat() if history.created_at else None,
        }
        for history, task in recent_history_rows
    ]

    self_test_healthy = bool(self_test.get("healthy", False))
    collection_summary = collection_health.get("summary") or {}
    collection_status = collection_summary.get("status", "unknown")
    trial_ready = (
        status.get("running", False)
        and self_test_healthy
        and collection_status != "unhealthy"
        and not any(task.priority <= 1 for task in active_blockers)
    )

    return {
        "trial_ready": trial_ready,
        "timestamp": datetime.now().isoformat(),
        "auto_evolution": {
            "running": status.get("running", False),
            "components": status.get("components", {}),
            "intervals": status.get("intervals", {}),
        },
        "self_test": self_test,
        "log_health": log_health,
        "collection_health": collection_health,
        "pipeline": pipeline_status,
        "open_issues": {
            "total": len(open_tasks),
            "p0": sum(1 for task in open_tasks if task.priority == 0),
            "p1": sum(1 for task in open_tasks if task.priority == 1),
            "active_blockers_6h": len(active_blockers),
        },
        "recent_actions": recent_actions,
    }


# ═══════════════════════════════════════════════════════════════════════════
# 反爬处理 API
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/anti-crawl/test", response_model=AntiCrawlTestResponse)
async def test_anti_crawl(request: AntiCrawlTestRequest):
    """测试 URL 的反爬情况"""
    from feeds.anti_crawl import get_anti_crawl_handler
    from db.models import AccessMethod

    handler = get_anti_crawl_handler()

    method_map = {
        "direct": AccessMethod.DIRECT,
        "proxy": AccessMethod.PROXY,
        "cloud": AccessMethod.CLOUD,
    }

    method = method_map.get(request.method, AccessMethod.DIRECT)

    result = await handler.fetch_with_auto_retry(
        url=request.url,
        initial_method=method
    )

    return AntiCrawlTestResponse(
        url=request.url,
        success=result.success,
        status=result.status.value,
        method_used=result.method_used,
        attempts=result.attempts
    )


# ═══════════════════════════════════════════════════════════════════════════
# 知识图谱 API
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/knowledge/extract", response_model=KnowledgeExtractResponse)
async def extract_knowledge(request: KnowledgeExtractRequest, db: AsyncSession = Depends(get_db)):
    """从文本中提取知识（图谱）"""
    from knowledge.graph import KnowledgeGraphManager

    kg = KnowledgeGraphManager(db)
    result = await kg.process_text(
        text=request.text,
        title=request.title,
        category=request.category
    )

    return KnowledgeExtractResponse(
        status=result.get("status", "unknown"),
        entities=result.get("entities", []),
        relations=result.get("relations", [])
    )


@router.post("/knowledge/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(request: KnowledgeSearchRequest, db: AsyncSession = Depends(get_db)):
    """搜索知识图谱"""
    from knowledge.graph import KnowledgeGraphManager

    kg = KnowledgeGraphManager(db)
    result = await kg.search(request.query, request.max_results)

    return KnowledgeSearchResponse(
        query=request.query,
        entities=[
            {"id": str(e.id), "name": e.name, "type": e.entity_type}
            for e in result.entities
        ],
        relations=[
            {"source": str(r.source_id), "target": str(r.target_id), "type": r.relation_type}
            for r in result.relations
        ]
    )


@router.get("/knowledge/reason")
async def reason_knowledge(
    entity: str,
    target_type: str = None,
    db: AsyncSession = Depends(get_db)
):
    """知识推理 - 找出从一个实体到目标类型的推理路径"""
    from knowledge.graph import KnowledgeGraphManager

    kg = KnowledgeGraphManager(db)
    results = await kg.reason(entity, target_type)

    return {
        "entity": entity,
        "target_type": target_type,
        "paths": results
    }


@router.get("/knowledge/categories")
async def get_knowledge_categories(db: AsyncSession = Depends(get_db)):
    """获取知识分类树"""
    from knowledge.graph import KnowledgeGraphManager

    kg = KnowledgeGraphManager(db)
    categories = await kg.get_categories()

    return {"categories": categories}


# ═══════════════════════════════════════════════════════════════════════════
# AI 决策 API
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/ai/decide")
async def ai_decision(
    decision_type: str,
    source_name: str = "",
    source_url: str = "",
    current_status: str = "",
    error_message: str = "",
    success_count: int = 0,
    failure_count: int = 0,
    goal: str = ""
):
    """让 AI 做决策"""
    from feeds.ai_brain import AIDecisionBrain, DecisionContext, DecisionType

    # 创建决策上下文
    context = DecisionContext(
        decision_type=DecisionType(decision_type),
        source_name=source_name,
        source_url=source_url,
        current_status=current_status,
        error_message=error_message,
        success_count=success_count,
        failure_count=failure_count,
        goal=goal
    )

    brain = AIDecisionBrain()
    decision = await brain.decide(context)

    return {
        "action": decision.action,
        "reasoning": decision.reasoning,
        "confidence": decision.confidence,
        "alternatives": decision.alternative_actions,
        "expected_outcome": decision.expected_outcome
    }


@router.post("/ai/analyze")
async def ai_analyze(
    problem: str,
    context_data: Dict[str, Any] = {}
):
    """让 AI 分析问题"""
    from feeds.external_agent import get_ai_integration

    integration = get_ai_integration()
    response = await integration.analyze_problem(problem, context_data)

    if response.success:
        return {
            "status": "success",
            "result": response.result,
            "execution_time": response.execution_time
        }
    else:
        raise HTTPException(status_code=500, detail=response.error)


@router.post("/ai/discover-sources", response_model=SourceDiscoveryResponse)
async def ai_discover_sources(request: SourceDiscoveryRequest):
    """让 AI 发现新的信息源"""
    from feeds.external_agent import get_ai_integration

    integration = get_ai_integration()
    response = await integration.discover_sources(request.domain, request.criteria)

    if response.success:
        return SourceDiscoveryResponse(
            status="success",
            candidates=response.result.get("candidates", []) if response.result else []
        )
    else:
        return SourceDiscoveryResponse(
            status="failed",
            candidates=[]
        )


# ═══════════════════════════════════════════════════════════════════════════
# 指标 API
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/metrics/source/{source_id}")
async def get_source_metrics(source_id: str, days: int = 30, db: AsyncSession = Depends(get_db)):
    """获取信息源的历史指标"""
    from feeds.metrics import SourceMetricsCollector

    collector = SourceMetricsCollector(db)
    history = await collector.get_metrics_history(source_id, days)
    trend = await collector.get_trend(source_id)

    return {
        "source_id": source_id,
        "days": days,
        "history": history,
        "trend": trend
    }


@router.get("/metrics/knowledge/{kb_id}")
async def get_knowledge_metrics(kb_id: str, db: AsyncSession = Depends(get_db)):
    """获取知识库指标统计"""
    from feeds.metrics import KnowledgeMetricsCollector

    collector = KnowledgeMetricsCollector(db)
    stats = await collector.get_knowledge_stats(kb_id)

    return {
        "knowledge_base_id": kb_id,
        "stats": stats
    }


# ═══════════════════════════════════════════════════════════════════════════
# 任务管理 API
# ═══════════════════════════════════════════════════════════════════════════

class TaskCreateRequest(BaseModel):
    """创建任务请求"""
    source_type: str
    source_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    priority: int = 2
    category: Optional[str] = None
    auto_processible: bool = False
    source_data: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    """任务响应"""
    id: str
    source_type: str
    source_id: Optional[str]
    title: str
    description: Optional[str]
    priority: int
    category: Optional[str]
    status: str
    auto_processible: bool
    created_at: str
    updated_at: Optional[str]
    created_by: str


class TaskListResponse(BaseModel):
    """任务列表响应"""
    tasks: List[TaskResponse]
    total: int
    pending_count: int
    p0_count: int
    p1_count: int


class TaskActionRequest(BaseModel):
    """任务操作请求"""
    action: str  # confirm, reject, execute
    reason: Optional[str] = None


@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    request: TaskCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建新任务"""
    from uuid import uuid4
    from db.models import Task, TaskStatus
    from feeds.task_processor import get_task_processor
    from feeds.task_classifier import get_task_classifier
    from notifications.task_notification import get_task_notification_service

    # 如果有来源数据，先进行分类
    if request.source_data:
        classifier = get_task_classifier()
        classification = classifier.classify(request.source_type, request.source_data)

        # 使用分类结果
        task = Task(
            id=uuid4(),
            source_type=classification.source_type,
            source_id=classification.source_id,
            source_data=classification.source_data,
            title=classification.title,
            description=classification.description,
            priority=classification.priority,
            category=classification.category,
            status=TaskStatus.PENDING.value,
            auto_processible=classification.auto_processible,
            created_by="system"
        )
    else:
        # 手动创建任务
        task = Task(
            id=uuid4(),
            source_type=request.source_type,
            source_id=request.source_id,
            source_data=request.source_data or {},
            title=request.title,
            description=request.description,
            priority=request.priority,
            category=request.category,
            status=TaskStatus.PENDING.value,
            auto_processible=request.auto_processible,
            created_by="user"
        )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    # 处理任务（自动处理或发送通知）
    processor = get_task_processor(db)
    await processor.process(task)

    # 发送通知
    notification_service = get_task_notification_service()
    await notification_service.notify_task_created(task)

    return TaskResponse(
        id=str(task.id),
        source_type=task.source_type,
        source_id=task.source_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        category=task.category,
        status=task.status,
        auto_processible=task.auto_processible,
        created_at=task.created_at.isoformat() if task.created_at else "",
        updated_at=task.updated_at.isoformat() if task.updated_at else None,
        created_by=task.created_by
    )


@router.get("/tasks", response_model=TaskListResponse)
async def get_tasks(
    priority: Optional[int] = None,
    status: Optional[str] = None,
    source_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """获取任务列表"""
    from db.models import Task
    from sqlalchemy import select, func

    # 构建查询
    query = select(Task)
    count_query = select(func.count(Task.id))

    # 添加过滤条件
    if priority is not None:
        query = query.where(Task.priority == priority)
        count_query = count_query.where(Task.priority == priority)

    if status:
        query = query.where(Task.status == status)
        count_query = count_query.where(Task.status == status)

    if source_type:
        query = query.where(Task.source_type == source_type)
        count_query = count_query.where(Task.source_type == source_type)

    # 排序和分页
    query = query.order_by(Task.priority.asc(), Task.created_at.desc())
    query = query.offset(offset).limit(limit)

    # 执行查询
    result = await db.execute(query)
    tasks = result.scalars().all()

    # 获取总数
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # 统计
    pending_result = await db.execute(
        select(func.count(Task.id)).where(Task.status == "pending")
    )
    pending_count = pending_result.scalar()

    p0_result = await db.execute(
        select(func.count(Task.id)).where(Task.priority == 0)
    )
    p0_count = p0_result.scalar()

    p1_result = await db.execute(
        select(func.count(Task.id)).where(Task.priority == 1)
    )
    p1_count = p1_result.scalar()

    return TaskListResponse(
        tasks=[
            TaskResponse(
                id=str(t.id),
                source_type=t.source_type,
                source_id=t.source_id,
                title=t.title,
                description=t.description,
                priority=t.priority,
                category=t.category,
                status=t.status,
                auto_processible=t.auto_processible,
                created_at=t.created_at.isoformat() if t.created_at else "",
                updated_at=t.updated_at.isoformat() if t.updated_at else None,
                created_by=t.created_by
            )
            for t in tasks
        ],
        total=total or 0,
        pending_count=pending_count or 0,
        p0_count=p0_count or 0,
        p1_count=p1_count or 0
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取单个任务详情"""
    from db.models import Task
    from uuid import UUID

    task = await db.get(Task, UUID(task_id))

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse(
        id=str(task.id),
        source_type=task.source_type,
        source_id=task.source_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        category=task.category,
        status=task.status,
        auto_processible=task.auto_processible,
        created_at=task.created_at.isoformat() if task.created_at else "",
        updated_at=task.updated_at.isoformat() if task.updated_at else None,
        created_by=task.created_by
    )


@router.post("/tasks/{task_id}/action")
async def task_action(
    task_id: str,
    request: TaskActionRequest,
    db: AsyncSession = Depends(get_db)
):
    """执行任务操作（确认/拒绝/执行）"""
    from db.models import Task
    from uuid import UUID
    from feeds.task_processor import get_task_processor

    task = await db.get(Task, UUID(task_id))

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    processor = get_task_processor(db)

    if request.action == "confirm":
        result = await processor.confirm_task(task, user_id="user")
    elif request.action == "reject":
        result = await processor.reject_task(task, reason=request.reason or "", user_id="user")
    elif request.action == "execute":
        result = await processor.execute_task(task, user_id="user")
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")

    return {
        "success": result.success,
        "action": result.action,
        "message": result.message,
        "task_id": str(task.id),
        "task_status": task.status
    }


@router.get("/tasks/{task_id}/history")
async def get_task_history(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取任务处理历史"""
    from db.models import TaskHistory
    from uuid import UUID
    from sqlalchemy import select

    result = await db.execute(
        select(TaskHistory)
        .where(TaskHistory.task_id == UUID(task_id))
        .order_by(TaskHistory.created_at.desc())
    )
    history = result.scalars().all()

    return {
        "history": [
            {
                "id": str(h.id),
                "action": h.action,
                "result": h.result,
                "details": h.details,
                "performed_by": h.performed_by,
                "created_at": h.created_at.isoformat() if h.created_at else ""
            }
            for h in history
        ]
    }


@router.post("/tasks/{task_id}/auto-process")
async def auto_process_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """自动处理任务（仅 P0 任务）"""
    from db.models import Task, TaskStatus
    from uuid import UUID
    from feeds.task_processor import get_task_processor

    task = await db.get(Task, UUID(task_id))

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 检查是否是 P0 任务且可自动处理
    if task.priority != 0 or not task.auto_processible:
        raise HTTPException(
            status_code=400,
            detail="Only P0 tasks with auto_processible=True can be auto-processed"
        )

    processor = get_task_processor(db)
    result = await processor.auto_process(task)

    return {
        "success": result.success,
        "message": result.message,
        "task_status": task.status
    }


@router.get("/tasks/stats/summary")
async def get_task_summary(db: AsyncSession = Depends(get_db)):
    """获取任务统计摘要"""
    from db.models import Task
    from sqlalchemy import select, func
    from datetime import datetime, timedelta

    # 总数统计
    total_result = await db.execute(select(func.count(Task.id)))
    total = total_result.scalar()

    # 按状态统计
    status_result = await db.execute(
        select(Task.status, func.count(Task.id))
        .group_by(Task.status)
    )
    status_counts = dict(status_result.all())

    # 按优先级统计
    priority_result = await db.execute(
        select(Task.priority, func.count(Task.id))
        .group_by(Task.priority)
    )
    priority_counts = dict(priority_result.all())

    # 今日新增
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_result = await db.execute(
        select(func.count(Task.id))
        .where(Task.created_at >= today_start)
    )
    today_count = today_result.scalar()

    # 待处理超时
    now = datetime.utcnow()
    timeout_result = await db.execute(
        select(func.count(Task.id))
        .where(Task.status == "pending")
        .where(Task.expired_at < now)
    )
    timeout_count = timeout_result.scalar()

    return {
        "total": total or 0,
        "by_status": status_counts,
        "by_priority": priority_counts,
        "today_new": today_count or 0,
        "timeout_pending": timeout_count or 0
    }


@router.post("/tasks/from-test-result")
async def create_task_from_test_result(
    test_type: str,  # api_test, ui_test
    test_result: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """从测试结果创建任务"""
    from feeds.task_classifier import get_task_classifier
    from feeds.task_processor import get_task_processor
    from notifications.task_notification import get_task_notification_service

    # 分类测试结果
    classifier = get_task_classifier()
    classification = classifier.classify(test_type, test_result)

    # 创建任务
    processor = get_task_processor(db)
    task = await processor.create_task(classification)

    # 处理任务
    await processor.process(task)

    # 发送通知
    notification_service = get_task_notification_service()
    await notification_service.notify_task_created(task)

    return {
        "task_id": str(task.id),
        "priority": task.priority,
        "status": task.status,
        "auto_processible": task.auto_processible
    }


# ═══════════════════════════════════════════════════════════════════════════
# 日志监控与分析 API
# ═══════════════════════════════════════════════════════════════════════════

class LogAnalysisRequest(BaseModel):
    """日志分析请求"""
    source: Optional[str] = None  # api, chat, web_api, web_frontend
    hours: int = 24
    level: Optional[str] = None  # ERROR, WARNING, INFO


class HealthSummaryResponse(BaseModel):
    """健康摘要响应"""
    total_logs: int
    error_count: int
    warning_count: int
    health_score: float
    status: str
    top_errors: List[Dict]
    insights: List[Dict]
    timestamp: str


class InsightResponse(BaseModel):
    """洞察响应"""
    insights: List[Dict]
    total: int
    critical_count: int
    warning_count: int


@router.post("/logs/analyze", response_model=HealthSummaryResponse)
async def analyze_logs(request: LogAnalysisRequest):
    """
    分析日志并生成健康报告

    收集和分析系统日志，识别错误模式、性能问题和改进建议
    """
    from feeds.log_monitor import get_log_monitor

    monitor = get_log_monitor()
    logs = monitor.collect_logs(
        source=request.source,
        hours=request.hours,
        level=request.level
    )

    # 统计
    error_count = len([l for l in logs if l.level == "ERROR"])
    warning_count = len([l for l in logs if l.level == "WARNING"])
    total = len(logs)

    # 计算健康分数
    if total > 0:
        health_score = 1 - (error_count / total) * 2 - (warning_count / total) * 0.5
        health_score = max(0, min(1, health_score))
    else:
        health_score = 1.0

    # 错误模式
    error_patterns = monitor.analyze_errors(logs)

    # 洞察建议
    insights = monitor.generate_insights(logs)

    # 确定状态
    if health_score > 0.8:
        status = "healthy"
    elif health_score > 0.5:
        status = "degraded"
    else:
        status = "unhealthy"

    return HealthSummaryResponse(
        total_logs=total,
        error_count=error_count,
        warning_count=warning_count,
        health_score=round(health_score, 2),
        status=status,
        top_errors=[
            {
                "pattern": p.pattern,
                "count": p.count,
                "severity": p.severity,
                "description": p.description,
                "suggestion": p.suggestion
            }
            for p in error_patterns[:5]
        ],
        insights=[
            {
                "id": i.id,
                "category": i.category,
                "severity": i.severity,
                "title": i.title,
                "description": i.description,
                "suggestion": i.suggestion,
                "impact": i.impact,
                "effort": i.effort
            }
            for i in insights[:10]
        ],
        timestamp=datetime.now().isoformat()
    )


@router.get("/logs/health", response_model=HealthSummaryResponse)
async def get_log_health_summary(hours: int = 24):
    """
    获取日志健康摘要

    快速获取系统健康状态，无需详细分析
    """
    from feeds.log_monitor import get_log_monitor

    monitor = get_log_monitor()
    logs = monitor.collect_logs(hours=hours)

    error_count = len([l for l in logs if l.level == "ERROR"])
    warning_count = len([l for l in logs if l.level == "WARNING"])
    total = len(logs)

    if total > 0:
        health_score = 1 - (error_count / total) * 2 - (warning_count / total) * 0.5
        health_score = max(0, min(1, health_score))
    else:
        health_score = 1.0

    error_patterns = monitor.analyze_errors(logs)
    insights = monitor.generate_insights(logs)

    if health_score > 0.8:
        status = "healthy"
    elif health_score > 0.5:
        status = "degraded"
    else:
        status = "unhealthy"

    return HealthSummaryResponse(
        total_logs=total,
        error_count=error_count,
        warning_count=warning_count,
        health_score=round(health_score, 2),
        status=status,
        top_errors=[
            {
                "pattern": p.pattern,
                "count": p.count,
                "severity": p.severity,
                "description": p.description,
                "suggestion": p.suggestion
            }
            for p in error_patterns[:5]
        ],
        insights=[
            {
                "id": i.id,
                "category": i.category,
                "severity": i.severity,
                "title": i.title,
                "description": i.description,
                "suggestion": i.suggestion,
                "impact": i.impact,
                "effort": i.effort
            }
            for i in insights[:10]
        ],
        timestamp=datetime.now().isoformat()
    )


@router.get("/logs/insights", response_model=InsightResponse)
async def get_system_insights(
    category: Optional[str] = None,
    severity: Optional[str] = None,
    hours: int = 24
):
    """
    获取系统改进建议

    基于日志分析生成系统改进建议
    """
    from feeds.log_monitor import get_log_monitor

    monitor = get_log_monitor()
    logs = monitor.collect_logs(hours=hours)
    insights = monitor.generate_insights(logs)

    # 过滤
    if category:
        insights = [i for i in insights if i.category == category]
    if severity:
        insights = [i for i in insights if i.severity == severity]

    critical_count = len([i for i in insights if i.severity == "critical"])
    warning_count = len([i for i in insights if i.severity == "warning"])

    return InsightResponse(
        insights=[
            {
                "id": i.id,
                "category": i.category,
                "severity": i.severity,
                "title": i.title,
                "description": i.description,
                "evidence": i.evidence,
                "suggestion": i.suggestion,
                "impact": i.impact,
                "effort": i.effort,
                "created_at": i.created_at.isoformat()
            }
            for i in insights
        ],
        total=len(insights),
        critical_count=critical_count,
        warning_count=warning_count
    )


@router.get("/logs/errors")
async def get_error_patterns(hours: int = 24, limit: int = 20):
    """
    获取错误模式统计

    分析并返回最常见的错误模式
    """
    from feeds.log_monitor import get_log_monitor

    monitor = get_log_monitor()
    logs = monitor.collect_logs(hours=hours)
    error_patterns = monitor.analyze_errors(logs)

    return {
        "errors": [
            {
                "pattern": p.pattern,
                "count": p.count,
                "severity": p.severity,
                "description": p.description,
                "suggestion": p.suggestion,
                "first_seen": p.first_seen.isoformat() if p.first_seen else None,
                "last_seen": p.last_seen.isoformat() if p.last_seen else None
            }
            for p in error_patterns[:limit]
        ],
        "total": len(error_patterns)
    }


@router.get("/logs/metrics")
async def get_log_metrics(hours: int = 24):
    """
    获取性能指标统计

    从日志中提取和计算性能指标
    """
    from feeds.log_monitor import get_log_monitor

    monitor = get_log_monitor()
    logs = monitor.collect_logs(hours=hours)
    metrics = monitor.analyze_metrics(logs)
    source_stats = monitor.analyze_by_source(logs)

    return {
        "metrics": [
            {
                "name": m.name,
                "value": round(m.value, 2),
                "unit": m.unit,
                "trend": m.trend,
                "description": m.description
            }
            for m in metrics
        ],
        "by_source": source_stats,
        "analyzed_logs": len(logs)
    }


@router.get("/logs/recent")
async def get_recent_logs(
    source: Optional[str] = None,
    level: Optional[str] = None,
    hours: int = 1,
    limit: int = 100
):
    """
    获取最近的日志条目

    用于实时查看日志
    """
    from feeds.log_monitor import get_log_monitor

    monitor = get_log_monitor()
    logs = monitor.collect_logs(source=source, hours=hours, level=level)

    return {
        "logs": [
            {
                "timestamp": l.timestamp.isoformat(),
                "level": l.level,
                "logger": l.logger,
                "message": l.message[:500],  # 限制长度
                "source": l.source
            }
            for l in logs[:limit]
        ],
        "total": len(logs)
    }


@router.post("/logs/insights/{insight_id}/to-task")
async def convert_insight_to_task(
    insight_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    将洞察建议转化为任务

    将系统改进建议转化为可执行的任务
    """
    from feeds.log_monitor import get_log_monitor

    monitor = get_log_monitor()
    logs = monitor.collect_logs(hours=24)
    insights = monitor.generate_insights(logs)

    # 查找对应的洞察
    insight = next((i for i in insights if i.id == insight_id), None)

    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")

    # 创建任务
    from uuid import uuid4
    from db.models import Task, TaskStatus

    # 确定优先级
    priority_map = {"critical": 0, "high": 1, "warning": 2, "medium": 2, "low": 3, "info": 3}
    priority = priority_map.get(insight.severity, 2)

    # 确定是否可自动处理
    auto_processible = insight.severity in ("critical", "high") and insight.category in ("performance", "reliability")

    task = Task(
        id=uuid4(),
        source_type="log_analysis",
        source_id=insight_id,
        source_data={
            "category": insight.category,
            "evidence": insight.evidence
        },
        title=f"[日志分析] {insight.title}",
        description=insight.description + "\n\n建议: " + insight.suggestion,
        priority=priority,
        category=insight.category,
        status=TaskStatus.PENDING.value,
        auto_processible=auto_processible,
        created_by="ai"
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    # 处理任务
    from feeds.task_processor import get_task_processor
    processor = get_task_processor(db)
    await processor.process(task)

    return {
        "task_id": str(task.id),
        "insight_id": insight_id,
        "priority": task.priority,
        "status": task.status,
        "message": "洞察已转化为任务"
    }


# ═══════════════════════════════════════════════════════════════════════════
# 实时监控和问题中心 API
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/health/quick")
async def quick_health_check():
    """
    快速健康检查 - 秒级响应

    只检查最近5分钟的日志，快速发现严重问题
    适用于实时监控告警
    """
    from feeds.log_monitor import quick_health_check

    result = quick_health_check()
    return result


@router.get("/dashboard/problems")
async def get_problem_dashboard():
    """
    问题中心仪表盘

    返回：
    - 实时状态（最近1小时）
    - 任务待办（待处理、紧急、重要）
    - 洞察建议（最近的改进建议）
    - 错误趋势（24小时）
    """
    from feeds.log_monitor import get_problem_dashboard

    return get_problem_dashboard()


@router.post("/health/check-now")
async def trigger_instant_check():
    """
    立即触发一次日志分析

    手动触发，绕过定时任务，立即分析并创建任务
    """
    from pipeline.log_analysis_scheduler import get_log_analysis_scheduler

    scheduler = get_log_analysis_scheduler()

    # 1. 快速检查
    quick_result = await scheduler.check_and_alert()

    # 2. 完整分析
    analysis_result = await scheduler.run_analysis()

    return {
        "quick_check": quick_result,
        "analysis": analysis_result,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/problems/urgent")
async def get_urgent_problems():
    """
    获取紧急问题列表

    返回所有需要立即处理的紧急任务和严重错误
    """
    from sqlalchemy import select
    from db.models import Task, TaskStatus

    async with get_db() as db:
        # P0 紧急任务
        p0_result = await db.execute(
            select(Task)
            .where(Task.priority == 0)
            .where(Task.status.in_([TaskStatus.PENDING.value, TaskStatus.EXECUTING.value]))
            .order_by(Task.created_at.desc())
        )
        p0_tasks = p0_result.scalars().all()

        # P1 重要任务（未确认）
        p1_result = await db.execute(
            select(Task)
            .where(Task.priority == 1)
            .where(Task.status == TaskStatus.PENDING.value)
            .order_by(Task.created_at.desc())
        )
        p1_tasks = p1_result.scalars().all()

    return {
        "urgent_p0": [
            {
                "id": str(t.id),
                "title": t.title,
                "description": t.description[:200] if t.description else "",
                "status": t.status,
                "auto_processible": t.auto_processible,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "source_type": t.source_type
            }
            for t in p0_tasks
        ],
        "important_p1": [
            {
                "id": str(t.id),
                "title": t.title,
                "description": t.description[:200] if t.description else "",
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "source_type": t.source_type
            }
            for t in p1_tasks
        ],
        "total_p0": len(p0_tasks),
        "total_p1": len(p1_tasks)
    }


@router.post("/problems/{task_id}/resolve")
async def resolve_problem(
    task_id: str,
    resolution: str,
    db: AsyncSession = Depends(get_db)
):
    """
    解决问题

    记录解决方式并完成任务
    """
    from uuid import UUID
    from db.models import Task, TaskStatus
    from feeds.task_processor import get_task_processor

    task = await db.get(Task, UUID(task_id))

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    processor = get_task_processor(db)

    # 确认并执行
    result = await processor.confirm_task(task, user_id="user")

    # 更新描述添加解决方案
    if task.description:
        task.description = f"{task.description}\n\n解决方案: {resolution}"

    await db.commit()

    return {
        "success": True,
        "task_id": str(task.id),
        "status": task.status,
        "message": f"问题已解决: {resolution}"
    }
