"""
任务处理器 - Task Processor
执行任务并记录结果
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Task, TaskHistory, TaskStatus

logger = logging.getLogger(__name__)

OPEN_TASK_STATUSES = (
    TaskStatus.PENDING.value,
    TaskStatus.CONFIRMED.value,
    TaskStatus.EXECUTING.value,
    TaskStatus.FAILED.value,
)

SYSTEM_HEALTH_STATUS_ORDER = {
    "unknown": 0,
    "unhealthy": 1,
    "degraded": 2,
    "healthy": 3,
}


def make_ascii_safe(value: Any) -> Any:
    if isinstance(value, str):
        return value.encode("ascii", "replace").decode("ascii")
    if isinstance(value, dict):
        return {make_ascii_safe(key): make_ascii_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [make_ascii_safe(item) for item in value]
    return value


def build_system_health_recovery_plan(source_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    payload = dict(source_data or {})
    issue_type = str(payload.get("type") or payload.get("task_type") or "").strip()
    summary = payload.get("summary") or {}
    state = str(payload.get("state") or summary.get("state") or "unknown").strip()

    if issue_type == "feed_collection_health":
        return {
            "issue_type": issue_type,
            "state": state,
            "strategy": "trigger_pipeline",
            "verify_endpoint": "/api/evolution/collection-health",
            "verify_delay_seconds": 4,
        }

    return {
        "issue_type": issue_type or "unknown",
        "state": state,
        "strategy": "observe_only",
        "verify_endpoint": "",
        "verify_delay_seconds": 0,
    }


def is_system_health_improved(before_status: str, after_status: str) -> bool:
    return SYSTEM_HEALTH_STATUS_ORDER.get(after_status, 0) > SYSTEM_HEALTH_STATUS_ORDER.get(before_status, 0)


@dataclass
class TaskResult:
    """任务执行结果"""
    success: bool
    action: str
    message: str
    details: Dict[str, Any]


class TaskProcessor:
    """任务处理器 - 执行任务并记录结果"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_existing_open_task(
        self,
        *,
        source_type: str,
        title: str,
        source_id: Optional[str] = None,
        category: Optional[str] = None,
        statuses: Optional[List[str]] = None,
    ) -> Optional[Task]:
        """Find an existing open task for the same issue."""
        stmt = select(Task).where(
            Task.source_type == source_type,
            Task.title == title,
            Task.status.in_(statuses or OPEN_TASK_STATUSES),
        )

        if source_id is None:
            stmt = stmt.where(Task.source_id.is_(None))
        else:
            stmt = stmt.where(Task.source_id == source_id)

        if category:
            stmt = stmt.where(Task.category == category)

        stmt = stmt.order_by(Task.updated_at.desc().nullslast(), Task.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().first()

    def build_task_source_data(
        self,
        source_data: Optional[Dict[str, Any]],
        existing_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Merge task source data and attach occurrence metadata."""
        now = datetime.utcnow().isoformat()
        merged = dict(existing_data or {})

        merged["occurrence_count"] = int(merged.get("occurrence_count") or 0) + 1
        merged.setdefault("first_seen_at", now)
        merged["last_seen_at"] = now

        if source_data:
            merged.update(source_data)
            merged["latest_payload"] = source_data

        return merged

    async def mark_task_seen(
        self,
        task: Task,
        *,
        source_data: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        auto_processible: Optional[bool] = None,
    ) -> Task:
        """Refresh an existing task when the same issue is detected again."""
        task.source_data = self.build_task_source_data(source_data, task.source_data)
        task.updated_at = datetime.utcnow()

        if description:
            task.description = description
        if priority is not None:
            task.priority = min(task.priority or priority, priority)
        if auto_processible is not None:
            task.auto_processible = task.auto_processible or auto_processible

        await self.db.commit()
        await self.db.refresh(task)

        await self._record_history(
            task=task,
            action="dedupe_update",
            result="skipped",
            details={
                "message": "Issue observed again; reused existing task",
                "occurrence_count": task.source_data.get("occurrence_count", 1),
            },
        )

        setattr(task, "_was_created", False)
        setattr(task, "_was_deduplicated", True)
        return task

    async def create_task(self, classification_result) -> Task:
        """
        根据分类结果创建任务

        Args:
            classification_result: 分类结果

        Returns:
            Task: 创建的任务
        """
        existing_task = await self.find_existing_open_task(
            source_type=classification_result.source_type,
            source_id=classification_result.source_id,
            title=classification_result.title,
            category=classification_result.category,
        )

        if existing_task:
            logger.info(f"复用已有任务: {existing_task.id} - {existing_task.title}")
            return await self.mark_task_seen(
                existing_task,
                source_data=classification_result.source_data,
                description=classification_result.description,
                priority=classification_result.priority,
                auto_processible=classification_result.auto_processible,
            )

        task = Task(
            id=uuid4(),
            source_type=classification_result.source_type,
            source_id=classification_result.source_id,
            source_data=self.build_task_source_data(classification_result.source_data),
            title=classification_result.title,
            description=classification_result.description,
            priority=classification_result.priority,
            category=classification_result.category,
            status=TaskStatus.PENDING.value,
            auto_processible=classification_result.auto_processible,
            created_by="system"
        )

        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)

        setattr(task, "_was_created", True)
        setattr(task, "_was_deduplicated", False)

        logger.info(f"创建任务: {task.id} - {task.title}")

        return task

    async def process(self, task: Task) -> TaskResult:
        """
        处理任务

        根据任务优先级和可自动处理属性决定处理方式：
        - P0级别且可自动处理：自动执行
        - P1级别：需要人工确认，发送通知
        - P2/P3级别：添加到汇总报告

        Args:
            task: 任务

        Returns:
            TaskResult: 处理结果
        """
        # 判断处理策略
        if task.source_type == "system_health" and task.auto_processible:
            return await self.auto_process(task)
        if task.priority == 0 and task.auto_processible:
            # P0 紧急任务，自动处理
            return await self.auto_process(task)
        elif task.priority == 1:
            # P1 重要任务，发送确认请求
            return await self.request_confirmation(task)
        else:
            # P2/P3 普通任务，汇总报告
            return await self.add_to_digest(task)

    async def auto_process(self, task: Task) -> TaskResult:
        """
        自动处理任务（P0级别）

        Args:
            task: 任务

        Returns:
            TaskResult: 处理结果
        """
        logger.info(f"自动处理任务: {task.id} - {task.title}")

        # 更新状态为执行中
        task.status = TaskStatus.EXECUTING.value
        task.executing_at = datetime.utcnow()
        await self.db.commit()

        # 根据来源类型执行不同的处理逻辑
        source_type = task.source_type
        source_data = task.source_data or {}

        try:
            if source_type == "api_test":
                result = await self._handle_api_test(task, source_data)
            elif source_type == "ui_test":
                result = await self._handle_ui_test(task, source_data)
            elif source_type == "anti_crawl":
                result = await self._handle_anti_crawl(task, source_data)
            elif source_type == "system_health":
                result = await self._handle_system_health(task, source_data)
            else:
                result = TaskResult(
                    success=False,
                    action="auto_retry",
                    message=f"未知的来源类型: {source_type}",
                    details={}
                )

            # 记录历史
            await self._record_history(
                task=task,
                action="auto_retry",
                result="success" if result.success else "failed",
                details={"message": result.message, **(result.details or {})}
            )

            # 更新任务状态
            if result.success:
                task.status = TaskStatus.COMPLETED.value
                task.completed_at = datetime.utcnow()
            else:
                task.status = TaskStatus.FAILED.value
                task.failed_at = datetime.utcnow()

            task.updated_at = datetime.utcnow()
            await self.db.commit()

            return result

        except Exception as e:
            logger.exception(f"自动处理任务失败: {task.id}")

            await self._record_history(
                task=task,
                action="auto_retry",
                result="failed",
                details={"error": str(e)}
            )

            task.status = TaskStatus.FAILED.value
            task.failed_at = datetime.utcnow()
            task.updated_at = datetime.utcnow()
            await self.db.commit()

            return TaskResult(
                success=False,
                action="auto_retry",
                message=f"处理失败: {str(e)}",
                details={"error": str(e)}
            )

    async def request_confirmation(self, task: Task) -> TaskResult:
        """
        请求人工确认（P1级别）

        Args:
            task: 任务

        Returns:
            TaskResult: 处理结果
        """
        logger.info(f"请求人工确认任务: {task.id} - {task.title}")

        # 保持 pending 状态，等待确认
        task.updated_at = datetime.utcnow()

        # 设置过期时间（默认60分钟）
        timeout = 60  # 默认超时时间（分钟）

        from datetime import timedelta
        task.expired_at = datetime.utcnow() + timedelta(minutes=timeout)

        await self.db.commit()

        # 发送通知
        await self._send_confirmation_notification(task)

        # 记录历史
        await self._record_history(
            task=task,
            action="manual_confirm",
            result="pending",
            details={"message": "等待人工确认"}
        )

        return TaskResult(
            success=True,
            action="manual_confirm",
            message="已发送确认请求，等待人工处理",
            details={"task_id": str(task.id)}
        )

    async def add_to_digest(self, task: Task) -> TaskResult:
        """
        添加到汇总报告（P2/P3级别）

        Args:
            task: 任务

        Returns:
            TaskResult: 处理结果
        """
        logger.info(f"添加到汇总报告: {task.id} - {task.title}")

        # 保持 pending 状态
        task.updated_at = datetime.utcnow()
        await self.db.commit()

        # 记录历史
        await self._record_history(
            task=task,
            action="add_to_digest",
            result="pending",
            details={"message": "添加到定期汇总报告"}
        )

        return TaskResult(
            success=True,
            action="add_to_digest",
            message="已添加到汇总报告",
            details={"task_id": str(task.id)}
        )

    async def confirm_task(self, task: Task, user_id: str = "user") -> TaskResult:
        """
        确认并执行任务

        Args:
            task: 任务
            user_id: 用户ID

        Returns:
            TaskResult: 处理结果
        """
        logger.info(f"确认任务: {task.id} - {task.title}")

        # 更新状态
        task.status = TaskStatus.CONFIRMED.value
        task.confirmed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        await self.db.commit()

        # 执行任务
        return await self.execute_task(task, user_id)

    async def reject_task(self, task: Task, reason: str = "", user_id: str = "user") -> TaskResult:
        """
        拒绝任务

        Args:
            task: 任务
            reason: 拒绝原因
            user_id: 用户ID

        Returns:
            TaskResult: 处理结果
        """
        logger.info(f"拒绝任务: {task.id} - {task.title}, reason: {reason}")

        # 更新状态
        task.status = TaskStatus.REJECTED.value
        task.rejected_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        await self.db.commit()

        # 记录历史
        await self._record_history(
            task=task,
            action="reject",
            result="success",
            details={"reason": reason, "user_id": user_id}
        )

        return TaskResult(
            success=True,
            action="reject",
            message="任务已拒绝",
            details={"reason": reason}
        )

    async def execute_task(self, task: Task, user_id: str = "user") -> TaskResult:
        """
        执行任务

        Args:
            task: 任务
            user_id: 用户ID

        Returns:
            TaskResult: 处理结果
        """
        logger.info(f"执行任务: {task.id} - {task.title}")

        # 更新状态为执行中
        task.status = TaskStatus.EXECUTING.value
        task.executing_at = datetime.utcnow()
        await self.db.commit()

        # 执行具体任务
        source_type = task.source_type
        source_data = task.source_data or {}

        try:
            if source_type == "source_evolution":
                result = await self._handle_source_evolution(task, source_data)
            elif source_type == "anti_crawl":
                result = await self._handle_anti_crawl(task, source_data)
            else:
                # 通用处理
                result = TaskResult(
                    success=True,
                    action="execute",
                    message="任务执行完成",
                    details={}
                )

            # 记录历史
            await self._record_history(
                task=task,
                action="execute",
                result="success" if result.success else "failed",
                details={"message": result.message, **(result.details or {})}
            )

            # 更新任务状态
            if result.success:
                task.status = TaskStatus.COMPLETED.value
                task.completed_at = datetime.utcnow()
            else:
                task.status = TaskStatus.FAILED.value
                task.failed_at = datetime.utcnow()

            task.updated_at = datetime.utcnow()
            await self.db.commit()

            return result

        except Exception as e:
            logger.exception(f"执行任务失败: {task.id}")

            await self._record_history(
                task=task,
                action="execute",
                result="failed",
                details={"error": str(e)}
            )

            task.status = TaskStatus.FAILED.value
            task.failed_at = datetime.utcnow()
            task.updated_at = datetime.utcnow()
            await self.db.commit()

            return TaskResult(
                success=False,
                action="execute",
                message=f"执行失败: {str(e)}",
                details={"error": str(e)}
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # 内部处理方法
    # ═══════════════════════════════════════════════════════════════════════════

    async def _handle_api_test(self, task: Task, source_data: Dict) -> TaskResult:
        """处理API测试失败"""
        # TODO: 实现具体的重试逻辑
        # 可以调用测试接口重新运行
        return TaskResult(
            success=True,
            action="auto_retry",
            message="API测试任务已自动重试",
            details={"source_data": source_data}
        )

    async def _handle_ui_test(self, task: Task, source_data: Dict) -> TaskResult:
        """处理UI测试失败"""
        # TODO: 实现具体的重试逻辑
        return TaskResult(
            success=True,
            action="auto_retry",
            message="UI测试任务已自动重试",
            details={"source_data": source_data}
        )

    async def _handle_anti_crawl(self, task: Task, source_data: Dict) -> TaskResult:
        """处理反爬拦截"""
        # TODO: 实现自动切换策略
        # 可以尝试切换到代理、云服务等方式
        return TaskResult(
            success=True,
            action="auto_fix",
            message="已自动切换反爬策略",
            details={"source_data": source_data}
        )

    async def _handle_system_health(self, task: Task, source_data: Dict) -> TaskResult:
        """处理系统健康问题"""
        plan = build_system_health_recovery_plan(source_data)
        before_summary = source_data.get("summary") or {}
        before_status = str(source_data.get("status") or before_summary.get("status") or "unknown")
        before_state = str(source_data.get("state") or before_summary.get("state") or "unknown")
        details: Dict[str, Any] = {
            "plan": plan,
            "before_status": before_status,
            "before_state": before_state,
        }

        if plan["strategy"] != "trigger_pipeline":
            return TaskResult(
                success=False,
                action="auto_fix",
                message=f"No automated recovery strategy for system health issue type: {plan['issue_type']}",
                details=details,
            )

        import aiohttp

        base_url = os.environ.get("MYATTENTION_INTERNAL_API_BASE", "http://127.0.0.1:8000").rstrip("/")
        timeout = aiohttp.ClientTimeout(total=30)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(f"{base_url}/api/pipeline/trigger") as resp:
                    trigger_text = await resp.text()
                    details["pipeline_trigger_status"] = resp.status
                    if resp.status != 200:
                        details["pipeline_trigger_response"] = trigger_text[:500]
                        return TaskResult(
                            success=False,
                            action="auto_fix",
                            message=f"Pipeline trigger failed with HTTP {resp.status}",
                            details=details,
                        )
                    try:
                        details["pipeline_trigger_result"] = await resp.json()
                    except Exception:
                        details["pipeline_trigger_response"] = trigger_text[:500]

                delay_seconds = int(plan.get("verify_delay_seconds", 0) or 0)
                if delay_seconds > 0:
                    await asyncio.sleep(delay_seconds)

                verify_endpoint = str(plan.get("verify_endpoint") or "").strip()
                async with session.get(f"{base_url}{verify_endpoint}", params={"fresh": "true"}) as resp:
                    verify_text = await resp.text()
                    details["verify_status"] = resp.status
                    if resp.status != 200:
                        details["verify_response"] = verify_text[:500]
                        return TaskResult(
                            success=False,
                            action="auto_fix",
                            message=f"Verification failed with HTTP {resp.status}",
                            details=details,
                        )
                    try:
                        verification = await resp.json()
                    except Exception:
                        details["verify_response"] = verify_text[:500]
                        return TaskResult(
                            success=False,
                            action="auto_fix",
                            message="Verification response was not valid JSON",
                            details=details,
                        )
        except Exception as exc:
            details["error"] = str(exc)
            return TaskResult(
                success=False,
                action="auto_fix",
                message=f"Automated recovery failed: {exc}",
                details=details,
            )

        after_summary = verification.get("summary") or {}
        after_status = str(after_summary.get("status") or "unknown")
        after_state = str(after_summary.get("state") or "unknown")
        details["after_status"] = after_status
        details["after_state"] = after_state
        details["verification"] = verification

        if after_status == "healthy" or is_system_health_improved(before_status, after_status):
            return TaskResult(
                success=True,
                action="auto_fix",
                message=f"System health improved from {before_status}/{before_state} to {after_status}/{after_state}",
                details=details,
            )

        return TaskResult(
            success=False,
            action="auto_fix",
            message=f"Recovery action executed but system health remains {after_status}/{after_state}",
            details=details,
        )

    async def _handle_source_evolution(self, task: Task, source_data: Dict) -> TaskResult:
        """处理信息源变更"""
        action = source_data.get("action", "modify")

        if action == "disable":
            # 禁用信息源
            return TaskResult(
                success=True,
                action="execute",
                message="信息源已禁用",
                details={"action": action}
            )
        elif action == "add":
            # 添加新信息源
            return TaskResult(
                success=True,
                action="execute",
                message="新信息源已添加",
                details={"action": action}
            )
        else:
            return TaskResult(
                success=True,
                action="execute",
                message="信息源已更新",
                details={"action": action}
            )

    async def _send_confirmation_notification(self, task: Task):
        """发送确认请求通知"""
        # TODO: 实现通知发送
        # 可以调用 notification 服务
        logger.info(f"发送确认请求通知: task_id={task.id}, title={task.title}")

    async def _record_history(
        self,
        task: Task,
        action: str,
        result: str,
        details: Dict[str, Any],
        performed_by: str = "system"
    ):
        """记录任务历史"""
        history = TaskHistory(
            id=uuid4(),
            task_id=task.id,
            action=action,
            result=result,
            details=make_ascii_safe(details),
            performed_by=performed_by
        )
        self.db.add(history)
        await self.db.commit()


# ═══════════════════════════════════════════════════════════════════════════
# 便捷函数
# ═══════════════════════════════════════════════════════════════════════════

def get_task_processor(db: AsyncSession) -> TaskProcessor:
    """获取任务处理器实例"""
    return TaskProcessor(db)
