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
    
    When enable_search is True, only uses the 3 search-capable models.
    When enable_search is False, uses all 5 models.
    """
    
    # Available voting models on Bailian platform
    BAILIAN_MODELS = {
        "qwen3.5-plus": {"provider": "qwen", "model": "qwen3.5-plus", "supports_search": True},
        "MiniMax-M2.5": {"provider": "qwen", "model": "MiniMax-M2.5", "supports_search": True},
        "deepseek-v3.2": {"provider": "qwen", "model": "deepseek-v3.2", "supports_search": True},
        "glm-5": {"provider": "qwen", "model": "glm-5", "supports_search": False},
        "kimi-k2.5": {"provider": "qwen", "model": "kimi-k2.5", "supports_search": False},
    }
    
    SEARCH_CAPABLE_MODELS = [
        {"provider": "qwen", "model": "qwen3.5-plus", "name": "qwen3.5-plus"},
        {"provider": "qwen", "model": "MiniMax-M2.5", "name": "MiniMax-M2.5"},
        {"provider": "qwen", "model": "deepseek-v3.2", "name": "deepseek-v3.2"},
    ]
    
    DEFAULT_MODELS = [
        {"provider": "qwen", "model": "qwen3.5-plus", "name": "qwen3.5-plus"},
        {"provider": "qwen", "model": "MiniMax-M2.5", "name": "MiniMax-M2.5"},
        {"provider": "qwen", "model": "deepseek-v3.2", "name": "deepseek-v3.2"},
        {"provider": "qwen", "model": "glm-5", "name": "glm-5"},
        {"provider": "qwen", "model": "kimi-k2.5", "name": "kimi-k2.5"},
    ]
    
    def __init__(
        self,
        models: List[Dict[str, str]] = None,
        consensus_threshold: float = 0.67,
        enable_search: bool = False,
    ):
        self.adapter = LLMAdapter()
        self.enable_search = enable_search
        
        # Determine which models to use
        if models:
            self.models = models
        elif enable_search:
            # Use search-capable models when search is enabled
            self.models = self.SEARCH_CAPABLE_MODELS
        else:
            # Default models
            self.models = self.DEFAULT_MODELS
        
        self.consensus_threshold = consensus_threshold
        
        self.system_prompt = """你是一个专业的分析师，请对以下问题给出详细、客观的分析。
        
要求：
1. 分析要全面，考虑多个角度
2. 给出明确的结论和建议
3. 标注关键观点的置信度
4. 列出主要的风险和机会"""
    
    async def _query_model(
        self,
        message: str,
        provider: str,
        model: str,
        name: str,
    ) -> VotingResult:
        """Query a single model (non-streaming, for backward compatibility)"""
        try:
            # Check if this model supports search and search is enabled
            model_info = self.BAILIAN_MODELS.get(model, {})
            use_search = self.enable_search and model_info.get("supports_search", False)
            
            _vlog(f"投票查询开始: model={name}, provider={provider}, search={use_search}, raw_model={repr(model)}")
            response = await self.adapter.chat(
                message=message,
                provider=provider,
                model=model,
                system_prompt=self.system_prompt,
                enable_search=use_search,
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
    ) -> VotingResult:
        """Query a single model with streaming, pushing content to queue"""
        content_buffer = ""
        try:
            model_info = self.BAILIAN_MODELS.get(model, {})
            use_search = self.enable_search and model_info.get("supports_search", False)
            
            _vlog(f"流式投票查询开始: model={name}, provider={provider}, search={use_search}")
            
            async for chunk in self.adapter.stream_chat(
                message=message,
                provider=provider,
                model=model,
                system_prompt=self.system_prompt,
                enable_search=use_search,
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
    
    async def vote_stream(self, message: str) -> AsyncGenerator[Dict[str, Any], None]:
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
                }
                for r in results
            ],
            "summary": {
                "total_models": len(self.models),
                "successful": len(successful_results),
                "threshold": self.consensus_threshold,
            },
        }
    
    async def vote(self, message: str) -> Dict[str, Any]:
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
                }
                for r in results
            ],
            "summary": {
                "total_models": len(self.models),
                "successful": len(successful_results),
                "threshold": self.consensus_threshold,
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
        
        # Build synthesis prompt
        synthesis_prompt = f"""请综合以下多个AI模型对同一问题的回答，生成一份综合分析报告。

原始问题：{original_question}

"""
        for i, result in enumerate(results, 1):
            synthesis_prompt += f"""
--- {result.model} 的回答 ---
{result.content}

"""
        
        synthesis_prompt += """
请生成综合报告，包含：
1. 【共识观点】所有模型都同意的核心结论
2. 【分歧观点】各模型存在差异的观点
3. 【综合建议】基于多方观点的最终建议
4. 【置信度】对每个结论的置信度评估
"""
        
        try:
            # Use the primary model for synthesis
            consensus = await self.adapter.chat(
                message=synthesis_prompt,
                provider="qwen",
                model="qwen-max",
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
        
        # Build synthesis prompt
        synthesis_prompt = f"""请综合以下多个AI模型对同一问题的回答，生成一份综合分析报告。

原始问题：{original_question}

"""
        for i, result in enumerate(results, 1):
            synthesis_prompt += f"""
--- {result.model} 的回答 ---
{result.content}

"""
        
        synthesis_prompt += """
请生成综合报告，包含：
1. 【共识观点】所有模型都同意的核心结论
2. 【分歧观点】各模型存在差异的观点
3. 【综合建议】基于多方观点的最终建议
4. 【置信度】对每个结论的置信度评估
"""
        
        try:
            # Use the primary model for synthesis with streaming
            async for chunk in self.adapter.stream_chat(
                message=synthesis_prompt,
                provider="qwen",
                model="qwen-max",
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
