# MyAttention 推送功能

## 概述

MyAttention 支持飞书和钉钉两种推送渠道，提供多种消息模板和格式支持。

## 飞书配置

飞书支持两种配置模式：

### 模式1: 应用 API 模式（推荐）

使用飞书开放平台应用 API，功能完整：

1. 在 [飞书开发者后台](https://open.feishu.cn/app) 创建企业自建应用
2. 获取 App ID 和 App Secret
3. 开通应用权限：
   - `im:message` - 获取与发送消息
   - `im:chat` - 获取群组信息
   - `im:chat:readonly` - 读取群组信息
4. 将应用添加到目标群聊
5. 获取群聊 ID：群设置 → 群信息 → 会话 ID

```bash
# .env 配置
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FEISHU_DEFAULT_TARGET_ID=oc_xxxxxxxxxxxxxxxxxxxxx
```

**优势**：
- 支持发送到任意群聊或用户
- 支持接收消息事件（需启用 WebSocket）
- 支持更丰富的消息格式
- 支持消息卡片交互

### 模式2: Webhook 模式

简单的单向推送：

1. 打开飞书群聊 → 群设置 → 群机器人
2. 点击「添加机器人」→ 选择「自定义机器人」
3. 复制 Webhook 地址

```bash
# .env 配置
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
```

## 钉钉配置

### Webhook 模式

1. 打开钉钉群聊 → 群设置 → 智能群助手
2. 点击「添加机器人」→ 选择「自定义」
3. 安全设置选择「加签」（推荐）
4. 复制 Webhook 地址和签名密钥

```bash
# .env 配置
DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=xxx
DINGTALK_SECRET=SECxxxxxxxx
```

## API 接口

### 测试通知

```bash
# 测试已配置的渠道
POST /api/settings/notifications/channels/{channel_id}/test
{
    "title": "测试通知",
    "message": "这是一条测试消息"
}

# 快速测试（无需保存配置）
POST /api/settings/notifications/send-test
{
    "channel_type": "feishu",
    "webhook_url": "https://...",
    "secret": "SECxxx",
    "title": "测试通知",
    "message": "这是一条测试消息"
}
```

### 发送每日简报

```bash
POST /api/settings/notifications/send-digest
{
    "channel_type": "feishu",
    "webhook_url": "https://..."
}
```

## 代码示例

### Python 后端调用

```python
from notifications import FeishuNotifier, DingTalkNotifier, get_notification_manager

# === 飞书应用 API 模式（推荐）===
feishu = FeishuNotifier(
    app_id="cli_xxx",
    app_secret="xxx",
    default_target_id="oc_xxx"  # 默认群聊
)

# 发送新闻卡片
await feishu.send_news_card(
    title="OpenAI 发布 GPT-5",
    source="机器之心",
    summary="OpenAI 今日正式发布 GPT-5，性能提升显著...",
    url="https://example.com/news/123",
    urgency=0.9
)

# 发送每日简报
await feishu.send_daily_digest([
    {"title": "新闻1", "url": "...", "source": "来源1", "urgency": 0.8},
    {"title": "新闻2", "url": "...", "source": "来源2", "urgency": 0.6},
])

# === 飞书 Webhook 模式 ===
feishu_webhook = FeishuNotifier(webhook_url="https://...")
await feishu_webhook.send_card(
    title="标题",
    content="内容",
    button_text="查看详情",
    button_url="https://..."
)

# === 钉钉 ===
dingtalk = DingTalkNotifier(
    webhook_url="https://...",
    secret="SECxxx"
)
await dingtalk.send_news_card(
    title="新闻标题",
    source="来源",
    summary="摘要...",
    url="https://...",
    urgency=0.8
)

# === 使用统一管理器（多渠道同时推送）===
manager = get_notification_manager()

# 配置飞书应用模式
manager.configure_feishu_app(
    app_id="cli_xxx",
    app_secret="xxx",
    default_target_id="oc_xxx"
)

# 配置钉钉
manager.configure_dingtalk(webhook_url="https://...", secret="SECxxx")

# 同时推送到两个渠道
results = await manager.send_news_card(
    title="重要新闻",
    source="来源",
    summary="摘要内容",
    url="https://...",
    urgency=0.8
)
# results: {"feishu": True, "dingtalk": True}
```

### WebSocket 长连接（接收消息）

```python
from notifications import FeishuNotifier

async def on_message(data):
    """收到消息回调"""
    print(f"Received: {data}")

async def on_event(event_type, event):
    """收到事件回调"""
    if event_type == "message":
        # 处理收到的消息
        message = event.get("message")
        print(f"Message: {message}")
    elif event_type == "card":
        # 处理卡片回调
        print(f"Card action: {event}")

# 启用 WebSocket 长连接
feishu = FeishuNotifier(
    app_id="cli_xxx",
    app_secret="xxx",
    default_target_id="oc_xxx",
    enable_websocket=True
)

# 启动 WebSocket 连接
await feishu.start_websocket(on_message=on_message, on_event=on_event)
```

## 消息模板

### 1. 新闻卡片

根据紧急度自动选择颜色和图标：
- 🔴 紧急 (urgency >= 0.85)
- 🟠 重要 (urgency >= 0.7)
- 🟡 一般 (urgency >= 0.5)
- 🟢 低 (urgency < 0.5)

### 2. 每日简报

自动分类显示新闻，包含统计信息。

### 3. 紧急提醒

高亮显示紧急信息，支持跳转链接。

## 消息格式规范

### 飞书

- 使用交互式卡片
- 支持按钮跳转
- 支持颜色主题
- 支持 Markdown 格式 (lark_md)

### 钉钉

- 使用 Markdown 格式
- 支持 @所有人
- 支持签名验证

### 链接格式

```markdown
正确格式:
[**标题**](https://example.com)

错误格式:
[标题](example.com)  # 缺少 https://
```

## 故障排除

### 飞书推送失败

1. **App API 模式**
   - 检查 App ID 和 App Secret 是否正确
   - 确认应用已添加到目标群聊
   - 检查应用权限配置

2. **Webhook 模式**
   - 检查 Webhook URL 是否正确
   - 确认机器人仍在群中

### 钉钉推送失败

1. 检查 Webhook URL 和 Secret 是否匹配
2. 确认安全设置（关键词/IP/加签）
3. 检查系统时间是否准确（签名验证需要）

### WebSocket 连接失败

1. 确保已安装 `websockets` 包: `pip install websockets`
2. 检查网络连接
3. 确认应用有接收消息的权限