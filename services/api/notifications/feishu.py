"""
Feishu (飞书) Notification Service

Supports three modes:
1. Webhook mode - Simple one-way push via custom robot webhook
2. App API mode - Full API access with App ID/Secret (supports sending to any chat)
3. WebSocket mode - Long connection for receiving events and messages

Based on:
- openclaw feishu-news-push skill
- Feishu Open Platform documentation
"""

from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import asyncio
import logging

import httpx

from config import get_settings

log = logging.getLogger("notifications.feishu")


@dataclass
class FeishuConfig:
    """飞书配置"""
    # Webhook 模式
    webhook_url: str = ""

    # 应用 API 模式
    app_id: str = ""
    app_secret: str = ""

    # 目标 ID（群聊 oc_xxx 或用户 ou_xxx）
    default_target_id: str = ""

    # WebSocket 模式
    enable_websocket: bool = False


class FeishuAppClient:
    """
    飞书应用 API 客户端

    使用 App ID 和 App Secret 进行认证，支持完整的飞书开放平台 API。

    功能:
    - 获取 tenant_access_token
    - 发送消息到任意群聊/用户
    - 上传文件
    - 管理群组
    """

    BASE_URL = "https://open.feishu.cn/open-apis"

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self._tenant_access_token: Optional[str] = None
        self._token_expires_at: float = 0
        self._last_error: Optional[dict] = None

    async def get_tenant_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        获取租户访问令牌

        tenant_access_token 有效期 2 小时，自动缓存和刷新。
        """
        import time

        # 检查缓存
        if not force_refresh and self._tenant_access_token:
            if time.time() < self._token_expires_at:
                return self._tenant_access_token

        url = f"{self.BASE_URL}/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data, timeout=10.0)
                result = response.json()

                if result.get("code") == 0:
                    self._tenant_access_token = result["tenant_access_token"]
                    # 提前 5 分钟过期
                    expire_seconds = result.get("expire", 7200)
                    self._token_expires_at = time.time() + expire_seconds - 300
                    log.info("Successfully obtained tenant_access_token")
                    return self._tenant_access_token
                else:
                    log.error(f"Failed to get token: {result}")
                    return None
        except Exception as e:
            log.error(f"Error getting token: {e}")
            return None

    async def _get_headers(self) -> Dict[str, str]:
        """获取带认证的请求头"""
        token = await self.get_tenant_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    async def send_message(
        self,
        receive_id: str,
        msg_type: str,
        content: str,
        receive_id_type: str = "chat_id"
    ) -> bool:
        """
        发送消息

        Args:
            receive_id: 接收者 ID（群聊 oc_xxx 或用户 ou_xxx）
            msg_type: 消息类型 (text, post, interactive, image, etc.)
            content: 消息内容 (JSON 字符串)
            receive_id_type: ID 类型 (chat_id, open_id, user_id)

        Returns:
            是否发送成功
        """
        headers = await self._get_headers()
        if not headers.get("Authorization"):
            return False

        url = f"{self.BASE_URL}/im/v1/messages?receive_id_type={receive_id_type}"
        data = {
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": content
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data, timeout=10.0)
                result = response.json()

                if result.get("code") == 0:
                    log.info(f"Message sent successfully to {receive_id}")
                    return True
                else:
                    log.error(f"Failed to send message: {result}")
                    self._last_error = result
                    return False
        except Exception as e:
            log.error(f"Error sending message: {e}")
            return False

    async def send_text(self, receive_id: str, text: str, receive_id_type: str = "chat_id") -> bool:
        """发送文本消息"""
        content = json.dumps({"text": text})
        return await self.send_message(receive_id, "text", content, receive_id_type)

    async def send_card(
        self,
        receive_id: str,
        title: str,
        content: str,
        color: str = "blue",
        button_text: str = None,
        button_url: str = None,
        receive_id_type: str = "chat_id"
    ) -> bool:
        """发送交互式卡片消息"""
        elements = [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": content
                }
            }
        ]

        if button_text and button_url:
            elements.append({
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": button_text
                        },
                        "type": "primary",
                        "url": button_url
                    }
                ]
            })

        card = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title
                },
                "template": color
            },
            "elements": elements
        }

        return await self.send_message(receive_id, "interactive", json.dumps(card), receive_id_type)

    async def send_news_card(
        self,
        receive_id: str,
        title: str,
        source: str,
        summary: str,
        url: str,
        urgency: float = 0.5,
        receive_id_type: str = "chat_id"
    ) -> bool:
        """发送新闻卡片"""
        # 根据紧急度选择颜色
        if urgency >= 0.85:
            color = "red"
            icon = "🔴"
        elif urgency >= 0.7:
            color = "orange"
            icon = "🟠"
        elif urgency >= 0.5:
            color = "yellow"
            icon = "🟡"
        else:
            color = "green"
            icon = "🟢"

        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        content = f"""**📰 来源:** {source}
**🕐 时间:** {now}

---

{summary}"""

        return await self.send_card(
            receive_id=receive_id,
            title=f"{icon} {title}",
            content=content,
            color=color,
            button_text="查看原文",
            button_url=url,
            receive_id_type=receive_id_type
        )

    async def send_daily_digest(
        self,
        receive_id: str,
        items: List[Dict[str, Any]],
        date: str = None,
        receive_id_type: str = "chat_id"
    ) -> bool:
        """发送每日简报"""
        if not items:
            return False

        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        now = datetime.now().strftime("%H:%M")

        # 构建内容
        content_lines = [f"**📅 {date} | 🕐 {now} 更新**\n"]

        # 高优先级新闻
        high_priority = [i for i in items if i.get("urgency", i.get("importance", 0)) >= 0.7]
        if high_priority:
            content_lines.append("**🔥 重点新闻**\n")
            for item in high_priority[:5]:
                title = item.get("title", "无标题")
                url = item.get("url", "#")
                source = item.get("source", "未知")
                content_lines.append(f"• [{title}]({url}) - {source}")
            content_lines.append("")

        # 其他新闻
        other_items = [i for i in items if i not in high_priority][:8]
        if other_items:
            content_lines.append("**📋 其他新闻**\n")
            for item in other_items:
                title = item.get("title", "无标题")
                url = item.get("url", "#")
                content_lines.append(f"• [{title}]({url})")
            content_lines.append("")

        # 统计
        total = len(items)
        high_count = len(high_priority)
        content_lines.append(f"---\n**总计:** {total} 条 | **高优先级:** {high_count} 条")

        content = "\n".join(content_lines)

        return await self.send_card(
            receive_id=receive_id,
            title="📰 每日简报",
            content=content,
            color="turquoise",
            button_text="查看全部",
            button_url="http://localhost:3000",
            receive_id_type=receive_id_type
        )


class FeishuWebSocketClient:
    """
    飞书 WebSocket 长连接客户端

    用于接收飞书事件和消息，实现双向通信。

    功能:
    - 建立 WebSocket 长连接
    - 接收消息事件
    - 接收卡片回调事件
    - 心跳保活
    """

    WS_URL = "wss://ws.feishu.cn/ws/v2/app-id/ticket"

    def __init__(
        self,
        app_client: FeishuAppClient,
        on_message: Callable = None,
        on_event: Callable = None
    ):
        self.app_client = app_client
        self.on_message = on_message
        self.on_event = on_event
        self._last_error = None
        self._running = False
        self._ws = None
        self._running = False
        self._ws = None

    async def get_ticket(self) -> Optional[str]:
        """获取 WebSocket 连接票据"""
        headers = await self.app_client._get_headers()
        if not headers.get("Authorization"):
            log.error("No Authorization header, cannot get ticket")
            return None

        url = f"{FeishuAppClient.BASE_URL}/auth/v3/app_ticket"
        log.info(f"Getting ticket from: {url}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, timeout=10.0)
                log.info(f"Ticket response status: {response.status_code}")

                # 尝试解析 JSON，失败时记录原始响应
                try:
                    result = response.json()
                except Exception as json_err:
                    log.error(f"Failed to parse JSON response: {json_err}, response text: {response.text[:500]}")
                    self._last_error = {"code": "parse_error", "msg": f"Invalid JSON response: {response.text[:200]}"}
                    return None

                if result.get("code") == 0:
                    return result.get("data", {}).get("ticket")
                else:
                    log.error(f"Failed to get ticket: {result}")
                    # 存储错误信息供调用方使用
                    self._last_error = result
                    return None
        except Exception as e:
            log.error(f"Error getting ticket: {e}")
            self._last_error = {"code": "exception", "msg": str(e)}
            return None

    @property
    def last_error(self):
        """获取最近一次错误信息"""
        return getattr(self, '_last_error', None)

    async def connect(self):
        """建立 WebSocket 连接"""
        ticket = await self.get_ticket()
        if not ticket:
            log.error("Cannot connect: failed to get ticket")
            return

        ws_url = f"wss://ws.feishu.cn/ws/v2/{self.app_client.app_id}/{ticket}"

        try:
            import websockets

            self._running = True
            async with websockets.connect(ws_url) as ws:
                self._ws = ws
                log.info("WebSocket connected to Feishu")

                async for message in ws:
                    if not self._running:
                        break

                    try:
                        data = json.loads(message)
                        await self._handle_message(data)
                    except json.JSONDecodeError:
                        log.warning(f"Invalid JSON message: {message[:100]}")

        except ImportError:
            log.warning("websockets package not installed. WebSocket mode disabled.")
            log.info("Install with: pip install websockets")
        except Exception as e:
            log.error(f"WebSocket error: {e}")
        finally:
            self._ws = None
            self._running = False

    async def _handle_message(self, data: Dict[str, Any]):
        """处理接收到的消息"""
        msg_type = data.get("type")

        if msg_type == "pong":
            # 心跳响应，忽略
            return

        log.debug(f"Received message type: {msg_type}")

        # 调用回调
        if self.on_message:
            try:
                await self.on_message(data)
            except Exception as e:
                log.error(f"Error in message handler: {e}")

        # 处理特定事件
        if msg_type == "event":
            event = data.get("event", {})
            event_type = event.get("type")

            if event_type == "message":
                # 收到消息
                if self.on_event:
                    await self.on_event("message", event)

            elif event_type == "card":
                # 卡片回调
                if self.on_event:
                    await self.on_event("card", event)

    async def send_pong(self):
        """发送心跳"""
        if self._ws:
            await self._ws.send(json.dumps({"type": "pong"}))

    def stop(self):
        """停止连接"""
        self._running = False


class FeishuNotifier:
    """
    飞书通知服务 - 统一接口

    支持三种模式:
    1. Webhook 模式 - 简单推送
    2. App API 模式 - 完整 API 功能
    3. WebSocket 模式 - 接收事件和消息

    使用方法:
    ```python
    # Webhook 模式
    notifier = FeishuNotifier(webhook_url="https://...")

    # App API 模式
    notifier = FeishuNotifier(app_id="cli_xxx", app_secret="xxx", default_target_id="oc_xxx")

    # 发送消息
    await notifier.send_text("Hello!")
    await notifier.send_card("标题", "内容")
    await notifier.send_news_card(...)
    ```
    """

    def __init__(
        self,
        webhook_url: str = None,
        app_id: str = None,
        app_secret: str = None,
        default_target_id: str = None,
        enable_websocket: bool = False
    ):
        settings = get_settings()

        # 配置
        self.webhook_url = webhook_url or settings.feishu_webhook_url
        self.app_id = app_id or settings.feishu_app_id
        self.app_secret = app_secret or settings.feishu_app_secret
        self.default_target_id = default_target_id or ""

        # 客户端
        self._app_client: Optional[FeishuAppClient] = None
        self._ws_client: Optional[FeishuWebSocketClient] = None

        # 初始化应用客户端
        if self.app_id and self.app_secret:
            self._app_client = FeishuAppClient(self.app_id, self.app_secret)

            if enable_websocket:
                self._ws_client = FeishuWebSocketClient(self._app_client)

    @property
    def app_client(self) -> Optional[FeishuAppClient]:
        """获取应用 API 客户端"""
        return self._app_client

    # ==================== Webhook 模式 ====================

    async def send_text_webhook(self, text: str) -> bool:
        """通过 Webhook 发送文本消息"""
        if not self.webhook_url:
            return False

        payload = {
            "msg_type": "text",
            "content": {"text": text}
        }

        return await self._send_webhook(payload)

    async def send_card_webhook(
        self,
        title: str,
        content: str,
        color: str = "blue",
        button_text: str = None,
        button_url: str = None
    ) -> bool:
        """通过 Webhook 发送卡片消息"""
        if not self.webhook_url:
            return False

        elements = [
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": content}
            }
        ]

        if button_text and button_url:
            elements.append({
                "tag": "action",
                "actions": [{
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": button_text},
                    "type": "primary",
                    "url": button_url
                }]
            })

        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": title},
                    "template": color
                },
                "elements": elements
            }
        }

        return await self._send_webhook(payload)

    async def _send_webhook(self, payload: Dict[str, Any]) -> bool:
        """发送 Webhook 请求"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10.0
                )
                result = response.json()
                return result.get("code") == 0 or result.get("StatusCode") == 0
        except Exception as e:
            log.error(f"Webhook send failed: {e}")
            return False

    # ==================== 统一发送接口 ====================

    async def send_text(self, text: str, target_id: str = None) -> bool:
        """
        发送文本消息

        优先使用 App API 模式，回退到 Webhook 模式
        """
        if self._app_client:
            target = target_id or self.default_target_id
            if target:
                return await self._app_client.send_text(target, text)

        return await self.send_text_webhook(text)

    async def send_card(
        self,
        title: str,
        content: str,
        color: str = "blue",
        button_text: str = None,
        button_url: str = None,
        target_id: str = None
    ) -> bool:
        """
        发送卡片消息

        优先使用 App API 模式，回退到 Webhook 模式
        """
        if self._app_client:
            target = target_id or self.default_target_id
            if target:
                return await self._app_client.send_card(
                    target, title, content, color, button_text, button_url
                )

        return await self.send_card_webhook(title, content, color, button_text, button_url)

    async def send_news_card(
        self,
        title: str,
        source: str,
        summary: str,
        url: str,
        category: str = "新闻",
        urgency: float = 0.5,
        target_id: str = None
    ) -> bool:
        """发送新闻卡片"""
        if self._app_client:
            target = target_id or self.default_target_id
            if target:
                return await self._app_client.send_news_card(
                    target, title, source, summary, url, urgency
                )

        # Webhook 模式
        return await self.send_card_webhook(
            title=f"📰 {title}",
            content=f"**来源:** {source}\n\n{summary}",
            color="blue",
            button_text="查看原文",
            button_url=url
        )

    async def send_daily_digest(
        self,
        items: List[Dict[str, Any]],
        date: str = None,
        target_id: str = None
    ) -> bool:
        """发送每日简报"""
        if self._app_client:
            target = target_id or self.default_target_id
            if target:
                return await self._app_client.send_daily_digest(target, items, date)

        # Webhook 模式
        if not items:
            return False

        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        now = datetime.now().strftime("%H:%M")

        content_lines = [f"**📅 {date} | 🕐 {now} 更新**\n"]
        content_lines.append(f"**总计:** {len(items)} 条新闻\n")

        for i, item in enumerate(items[:8], 1):
            title = item.get("title", "无标题")
            url = item.get("url", "#")
            content_lines.append(f"{i}. [{title}]({url})")

        return await self.send_card_webhook(
            title="📰 每日简报",
            content="\n".join(content_lines),
            color="turquoise"
        )

    async def send_urgent_alert(
        self,
        title: str,
        content: str,
        source: str,
        url: str = None,
        target_id: str = None
    ) -> bool:
        """发送紧急提醒"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        alert_content = f"""**🚨 紧急信息**

**来源:** {source}
**时间:** {now}

---

{content}"""

        return await self.send_card(
            title=f"⚠️ {title}",
            content=alert_content,
            color="red",
            button_text="查看原文" if url else None,
            button_url=url,
            target_id=target_id
        )

    # ==================== WebSocket 模式 ====================

    async def start_websocket(self, on_message: Callable = None, on_event: Callable = None):
        """启动 WebSocket 长连接"""
        if not self._ws_client:
            log.warning("WebSocket client not initialized. Set enable_websocket=True")
            return

        if on_message:
            self._ws_client.on_message = on_message
        if on_event:
            self._ws_client.on_event = on_event

        await self._ws_client.connect()

    def stop_websocket(self):
        """停止 WebSocket 连接"""
        if self._ws_client:
            self._ws_client.stop()

    # ==================== 测试 ====================

    async def test(self) -> bool:
        """测试连接"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self._app_client and self.default_target_id:
            # 测试 App API 模式
            return await self._app_client.send_card(
                self.default_target_id,
                "🔔 MyAttention 通知测试",
                f"**测试时间:** {now}\n\n✅ 飞书 App API 连接成功！",
                "blue"
            )

        # 测试 Webhook 模式
        return await self.send_card_webhook(
            title="🔔 MyAttention 通知测试",
            content=f"**测试时间:** {now}\n\n✅ 飞书 Webhook 连接成功！",
            color="blue"
        )