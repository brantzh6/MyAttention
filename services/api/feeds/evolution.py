"""
源进化引擎 (Source Evolution Engine)

核心功能：
1. 源效果评估 - 追踪每个信息源的实际效果指标
2. 自适应获取 - 根据反爬状态自动调整获取策略
3. 自动优化 - 根据效果动态调整权威评分、禁用低效源
4. 新源发现 - AI 自动搜索和评估潜在信息源
"""

import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    Source, SourceMetrics, SourceCandidate, FeedItem, FeedItemInteraction,
    AntiCrawlStatus, AccessMethod
)
from feeds.authority import get_authority_classifier

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# 数据模型
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class EvolutionResult:
    """进化操作结果"""
    action: str  # adjust_score, disable, enable, change_method, etc.
    source_id: str
    details: Dict[str, Any]
    success: bool
    message: str


@dataclass
class SourceScorecard:
    """信息源计分卡"""
    source_id: str
    source_name: str

    # 数量指标
    total_items: int = 0
    items_fetched: int = 0

    # 质量指标
    items_read: int = 0
    items_shared: int = 0
    items_to_knowledge: int = 0

    # 计算指标
    read_rate: float = 0.0
    quality_rate: float = 0.0
    knowledge_rate: float = 0.0

    # 历史趋势
    read_rate_trend: float = 0.0  # 正数=上升，负数=下降

    # 综合评分 (0-100)
    overall_score: float = 50.0

    # 建议
    recommendation: str = ""
    suggested_actions: List[str] = None

    def __post_init__(self):
        if self.suggested_actions is None:
            self.suggested_actions = []


# ═══════════════════════════════════════════════════════════════════════════
# 指标收集器
# ═══════════════════════════════════════════════════════════════════════════

class MetricsCollector:
    """指标收集器 - 收集和聚合源效果数据"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def collect_source_metrics(
        self,
        source_id: str,
        date: datetime = None
    ) -> SourceMetrics:
        """
        收集指定源在指定日期的指标

        Args:
            source_id: 信息源 ID
            date: 统计日期，默认为今天

        Returns:
            SourceMetrics 对象
        """
        if date is None:
            date = datetime.now(timezone.utc).date()

        # 检查是否已存在该日期的指标
        result = await self.db.execute(
            select(SourceMetrics).where(
                and_(
                    SourceMetrics.source_id == source_id,
                    func.date(SourceMetrics.date) == date
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            return existing

        # 创建新的指标记录
        metrics = SourceMetrics(
            id=uuid4(),
            source_id=source_id,
            date=datetime.combine(date, datetime.min.time(), tzinfo=timezone.utc)
        )

        # 统计获取的条目数
        feed_result = await self.db.execute(
            select(func.count(FeedItem.id)).where(FeedItem.source_id == source_id)
        )
        metrics.total_items = feed_result.scalar() or 0
        metrics.items_fetched = metrics.total_items  # 简化处理

        # 统计阅读数（需要关联 interaction）
        # 暂时跳过，后续完善

        self.db.add(metrics)
        await self.db.commit()
        await self.db.refresh(metrics)

        return metrics

    async def update_interaction_metrics(self, source_id: str):
        """根据交互数据更新指标"""
        # 获取最近7天的数据
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        # 获取该源的所有 FeedItem IDs
        result = await self.db.execute(
            select(FeedItem.id).where(FeedItem.source_id == source_id)
        )
        item_ids = [row[0] for row in result.fetchall()]

        if not item_ids:
            return

        # 统计阅读数
        read_result = await self.db.execute(
            select(func.count(FeedItemInteraction.id))
            .join(FeedItem)
            .where(
                and_(
                    FeedItem.source_id == source_id,
                    FeedItemInteraction.is_read == True
                )
            )
        )
        items_read = read_result.scalar() or 0

        # 统计收藏数
        fav_result = await self.db.execute(
            select(func.count(FeedItemInteraction.id))
            .join(FeedItem)
            .where(
                and_(
                    FeedItem.source_id == source_id,
                    FeedItemInteraction.is_favorite == True
                )
            )
        )
        items_shared = fav_result.scalar() or 0

        # 计算阅读率
        if metrics.total_items > 0:
            metrics.read_rate = items_read / metrics.total_items
            metrics.quality_rate = (items_read + items_shared) / metrics.total_items

        logger.info(
            f"Updated metrics for source {source_id}: "
            f"read_rate={metrics.read_rate:.2%}, quality_rate={metrics.quality_rate:.2%}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 源进化引擎
# ═══════════════════════════════════════════════════════════════════════════

class SourceEvolutionEngine:
    """源进化引擎 - 评估和优化信息源"""

    # 阈值配置
    MIN_SUCCESS_RATE = 0.5       # 最低成功率，低于此值禁用
    MIN_QUALITY_RATE = 0.1       # 最低质量率，低于此值增加深度
    MAX_READ_RATE_TREND = -0.2   # 阅读率下降阈值，触发警告

    # 自动调整间隔
    SCORE_DECAY = 0.02           # 每月权威评分自然衰减
    SCORE_BOOST = 0.05           # 优质源评分提升

    def __init__(self, db: AsyncSession):
        self.db = db
        self.collector = MetricsCollector(db)

    async def get_source_scorecard(self, source_id: str) -> Optional[SourceScorecard]:
        """获取信息源计分卡"""
        # 获取源信息
        result = await self.db.execute(
            select(Source).where(Source.id == source_id)
        )
        source = result.scalar_one_or_none()

        if not source:
            return None

        # 获取今日指标
        metrics = await self.collector.collect_source_metrics(source_id)

        # 创建计分卡
        scorecard = SourceScorecard(
            source_id=str(source.id),
            source_name=source.name,
            total_items=metrics.total_items,
            items_fetched=metrics.items_fetched,
            items_read=metrics.items_read,
            items_shared=metrics.items_shared,
            items_to_knowledge=metrics.items_to_knowledge,
            read_rate=metrics.read_rate,
            quality_rate=metrics.quality_rate,
        )

        # 计算知识转化率
        if metrics.total_items > 0:
            scorecard.knowledge_rate = metrics.items_to_knowledge / metrics.total_items

        # 计算综合评分
        scorecard.overall_score = self._calculate_overall_score(scorecard)

        # 生成建议
        scorecard.recommendation, scorecard.suggested_actions = self._generate_recommendations(
            source, scorecard
        )

        return scorecard

    def _calculate_overall_score(self, card: SourceScorecard) -> float:
        """计算综合评分 (0-100)"""
        # 权重配置
        WEIGHT_FETCH = 0.2      # 获取能力
        WEIGHT_QUALITY = 0.5    # 质量
        WEIGHT_KNOWLEDGE = 0.3  # 知识转化

        # 基础分
        fetch_score = min(card.items_fetched / 10, 1.0) * 100 * WEIGHT_FETCH
        quality_score = card.read_rate * 100 * WEIGHT_QUALITY
        knowledge_score = card.knowledge_rate * 100 * WEIGHT_KNOWLEDGE

        return fetch_score + quality_score + knowledge_score

    def _generate_recommendations(
        self,
        source: Source,
        card: SourceScorecard
    ) -> tuple[str, List[str]]:
        """生成优化建议"""
        actions = []

        # 检查成功率
        total = source.success_count + source.failure_count
        if total > 0:
            success_rate = source.success_count / total
            if success_rate < self.MIN_SUCCESS_RATE:
                return "该源成功率过低，建议禁用", ["disable"]

        # 检查质量率
        if card.quality_rate < self.MIN_QUALITY_RATE:
            actions.append("increase_depth")

        # 检查反爬状态
        if source.anti_crawl_status == AntiCrawlStatus.BLOCKED:
            actions.append("change_to_proxy")
        elif source.anti_crawl_status == AntiCrawlStatus.PAYWALL:
            actions.append("reduce_depth")

        # 检查阅读率趋势
        if card.read_rate_trend < self.MAX_READ_RATE_TREND:
            actions.append("investigate")

        # 高质量源建议
        if card.overall_score > 80:
            return "优质信息源，建议保持当前策略", []

        if not actions:
            return "运行正常", []

        return "建议优化", actions

    async def evaluate_and_evolve(self, source_id: str) -> EvolutionResult:
        """
        评估并执行进化

        核心反馈驱动闭环：
        用户行为数据 → 效果评估 → 策略优化 → 自动执行 → 新数据
        """
        # 获取源信息
        result = await self.db.execute(
            select(Source).where(Source.id == source_id)
        )
        source = result.scalar_one_or_none()

        if not source:
            return EvolutionResult(
                action="error",
                source_id=source_id,
                details={},
                success=False,
                message="源不存在"
            )

        # 获取计分卡
        scorecard = await self.get_source_scorecard(source_id)

        # 执行优化动作
        for action in scorecard.suggested_actions:
            result = await self._execute_action(source, action, scorecard)
            if not result.success:
                return result

        return EvolutionResult(
            action="optimized",
            source_id=source_id,
            details={"overall_score": scorecard.overall_score},
            success=True,
            message=f"优化完成，综合评分: {scorecard.overall_score:.1f}"
        )

    async def _execute_action(
        self,
        source: Source,
        action: str,
        scorecard: SourceScorecard
    ) -> EvolutionResult:
        """执行具体的优化动作"""

        if action == "disable":
            source.enabled = False
            await self.db.commit()
            return EvolutionResult(
                action="disable",
                source_id=str(source.id),
                details={},
                success=True,
                message="已自动禁用低效源"
            )

        if action == "increase_depth":
            if source.fetch_depth < 3:
                source.fetch_depth += 1
                await self.db.commit()
                return EvolutionResult(
                    action="increase_depth",
                    source_id=str(source.id),
                    details={"new_depth": source.fetch_depth},
                    success=True,
                    message=f"已增加获取深度到 L{source.fetch_depth}"
                )

        if action == "decrease_depth":
            if source.fetch_depth > 1:
                source.fetch_depth -= 1
                await self.db.commit()
                return EvolutionResult(
                    action="decrease_depth",
                    source_id=str(source.id),
                    details={"new_depth": source.fetch_depth},
                    success=True,
                    message=f"已降低获取深度到 L{source.fetch_depth}"
                )

        if action == "change_to_proxy":
            if source.access_method == AccessMethod.DIRECT:
                source.access_method = AccessMethod.PROXY
                source.retry_count = 0
                await self.db.commit()
                return EvolutionResult(
                    action="change_to_proxy",
                    source_id=str(source.id),
                    details={},
                    success=True,
                    message="已切换到代理访问"
                )

        if action == "change_to_cloud":
            if source.access_method in [AccessMethod.DIRECT, AccessMethod.PROXY]:
                source.access_method = AccessMethod.CLOUD
                source.retry_count = 0
                await self.db.commit()
                return EvolutionResult(
                    action="change_to_cloud",
                    source_id=str(source.id),
                    details={},
                    success=True,
                    message="已切换到云访问"
                )

        return EvolutionResult(
            action=action,
            source_id=str(source.id),
            details={},
            success=True,
            message=f"执行动作: {action}"
        )

    async def evolve_all_sources(self) -> List[EvolutionResult]:
        """批量进化所有启用的源"""
        result = await self.db.execute(
            select(Source).where(Source.enabled == True)
        )
        sources = result.scalars().all()

        results = []
        for source in sources:
            evolution_result = await self.evaluate_and_evolve(str(source.id))
            results.append(evolution_result)

        logger.info(f"进化评估完成，处理了 {len(results)} 个信息源")

        # 统计
        disabled = sum(1 for r in results if r.action == "disable")
        optimized = sum(1 for r in results if r.success)

        logger.info(f"禁用: {disabled}, 优化: {optimized}")

        return results


# ═══════════════════════════════════════════════════════════════════════════
# 自适应获取器
# ═══════════════════════════════════════════════════════════════════════════

class AdaptiveFetcher:
    """自适应获取器 - 根据反爬状态自动调整获取策略"""

    # 反爬状态到访问方式的映射
    ANTI_CRAWL_MAPPING = {
        AntiCrawlStatus.BLOCKED: AccessMethod.PROXY,
        AntiCrawlStatus.RATE_LIMITED: AccessMethod.PROXY,
        AntiCrawlStatus.PAYWALL: AccessMethod.CLOUD,
        AntiCrawlStatus.CAPTCHA: AccessMethod.CLOUD,
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    def should_switch_method(self, source: Source) -> bool:
        """判断是否需要切换访问方式"""
        if source.anti_crawl_status == AntiCrawlStatus.OK:
            return False

        # 当前方法已经是较高级别的
        current_priority = self._get_method_priority(source.access_method)
        recommended = self.ANTI_CRAWL_MAPPING.get(source.anti_crawl_status)

        if recommended is None:
            return False

        recommended_priority = self._get_method_priority(recommended)
        return recommended_priority > current_priority

    def _get_method_priority(self, method: AccessMethod) -> int:
        """获取访问方式优先级"""
        priorities = {
            AccessMethod.DIRECT: 1,
            AccessMethod.PROXY: 2,
            AccessMethod.CLOUD: 3,
            AccessMethod.MANUAL: 4,
        }
        return priorities.get(method, 0)

    async def adapt_source(self, source: Source) -> Optional[EvolutionResult]:
        """
        自适应调整源配置

        逻辑：
        1. 检查反爬状态，自动切换访问方式
        2. 检查成功率，自动禁用低效源
        3. 检查效果，动态调整获取深度
        """
        if not self.should_switch_method(source):
            return None

        old_method = source.access_method
        new_method = self.ANTI_CRAWL_MAPPING.get(source.anti_crawl_status)

        if new_method:
            source.access_method = new_method
            source.retry_count = 0
            await self.db.commit()

            return EvolutionResult(
                action="adapt_method",
                source_id=str(source.id),
                details={
                    "old_method": old_method.value,
                    "new_method": new_method.value
                },
                success=True,
                message=f"自适应切换访问方式: {old_method.value} -> {new_method.value}"
            )

        return None

    async def evaluate_success_rate(self, source: Source) -> Optional[EvolutionResult]:
        """评估并处理成功率"""
        total = source.success_count + source.failure_count

        if total < 10:  # 至少10次尝试
            return None

        success_rate = source.success_count / total

        if success_rate < SourceEvolutionEngine.MIN_SUCCESS_RATE:
            source.enabled = False
            await self.db.commit()

            return EvolutionResult(
                action="auto_disable",
                source_id=str(source.id),
                details={"success_rate": success_rate},
                success=True,
                message=f"成功率 {success_rate:.1%} 低于阈值，已自动禁用"
            )

        return None


# ═══════════════════════════════════════════════════════════════════════════
# 新源发现系统
# ═══════════════════════════════════════════════════════════════════════════

class SourceDiscovery:
    """新源发现系统 - AI 自动发现和评估潜在信息源"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.classifier = get_authority_classifier()

    async def add_candidate(
        self,
        url: str,
        name: str = "",
        category: str = "",
        content_sample: str = ""
    ) -> SourceCandidate:
        """添加潜在源候选"""

        # 评估权威性
        authority_result = self.classifier.classify(url, name, category)

        candidate = SourceCandidate(
            id=uuid4(),
            url=url,
            name=name or url,
            category=category,
            authority_tier=authority_result.tier,
            ai_score=authority_result.score,
            content_sample=content_sample[:500] if content_sample else "",
            status="pending"
        )

        self.db.add(candidate)
        await self.db.commit()
        await self.db.refresh(candidate)

        return candidate

    async def get_recommended_candidates(self) -> List[SourceCandidate]:
        """获取推荐的候选源"""
        result = await self.db.execute(
            select(SourceCandidate)
            .where(SourceCandidate.status == "pending")
            .order_by(SourceCandidate.ai_score.desc())
            .limit(10)
        )
        return result.scalars().all()

    async def approve_candidate(self, candidate_id: str) -> Optional[Source]:
        """批准候选源，实际添加到信息源列表"""
        result = await self.db.execute(
            select(SourceCandidate).where(SourceCandidate.id == candidate_id)
        )
        candidate = result.scalar_one_or_none()

        if not candidate:
            return None

        # 更新状态
        candidate.status = "approved"
        candidate.approved_at = datetime.now(timezone.utc)

        # 创建实际的信息源（如果是 RSS 类型）
        if candidate.url:
            source = Source(
                id=candidate.id,
                name=candidate.name,
                url=candidate.url,
                category=candidate.category or "未分类",
                authority_tier=candidate.authority_tier,
                authority_score=candidate.ai_score,
                type="rss",  # 假设为 RSS
            )
            self.db.add(source)

        await self.db.commit()

        return source

    async def reject_candidate(self, candidate_id: str, reason: str = ""):
        """拒绝候选源"""
        result = await self.db.execute(
            select(SourceCandidate).where(SourceCandidate.id == candidate_id)
        )
        candidate = result.scalar_one_or_none()

        if candidate:
            candidate.status = "rejected"
            candidate.rejected_at = datetime.now(timezone.utc)
            candidate.reject_reason = reason
            await self.db.commit()

    async def auto_discover(self, keywords: List[str]) -> List[SourceCandidate]:
        """
        自动发现新源

        基于关键词搜索发现潜在信息源。
        实际实现需要调用搜索引擎或 AI。
        """
        # TODO: 实现实际的搜索逻辑
        # 这里只做占位

        discovered = []

        for keyword in keywords:
            # 模拟发现
            logger.info(f"Auto-discovering sources for keyword: {keyword}")

            # 实际实现应该：
            # 1. 调用搜索引擎搜索相关 RSS 源
            # 2. 调用 AI 评估内容质量
            # 3. 添加为候选源

        return discovered