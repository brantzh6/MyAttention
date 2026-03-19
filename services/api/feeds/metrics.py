"""
指标收集器 (Metrics Collector)

用于收集和聚合源效果数据和知识使用数据。
为进化引擎提供数据支撑。
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    Source, SourceMetrics, FeedItem, FeedItemInteraction,
    KnowledgeLink, KnowledgeMetrics, KnowledgeEntity
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# 源指标收集
# ═══════════════════════════════════════════════════════════════════════════

class SourceMetricsCollector:
    """源指标收集器"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def collect_daily_metrics(
        self,
        source_id: str,
        date: datetime = None
    ) -> SourceMetrics:
        """
        收集指定源在指定日期的指标

        统计维度：
        - 获取数量：total_items, items_fetched
        - 交互数量：items_read, items_shared, items_to_knowledge
        - 计算指标：read_rate, quality_rate
        """
        if date is None:
            date = datetime.now(timezone.utc)

        date_date = date.date()

        # 检查是否已存在该日期的指标
        result = await self.db.execute(
            select(SourceMetrics).where(
                and_(
                    SourceMetrics.source_id == source_id,
                    func.date(SourceMetrics.date) == date_date
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # 更新现有指标
            return await self._update_metrics(existing)

        # 创建新的指标记录
        return await self._create_metrics(source_id, date_date)

    async def _create_metrics(self, source_id: str, date) -> SourceMetrics:
        """创建新的指标记录"""
        metrics = SourceMetrics(
            id=uuid4(),
            source_id=source_id,
            date=datetime.combine(date, datetime.min.time(), tzinfo=timezone.utc),
            total_items=0,
            items_fetched=0,
            items_read=0,
            items_shared=0,
            items_to_knowledge=0,
            read_rate=0.0,
            quality_rate=0.0
        )

        # 统计获取的条目数
        start_of_day = datetime.combine(date, datetime.min.time(), tzinfo=timezone.utc)
        end_of_day = datetime.combine(date, datetime.max.time(), tzinfo=timezone.utc)

        result = await self.db.execute(
            select(func.count(FeedItem.id)).where(
                and_(
                    FeedItem.source_id == source_id,
                    FeedItem.fetched_at >= start_of_day,
                    FeedItem.fetched_at <= end_of_day
                )
            )
        )
        metrics.total_items = result.scalar() or 0
        metrics.items_fetched = metrics.total_items

        # 统计阅读数
        read_result = await self.db.execute(
            select(func.count(FeedItemInteraction.id)).where(
                and_(
                    FeedItemInteraction.feed_item.has(FeedItem.source_id == source_id),
                    FeedItemInteraction.is_read == True,
                    FeedItemInteraction.read_at >= start_of_day,
                    FeedItemInteraction.read_at <= end_of_day
                )
            )
        )
        metrics.items_read = read_result.scalar() or 0

        # 统计收藏/分享数
        fav_result = await self.db.execute(
            select(func.count(FeedItemInteraction.id)).where(
                and_(
                    FeedItemInteraction.feed_item.has(FeedItem.source_id == source_id),
                    FeedItemInteraction.is_favorite == True,
                    FeedItemInteraction.updated_at >= start_of_day,
                    FeedItemInteraction.updated_at <= end_of_day
                )
            )
        )
        metrics.items_shared = fav_result.scalar() or 0

        # 统计转入知识库数
        kb_result = await self.db.execute(
            select(func.count(KnowledgeLink.id)).where(
                and_(
                    KnowledgeLink.source_id == source_id,
                    KnowledgeLink.linked_at >= start_of_day,
                    KnowledgeLink.linked_at <= end_of_day
                )
            )
        )
        metrics.items_to_knowledge = kb_result.scalar() or 0

        # 计算比率
        if metrics.total_items > 0:
            metrics.read_rate = metrics.items_read / metrics.total_items
            metrics.quality_rate = (metrics.items_read + metrics.items_shared) / metrics.total_items

        self.db.add(metrics)
        await self.db.commit()
        await self.db.refresh(metrics)

        return metrics

    async def _update_metrics(self, metrics: SourceMetrics) -> SourceMetrics:
        """更新现有指标"""
        await self.db.commit()
        await self.db.refresh(metrics)
        return metrics

    async def collect_all_sources(self, date: datetime = None) -> List[SourceMetrics]:
        """收集所有源在某日的指标"""
        if date is None:
            date = datetime.now(timezone.utc)

        date_date = date.date()

        # 获取所有启用的源
        result = await self.db.execute(
            select(Source).where(Source.enabled == True)
        )
        sources = result.scalars().all()

        all_metrics = []
        for source in sources:
            metrics = await self.collect_daily_metrics(str(source.id), date)
            all_metrics.append(metrics)

        return all_metrics

    async def get_metrics_history(
        self,
        source_id: str,
        days: int = 30
    ) -> List[Dict]:
        """获取源的历史指标"""
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self.db.execute(
            select(SourceMetrics).where(
                and_(
                    SourceMetrics.source_id == source_id,
                    SourceMetrics.date >= start_date
                )
            ).order_by(SourceMetrics.date.desc())
        )
        metrics = result.scalars().all()

        return [
            {
                "date": m.date.isoformat(),
                "total_items": m.total_items,
                "items_read": m.items_read,
                "items_shared": m.items_shared,
                "items_to_knowledge": m.items_to_knowledge,
                "read_rate": m.read_rate,
                "quality_rate": m.quality_rate
            }
            for m in metrics
        ]

    async def get_trend(self, source_id: str, metric: str = "read_rate") -> float:
        """
        计算指标趋势

        Args:
            source_id: 源 ID
            metric: 指标名 (read_rate, quality_rate, etc.)

        Returns:
            趋势值：正数=上升，负数=下降
        """
        history = await self.get_metrics_history(source_id, days=14)

        if len(history) < 2:
            return 0.0

        # 简单线性回归计算趋势
        values = [h.get(metric, 0) for h in history]
        n = len(values)

        if n < 2:
            return 0.0

        # 计算斜率
        avg_x = (n - 1) / 2
        avg_y = sum(values) / n

        numerator = sum((i - avg_x) * (values[i] - avg_y) for i in range(n))
        denominator = sum((i - avg_x) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator

        # 标准化到 -1 到 1
        return max(-1, min(1, slope * 7))  # 周趋势


# ═══════════════════════════════════════════════════════════════════════════
# 知识指标收集
# ═══════════════════════════════════════════════════════════════════════════

class KnowledgeMetricsCollector:
    """知识指标收集器"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_query(
        self,
        knowledge_base_id: str,
        document_id: str,
        relevance_score: float = 0.0
    ):
        """
        记录知识查询

        当知识库内容被查询时调用，更新使用统计
        """
        # 查找现有记录
        result = await self.db.execute(
            select(KnowledgeMetrics).where(
                and_(
                    KnowledgeMetrics.knowledge_base_id == knowledge_base_id,
                    KnowledgeMetrics.document_id == document_id
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.query_count += 1
            existing.last_queried = datetime.now(timezone.utc)
            # 移动平均更新相关性评分
            existing.relevance_score = (
                existing.relevance_score * 0.7 + relevance_score * 0.3
            )
        else:
            # 创建新记录
            metrics = KnowledgeMetrics(
                id=uuid4(),
                knowledge_base_id=knowledge_base_id,
                document_id=document_id,
                query_count=1,
                relevance_score=relevance_score,
                last_queried=datetime.now(timezone.utc)
            )
            self.db.add(metrics)

        await self.db.commit()

    async def record_feedback(
        self,
        knowledge_base_id: str,
        document_id: str,
        feedback_score: float
    ):
        """
        记录用户反馈

        当用户对知识库内容提供反馈时调用
        """
        result = await self.db.execute(
            select(KnowledgeMetrics).where(
                and_(
                    KnowledgeMetrics.knowledge_base_id == knowledge_base_id,
                    KnowledgeMetrics.document_id == document_id
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # 更新反馈评分（移动平均）
            if existing.feedback_score > 0:
                existing.feedback_score = (
                    existing.feedback_score * 0.7 + feedback_score * 0.3
                )
            else:
                existing.feedback_score = feedback_score

            existing.updated_at = datetime.now(timezone.utc)

        await self.db.commit()

    async def get_knowledge_stats(self, knowledge_base_id: str) -> Dict:
        """获取知识库统计信息"""
        result = await self.db.execute(
            select(KnowledgeMetrics).where(
                KnowledgeMetrics.knowledge_base_id == knowledge_base_id
            )
        )
        metrics = result.scalars().all()

        if not metrics:
            return {
                "total_documents": 0,
                "total_queries": 0,
                "avg_relevance": 0.0,
                "avg_feedback": 0.0
            }

        total_queries = sum(m.query_count for m in metrics)
        avg_relevance = sum(m.relevance_score * m.query_count for m in metrics) / max(total_queries, 1)
        avg_feedback = sum(m.feedback_score for m in metrics) / len(metrics)

        return {
            "total_documents": len(metrics),
            "total_queries": total_queries,
            "avg_relevance": avg_relevance,
            "avg_feedback": avg_feedback,
            "top_queried": sorted(
                [(m.document_id, m.query_count) for m in metrics],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }

    async def get_unused_knowledge(self, days_threshold: int = 30) -> List[str]:
        """获取长期未使用的知识 ID"""
        threshold = datetime.now(timezone.utc) - timedelta(days=days_threshold)

        result = await self.db.execute(
            select(KnowledgeMetrics).where(
                and_(
                    KnowledgeMetrics.last_queried < threshold,
                    KnowledgeMetrics.query_count == 0
                )
            )
        )
        metrics = result.scalars().all()

        return [
            f"{m.knowledge_base_id}/{m.document_id}"
            for m in metrics
        ]


# ═══════════════════════════════════════════════════════════════════════════
# 便捷函数
# ═══════════════════════════════════════════════════════════════════════════

async def create_metrics_collector(db: AsyncSession) -> SourceMetricsCollector:
    """创建源指标收集器"""
    return SourceMetricsCollector(db)


async def create_knowledge_collector(db: AsyncSession) -> KnowledgeMetricsCollector:
    """创建知识指标收集器"""
    return KnowledgeMetricsCollector(db)