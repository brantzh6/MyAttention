"""
DingTalk (钉钉) Notification Service

Enhanced implementation based on openclaw dingtalk-push skill.
Supports text, Markdown, link, ActionCard with HMAC signing.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import hashlib
import hmac
import base64
import time
import urllib.parse
import httpx

from config import get_settings


@dataclass
class DingTalkMessage:
    """钉钉消息结构"""
    title: str
    content: str
    link: Optional[str] = None
    importance: str = "normal"


class DingTalkNotifier:
    """
    钉钉 Webhook 通知服务

    支持:
    - 文本消息
    - Markdown 消息
    - 链接消息
    - ActionCard 消息
    - HMAC 签名验证
    - 新闻推送模板
    - 每日简报

    使用方法:
    ```python
    notifier = DingTalkNotifier()

    # 发送新闻卡片
    await notifier.send_news_card(
        title="OpenAI 发布 GPT-5",
        source="机器之心",
        summary="OpenAI 今日正式发布 GPT-5...",
        url="https://example.com/news/123",
        urgency=0.85
    )

    # 发送每日简报
    await notifier.send_daily_digest([
        {"title": "新闻1", "url": "...", "source": "来源1"},
        {"title": "新闻2", "url": "...", "source": "来源2"},
    ])
    ```
    """

    def __init__(self, webhook_url: str = None, secret: str = None):
        settings = get_settings()
        self.webhook_url = webhook_url or settings.dingtalk_webhook_url
        self.secret = secret or settings.dingtalk_secret

    def _get_signed_url(self) -> str:
        """生成带签名的 URL (安全模式)"""
        if not self.secret:
            return self.webhook_url

        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{self.secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

        return f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"

    async def send_text(self, text: str, at_all: bool = False, at_mobiles: List[str] = None) -> bool:
        """发送纯文本消息"""
        if not self.webhook_url:
            return False

        payload = {
            "msgtype": "text",
            "text": {
                "content": text
            },
            "at": {
                "isAtAll": at_all,
                "atMobiles": at_mobiles or []
            }
        }

        return await self._send(payload)

    async def send_markdown(
        self,
        title: str,
        content: str,
        at_all: bool = False,
        at_mobiles: List[str] = None
    ) -> bool:
        """发送 Markdown 消息"""
        if not self.webhook_url:
            return False

        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": content
            },
            "at": {
                "isAtAll": at_all,
                "atMobiles": at_mobiles or []
            }
        }

        return await self._send(payload)

    async def send_link(
        self,
        title: str,
        text: str,
        message_url: str,
        pic_url: str = None,
    ) -> bool:
        """发送链接消息"""
        if not self.webhook_url:
            return False

        payload = {
            "msgtype": "link",
            "link": {
                "title": title,
                "text": text,
                "messageUrl": message_url,
                "picUrl": pic_url or ""
            }
        }

        return await self._send(payload)

    async def send_action_card(
        self,
        title: str,
        content: str,
        button_text: str = "查看详情",
        button_url: str = None,
    ) -> bool:
        """发送 ActionCard 消息"""
        if not self.webhook_url:
            return False

        payload = {
            "msgtype": "actionCard",
            "actionCard": {
                "title": title,
                "text": content,
                "singleTitle": button_text,
                "singleURL": button_url or "http://localhost:3000"
            }
        }

        return await self._send(payload)

    async def send_news_card(
        self,
        title: str,
        source: str,
        summary: str,
        url: str,
        category: str = "新闻",
        urgency: float = 0.5,
        at_all: bool = False
    ) -> bool:
        """
        发送新闻卡片 (基于 openclaw 模板)

        Args:
            title: 新闻标题
            source: 新闻来源
            summary: 摘要内容
            url: 原文链接
            category: 分类标签
            urgency: 紧急度 (0-1)，用于选择图标
            at_all: 是否 @所有人
        """
        # 根据紧急度选择图标和等级
        if urgency >= 0.85:
            icon = "🔴"
            level = "紧急"
        elif urgency >= 0.7:
            icon = "🟠"
            level = "重要"
        elif urgency >= 0.5:
            icon = "🟡"
            level = "一般"
        else:
            icon = "🟢"
            level = "低"

        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        markdown_content = f"""### {icon} [{level}·{category}] {title}

---

**📰 来源:** {source}
**🕐 时间:** {now}

---

{summary}

[📖 查看原文]({url})

---
**紧急度:** {urgency:.2f} | **标签:** {category}
"""

        return await self.send_markdown(
            title=f"[{level}] {title}",
            content=markdown_content,
            at_all=at_all
        )

    async def send_daily_digest(
        self,
        items: List[Dict[str, Any]],
        date: str = None,
    ) -> bool:
        """
        发送每日简报

        Args:
            items: 新闻条目列表，每项包含 title, url, source, urgency 等
            date: 日期字符串
        """
        if not items:
            return False

        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        now = datetime.now().strftime("%H:%M")

        # 构建新闻列表
        news_list = []
        for i, item in enumerate(items[:10], 1):
            title_text = item.get("title", "无标题")
            source = item.get("source", "未知来源")
            url = item.get("url", "#")
            urgency = item.get("urgency", item.get("importance", 0.5))

            # 紧急度图标
            if urgency >= 0.7:
                icon = "🔴"
            elif urgency >= 0.5:
                icon = "🟡"
            else:
                icon = "🟢"

            news_list.append(f"{i}. {icon} **[{title_text}]({url})**\n   📰 {source}")

        news_section = "\n\n".join(news_list) if news_list else "暂无新闻"

        # 统计信息
        total = len(items)
        high_urgency = sum(1 for item in items if item.get("urgency", item.get("importance", 0)) >= 0.7)

        markdown_content = f"""## 📰 每日简报

**📅 {date} | 🕐 {now} 更新**

---

### 🔥 今日要闻 ({min(total, 10)}条)

{news_section}

---

### 📊 统计

- 总计: {total} 条
- 高紧急度: {high_urgency} 条

---
*由 IKE 自动推送*
"""

        return await self.send_markdown(
            title=f"每日简报 - {date}",
            content=markdown_content
        )

    async def send_urgent_alert(
        self,
        title: str,
        content: str,
        source: str,
        url: str = None,
    ) -> bool:
        """发送紧急信息提醒"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        markdown_content = f"""## 🚨 {title}

**来源:** {source}
**时间:** {now}

---

{content}
"""
        if url:
            markdown_content += f"\n[查看原文]({url})"

        return await self.send_markdown(
            title=f"紧急提醒: {title}",
            content=markdown_content,
            at_all=True
        )

    async def send_system_alert(
        self,
        alert_type: str,
        message: str,
        details: Dict[str, Any] = None,
        at_all: bool = True
    ) -> bool:
        """
        发送系统告警

        Args:
            alert_type: 告警类型 (CPU/Memory/Disk/Error等)
            message: 告警消息
            details: 详细信息
            at_all: 是否 @所有人
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        details_text = ""
        if details:
            for key, value in details.items():
                details_text += f"- **{key}:** {value}\n"

        markdown_content = f"""## ⚠️ 系统告警

**类型:** {alert_type}
**时间:** {now}

---

{message}

{details_text}
"""

        return await self.send_markdown(
            title=f"系统告警 - {alert_type}",
            content=markdown_content,
            at_all=at_all
        )

    async def send_deployment_notification(
        self,
        project: str,
        version: str,
        status: str = "success",
        details: str = ""
    ) -> bool:
        """
        发送部署通知

        Args:
            project: 项目名称
            version: 版本号
            status: 状态 (success/failed/rollback)
            details: 详细信息
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        status_icons = {
            "success": "✅",
            "failed": "❌",
            "rollback": "🔄"
        }
        icon = status_icons.get(status, "ℹ️")

        markdown_content = f"""## {icon} 部署通知

**项目:** {project}
**版本:** {version}
**状态:** {status}
**时间:** {now}

{details}
"""

        return await self.send_markdown(
            title=f"部署通知 - {project}",
            content=markdown_content
        )

    async def send_morning_brief(
        self,
        items: List[Dict[str, Any]],
        date: str = None
    ) -> bool:
        """发送早间简报 (11:00 推送模板)"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        now = datetime.now().strftime("%H:%M")

        # 按分类组织
        categories = {}
        for item in items[:12]:
            cat = item.get("category", "其他")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)

        markdown_content = f"""## 🌅 午间快讯

**📅 {date} | 🕐 {now} 更新**

---

"""

        category_names = {
            "重磅发布": "💥 重磅发布",
            "海外动态": "🌍 海外动态",
            "技术前沿": "🔬 技术前沿",
            "产业动态": "🏢 产业动态",
            "其他": "📋 其他"
        }

        for cat, cat_items in categories.items():
            cat_name = category_names.get(cat, cat)
            markdown_content += f"### {cat_name}\n\n"
            for item in cat_items[:4]:
                title = item.get("title", "无标题")
                url = item.get("url", "#")
                markdown_content += f"- [**{title}**]({url})\n"
            markdown_content += "\n"

        return await self.send_markdown(
            title="午间快讯",
            content=markdown_content
        )

    async def send_evening_brief(
        self,
        items: List[Dict[str, Any]],
        date: str = None
    ) -> bool:
        """发送晚间简报 (18:00 推送模板)"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        now = datetime.now().strftime("%H:%M")

        markdown_content = f"""## 🌆 晚间日报

**📅 {date} | 🕐 {now} 更新**

---

### 🎯 今日焦点

"""

        for item in items[:3]:
            title = item.get("title", "无标题")
            url = item.get("url", "#")
            source = item.get("source", "未知来源")
            markdown_content += f"- [**{title}**]({url}) - {source}\n"

        markdown_content += "\n### 📖 深度阅读\n\n"
        for item in items[3:6]:
            title = item.get("title", "无标题")
            url = item.get("url", "#")
            markdown_content += f"- [**{title}**]({url})\n"

        return await self.send_markdown(
            title="晚间日报",
            content=markdown_content
        )

    async def _send(self, payload: Dict[str, Any]) -> bool:
        """发送请求到钉钉 Webhook"""
        try:
            url = self._get_signed_url()
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    timeout=10.0,
                )
                result = response.json()
                return result.get("errcode") == 0
        except Exception as e:
            print(f"钉钉通知发送失败: {e}")
            return False

    async def test(self) -> bool:
        """测试 Webhook 连接"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return await self.send_markdown(
            title="🔔 IKE 通知测试",
            content=f"**测试时间:** {now}\n\n✅ 钉钉 Webhook 连接成功！"
        )
