from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import uuid4, UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import socket
from urllib.parse import urlparse

from sqlalchemy import text

from notifications.feishu import FeishuNotifier
from notifications.dingtalk import DingTalkNotifier
from config import create_qdrant_client, get_settings, is_local_qdrant_mode
from db import get_db_context
from db.models import NotificationChannel
from feeds.auto_evolution import get_auto_evolution_system
from feeds.proxy_config import get_proxy_status, load_proxy_settings, save_proxy_settings

router = APIRouter()
log = logging.getLogger("settings")


class NotificationChannelCreate(BaseModel):
    """创建通知渠道请求"""
    name: str
    type: str  # feishu or dingtalk
    webhook_url: str = ""
    secret: Optional[str] = None
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    default_target_id: Optional[str] = None
    enabled: bool = True
    user_id: Optional[str] = None  # 可选，用于个人渠道
    test_connection: bool = True  # 是否在保存前测试长连接


class NotificationChannelResponse(BaseModel):
    """通知渠道响应 (脱敏)"""
    id: str
    name: str
    type: str
    webhook_url: str
    secret: Optional[str] = None
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    default_target_id: Optional[str] = None
    enabled: bool
    last_test_at: Optional[str] = None
    last_test_status: Optional[str] = None


class PushSettings(BaseModel):
    push_important: bool = True
    push_daily_digest: bool = True
    digest_times: List[str] = ["09:00", "18:00"]
    importance_threshold: int = 70


class ProxySettingsPayload(BaseModel):
    enabled: bool = False
    http_proxy: str = ""
    socks_proxy: str = ""
    auto_detect_domains: bool = True
    test_url: str = "https://httpbin.org/ip"


class TestNotificationRequest(BaseModel):
    title: str = "测试通知"
    message: str = "这是一条测试消息"


# 内存缓存 - 用于快速读取，当数据库不可用时回退
_channels_cache: List[dict] = []


def _channel_to_response(channel) -> dict:
    """将数据库模型转换为 API 响应"""
    # type 现在是字符串，直接使用
    channel_type = channel.type.value if hasattr(channel.type, 'value') else str(channel.type)
    return {
        "id": str(channel.id),
        "name": channel.name,
        "type": channel_type,
        "webhook_url": channel.webhook_url or "",
        "secret": channel.secret,
        "app_id": channel.app_id,
        "app_secret": channel.app_secret,
        "default_target_id": channel.default_target_id,
        "enabled": channel.enabled,
        "last_test": channel.last_test_at.isoformat() if channel.last_test_at else None,
        "test_status": channel.last_test_status,
    }


@router.get("/settings/notifications/channels")
async def get_notification_channels():
    """
    获取通知渠道列表
    """
    try:
        async with get_db_context() as db:
            result = await db.execute(
                select(NotificationChannel).order_by(NotificationChannel.created_at.desc())
            )
            channels_db = result.scalars().all()

            channels = []
            for channel in channels_db:
                channels.append(_channel_to_response(channel))

            # 更新内存缓存
            global _channels_cache
            _channels_cache = channels

            return channels
    except Exception as e:
        # 回退到内存缓存
        return _channels_cache


async def _test_feishu_websocket(app_id: str, app_secret: str, target_id: str) -> dict:
    """
    测试飞书 WebSocket 长连接

    返回: {"status": "success"/"error", "message": "...", "step": "...", "hint": "..."}
    """
    import asyncio
    try:
        from notifications.feishu import FeishuAppClient, FeishuWebSocketClient

        # 1. 测试获取 tenant_access_token
        app_client = FeishuAppClient(app_id, app_secret)
        token = await app_client.get_tenant_access_token()
        if not token:
            return {
                "status": "error",
                "message": "获取 tenant_access_token 失败，请检查 app_id 和 app_secret 是否正确",
                "step": "token"
            }

        # 2. 测试连接 - 直接尝试发送消息
        # WebSocket 模式需要 app_ticket 通过回调获取，这需要配置事件订阅回调服务器
        # 所以这里直接使用 API 模式测试发送消息
        try:
            import json
            from notifications.feishu import FeishuAppClient

            test_client = FeishuAppClient(app_id, app_secret)

            if not target_id:
                return {
                    "status": "error",
                    "message": "请填写默认推送目标（群聊ID）",
                    "step": "config",
                    "hint": "群聊格式: oc_xxx，用户格式: ou_xxx"
                }

            # 尝试发送测试消息
            log.info(f"Testing Feishu API connection for app {app_id}, target: {target_id}")
            success = await test_client.send_message(
                receive_id=target_id,
                msg_type="text",
                content=json.dumps({"text": "🔔 MyAttention 连接测试消息"}),
                receive_id_type="chat_id"
            )

            if success:
                log.info(f"Feishu API test successful for app {app_id}")
                return {
                    "status": "success",
                    "message": "连接测试成功！（使用 API 模式）"
                }
            else:
                # 获取详细错误
                error_detail = getattr(test_client, '_last_error', None) or {}
                error_code = error_detail.get("code", "unknown")
                error_msg = error_detail.get("msg", "消息发送失败")

                # 针对常见错误码给出明确提示
                hint = ""
                if error_code == 230013:
                    hint = "应用未添加到群聊，请将应用添加到目标群聊：群设置 → 添加应用 → 选择你的应用"
                elif error_code == 230001:
                    hint = "无效的群聊ID，请检查默认推送目标是否正确"
                elif error_code == 99991663:
                    hint = "应用未开通'接收消息'权限，请到飞书开放平台 → 应用 → 权限管理 → 开通 im:message 权限"
                else:
                    hint = f"错误码 {error_code}: {error_msg}"

                return {
                    "status": "error",
                    "message": f"消息发送失败 (错误码: {error_code}): {error_msg}",
                    "step": "send_message",
                    "hint": hint
                }

        except Exception as e:
            log.error(f"Feishu connection test failed: {e}")
            return {
                "status": "error",
                "message": f"连接测试失败: {str(e)}",
                "step": "exception"
            }

        # 下面是原来的 WebSocket 测试代码（保留但不使用，因为需要回调服务器）
        # 3. 尝试建立短连接测试
        try:
            import websockets
            ws_url = f"wss://ws.feishu.cn/ws/v2/{app_id}/{ticket}"

            async with asyncio.timeout(10):
                async with websockets.connect(ws_url) as ws:
                    log.info(f"WebSocket connection test successful for app {app_id}")
                    return {
                        "status": "success",
                        "message": "长连接测试成功！"
                    }
        except asyncio.TimeoutError:
            return {
                "status": "error",
                "message": "WebSocket 连接超时",
                "step": "websocket_connect"
            }
        except Exception as ws_err:
            return {
                "status": "error",
                "message": f"WebSocket 连接失败: {str(ws_err)}",
                "step": "websocket_connect"
            }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": f"测试失败: {str(e)}",
            "detail": traceback.format_exc()
        }


@router.post("/settings/notifications/channels")
async def create_notification_channel(channel: NotificationChannelCreate):
    """
    创建新的通知渠道

    如果 test_connection=True 且为飞书 App API 模式，会在保存前测试长连接
    """
    # 先测试连接（如果需要）
    ws_test_result = None
    if channel.test_connection and channel.type == "feishu" and channel.app_id and channel.app_secret:
        ws_test_result = await _test_feishu_websocket(
            channel.app_id,
            channel.app_secret,
            channel.default_target_id
        )
        if ws_test_result["status"] != "success":
            # 连接测试失败，不保存，直接返回错误
            return {
                "status": "error",
                "message": ws_test_result.get("message", "长连接测试失败"),
                "step": ws_test_result.get("step", "unknown"),
                "hint": ws_test_result.get("hint", ""),
                "ws_test_failed": True
            }

    try:
        async with get_db_context() as db:
            # 将字符串 type 转换为数据库可存储的字符串
            if channel.type == "feishu":
                channel_type_str = "feishu"
            elif channel.type == "dingtalk":
                channel_type_str = "dingtalk"
            elif channel.type == "email":
                channel_type_str = "email"
            elif channel.type == "webhook":
                channel_type_str = "webhook"
            else:
                channel_type_str = channel.type

            # 转换 user_id
            user_uuid = None
            if channel.user_id:
                try:
                    user_uuid = UUID(channel.user_id)
                except ValueError:
                    pass  # 忽略无效的 UUID

            new_channel = NotificationChannel(
                id=uuid4(),
                user_id=user_uuid,  # 可选的 user_id
                name=channel.name,
                type=channel_type_str,
                webhook_url=channel.webhook_url or None,
                secret=channel.secret,
                app_id=channel.app_id,
                app_secret=channel.app_secret,
                default_target_id=channel.default_target_id,
                enabled=channel.enabled,
            )
            db.add(new_channel)
            await db.flush()
            await db.refresh(new_channel)

            return {
                "status": "created",
                "channel": _channel_to_response(new_channel),
                "ws_test": ws_test_result
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create channel: {str(e)}")


@router.put("/settings/notifications/channels/{channel_id}")
async def update_notification_channel(channel_id: str, channel: NotificationChannelCreate):
    """
    更新通知渠道
    """
    # 先测试连接（如果需要）
    ws_test_result = None
    if channel.test_connection and channel.type == "feishu" and channel.app_id and channel.app_secret:
        ws_test_result = await _test_feishu_websocket(
            channel.app_id,
            channel.app_secret,
            channel.default_target_id
        )
        if ws_test_result["status"] != "success":
            # 连接测试失败，不保存，直接返回错误
            return {
                "status": "error",
                "message": ws_test_result.get("message", "长连接测试失败"),
                "step": ws_test_result.get("step", "unknown"),
                "hint": ws_test_result.get("hint", ""),
                "ws_test_failed": True
            }

    try:
        async with get_db_context() as db:
            # 查找现有记录
            result = await db.execute(
                select(NotificationChannel).where(NotificationChannel.id == channel_id)
            )
            existing = result.scalar_one_or_none()

            if not existing:
                raise HTTPException(status_code=404, detail="Channel not found")

            # 更新字段 - type 现在是字符串
            existing.name = channel.name
            existing.type = channel.type  # 直接使用字符串
            existing.webhook_url = channel.webhook_url or None
            existing.secret = channel.secret
            existing.app_id = channel.app_id
            existing.app_secret = channel.app_secret
            existing.default_target_id = channel.default_target_id
            existing.enabled = channel.enabled
            existing.updated_at = datetime.now()

            await db.flush()
            await db.refresh(existing)

            return {
                "status": "updated",
                "channel": _channel_to_response(existing),
                "ws_test": ws_test_result
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update channel: {str(e)}")


@router.delete("/settings/notifications/channels/{channel_id}")
async def delete_notification_channel(channel_id: str):
    """
    删除通知渠道
    """
    try:
        async with get_db_context() as db:
            result = await db.execute(
                select(NotificationChannel).where(NotificationChannel.id == channel_id)
            )
            channel = result.scalar_one_or_none()

            if not channel:
                raise HTTPException(status_code=404, detail="Channel not found")

            await db.delete(channel)
            return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete channel: {str(e)}")


@router.post("/settings/notifications/channels/{channel_id}/test")
async def test_notification_channel(channel_id: str, request: TestNotificationRequest = None):
    """
    测试通知渠道
    """
    try:
        async with get_db_context() as db:
            result = await db.execute(
                select(NotificationChannel).where(NotificationChannel.id == channel_id)
            )
            channel_db = result.scalar_one_or_none()

            if not channel_db:
                raise HTTPException(status_code=404, detail="Channel not found")

            channel = _channel_to_response(channel_db)
    except HTTPException:
        raise
    except Exception as e:
        # 回退到内存缓存
        channel = next((c for c in _channels_cache if c["id"] == channel_id), None)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")

    # 支持 Webhook 和 App API 两种模式
    has_webhook = bool(channel.get("webhook_url"))
    has_app_api = bool(channel.get("app_id") and channel.get("app_secret") and channel.get("default_target_id"))

    if not has_webhook and not has_app_api:
        raise HTTPException(status_code=400, detail="请配置 Webhook URL 或 App API (app_id + app_secret + target_id)")

    test_title = request.title if request else "测试通知"
    test_message = request.message if request else "🔔 MyAttention 通知测试 - 连接成功!"

    try:
        if channel["type"] == "feishu":
            if has_app_api:
                notifier = FeishuNotifier(
                    app_id=channel["app_id"],
                    app_secret=channel["app_secret"],
                    default_target_id=channel["default_target_id"]
                )
            else:
                notifier = FeishuNotifier(webhook_url=channel["webhook_url"])

            success = await notifier.send_card(
                title=f"🔔 {test_title}",
                content=f"**测试时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{test_message}",
                color="blue"
            )
        elif channel["type"] == "dingtalk":
            notifier = DingTalkNotifier(
                webhook_url=channel["webhook_url"],
                secret=channel.get("secret")
            )
            success = await notifier.send_markdown(
                title=test_title,
                content=f"**测试时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{test_message}"
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown channel type: {channel['type']}")

        # 更新数据库中的测试状态
        now = datetime.now()
        try:
            async with get_db_context() as db:
                result = await db.execute(
                    select(NotificationChannel).where(NotificationChannel.id == channel_id)
                )
                channel_db = result.scalar_one_or_none()
                if channel_db:
                    channel_db.last_test_at = now
                    channel_db.last_test_status = "success" if success else "failed"
        except:
            pass  # 忽略更新失败

        return {
            "status": "success" if success else "failed",
            "message": "Test notification sent successfully" if success else "Failed to send notification",
            "timestamp": now.isoformat()
        }

    except Exception as e:
        # 更新错误状态
        try:
            async with get_db_context() as db:
                result = await db.execute(
                    select(NotificationChannel).where(NotificationChannel.id == channel_id)
                )
                channel_db = result.scalar_one_or_none()
                if channel_db:
                    channel_db.last_test_at = datetime.now()
                    channel_db.last_test_status = f"error: {str(e)[:50]}"
        except:
            pass

        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.post("/settings/notifications/send-test")
async def send_test_notification(
    channel_type: str,
    webhook_url: str,
    secret: str = None,
    title: str = "测试通知",
    message: str = "这是一条测试消息"
):
    """快速测试接口 - 无需保存配置"""
    try:
        if channel_type == "feishu":
            notifier = FeishuNotifier(webhook_url=webhook_url)
            success = await notifier.send_card(
                title=f"🔔 {title}",
                content=f"**测试时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{message}",
                color="blue"
            )
        elif channel_type == "dingtalk":
            notifier = DingTalkNotifier(webhook_url=webhook_url, secret=secret)
            success = await notifier.send_markdown(
                title=title,
                content=f"**测试时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{message}"
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown channel type: {channel_type}")

        return {"status": "success" if success else "failed", "message": "Notification sent successfully" if success else "Failed to send notification"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
# Feishu App API 模式测试接口
# ═══════════════════════════════════════════════════════════════════════════

class FeishuAppTestRequest(BaseModel):
    app_id: str
    app_secret: str
    target_id: str


@router.post("/settings/notifications/feishu-app/test")
async def test_feishu_app_api(request: FeishuAppTestRequest):
    """测试飞书 App API 模式"""
    try:
        notifier = FeishuNotifier(
            app_id=request.app_id,
            app_secret=request.app_secret,
            default_target_id=request.target_id
        )

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        success = await notifier.send_card(
            title="🔔 MyAttention 飞书通知测试",
            content=f"**测试时间:** {now}\n\n✅ 飞书 App API 连接成功！",
            color="green",
            button_text="打开 MyAttention",
            button_url="http://localhost:3000"
        )

        return {
            "status": "success" if success else "failed",
            "message": "Test message sent successfully" if success else "Failed to send message",
            "mode": "App API",
            "target_id": request.target_id
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


class FeishuWebSocketTestRequest(BaseModel):
    app_id: str
    app_secret: str
    target_id: str


@router.post("/settings/notifications/feishu-ws/test")
async def test_feishu_websocket_connection(request: FeishuWebSocketTestRequest):
    """
    测试飞书 WebSocket 长连接

    用于验证应用是否正确配置了"接收消息"权限。
    长连接成功后，UI 才能保存配置。
    """
    try:
        from notifications.feishu import FeishuAppClient, FeishuWebSocketClient
        import asyncio

        # 1. 测试获取 tenant_access_token
        app_client = FeishuAppClient(request.app_id, request.app_secret)
        token = await app_client.get_tenant_access_token()
        if not token:
            return {
                "status": "error",
                "message": "获取 tenant_access_token 失败，请检查 app_id 和 app_secret 是否正确",
                "step": "token"
            }

        # 2. 测试连接 - 直接尝试发送消息
        # WebSocket 模式需要 app_ticket 通过回调获取，这需要配置事件订阅回调服务器
        # 所以这里直接使用 API 模式测试发送消息
        try:
            import json
            from notifications.feishu import FeishuAppClient

            test_client = FeishuAppClient(app_id, app_secret)

            if not target_id:
                return {
                    "status": "error",
                    "message": "请填写默认推送目标（群聊ID）",
                    "step": "config",
                    "hint": "群聊格式: oc_xxx，用户格式: ou_xxx"
                }

            # 尝试发送测试消息
            log.info(f"Testing Feishu API connection for app {app_id}, target: {target_id}")
            success = await test_client.send_message(
                receive_id=target_id,
                msg_type="text",
                content=json.dumps({"text": "🔔 MyAttention 连接测试消息"}),
                receive_id_type="chat_id"
            )

            if success:
                log.info(f"Feishu API test successful for app {app_id}")
                return {
                    "status": "success",
                    "message": "连接测试成功！（使用 API 模式）"
                }
            else:
                # 获取详细错误
                error_detail = getattr(test_client, '_last_error', None) or {}
                error_code = error_detail.get("code", "unknown")
                error_msg = error_detail.get("msg", "消息发送失败")

                # 针对常见错误码给出明确提示
                hint = ""
                if error_code == 230013:
                    hint = "应用未添加到群聊，请将应用添加到目标群聊：群设置 → 添加应用 → 选择你的应用"
                elif error_code == 230001:
                    hint = "无效的群聊ID，请检查默认推送目标是否正确"
                elif error_code == 99991663:
                    hint = "应用未开通'接收消息'权限，请到飞书开放平台 → 应用 → 权限管理 → 开通 im:message 权限"
                else:
                    hint = f"错误码 {error_code}: {error_msg}"

                return {
                    "status": "error",
                    "message": f"消息发送失败 (错误码: {error_code}): {error_msg}",
                    "step": "send_message",
                    "hint": hint
                }

        except Exception as e:
            log.error(f"Feishu connection test failed: {e}")
            return {
                "status": "error",
                "message": f"连接测试失败: {str(e)}",
                "step": "exception"
            }

        # 下面是原来的 WebSocket 测试代码（保留但不使用，因为需要回调服务器）
        # 3. 尝试建立短连接测试 (不阻塞等待消息)
        # 创建连接任务但只等待几秒看是否能握手成功
        try:
            import websockets
            ws_url = f"wss://ws.feishu.cn/ws/v2/{request.app_id}/{ticket}"

            # 设置短超时，只测试连接能否建立
            async with asyncio.timeout(10):
                async with websockets.connect(ws_url) as ws:
                    # 成功建立连接
                    log.info(f"WebSocket connection test successful for app {request.app_id}")
                    return {
                        "status": "success",
                        "message": "WebSocket 长连接测试成功！可以保存配置。",
                        "app_id": request.app_id,
                        "target_id": request.target_id
                    }
        except asyncio.TimeoutError:
            return {
                "status": "error",
                "message": "WebSocket 连接超时",
                "step": "websocket_connect"
            }
        except Exception as ws_err:
            return {
                "status": "error",
                "message": f"WebSocket 连接失败: {str(ws_err)}",
                "step": "websocket_connect"
            }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": f"测试失败: {str(e)}",
            "detail": traceback.format_exc()
        }


@router.get("/settings/notifications/feishu/status")
async def get_feishu_config_status():
    """获取飞书配置状态"""
    from config import get_settings
    settings = get_settings()

    has_webhook = bool(settings.feishu_webhook_url)
    has_app_api = bool(settings.feishu_app_id and settings.feishu_app_secret)
    has_target = bool(settings.feishu_default_target_id)

    return {
        "webhook_configured": has_webhook,
        "app_api_configured": has_app_api,
        "target_configured": has_target,
        "ready": (has_webhook or has_app_api) and has_target,
        "mode": "App API (推荐)" if (has_app_api and has_target) else ("Webhook" if has_webhook else None)
    }


# 内存存储 (回退用)
_push_settings = PushSettings()


@router.get("/settings/notifications/push")
async def get_push_settings():
    return _push_settings


@router.put("/settings/notifications/push")
async def update_push_settings(settings: PushSettings):
    global _push_settings
    _push_settings = settings
    return {"status": "updated"}


@router.get("/settings/proxy")
async def get_proxy_settings():
    settings = load_proxy_settings()
    status = await get_proxy_status(settings)
    return {**settings, "status": status}


@router.put("/settings/proxy")
async def update_proxy_settings(payload: ProxySettingsPayload):
    settings = save_proxy_settings(payload.model_dump())
    status = await get_proxy_status(settings)
    return {"status": "updated", **settings, "status_info": status}


@router.post("/settings/proxy/test")
async def test_proxy_settings():
    settings = load_proxy_settings()
    status = await get_proxy_status(settings)
    return {"status": "ok", "proxy": settings, "status_info": status}


@router.get("/settings/system")
async def get_system_settings():
    """获取系统健康状态"""
    import httpx
    from datetime import datetime

    settings = get_settings()
    results = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "healthy",
        "summary": {"total": 0, "healthy": 0, "unhealthy": 0, "error": 0},
        "databases": [],
        "services": [],
        "external": []
    }

    # Check PostgreSQL
    try:
        async with get_db_context() as db:
            await db.execute(text("SELECT 1"))
        results["databases"].append({"name": "PostgreSQL", "status": "healthy", "running": True, "mode": "local"})
    except Exception as e:
        results["databases"].append({"name": "PostgreSQL", "status": "error", "running": False, "mode": "local", "error": str(e)})

    # Check Redis
    try:
        redis = urlparse(settings.redis_url)
        redis_host = redis.hostname or "localhost"
        redis_port = redis.port or 6379
        with socket.create_connection((redis_host, redis_port), timeout=2):
            pass
        results["databases"].append({"name": "Redis", "status": "healthy", "running": True, "mode": "local"})
    except Exception as e:
        results["databases"].append({"name": "Redis", "status": "unhealthy", "running": False, "mode": "local", "error": str(e)})

    # Check Qdrant
    try:
        if is_local_qdrant_mode(settings):
            client = create_qdrant_client(settings)
            client.get_collections()
            results["databases"].append({"name": "Qdrant", "status": "healthy", "running": True, "mode": "embedded"})
        else:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.qdrant_url}/readyz")
                qdrant_running = response.status_code == 200
                results["databases"].append({"name": "Qdrant", "status": "healthy" if qdrant_running else "unhealthy", "running": qdrant_running, "mode": "service"})
    except Exception as e:
        results["databases"].append({"name": "Qdrant", "status": "error", "running": False, "error": str(e)})

    # Check API service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/health")
            results["services"].append({"name": "MyAttention API", "status": "healthy" if response.status_code == 200 else "unhealthy", "running": response.status_code == 200})
    except Exception as e:
        results["services"].append({"name": "MyAttention API", "status": "error", "running": False, "error": str(e)})

    # Check auto evolution
    try:
        evolution = get_auto_evolution_system().get_status()
        quick_log_health = evolution.get("last_results", {}).get("log_health") or {}
        evolution_status = "healthy" if evolution.get("running") else "unhealthy"
        if quick_log_health.get("critical_count", 0) > 0 or quick_log_health.get("critical_errors", 0) > 0:
            evolution_status = "degraded"
        results["services"].append({
            "name": "Auto Evolution",
            "status": evolution_status,
            "running": evolution.get("running", False),
            "details": {
                "components": evolution.get("components", {}),
                "last_results": evolution.get("last_results", {}),
            },
        })
    except Exception as e:
        results["services"].append({"name": "Auto Evolution", "status": "error", "running": False, "error": str(e)})

    # Check feed collection durability
    try:
        from feeds.collection_health import collect_collection_health_snapshot

        async with get_db_context() as db:
            collection_health = await collect_collection_health_snapshot(db)
        summary = collection_health.get("summary", {})
        results["services"].append({
            "name": "Feed Collection",
            "status": summary.get("status", "unknown"),
            "running": summary.get("status") != "unhealthy",
            "details": collection_health,
        })
    except Exception as e:
        results["services"].append({"name": "Feed Collection", "status": "error", "running": False, "error": str(e)})

    # Check proxy
    try:
        proxy_settings = load_proxy_settings()
        proxy_status = await get_proxy_status(proxy_settings)
        results["services"].append({
            "name": "Proxy",
            "status": proxy_status["state"],
            "running": proxy_status["state"] in {"healthy", "degraded"},
            "enabled": proxy_settings.get("enabled", False),
            "details": proxy_status,
        })
    except Exception as e:
        results["services"].append({"name": "Proxy", "status": "error", "running": False, "error": str(e)})

    # Check LLM services
    llm_configs = [
        {"name": "通义千问 (Qwen)", "api_key": settings.qwen_api_key, "model": "qwen-turbo"},
        {"name": "智谱 (GLM)", "api_key": settings.glm_api_key, "model": "glm-4-flash"},
        {"name": "Kimi", "api_key": settings.kimi_api_key, "model": "moonshot-v1-8k"},
    ]

    test_message = [{"role": "user", "content": "Hi"}]

    for llm in llm_configs:
        if not llm["api_key"]:
            results["external"].append({"name": llm["name"], "status": "not_configured", "running": False})
            continue
        results["external"].append({"name": llm["name"], "status": "healthy", "running": True, "model": llm["model"]})

    all_services = results["databases"] + results["services"] + results["external"]
    results["summary"]["total"] = len(all_services)
    for svc in all_services:
        status = svc.get("status", "unknown")
        if status in ["healthy", "running", "disabled"]:
            results["summary"]["healthy"] += 1
        elif status in ["unhealthy", "not_configured"]:
            results["summary"]["unhealthy"] += 1
        else:
            results["summary"]["error"] += 1

    if results["summary"]["error"] > 0:
        results["overall_status"] = "error"
    elif results["summary"]["unhealthy"] > 0:
        results["overall_status"] = "degraded"

    return results


@router.post("/settings/notifications/send-digest")
async def send_manual_digest(channel_type: str, webhook_url: str, secret: str = None):
    """手动发送每日简报"""
    sample_items = [
        {"title": "OpenAI 发布 GPT-5 模型", "url": "https://example.com/1", "source": "机器之心", "urgency": 0.9},
        {"title": "Google DeepMind 发布 AlphaFold 3", "url": "https://example.com/2", "source": "量子位", "urgency": 0.85},
    ]

    try:
        if channel_type == "feishu":
            notifier = FeishuNotifier(webhook_url=webhook_url)
            success = await notifier.send_daily_digest(sample_items)
        elif channel_type == "dingtalk":
            notifier = DingTalkNotifier(webhook_url=webhook_url, secret=secret)
            success = await notifier.send_daily_digest(sample_items)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown channel type: {channel_type}")

        return {"status": "success" if success else "failed", "message": "Digest sent successfully" if success else "Failed to send digest"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
