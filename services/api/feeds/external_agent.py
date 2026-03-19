"""
外部 AI Agent 集成 (External AI Agent Integration)

通过标准协议与外部 AI Agent 系统（如 OpenClaw、AutoGen 等）集成

支持的协议：
1. HTTP/REST API - 直接调用外部 Agent API
2. A2A (Agent-to-Agent) - Agent 间通信协议
3. MCP (Model Context Protocol) - Anthropic 的 Agent 协议

这样 MyAttention 不需要重复造轮子，可以调用强大的外部 AI 能力
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime, timezone
from enum import Enum

import aiohttp

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# 协议定义
# ═══════════════════════════════════════════════════════════════════════════

class AgentProtocol(str, Enum):
    """Agent 通信协议"""
    REST = "rest"      # HTTP REST API
    A2A = "a2a"        # Agent-to-Agent 协议
    MCP = "mcp"        # Model Context Protocol


@dataclass
class AgentRequest:
    """Agent 请求"""
    task: str                          # 任务描述
    context: Dict[str, Any] = field(default_factory=dict)  # 上下文
    parameters: Dict[str, Any] = field(default_factory=dict)  # 参数
    protocol: AgentProtocol = AgentProtocol.REST


@dataclass
class AgentResponse:
    """Agent 响应"""
    success: bool
    result: Any = None
    error: str = ""
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════
# 外部 Agent 客户端
# ═══════════════════════════════════════════════════════════════════════════

class ExternalAgentClient:
    """
    外部 AI Agent 客户端

    通过 HTTP/A2A 协议调用外部 Agent 服务
    """

    def __init__(
        self,
        endpoint: str = "http://localhost:8080",
        api_key: str = "",
        protocol: AgentProtocol = AgentProtocol.REST,
        timeout: int = 60
    ):
        """
        Args:
            endpoint: Agent 服务端点
            api_key: API 密钥
            protocol: 通信协议
            timeout: 超时时间（秒）
        """
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.protocol = protocol
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建会话"""
        if self._session is None or self._session.closed:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session

    async def close(self):
        """关闭会话"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def call(
        self,
        task: str,
        context: Dict[str, Any] = None,
        parameters: Dict[str, Any] = None
    ) -> AgentResponse:
        """
        调用外部 Agent 执行任务

        Args:
            task: 任务描述
            context: 上下文信息
            parameters: 额外参数

        Returns:
            AgentResponse: 执行结果
        """
        start_time = datetime.now(timezone.utc)

        try:
            if self.protocol == AgentProtocol.REST:
                return await self._call_rest(task, context or {}, parameters or {})
            elif self.protocol == AgentProtocol.A2A:
                return await self._call_a2a(task, context or {}, parameters or {})
            elif self.protocol == AgentProtocol.MCP:
                return await self._call_mcp(task, context or {}, parameters or {})
            else:
                return AgentResponse(
                    success=False,
                    error=f"Unknown protocol: {self.protocol}"
                )
        except Exception as e:
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            return AgentResponse(
                success=False,
                error=str(e),
                execution_time=execution_time
            )

    async def _call_rest(
        self,
        task: str,
        context: Dict,
        parameters: Dict
    ) -> AgentResponse:
        """通过 REST API 调用"""
        session = await self._get_session()

        payload = {
            "task": task,
            "context": context,
            "parameters": parameters
        }

        async with session.post(
            f"{self.endpoint}/execute",
            json=payload,
            timeout=self.timeout
        ) as resp:
            execution_time = (datetime.now(timezone.utc) - datetime.now(timezone.utc)).total_seconds()

            if resp.status == 200:
                data = await resp.json()
                return AgentResponse(
                    success=True,
                    result=data.get("result"),
                    execution_time=data.get("execution_time", execution_time),
                    metadata=data.get("metadata", {})
                )
            else:
                error_text = await resp.text()
                return AgentResponse(
                    success=False,
                    error=f"HTTP {resp.status}: {error_text}",
                    execution_time=execution_time
                )

    async def _call_a2a(
        self,
        task: str,
        context: Dict,
        parameters: Dict
    ) -> AgentResponse:
        """
        通过 A2A 协议调用

        A2A 协议格式：
        {
            "jsonrpc": "2.0",
            "id": "unique-id",
            "method": "agent.execute",
            "params": {
                "task": "...",
                "context": {...},
                "capabilities": [...]
            }
        }
        """
        session = await self._get_session()

        a2a_request = {
            "jsonrpc": "2.0",
            "id": f"myattention-{datetime.now(timezone.utc).timestamp()}",
            "method": "agent.execute",
            "params": {
                "task": task,
                "context": context,
                "capabilities": [
                    "web_search",
                    "content_analysis",
                    "reasoning",
                    "knowledge_graph"
                ]
            }
        }

        async with session.post(
            f"{self.endpoint}/rpc",
            json=a2a_request,
            timeout=self.timeout
        ) as resp:
            execution_time = (datetime.now(timezone.utc) - datetime.now(timezone.utc)).total_seconds()

            if resp.status == 200:
                data = await resp.json()

                if "error" in data:
                    return AgentResponse(
                        success=False,
                        error=data["error"].get("message", "Unknown error"),
                        execution_time=execution_time
                    )

                return AgentResponse(
                    success=True,
                    result=data.get("result", {}).get("output"),
                    execution_time=execution_time,
                    metadata=data.get("result", {}).get("metadata", {})
                )
            else:
                return AgentResponse(
                    success=False,
                    error=f"HTTP {resp.status}",
                    execution_time=execution_time
                )

    async def _call_mcp(
        self,
        task: str,
        context: Dict,
        parameters: Dict
    ) -> AgentResponse:
        """通过 MCP 协议调用"""
        session = await self._get_session()

        mcp_request = {
            "jsonrpc": "2.0",
            "id": f"myattention-{datetime.now(timezone.utc).timestamp()}",
            "method": "tools/call",
            "params": {
                "name": "execute_task",
                "arguments": {
                    "task": task,
                    "context": context
                }
            }
        }

        async with session.post(
            f"{self.endpoint}/mcp",
            json=mcp_request,
            timeout=self.timeout
        ) as resp:
            execution_time = (datetime.now(timezone.utc) - datetime.now(timezone.utc)).total_seconds()

            if resp.status == 200:
                data = await resp.json()
                return AgentResponse(
                    success=True,
                    result=data.get("result", {}),
                    execution_time=execution_time
                )
            else:
                return AgentResponse(
                    success=False,
                    error=f"HTTP {resp.status}",
                    execution_time=execution_time
                )


# ═══════════════════════════════════════════════════════════════════════════
# Agent 注册表 - 管理多个外部 Agent
# ═══════════════════════════════════════════════════════════════════════════

class AgentRegistry:
    """Agent 注册表 - 管理可用的外部 Agent"""

    def __init__(self):
        self._agents: Dict[str, ExternalAgentClient] = {}
        self._default_agent: Optional[str] = None

    def register(
        self,
        name: str,
        endpoint: str,
        api_key: str = "",
        protocol: AgentProtocol = AgentProtocol.REST,
        set_default: bool = False
    ):
        """注册一个 Agent"""
        client = ExternalAgentClient(
            endpoint=endpoint,
            api_key=api_key,
            protocol=protocol
        )
        self._agents[name] = client

        if set_default or not self._default_agent:
            self._default_agent = name

        logger.info(f"Registered agent: {name} -> {endpoint}")

    def get(self, name: str = None) -> Optional[ExternalAgentClient]:
        """获取 Agent 客户端"""
        if name is None:
            name = self._default_agent
        return self._agents.get(name)

    def list_agents(self) -> List[str]:
        """列出所有注册的 Agent"""
        return list(self._agents.keys())

    async def close_all(self):
        """关闭所有 Agent 连接"""
        for agent in self._agents.values():
            await agent.close()


# ═══════════════════════════════════════════════════════════════════════════
# MyAttention AI 集成层
# ═══════════════════════════════════════════════════════════════════════════

class MyAttentionAIIntegration:
    """
    MyAttention AI 集成层

    封装对外部 AI Agent 的调用，提供给内部模块使用
    """

    def __init__(self):
        self.registry = AgentRegistry()

        # 默认配置（从环境变量读取）
        import os

        # 注册默认的 Agent（通常是本地或云端的 OpenClaw/MCP 服务）
        default_endpoint = os.environ.get("AGENT_ENDPOINT", "http://localhost:8080")
        if default_endpoint:
            self.registry.register(
                name="default",
                endpoint=default_endpoint,
                api_key=os.environ.get("AGENT_API_KEY", ""),
                protocol=AgentProtocol(os.environ.get("AGENT_PROTOCOL", "a2a")),
                set_default=True
            )

    async def analyze_problem(
        self,
        problem: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """
        让 AI Agent 分析问题

        用途：
        - 分析反爬原因
        - 分析源效果下降原因
        - 分析知识提取问题
        """
        task = f"""你是一个信息源管理专家。请分析以下问题：

问题：{problem}

背景信息：
{json.dumps(context, ensure_ascii=False, indent=2)}

请提供：
1. 问题根因分析
2. 可能的解决方案
3. 每个方案的优缺点
4. 推荐的最优方案

请以 JSON 格式返回。"""

        agent = self.registry.get()
        if not agent:
            return AgentResponse(
                success=False,
                error="No agent configured"
            )

        return await agent.call(
            task=task,
            context=context,
            parameters={"analysis_mode": "root_cause"}
        )

    async def make_decision(
        self,
        decision_type: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """
        让 AI Agent 做决策

        用途：
        - 信息源优化决策
        - 获取策略选择
        - 知识提取方案
        """
        task = f"""你是一个智能信息源管理系统的决策大脑。请为以下决策类型做出最佳选择：

决策类型：{decision_type}

当前状态：
{json.dumps(context, ensure_ascii=False, indent=2)}

请以 JSON 格式返回决策：
{{
    "action": "具体要执行的行动",
    "reasoning": "为什么选择这个行动",
    "confidence": 0.0-1.0,
    "alternative_actions": ["备选方案"],
    "expected_outcome": "预期结果"
}}"""

        agent = self.registry.get()
        if not agent:
            return AgentResponse(
                success=False,
                error="No agent configured"
            )

        return await agent.call(
            task=task,
            context=context,
            parameters={"decision_type": decision_type}
        )

    async def extract_knowledge(
        self,
        text: str,
        context: str = ""
    ) -> AgentResponse:
        """
        让 AI Agent 提取知识

        用途：
        - 从信息中提取实体
        - 抽取关系
        - 生成摘要
        """
        task = f"""你是一个知识提取专家。请从以下文本中提取结构化知识：

文本：{text[:3000]}

上下文：{context}

请提取：
1. 实体（人物、组织、概念、技术等）
2. 实体间关系
3. 关键信息摘要
4. 标签/分类

请以 JSON 格式返回。"""

        agent = self.registry.get()
        if not agent:
            return AgentResponse(
                success=False,
                error="No agent configured"
            )

        return await agent.call(
            task=task,
            context={"text": text, "context": context},
            parameters={"extraction_mode": "knowledge_graph"}
        )

    async def discover_sources(
        self,
        domain: str,
        criteria: Dict[str, Any] = None
    ) -> AgentResponse:
        """
        让 AI Agent 发现新信息源
        """
        task = f"""你是一个信息源发现专家。请为以下领域发现高质量的信息源：

领域：{domain}

条件：{json.dumps(criteria or {}, ensure_ascii=False)}

请发现：
1. 相关的 RSS 源
2. 相关的网站/博客
3. 相关的社交媒体账号

请按权威性排序，并给出每个源的评估。"""

        agent = self.registry.get()
        if not agent:
            return AgentResponse(
                success=False,
                error="No agent configured"
            )

        return await agent.call(
            task=task,
            context={"domain": domain, "criteria": criteria or {}},
            parameters={"discovery_mode": "sources"}
        )

    async def reason(
        self,
        query: str,
        knowledge: List[Dict]
    ) -> AgentResponse:
        """
        让 AI Agent 进行知识推理
        """
        task = f"""你是一个知识推理专家。请基于以下知识回答问题：

问题：{query}

知识库：
{json.dumps(knowledge[:10], ensure_ascii=False, indent=2)}

请进行推理并给出答案。"""

        agent = self.registry.get()
        if not agent:
            return AgentResponse(
                success=False,
                error="No agent configured"
            )

        return await agent.call(
            task=task,
            context={"query": query, "knowledge": knowledge},
            parameters={"reasoning_mode": "inductive"}
        )


# ═══════════════════════════════════════════════════════════════════════════
# 全局实例
# ═══════════════════════════════════════════════════════════════════════════

_ai_integration: Optional[MyAttentionAIIntegration] = None


def get_ai_integration() -> MyAttentionAIIntegration:
    """获取 AI 集成实例"""
    global _ai_integration
    if _ai_integration is None:
        _ai_integration = MyAttentionAIIntegration()
    return _ai_integration


# 便捷函数
async def ai_analyze_problem(problem: str, context: Dict) -> AgentResponse:
    """AI 分析问题"""
    integration = get_ai_integration()
    return await integration.analyze_problem(problem, context)


async def ai_make_decision(decision_type: str, context: Dict) -> AgentResponse:
    """AI 决策"""
    integration = get_ai_integration()
    return await integration.make_decision(decision_type, context)


async def ai_extract_knowledge(text: str, context: str = "") -> AgentResponse:
    """AI 知识提取"""
    integration = get_ai_integration()
    return await integration.extract_knowledge(text, context)


async def ai_discover_sources(domain: str, criteria: Dict = None) -> AgentResponse:
    """AI 发现源"""
    integration = get_ai_integration()
    return await integration.discover_sources(domain, criteria)


async def ai_reason(query: str, knowledge: List[Dict]) -> AgentResponse:
    """AI 推理"""
    integration = get_ai_integration()
    return await integration.reason(query, knowledge)