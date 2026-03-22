"""
Multi-Model Voting System

For critical decisions, this module runs the same query against multiple
LLM models in parallel and synthesizes their responses into a consensus.

Voting Process:
1. Parallel invocation of multiple models
2. Semantic similarity analysis to find consensus points
3. Difference annotation for divergent views
4. Confidence calculation based on agreement level
5. Comprehensive report generation
"""

from typing import List, Dict, Any, Optional, AsyncGenerator, Union
import asyncio
import logging
from dataclasses import dataclass, field

from .adapter import LLMAdapter

import os, sys

_voting_logger = logging.getLogger("myattention.voting")
_voting_logger.setLevel(logging.DEBUG)
if not _voting_logger.handlers:
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(logging.Formatter("[%(asctime)s] [voting] %(message)s", datefmt="%H:%M:%S"))
    _h.setLevel(logging.DEBUG)
    _voting_logger.addHandler(_h)
    _log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chat_debug.log")
    _fh = logging.FileHandler(_log_file, encoding="utf-8")
    _fh.setFormatter(logging.Formatter("[%(asctime)s] [voting] %(message)s", datefmt="%H:%M:%S"))
    _fh.setLevel(logging.DEBUG)
    _voting_logger.addHandler(_fh)

def _vlog(msg: str):
    _voting_logger.info(msg)


@dataclass
class VotingResult:
    """Result from a single model in the voting process"""
    model: str
    provider: str
    content: str
    success: bool
    error: Optional[str] = None


@dataclass
class StreamEvent:
    """Event for streaming multi-model voting"""
    event_type: str  # "content", "complete", "error"
    model: str
    data: str = ""


@dataclass
class ConsensusResult:
    """Final consensus result from multi-model voting"""
    consensus: str
    confidence: float
    individual_results: List[VotingResult]
    agreements: List[str]
    disagreements: List[str]


class MultiModelVoting:
    """
    Multi-model voting system for critical decisions
    
    Available models (Alibaba Cloud Bailian API):
    - qwen3.5-plus (supports web search)
    - MiniMax-M2.5 (supports web search)
    - deepseek-v3.2 (supports web search)
    - glm-5
    - kimi-k2.5
    
    When only one capability is requested, only models supporting that capability participate.
    When both search and thinking are requested, models supporting either capability participate.
    Models supporting both capabilities act as primary decision models.
    """
    
    # Available voting models on Bailian platform
    BAILIAN_MODELS = {
        "qwen3.5-plus": {"provider": "qwen", "model": "qwen3.5-plus", "supports_search": True, "supports_thinking": True},
        "MiniMax-M2.5": {"provider": "qwen", "model": "MiniMax-M2.5", "supports_search": True, "supports_thinking": False},
        "deepseek-v3.2": {"provider": "qwen", "model": "deepseek-v3.2", "supports_search": True, "supports_thinking": True},
        "glm-5": {"provider": "qwen", "model": "glm-5", "supports_search": False, "supports_thinking": True},
        "kimi-k2.5": {"provider": "qwen", "model": "kimi-k2.5", "supports_search": False, "supports_thinking": False},
    }
    
    def __init__(
        self,
        models: List[Union[str, Dict[str, str]]] = None,
        consensus_threshold: float = 0.67,
        enable_search: bool = False,
        enable_thinking: bool = False,
    ):
        self.adapter = LLMAdapter()
        self.enable_search = enable_search
        self.enable_thinking = enable_thinking
        
        # Determine which models to use
        if models:
            requested_models = self._normalize_models(models)
            self.models = self._filter_models_by_capability(requested_models)
        else:
            self.models = self._filter_models_by_capability(self._default_models())
        
        self.consensus_threshold = consensus_threshold
        
        self.system_prompt = """你是 MyAttention 的决策分析模型，不要写空话，不要重复用户问题，不要写泛泛而谈的正确废话。

你的任务是为决策提供可执行材料。回答必须：
1. 先给出明确判断，不要先铺垫。
2. 只保留最关键的 3-5 个理由，理由要具体。
3. 明确区分：事实、推断、假设。
4. 指出最重要的不确定性和可能误判点。
5. 给出可执行建议，而不是原则性口号。
6. 如果证据不足，直接说明缺口，不要假装确定。

输出结构固定为：
【结论】
【关键依据】
【关键假设】
【主要风险/反例】
【建议动作】
【置信度】"""

    def _normalize_models(
        self,
        models: List[Union[str, Dict[str, str]]],
    ) -> List[Dict[str, str]]:
        normalized: List[Dict[str, str]] = []

        for item in models:
            if isinstance(item, str):
                model_info = self.BAILIAN_MODELS.get(item)
                if not model_info:
                    raise ValueError(f"Unsupported voting model: {item}")
                normalized.append(
                    {
                        "provider": model_info["provider"],
                        "model": model_info["model"],
                        "name": item,
                    }
                )
                continue

            if not isinstance(item, dict):
                raise ValueError("Voting models must be strings or model config objects")

            provider = item.get("provider")
            model = item.get("model")
            name = item.get("name") or model
            if not provider or not model:
                raise ValueError("Voting model config must include provider and model")

            normalized.append(
                {
                    "provider": provider,
                    "model": model,
                    "name": name,
                }
            )

        if not normalized:
            raise ValueError("Voting models cannot be empty")

        return normalized

    def _default_models(self) -> List[Dict[str, str]]:
        return [
            {"provider": info["provider"], "model": info["model"], "name": name}
            for name, info in self.BAILIAN_MODELS.items()
        ]

    def _filter_models_by_capability(
        self,
        models: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        filtered: List[Dict[str, str]] = []

        for model in models:
            model_key = model.get("name") or model.get("model")
            model_info = self.BAILIAN_MODELS.get(model_key) or self.BAILIAN_MODELS.get(model.get("model", ""))
            if not model_info:
                filtered.append(model)
                continue

            supports_search = model_info.get("supports_search", False)
            supports_thinking = model_info.get("supports_thinking", False)

            if self.enable_search and self.enable_thinking:
                if not (supports_search or supports_thinking):
                    continue
            elif self.enable_search and not supports_search:
                continue
            elif self.enable_thinking and not supports_thinking:
                continue

            filtered.append(model)

        if filtered:
            return filtered

        raise ValueError(
            f"No voting models satisfy search={self.enable_search}, thinking={self.enable_thinking}"
        )

    def _model_capability_summary(self, model_name: str) -> Dict[str, Any]:
        model_info = self.BAILIAN_MODELS.get(model_name, {})
        supports_search = model_info.get("supports_search", False)
        supports_thinking = model_info.get("supports_thinking", False)
        if self.enable_search and self.enable_thinking:
            if supports_search and supports_thinking:
                role = "primary"
                contribution = "search+thinking"
            elif supports_search:
                role = "support"
                contribution = "search"
            elif supports_thinking:
                role = "support"
                contribution = "thinking"
            else:
                role = "support"
                contribution = "general"
        elif self.enable_search:
            role = "primary"
            contribution = "search"
        elif self.enable_thinking:
            role = "primary"
            contribution = "thinking"
        else:
            role = "primary"
            contribution = "general"

        return {
            "supports_search": supports_search,
            "supports_thinking": supports_thinking,
            "role": role,
            "contribution": contribution,
        }
    
    async def _query_model(
        self,
        message: str,
        provider: str,
        model: str,
        name: str,
        system_prompt: Optional[str] = None,
    ) -> VotingResult:
        """Query a single model (non-streaming, for backward compatibility)"""
        try:
            # Check if this model supports search and search is enabled
            model_info = self.BAILIAN_MODELS.get(model, {})
            use_search = self.enable_search and model_info.get("supports_search", False)
            use_thinking = self.enable_thinking and model_info.get("supports_thinking", False)
            
            _vlog(f"投票查询开始: model={name}, provider={provider}, search={use_search}, thinking={use_thinking}, raw_model={repr(model)}")
            response = await self.adapter.chat(
                message=message,
                provider=provider,
                model=model,
                system_prompt=system_prompt or self.system_prompt,
                enable_search=use_search,
                enable_thinking=use_thinking,
            )
            _vlog(f"投票查询成功: model={name}, 响应长度={len(response)}")
            return VotingResult(
                model=name,
                provider=provider,
                content=response,
                success=True,
            )
        except Exception as e:
            _vlog(f"投票查询失败: model={name}, error={e}")
            return VotingResult(
                model=name,
                provider=provider,
                content="",
                success=False,
                error=str(e),
            )

    async def _query_model_stream(
        self,
        message: str,
        provider: str,
        model: str,
        name: str,
        queue: asyncio.Queue,
        system_prompt: Optional[str] = None,
    ) -> VotingResult:
        """Query a single model with streaming, pushing content to queue"""
        content_buffer = ""
        try:
            model_info = self.BAILIAN_MODELS.get(model, {})
            use_search = self.enable_search and model_info.get("supports_search", False)
            use_thinking = self.enable_thinking and model_info.get("supports_thinking", False)
            
            _vlog(f"流式投票查询开始: model={name}, provider={provider}, search={use_search}, thinking={use_thinking}")
            
            async for chunk in self.adapter.stream_chat(
                message=message,
                provider=provider,
                model=model,
                system_prompt=system_prompt or self.system_prompt,
                enable_search=use_search,
                enable_thinking=use_thinking,
            ):
                # Skip thinking markers in voting mode
                if chunk.startswith("__THINKING__"):
                    continue
                content_buffer += chunk
                # Push content chunk to queue for real-time display
                await queue.put(StreamEvent(
                    event_type="content",
                    model=name,
                    data=chunk,
                ))
            
            _vlog(f"流式投票查询成功: model={name}, 响应长度={len(content_buffer)}")
            
            # Check if output contains tool_call artifacts (model tried to call tools instead of answering)
            import re
            tool_call_pattern = re.compile(r'<invoke\s+name=|tool_call|<parameter\s+name=', re.IGNORECASE)
            if tool_call_pattern.search(content_buffer) and len(content_buffer.strip()) < 500:
                _vlog(f"模型 {name} 输出包含 tool_call 标记，标记为异常输出")
                # Clean up tool_call artifacts from content
                clean_content = re.sub(r'<invoke.*?</invoke>|<parameter.*?</parameter>|minimax:tool_call.*', '', content_buffer, flags=re.DOTALL).strip()
                if len(clean_content) < 20:
                    await queue.put(StreamEvent(
                        event_type="error",
                        model=name,
                        data="模型尝试调用工具但未能完成回答",
                    ))
                    return VotingResult(
                        model=name,
                        provider=provider,
                        content=content_buffer,
                        success=False,
                        error="模型尝试调用工具但未能完成回答",
                    )
            
            # Signal completion
            await queue.put(StreamEvent(
                event_type="complete",
                model=name,
                data="",
            ))
            return VotingResult(
                model=name,
                provider=provider,
                content=content_buffer,
                success=True,
            )
        except Exception as e:
            _vlog(f"流式投票查询失败: model={name}, error={e}")
            # Signal error
            await queue.put(StreamEvent(
                event_type="error",
                model=name,
                data=str(e),
            ))
            return VotingResult(
                model=name,
                provider=provider,
                content=content_buffer,
                success=False,
                error=str(e),
            )
    
    async def vote_stream(
        self,
        message: str,
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Run multi-model voting with streaming progress updates
        
        Yields progress events:
        - {"type": "voting_start", "models": [...], "total": N}
        - {"type": "voting_model_content", "model": "xxx", "content": "..."} - real-time content chunks
        - {"type": "voting_progress", "model": "xxx", "status": "completed|failed", ...}
        - {"type": "voting_synthesizing"}
        - {"type": "voting_synthesis_content", "content": "..."} - synthesis streaming
        - {"type": "voting_result", "consensus": "...", ...}
        """
        # Send start event with participating models
        model_names = [m["name"] for m in self.models]
        yield {
            "type": "voting_start",
            "models": model_names,
            "total": len(self.models),
            "enable_search": self.enable_search,
            "enable_thinking": self.enable_thinking,
            "participants": [
                {
                    "model": model_name,
                    **self._model_capability_summary(model_name),
                }
                for model_name in model_names
            ],
        }
        
        # Queue for collecting streaming content from all models
        event_queue: asyncio.Queue[StreamEvent] = asyncio.Queue()
        
        # Track model states
        model_contents: Dict[str, str] = {m["name"]: "" for m in self.models}
        completed_models: set = set()
        results: List[VotingResult] = []
        
        # Create streaming tasks for all models
        async def stream_model(m: Dict[str, str]) -> VotingResult:
            return await self._query_model_stream(
                message=message,
                provider=m["provider"],
                model=m["model"],
                name=m["name"],
                queue=event_queue,
                system_prompt=system_prompt,
            )
        
        # Start all model tasks
        tasks = [asyncio.create_task(stream_model(m)) for m in self.models]
        
        # Process queue events while tasks are running
        async def process_queue():
            while len(completed_models) < len(self.models):
                try:
                    event = await asyncio.wait_for(event_queue.get(), timeout=0.1)
                    
                    if event.event_type == "content":
                        # Real-time content chunk from a model
                        model_contents[event.model] += event.data
                        yield {
                            "type": "voting_model_content",
                            "model": event.model,
                            "content": event.data,
                        }
                    
                    elif event.event_type == "complete":
                        completed_models.add(event.model)
                        yield {
                            "type": "voting_progress",
                            "model": event.model,
                            "status": "completed",
                            "completed": len(completed_models),
                            "total": len(self.models),
                            "success": True,
                        }
                    
                    elif event.event_type == "error":
                        completed_models.add(event.model)
                        yield {
                            "type": "voting_progress",
                            "model": event.model,
                            "status": "failed",
                            "completed": len(completed_models),
                            "total": len(self.models),
                            "success": False,
                            "error": event.data,
                        }
                        
                except asyncio.TimeoutError:
                    # No events available, check if all tasks done
                    continue
        
        # Yield events from queue processor
        async for event in process_queue():
            yield event
        
        # Gather all results
        results = await asyncio.gather(*tasks)
        
        # Filter successful results
        successful_results = [r for r in results if r.success]
        
        if not successful_results:
            yield {
                "type": "voting_result",
                "consensus": "无法获取任何模型的回答，请检查 API 配置。",
                "confidence": 0,
                "individual_results": [
                    {"model": r.model, "content": r.error or model_contents.get(r.model, ""), "success": False, "error": r.error}
                    for r in results
                ],
                "summary": {"agreements": [], "disagreements": []},
            }
            return
        
        # Send synthesizing status
        yield {"type": "voting_synthesizing"}
        
        # Synthesize consensus with streaming
        consensus_buffer = ""
        async for chunk in self._synthesize_consensus_stream(message, successful_results):
            consensus_buffer += chunk
            yield {
                "type": "voting_synthesis_content",
                "content": chunk,
            }
        
        # Calculate confidence based on number of successful responses
        confidence = len(successful_results) / len(self.models)
        
        # Send final result
        yield {
            "type": "voting_result",
            "consensus": consensus_buffer,
            "confidence": confidence,
            "individual_results": [
                {
                    "model": r.model,
                    "content": r.content if r.success else (r.error or ""),
                    "success": r.success,
                    "error": r.error if not r.success else None,
                    **self._model_capability_summary(r.model),
                }
                for r in results
            ],
            "summary": {
                "total_models": len(self.models),
                "successful": len(successful_results),
                "threshold": self.consensus_threshold,
                "participants": [
                    {
                        "model": m["name"],
                        **self._model_capability_summary(m["name"]),
                    }
                    for m in self.models
                ],
            },
        }
    
    async def vote(
        self,
        message: str,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run multi-model voting on a query (non-streaming version)
        
        Returns a dictionary with:
        - consensus: The synthesized consensus view
        - confidence: Confidence level (0-1)
        - individual_results: Results from each model
        - summary: Summary of agreements and disagreements
        """
        # Query all models in parallel
        tasks = [
            self._query_model(
                message=message,
                provider=m["provider"],
                model=m["model"],
                name=m["name"],
                system_prompt=system_prompt,
            )
            for m in self.models
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Filter successful results
        successful_results = [r for r in results if r.success]
        
        if not successful_results:
            return {
                "consensus": "无法获取任何模型的回答，请检查 API 配置。",
                "confidence": 0,
                "individual_results": [
                    {"model": r.model, "content": r.error, "success": False}
                    for r in results
                ],
                "summary": {"agreements": [], "disagreements": []},
            }
        
        # Synthesize consensus using the first available model
        consensus = await self._synthesize_consensus(message, successful_results)
        
        # Calculate confidence based on number of successful responses
        confidence = len(successful_results) / len(self.models)
        
        return {
            "consensus": consensus,
            "confidence": confidence,
            "individual_results": [
                {
                    "model": r.model,
                    "content": r.content if r.success else r.error,
                    "success": r.success,
                    **self._model_capability_summary(r.model),
                }
                for r in results
            ],
            "summary": {
                "total_models": len(self.models),
                "successful": len(successful_results),
                "threshold": self.consensus_threshold,
                "participants": [
                    {
                        "model": m["name"],
                        **self._model_capability_summary(m["name"]),
                    }
                    for m in self.models
                ],
            },
        }
    
    async def _synthesize_consensus(
        self,
        original_question: str,
        results: List[VotingResult],
    ) -> str:
        """
        Synthesize a consensus from multiple model responses (non-streaming)
        """
        if len(results) == 1:
            return results[0].content
        
        synthesis_prompt = self._build_synthesis_prompt(original_question, results)
        
        try:
            # Use the primary model for synthesis
            consensus = await self.adapter.chat(
                message=synthesis_prompt,
                provider="qwen",
                model=self.adapter.default_model,
            )
            return consensus
        except Exception:
            # Fallback: just combine the results
            combined = "【多模型分析结果】\n\n"
            for result in results:
                combined += f"**{result.model}**:\n{result.content}\n\n---\n\n"
            return combined

    async def _synthesize_consensus_stream(
        self,
        original_question: str,
        results: List[VotingResult],
    ) -> AsyncGenerator[str, None]:
        """
        Synthesize a consensus from multiple model responses with streaming
        """
        if len(results) == 1:
            yield results[0].content
            return
        
        synthesis_prompt = self._build_synthesis_prompt(original_question, results)
        
        try:
            # Use the primary model for synthesis with streaming
            async for chunk in self.adapter.stream_chat(
                message=synthesis_prompt,
                provider="qwen",
                model=self.adapter.default_model,
            ):
                # Skip thinking markers
                if chunk.startswith("__THINKING__"):
                    continue
                yield chunk
        except Exception as e:
            _vlog(f"综合分析流式输出失败: {e}")
            # Fallback: just combine the results
            combined = "【多模型分析结果】\n\n"
            for result in results:
                combined += f"**{result.model}**:\n{result.content}\n\n---\n\n"
            yield combined

    def _build_synthesis_prompt(
        self,
        original_question: str,
        results: List[VotingResult],
    ) -> str:
        synthesis_prompt = f"""你是最终裁决器。你不是要重复各模型的套话，而是要把它们压缩成对决策真正有用的材料。

任务要求：
1. 先给出一句话决策判断。
2. 明确列出“共识”与“分歧”，不要混在一起。
3. 每条共识或分歧都要点名来源模型。
4. 抽取隐藏假设、证据缺口、潜在误判点。
5. 最后给出可执行下一步，不要写空泛建议。
6. 如果多个模型都缺乏依据，要明确说“当前证据不足”。
7. 严禁使用“综合来看”“总体而言”这类空洞过渡句堆字数。

请严格按以下结构输出：
【一句话判断】
【共识】
- 观点
  来源:
【关键分歧】
- 分歧点
  支持模型:
【隐藏假设】
【证据缺口】
【风险提示】
【建议动作】
【最终置信度】

用户问题：
{original_question}

以下是各模型原始回答：
"""

        for result in results:
            synthesis_prompt += f"""
--- {result.model} ---
{result.content}
"""

        return synthesis_prompt
