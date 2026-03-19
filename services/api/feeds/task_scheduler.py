"""
任务调度器 - Task Scheduler
定时检查和处理任务
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Task, TaskStatus

logger = logging.getLogger(__name__)


class TaskScheduler:
    """任务调度器 - 定时检查和处理任务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_pending_tasks(self) -> dict:
        """
        检查待处理任务，执行自动处理或发送超时提醒

        Returns:
            dict: 检查结果统计
        """
        # 1. 检查 P0 待处理任务（自动执行）
        p0_pending = await self._get_p0_pending_tasks()
        auto_processed = 0

        for task in p0_pending:
            try:
                from feeds.task_processor import get_task_processor
                processor = get_task_processor(self.db)
                result = await processor.auto_process(task)
                if result.success:
                    auto_processed += 1
            except Exception as e:
                logger.exception(f"自动处理任务失败: {task.id}")

        # 2. 检查超时任务（自动拒绝）
        timeout_tasks = await self._get_timeout_tasks()
        timeout_processed = 0

        for task in timeout_tasks:
            try:
                from feeds.task_processor import get_task_processor
                processor = get_task_processor(self.db)
                result = await processor.reject_task(
                    task,
                    reason="超时自动拒绝",
                    user_id="system"
                )
                if result.success:
                    timeout_processed += 1
            except Exception as e:
                logger.exception(f"处理超时任务失败: {task.id}")

        # 3. 发送 P1 待确认任务提醒
        p1_pending = await self._get_p1_pending_tasks()
        reminder_sent = 0

        for task in p1_pending:
            try:
                # 超过30分钟未确认，发送提醒
                if task.created_at and (datetime.utcnow() - task.created_at).total_seconds() > 1800:
                    from notifications.task_notification import get_task_notification_service
                    notification_service = get_task_notification_service()
                    await notification_service.notify_task_created(task)
                    reminder_sent += 1
            except Exception as e:
                logger.exception(f"发送提醒失败: {task.id}")

        return {
            "p0_auto_processed": auto_processed,
            "timeout_processed": timeout_processed,
            "reminder_sent": reminder_sent
        }

    async def _get_p0_pending_tasks(self) -> list:
        """获取待处理的 P0 任务"""
        result = await self.db.execute(
            select(Task)
            .where(Task.priority == 0)
            .where(Task.auto_processible == True)
            .where(Task.status == TaskStatus.PENDING.value)
            .limit(10)
        )
        return list(result.scalars().all())

    async def _get_timeout_tasks(self) -> list:
        """获取超时的任务"""
        now = datetime.utcnow()
        result = await self.db.execute(
            select(Task)
            .where(Task.status == TaskStatus.PENDING.value)
            .where(Task.expired_at < now)
            .limit(20)
        )
        return list(result.scalars().all())

    async def _get_p1_pending_tasks(self) -> list:
        """获取待确认的 P1 任务"""
        result = await self.db.execute(
            select(Task)
            .where(Task.priority == 1)
            .where(Task.status == TaskStatus.PENDING.value)
            .limit(20)
        )
        return list(result.scalars().all())

    async def generate_daily_report(self) -> dict:
        """
        生成每日任务报告

        Returns:
            dict: 报告数据
        """
        from datetime import date

        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())

        # 今日新增
        new_result = await self.db.execute(
            select(func.count(Task.id))
            .where(Task.created_at >= today_start)
        )
        new_count = new_result.scalar()

        # 今日完成
        completed_result = await self.db.execute(
            select(func.count(Task.id))
            .where(Task.status == TaskStatus.COMPLETED.value)
            .where(Task.completed_at >= today_start)
        )
        completed_count = completed_result.scalar()

        # 今日失败
        failed_result = await self.db.execute(
            select(func.count(Task.id))
            .where(Task.status == TaskStatus.FAILED.value)
            .where(Task.failed_at >= today_start)
        )
        failed_count = failed_result.scalar()

        # 统计 P0/P1
        p0_result = await self.db.execute(
            select(func.count(Task.id))
            .where(Task.priority == 0)
            .where(Task.status.in_([TaskStatus.PENDING.value, TaskStatus.EXECUTING.value]))
        )
        p0_pending = p0_result.scalar()

        p1_result = await self.db.execute(
            select(func.count(Task.id))
            .where(Task.priority == 1)
            .where(Task.status == TaskStatus.PENDING.value)
        )
        p1_pending = p1_result.scalar()

        return {
            "date": today.isoformat(),
            "new_tasks": new_count or 0,
            "completed": completed_count or 0,
            "failed": failed_count or 0,
            "p0_pending": p0_pending or 0,
            "p1_pending": p1_pending or 0
        }


# ═══════════════════════════════════════════════════════════════════════════
# 便捷函数
# ═══════════════════════════════════════════════════════════════════════════

def get_task_scheduler(db: AsyncSession) -> TaskScheduler:
    """获取任务调度器实例"""
    return TaskScheduler(db)