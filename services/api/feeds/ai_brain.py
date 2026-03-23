"""
AI 决策大脑 (AI Decision Brain)

核心思想：调用外部 AI Agent 服务，而不是在内部重复造轮子

支持：
1. 本地 LLM 回退 - 没有外部 Agent 时使用本地模型
2. 外部 Agent 调用 - 通过 A2A/REST/MCP 协议调用 OpenClaw 等服务
3. 混合模式 - 本地决策 + 外部 Agent 复杂推理
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Source, SourceMetrics, FeedItem, AntiCrawlStatus, AccessMethod

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# 决策类型
# ═══════════════════════════════════════════════════════════════════════════

class DecisionType(str, Enum):
    """决策类型"""
    ANALYZE = "analyze"           # 分析问题
    FETCH_STRATEGY = "fetch"      # 获取策略
    SOURCE_EVAL = "source_eval"  # 源评估
    KNOWLEDGE_EXTRACT = "extract" # 知识提取
    DISCOVERY = "discovery"       # 新源发现
    REASONING = "reasoning"       # 知识推理


@dataclass
class DecisionContext:
    """决策上下文"""
    decision_type: DecisionType

    # 源信息
    source_id: str = ""
    source_name: str = ""
    source_url: str = ""
    source_category: str = ""

    # 当前状态
    current_status: str = ""      # 当前反爬状态
    error_message: str = ""       # 错误信息
    error_details: Dict = field(default_factory=dict)

    # 历史数据
    success_count: int = 0
    failure_count: int = 0
    read_rate: float = 0.0

    # 目标
    goal: str = ""

    # 可用选项
    available_methods: List[str] = field(default_factory=lambda: ["direct", "proxy", "cloud"])
    available_actions: List[str] = field(default_factory=list)


@dataclass
class Decision:
    """AI 决策结果"""
    action: str                   # 执行的行动
    reasoning: str                # 推理过程
    confidence: float             # 置信度 0-1
    alternative_actions: List[str] = field(default_factory=list)  # 备选方案
    expected_outcome: str = ""    # 预期结果
    learning_notes: str = ""     # 学习笔记


@dataclass
class DecisionResult:
    """执行结果"""
    success: bool
    action: str
    result_data: Dict = field(default_factory=dict)
    feedback: str = ""
    actual_outcome: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# AI 决策大脑
# ═══════════════════════════════════════════════════════════════════════════

class AIDecisionBrain:
    """
    AI 决策大脑

    决策优先级：
    1. 外部 Agent（OpenClaw 等）- 用于复杂决策和推理
    2. 本地 LLM - 用于快速决策
    3. 规则回退 - 兜底方案
    """

    def __init__(self, llm_client=None, use_external_agent: bool = True):
        """
        Args:
            llm_client: 本地 LLM 客户端
            use_external_agent: 是否优先使用外部 Agent
        """
        self.llm_client = llm_client
        self.use_external_agent = use_external_agent
        self._external_agent = None
        self._decision_history: List[Dict] = []

    async def _get_external_agent(self):
        """获取外部 Agent 客户端"""
        if self._external_agent is None and self.use_external_agent:
            try:
                from feeds.external_agent import get_ai_integration
                self._external_agent = get_ai_integration()
            except Exception as e:
                logger.warning(f"Failed to load external agent: {e}")
        return self._external_agent

    async def decide(self, context: DecisionContext) -> Decision:
        """
        核心决策方法

        优先使用外部 Agent，其次使用本地 LLM，最后回退到规则
        """
        # 1. 尝试外部 Agent
        if self.use_external_agent:
            external = await self._get_external_agent()
            if external:
                try:
                    response = await external.make_decision(
                        decision_type=context.decision_type.value,
                        context={
                            "source_name": context.source_name,
                            "source_url": context.source_url,
                            "current_status": context.current_status,
                            "error_message": context.error_message,
                            "success_count": context.success_count,
                            "failure_count": context.failure_count,
                            "read_rate": context.read_rate,
                            "goal": context.goal
                        }
                    )

                    if response.success and response.result:
                        # 解析外部 Agent 的响应
                        return self._parse_external_response(response.result, context)
                except Exception as e:
                    logger.warning(f"External agent failed: {e}, falling back to local LLM")

        # 2. 使用本地 LLM
        if self.llm_client:
            return await self._decide_with_local_llm(context)

        # 3. 回退到规则
        return self._fallback_decision(context)

    async def _decide_with_local_llm(self, context: DecisionContext) -> Decision:
        """使用本地 LLM 决策"""
        prompt = self._build_decision_prompt(context)

        try:
            response = await self.llm_client.chat([
                {"role": "user", "content": prompt}
            ])

            decision = self._parse_decision(self._extract_response_text(response), context)
            self._record_decision(context, decision)
            return decision

        except Exception as e:
            logger.error(f"Local LLM decision failed: {e}")
            return self._fallback_decision(context)

    def _extract_response_text(self, response: Any) -> str:
        """兼容不同 LLM 客户端返回格式，统一提取文本。"""
        if isinstance(response, str):
            return response

        content = getattr(response, "content", None)
        if isinstance(content, str):
            return content

        text = getattr(response, "text", None)
        if isinstance(text, str):
            return text

        if isinstance(response, dict):
            for key in ("content", "text", "response", "output"):
                value = response.get(key)
                if isinstance(value, str):
                    return value

        raise TypeError(f"Unsupported LLM response type: {type(response).__name__}")

    def _parse_external_response(self, result: Any, context: DecisionContext) -> Decision:
        """解析外部 Agent 响应"""
        try:
            if isinstance(result, str):
                data = json.loads(result)
            elif isinstance(result, dict):
                data = result
            else:
                return self._fallback_decision(context)

            return Decision(
                action=data.get("action", "continue"),
                reasoning=data.get("reasoning", "来自外部 Agent"),
                confidence=float(data.get("confidence", 0.5)),
                alternative_actions=data.get("alternative_actions", []),
                expected_outcome=data.get("expected_outcome", ""),
                learning_notes=data.get("learning_notes", "")
            )
        except Exception as e:
            logger.warning(f"Failed to parse external response: {e}")
            return self._fallback_decision(context)

    def _build_decision_prompt(self, context: DecisionContext) -> str:
        """构建决策提示词"""

        system_prompt = """你是一个智能信息源管理系统的AI决策大脑。你的任务是根据当前情况做出最佳决策。

决策类型：{decision_type}

当前信息源：
- 名称：{source_name}
- URL：{source_url}
- 分类：{source_category}

当前状态：
- 反爬状态：{current_status}
- 错误信息：{error_message}
- 成功次数：{success_count}
- 失败次数：{failure_count}
- 阅读率：{read_rate}

可用方法：{available_methods}
可用动作：{available_actions}

目标：{goal}

请以JSON格式返回决策：
{{
    "action": "具体要执行的行动",
    "reasoning": "推理过程（为什么选择这个行动）",
    "confidence": 0.0-1.0的置信度,
    "alternative_actions": ["备选方案1", "备选方案2"],
    "expected_outcome": "预期结果",
    "learning_notes": "这次决策学到了什么"
}}

只返回JSON，不要其他内容。"""

        return system_prompt.format(
            decision_type=context.decision_type.value,
            source_name=context.source_name or "未知",
            source_url=context.source_url or "未知",
            source_category=context.source_category or "未分类",
            current_status=context.current_status or "正常",
            error_message=context.error_message or "无",
            success_count=context.success_count,
            failure_count=context.failure_count,
            read_rate=f"{context.read_rate:.2%}",
            available_methods=", ".join(context.available_methods),
            available_actions=", ".join(context.available_actions) if context.available_actions else "无限制",
            goal=context.goal or "优化信息源性能"
        )

    def _parse_decision(self, response: str, context: DecisionContext) -> Decision:
        """解析 AI 响应"""
        try:
            # 提取 JSON
            text = response.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            data = json.loads(text.strip())

            return Decision(
                action=data.get("action", "continue"),
                reasoning=data.get("reasoning", ""),
                confidence=float(data.get("confidence", 0.5)),
                alternative_actions=data.get("alternative_actions", []),
                expected_outcome=data.get("expected_outcome", ""),
                learning_notes=data.get("learning_notes", "")
            )

        except Exception as e:
            logger.warning(f"Failed to parse AI decision: {e}")
            return self._fallback_decision(context)

    def _fallback_decision(self, context: DecisionContext) -> Decision:
        """回退到简单规则决策"""
        # 简单的规则回退
        if context.error_message:
            if "403" in context.error_message or "blocked" in context.error_message.lower():
                return Decision(
                    action="switch_to_proxy",
                    reasoning="检测到被封禁，切换到代理",
                    confidence=0.9,
                    alternative_actions=["switch_to_cloud", "reduce_frequency"]
                )
            elif "timeout" in context.error_message.lower():
                return Decision(
                    action="retry_with_longer_timeout",
                    reasoning="请求超时，增加超时时间重试",
                    confidence=0.7
                )

        # 检查失败率
        total = context.success_count + context.failure_count
        if total > 0:
            failure_rate = context.failure_count / total
            if failure_rate > 0.5:
                return Decision(
                    action="disable_source",
                    reasoning="失败率过高，建议禁用",
                    confidence=0.9
                )
            elif failure_rate > 0.3:
                return Decision(
                    action="increase_depth",
                    reasoning="失败率中等，增加获取深度",
                    confidence=0.6
                )

        return Decision(
            action="continue",
            reasoning="状态正常，保持当前策略",
            confidence=0.8
        )

    def _record_decision(self, context: DecisionContext, decision: Decision):
        """记录决策历史用于学习"""
        self._decision_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision_type": context.decision_type.value,
            "source_id": context.source_id,
            "action": decision.action,
            "reasoning": decision.reasoning,
            "confidence": decision.confidence,
            "error": context.error_message
        })

        # 保留最近100条
        if len(self._decision_history) > 100:
            self._decision_history = self._decision_history[-100:]

    def get_learning_insights(self) -> Dict[str, Any]:
        """从决策历史中提取学习洞察"""
        if not self._decision_history:
            return {"insights": "No history yet", "patterns": []}

        # 统计
        action_counts: Dict[str, int] = {}
        for record in self._decision_history:
            action = record["action"]
            action_counts[action] = action_counts.get(action, 0) + 1

        # 找出最常见的行动
        most_common = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_decisions": len(self._decision_history),
            "action_distribution": dict(most_common),
            "last_decision": self._decision_history[-1] if self._decision_history else None
        }


# ═══════════════════════════════════════════════════════════════════════════
# AI 驱动的进化引擎
# ═══════════════════════════════════════════════════════════════════════════

class AIEvolutionEngine:
    """
    AI 驱动的进化引擎

    使用 AI 大脑替代静态规则进行决策
    """

    def __init__(self, db: AsyncSession, llm_client=None):
        self.db = db
        self.brain = AIDecisionBrain(llm_client)

    async def evaluate_and_evolve(self, source_id: str) -> Dict[str, Any]:
        """
        AI 驱动的源评估和进化

        流程：
        1. 收集源的所有信息
        2. 让 AI 分析问题
        3. 让 AI 制定决策
        4. 执行决策
        5. 记录结果让 AI 学习
        """
        # 1. 收集信息
        source = await self._gather_source_info(source_id)
        if not source:
            return {"error": "Source not found"}

        # 2. 构建决策上下文
        context = self._build_context(source)

        # 3. AI 决策
        decision = await self.brain.decide(context)

        # 4. 执行决策
        result = await self._execute_decision(source, decision)

        # 5. 记录学习
        await self._learn_from_result(source, decision, result)

        return {
            "source_id": source_id,
            "source_name": source.name,
            "decision": {
                "action": decision.action,
                "reasoning": decision.reasoning,
                "confidence": decision.confidence
            },
            "result": {
                "success": result.success,
                "feedback": result.feedback
            }
        }

    async def _gather_source_info(self, source_id: str) -> Optional[Source]:
        """收集源信息"""
        result = await self.db.execute(
            select(Source).where(Source.id == source_id)
        )
        return result.scalar_one_or_none()

    def _build_context(self, source: Source) -> DecisionContext:
        """构建决策上下文"""
        return DecisionContext(
            decision_type=DecisionType.SOURCE_EVAL,
            source_id=str(source.id),
            source_name=source.name,
            source_url=source.url,
            source_category=source.category or "",
            current_status=source.anti_crawl_status.value if source.anti_crawl_status else "ok",
            success_count=source.success_count,
            failure_count=source.failure_count,
            available_methods=[m.value for m in [source.access_method]],
            available_actions=[
                "switch_to_proxy",
                "switch_to_cloud",
                "increase_depth",
                "decrease_depth",
                "disable_source",
                "increase_frequency",
                "decrease_frequency"
            ],
            goal="最大化信息获取质量"
        )

    async def _execute_decision(self, source: Source, decision: Decision) -> DecisionResult:
        """执行 AI 决策"""
        action = decision.action

        try:
            if action == "switch_to_proxy":
                source.access_method = AccessMethod.PROXY
                await self.db.commit()
                return DecisionResult(
                    success=True,
                    action=action,
                    result_data={"new_method": "proxy"},
                    feedback="已切换到代理访问"
                )

            elif action == "switch_to_cloud":
                source.access_method = AccessMethod.CLOUD
                await self.db.commit()
                return DecisionResult(
                    success=True,
                    action=action,
                    result_data={"new_method": "cloud"},
                    feedback="已切换到云访问"
                )

            elif action == "increase_depth":
                if source.fetch_depth < 3:
                    source.fetch_depth += 1
                    await self.db.commit()
                return DecisionResult(
                    success=True,
                    action=action,
                    result_data={"new_depth": source.fetch_depth},
                    feedback=f"已增加获取深度到 L{source.fetch_depth}"
                )

            elif action == "decrease_depth":
                if source.fetch_depth > 1:
                    source.fetch_depth -= 1
                    await self.db.commit()
                return DecisionResult(
                    success=True,
                    action=action,
                    result_data={"new_depth": source.fetch_depth},
                    feedback=f"已降低获取深度到 L{source.fetch_depth}"
                )

            elif action == "disable_source":
                source.enabled = False
                await self.db.commit()
                return DecisionResult(
                    success=True,
                    action=action,
                    result_data={"enabled": False},
                    feedback="已禁用该信息源"
                )

            else:
                return DecisionResult(
                    success=True,
                    action=action,
                    feedback="继续当前策略"
                )

        except Exception as e:
            return DecisionResult(
                success=False,
                action=action,
                feedback=f"执行失败: {str(e)}"
            )

    async def _learn_from_result(
        self,
        source: Source,
        decision: Decision,
        result: DecisionResult
    ):
        """从结果中学习"""
        # 可以将结果反馈给 AI 进行学习
        # 目前简单记录到日志
        logger.info(
            f"Decision result: action={decision.action}, "
            f"success={result.success}, feedback={result.feedback}"
        )

    async def evolve_all_with_ai(self) -> Dict[str, Any]:
        """批量 AI 进化所有源"""
        result = await self.db.execute(
            select(Source).where(Source.enabled == True)
        )
        sources = result.scalars().all()

        results = []
        for source in sources:
            eval_result = await self.evaluate_and_evolve(str(source.id))
            results.append(eval_result)

        return {
            "total": len(sources),
            "results": results,
            "insights": self.brain.get_learning_insights()
        }


# ═══════════════════════════════════════════════════════════════════════════
# 智能知识提取
# ═══════════════════════════════════════════════════════════════════════════

class AIKnowledgeExtractor:
    """
    AI 知识提取器

    使用 AI 从信息中提取结构化知识
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    async def extract(self, text: str, context: str = "") -> Dict[str, Any]:
        """
        使用 AI 提取知识

        Returns:
            包含实体、关系、摘要的字典
        """
        if not self.llm_client:
            return {"error": "No LLM client"}

        prompt = f"""你是一个知识提取专家。从以下文本中提取结构化知识：

文本：
{text[:3000]}

上下文（可选）：{context}

请以JSON格式返回：
{{
    "summary": "一句话摘要",
    "entities": [
        {{"name": "实体名", "type": "person/org/tech/concept", "description": "描述"}}
    ],
    "relations": [
        {{"source": "实体1", "target": "实体2", "type": "关系类型"}}
    ],
    "keywords": ["关键词1", "关键词2"],
    "importance": 0.0-1.0,
    "topics": ["主题1", "主题2"]
}}

只返回JSON。"""

        try:
            response = await self.llm_client.chat([
                {"role": "user", "content": prompt}
            ])

            text = self._extract_response_text(response).strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            return json.loads(text.strip())

        except Exception as e:
            logger.error(f"Knowledge extraction failed: {e}")
            return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
# 便捷函数
# ═══════════════════════════════════════════════════════════════════════════

_brain: Optional[AIDecisionBrain] = None


def get_ai_brain(llm_client=None) -> AIDecisionBrain:
    """获取 AI 大脑实例"""
    global _brain
    if _brain is None:
        _brain = AIDecisionBrain(llm_client)
    return _brain
