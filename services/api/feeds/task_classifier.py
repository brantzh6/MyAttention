"""
任务分类器 - Task Classifier
根据任务来源和内容确定优先级和处理方式
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from db.models import TaskPriority, TaskCategory, TaskSourceType

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# 分类规则配置
# ═══════════════════════════════════════════════════════════════════════════

# 优先级规则：来源类型 + 错误类型 → 优先级
PRIORITY_RULES = {
    # P0 - 紧急（自动处理）
    "api_test_crash": 0,
    "api_test_critical": 0,
    "ui_test_crash": 0,
    "ui_test_critical": 0,
    "anti_crawl_blocked": 0,
    "system_health_critical": 0,

    # P1 - 重要（需确认）
    "source_evolution_disable": 1,
    "source_evolution_add": 1,
    "source_evolution_modify": 1,
    "anti_crawl_rate_limit": 1,
    "system_health_warning": 1,

    # P2 - 普通（汇总报告）
    "api_test_error": 2,
    "ui_test_error": 2,
    "performance_issue": 2,

    # P3 - 建议（定期汇总）
    "quality_issue": 3,
    "ui_test_warning": 3,
    "suggestion": 3,
}

# 自动处理规则：哪些任务可以自动处理
AUTO_PROCESS_RULES = {
    "api_test_crash": True,
    "api_test_critical": True,
    "ui_test_crash": True,
    "anti_crawl_blocked": True,
    "anti_crawl_rate_limit": True,
    "system_health_critical": True,
}

# 分类映射：具体错误类型 → 任务分类
CATEGORY_RULES = {
    "api_test": TaskCategory.FUNCTIONAL,
    "ui_test": TaskCategory.FUNCTIONAL,
    "anti_crawl": TaskCategory.CONFIG,
    "source_evolution": TaskCategory.CONFIG,
    "system_health": TaskCategory.SECURITY,
    "knowledge_quality": TaskCategory.QUALITY,
}


@dataclass
class ClassificationResult:
    """分类结果"""
    priority: int  # 0-3
    category: str  # functional, performance, security, config
    auto_processible: bool
    title: str
    description: str
    source_type: str
    source_id: Optional[str] = None
    source_data: Optional[Dict[str, Any]] = None


class TaskClassifier:
    """任务分类器 - 根据来源和内容确定优先级和处理方式"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def classify(self, source_type: str, error_data: Dict[str, Any]) -> ClassificationResult:
        """
        根据来源和错误数据分类任务

        Args:
            source_type: 来源类型 (api_test, ui_test, anti_crawl, etc.)
            error_data: 错误数据

        Returns:
            ClassificationResult: 分类结果
        """
        # 确定任务类型
        task_type = self._determine_task_type(source_type, error_data)

        # 获取优先级
        priority = PRIORITY_RULES.get(task_type, 2)

        # 获取分类
        category = CATEGORY_RULES.get(source_type, TaskCategory.FUNCTIONAL)

        # 判断是否可自动处理
        auto_processible = AUTO_PROCESS_RULES.get(task_type, False)

        # 生成标题和描述
        title = self._generate_title(source_type, error_data)
        description = self._generate_description(source_type, error_data)

        # 构建源数据
        source_id = error_data.get("id") or error_data.get("source_id")
        source_data = {
            "original_data": error_data,
            "task_type": task_type
        }

        result = ClassificationResult(
            priority=priority,
            category=category.value if isinstance(category, TaskCategory) else category,
            auto_processible=auto_processible,
            title=title,
            description=description,
            source_type=source_type,
            source_id=source_id,
            source_data=source_data
        )

        self.logger.info(
            f"任务分类: {source_type} -> priority={priority}, "
            f"auto_processible={auto_processible}, title={title[:50]}"
        )

        return result

    def _determine_task_type(self, source_type: str, error_data: Dict[str, Any]) -> str:
        """确定具体任务类型"""
        severity = error_data.get("severity", "error")
        error_type = error_data.get("type", "error")

        # 构建任务类型键
        if source_type in ["api_test", "ui_test"]:
            if severity == "critical" or error_type in ["crash", "error"]:
                return f"{source_type}_critical" if severity == "critical" else f"{source_type}_error"
            return f"{source_type}_error"

        if source_type == "anti_crawl":
            status = error_data.get("status", "")
            if status == "blocked":
                return "anti_crawl_blocked"
            elif status == "rate_limited":
                return "anti_crawl_rate_limit"
            return "anti_crawl_blocked"

        if source_type == "source_evolution":
            action = error_data.get("action", "modify")
            return f"source_evolution_{action}"

        if source_type == "system_health":
            health = error_data.get("health", "healthy")
            return f"system_health_critical" if health == "critical" else "system_health_warning"

        return source_type

    def _generate_title(self, source_type: str, error_data: Dict[str, Any]) -> str:
        """生成任务标题"""
        titles = {
            "api_test": f"API测试失败: {error_data.get('endpoint', 'unknown')}",
            "ui_test": f"UI测试错误: {error_data.get('page', 'unknown')}",
            "anti_crawl": f"反爬被拦截: {error_data.get('url', 'unknown')[:50]}",
            "source_evolution": f"信息源变更: {error_data.get('source_name', 'unknown')}",
            "system_health": f"系统健康: {error_data.get('message', '系统异常')}",
            "knowledge_quality": f"知识质量问题: {error_data.get('kb_id', 'unknown')}",
        }
        return titles.get(source_type, f"任务: {source_type}")

    def _generate_description(self, source_type: str, error_data: Dict[str, Any]) -> str:
        """生成任务描述"""
        description = error_data.get("message", "")

        # 添加额外信息
        if source_type == "api_test":
            if error_data.get("status_code"):
                description += f"\n状态码: {error_data.get('status_code')}"
            if error_data.get("error"):
                description += f"\n错误: {error_data.get('error')}"

        elif source_type == "ui_test":
            if error_data.get("console_errors"):
                count = len(error_data.get("console_errors", []))
                description += f"\n控制台错误数: {count}"
            if error_data.get("page"):
                description += f"\n页面: {error_data.get('page')}"

        elif source_type == "anti_crawl":
            if error_data.get("status"):
                description += f"\n反爬状态: {error_data.get('status')}"
            if error_data.get("attempts"):
                description += f"\n尝试次数: {error_data.get('attempts')}"

        elif source_type == "source_evolution":
            if error_data.get("reason"):
                description += f"\n原因: {error_data.get('reason')}"

        return description


# ═══════════════════════════════════════════════════════════════════════════
# 便捷函数
# ═══════════════════════════════════════════════════════════════════════════

_classifier: Optional[TaskClassifier] = None


def get_task_classifier() -> TaskClassifier:
    """获取任务分类器单例"""
    global _classifier
    if _classifier is None:
        _classifier = TaskClassifier()
    return _classifier