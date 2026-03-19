"""
任务通知服务 - Task Notification Service
专门用于任务系统的通知功能
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

from notifications import (
    NotificationManager,
    NotificationChannel,
    get_notification_manager
)
from notifications.feishu import FeishuNotifier
from notifications.dingtalk import DingTalkNotifier
from db.models import Task, TaskPriority, TaskStatus

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# 动态获取已配置的渠道设置
# ═══════════════════════════════════════════════════════════════════════════

def _get_configured_channels() -> List[Dict[str, Any]]:
    """
    从 settings.py 获取已配置的渠道设置

    这样任务通知可以使用 UI 中配置的设置
    """
    try:
        # 导入 settings router 中的 channel 配置
        from routers.settings import _channels
        return [
            {
                "type": c.type,
                "enabled": c.enabled,
                "webhook_url": c.webhook_url,
                "secret": c.secret,
                "app_id": getattr(c, 'app_id', None),
                "app_secret": getattr(c, 'app_secret', None),
                "default_target_id": getattr(c, 'default_target_id', None),
            }
            for c in _channels if c.enabled
        ]
    except Exception as e:
        logger.warning(f"无法读取渠道配置: {e}")
        return []


# 优先级到通知渠道的映射
PRIORITY_CHANNELS = {
    0: ["feishu", "dingtalk"],  # P0 紧急：多渠道
    1: ["feishu"],  # P1 重要：飞书
    2: [],  # P2 普通：仅汇总
    3: [],  # P3 建议：仅汇总
}


class TaskNotificationService:
    """任务通知服务 - 发送任务相关通知"""

    def __init__(self, notification_manager: NotificationManager = None):
        self.notification_manager = notification_manager or get_notification_manager()

    async def _send_via_channel(self, channel_config: Dict[str, Any], title: str, content: str) -> bool:
        """
        使用渠道配置发送通知
        """
        try:
            if channel_config["type"] == "feishu":
                # 优先使用 App API 模式
                if channel_config.get("app_id") and channel_config.get("app_secret") and channel_config.get("default_target_id"):
                    notifier = FeishuNotifier(
                        app_id=channel_config["app_id"],
                        app_secret=channel_config["app_secret"],
                        default_target_id=channel_config["default_target_id"]
                    )
                elif channel_config.get("webhook_url"):
                    notifier = FeishuNotifier(webhook_url=channel_config["webhook_url"])
                else:
                    logger.warning("飞书渠道未配置 App API 或 Webhook")
                    return False

                return await notifier.send_card(
                    title=title,
                    content=content,
                    color="red" if "紧急" in title else "blue"
                )

            elif channel_config["type"] == "dingtalk":
                if not channel_config.get("webhook_url"):
                    logger.warning("钉钉渠道未配置 Webhook")
                    return False

                notifier = DingTalkNotifier(
                    webhook_url=channel_config["webhook_url"],
                    secret=channel_config.get("secret")
                )
                return await notifier.send_markdown(title=title, content=content)

            return False
        except Exception as e:
            logger.error(f"发送通知失败: {e}")
            return False

    async def _get_enabled_channels(self, priority: int) -> List[Dict[str, Any]]:
        """获取指定优先级需要发送的渠道"""
        channel_types = PRIORITY_CHANNELS.get(priority, [])
        all_channels = _get_configured_channels()

        # 过滤出需要发送的渠道类型
        enabled = []
        for ch in all_channels:
            if ch["type"] in channel_types and ch["enabled"]:
                enabled.append(ch)

        return enabled

    async def notify_task_created(self, task: Task) -> Dict[str, bool]:
        """
        通知任务创建

        Args:
            task: 创建的任务

        Returns:
            Dict[str, bool]: 各渠道发送结果
        """
        # 获取通知渠道
        channels = await self._get_enabled_channels(task.priority)

        if not channels:
            # 如果没有配置渠道，回退到旧的 NotificationManager
            channels = PRIORITY_CHANNELS.get(task.priority, [])
            if not channels:
                logger.debug(f"P{task.priority} 级别任务不需要即时通知")
                return {}

            # 使用旧的 NotificationManager
            legacy_channels = [NotificationChannel.FEISHU] if "feishu" in channels else []
            if task.priority == 0:
                return await self._send_urgent_alert_legacy(task, legacy_channels)
            elif task.priority == 1:
                return await self._send_confirmation_request_legacy(task, legacy_channels)
            return {}

        # 根据优先级构建消息
        if task.priority == 0:
            # P0 紧急：发送告警
            return await self._send_urgent_alert(task, channels)
        elif task.priority == 1:
            # P1 重要：发送确认请求
            return await self._send_confirmation_request(task, channels)
        else:
            # P2/P3：静默处理
            return {}

    async def _send_urgent_alert(self, task: Task, channels: List[Dict[str, Any]]) -> Dict[str, bool]:
        """发送紧急告警（使用动态配置）"""
        priority_emoji = {0: "🔴", 1: "🟡", 2: "🟢", 3: "⚪"}
        emoji = priority_emoji.get(task.priority, "⚪")

        title = f"{emoji} 紧急任务 - P{task.priority}"
        content = f"**任务:** {task.title}\n\n" \
                  f"**描述:** {task.description or '无'}\n\n" \
                  f"**来源:** {task.source_type}\n" \
                  f"**分类:** {task.category or '未知'}\n\n" \
                  f"👉 [查看任务](/evolution/tasks/{task.id})"

        results = {}
        for ch in channels:
            results[ch["type"]] = await self._send_via_channel(ch, title, content)

        return results

    async def _send_confirmation_request(self, task: Task, channels: List[Dict[str, Any]]) -> Dict[str, bool]:
        """发送确认请求（使用动态配置）"""
        title = f"📋 需要确认的任务 - P{task.priority}"
        content = f"**任务:** {task.title}\n\n" \
                  f"**描述:** {task.description or '无'}\n\n" \
                  f"**分类:** {task.category or '未知'}\n\n" \
                  f"请确认是否执行此任务。\n\n" \
                  f"👉 [确认执行](/evolution/tasks/{task.id}/action?action=confirm)\n" \
                  f"👉 [拒绝任务](/evolution/tasks/{task.id}/action?action=reject)"

        results = {}
        for ch in channels:
            results[ch["type"]] = await self._send_via_channel(ch, title, content)

        return results

    async def notify_task_timeout(self, task: Task) -> Dict[str, bool]:
        """
        通知任务超时
        """
        channels = await self._get_enabled_channels(task.priority)

        message = f"⏰ **任务超时提醒**\n\n" \
                  f"**任务:** {task.title}\n" \
                  f"**优先级:** P{task.priority}\n" \
                  f"**状态:** {task.status}\n\n" \
                  f"请尽快处理！"

        title = "⏰ 任务超时提醒"
        logger.warning(f"任务超时通知: task_id={task.id}")

        results = {}
        if channels:
            for ch in channels:
                results[ch["type"]] = await self._send_via_channel(ch, title, message)
        else:
            # 回退到旧方式
            return await self.notification_manager.send_text(text=message)

        return results

    async def notify_task_completed(self, task: Task) -> Dict[str, bool]:
        """
        通知任务完成（可选）
        """
        # 仅对 P0 任务发送完成通知
        if task.priority != 0:
            return {}

        channels = await self._get_enabled_channels(task.priority)

        title = "✅ 任务已自动处理完成"
        content = f"**任务:** {task.title}\n" \
                  f"**优先级:** P{task.priority}"

        if channels:
            results = {}
            for ch in channels:
                results[ch["type"]] = await self._send_via_channel(ch, title, content)
            return results
        else:
            # 回退到旧方式
            message = f"✅ 任务已自动处理完成\n\n任务: {task.title}\n优先级: P{task.priority}"
            return await self.notification_manager.send_text(text=message)

    # ═══════════════════════════════════════════════════════════════════════════
    # 回退方法（使用旧 NotificationManager）
    # ═══════════════════════════════════════════════════════════════════════════

    async def _send_urgent_alert_legacy(self, task: Task, channels: List[NotificationChannel]) -> Dict[str, bool]:
        """使用旧方式发送紧急告警（回退用）"""
        priority_emoji = {0: "🔴", 1: "🟡", 2: "🟢", 3: "⚪"}
        emoji = priority_emoji.get(task.priority, "⚪")

        title = f"{emoji} 紧急任务 - P{task.priority}"
        content = f"任务: {task.title}\n\n描述: {task.description or '无'}\n\n来源: {task.source_type}\n分类: {task.category or '未知'}"

        try:
            return await self.notification_manager.send_important_alert(
                title=title,
                content=content,
                source="MyAttention 任务系统",
                url=f"/tasks/{task.id}",
                channels=channels
            )
        except Exception as e:
            logger.exception(f"发送紧急告警失败: {e}")
            return {"error": str(e)}

    async def _send_confirmation_request_legacy(self, task: Task, channels: List[NotificationChannel]) -> Dict[str, bool]:
        """使用旧方式发送确认请求（回退用）"""
        message = f"📋 需要确认的任务\n\n任务: {task.title}\n\n描述: {task.description or '无'}\n\n优先级: P{task.priority} (重要)\n分类: {task.category or '未知'}\n\n请确认是否执行此任务。"

        try:
            return await self.notification_manager.send_text(text=message, channels=channels)
        except Exception as e:
            logger.exception(f"发送确认请求失败: {e}")
            return {"error": str(e)}

    async def send_daily_task_summary(self, tasks: List[Task], date: str = None) -> Dict[str, bool]:
        """
        发送每日任务汇总

        Args:
            tasks: 任务列表
            date: 日期

        Returns:
            Dict[str, bool]: 各渠道发送结果
        """
        if not tasks:
            return {}

        # 统计各类任务
        pending = [t for t in tasks if t.status == TaskStatus.PENDING.value]
        completed = [t for t in tasks if t.status == TaskStatus.COMPLETED.value]
        failed = [t for t in tasks if t.status == TaskStatus.FAILED.value]

        # 按优先级统计
        p0_count = len([t for t in tasks if t.priority == 0])
        p1_count = len([t for t in tasks if t.priority == 1])

        # 构建汇总消息
        summary_items = []

        if pending:
            summary_items.append({
                "title": f"待处理任务 ({len(pending)})",
                "content": "\n".join([f"- {t.title[:40]}" for t in pending[:5]])
            })

        if failed:
            summary_items.append({
                "title": f"处理失败 ({len(failed)})",
                "content": "\n".join([f"- {t.title[:40]}" for t in failed[:3]])
            })

        if not summary_items:
            summary_items.append({
                "title": "任务状态",
                "content": "今日无新增任务"
            })

        # 添加统计信息
        stats = f"📊 任务统计\n" \
                f"- 总计: {len(tasks)}\n" \
                f"- P0紧急: {p0_count}\n" \
                f"- P1重要: {p1_count}\n" \
                f"- 已完成: {len(completed)}"

        summary_items.insert(0, {"title": "统计", "content": stats})

        try:
            return await self.notification_manager.send_daily_digest(
                items=summary_items,
                date=date
            )
        except Exception as e:
            logger.exception(f"发送每日汇总失败: {e}")
            return {"error": str(e)}

    async def _send_urgent_alert(self, task: Task, channels: List[NotificationChannel]) -> Dict[str, bool]:
        """发送紧急告警"""
        priority_emoji = {
            0: "🔴",
            1: "🟡",
            2: "🟢",
            3: "⚪"
        }

        emoji = priority_emoji.get(task.priority, "⚪")

        title = f"{emoji} 紧急任务 - P{task.priority}"
        content = f"任务: {task.title}\n\n" \
                  f"描述: {task.description or '无'}\n\n" \
                  f"来源: {task.source_type}\n" \
                  f"分类: {task.category or '未知'}"

        try:
            return await self.notification_manager.send_important_alert(
                title=title,
                content=content,
                source="MyAttention 任务系统",
                url=f"/tasks/{task.id}",
                channels=channels
            )
        except Exception as e:
            logger.exception(f"发送紧急告警失败: {e}")
            return {"error": str(e)}

    async def _send_confirmation_request(self, task: Task, channels: List[NotificationChannel]) -> Dict[str, bool]:
        """发送确认请求"""
        message = f"📋 需要确认的任务\n\n" \
                  f"任务: {task.title}\n\n" \
                  f"描述: {task.description or '无'}\n\n" \
                  f"优先级: P{task.priority} (重要)\n" \
                  f"分类: {task.category or '未知'}\n\n" \
                  f"请确认是否执行此任务。\n" \
                  f"操作链接: /evolution/tasks/{task.id}"

        try:
            return await self.notification_manager.send_text(
                text=message,
                channels=channels
            )
        except Exception as e:
            logger.exception(f"发送确认请求失败: {e}")
            return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
# 便捷函数
# ═══════════════════════════════════════════════════════════════════════════

_notification_service: Optional[TaskNotificationService] = None


def get_task_notification_service() -> TaskNotificationService:
    """获取任务通知服务实例"""
    global _notification_service
    if _notification_service is None:
        _notification_service = TaskNotificationService()
    return _notification_service