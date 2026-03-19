"""
深度信息获取服务 (Depth Fetcher)

支持多层信息获取：
- L1: RSS 摘要 (已有 fetcher.py)
- L2: 完整文章内容 (网页抓取)
- L3: 关键信息提取 (AI 分析)
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class DepthContent:
    """不同深度的内容"""
    depth: int  # 1, 2, 3
    content: str
    title: str = ""
    extracted_data: dict = None  # L3 特有

    def __post_init__(self):
        if self.extracted_data is None:
            self.extracted_data = {}


class DepthFetcher:
    """多层信息获取器"""

    # 请求头
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    # 超时配置
    TIMEOUT = aiohttp.ClientTimeout(total=30, connect=10)

    def __init__(self, proxy_url: str = None):
        self.proxy_url = proxy_url

    async def fetch_depth_1(self, rss_entry: dict) -> DepthContent:
        """
        L1: RSS 摘要
        返回标题 + 描述
        """
        return DepthContent(
            depth=1,
            content=rss_entry.get("summary", ""),
            title=rss_entry.get("title", "")
        )

    async def fetch_depth_2(
        self,
        url: str,
        access_method: str = "direct"
    ) -> DepthContent:
        """
        L2: 完整文章内容
        根据访问方式选择不同的抓取策略
        """
        if access_method == "proxy" and self.proxy_url:
            content = await self._fetch_with_proxy(url)
        elif access_method == "cloud":
            content = await self._fetch_with_cloud(url)
        else:
            content = await self._fetch_direct(url)

        # 解析 HTML 提取正文
        parsed = self._parse_html(content, url)

        return DepthContent(
            depth=2,
            content=parsed["text"],
            title=parsed["title"]
        )

    async def fetch_depth_3(
        self,
        content: str,
        title: str,
        category: str,
        llm_client=None
    ) -> DepthContent:
        """
        L3: 关键信息提取
        使用 AI 从内容中提取结构化信息
        """
        if llm_client is None:
            # 如果没有 LLM，返回 L2 内容
            return DepthContent(
                depth=3,
                content=content,
                title=title,
                extracted_data={"error": "No LLM client"}
            )

        prompt = f"""从以下{category}领域文章中提取关键信息：

标题：{title}

内容：{content[:5000]}

请以JSON格式返回以下字段：
{{
    "主题": "文章主要讨论什么",
    "关键事件": ["事件1", "事件2"],
    "相关公司": ["公司1", "公司2"],
    "影响分析": "对行业/市场的影响",
    "后续关注点": "需要持续关注的事项",
    "置信度": 0.0-1.0
}}

只返回JSON，不要其他内容。"""

        try:
            response = await llm_client.chat([
                {"role": "user", "content": prompt}
            ])

            import json
            # 尝试解析 JSON
            text = response.content.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            extracted_data = json.loads(text.strip())

            return DepthContent(
                depth=3,
                content=content,
                title=title,
                extracted_data=extracted_data
            )
        except Exception as e:
            logger.warning(f"L3 extraction failed: {e}")
            return DepthContent(
                depth=3,
                content=content,
                title=title,
                extracted_data={"error": str(e)}
            )

    async def _fetch_direct(self, url: str) -> str:
        """直接抓取"""
        async with aiohttp.ClientSession(timeout=self.TIMEOUT) as session:
            async with session.get(url, headers=self.HEADERS, ssl=False) as resp:
                resp.raise_for_status()
                return await resp.text()

    async def _fetch_with_proxy(self, url: str) -> str:
        """使用代理抓取"""
        async with aiohttp.ClientSession(timeout=self.TIMEOUT) as session:
            async with session.get(
                url,
                headers=self.HEADERS,
                proxy=self.proxy_url,
                ssl=False
            ) as resp:
                resp.raise_for_status()
                return await resp.text()

    async def _fetch_with_cloud(self, url: str) -> str:
        """
        使用云手机服务抓取（付费内容）
        TODO: 实现云手机集成
        """
        # 占位实现
        logger.warning("Cloud fetch not implemented, falling back to direct")
        return await self._fetch_direct(url)

    def _parse_html(self, html: str, url: str) -> dict:
        """解析 HTML 提取正文"""
        soup = BeautifulSoup(html, "html.parser")

        # 移除脚本和样式
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()

        # 提取标题
        title = ""
        if soup.title:
            title = soup.title.string
        elif soup.h1:
            title = soup.h1.get_text(strip=True)

        # 尝试多种选择器获取正文
        content = ""

        # 常见正文选择器
        selectors = [
            "article",
            "[role='main']",
            ".article-content",
            ".post-content",
            ".entry-content",
            ".content",
            "main",
            ".main-content",
        ]

        for sel in selectors:
            el = soup.select_one(sel)
            if el:
                content = el.get_text(separator="\n", strip=True)
                if len(content) > 200:
                    break

        # 如果还是太短，尝试 body
        if len(content) < 200 and soup.body:
            content = soup.body.get_text(separator="\n", strip=True)

        # 清理内容
        content = self._clean_text(content)

        # 截取前 10000 字符
        content = content[:10000]

        return {
            "title": title,
            "text": content
        }

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        import re

        # 移除多余空白
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)

        # 移除常见噪音
        lines = []
        for line in text.split("\n"):
            # 跳过太短的行
            if len(line.strip()) < 10:
                continue
            # 跳过常见噪音行
            if any(n in line.lower() for n in ["copyright", "all rights reserved", "分享到"]):
                continue
            lines.append(line)

        return "\n".join(lines)


# 全局单例
_fetcher: Optional[DepthFetcher] = None


def get_depth_fetcher(proxy_url: str = None) -> DepthFetcher:
    """获取深度获取器实例"""
    global _fetcher
    if _fetcher is None or (proxy_url and _fetcher.proxy_url != proxy_url):
        _fetcher = DepthFetcher(proxy_url=proxy_url)
    return _fetcher