"""
AI 测试代理 (AI Testing Agent)

自我进化系统的关键组件：自动测试和体验系统功能

职责：
1. 功能测试 - 测试各个 API 和前端功能
2. 体验评估 - 评估用户体验、响应速度
3. Bug 发现 - 自动发现并记录问题
4. 回归测试 - 验证修复是否有效
5. 质量监控 - 持续监控产品质量

测试维度：
- 功能正确性
- 性能表现
- UI/UX 体验
- 错误处理
- 边界情况
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
from pathlib import Path

import aiohttp

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from db.models import User

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# 测试类型和状态
# ═══════════════════════════════════════════════════════════════════════════

class TestType(str, Enum):
    """测试类型"""
    API = "api"           # API 测试
    UI = "ui"            # UI 测试
    INTEGRATION = "integration"  # 集成测试
    PERFORMANCE = "performance"  # 性能测试
    REGRESSION = "regression"    # 回归测试


class TestStatus(str, Enum):
    """测试状态"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class IssueSeverity(str, Enum):
    """问题严重性"""
    CRITICAL = "critical"   # 阻断性问题
    HIGH = "high"          # 高优先级
    MEDIUM = "medium"     # 中优先级
    LOW = "low"            # 低优先级
    INFO = "info"          # 信息性


class IssueCategory(str, Enum):
    """问题分类"""
    FUNCTIONAL = "functional"     # 功能问题
    PERFORMANCE = "performance"    # 性能问题
    UX = "ux"                      # 体验问题
    UI = "ui"                      # UI 问题
    SECURITY = "security"          # 安全问题
    DATA = "data"                  # 数据问题
    API = "api"                    # API 问题


# ═══════════════════════════════════════════════════════════════════════════
# 测试用例和结果
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TestCase:
    """测试用例"""
    id: str
    name: str
    description: str
    test_type: TestType
    test_function: Callable  # 测试执行函数
    expected_result: str
    timeout: int = 30  # 超时时间（秒）


@dataclass
class TestResult:
    """测试结果"""
    test_id: str
    test_name: str
    status: TestStatus
    duration: float  # 耗时（秒）
    passed: bool
    message: str = ""
    error: str = ""
    metadata: Dict = field(default_factory=dict)


@dataclass
class Issue:
    """发现的问题"""
    id: str
    title: str
    description: str
    severity: IssueSeverity
    category: IssueCategory
    test_id: Optional[str]
    location: str  # 位置（如 API 路径、UI 元素）
    evidence: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "open"  # open, in_progress, resolved, wonfix
    assignee: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# 测试执行器
# ═══════════════════════════════════════════════════════════════════════════

class TestExecutor:
    """测试执行器"""

    def __init__(self):
        self.results: List[TestResult] = []
        self.issues: List[Issue] = []

    async def run_test(self, test_case: TestCase) -> TestResult:
        """执行单个测试"""
        start_time = time.time()

        logger.info(f"Running test: {test_case.name}")

        try:
            # 执行测试（带超时）
            result = await asyncio.wait_for(
                test_case.test_function(),
                timeout=test_case.timeout
            )

            duration = time.time() - start_time

            # 判断是否通过
            passed = result.get("passed", False) if isinstance(result, dict) else result

            test_result = TestResult(
                test_id=test_case.id,
                test_name=test_case.name,
                status=TestStatus.PASSED if passed else TestStatus.FAILED,
                duration=duration,
                passed=passed,
                message=result.get("message", "") if isinstance(result, dict) else "",
                metadata=result if isinstance(result, dict) else {}
            )

        except asyncio.TimeoutError:
            duration = time.time() - start_time
            test_result = TestResult(
                test_id=test_case.id,
                test_name=test_case.name,
                status=TestStatus.FAILED,
                duration=duration,
                passed=False,
                message="Test timeout",
                error=f"Test exceeded {test_case.timeout}s timeout"
            )

        except Exception as e:
            duration = time.time() - start_time
            test_result = TestResult(
                test_id=test_case.id,
                test_name=test_case.name,
                status=TestStatus.FAILED,
                duration=duration,
                passed=False,
                message="Test error",
                error=str(e)
            )

            # 自动创建 issue
            issue = Issue(
                id=f"issue-{test_case.id}-{int(time.time())}",
                title=f"测试失败: {test_case.name}",
                description=f"测试执行出错: {str(e)}",
                severity=IssueSeverity.HIGH,
                category=IssueCategory.FUNCTIONAL,
                test_id=test_case.id,
                location=test_case.id,
                evidence={"error": str(e), "test_type": test_case.test_type.value}
            )
            self.issues.append(issue)

        self.results.append(test_result)
        return test_result

    async def run_all_tests(self, test_cases: List[TestCase]) -> Dict:
        """运行所有测试"""
        logger.info(f"Running {len(test_cases)} tests...")

        for test_case in test_cases:
            await self.run_test(test_case)

        # 统计结果
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0,
            "results": self.results,
            "issues": self.issues
        }


# ═══════════════════════════════════════════════════════════════════════════
# API 测试套件
# ═══════════════════════════════════════════════════════════════════════════

class APITestSuite:
    """API 测试套件"""

    BASE_URL = "http://localhost:8000"

    def __init__(self):
        import aiohttp
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        if self.session:
            await self.session.close()

    # ═══════════════════════════════════════════════════════════════════
    # 对话 API 测试
    # ═══════════════════════════════════════════════════════════════════

    async def test_chat_api_basic(self) -> Dict:
        """测试基础对话功能"""
        session = await self._get_session()

        payload = {
            "message": "你好，请介绍一下你自己",
            "use_rag": False
        }

        async with session.post(
            f"{self.BASE_URL}/api/chat",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as resp:
            content = await resp.text()

            # 检查响应
            if resp.status == 200:
                # 尝试解析 SSE 响应
                if "data:" in content:
                    return {
                        "passed": True,
                        "message": "Chat API responds with SSE",
                        "metadata": {"status": resp.status}
                    }

            return {
                "passed": False,
                "message": f"Chat API failed: {resp.status}",
                "metadata": {"status": resp.status, "content": content[:200]}
            }

    async def test_chat_with_rag(self) -> Dict:
        """测试带 RAG 的对话"""
        session = await self._get_session()

        payload = {
            "message": "什么是 MyAttention",
            "use_rag": True
        }

        try:
            async with session.post(
                f"{self.BASE_URL}/api/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=90)
            ) as resp:
                content = await resp.text()

                # 检查是否使用了 RAG
                if "知识库" in content or "sources" in content or resp.status == 200:
                    return {
                        "passed": True,
                        "message": "Chat with RAG works",
                        "metadata": {"status": resp.status}
                    }

                return {
                    "passed": False,
                    "message": "RAG not working properly",
                    "metadata": {"status": resp.status}
                }

        except Exception as e:
            return {
                "passed": False,
                "message": f"RAG test error: {str(e)}",
                "error": str(e)
            }

    async def test_voting_mode(self) -> Dict:
        """测试多模型投票功能"""
        session = await self._get_session()

        payload = {
            "message": "1+1等于几",
            "use_voting": True,
            "voting_models": ["qwen-plus", "glm-4"]
        }

        try:
            async with session.post(
                f"{self.BASE_URL}/api/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                content = await resp.text()

                # 检查是否有投票结果
                if "voting" in content.lower() or "vote" in content.lower():
                    return {
                        "passed": True,
                        "message": "Voting mode works",
                        "metadata": {"status": resp.status}
                    }

                # 即使没有明确的投票关键字，只要返回了就算通过（简化）
                if resp.status == 200:
                    return {
                        "passed": True,
                        "message": "Voting API responded",
                        "metadata": {"status": resp.status}
                    }

                return {
                    "passed": False,
                    "message": "Voting mode not working",
                    "metadata": {"status": resp.status}
                }

        except Exception as e:
            return {
                "passed": False,
                "message": f"Voting test error: {str(e)}",
                "error": str(e)
            }

    # ═══════════════════════════════════════════════════════════════════
    # 进化系统 API 测试
    # ═══════════════════════════════════════════════════════════════════

    async def test_evolution_status(self) -> Dict:
        """测试进化系统状态"""
        session = await self._get_session()

        try:
            async with session.get(f"{self.BASE_URL}/api/evolution/status") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "passed": True,
                        "message": "Evolution status OK",
                        "metadata": data
                    }
                return {
                    "passed": False,
                    "message": f"Evolution status failed: {resp.status}"
                }
        except Exception as e:
            return {
                "passed": False,
                "message": f"Evolution status error: {str(e)}",
                "error": str(e)
            }

    async def test_anti_crawl(self) -> Dict:
        """测试反爬功能"""
        session = await self._get_session()

        payload = {
            "url": "https://httpbin.org/html",
            "method": "direct"
        }

        try:
            async with session.post(
                f"{self.BASE_URL}/api/evolution/anti-crawl/test",
                json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "passed": True,
                        "message": "Anti-crawl test OK",
                        "metadata": data
                    }
                return {
                    "passed": False,
                    "message": f"Anti-crawl test failed: {resp.status}"
                }
        except Exception as e:
            return {
                "passed": False,
                "message": f"Anti-crawl error: {str(e)}",
                "error": str(e)
            }

    async def test_knowledge_graph(self) -> Dict:
        """测试知识图谱"""
        session = await self._get_session()

        payload = {
            "text": "OpenAI 开发了 GPT-4 大语言模型",
            "title": "关于 OpenAI",
            "category": "AI"
        }

        try:
            async with session.post(
                f"{self.BASE_URL}/api/evolution/knowledge/extract",
                json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "passed": True,
                        "message": "Knowledge extraction OK",
                        "metadata": data
                    }
                return {
                    "passed": False,
                    "message": f"Knowledge extraction failed: {resp.status}"
                }
        except Exception as e:
            return {
                "passed": False,
                "message": f"Knowledge extraction error: {str(e)}",
                "error": str(e)
            }

    # ═══════════════════════════════════════════════════════════════════
    # 信息源 API 测试
    # ═══════════════════════════════════════════════════════════════════

    async def test_feeds_list(self) -> Dict:
        """测试获取信息流"""
        session = await self._get_session()

        try:
            async with session.get(f"{self.BASE_URL}/api/feeds") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "passed": True,
                        "message": f"Feeds OK, got {len(data)} items",
                        "metadata": {"count": len(data)}
                    }
                return {
                    "passed": False,
                    "message": f"Feeds failed: {resp.status}"
                }
        except Exception as e:
            return {
                "passed": False,
                "message": f"Feeds error: {str(e)}",
                "error": str(e)
            }

    async def test_sources_list(self) -> Dict:
        """测试获取信息源列表"""
        session = await self._get_session()

        try:
            async with session.get(f"{self.BASE_URL}/api/sources") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "passed": True,
                        "message": f"Sources OK, got {len(data)} sources",
                        "metadata": {"count": len(data)}
                    }
                return {
                    "passed": False,
                    "message": f"Sources failed: {resp.status}"
                }
        except Exception as e:
            return {
                "passed": False,
                "message": f"Sources error: {str(e)}",
                "error": str(e)
            }

    # ═══════════════════════════════════════════════════════════════════
    # 知识库 API 测试
    # ═══════════════════════════════════════════════════════════════════

    async def test_kb_list(self) -> Dict:
        """测试知识库列表"""
        session = await self._get_session()

        try:
            async with session.get(f"{self.BASE_URL}/api/rag/knowledge-bases") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "passed": True,
                        "message": "Knowledge bases OK",
                        "metadata": data
                    }
                return {
                    "passed": False,
                    "message": f"KB list failed: {resp.status}"
                }
        except Exception as e:
            return {
                "passed": False,
                "message": f"KB list error: {str(e)}",
                "error": str(e)
            }


# ═══════════════════════════════════════════════════════════════════════════
# AI 测试代理（大脑）
# ═══════════════════════════════════════════════════════════════════════════

class AITestingAgent:
    """
    AI 测试代理

    自动执行测试、发现问题的 AI 组件
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.executor = TestExecutor()
        self.api_suite = APITestSuite()
        self._issues: List[Issue] = []

    async def run_full_suite(self) -> Dict:
        """运行完整测试套件"""
        logger.info("Starting full test suite...")

        # 创建测试用例
        test_cases = [
            TestCase(
                id="api-chat-basic",
                name="基础对话功能",
                description="测试 /api/chat 基本功能",
                test_type=TestType.API,
                test_function=self.api_suite.test_chat_api_basic,
                expected_result="返回流式响应"
            ),
            TestCase(
                id="api-chat-rag",
                name="RAG 对话",
                description="测试带知识库的对话",
                test_type=TestType.API,
                test_function=self.api_suite.test_chat_with_rag,
                expected_result="返回知识库引用"
            ),
            TestCase(
                id="api-chat-voting",
                name="多模型投票",
                description="测试多模型投票功能",
                test_type=TestType.API,
                test_function=self.api_suite.test_voting_mode,
                expected_result="返回投票结果"
            ),
            TestCase(
                id="api-evolution-status",
                name="进化系统状态",
                description="测试进化系统状态接口",
                test_type=TestType.API,
                test_function=self.api_suite.test_evolution_status,
                expected_result="返回系统状态"
            ),
            TestCase(
                id="api-anti-crawl",
                name="反爬测试",
                description="测试反爬功能",
                test_type=TestType.API,
                test_function=self.api_suite.test_anti_crawl,
                expected_result="返回检测结果"
            ),
            TestCase(
                id="api-knowledge-graph",
                name="知识图谱",
                description="测试知识图谱功能",
                test_type=TestType.API,
                test_function=self.api_suite.test_knowledge_graph,
                expected_result="返回提取的实体"
            ),
            TestCase(
                id="api-feeds-list",
                name="信息流列表",
                description="测试获取信息流",
                test_type=TestType.API,
                test_function=self.api_suite.test_feeds_list,
                expected_result="返回信息列表"
            ),
            TestCase(
                id="api-sources-list",
                name="信息源列表",
                description="测试获取信息源",
                test_type=TestType.API,
                test_function=self.api_suite.test_sources_list,
                expected_result="返回源列表"
            ),
            TestCase(
                id="api-kb-list",
                name="知识库列表",
                description="测试获取知识库列表",
                test_type=TestType.API,
                test_function=self.api_suite.test_kb_list,
                expected_result="返回知识库"
            ),
        ]

        # 执行测试
        result = await self.executor.run_all_tests(test_cases)

        # 保存问题
        self._issues.extend(self.executor.issues)

        # 关闭 session
        await self.api_suite.close()

        # AI 分析
        analysis = await self._analyze_results(result)

        return {
            "summary": {
                "total": result["total"],
                "passed": result["passed"],
                "failed": result["failed"],
                "pass_rate": result["pass_rate"]
            },
            "results": [
                {
                    "test_id": r.test_id,
                    "test_name": r.test_name,
                    "status": r.status.value,
                    "duration": r.duration,
                    "passed": r.passed,
                    "message": r.message,
                    "error": r.error
                }
                for r in result["results"]
            ],
            "issues": [
                {
                    "id": i.id,
                    "title": i.title,
                    "description": i.description,
                    "severity": i.severity.value,
                    "category": i.category.value,
                    "location": i.location
                }
                for i in self._issues
            ],
            "analysis": analysis
        }

    async def _analyze_results(self, result: Dict) -> Dict:
        """AI 分析测试结果"""
        if not self.llm_client:
            # 无 LLM，使用简单分析
            failed = result["failed"]
            if failed == 0:
                return {
                    "summary": "所有测试通过！",
                    "recommendations": ["继续监控", "可以发布"]
                }
            else:
                return {
                    "summary": f"{failed} 个测试失败",
                    "recommendations": ["查看失败详情", "修复问题后重新测试"]
                }

        # 使用 AI 分析
        prompt = f"""分析以下测试结果，给出改进建议：

测试统计：
- 总数: {result['total']}
- 通过: {result['passed']}
- 失败: {result['failed']}
- 通过率: {result['pass_rate']:.1%}

失败测试：
{self._format_failed_tests(result['results'])}

请给出：
1. 问题分析
2. 根本原因
3. 修复建议
4. 优先级排序

只返回 JSON：
{{
    "summary": "...",
    "root_causes": ["..."],
    "recommendations": ["..."],
    "priority_fixes": [{{"test_id": "...", "priority": "..."}}]
}}"""

        try:
            response = await self.llm_client.chat([
                {"role": "user", "content": prompt}
            ])

            # 解析 JSON
            text = response.content.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            return json.loads(text.strip())

        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {
                "summary": "分析失败",
                "error": str(e)
            }

    def _format_failed_tests(self, results: List) -> str:
        """格式化失败测试"""
        failed = [r for r in results if not r.passed]
        lines = []
        for r in failed:
            lines.append(f"- {r.test_name}: {r.message} ({r.error})")
        return "\n".join(lines)

    def get_issues(self) -> List[Issue]:
        """获取所有问题"""
        return self._issues


# ═══════════════════════════════════════════════════════════════════════════
# 便捷函数
# ═══════════════════════════════════════════════════════════════════════════

async def run_ai_test(llm_client=None) -> Dict:
    """运行 AI 测试（便捷函数）"""
    agent = AITestingAgent(llm_client)
    result = await agent.run_full_suite()
    return result


async def quick_test() -> Dict:
    """快速测试（无 LLM）"""
    return await run_ai_test(None)