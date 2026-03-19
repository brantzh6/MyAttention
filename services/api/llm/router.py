"""
Task Router - Intelligent model selection based on task type

Routes different types of tasks to the most appropriate LLM model
based on task characteristics, model capabilities, and cost.
"""

from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass


class TaskType(str, Enum):
    SIMPLE_QA = "simple_qa"
    SUMMARIZATION = "summarization"
    DEEP_ANALYSIS = "deep_analysis"
    LONG_CONTEXT = "long_context"
    CODE_GENERATION = "code_generation"
    CREATIVE_WRITING = "creative_writing"
    CRITICAL_DECISION = "critical_decision"
    FACT_CHECK = "fact_check"


@dataclass
class ModelConfig:
    provider: str
    model: str
    fallback_provider: Optional[str] = None
    fallback_model: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7


# Task-to-model routing configuration (using Alibaba Cloud Bailian API)
ROUTING_CONFIG: Dict[TaskType, ModelConfig] = {
    TaskType.SIMPLE_QA: ModelConfig(
        provider="qwen",
        model="qwen-turbo",
        fallback_provider="qwen",
        fallback_model="qwen-plus",
        temperature=0.3,
    ),
    TaskType.SUMMARIZATION: ModelConfig(
        provider="qwen",
        model="qwen-plus",
        fallback_provider="qwen",
        fallback_model="qwen-max",
        temperature=0.5,
    ),
    TaskType.DEEP_ANALYSIS: ModelConfig(
        provider="qwen",
        model="qwen-max",
        fallback_provider="qwen",
        fallback_model="qwen-plus",
        temperature=0.7,
    ),
    TaskType.LONG_CONTEXT: ModelConfig(
        provider="qwen",
        model="qwen-long",
        fallback_provider="qwen",
        fallback_model="qwen-max",
        max_tokens=8192,
    ),
    TaskType.CODE_GENERATION: ModelConfig(
        provider="qwen",
        model="qwen-max",
        fallback_provider="qwen",
        fallback_model="qwen-plus",
        temperature=0.3,
    ),
    TaskType.CREATIVE_WRITING: ModelConfig(
        provider="qwen",
        model="qwen-max",
        fallback_provider="qwen",
        fallback_model="qwen-plus",
        temperature=0.9,
    ),
    TaskType.CRITICAL_DECISION: ModelConfig(
        provider="voting",  # Special: triggers multi-model voting
        model="voting",
        temperature=0.5,
    ),
    TaskType.FACT_CHECK: ModelConfig(
        provider="voting",  # Use voting for fact checking
        model="voting",
        temperature=0.3,
    ),
}


class TaskRouter:
    """
    Routes tasks to appropriate models based on task type
    """
    
    def __init__(self, custom_routing: Dict[TaskType, ModelConfig] = None):
        self.routing = {**ROUTING_CONFIG, **(custom_routing or {})}
    
    def classify_task(self, message: str, context_length: int = 0) -> TaskType:
        """
        Classify the task type based on message content and context
        
        Simple heuristic-based classification. Can be enhanced with
        a dedicated classifier model.
        """
        message_lower = message.lower()
        
        # Check for critical decision keywords
        critical_keywords = ["投资", "决策", "选择", "建议", "重大", "分析对比"]
        if any(kw in message_lower for kw in critical_keywords):
            return TaskType.CRITICAL_DECISION
        
        # Check for fact-checking
        fact_keywords = ["验证", "核实", "是否正确", "真的吗", "fact check"]
        if any(kw in message_lower for kw in fact_keywords):
            return TaskType.FACT_CHECK
        
        # Check for code generation
        code_keywords = ["代码", "code", "实现", "function", "写一个", "编程"]
        if any(kw in message_lower for kw in code_keywords):
            return TaskType.CODE_GENERATION
        
        # Check for summarization
        summary_keywords = ["总结", "摘要", "概括", "summarize", "归纳"]
        if any(kw in message_lower for kw in summary_keywords):
            return TaskType.SUMMARIZATION
        
        # Check for deep analysis
        analysis_keywords = ["分析", "深入", "详细", "全面", "评估"]
        if any(kw in message_lower for kw in analysis_keywords):
            return TaskType.DEEP_ANALYSIS
        
        # Check for creative writing
        creative_keywords = ["写一篇", "创作", "故事", "文章", "诗"]
        if any(kw in message_lower for kw in creative_keywords):
            return TaskType.CREATIVE_WRITING
        
        # Check for long context
        if context_length > 32000:
            return TaskType.LONG_CONTEXT
        
        # Default to simple QA
        return TaskType.SIMPLE_QA
    
    def get_model_config(self, task_type: TaskType) -> ModelConfig:
        """Get the model configuration for a task type"""
        return self.routing.get(task_type, self.routing[TaskType.SIMPLE_QA])
    
    def route(
        self,
        message: str,
        context_length: int = 0,
        override_task_type: TaskType = None,
    ) -> ModelConfig:
        """
        Route a message to the appropriate model
        
        Args:
            message: The user's message
            context_length: Length of the context (for long context routing)
            override_task_type: Optional override for automatic classification
            
        Returns:
            ModelConfig with provider and model information
        """
        task_type = override_task_type or self.classify_task(message, context_length)
        return self.get_model_config(task_type)
