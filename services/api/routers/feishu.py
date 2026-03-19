"""
飞书回调事件处理 - Feishu Callback Handler

用于接收飞书消息事件，实现双向通信：
1. 回调 URL 验证（飞书配置时需要）
2. 接收消息事件
3. 处理卡片回调

复用 OpenClaw 的飞书配置：直接读取 OpenClaw 的配置文件获取 app_id/app_secret
"""

import logging
import json
import os
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger("feishu.callback")

router = APIRouter()


def get_openclaw_feishu_config(account_id: str = "default") -> Optional[Dict[str, str]]:
    """
    从 OpenClaw 配置文件读取飞书配置

    Args:
        account_id: 飞书账号ID (default, researcher, claude_code, angela-main)

    Returns:
        包含 app_id 和 app_secret 的字典，如果没有配置则返回 None
    """
    openclaw_config_path = os.path.expanduser("~/.openclaw/openclaw.json")

    if not os.path.exists(openclaw_config_path):
        logger.warning(f"OpenClaw config not found at {openclaw_config_path}")
        return None

    try:
        import json
        with open(openclaw_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        feishu_config = config.get("channels", {}).get("feishu", {})
        accounts = feishu_config.get("accounts", {})

        # 优先使用指定的账号，否则使用 default
        account = accounts.get(account_id) or accounts.get("default")

        if not account:
            logger.warning(f"Feishu account '{account_id}' not found in OpenClaw config")
            return None

        app_id = account.get("appId")
        app_secret = account.get("appSecret")

        if app_id and app_secret:
            logger.info(f"Using OpenClaw Feishu account: {account_id}")
            return {"app_id": app_id, "app_secret": app_secret}

        return None

    except Exception as e:
        logger.error(f"Error reading OpenClaw config: {e}")
        return None


class FeishuCallbackRequest(BaseModel):
    """飞书回调请求体"""
    challenge: Optional[str] = None
    token: Optional[str] = None
    type: Optional[str] = None
    event: Optional[Dict[str, Any]] = None


class FeishuMessageEvent(BaseModel):
    """飞书消息事件"""
    message_id: str
    chat_id: str
    sender_id: Dict[str, str]
    message_type: str
    content: str
    create_time: str


# ═══════════════════════════════════════════════════════════════════════════
# 回调 URL 验证（飞书开放平台配置时需要）
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/feishu/callback")
async def verify_callback_url(
    challenge: str = Query(..., description="飞书发送的验证挑战"),
    token: str = Query(..., description="验证令牌")
):
    """
    飞书回调 URL 验证接口

    在飞书开放平台配置回调地址时，飞书会发送 GET 请求验证服务器。
    需要返回 challenge 作为响应。

    配置步骤：
    1. 在飞书开放平台 -> 你的应用 -> 事件订阅
    2. 回调地址填写: https://你的域名/api/feishu/callback
    3. 验证令牌(token) 填写: 在应用详情中设置并保存
    """
    logger.info(f"Feishu callback verification: token={token[:10]}...")

    # TODO: 验证 token 是否匹配配置的密钥
    # settings = get_settings()
    # if token != settings.feishu_verification_token:
    #     raise HTTPException(status_code=403, detail="Invalid token")

    return {"challenge": challenge}


@router.post("/feishu/callback")
async def handle_callback(request: Request):
    """
    处理飞书回调事件

    接收飞书推送的各种事件：
    - message: 收到新消息
    - card: 卡片交互回调
    - user_add: 用户添加
    - etc.
    """
    try:
        body = await request.json()
        logger.info(f"Feishu callback received: {body.get('type')}")

        event_type = body.get("type")

        if event_type == "url_verification":
            # URL 验证（POST 方式）
            return {"challenge": body.get("challenge")}

        elif event_type == "event":
            # 事件回调
            event = body.get("event", {})
            event_callback_type = event.get("type")

            if event_callback_type == "message":
                # 收到消息
                await handle_message_event(event)
            elif event_callback_type == "card":
                # 卡片回调
                await handle_card_callback(event)
            elif event_callback_type == "im.message":
                # 新版消息事件
                await handle_im_message(event)

        return {"code": 0}

    except Exception as e:
        logger.exception(f"Error handling Feishu callback: {e}")
        return {"code": -1, "msg": str(e)}


async def handle_message_event(event: Dict[str, Any]):
    """处理消息事件"""
    message = event.get("message", {})
    message_id = message.get("message_id")
    chat_id = message.get("chat_id")
    sender_id = message.get("sender_id", {})
    message_type = message.get("message_type")
    content = message.get("content", "")

    logger.info(f"Received message: chat={chat_id}, type={message_type}")

    # 根据消息类型处理
    if message_type == "text":
        # 处理文本消息
        try:
            content_dict = json.loads(content)
            text = content_dict.get("text", "")
            await process_text_message(chat_id, sender_id, text)
        except:
            pass
    elif message_type == "interactive":
        # 卡片消息
        pass


async def handle_card_callback(event: Dict[str, Any]):
    """处理卡片回调"""
    callback_id = event.get("callback_id")
    response_id = event.get("response_id")
    # 处理卡片按钮点击
    logger.info(f"Card callback: {callback_id}")


async def handle_im_message(event: Dict[str, Any]):
    """处理 IM 消息事件"""
    message = event.get("message", {})
    chat_id = message.get("chat_id")
    sender_id = message.get("sender_id", {})

    logger.info(f"IM message from chat: {chat_id}")

    # 可以在这里处理自动回复
    # await send_auto_reply(chat_id, sender_id, message)


async def process_text_message(chat_id: str, sender_id: Dict[str, Any], text: str):
    """
    处理收到的文本消息，可以用于智能对话

    这里可以接入 MyAttention 的对话功能
    """
    logger.info(f"Process text message: {text[:50]}...")

    # TODO: 将消息转发给 MyAttention 聊天系统
    # from routers.chat import chat_router
    # response = await chat_router.process_message(chat_id, text)

    # 可以选择是否自动回复
    # if should_auto_reply(text):
    #     await send_reply_message(chat_id, response)


# ═══════════════════════════════════════════════════════════════════════════
# 消息发送接口（用于主动发送消息给飞书）
# ═══════════════════════════════════════════════════════════════════════════

class SendMessageRequest(BaseModel):
    """发送消息请求"""
    receive_id: str  # 群聊 ID (oc_xxx) 或用户 ID (ou_xxx)
    msg_type: str = "text"
    content: str
    receive_id_type: str = "chat_id"  # chat_id 或 user_id


@router.post("/feishu/send")
async def send_feishu_message(request: SendMessageRequest, account_id: str = "default"):
    """
    发送消息到飞书

    需要在飞书应用配置中开启"发送消息"权限

    优先级：
    1. 前端设置页面保存的配置 (通知渠道)
    2. OpenClaw 配置
    3. 环境变量 FEISHU_APP_ID/FEISHU_APP_SECRET
    """
    from notifications.feishu import FeishuNotifier
    from config import get_settings

    # 1. 优先使用前端保存的渠道配置
    app_id = None
    app_secret = None
    default_target = request.receive_id  # 使用请求中的 receive_id 作为默认

    # 尝试从设置页面获取已保存的飞书配置
    try:
        from routers.settings import _channels
        feishu_channel = next((c for c in _channels if c.type == "feishu" and c.enabled), None)
        if feishu_channel and feishu_channel.app_id and feishu_channel.app_secret:
            app_id = feishu_channel.app_id
            app_secret = feishu_channel.app_secret
            default_target = feishu_channel.default_target_id or default_target
            logger.info("Using channel config from settings page")
    except Exception as e:
        logger.warning(f"Failed to get channel config: {e}")

    # 2. 回退到 OpenClaw 配置
    if not app_id or not app_secret:
        openclaw_config = get_openclaw_feishu_config(account_id)
        if openclaw_config:
            app_id = openclaw_config["app_id"]
            app_secret = openclaw_config["app_secret"]
            logger.info(f"Using OpenClaw Feishu config for account: {account_id}")

    # 3. 回退到环境变量
    if not app_id or not app_secret:
        settings = get_settings()
        app_id = settings.feishu_app_id
        app_secret = settings.feishu_app_secret

    if not app_id or not app_id.strip():
        raise HTTPException(status_code=400, detail="Feishu App not configured. Set in settings page, OpenClaw config, or FEISHU_APP_ID env.")
    if not app_secret or not app_secret.strip():
        raise HTTPException(status_code=400, detail="Feishu App secret not configured. Set in settings page, OpenClaw config, or FEISHU_APP_SECRET env.")

    notifier = FeishuNotifier(
        app_id=app_id,
        app_secret=app_secret,
        default_target_id=default_target
    )

    if request.msg_type == "text":
        success = await notifier.send_text(
            text=request.content,
            target_id=request.receive_id
        )
    else:
        success = await notifier.send_card(
            title="消息",
            content=request.content,
            target_id=request.receive_id
        )

    return {"success": success, "account_id": account_id}


@router.get("/feishu/config")
async def get_feishu_config_info():
    """
    获取飞书回调配置信息

    返回需要在飞书后台配置的信息
    """
    from config import get_settings
    import socket
    import os

    settings = get_settings()

    # 获取本机 IP
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    # 检查 OpenClaw 配置
    openclaw_config = get_openclaw_feishu_config()
    openclaw_available = openclaw_config is not None

    # 检查 MyAttention 配置
    myattention_configured = bool(settings.feishu_app_id and settings.feishu_app_secret)

    callback_url = f"http://{local_ip}:8000/api/feishu/callback"

    return {
        "callback_url": callback_url,
        "https_callback_url": "https://你的域名/api/feishu/callback",
        "note": "回调地址需要公网可访问，建议使用内网穿透或配置域名",
        "config_sources": {
            "openclaw": {
                "available": openclaw_available,
                "config_path": os.path.expanduser("~/.openclaw/openclaw.json"),
                "accounts": ["default", "researcher", "claude_code", "angela-main"]
            },
            "myattention_env": {
                "configured": myattention_configured,
                "env_vars": ["FEISHU_APP_ID", "FEISHU_APP_SECRET", "FEISHU_DEFAULT_TARGET_ID"]
            }
        },
        "active_config": "openclaw" if openclaw_available else ("myattention" if myattention_configured else "none"),
        "required_permissions": [
            "im:message",
            "im:chat:readonly",
            "im:message:send_as_bot"
        ]
    }


@router.get("/feishu/test-config")
async def test_feishu_config(account_id: str = "default"):
    """
    测试飞书配置是否正确

    尝试读取配置并获取 tenant_access_token 来验证凭据是否有效
    """
    from notifications.feishu import FeishuAppClient

    # 优先使用 OpenClaw 配置
    openclaw_config = get_openclaw_feishu_config(account_id)

    if openclaw_config:
        app_id = openclaw_config["app_id"]
        app_secret = openclaw_config["app_secret"]
        source = "openclaw"
    else:
        from config import get_settings
        settings = get_settings()
        app_id = settings.feishu_app_id
        app_secret = settings.feishu_app_secret
        source = "myattention"

    if not app_id or not app_secret:
        raise HTTPException(
            status_code=400,
            detail=f"No Feishu config found. Account: {account_id}. Set in .env or use OpenClaw config."
        )

    # 尝试获取 token 来验证凭据
    client = FeishuAppClient(app_id, app_secret)
    token = await client.get_tenant_access_token()

    if token:
        return {
            "status": "success",
            "source": source,
            "account_id": account_id,
            "app_id": app_id[:10] + "...",
            "message": "Feishu config is valid"
        }
    else:
        raise HTTPException(status_code=400, detail="Failed to get Feishu token. Check app_id and app_secret.")