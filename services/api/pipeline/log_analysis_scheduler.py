"""
日志分析调度器 - Log Analysis Scheduler

定时任务：
1. 每小时运行日志分析
2. 生成系统洞察
3. 自动创建任务处理问题
4. 发送每日报告
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class LogAnalysisScheduler:
    """日志分析调度器 - 定期分析日志并生成改进建议"""

    def __init__(self):
        self._last_analysis = None
        self._last_report_time = None

    async def run_analysis(self) -> Dict[str, Any]:
        """
        运行日志分析

        Returns:
            Dict: 分析结果
        """
        from feeds.log_monitor import get_log_monitor

        logger.info("开始运行日志分析...")

        monitor = get_log_monitor()

        # 收集最近24小时的日志
        logs = monitor.collect_logs(hours=24)
        logger.info(f"收集到 {len(logs)} 条日志")

        # 分析错误模式
        error_patterns = monitor.analyze_errors(logs)
        logger.info(f"发现 {len(error_patterns)} 种错误模式")

        # 生成洞察
        insights = monitor.generate_insights(logs)
        logger.info(f"生成 {len(insights)} 条洞察建议")

        # 创建任务处理严重问题
        tasks_created = await self._create_tasks_from_insights(insights)

        # 更新最后分析时间
        self._last_analysis = datetime.now()

        return {
            "logs_analyzed": len(logs),
            "error_patterns": len(error_patterns),
            "insights": len(insights),
            "tasks_created": tasks_created,
            "top_insights": [
                {
                    "id": insight.id,
                    "title": insight.title,
                    "severity": insight.severity,
                    "category": insight.category,
                }
                for insight in insights[:5]
            ],
            "timestamp": self._last_analysis.isoformat()
        }

    async def _create_tasks_from_insights(self, insights) -> int:
        """从洞察创建任务"""
        tasks_count = 0

        for insight in insights:
            # 只处理 critical 和 warning 级别
            if insight.severity not in ("critical", "warning"):
                continue

            try:
                tasks_count += await self._create_task_from_insight(insight)
            except Exception as e:
                logger.error(f"从洞察创建任务失败: {e}")

        return tasks_count

    async def _create_task_from_insight(self, insight) -> int:
        """从单个洞察创建任务"""
        from uuid import uuid4
        from db import get_db
        from db.models import Task, TaskStatus
        from feeds.task_processor import get_task_processor

        # 确定优先级
        priority_map = {
            "critical": 0,
            "warning": 1,
            "info": 2
        }
        priority = priority_map.get(insight.severity, 2)

        # 确定是否可自动处理
        auto_processible = insight.severity == "critical" and insight.category in ("performance", "reliability")
        task_title = f"[日志分析] {insight.title}"
        task_description = insight.description + "\n\n建议: " + insight.suggestion
        task_source_data = {
            "category": insight.category,
            "severity": insight.severity,
            "evidence": insight.evidence
        }

        # 保存到数据库
        async for db in get_db():
            try:
                processor = get_task_processor(db)
                existing_task = await processor.find_existing_open_task(
                    source_type="log_analysis",
                    source_id=insight.id,
                    title=task_title,
                    category=insight.category,
                )

                if existing_task:
                    await processor.mark_task_seen(
                        existing_task,
                        source_data=task_source_data,
                        description=task_description,
                        priority=priority,
                        auto_processible=auto_processible,
                    )
                    logger.info(f"复用日志分析任务: {existing_task.id} - {existing_task.title[:50]}")
                    return 0

                task = Task(
                    id=uuid4(),
                    source_type="log_analysis",
                    source_id=insight.id,
                    source_data=processor.build_task_source_data(task_source_data),
                    title=task_title,
                    description=task_description,
                    priority=priority,
                    category=insight.category,
                    status=TaskStatus.PENDING.value,
                    auto_processible=auto_processible,
                    created_by="ai"
                )

                db.add(task)
                await db.commit()
                await db.refresh(task)

                logger.info(f"从洞察创建任务: {task.id} - {task.title[:50]}")

                # 处理任务
                await processor.process(task)

                return 1
            except Exception as e:
                logger.error(f"保存任务失败: {e}")
                return 0

        return 0

    async def run_daily_report(self) -> Dict[str, Any]:
        """
        生成每日报告

        Returns:
            Dict: 报告结果
        """
        from feeds.log_monitor import get_log_monitor
        from notifications.task_notification import get_task_notification_service

        logger.info("生成每日日志报告...")

        monitor = get_log_monitor()
        logs = monitor.collect_logs(hours=24)

        # 统计
        error_count = len([l for l in logs if l.level == "ERROR"])
        warning_count = len([l for l in logs if l.level == "WARNING"])

        # 获取洞察
        insights = monitor.generate_insights(logs)

        # 筛选重要洞察
        important_insights = [i for i in insights if i.severity in ("critical", "warning")]

        # 发送通知
        notification_service = get_task_notification_service()

        # 创建任务对象用于通知
        from uuid import uuid4
        from db.models import Task

        class ReportTask:
            def __init__(self):
                self.id = uuid4()
                self.title = f"每日日志报告 - {datetime.now().strftime('%Y-%m-%d')}"
                self.priority = 2 if error_count == 0 else 1
                self.status = "completed"

        report_task = ReportTask()

        await notification_service.send_daily_task_summary(important_insights)

        self._last_report_time = datetime.now()

        return {
            "logs_analyzed": len(logs),
            "errors": error_count,
            "warnings": warning_count,
            "insights": len(important_insights),
            "timestamp": self._last_report_time.isoformat()
        }

    async def check_and_alert(self) -> Dict[str, Any]:
        """
        快速检查并告警

        Returns:
            Dict: 检查结果
        """
        from feeds.log_monitor import get_log_monitor

        # 只分析最近1小时的日志
        monitor = get_log_monitor()
        logs = monitor.collect_logs(hours=1)

        # 快速检查严重错误
        critical_errors = []
        for log in logs:
            msg = log.message.lower()
            if log.level in ("ERROR", "CRITICAL") or any(
                kw in msg for kw in ["exception", "fatal", "critical", "crash", "failed", "error"]
            ):
                critical_errors.append(log.message[:200])

        if critical_errors:
            logger.warning(f"检测到 {len(critical_errors)} 个严重错误!")
            # 可以在这里触发即时通知

        return {
            "critical_errors": len(critical_errors),
            "sample_errors": critical_errors[:3],
            "timestamp": datetime.now().isoformat()
        }


# ═══════════════════════════════════════════════════════════════════════════
# 便捷函数
# ═══════════════════════════════════════════════════════════════════════════

_log_scheduler: LogAnalysisScheduler = None


def get_log_analysis_scheduler() -> LogAnalysisScheduler:
    """获取日志分析调度器实例"""
    global _log_scheduler
    if _log_scheduler is None:
        _log_scheduler = LogAnalysisScheduler()
    return _log_scheduler


async def run_log_analysis() -> Dict[str, Any]:
    """运行日志分析（供调度器调用）"""
    scheduler = get_log_analysis_scheduler()
    return await scheduler.run_analysis()


async def run_log_daily_report() -> Dict[str, Any]:
    """运行每日报告（供调度器调用）"""
    scheduler = get_log_analysis_scheduler()
    return await scheduler.run_daily_report()


async def check_system_health() -> Dict[str, Any]:
    """快速健康检查（供调度器调用）"""
    scheduler = get_log_analysis_scheduler()
    return await scheduler.check_and_alert()
