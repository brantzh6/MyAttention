"""
自动进化系统启动器

在应用启动时自动加载所有进化组件：
1. AI 决策大脑
2. 反爬自动处理器
3. 进化调度器
4. 知识图谱

实现真正的全自动：无需人工介入，系统自我进化
"""

import asyncio
import logging
import os
import json
import time
from typing import Any, Optional
from datetime import datetime, timezone
from pathlib import Path
import aiohttp

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.session import get_db, get_db_context
from db.models import SourcePlan

logger = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parents[3]
UI_SMOKE_SCRIPT = REPO_ROOT / "services" / "web" / "scripts" / "ui-smoke-check.mjs"


def build_self_test_issue(snapshot: dict | None) -> dict | None:
    snapshot = snapshot or {}
    if snapshot.get("healthy", True):
        return None

    checks = snapshot.get("checks", [])
    failed_checks = [check for check in checks if not check.get("ok")]
    degraded_checks = [
        check for check in checks
        if check.get("ok") and (check.get("performance_warning") or check.get("stability_warning") or check.get("security_warning"))
    ]
    if not failed_checks and not degraded_checks:
        return None

    critical_ids = {"/health", "chat-voting-canary", "chat-single-canary", "frontend:/chat", "ui-browser:/chat"}
    is_critical = any(check.get("id") in critical_ids for check in failed_checks)
    has_performance_regression = any(check.get("performance_warning") for check in degraded_checks)
    priority = 0 if is_critical else (1 if failed_checks else 2)
    health = "critical" if is_critical else ("warning" if failed_checks else "degraded")

    failed_names = [check.get("name") or check.get("id") or "unknown" for check in failed_checks]
    degraded_names = [check.get("name") or check.get("id") or "unknown" for check in degraded_checks]
    if failed_checks:
        title = "[self-test] critical path failed" if is_critical else "[self-test] checks failed"
        description = "Failed checks: " + ", ".join(failed_names[:5])
    elif has_performance_regression:
        title = "[self-test] performance degraded"
        description = "Slow checks: " + ", ".join(degraded_names[:5])
    else:
        title = "[self-test] runtime degraded"
        description = "Degraded checks: " + ", ".join(degraded_names[:5])

    return {
        "priority": priority,
        "category": "reliability",
        "auto_processible": False,
        "title": title,
        "description": description,
        "source_type": "system_health",
        "source_id": "self_test",
        "source_data": {
            "type": "self_test",
            "health": health,
            "state": "failed",
            "summary": {
                "failed_count": len(failed_checks),
                "degraded_count": len(degraded_checks),
                "total_count": len(checks),
            },
            "checks": failed_checks or degraded_checks,
        },
    }


def build_source_plan_review_issues(snapshot: dict | None) -> list[dict[str, Any]]:
    snapshot = snapshot or {}
    issues: list[dict[str, Any]] = []

    for failure in snapshot.get("failures", []) or []:
        plan_id = str(failure.get("plan_id") or "unknown")
        issues.append(
            {
                "priority": 1,
                "category": "reliability",
                "auto_processible": False,
                "title": f"[source-plan] refresh failed: {plan_id[:8]}",
                "description": f"Scheduled source-plan refresh failed for plan {plan_id}.",
                "source_type": "system_health",
                "source_id": plan_id,
                "source_data": {
                    "type": "source_plan_review",
                    "health": "warning",
                    "state": "failed",
                    "summary": {
                        "plan_id": plan_id,
                        "topic": failure.get("topic", ""),
                        "status": failure.get("status"),
                    },
                    "failure": failure,
                },
            }
        )

    for refreshed in snapshot.get("refreshed", []) or []:
        review_status = str(refreshed.get("review_status") or "").strip().lower()
        current_version = int(refreshed.get("current_version") or 0)
        latest_version = int(refreshed.get("latest_version") or 0)
        if review_status != "needs_review" and latest_version <= current_version:
            continue

        plan_id = str(refreshed.get("plan_id") or "unknown")
        issues.append(
            {
                "priority": 1,
                "category": "quality",
                "auto_processible": False,
                "title": f"[source-plan] candidate needs review: {plan_id[:8]}",
                "description": f"Scheduled refresh produced a candidate source-plan version that needs review for plan {plan_id}.",
                "source_type": "system_health",
                "source_id": plan_id,
                "source_data": {
                    "type": "source_plan_review",
                    "health": "warning",
                    "state": "needs_review",
                    "summary": {
                        "plan_id": plan_id,
                        "topic": refreshed.get("topic", ""),
                        "current_version": current_version,
                        "latest_version": latest_version,
                    },
                    "refreshed": refreshed,
                },
            }
        )

    return issues


def evaluate_source_plan_quality_snapshot(
    *,
    topic: str,
    focus: str,
    review_status: str,
    policy_version: int,
    live_policy_version: int,
    item_types: list[str],
    bucket_counts: dict[str, int],
    gate_status_counts: dict[str, int],
    gate_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    gate_policy = dict(gate_policy or {})
    focus_value = str(focus or "").strip().lower()
    normalized_item_types = [str(item_type or "").strip().lower() for item_type in item_types if item_type]
    normalized_review_status = str(review_status or "").strip().lower()
    distinct_item_types = sorted(set(normalized_item_types))
    distinct_bucket_count = len([bucket for bucket, count in bucket_counts.items() if count > 0])
    total_items = max(sum(bucket_counts.values()), len(normalized_item_types))
    needs_review_items = int(gate_status_counts.get("needs_review", 0))
    selected_items = int(gate_status_counts.get("selected", 0))

    status = "healthy"
    reasons: list[str] = []

    if int(policy_version or 0) < int(live_policy_version or 0):
        status = "degraded"
        reasons.append("plan is still using an outdated attention policy version")

    minimum_distinct_buckets = int(gate_policy.get("minimum_distinct_buckets", 1) or 1)
    if distinct_bucket_count < minimum_distinct_buckets:
        status = "degraded" if focus_value == "method" else "warning"
        reasons.append("portfolio lacks enough bucket diversity for its current policy")

    if gate_policy.get("require_authority_bucket") and bucket_counts.get("authority", 0) == 0:
        status = "degraded"
        reasons.append("portfolio is missing an authority bucket")
    if gate_policy.get("require_research_bucket") and bucket_counts.get("research", 0) == 0:
        status = "degraded"
        reasons.append("portfolio is missing a research bucket")
    if gate_policy.get("require_implementation_bucket") and bucket_counts.get("implementation", 0) == 0:
        status = "degraded"
        reasons.append("portfolio is missing an implementation bucket")

    if focus_value == "method" and total_items > 0:
        if not any(item_type in {"repository", "community", "person"} for item_type in distinct_item_types):
            status = "degraded"
            reasons.append("method plan is still dominated by generic domains instead of concrete objects")

    if normalized_review_status == "accepted" and needs_review_items > 0 and needs_review_items >= max(2, total_items // 2):
        status = "warning" if status == "healthy" else status
        reasons.append("accepted plan still contains too many needs_review candidates")

    if normalized_review_status == "accepted" and selected_items == 0 and total_items > 0:
        status = "warning" if status == "healthy" else status
        reasons.append("accepted plan has no clearly selected candidates")

    if not reasons:
        reasons.append("source plan currently satisfies runtime quality checks")

    return {
        "topic": topic,
        "focus": focus_value,
        "status": status,
        "reasons": reasons,
        "summary": {
            "review_status": normalized_review_status,
            "policy_version": int(policy_version or 0),
            "live_policy_version": int(live_policy_version or 0),
            "distinct_item_types": distinct_item_types,
            "bucket_counts": dict(bucket_counts),
            "gate_status_counts": dict(gate_status_counts),
            "distinct_bucket_count": distinct_bucket_count,
            "total_items": total_items,
        },
    }


def build_source_plan_quality_issues(snapshot: dict | None) -> list[dict[str, Any]]:
    snapshot = snapshot or {}
    issues: list[dict[str, Any]] = []

    for finding in snapshot.get("quality_findings", []) or []:
        if str(finding.get("status") or "healthy") == "healthy":
            continue

        plan_id = str(finding.get("plan_id") or "unknown")
        severity = "critical" if finding.get("status") == "degraded" else "warning"
        priority = 0 if severity == "critical" else 1
        reasons = list(finding.get("reasons") or [])
        auto_processible = any(
            token in reason
            for reason in reasons
            for token in (
                "outdated attention policy version",
                "dominated by generic domains",
                "lacks enough bucket diversity",
                "missing an implementation bucket",
                "missing an authority bucket",
                "missing a research bucket",
            )
        )
        issues.append(
            {
                "priority": priority,
                "category": "quality",
                "auto_processible": auto_processible,
                "title": f"[source-plan] quality drift: {plan_id[:8]}",
                "description": "; ".join(reasons[:3]) or f"Source-plan quality drift detected for plan {plan_id}.",
                "source_type": "system_health",
                "source_id": plan_id,
                "source_data": {
                    "type": "source_plan_quality",
                    "health": severity,
                    "state": finding.get("status", "warning"),
                    "summary": finding.get("summary", {}),
                    "finding": finding,
                },
            }
        )

    return issues


def update_voting_canary_state(state: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
    event_type = event.get("type")

    if event_type == "voting_start":
        state["saw_start"] = True
        state["participants"] = event.get("models", []) or []
        return state

    if event_type == "voting_progress":
        model = event.get("model")
        if event.get("success"):
            if model:
                state["successful_models"].add(model)
        else:
            if model:
                state["failed_models"][model] = event.get("error") or "unknown"
        return state

    if event_type == "voting_synthesizing":
        state["saw_synthesizing"] = True
        return state

    if event_type == "voting_synthesis_content":
        chunk = (event.get("content") or "").strip()
        if chunk:
            state["saw_synthesis_content"] = True
        return state

    if event_type == "voting_result":
        state["saw_result"] = True
        state["result_consensus"] = (event.get("consensus") or "").strip()
        state["result_successes"] = len(
            [item for item in event.get("individual_results", []) if item.get("success")]
        )
        return state

    if event.get("error"):
        state["stream_error"] = str(event.get("error"))

    return state


def is_voting_canary_successful(state: dict[str, Any]) -> bool:
    successful_models = len(state.get("successful_models", set()))
    if successful_models < 2:
        return False

    if state.get("saw_result") and state.get("result_consensus"):
        return True

    return bool(state.get("saw_start") and state.get("saw_synthesizing"))


async def iter_sse_events(response) -> Any:
    buffer = ""
    async for raw_bytes in response.content.iter_any():
        if not raw_bytes:
            continue
        buffer += raw_bytes.decode("utf-8", errors="replace")
        while "\n\n" in buffer:
            chunk, buffer = buffer.split("\n\n", 1)
            data_lines = []
            for line in chunk.splitlines():
                if line.startswith("data: "):
                    data_lines.append(line[6:])
            if not data_lines:
                continue
            payload_text = "\n".join(data_lines).strip()
            if payload_text and payload_text != "[DONE]":
                yield payload_text

    trailing = buffer.strip()
    if trailing.startswith("data: "):
        payload_text = trailing[6:].strip()
        if payload_text and payload_text != "[DONE]":
            yield payload_text


# ═══════════════════════════════════════════════════════════════════════════
# 全局自动进化系统
# ═══════════════════════════════════════════════════════════════════════════

class AutoEvolutionSystem:
    """
    自动进化系统主控制器

    启动后自动运行：
    1. 定期检查信息源健康状态
    2. 自动处理反爬
    3. AI 驱动的源评估
    4. 知识图谱自动更新
    """

    _instance: Optional['AutoEvolutionSystem'] = None
    _running = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True

        # 组件
        self.anti_crawl_handler = None
        self.evolution_scheduler = None
        self.ai_brain = None

        # 配置
        self.check_interval = 1800  # 30分钟检查一次
        self.evolution_interval = 3600  # 1小时运行一次进化
        self.log_health_interval = int(os.environ.get("LOG_HEALTH_INTERVAL", "60"))
        self.log_analysis_interval = int(os.environ.get("LOG_ANALYSIS_INTERVAL", "900"))
        self.testing_interval = int(os.environ.get("SELF_TEST_INTERVAL", "600"))
        self.collection_health_interval = int(os.environ.get("COLLECTION_HEALTH_INTERVAL", "120"))
        self.source_plan_review_interval = int(os.environ.get("SOURCE_PLAN_REVIEW_INTERVAL", "300"))

        # 任务
        self._tasks = []
        self._last_log_health = None
        self._last_log_analysis = None
        self._last_self_test = None
        self._last_evolution_cycle = None
        self._last_collection_health = None
        self._last_source_plan_review = None
        self._last_source_plan_quality = None

    async def start(self, llm_client=None):
        """启动自动进化系统"""
        if self._running:
            logger.warning("Auto evolution system already running")
            return

        logger.info("=" * 50)
        logger.info("Starting Auto Evolution System...")
        logger.info("=" * 50)

        self._running = True
        self.llm_client = llm_client

        # 1. 初始化反爬处理器
        try:
            from feeds.anti_crawl import AutomaticAntiCrawlHandler, AntiCrawlScheduler
            self.anti_crawl_handler = AutomaticAntiCrawlHandler()
            self.anti_crawl_scheduler = AntiCrawlScheduler(
                get_db,
                check_interval=self.check_interval
            )
            logger.info("[OK] Anti-crawl system loaded")
        except Exception as e:
            logger.error(f"Failed to load anti-crawl: {e}")

        # 2. 初始化 AI 大脑
        try:
            from feeds.ai_brain import get_ai_brain
            self.ai_brain = get_ai_brain(llm_client)
            logger.info("[OK] AI Decision Brain loaded")
        except Exception as e:
            logger.error(f"Failed to load AI brain: {e}")

        # 3. 初始化进化调度器
        try:
            from pipeline.evolution_scheduler import SchedulerTask, SchedulerConfig
            config = SchedulerConfig(
                enable_auto_evolution=True,
                enable_auto_discovery=True,
                source_evaluation_interval=1  # 每天评估
            )
            # 使用工厂函数而非直接实例
            self.evolution_scheduler = SchedulerTask(get_db, config)
            logger.info("[OK] Evolution scheduler loaded")
        except Exception as e:
            logger.error(f"Failed to load scheduler: {e}")

        # 4. 初始化日志分析调度器
        try:
            from pipeline.log_analysis_scheduler import get_log_analysis_scheduler
            self.log_scheduler = get_log_analysis_scheduler()
            logger.info("[OK] Log analysis scheduler loaded")
        except Exception as e:
            logger.error(f"Failed to load log scheduler: {e}")
            self.log_scheduler = None

        # 5. 启动后台任务
        self._tasks.append(asyncio.create_task(self._run_evolution_loop()))
        self._tasks.append(asyncio.create_task(self._run_log_monitor_loop()))
        self._tasks.append(asyncio.create_task(self._run_self_test_loop()))
        self._tasks.append(asyncio.create_task(self._run_collection_health_loop()))
        self._tasks.append(asyncio.create_task(self._run_source_plan_review_loop()))
        self._tasks.append(asyncio.create_task(self._run_initial_observability_warmup()))

        logger.info("=" * 50)
        logger.info("Auto Evolution System started successfully!")
        logger.info("System will automatically:")
        logger.info("  - Monitor and handle anti-crawl issues")
        logger.info("  - Evaluate source performance with AI")
        logger.info("  - Optimize source strategies")
        logger.info("  - Analyze logs and generate insights")
        logger.info("  - Run periodic self-tests")
        logger.info("  - Discover new sources")
        logger.info("=" * 50)

    async def stop(self):
        """停止自动进化系统"""
        self._running = False

        if hasattr(self, 'anti_crawl_scheduler'):
            await self.anti_crawl_scheduler.stop()

        for task in self._tasks:
            task.cancel()
        for task in self._tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass
        self._tasks.clear()

        logger.info("Auto evolution system stopped")

    async def _run_evolution_loop(self):
        """运行进化主循环"""
        while self._running:
            try:
                await self._run_evolution_cycle()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Evolution cycle error: {e}", exc_info=True)

            await asyncio.sleep(self.evolution_interval)

    async def _run_log_monitor_loop(self):
        """Run minute-level log health checks and periodic deep analysis."""
        last_analysis_at = 0.0
        while self._running:
            try:
                if self.log_scheduler:
                    health = await self.log_scheduler.check_and_alert()
                    self._last_log_health = health

                    now = asyncio.get_event_loop().time()
                    if now - last_analysis_at >= self.log_analysis_interval:
                        analysis = await self.log_scheduler.run_analysis()
                        self._last_log_analysis = analysis
                        last_analysis_at = now
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Log monitor loop failed: {e}", exc_info=True)

            await asyncio.sleep(self.log_health_interval)

    async def _run_self_test_loop(self):
        """Run lightweight internal smoke tests to catch regressions early."""
        while self._running:
            try:
                await self._run_self_test_once()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Self test loop failed: {e}", exc_info=True)

            await asyncio.sleep(self.testing_interval)

    async def _run_collection_health_loop(self):
        """Track whether collection is producing durable feed data."""
        while self._running:
            try:
                await self._run_collection_health_once()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Collection health loop failed: {e}", exc_info=True)

            await asyncio.sleep(self.collection_health_interval)

    async def _run_source_plan_review_loop(self):
        """Run scheduled source-plan reviews based on review cadence."""
        while self._running:
            try:
                await self._run_source_plan_review_once()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Source plan review loop failed: {e}", exc_info=True)

            await asyncio.sleep(self.source_plan_review_interval)

    async def _run_initial_observability_warmup(self):
        """Seed initial monitoring data without blocking API startup."""
        try:
            await asyncio.sleep(3)
            if self.log_scheduler:
                self._last_log_health = await self.log_scheduler.check_and_alert()
                self._last_log_analysis = await self.log_scheduler.run_analysis()
            await self._run_self_test_once()
            await self._run_collection_health_once()
            await self._run_source_plan_review_once()
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Initial observability warmup failed: {e}", exc_info=True)

    async def _run_self_test_once(self):
        checks = []
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120)) as session:
            for path in ("/health", "/api/sources", "/api/evolution/status"):
                try:
                    async with session.get(f"http://localhost:8000{path}") as resp:
                        checks.append({
                            "id": path,
                            "name": path,
                            "path": path,
                            "status": resp.status,
                            "ok": resp.status == 200,
                        })
                except Exception as exc:
                    checks.append({
                        "id": path,
                        "name": path,
                        "path": path,
                        "status": 0,
                        "ok": False,
                        "error": str(exc),
                    })

            provider_status = None
            try:
                async with session.get("http://localhost:8000/api/llm/providers") as resp:
                    provider_status = resp.status
                    body = await resp.json()
                    qwen_enabled = any(
                        item.get("provider") == "qwen" and item.get("enabled")
                        for item in body
                    )
                    checks.append({
                        "id": "/api/llm/providers",
                        "name": "LLM providers",
                        "path": "/api/llm/providers",
                        "status": resp.status,
                        "ok": resp.status == 200,
                        "qwen_enabled": qwen_enabled,
                    })
                    if qwen_enabled:
                        checks.append(await self._run_single_chat_canary(session))
                        checks.append(await self._run_voting_canary(session))
            except Exception as exc:
                checks.append({
                    "id": "/api/llm/providers",
                    "name": "LLM providers",
                    "path": "/api/llm/providers",
                    "status": provider_status or 0,
                    "ok": False,
                    "error": str(exc),
                })

            checks.append(await self._run_frontend_page_check(session, "/chat"))
            checks.append(await self._run_browser_ui_check("/chat", "智能对话"))
            checks.append(await self._run_browser_ui_check("/evolution", "进化大脑"))

        self._last_self_test = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": checks,
            "healthy": all(item.get("ok") for item in checks),
        }

        issue = build_self_test_issue(self._last_self_test)
        from feeds.task_classifier import ClassificationResult
        from feeds.task_processor import get_task_processor
        from memory.runtime import record_task_memory, upsert_procedural_memory
        from tasks.runtime import (
            build_context_task_defaults,
            create_context_artifact,
            ensure_task_context,
            record_context_event,
        )

        async with get_db_context() as db:
            context = await ensure_task_context(
                db,
                context_type="evolution",
                owner_type="system",
                owner_id="auto-evolution:self-test",
                title="Auto Evolution Self-Test",
                goal="Continuously verify critical runtime paths and capture structured evidence.",
            )
            await create_context_artifact(
                db,
                context=context,
                task=None,
                artifact_type="report",
                title="Self-test snapshot",
                summary="healthy" if self._last_self_test["healthy"] else "degraded",
                payload=self._last_self_test,
            )
            await record_context_event(
                db,
                context=context,
                task=None,
                event_type="self_test_snapshot",
                action="observe",
                result="success" if self._last_self_test["healthy"] else "failed",
                reason="periodic self-test run",
                payload={
                    "healthy": self._last_self_test["healthy"],
                    "check_count": len(checks),
                },
            )
            await record_task_memory(
                db,
                context=context,
                task=None,
                memory_kind="checkpoint",
                title="Self-test checkpoint",
                summary="healthy" if self._last_self_test["healthy"] else "degraded",
                content=json.dumps(self._last_self_test, ensure_ascii=False),
                payload={
                    "problem_type": "system_evolution",
                    "thinking_framework": "systems_diagnosis",
                },
            )
            await upsert_procedural_memory(
                db,
                memory_key="evolution:self_test_cycle:v1",
                name="Evolution self-test cycle",
                problem_type="system_evolution",
                thinking_framework="systems_diagnosis",
                method_name="periodic_self_test_with_ui_probe",
                applicability="Use for continuous runtime validation of API, frontend, and voting critical paths.",
                procedure="Run health probes, provider checks, voting canary, frontend checks, and browser UI probes. Persist snapshots and raise structured tasks on failure.",
                effectiveness_score=1.0 if self._last_self_test["healthy"] else 0.6,
                validation_status="validated" if self._last_self_test["healthy"] else "candidate",
                source_kind="runtime",
                source_ref="auto-evolution:self-test",
                payload={
                    "check_count": len(checks),
                    "healthy": self._last_self_test["healthy"],
                },
            )

            if issue:
                processor = get_task_processor(db)
                classification = ClassificationResult(
                    priority=issue["priority"],
                    category=issue["category"],
                    auto_processible=issue["auto_processible"],
                    title=issue["title"],
                    description=issue["description"],
                    source_type=issue["source_type"],
                    source_id=issue["source_id"],
                    source_data=issue["source_data"],
                    **build_context_task_defaults(context=context),
                )
                task = await processor.create_task(classification)
                if getattr(task, "_was_created", True):
                    await processor.process(task)

    async def _run_frontend_page_check(self, session, path: str):
        url = f"http://127.0.0.1:3000{path}"
        error_markers = (
            "Server Error",
            "Cannot find module",
            "PageNotFoundError",
            "TypeError:",
            "webpack-runtime",
        )

        try:
            async with session.get(url) as resp:
                body = await resp.text()
                has_error_marker = any(marker in body for marker in error_markers)
                return {
                    "id": f"frontend:{path}",
                    "name": f"Frontend page {path}",
                    "path": path,
                    "status": resp.status,
                    "ok": resp.status == 200 and not has_error_marker,
                    "error": None if resp.status == 200 and not has_error_marker else "frontend page unhealthy",
                }
        except Exception as exc:
            return {
                "id": f"frontend:{path}",
                "name": f"Frontend page {path}",
                "path": path,
                "status": 0,
                "ok": False,
                "error": str(exc),
            }

    async def _run_browser_ui_check(self, path: str, expected_text: str):
        url = f"http://127.0.0.1:3000{path}"
        if not UI_SMOKE_SCRIPT.exists():
            return {
                "id": f"ui-browser:{path}",
                "name": f"Browser UI check {path}",
                "path": path,
                "status": 0,
                "ok": False,
                "error": f"missing script: {UI_SMOKE_SCRIPT}",
            }

        try:
            process = await asyncio.create_subprocess_exec(
                "node",
                str(UI_SMOKE_SCRIPT),
                "--url",
                url,
                "--expect",
                expected_text,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=45)
        except asyncio.TimeoutError:
            return {
                "id": f"ui-browser:{path}",
                "name": f"Browser UI check {path}",
                "path": path,
                "status": 0,
                "ok": False,
                "error": "browser UI check timed out",
            }
        except Exception as exc:
            return {
                "id": f"ui-browser:{path}",
                "name": f"Browser UI check {path}",
                "path": path,
                "status": 0,
                "ok": False,
                "error": str(exc),
            }

        stderr_text = stderr.decode("utf-8", errors="replace").strip()
        stdout_text = stdout.decode("utf-8", errors="replace").strip()
        if process.returncode != 0:
            return {
                "id": f"ui-browser:{path}",
                "name": f"Browser UI check {path}",
                "path": path,
                "status": process.returncode,
                "ok": False,
                "error": stderr_text or stdout_text or "browser UI check failed",
            }

        try:
            payload = json.loads(stdout_text)
        except json.JSONDecodeError:
            return {
                "id": f"ui-browser:{path}",
                "name": f"Browser UI check {path}",
                "path": path,
                "status": process.returncode,
                "ok": False,
                "error": f"invalid browser probe output: {stdout_text[:200]}",
            }

        return {
            "id": f"ui-browser:{path}",
            "name": f"Browser UI check {path}",
            "path": path,
            "status": payload.get("status", 0),
            "ok": bool(payload.get("ok")),
            "error": payload.get("error") or (stderr_text or None),
            "details": payload,
        }

    async def _run_single_chat_canary(self, session):
        payload = {
            "message": "[self-test] Reply in exactly five English words describing this project.",
            "use_voting": False,
            "use_rag": False,
            "enable_search": False,
            "enable_thinking": False,
            "kb_ids": [],
        }
        conversation_id = None
        selected_model = ""
        start_time = time.time()

        try:
            async with session.post(
                "http://localhost:8000/api/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=90),
            ) as resp:
                error = ""
                saw_content = False
                first_content_seconds = None
                async for data in iter_sse_events(resp):
                    try:
                        event = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    if event.get("conversation_id"):
                        conversation_id = event.get("conversation_id")
                    brain_plan = event.get("brain_plan") or {}
                    if not selected_model:
                        if event.get("model"):
                            selected_model = str(event.get("model"))
                        elif isinstance(brain_plan, dict):
                            models = list(brain_plan.get("selected_models") or [])
                            if models:
                                selected_model = str(models[0])
                    if event.get("error"):
                        error = str(event.get("error"))
                        break
                    if (event.get("content") or "").strip():
                        saw_content = True
                        first_content_seconds = round(time.time() - start_time, 2)
                        break

                total_seconds = round(time.time() - start_time, 2)
                performance_warning = bool(
                    (first_content_seconds is not None and first_content_seconds > 8.0)
                    or total_seconds > 30.0
                )

                return {
                    "id": "chat-single-canary",
                    "name": "Single chat canary",
                    "path": "/api/chat",
                    "status": resp.status,
                    "ok": resp.status == 200 and saw_content and not error and not performance_warning,
                    "error": None if resp.status == 200 and saw_content and not error and not performance_warning else (
                        f"slow response: first_content={first_content_seconds}s total={total_seconds}s"
                        if performance_warning and not error
                        else error or "no assistant content returned"
                    ),
                    "model": selected_model,
                    "first_content_seconds": first_content_seconds,
                    "total_seconds": total_seconds,
                    "performance_warning": performance_warning,
                }
        except Exception as exc:
            return {
                "id": "chat-single-canary",
                "name": "Single chat canary",
                "path": "/api/chat",
                "status": 0,
                "ok": False,
                "error": str(exc) or exc.__class__.__name__,
                "model": selected_model,
                "performance_warning": False,
            }
        finally:
            if conversation_id:
                await self._cleanup_test_conversation(conversation_id)

    async def _run_voting_canary(self, session):
        payload = {
            "message": (
                "[self-test] 你正在为一款家庭场景的本地 AI 中枢做方向取舍。"
                "约束条件是预算有限、必须保护用户隐私、还要尽快落地。"
                "请在“优先极致本地隐私”“优先最低硬件成本”“优先多模态交互体验”三者中做取舍，"
                "并明确给出：一句话判断、关键分歧、建议动作。"
            ),
            "use_voting": True,
            "use_rag": False,
            "enable_search": False,
            "enable_thinking": False,
            "voting_models": ["MiniMax-M2.5", "deepseek-v3.2"],
        }
        state = {
            "saw_start": False,
            "participants": [],
            "successful_models": set(),
            "failed_models": {},
            "saw_synthesizing": False,
            "saw_synthesis_content": False,
            "saw_result": False,
            "result_consensus": "",
            "result_successes": 0,
            "stream_error": "",
        }
        conversation_id = None
        start_time = time.time()

        try:
            async with session.post(
                "http://localhost:8000/api/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=90),
            ) as resp:
                error = ""
                async for data in iter_sse_events(resp):
                    try:
                        event = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    if event.get("conversation_id"):
                        conversation_id = event.get("conversation_id")
                    state = update_voting_canary_state(state, event)
                    if is_voting_canary_successful(state):
                        total_seconds = round(time.time() - start_time, 2)
                        performance_warning = total_seconds > 45.0
                        return {
                            "id": "chat-voting-canary",
                            "name": "Voting canary",
                            "path": "/api/chat",
                            "status": resp.status,
                            "ok": not performance_warning,
                            "error": f"slow response: total={total_seconds}s" if performance_warning else None,
                            "participants": state["participants"],
                            "successful_models": sorted(state["successful_models"]),
                            "total_seconds": total_seconds,
                            "performance_warning": performance_warning,
                        }
                    if event.get("error"):
                        error = str(event.get("error"))

                total_seconds = round(time.time() - start_time, 2)
                return {
                    "id": "chat-voting-canary",
                    "name": "Voting canary",
                    "path": "/api/chat",
                    "status": resp.status,
                    "ok": False,
                    "error": error or self._build_voting_canary_failure(state),
                    "participants": state["participants"],
                    "successful_models": sorted(state["successful_models"]),
                    "total_seconds": total_seconds,
                    "performance_warning": False,
                }
        except Exception as exc:
            return {
                "id": "chat-voting-canary",
                "name": "Voting canary",
                "path": "/api/chat",
                "status": 0,
                "ok": False,
                "error": str(exc) or exc.__class__.__name__,
                "performance_warning": False,
            }
        finally:
            if conversation_id:
                await self._cleanup_test_conversation(conversation_id)

    def _build_voting_canary_failure(self, state: dict[str, Any]) -> str:
        failed_models = state.get("failed_models") or {}
        parts = []
        if state.get("participants"):
            parts.append(f"participants={','.join(state['participants'])}")
        if state.get("successful_models"):
            parts.append(f"successful={','.join(sorted(state['successful_models']))}")
        if failed_models:
            parts.append(
                "failed="
                + ",".join(f"{model}:{reason}" for model, reason in sorted(failed_models.items()))
            )
        if state.get("stream_error"):
            parts.append(f"stream_error={state['stream_error']}")
        if not state.get("saw_start"):
            parts.append("missing=voting_start")
        elif len(state.get("successful_models", set())) < 2:
            parts.append("missing=two_successful_models")
        elif not state.get("saw_synthesizing"):
            parts.append("missing=voting_synthesizing")
        return "; ".join(parts) or "voting canary did not reach synthesis stage"

    async def _cleanup_test_conversation(self, conversation_id: str):
        from uuid import UUID
        from sqlalchemy import delete
        from db import Conversation

        try:
            async with get_db_context() as db:
                await db.execute(
                    delete(Conversation).where(
                        Conversation.id == UUID(conversation_id),
                    )
                )
                await db.commit()
        except Exception as exc:
            logger.warning("Failed to cleanup self-test conversation %s: %s", conversation_id, exc)

    async def _run_collection_health_once(self):
        from feeds.collection_health import (
            build_collection_health_issue,
            collect_collection_health_snapshot,
        )
        from feeds.task_classifier import ClassificationResult
        from feeds.task_processor import get_task_processor
        from memory.runtime import record_task_memory, upsert_procedural_memory

        async with get_db_context() as db:
            snapshot = await collect_collection_health_snapshot(db)
            self._last_collection_health = snapshot
            from tasks.runtime import (
                build_context_task_defaults,
                create_context_artifact,
                ensure_task_context,
                record_context_event,
            )

            context = await ensure_task_context(
                db,
                context_type="source_intelligence",
                owner_type="system",
                owner_id="feed-collection:health",
                title="Feed Collection Health",
                goal="Track collection degradation, pending backlogs, and recovery signals for the information brain.",
            )
            await create_context_artifact(
                db,
                context=context,
                task=None,
                artifact_type="report",
                title="Collection health snapshot",
                summary=(snapshot.get("summary") or {}).get("status", "unknown"),
                payload=snapshot,
            )
            await record_context_event(
                db,
                context=context,
                task=None,
                event_type="collection_health_snapshot",
                action="observe",
                result="success",
                reason="periodic collection health run",
                payload={
                    "status": (snapshot.get("summary") or {}).get("status", "unknown"),
                    "pending_sources_1h": snapshot.get("pending_sources_1h", []),
                    "error_sources_24h": snapshot.get("error_sources_24h", []),
                },
            )
            await record_task_memory(
                db,
                context=context,
                task=None,
                memory_kind="checkpoint",
                title="Collection health checkpoint",
                summary=(snapshot.get("summary") or {}).get("status", "unknown"),
                content=json.dumps(snapshot, ensure_ascii=False),
                payload={
                    "problem_type": "source_intelligence",
                    "thinking_framework": "source_intelligence",
                },
            )
            await upsert_procedural_memory(
                db,
                memory_key="source_intelligence:collection_health:v1",
                name="Collection health review loop",
                problem_type="source_intelligence",
                thinking_framework="source_intelligence",
                method_name="periodic_collection_health_snapshot",
                applicability="Use for ongoing monitoring of durable feed collection, backlog detection, and source-quality drift.",
                procedure="Collect durable ingest and feed-item counts, identify pending/error sources, persist snapshots, and generate structured remediation tasks when health degrades.",
                effectiveness_score=1.0 if (snapshot.get("summary") or {}).get("status") == "healthy" else 0.6,
                validation_status="validated" if (snapshot.get("summary") or {}).get("status") == "healthy" else "candidate",
                source_kind="runtime",
                source_ref="feed-collection:health",
                payload={
                    "status": (snapshot.get("summary") or {}).get("status", "unknown"),
                    "pending_sources_1h": snapshot.get("pending_sources_1h", []),
                    "error_sources_24h": snapshot.get("error_sources_24h", []),
                },
            )

            issue = build_collection_health_issue(snapshot)
            if issue:
                processor = get_task_processor(db)
                classification = ClassificationResult(
                    priority=issue["priority"],
                    category=issue["category"],
                    auto_processible=issue["auto_processible"],
                    title=issue["title"],
                    description=issue["description"],
                    source_type=issue["source_type"],
                    source_id=issue["source_id"],
                    source_data=issue["source_data"],
                    **build_context_task_defaults(
                        context=context,
                        assigned_brain="source-intelligence-brain",
                    ),
                )
                task = await processor.create_task(classification)
                if getattr(task, "_was_created", True):
                    await processor.process(task)

    async def _run_source_plan_review_once(self):
        from feeds.task_classifier import ClassificationResult
        from feeds.task_processor import get_task_processor
        from memory.runtime import record_task_memory, upsert_procedural_memory
        from tasks.runtime import create_context_artifact, ensure_task_context, record_context_event
        from tasks.runtime import build_context_task_defaults
        from attention.policies import resolve_attention_policy

        now = datetime.now(timezone.utc)
        due_plans: list[dict[str, Any]] = []
        async with get_db_context() as db:
            result = await db.execute(select(SourcePlan).where(SourcePlan.status == "active"))
            plans = result.scalars().all()

            for plan in plans:
                extra = dict(plan.extra or {})
                next_due_raw = extra.get("next_review_due_at")
                next_due = None
                if isinstance(next_due_raw, str):
                    try:
                        next_due = datetime.fromisoformat(next_due_raw.replace("Z", "+00:00"))
                    except ValueError:
                        next_due = None
                if next_due is None:
                    next_due = plan.updated_at or plan.created_at or now
                if next_due <= now:
                    due_plans.append(
                        {
                            "id": str(plan.id),
                            "topic": plan.topic,
                            "current_version": int(plan.current_version or 1),
                            "latest_version": int(plan.latest_version or 1),
                            "review_cadence_days": int(plan.review_cadence_days or 14),
                        }
                    )

        refreshed: list[dict[str, Any]] = []
        failures: list[dict[str, Any]] = []

        if due_plans:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120)) as session:
                for plan in due_plans:
                    try:
                        async with session.post(
                            f"http://127.0.0.1:8000/api/sources/plans/{plan['id']}/refresh?limit=12&trigger_type=scheduled_refresh"
                        ) as response:
                            body = await response.json()
                            if response.status != 200:
                                failures.append(
                                    {
                                        "plan_id": plan["id"],
                                        "topic": plan["topic"],
                                        "status": response.status,
                                        "error": body,
                                    }
                                )
                                continue
                            refreshed.append(
                                {
                                    "plan_id": plan["id"],
                                    "topic": plan["topic"],
                                    "review_status": body.get("review_status"),
                                    "current_version": body.get("current_version"),
                                    "latest_version": body.get("latest_version"),
                                    "next_review_due_at": body.get("next_review_due_at"),
                                }
                            )
                    except Exception as exc:
                        failures.append(
                            {
                                "plan_id": plan["id"],
                                "topic": plan["topic"],
                                "error": str(exc),
                            }
                        )

        snapshot = {
            "timestamp": now.isoformat(),
            "due_count": len(due_plans),
            "refreshed": refreshed,
            "failures": failures,
            "healthy": not failures,
        }

        quality_findings: list[dict[str, Any]] = []
        async with get_db_context() as db:
            result = await db.execute(
                select(SourcePlan)
                .where(SourcePlan.status == "active")
                .options(selectinload(SourcePlan.items))
            )
            reviewed_plans = result.scalars().all()
            for plan in reviewed_plans:
                policy = await resolve_attention_policy(db, plan.focus)
                plan_extra = dict(plan.extra or {})
                policy_meta = dict(plan_extra.get("attention_policy", {}) or {})
                bucket_counts: dict[str, int] = {}
                gate_status_counts: dict[str, int] = {}
                item_types: list[str] = []
                for item in list(plan.items or []):
                    evidence = dict(item.evidence or {})
                    item_types.append(str(item.item_type or "domain"))
                    bucket = str(evidence.get("object_bucket", "") or "")
                    if bucket:
                        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
                    gate_status = str(evidence.get("gate_status", "") or "")
                    if gate_status:
                        gate_status_counts[gate_status] = gate_status_counts.get(gate_status, 0) + 1

                quality = evaluate_source_plan_quality_snapshot(
                    topic=plan.topic,
                    focus=plan.focus,
                    review_status=plan.review_status,
                    policy_version=int(policy_meta.get("policy_version", 0) or 0),
                    live_policy_version=int(policy.current_version or 0),
                    item_types=item_types,
                    bucket_counts=bucket_counts,
                    gate_status_counts=gate_status_counts,
                    gate_policy={
                        **dict(policy.gate_policy or {}),
                        "minimum_distinct_buckets": int(
                            dict(policy.candidate_mix_policy or {}).get("minimum_distinct_buckets", 1) or 1
                        ),
                    },
                )
                quality_findings.append(
                    {
                        "plan_id": str(plan.id),
                        "topic": plan.topic,
                        "focus": plan.focus,
                        **quality,
                    }
                )

        quality_issues = [finding for finding in quality_findings if finding.get("status") != "healthy"]
        quality_snapshot = {
            "timestamp": now.isoformat(),
            "plan_count": len(quality_findings),
            "issue_count": len(quality_issues),
            "quality_findings": quality_findings,
        }
        self._last_source_plan_quality = quality_snapshot

        snapshot["quality_findings"] = quality_issues
        snapshot["healthy"] = not failures and not quality_issues
        if failures:
            snapshot["review_state"] = "failed"
        elif quality_issues:
            snapshot["review_state"] = "degraded"
        else:
            snapshot["review_state"] = "healthy"
        self._last_source_plan_review = snapshot

        async with get_db_context() as db:
            context = await ensure_task_context(
                db,
                context_type="source_intelligence",
                owner_type="system",
                owner_id="source-plan:review-daemon",
                title="Source Plan Review Daemon",
                goal="Continuously refresh due source plans and preserve versioned review history.",
            )
            await create_context_artifact(
                db,
                context=context,
                task=None,
                artifact_type="report",
                title="Source plan review snapshot",
                summary=snapshot["review_state"],
                payload=snapshot,
            )
            await record_context_event(
                db,
                context=context,
                task=None,
                event_type="source_plan_review",
                action="observe",
                result="failed" if failures else ("warning" if quality_issues else "success"),
                reason="periodic source-plan review cycle",
                payload={
                    "due_count": snapshot["due_count"],
                    "refreshed_count": len(refreshed),
                    "failure_count": len(failures),
                    "quality_issue_count": len(quality_issues),
                },
            )
            await record_task_memory(
                db,
                context=context,
                task=None,
                memory_kind="checkpoint",
                title="Source plan review checkpoint",
                summary=snapshot["review_state"],
                content=json.dumps(snapshot, ensure_ascii=False),
                payload={
                    "problem_type": "source_intelligence",
                    "thinking_framework": "source_intelligence",
                },
            )
            await create_context_artifact(
                db,
                context=context,
                task=None,
                artifact_type="report",
                title="Source plan quality snapshot",
                summary="healthy" if not quality_issues else "degraded",
                payload=quality_snapshot,
            )
            await upsert_procedural_memory(
                db,
                memory_key="source_intelligence:scheduled_plan_review:v1",
                name="Scheduled source plan review",
                problem_type="source_intelligence",
                thinking_framework="source_intelligence",
                method_name="scheduled_source_plan_review",
                applicability="Use for recurring source-plan review and calibration.",
                procedure="Scan active source plans for due review windows, trigger scheduled refresh, preserve versioned deltas, and persist review outcomes into runtime memory.",
                effectiveness_score=1.0 if snapshot["healthy"] else 0.6,
                validation_status="validated" if snapshot["healthy"] else "candidate",
                source_kind="runtime",
                source_ref="auto-evolution:source-plan-review",
                payload={
                    "due_count": snapshot["due_count"],
                    "refreshed_count": len(refreshed),
                    "failure_count": len(failures),
                    "quality_issue_count": len(quality_issues),
                    "review_state": snapshot["review_state"],
                },
            )

            processor = get_task_processor(db)
            for issue in build_source_plan_review_issues(snapshot):
                classification = ClassificationResult(
                    priority=issue["priority"],
                    category=issue["category"],
                    auto_processible=issue["auto_processible"],
                    title=issue["title"],
                    description=issue["description"],
                    source_type=issue["source_type"],
                    source_id=issue["source_id"],
                    source_data=issue["source_data"],
                    **build_context_task_defaults(
                        context=context,
                        assigned_brain="source-intelligence-brain",
                    ),
                )
                task = await processor.create_task(classification)
                if task.auto_processible and (
                    getattr(task, "_was_created", True) or getattr(task, "_was_deduplicated", False)
                ):
                    await processor.process(task)
            for issue in build_source_plan_quality_issues(quality_snapshot):
                classification = ClassificationResult(
                    priority=issue["priority"],
                    category=issue["category"],
                    auto_processible=issue["auto_processible"],
                    title=issue["title"],
                    description=issue["description"],
                    source_type=issue["source_type"],
                    source_id=issue["source_id"],
                    source_data=issue["source_data"],
                    **build_context_task_defaults(
                        context=context,
                        assigned_brain="source-intelligence-brain",
                    ),
                )
                task = await processor.create_task(classification)
                if task.auto_processible and (
                    getattr(task, "_was_created", True) or getattr(task, "_was_deduplicated", False)
                ):
                    await processor.process(task)

    async def _run_evolution_cycle(self):
        """运行一次进化周期"""
        logger.info("Running evolution cycle...")
        self._last_evolution_cycle = datetime.now(timezone.utc).isoformat()

        # 1. 反爬检查
        if hasattr(self, 'anti_crawl_scheduler'):
            try:
                await self.anti_crawl_scheduler._check_all_sources()
            except Exception as e:
                logger.error(f"Anti-crawl check failed: {e}")

        # 2. AI 驱动的源评估
        if self.ai_brain:
            try:
                async for db in get_db():
                    from feeds.ai_brain import AIEvolutionEngine
                    engine = AIEvolutionEngine(db, self.llm_client)
                    result = await engine.evolve_all_with_ai()
                    logger.info(f"AI evolution: {result.get('total', 0)} sources evaluated")
                    break
            except Exception as e:
                logger.error(f"AI evolution failed: {e}")

        # 3. 知识质量评估
        try:
            async for db in get_db():
                from pipeline.evolution_scheduler import EvolutionScheduler
                scheduler = EvolutionScheduler(db)
                result = await scheduler.run_knowledge_evaluation()
                logger.info(f"Knowledge evaluation: {result.get('total_tracked', 0)} items")
                break
        except Exception as e:
            logger.error(f"Knowledge evaluation failed: {e}")

        logger.info("Evolution cycle completed")

    async def trigger_now(self):
        """手动触发立即执行"""
        await self._run_evolution_cycle()

    def get_status(self) -> dict:
        """获取系统状态"""
        self_test = self._last_self_test or {}
        collection_health = self._last_collection_health or {}
        log_health = self._last_log_health or {}
        source_plan_review = self._last_source_plan_review or {}
        source_plan_quality = self._last_source_plan_quality or {}

        health = "healthy"
        issues: list[str] = []

        if self._running:
            if self_test and not self_test.get("healthy", True):
                health = "degraded"
                issues.append("self_test_failed")
            collection_summary = collection_health.get("summary") or {}
            if collection_summary.get("status") == "unhealthy":
                health = "degraded"
                issues.append("collection_unhealthy")
            if log_health.get("critical_errors", 0) > 0:
                health = "degraded"
                issues.append("critical_log_errors")
            review_failures = list(source_plan_review.get("failures", []) or [])
            if review_failures:
                health = "degraded"
                issues.append("source_plan_review_failed")
            quality_count = int(source_plan_quality.get("issue_count", 0) or 0)
            if quality_count > 0:
                health = "degraded"
                issues.append("source_plan_quality_degraded")
        else:
            health = "stopped"

        return {
            "running": self._running,
            "health": health,
            "issues": issues,
            "components": {
                "anti_crawl": self.anti_crawl_handler is not None,
                "ai_brain": self.ai_brain is not None,
                "scheduler": self.evolution_scheduler is not None,
                "log_monitor": self.log_scheduler is not None,
                "self_test": True,
                "collection_monitor": True,
                "source_plan_review": True,
                "source_plan_quality": True,
            },
            "intervals": {
                "check_interval": self.check_interval,
                "evolution_interval": self.evolution_interval,
                "log_health_interval": self.log_health_interval,
                "log_analysis_interval": self.log_analysis_interval,
                "testing_interval": self.testing_interval,
                "collection_health_interval": self.collection_health_interval,
                "source_plan_review_interval": self.source_plan_review_interval,
            },
            "last_results": {
                "evolution_cycle": self._last_evolution_cycle,
                "log_health": log_health,
                "log_analysis": self._last_log_analysis,
                "self_test": self_test,
                "collection_health": collection_health,
                "source_plan_review": self._last_source_plan_review,
                "source_plan_quality": self._last_source_plan_quality,
            },
        }


# ═══════════════════════════════════════════════════════════════════════════
# 便捷函数
# ═══════════════════════════════════════════════════════════════════════════

_auto_system: Optional[AutoEvolutionSystem] = None


def get_auto_evolution_system() -> AutoEvolutionSystem:
    """获取自动进化系统实例"""
    global _auto_system
    if _auto_system is None:
        _auto_system = AutoEvolutionSystem()
    return _auto_system


async def start_auto_evolution(llm_client=None):
    """启动自动进化系统（便捷函数）"""
    system = get_auto_evolution_system()
    await system.start(llm_client)
    return system


async def stop_auto_evolution():
    """停止自动进化系统"""
    system = get_auto_evolution_system()
    await system.stop()


async def trigger_evolution_now():
    """立即触发一次进化"""
    system = get_auto_evolution_system()
    await system.trigger_now()
