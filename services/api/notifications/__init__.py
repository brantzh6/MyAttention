"""
Notification Services

Unified interface for sending notifications through various channels.

Feishu modes:
- Webhook: Simple one-way push via custom robot
- App API: Full API with App ID/Secret
- WebSocket: Long connection for receiving events
"""

from typing import Dict, Any, List, Optional
from enum import Enum

from .feishu import (
    FeishuNotifier,
    FeishuAppClient,
    FeishuWebSocketClient,
    FeishuConfig,
)
from .dingtalk import DingTalkNotifier, DingTalkMessage


class NotificationChannel(str, Enum):
    FEISHU = "feishu"
    DINGTALK = "dingtalk"


class NotificationManager:
    """
    统一通知管理器

    支持多渠道通知发送

    Feishu 配置:
    - Webhook 模式: configure_feishu(webhook_url="...")
    - App API 模式: configure_feishu_app(app_id="...", app_secret="...", target_id="...")
    """

    def __init__(self):
        self._feishu: Optional[FeishuNotifier] = None
        self._dingtalk: Optional[DingTalkNotifier] = None

    def configure_feishu(
        self,
        webhook_url: str = None,
        app_id: str = None,
        app_secret: str = None,
        default_target_id: str = None,
        enable_websocket: bool = False
    ) -> None:
        """
        配置飞书通知

        支持两种模式:
        1. Webhook 模式: 只需传入 webhook_url
        2. App API 模式: 传入 app_id, app_secret, default_target_id
        """
        self._feishu = FeishuNotifier(
            webhook_url=webhook_url,
            app_id=app_id,
            app_secret=app_secret,
            default_target_id=default_target_id,
            enable_websocket=enable_websocket
        )

    def configure_feishu_app(
        self,
        app_id: str,
        app_secret: str,
        default_target_id: str,
        enable_websocket: bool = False
    ) -> None:
        """配置飞书应用 API 模式（推荐）"""
        self._feishu = FeishuNotifier(
            app_id=app_id,
            app_secret=app_secret,
            default_target_id=default_target_id,
            enable_websocket=enable_websocket
        )

    def configure_dingtalk(self, webhook_url: str, secret: str = None) -> None:
        """配置钉钉通知"""
        self._dingtalk = DingTalkNotifier(webhook_url=webhook_url, secret=secret)
    
    async def send_text(
        self,
        text: str,
        channels: List[NotificationChannel] = None,
    ) -> Dict[str, bool]:
        """发送文本消息到指定渠道"""
        channels = channels or [NotificationChannel.FEISHU, NotificationChannel.DINGTALK]
        results = {}
        
        if NotificationChannel.FEISHU in channels and self._feishu:
            results["feishu"] = await self._feishu.send_text(text)
        
        if NotificationChannel.DINGTALK in channels and self._dingtalk:
            results["dingtalk"] = await self._dingtalk.send_text(text)
        
        return results
    
    async def send_daily_digest(
        self,
        items: List[Dict[str, Any]],
        date: str = None,
        channels: List[NotificationChannel] = None,
    ) -> Dict[str, bool]:
        """发送每日简报"""
        channels = channels or [NotificationChannel.FEISHU, NotificationChannel.DINGTALK]
        results = {}
        
        if NotificationChannel.FEISHU in channels and self._feishu:
            results["feishu"] = await self._feishu.send_daily_digest(items, date)
        
        if NotificationChannel.DINGTALK in channels and self._dingtalk:
            results["dingtalk"] = await self._dingtalk.send_daily_digest(items, date)
        
        return results
    
    async def send_important_alert(
        self,
        title: str,
        content: str,
        source: str,
        url: str = None,
        channels: List[NotificationChannel] = None,
    ) -> Dict[str, bool]:
        """发送重要提醒"""
        channels = channels or [NotificationChannel.FEISHU, NotificationChannel.DINGTALK]
        results = {}

        if NotificationChannel.FEISHU in channels and self._feishu:
            results["feishu"] = await self._feishu.send_urgent_alert(
                title, content, source, url
            )

        if NotificationChannel.DINGTALK in channels and self._dingtalk:
            results["dingtalk"] = await self._dingtalk.send_urgent_alert(
                title, content, source, url
            )

        return results

    async def send_news_card(
        self,
        title: str,
        source: str,
        summary: str,
        url: str,
        category: str = "新闻",
        urgency: float = 0.5,
        channels: List[NotificationChannel] = None,
    ) -> Dict[str, bool]:
        """发送新闻卡片"""
        channels = channels or [NotificationChannel.FEISHU, NotificationChannel.DINGTALK]
        results = {}

        if NotificationChannel.FEISHU in channels and self._feishu:
            results["feishu"] = await self._feishu.send_news_card(
                title, source, summary, url, category, urgency
            )

        if NotificationChannel.DINGTALK in channels and self._dingtalk:
            results["dingtalk"] = await self._dingtalk.send_news_card(
                title, source, summary, url, category, urgency
            )

        return results

    async def send_morning_brief(
        self,
        items: List[Dict[str, Any]],
        date: str = None,
        channels: List[NotificationChannel] = None,
    ) -> Dict[str, bool]:
        """发送早间简报"""
        channels = channels or [NotificationChannel.FEISHU, NotificationChannel.DINGTALK]
        results = {}

        # 早间简报使用每日简报格式
        if NotificationChannel.FEISHU in channels and self._feishu:
            results["feishu"] = await self._feishu.send_daily_digest(items, date)

        if NotificationChannel.DINGTALK in channels and self._dingtalk:
            results["dingtalk"] = await self._dingtalk.send_morning_brief(items, date)

        return results

    async def send_evening_brief(
        self,
        items: List[Dict[str, Any]],
        date: str = None,
        channels: List[NotificationChannel] = None,
    ) -> Dict[str, bool]:
        """发送晚间简报"""
        channels = channels or [NotificationChannel.FEISHU, NotificationChannel.DINGTALK]
        results = {}

        # 晚间简报使用每日简报格式
        if NotificationChannel.FEISHU in channels and self._feishu:
            results["feishu"] = await self._feishu.send_daily_digest(items, date)

        if NotificationChannel.DINGTALK in channels and self._dingtalk:
            results["dingtalk"] = await self._dingtalk.send_evening_brief(items, date)

        return results
    
    async def test_channel(self, channel: NotificationChannel) -> bool:
        """测试指定渠道"""
        if channel == NotificationChannel.FEISHU and self._feishu:
            return await self._feishu.test()
        if channel == NotificationChannel.DINGTALK and self._dingtalk:
            return await self._dingtalk.test()
        return False


# Singleton instance
_notification_manager: Optional[NotificationManager] = None


def get_notification_manager() -> NotificationManager:
    """获取通知管理器实例"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager


__all__ = [
    # Feishu
    "FeishuNotifier",
    "FeishuAppClient",
    "FeishuWebSocketClient",
    "FeishuConfig",
    # DingTalk
    "DingTalkNotifier",
    "DingTalkMessage",
    # Manager
    "NotificationChannel",
    "NotificationManager",
    "get_notification_manager",
]
