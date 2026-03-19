"""
自动反爬系统 (Automatic Anti-Crawl System)

核心特性：
1. 自动检测 - 通过响应状态码、内容特征自动识别反爬
2. 自动切换 - 检测到反爬后自动尝试其他访问方式
3. 自动重试 - 失败后自动重试并记录
4. 后台学习 - 记录成功/失败模式，持续优化

反馈驱动闭环：
抓取失败 → 检测原因 → 切换策略 → 重试成功 → 记录模式 → 持续优化
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime, timezone, timedelta
from enum import Enum

import aiohttp

from feeds.proxy_config import load_proxy_settings
from db.models import Source, AntiCrawlStatus, AccessMethod

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# 反爬检测器
# ═══════════════════════════════════════════════════════════════════════════

class AntiCrawlDetector:
    """自动反爬检测器"""

    # 反爬特征检测模式
    BLOCKED_PATTERNS = [
        # HTTP 4xx 错误
        r"403 Forbidden",
        r"403 Client Error",
        r"429 Too Many Requests",
        r"418 I'm a teapot",  # Cloudflare 挑战
        # 页面内容特征
        r"Access Denied",
        r"Access to this page is denied",
        r"Please wait while we verify",
        r"Cloudflare",
        r"security check",
        r"captcha",
        r"blocked",
        r"请验证",
        r"访问受限",
        r"异常访问",
    ]

    PAYWALL_PATTERNS = [
        r"订阅墙",
        r"paywall",
        r"premium",
        r"付费",
        r"subscription",
        r"会员专享",
        r"立即登录",
        r"login to continue",
        r"sign in to read",
    ]

    RATE_LIMIT_PATTERNS = [
        r"too many requests",
        r"请求过于频繁",
        r"rate limit",
        r"稍后再试",
    ]

    def __init__(self):
        self._blocked_re = [re.compile(p, re.I) for p in self.BLOCKED_PATTERNS]
        self._paywall_re = [re.compile(p, re.I) for p in self.PAYWALL_PATTERNS]
        self._rate_limit_re = [re.compile(p, re.I) for p in self.RATE_LIMIT_PATTERNS]

    def detect(self, status_code: int, content: str = "") -> AntiCrawlStatus:
        """
        检测反爬状态

        Args:
            status_code: HTTP 状态码
            content: 响应内容

        Returns:
            AntiCrawlStatus: 检测到的状态
        """
        # 1. 基于状态码检测
        if status_code == 403:
            return AntiCrawlStatus.BLOCKED
        elif status_code == 418:
            return AntiCrawlStatus.BLOCKED
        elif status_code == 429:
            return AntiCrawlStatus.RATE_LIMITED
        elif status_code == 401 or status_code == 407:
            return AntiCrawlStatus.PAYWALL

        # 2. 基于内容特征检测
        content_lower = content.lower()[:5000] if content else ""  # 只检查前5000字符

        # 检查被封禁特征
        for pattern in self._blocked_re:
            if pattern.search(content_lower):
                # 区分是 paywall 还是 blocked
                for pw in self._paywall_re:
                    if pw.search(content_lower):
                        return AntiCrawlStatus.PAYWALL
                return AntiCrawlStatus.BLOCKED

        # 检查限速特征
        for pattern in self._rate_limit_re:
            if pattern.search(content_lower):
                return AntiCrawlStatus.RATE_LIMITED

        # 检查付费墙特征
        for pattern in self._paywall_re:
            if pattern.search(content_lower):
                return AntiCrawlStatus.PAYWALL

        return AntiCrawlStatus.OK

    def detect_from_error(self, error: Exception) -> AntiCrawlStatus:
        """从异常中检测反爬状态"""
        error_msg = str(error).lower()

        if "403" in error_msg:
            return AntiCrawlStatus.BLOCKED
        elif "429" in error_msg:
            return AntiCrawlStatus.RATE_LIMITED
        elif "timeout" in error_msg:
            return AntiCrawlStatus.RATE_LIMITED
        elif "certificate" in error_msg or "ssl" in error_msg:
            return AntiCrawlStatus.BLOCKED

        return AntiCrawlStatus.UNKNOWN


# ═══════════════════════════════════════════════════════════════════════════
# 自动反爬处理器
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AntiCrawlResult:
    """反爬处理结果"""
    success: bool
    status: AntiCrawlStatus
    content: str = ""
    status_code: int = 0
    method_used: str = "direct"
    attempts: int = 1
    error: str = ""


class AutomaticAntiCrawlHandler:
    """
    自动反爬处理器

    工作流程：
    1. 尝试直接访问
    2. 失败 → 检测反爬类型
    3. 根据类型切换策略（代理 → 云 → 降低频率）
    4. 重试
    5. 记录结果到数据库
    """

    # 访问方式优先级
    METHOD_PRIORITY = [
        AccessMethod.DIRECT,
        AccessMethod.PROXY,
        AccessMethod.CLOUD,
        AccessMethod.MANUAL,
    ]

    # 每种方式的最大重试次数
    MAX_RETRIES = {
        AccessMethod.DIRECT: 2,
        AccessMethod.PROXY: 3,
        AccessMethod.CLOUD: 2,
    }

    # 重试间隔（秒）
    RETRY_DELAY = {
        AntiCrawlStatus.OK: 0,
        AntiCrawlStatus.BLOCKED: 5,
        AntiCrawlStatus.RATE_LIMITED: 10,
        AntiCrawlStatus.PAYWALL: 3,
    }

    # 请求头配置
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    def __init__(
        self,
        proxy_url: str = None,
        cloud_service: str = None,
        on_status_change: Callable = None
    ):
        """
        Args:
            proxy_url: 代理服务器 URL
            cloud_service: 云手机服务（可选）
            on_status_change: 状态变化回调，用于更新数据库
        """
        proxy_settings = load_proxy_settings()
        proxy_enabled = proxy_settings.get("enabled", False)
        self.proxy_url = proxy_url or (
            proxy_settings.get("http_proxy") if proxy_enabled else None
        )
        self.cloud_service = cloud_service
        self.detector = AntiCrawlDetector()
        self.on_status_change = on_status_change

    async def fetch_with_auto_retry(
        self,
        url: str,
        source_id: str = None,
        initial_method: AccessMethod = AccessMethod.DIRECT,
        timeout: int = 30
    ) -> AntiCrawlResult:
        """
        自动重试获取

        核心方法：尝试多种访问方式，直到成功或耗尽所有选项

        Args:
            url: 目标 URL
            source_id: 信息源 ID（用于更新数据库）
            initial_method: 初始访问方式
            timeout: 超时时间（秒）

        Returns:
            AntiCrawlResult: 获取结果
        """
        last_error = ""
        last_status = AntiCrawlStatus.OK

        # 从初始方式开始，按优先级尝试
        if initial_method == AccessMethod.PROXY and not self.proxy_url:
            initial_method = AccessMethod.DIRECT

        start_idx = self.METHOD_PRIORITY.index(initial_method)
        methods_to_try = [
            method
            for method in self.METHOD_PRIORITY[start_idx:]
            if method != AccessMethod.PROXY or self.proxy_url
        ]

        for method in methods_to_try:
            max_retries = self.MAX_RETRIES.get(method, 1)

            for attempt in range(max_retries):
                try:
                    # 等待一段时间（如果是重试）
                    if attempt > 0 or method != AccessMethod.DIRECT:
                        await asyncio.sleep(self.RETRY_DELAY.get(last_status, 2))

                    # 执行获取
                    result = await self._fetch_with_method(
                        url, method, timeout
                    )

                    # 检测反爬状态
                    detected = self.detector.detect(
                        result.status_code,
                        result.content if result.content else ""
                    )

                    if result.status_code == 200 and detected == AntiCrawlStatus.OK:
                        # 成功！
                        return AntiCrawlResult(
                            success=True,
                            status=AntiCrawlStatus.OK,
                            content=result.content,
                            status_code=result.status_code,
                            method_used=method.value,
                            attempts=attempt + 1
                        )

                    # 失败了，记录状态并尝试下一种方法
                    last_status = detected
                    last_error = f"Status {result.status_code}, detected: {detected.value}"

                    # 如果检测到严重反爬，直接切换
                    if detected in [AntiCrawlStatus.BLOCKED, AntiCrawlStatus.PAYWALL]:
                        logger.warning(
                            f"Detected {detected.value} on {url}, "
                            f"switching from {method.value}"
                        )
                        break  # 跳出当前方式的尝试，切换到下一种方式

                except Exception as e:
                    last_status = self.detector.detect_from_error(e)
                    last_error = str(e)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")

                    # 如果是严重错误，直接切换
                    if last_status in [AntiCrawlStatus.BLOCKED, AntiCrawlStatus.PAYWALL]:
                        break

        # 所有方法都失败了
        return AntiCrawlResult(
            success=False,
            status=last_status,
            content="",
            status_code=0,
            method_used="none",
            attempts=sum(self.MAX_RETRIES.values()),
            error=last_error
        )

    async def _fetch_with_method(
        self,
        url: str,
        method: AccessMethod,
        timeout: int
    ) -> Dict[str, Any]:
        """使用指定方式获取"""
        timeout_obj = aiohttp.ClientTimeout(total=timeout, connect=10)

        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            if method == AccessMethod.DIRECT:
                async with session.get(url, headers=self.HEADERS, ssl=False) as resp:
                    return {
                        "content": await resp.text(),
                        "status_code": resp.status,
                        "headers": dict(resp.headers)
                    }

            elif method == AccessMethod.PROXY:
                if not self.proxy_url:
                    raise Exception("Proxy is disabled or not configured")
                async with session.get(
                    url,
                    headers=self.HEADERS,
                    proxy=self.proxy_url,
                    ssl=False
                ) as resp:
                    return {
                        "content": await resp.text(),
                        "status_code": resp.status,
                        "headers": dict(resp.headers)
                    }

            elif method == AccessMethod.CLOUD:
                # 云手机服务（需要集成实际的云服务）
                if self.cloud_service:
                    return await self._fetch_with_cloud(url, session)
                else:
                    # 没有云服务，回退到代理
                    return await self._fetch_with_method(url, AccessMethod.PROXY, timeout)

            elif method == AccessMethod.MANUAL:
                # 需要手动处理，记录为失败
                raise Exception("Manual access required")

    async def _fetch_with_cloud(self, url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """使用云手机服务获取"""
        # TODO: 集成实际的云手机服务（如云闪达、比特浏览器等）
        # 这里是一个占位实现
        logger.warning(f"Cloud fetch not implemented for {url}, falling back")
        raise Exception("Cloud service not configured")

    async def update_source_status(
        self,
        db,
        source_id: str,
        status: AntiCrawlStatus,
        success_count_delta: int = 0,
        failure_count_delta: int = 0
    ):
        """更新源的反爬状态和计数"""
        from sqlalchemy import select

        result = await db.execute(
            select(Source).where(Source.id == source_id)
        )
        source = result.scalar_one_or_none()

        if source:
            # 更新状态
            source.anti_crawl_status = status

            # 更新计数
            if success_count_delta:
                source.success_count += success_count_delta
            if failure_count_delta:
                source.failure_count += failure_count_delta

            # 根据状态调整访问方式
            if status == AntiCrawlStatus.BLOCKED:
                source.access_method = AccessMethod.PROXY
                source.retry_count += 1
            elif status == AntiCrawlStatus.PAYWALL:
                source.access_method = AccessMethod.CLOUD
            elif status == AntiCrawlStatus.RATE_LIMITED:
                source.retry_count += 1

            await db.commit()

            logger.info(
                f"Updated source {source.name}: status={status.value}, "
                f"method={source.access_method.value}"
            )


# ═══════════════════════════════════════════════════════════════════════════
# 反爬调度器（后台任务）
# ═══════════════════════════════════════════════════════════════════════════

class AntiCrawlScheduler:
    """
    反爬调度器 - 后台定时检查和优化

    自动运行：
    1. 定期检查所有源的健康状态
    2. 对失败的源尝试不同策略
    3. 更新数据库状态
    """

    def __init__(self, db_factory, check_interval: int = 3600):
        """
        Args:
            db_factory: 数据库会话工厂
            check_interval: 检查间隔（秒），默认1小时
        """
        self.db_factory = db_factory
        self.check_interval = check_interval
        self._running = False
        self._task = None
        self.handler = AutomaticAntiCrawlHandler()

    async def start(self):
        """启动调度器"""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Anti-crawl scheduler started")

    async def stop(self):
        """停止调度器"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Anti-crawl scheduler stopped")

    async def _run_loop(self):
        """运行调度循环"""
        while self._running:
            try:
                await self._check_all_sources()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Anti-crawl check error: {e}", exc_info=True)

            await asyncio.sleep(self.check_interval)

    async def _check_all_sources(self):
        """检查所有信息源"""
        async for db in self.db_factory():
            from sqlalchemy import select

            # 获取所有启用的源
            result = await db.execute(
                select(Source).where(Source.enabled == True)
            )
            sources = result.scalars().all()

            for source in sources:
                # 跳过刚失败的源（避免频繁检查）
                if source.retry_count >= 5:
                    logger.info(f"Source {source.name} needs attention (retry={source.retry_count})")
                    continue

                # 只检查有反爬历史的源
                if source.anti_crawl_status != AntiCrawlStatus.OK:
                    logger.info(f"Checking source {source.name} (status={source.anti_crawl_status.value})")

                    # 尝试获取
                    result = await self.handler.fetch_with_auto_retry(
                        url=source.url,
                        source_id=str(source.id),
                        initial_method=source.access_method
                    )

                    # 更新状态
                    if result.success:
                        await self.handler.update_source_status(
                            db, str(source.id),
                            AntiCrawlStatus.OK,
                            success_count_delta=1
                        )
                    else:
                        await self.handler.update_source_status(
                            db, str(source.id),
                            result.status,
                            failure_count_delta=1
                        )

            break  # 退出 async for

    async def test_source(self, url: str, method: AccessMethod = AccessMethod.DIRECT) -> AntiCrawlResult:
        """测试特定 URL 的反爬情况"""
        return await self.handler.fetch_with_auto_retry(url, method=method)


# ═══════════════════════════════════════════════════════════════════════════
# 便捷函数
# ═══════════════════════════════════════════════════════════════════════════

# 全局处理器
_handler: Optional[AutomaticAntiCrawlHandler] = None


def get_anti_crawl_handler() -> AutomaticAntiCrawlHandler:
    """获取全局反爬处理器"""
    global _handler
    proxy_settings = load_proxy_settings()
    expected_proxy = proxy_settings.get("http_proxy") if proxy_settings.get("enabled") else None
    if _handler is None or _handler.proxy_url != expected_proxy:
        _handler = AutomaticAntiCrawlHandler()
    return _handler


async def auto_fetch(url: str, source_id: str = None) -> AntiCrawlResult:
    """便捷函数：自动获取 URL"""
    handler = get_anti_crawl_handler()
    return await handler.fetch_with_auto_retry(url, source_id)
