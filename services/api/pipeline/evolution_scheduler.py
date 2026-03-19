"""
进化调度器 (Evolution Scheduler)

定时任务：
1. 每周运行源效果评估
2. 每周运行知识质量评估
3. 每月运行信息源组合优化
4. 定期自动发现新源
"""

import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Source, SourceMetrics, KnowledgeMetrics, KnowledgeEntity, KnowledgeRelation
from feeds.evolution import SourceEvolutionEngine, AdaptiveFetcher, SourceDiscovery, SourceScorecard
from knowledge.graph import KnowledgeGraphManager

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# 调度配置
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SchedulerConfig:
    """调度器配置"""

    # 评估周期（天）
    source_evaluation_interval: int = 7
    knowledge_evaluation_interval: int = 7
    source_discovery_interval: int = 30

    # 执行时间（小时，0-23）
    evaluation_hour: int = 2  # 凌晨2点
    discovery_hour: int = 3    # 凌晨3点

    # 开关
    enable_auto_evolution: bool = True
    enable_auto_discovery: bool = True

    # 阈值
    min_quality_threshold: float = 0.1
    max_sources_to_disable: int = 5


# ═══════════════════════════════════════════════════════════════════════════
# 调度任务
# ═══════════════════════════════════════════════════════════════════════════

class EvolutionScheduler:
    """进化调度器 - 定期执行优化任务"""

    def __init__(self, db: AsyncSession, config: SchedulerConfig = None):
        self.db = db
        self.config = config or SchedulerConfig()

    async def run_source_evaluation(self) -> Dict[str, Any]:
        """
        运行信息源效果评估

        任务：
        1. 收集所有启用源的效果指标
        2. 计算综合评分
        3. 执行自动优化动作
        4. 生成评估报告
        """
        logger.info("开始信息源效果评估...")

        engine = SourceEvolutionEngine(self.db)

        # 获取所有启用的源
        result = await self.db.execute(
            select(Source).where(Source.enabled == True)
        )
        sources = result.scalars().all()

        scorecards: List[SourceScorecard] = []
        evolution_results = []

        for source in sources:
            # 获取计分卡
            scorecard = await engine.get_source_scorecard(str(source.id))
            if scorecard:
                scorecards.append(scorecard)

            # 执行进化
            evolution_result = await engine.evaluate_and_evolve(str(source.id))
            evolution_results.append(evolution_result)

        # 统计结果
        disabled = sum(1 for r in evolution_results if r.action == "disable")
        optimized = sum(1 for r in evolution_results if r.success and r.action != "disable")

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_sources": len(sources),
            "scorecards": [
                {
                    "source_id": sc.source_id,
                    "source_name": sc.source_name,
                    "overall_score": sc.overall_score,
                    "read_rate": sc.read_rate,
                    "quality_rate": sc.quality_rate,
                    "recommendation": sc.recommendation
                }
                for sc in scorecards
            ],
            "actions": {
                "disabled": disabled,
                "optimized": optimized
            }
        }

        logger.info(
            f"信息源效果评估完成: 共 {len(sources)} 个源, "
            f"禁用 {disabled}, 优化 {optimized}"
        )

        return report

    async def run_adaptive_fetching(self) -> Dict[str, Any]:
        """
        运行自适应获取调整

        任务：
        1. 检查所有源的反爬状态
        2. 自动切换访问方式
        3. 禁用连续失败的源
        """
        logger.info("开始自适应获取调整...")

        adaptive_fetcher = AdaptiveFetcher(self.db)

        result = await self.db.execute(
            select(Source).where(Source.enabled == True)
        )
        sources = result.scalars().all()

        adaptations = []

        for source in sources:
            # 自适应调整
            adapt_result = await adaptive_fetcher.adapt_source(source)
            if adapt_result:
                adaptations.append(adapt_result)

            # 成功率检查
            rate_result = await adaptive_fetcher.evaluate_success_rate(source)
            if rate_result:
                adaptations.append(rate_result)

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sources_checked": len(sources),
            "adaptations": [
                {
                    "action": a.action,
                    "source_id": a.source_id,
                    "message": a.message
                }
                for a in adaptations
            ]
        }

        logger.info(f"自适应获取调整完成: 检查 {len(sources)} 个源, 调整 {len(adaptations)} 个")

        return report

    async def run_knowledge_evaluation(self) -> Dict[str, Any]:
        """
        运行知识质量评估

        任务：
        1. 评估知识库内容质量
        2. 识别高价值知识
        3. 清理低价值知识
        """
        logger.info("开始知识质量评估...")

        # 获取知识指标统计
        result = await self.db.execute(
            select(KnowledgeMetrics).order_by(KnowledgeMetrics.query_count.desc()).limit(100)
        )
        metrics = result.scalars().all()

        # 统计
        high_value = sum(1 for m in metrics if m.query_count > 10 and m.relevance_score > 0.7)
        low_value = sum(1 for m in metrics if m.query_count == 0)

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_tracked": len(metrics),
            "high_value": high_value,
            "low_value": low_value,
            "top_queried": [
                {
                    "kb_id": m.knowledge_base_id,
                    "query_count": m.query_count,
                    "relevance_score": m.relevance_score
                }
                for m in metrics[:10]
            ]
        }

        logger.info(f"知识质量评估完成: {len(metrics)} 个知识项, 高价值 {high_value}")

        return report

    async def run_source_discovery(self, keywords: List[str] = None) -> Dict[str, Any]:
        """
        运行新源发现

        任务：
        1. 基于关键词搜索新信息源
        2. AI 评估内容质量
        3. 生成推荐报告
        """
        logger.info("开始新源发现...")

        if keywords is None:
            # 默认关键词（可以从配置获取）
            keywords = [
                "AI 大模型",
                "LLM ChatGPT",
                "人工智能 投资",
                "科技 行业动态",
                "加密货币 BTC"
            ]

        discovery = SourceDiscovery(self.db)

        # 自动发现
        candidates = await discovery.auto_discover(keywords)

        # 获取待推荐的候选源
        recommended = await discovery.get_recommended_candidates()

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "keywords": keywords,
            "newly_discovered": len(candidates),
            "pending_recommendations": len(recommended),
            "candidates": [
                {
                    "id": str(c.id),
                    "name": c.name,
                    "url": c.url,
                    "ai_score": c.ai_score,
                    "authority_tier": c.authority_tier
                }
                for c in recommended[:10]
            ]
        }

        logger.info(f"新源发现完成: 发现 {len(candidates)} 个新源, 待推荐 {len(recommended)} 个")

        return report

    async def run_full_cycle(self) -> Dict[str, Any]:
        """
        运行完整进化周期

        包含所有调度任务的完整执行
        """
        logger.info("========== 开始完整进化周期 ==========")

        results = {}

        # 1. 源效果评估
        if self.config.enable_auto_evolution:
            results["source_evaluation"] = await self.run_source_evaluation()
            results["adaptive_fetching"] = await self.run_adaptive_fetching()

        # 2. 知识质量评估
        results["knowledge_evaluation"] = await self.run_knowledge_evaluation()

        # 3. 新源发现（可选）
        if self.config.enable_auto_discovery:
            results["source_discovery"] = await self.run_source_discovery()

        logger.info("========== 完整进化周期完成 ==========")

        return results


# ═══════════════════════════════════════════════════════════════════════════
# 定时任务辅助
# ═══════════════════════════════════════════════════════════════════════════

class SchedulerTask:
    """可调度的任务包装器"""

    def __init__(self, db_factory, config: SchedulerConfig = None):
        """
        Args:
            db_factory: 数据库会话工厂函数
            config: 调度配置
        """
        self.db_factory = db_factory
        self.config = config or SchedulerConfig()
        self._running = False
        self._task = None

    async def start(self):
        """启动调度器"""
        if self._running:
            logger.warning("Scheduler already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Evolution scheduler started")

    async def stop(self):
        """停止调度器"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Evolution scheduler stopped")

    async def _run_loop(self):
        """运行调度循环"""
        while self._running:
            try:
                # 获取数据库会话
                async for db in self.db_factory():
                    scheduler = EvolutionScheduler(db, self.config)

                    # 检查是否到了执行时间
                    now = datetime.now(timezone.utc)
                    hour = now.hour

                    # 每周评估（周日）
                    if now.weekday() == 0 and hour == self.config.evaluation_hour:
                        await scheduler.run_full_cycle()

                    # 每日检查（反爬自适应）
                    # 可以更频繁地运行

                    # 每月发现新源
                    if now.day == 1 and hour == self.config.discovery_hour:
                        await scheduler.run_source_discovery()

                    break  # 退出 async for 循环

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}", exc_info=True)

            # 等待一小时再检查
            await asyncio.sleep(3600)

    async def trigger_now(self):
        """手动触发立即执行"""
        async for db in self.db_factory():
            scheduler = EvolutionScheduler(db, self.config)
            result = await scheduler.run_full_cycle()
            return result


# ═══════════════════════════════════════════════════════════════════════════
# 便捷函数
# ═══════════════════════════════════════════════════════════════════════════

async def run_evolution_cycle(db: AsyncSession) -> Dict[str, Any]:
    """运行一次完整的进化周期（单次调用）"""
    scheduler = EvolutionScheduler(db)
    return await scheduler.run_full_cycle()


async def evaluate_source(db: AsyncSession, source_id: str) -> Dict[str, Any]:
    """评估单个信息源"""
    engine = SourceEvolutionEngine(db)
    scorecard = await engine.get_source_scorecard(source_id)

    if scorecard is None:
        return {"error": "Source not found"}

    result = await engine.evaluate_and_evolve(source_id)

    return {
        "scorecard": {
            "source_id": scorecard.source_id,
            "source_name": scorecard.source_name,
            "overall_score": scorecard.overall_score,
            "read_rate": scorecard.read_rate,
            "quality_rate": scorecard.quality_rate,
            "recommendation": scorecard.recommendation
        },
        "evolution": {
            "action": result.action,
            "message": result.message,
            "success": result.success
        }
    }