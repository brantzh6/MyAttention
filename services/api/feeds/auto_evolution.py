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
from typing import Any, Optional
from datetime import datetime, timezone
from pathlib import Path
import aiohttp

from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db, get_db_context

logger = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parents[3]
UI_SMOKE_SCRIPT = REPO_ROOT / "services" / "web" / "scripts" / "ui-smoke-check.mjs"


def build_self_test_issue(snapshot: dict | None) -> dict | None:
    snapshot = snapshot or {}
    if snapshot.get("healthy", True):
        return None

    checks = snapshot.get("checks", [])
    failed_checks = [check for check in checks if not check.get("ok")]
    if not failed_checks:
        return None

    critical_ids = {"/health", "chat-voting-canary", "frontend:/chat", "ui-browser:/chat"}
    is_critical = any(check.get("id") in critical_ids for check in failed_checks)
    priority = 0 if is_critical else 1
    health = "critical" if is_critical else "warning"

    failed_names = [check.get("name") or check.get("id") or "unknown" for check in failed_checks]
    title = "[self-test] critical path failed" if is_critical else "[self-test] checks failed"
    description = "Failed checks: " + ", ".join(failed_names[:5])

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
                "total_count": len(checks),
            },
            "checks": failed_checks,
        },
    }


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

    return bool(
        state.get("saw_start")
        and state.get("saw_synthesizing")
        and state.get("saw_synthesis_content")
    )


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

        # 任务
        self._tasks = []
        self._last_log_health = None
        self._last_log_analysis = None
        self._last_self_test = None
        self._last_evolution_cycle = None
        self._last_collection_health = None

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

    async def _run_initial_observability_warmup(self):
        """Seed initial monitoring data without blocking API startup."""
        try:
            await asyncio.sleep(3)
            if self.log_scheduler:
                self._last_log_health = await self.log_scheduler.check_and_alert()
                self._last_log_analysis = await self.log_scheduler.run_analysis()
            await self._run_self_test_once()
            await self._run_collection_health_once()
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Initial observability warmup failed: {e}", exc_info=True)

    async def _run_self_test_once(self):
        checks = []
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as session:
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
        if issue:
            from feeds.task_classifier import ClassificationResult
            from feeds.task_processor import get_task_processor

            async with get_db_context() as db:
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

    async def _run_voting_canary(self, session):
        payload = {
            "message": "1+1等于几？请只回答结果。",
            "use_voting": True,
            "use_rag": False,
            "enable_search": False,
            "voting_models": ["qwen3.5-plus", "deepseek-v3.2"],
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

        try:
            async with session.post(
                "http://localhost:8000/api/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=45),
            ) as resp:
                error = ""
                async for raw_bytes in resp.content:
                    raw_line = raw_bytes.decode("utf-8", errors="replace").strip()
                    if not raw_line.startswith("data: "):
                        continue
                    data = raw_line[6:]
                    if data == "[DONE]":
                        continue
                    try:
                        event = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    state = update_voting_canary_state(state, event)
                    if is_voting_canary_successful(state):
                        return {
                            "id": "chat-voting-canary",
                            "name": "Voting canary",
                            "path": "/api/chat",
                            "status": resp.status,
                            "ok": True,
                            "participants": state["participants"],
                            "successful_models": sorted(state["successful_models"]),
                        }
                    if event.get("error"):
                        error = str(event.get("error"))

                return {
                    "id": "chat-voting-canary",
                    "name": "Voting canary",
                    "path": "/api/chat",
                    "status": resp.status,
                    "ok": False,
                    "error": error or self._build_voting_canary_failure(state),
                    "participants": state["participants"],
                    "successful_models": sorted(state["successful_models"]),
                }
        except Exception as exc:
            return {
                "id": "chat-voting-canary",
                "name": "Voting canary",
                "path": "/api/chat",
                "status": 0,
                "ok": False,
                "error": str(exc) or exc.__class__.__name__,
            }

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
        elif not state.get("saw_synthesis_content") and not state.get("result_consensus"):
            parts.append("missing=synthesis_content")
        return "; ".join(parts) or "voting canary did not reach synthesis stage"

    async def _run_collection_health_once(self):
        from feeds.collection_health import (
            build_collection_health_issue,
            collect_collection_health_snapshot,
        )
        from feeds.task_classifier import ClassificationResult
        from feeds.task_processor import get_task_processor

        async with get_db_context() as db:
            snapshot = await collect_collection_health_snapshot(db)
            self._last_collection_health = snapshot

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
                )
                task = await processor.create_task(classification)
                if getattr(task, "_was_created", True):
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
            },
            "intervals": {
                "check_interval": self.check_interval,
                "evolution_interval": self.evolution_interval,
                "log_health_interval": self.log_health_interval,
                "log_analysis_interval": self.log_analysis_interval,
                "testing_interval": self.testing_interval,
                "collection_health_interval": self.collection_health_interval,
            },
            "last_results": {
                "evolution_cycle": self._last_evolution_cycle,
                "log_health": log_health,
                "log_analysis": self._last_log_analysis,
                "self_test": self_test,
                "collection_health": collection_health,
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
