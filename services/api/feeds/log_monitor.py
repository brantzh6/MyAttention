"""
日志监控与分析系统 - Log Monitor & Analyzer
实时监控、分析日志并生成系统改进建议
"""

import os
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# 日志源配置
# ═══════════════════════════════════════════════════════════════════════════

LOG_SOURCES = {
    "api": {
        "path": "services/api/api.log",
        "encoding": "utf-8",
    },
    "chat": {
        "path": "services/api/chat_debug.log",
        "encoding": "utf-8",
    },
    "web_api": {
        "path": "services/web/api.log",
        "encoding": "utf-8",
    },
    "web_frontend": {
        "path": "services/web/frontend.log",
        "encoding": "utf-8",
    },
}


def _resolve_project_root() -> Path:
    env_path = os.environ.get("MYATTENTION_BASE_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return Path(__file__).resolve().parents[3]


# ═══════════════════════════════════════════════════════════════════════════
# 数据模型
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class LogEntry:
    """日志条目"""
    timestamp: datetime
    level: str
    logger: str
    message: str
    source: str
    raw: str


@dataclass
class ErrorPattern:
    """错误模式"""
    pattern: str
    count: int
    severity: str  # critical, high, medium, low
    description: str
    suggestion: str
    first_seen: datetime
    last_seen: datetime


@dataclass
class MetricStats:
    """指标统计"""
    name: str
    value: float
    unit: str
    trend: str  # up, down, stable
    description: str


@dataclass
class SystemInsight:
    """系统洞察/改进建议"""
    id: str
    category: str  # performance, reliability, security, ux, optimization
    severity: str  # critical, warning, info
    title: str
    description: str
    evidence: List[str]
    suggestion: str
    impact: str
    effort: str  # low, medium, high
    created_at: datetime
    related_logs: int = 0


# ═══════════════════════════════════════════════════════════════════════════
# 日志分析器
# ═══════════════════════════════════════════════════════════════════════════

class LogMonitor:
    """日志监控器 - 收集和分析日志"""

    def __init__(self, base_path: str | None = None):
        self.base_path = Path(base_path).expanduser().resolve() if base_path else _resolve_project_root()
        self._error_patterns = self._init_error_patterns()
        self._metrics_patterns = self._init_metrics_patterns()

    def _init_error_patterns(self) -> Dict[str, Dict]:
        """初始化错误模式匹配规则"""
        return {
            # 数据库相关
            r"connection.*refused": {
                "severity": "critical",
                "category": "database",
                "description": "数据库连接被拒绝",
                "suggestion": "检查 PostgreSQL 服务是否运行，验证连接配置"
            },
            r"deadlock": {
                "severity": "high",
                "category": "database",
                "description": "数据库死锁",
                "suggestion": "优化事务顺序，添加重试机制"
            },
            r"timeout": {
                "severity": "high",
                "category": "performance",
                "description": "操作超时",
                "suggestion": "增加超时时间，优化查询性能"
            },
            r"connection pool": {
                "severity": "high",
                "category": "performance",
                "description": "连接池问题",
                "suggestion": "调整连接池大小，检查连接泄漏"
            },

            # API 相关
            r"500\s+error|internal\s+server\s+error": {
                "severity": "critical",
                "category": "api",
                "description": "服务器内部错误",
                "suggestion": "检查服务器日志，修复代码错误"
            },
            r"404\s+not\s+found": {
                "severity": "medium",
                "category": "api",
                "description": "资源未找到",
                "suggestion": "检查路由配置，验证资源存在"
            },
            r"429\s+rate\s+limit": {
                "severity": "high",
                "category": "api",
                "description": "请求频率超限",
                "suggestion": "实现请求限流，优化缓存策略"
            },
            r"401\s+unauthorized|403\s+forbidden": {
                "severity": "high",
                "category": "security",
                "description": "认证/授权失败",
                "suggestion": "检查 token 有效性，确认权限配置"
            },

            # LLM 相关
            r"rate\s+limit.*api": {
                "severity": "warning",
                "category": "llm",
                "description": "LLM API 限流",
                "suggestion": "实现自动模型切换，添加请求队列"
            },
            r"api.*error.*timeout": {
                "severity": "warning",
                "category": "llm",
                "description": "LLM API 超时",
                "suggestion": "增加超时时间，添加备用模型"
            },
            r"invalid.*api.*key": {
                "severity": "critical",
                "category": "llm",
                "description": "API Key 无效",
                "suggestion": "检查 API Key 配置，更新凭证"
            },

            # 性能相关
            r"slow\s+query": {
                "severity": "warning",
                "category": "performance",
                "description": "慢查询",
                "suggestion": "添加索引，优化 SQL"
            },
            r"memory.*leak": {
                "severity": "critical",
                "category": "performance",
                "description": "内存泄漏",
                "suggestion": "检查对象引用，添加内存监控"
            },
            r"high\s+latency": {
                "severity": "warning",
                "category": "performance",
                "description": "高延迟",
                "suggestion": "分析性能瓶颈，优化代码路径"
            },

            # 反爬相关
            r"blocked|anti.?crawl": {
                "severity": "high",
                "category": "anti_crawl",
                "description": "反爬被拦截",
                "suggestion": "切换访问策略，使用代理/云服务"
            },
            r"captcha": {
                "severity": "high",
                "category": "anti_crawl",
                "description": "遇到验证码",
                "suggestion": "使用打码服务或等待后重试"
            },

            # 前端相关
            r"cannot\s+read.*undefined": {
                "severity": "warning",
                "category": "frontend",
                "description": "前端未定义错误",
                "suggestion": "添加空值检查，完善类型定义"
            },
            r"failed\s+to\s+fetch": {
                "severity": "warning",
                "category": "frontend",
                "description": "前端请求失败",
                "suggestion": "检查网络状态，添加错误边界"
            },
        }

    def _init_metrics_patterns(self) -> Dict[str, Dict]:
        """初始化指标提取规则"""
        return {
            "response_time": {
                "pattern": r"response\s+time[:\s]+(\d+\.?\d*)\s*ms",
                "unit": "ms",
                "threshold": 1000,
                "description": "API 响应时间"
            },
            "tokens_used": {
                "pattern": r"tokens[:\s]+(\d+)",
                "unit": "tokens",
                "threshold": 100000,
                "description": "Token 消耗"
            },
            "cost": {
                "pattern": r"cost[:\s]+\$?(\d+\.?\d*)",
                "unit": "USD",
                "threshold": 10,
                "description": "API 调用成本"
            },
            "error_rate": {
                "pattern": r"error\s+rate[:\s]+(\d+\.?\d*)%",
                "unit": "%",
                "threshold": 5,
                "description": "错误率"
            },
        }

    def collect_logs(
        self,
        source: str = None,
        hours: int = 24,
        level: str = None
    ) -> List[LogEntry]:
        """
        收集日志

        Args:
            source: 日志源 (api, chat, web_api, web_frontend)
            hours: 回溯小时数
            level: 日志级别 (ERROR, WARNING, INFO)

        Returns:
            List[LogEntry]: 日志条目列表
        """
        logs = []
        sources = [source] if source else LOG_SOURCES.keys()

        for src in sources:
            if src not in LOG_SOURCES:
                continue

            config = LOG_SOURCES[src]
            log_path = self.base_path / config["path"]

            if not log_path.exists():
                logger.warning(f"Log file not found: {log_path}")
                continue

            try:
                entries = self._parse_log_file(log_path, src, hours, level)
                logs.extend(entries)
            except Exception as e:
                logger.error(f"Failed to parse {log_path}: {e}")

        return sorted(logs, key=lambda x: x.timestamp, reverse=True)

    def _parse_log_file(
        self,
        path: Path,
        source_name: str,
        hours: int,
        level: str
    ) -> List[LogEntry]:
        """解析日志文件 - 支持多种格式"""
        entries = []
        cutoff = datetime.now() - timedelta(hours=hours)
        file_timestamp = datetime.fromtimestamp(path.stat().st_mtime)

        # 多种日志格式的正则表达式
        patterns = [
            # 格式1: 2026-03-13 22:58:23,226 INFO sqlalchemy.engine.Engine ...
            re.compile(r"^(?P<timestamp>[\d\-]+\s+[\d:,]+)\s+(?P<level>INFO|ERROR|WARNING|WARN|CRITICAL|DEBUG)\s+(?P<logger>[\w\.]+)\s+-\s+(?P<message>.*)$"),
            # 格式2: INFO:     Started server process
            re.compile(r"^(?P<level>INFO|ERROR|WARNING|WARN|CRITICAL|DEBUG):?\s+(?P<message>.*)$"),
            # 格式3: 127.0.0.1:9242 - "POST /api/feeds/import HTTP/1.1" 200 OK
            re.compile(r'^(?P<message>".*"\s+\d+\s+\w+)$'),
        ]

        try:
            # 读取最后 10000 行以提高效率
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()[-10000:]

            for line in lines:
                try:
                    timestamp = None
                    log_level = None
                    logger_name = ""
                    message = ""

                    # 尝试每种模式
                    for pattern in patterns:
                        match = pattern.match(line.strip())
                        if match:
                            data = match.groupdict()

                            # 提取时间戳
                            ts_str = data.get("timestamp", "")
                            if ts_str:
                                try:
                                    # 处理不同格式
                                    ts_str = ts_str.replace(",", ".").replace(" ", "T")
                                    if len(ts_str.split("T")) == 1:
                                        ts_str = ts_str.replace(":", " ", 1)  # 日期和时间之间的空格
                                    timestamp = datetime.fromisoformat(ts_str[:19])
                                except:
                                    timestamp = file_timestamp
                            else:
                                timestamp = file_timestamp

                            # 提取级别
                            log_level = data.get("level", "INFO").upper()
                            if log_level == "WARN":
                                log_level = "WARNING"

                            # 提取消息
                            message = data.get("message", "")

                            # 提取 logger
                            logger_name = data.get("logger", "")

                            break  # 找到匹配的模式就退出

                    if not message:
                        continue

                    # 过滤时间
                    if timestamp and timestamp < cutoff:
                        continue

                    # 过滤级别
                    if level and log_level != level:
                        continue

                    entries.append(LogEntry(
                        timestamp=timestamp or datetime.now(),
                        level=log_level or "INFO",
                        logger=logger_name,
                        message=message,
                        source=source_name,
                        raw=line.strip()
                    ))
                except:
                    continue

        except Exception as e:
            logger.error(f"Error reading {path}: {e}")

        return entries

    def analyze_errors(self, logs: List[LogEntry]) -> List[ErrorPattern]:
        """
        分析错误模式

        Args:
            logs: 日志列表

        Returns:
            List[ErrorPattern]: 错误模式列表
        """
        # 收集所有非 INFO 级别的日志
        error_logs = [l for l in logs if l.level in ("ERROR", "CRITICAL", "WARNING")]

        # 也检查 INFO 中可能的问题
        info_logs = [l for l in logs if l.level == "INFO"]
        for log in info_logs:
            msg = log.message.lower()
            # 检查关键问题关键词
            if any(kw in msg for kw in ["exception", "fail", "error", "timeout", "blocked", "refused"]):
                error_logs.append(log)

        # 按模式分组
        pattern_counts = defaultdict(lambda: {"count": 0, "first_seen": None, "last_seen": None, "samples": []})

        for log in error_logs:
            message = log.message.lower()

            for pattern, config in self._error_patterns.items():
                if re.search(pattern, message, re.IGNORECASE):
                    key = pattern
                    pattern_counts[key]["count"] += 1
                    if pattern_counts[key]["first_seen"] is None:
                        pattern_counts[key]["first_seen"] = log.timestamp
                    pattern_counts[key]["last_seen"] = log.timestamp
                    # 保存样本
                    if len(pattern_counts[key]["samples"]) < 3:
                        pattern_counts[key]["samples"].append(log.message[:200])
                    break

        # 转换为错误模式列表
        results = []
        for pattern, data in pattern_counts.items():
            if data["count"] == 0:
                continue

            config = self._error_patterns[pattern]
            results.append(ErrorPattern(
                pattern=pattern,
                count=data["count"],
                severity=config["severity"],
                description=config["description"],
                suggestion=config["suggestion"],
                first_seen=data["first_seen"],
                last_seen=data["last_seen"]
            ))

        return sorted(results, key=lambda x: (self._severity_order(x.severity), -x.count))

    def analyze_metrics(self, logs: List[LogEntry]) -> List[MetricStats]:
        """
        分析性能指标

        Args:
            logs: 日志列表

        Returns:
            List[MetricStats]: 指标统计列表
        """
        metrics = []

        for name, config in self._metrics_patterns.items():
            values = []

            for log in logs:
                match = re.search(config["pattern"], log.message, re.IGNORECASE)
                if match:
                    try:
                        values.append(float(match.group(1)))
                    except:
                        continue

            if values:
                avg = sum(values) / len(values)
                trend = "stable"

                # 简单趋势分析
                recent = values[-10:] if len(values) > 10 else values
                older = values[:-10] if len(values) > 10 else []

                if older and sum(older) / len(older) < avg * 0.9:
                    trend = "up"
                elif older and sum(older) / len(older) > avg * 1.1:
                    trend = "down"

                metrics.append(MetricStats(
                    name=name,
                    value=avg,
                    unit=config["unit"],
                    trend=trend,
                    description=config["description"]
                ))

        return metrics

    def analyze_by_source(self, logs: List[LogEntry]) -> Dict[str, Dict]:
        """按来源分析日志"""
        source_stats = defaultdict(lambda: {"total": 0, "errors": 0, "warnings": 0})

        for log in logs:
            source_stats[log.source]["total"] += 1
            if log.level == "ERROR":
                source_stats[log.source]["errors"] += 1
            elif log.level == "WARNING":
                source_stats[log.source]["warnings"] += 1

        return dict(source_stats)

    def analyze_by_time(self, logs: List[LogEntry], interval_minutes: int = 60) -> Dict[str, int]:
        """按时段分析日志（检测异常时段）"""
        time_buckets = defaultdict(int)

        for log in logs:
            bucket = log.timestamp.replace(
                minute=log.timestamp.minute // interval_minutes * interval_minutes,
                second=0,
                microsecond=0
            )
            time_buckets[bucket.isoformat()] += 1

        return dict(time_buckets)

    def _severity_order(self, severity: str) -> int:
        """严重程度排序"""
        order = {"critical": 0, "high": 1, "warning": 2, "medium": 3, "low": 4, "info": 5}
        return order.get(severity, 5)

    # ═══════════════════════════════════════════════════════════════════════════
    # 生成系统洞察
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_insights(self, logs: List[LogEntry]) -> List[SystemInsight]:
        """
        生成系统改进建议

        Args:
            logs: 日志列表

        Returns:
            List[SystemInsight]: 系统洞察列表
        """
        insights = []

        # 1. 分析错误模式
        error_patterns = self.analyze_errors(logs)
        for pattern in error_patterns[:5]:  # 最多 5 个
            insights.append(SystemInsight(
                id=f"err_{pattern.pattern[:20]}",
                category="reliability",
                severity=pattern.severity,
                title=f"频繁错误: {pattern.description}",
                description=f"在最近的分析中发现 {pattern.count} 次 '{pattern.pattern}' 错误",
                evidence=[f"首次出现: {pattern.first_seen}", f"最后出现: {pattern.last_seen}"],
                suggestion=pattern.suggestion,
                impact="影响系统稳定性和用户体验",
                effort="medium",
                created_at=datetime.now(),
                related_logs=pattern.count
            ))

        # 2. 分析性能指标
        metrics = self.analyze_metrics(logs)
        for metric in metrics:
            if metric.trend == "up" or metric.value > 1000:  # 阈值
                insights.append(SystemInsight(
                    id=f"perf_{metric.name}",
                    category="performance",
                    severity="warning" if metric.trend == "up" else "info",
                    title=f"性能指标异常: {metric.description}",
                    description=f"当前平均值: {metric.value:.2f} {metric.unit}，趋势: {metric.trend}",
                    evidence=[f"当前值: {metric.value:.2f} {metric.unit}", f"趋势: {metric.trend}"],
                    suggestion=f"关注 {metric.description} 指标，考虑优化",
                    impact="可能影响系统响应速度",
                    effort="medium",
                    created_at=datetime.now()
                ))

        # 3. 按来源统计
        source_stats = self.analyze_by_source(logs)
        for source, stats in source_stats.items():
            if stats["errors"] > 0:
                insights.append(SystemInsight(
                    id=f"src_{source}",
                    category="reliability",
                    severity="warning",
                    title=f"来源异常: {source}",
                    description=f"该来源产生 {stats['errors']} 个错误，{stats['warnings']} 个警告",
                    evidence=[f"错误: {stats['errors']}", f"警告: {stats['warnings']}", f"总计: {stats['total']}"],
                    suggestion=f"重点检查 {source} 模块",
                    impact="影响特定模块的稳定性",
                    effort="low",
                    created_at=datetime.now()
                ))

        # 4. 综合建议 - 基于日志量分析
        total_errors = sum(s["errors"] for s in source_stats.values())
        total_warnings = sum(s["warnings"] for s in source_stats.values())
        total_logs = len(logs)

        if total_errors > 50:
            insights.append(SystemInsight(
                id="overall_errors",
                category="reliability",
                severity="critical",
                title="系统错误过多",
                description=f"过去 24 小时共发现 {total_errors} 个错误，{total_warnings} 个警告",
                evidence=[f"错误总数: {total_errors}", f"警告总数: {total_warnings}"],
                suggestion="建议进行系统性排查，优先处理 critical 和 high 级别问题",
                impact="影响整体系统稳定性",
                effort="high",
                created_at=datetime.now()
            ))
        elif total_logs > 0:
            # 系统运行正常，但给出优化建议
            insights.append(SystemInsight(
                id="system_healthy",
                category="optimization",
                severity="info",
                title="系统运行正常",
                description=f"过去 24 小时共处理 {total_logs} 条日志，系统运行稳定",
                evidence=[f"日志总数: {total_logs}", f"错误: {total_errors}", f"警告: {total_warnings}"],
                suggestion="建议定期查看日志分析报告，持续监控系统健康状态",
                impact="系统运行良好",
                effort="low",
                created_at=datetime.now()
            ))

            # 检查是否有特定模块需要关注
            api_logs = sum(s["total"] for k, s in source_stats.items() if "api" in k.lower())
            if api_logs > 100:
                insights.append(SystemInsight(
                    id="high_api_usage",
                    category="optimization",
                    severity="info",
                    title="API 使用率高",
                    description=f"API 日志量较大 ({api_logs} 条)，建议监控性能",
                    evidence=[f"API 日志: {api_logs}"],
                    suggestion="考虑添加 API 缓存，优化查询性能",
                    impact="高流量可能影响响应速度",
                    effort="medium",
                    created_at=datetime.now()
                ))

        return sorted(insights, key=lambda x: (self._severity_order(x.severity), x.created_at))


# ═══════════════════════════════════════════════════════════════════════════
# 便捷函数
# ═══════════════════════════════════════════════════════════════════════════

_monitor: Optional[LogMonitor] = None


def get_log_monitor() -> LogMonitor:
    """获取日志监控器实例"""
    global _monitor
    if _monitor is None:
        _monitor = LogMonitor()
    return _monitor


def analyze_system_health(hours: int = 24) -> Dict[str, Any]:
    """
    快速分析系统健康状态

    Args:
        hours: 回溯小时数

    Returns:
        Dict: 健康分析结果
    """
    monitor = get_log_monitor()
    logs = monitor.collect_logs(hours=hours)

    return {
        "total_logs": len(logs),
        "error_count": len([l for l in logs if l.level == "ERROR"]),
        "warning_count": len([l for l in logs if l.level == "WARNING"]),
        "error_patterns": monitor.analyze_errors(logs)[:5],
        "metrics": monitor.analyze_metrics(logs),
        "source_stats": monitor.analyze_by_source(logs),
        "insights": monitor.generate_insights(logs)[:10]
    }


def quick_health_check() -> Dict[str, Any]:
    """
    快速健康检查 - 秒级响应

    只检查最近5分钟的日志，快速发现严重问题

    Returns:
        Dict: 快速健康检查结果
    """
    import time
    start_time = time.time()

    monitor = get_log_monitor()

    # 只检查最近5分钟
    logs = monitor.collect_logs(hours=0.083)  # 5分钟 = 0.083小时

    # 快速分析严重问题
    critical_issues = []
    for log in logs:
        msg = log.message.lower()
        if log.level in ("ERROR", "CRITICAL") or any(kw in msg for kw in ["exception", "fatal", "crash", "failed"]):
            critical_issues.append({
                "timestamp": log.timestamp.isoformat(),
                "level": log.level,
                "message": log.message[:200],
                "source": log.source
            })

    elapsed = time.time() - start_time

    return {
        "status": "healthy" if len(critical_issues) == 0 else "critical",
        "checked_at": datetime.now().isoformat(),
        "logs_checked": len(logs),
        "critical_issues": critical_issues[:10],  # 最多10条
        "critical_count": len(critical_issues),
        "response_time_ms": int(elapsed * 1000)
    }


def get_problem_dashboard() -> Dict[str, Any]:
    """
    获取问题中心仪表盘数据

    Returns:
        Dict: 问题中心数据
    """
    from sqlalchemy import select, func
    from db.session import async_session_maker
    from db.models import Task, TaskStatus

    monitor = get_log_monitor()

    # 最近1小时日志
    logs = monitor.collect_logs(hours=1)
    logs_24h = monitor.collect_logs(hours=24)

    # 问题统计
    error_count = len([l for l in logs if l.level == "ERROR"])
    warning_count = len([l for l in logs if l.level == "WARNING"])

    # 任务统计
    import asyncio
    async def get_task_stats():
        async with async_session_maker() as db:
            # 待处理任务
            pending_result = await db.execute(
                select(func.count(Task.id))
                .where(Task.status == TaskStatus.PENDING.value)
            )
            pending = pending_result.scalar() or 0

            # 紧急任务 P0
            p0_result = await db.execute(
                select(func.count(Task.id))
                .where(Task.priority == 0)
                .where(Task.status.in_([TaskStatus.PENDING.value, TaskStatus.EXECUTING.value]))
            )
            p0 = p0_result.scalar() or 0

            # 重要任务 P1
            p1_result = await db.execute(
                select(func.count(Task.id))
                .where(Task.priority == 1)
                .where(Task.status == TaskStatus.PENDING.value)
            )
            p1 = p1_result.scalar() or 0

            return {"pending": pending, "p0_urgent": p0, "p1_important": p1}

    try:
        asyncio.get_running_loop()
        task_stats = {"pending": 0, "p0_urgent": 0, "p1_important": 0}
    except RuntimeError:
        task_stats = asyncio.run(get_task_stats())

    # 生成洞察
    insights = monitor.generate_insights(logs_24h)

    return {
        # 实时状态
        "realtime": {
            "status": "healthy" if error_count == 0 else "degraded",
            "logs_last_hour": len(logs),
            "errors_last_hour": error_count,
            "warnings_last_hour": warning_count
        },
        # 任务待办
        "tasks": task_stats,
        # 洞察建议
        "insights": [
            {
                "id": i.id,
                "severity": i.severity,
                "title": i.title,
                "description": i.description[:100],
                "suggestion": i.suggestion,
                "category": i.category,
                "effort": i.effort
            }
            for i in insights[:5]
        ],
        # 错误趋势
        "trend": {
            "logs_24h": len(logs_24h),
            "errors_24h": len([l for l in logs_24h if l.level == "ERROR"]),
            "warnings_24h": len([l for l in logs_24h if l.level == "WARNING"])
        },
        "updated_at": datetime.now().isoformat()
    }
